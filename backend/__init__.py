#!/usr/bin/env python3
"""
Backend package for Lucy World Search
Provides a Flask app factory `create_app()` that registers routes and config.
"""
import os
import json
import csv
import io
import logging
import requests
from datetime import datetime
from typing import Any
from flask import Flask, render_template, request, jsonify, send_file, redirect, abort
from flask import send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from backend.services.advanced_keyword_tool import AdvancedKeywordTool
from backend.services.free_keyword_tool import FreeKeywordTool
from .extensions import db
from .routes_projects import bp as projects_bp
from .routes_auth import bp as auth_bp


def create_app() -> Flask:
	base_dir = os.path.dirname(os.path.abspath(__file__))
	project_root = os.path.dirname(base_dir)
	static_folder = os.path.join(project_root, 'static')
	templates_folder = os.path.join(project_root, 'templates')

	# Configure logging for production
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)

	app = Flask(__name__, static_folder=static_folder, template_folder=templates_folder)

	# Accept both trailing and non-trailing slash variants for all routes
	try:
		app.url_map.strict_slashes = False
	except Exception:
		pass

	# Database setup (SQLite by default; can be overridden with DATABASE_URL)
	db_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL')
	# Normalize DATABASE_URL for SQLAlchemy (postgres:// -> postgresql://)
	if db_url and db_url.startswith('postgres://'):
		db_url = 'postgresql://' + db_url[len('postgres://'):]
	# Ensure sslmode=require for Postgres if not present (DigitalOcean default)
	if db_url and db_url.startswith('postgresql://') and 'sslmode=' not in db_url:
		sep = '&' if '?' in db_url else '?'
		db_url = f"{db_url}{sep}sslmode=require"
	if not db_url:
		db_path = os.path.join(project_root, 'lucy.sqlite3')
		db_url = f"sqlite:///{db_path}"
	app.config.update(
		SQLALCHEMY_DATABASE_URI=db_url,
		SQLALCHEMY_TRACK_MODIFICATIONS=False,
		SQLALCHEMY_ENGINE_OPTIONS={
			'pool_pre_ping': True,
			'pool_recycle': 300,
		}
	)
	db.init_app(app)

	# Trust proxy headers from the DigitalOcean load balancer so request.scheme is correct
	app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

	# Security: prefer HTTPS for generated URLs and secure cookies in production
	app.config.update(
		PREFERRED_URL_SCHEME="https",
		SESSION_COOKIE_SECURE=True,
		SESSION_COOKIE_SAMESITE="Lax",
	)

	# Initialiseer beide keyword tools
	try:
		advanced_tool = AdvancedKeywordTool()
		free_tool = FreeKeywordTool()
		logger.info("Keyword tools successfully initialized")
	except Exception as e:
		logger.error(f"Error initializing keyword tools: {e}")
		advanced_tool = None
		free_tool = None

	def _supported_langs():
		"""Return a deduplicated list of primary language codes.
		Use languages/languages.json as the source of truth. Fall back to registry/* only if needed, then static fallback.
		"""
		primary: list[str] = []
		# Preferred: aggregated master list
		for path in (
			os.path.join(project_root, 'languages', 'languages.json'),
			os.path.join(static_folder, 'i18n', 'languages.json'),
		):
			try:
				with open(path, 'r', encoding='utf-8') as f:
					data = json.load(f)
					langs = data.get('languages') or []
					for l in langs:
						code = str(l).split('-')[0].lower()
						if len(code) == 2 and code.isalpha() and code not in primary:
							primary.append(code)
					if primary:
						return primary
			except Exception:
				continue
		# Optional fallback: per-language registry files
		reg_dir = os.path.join(project_root, 'languages', 'registry')
		if os.path.isdir(reg_dir):
			for name in sorted(os.listdir(reg_dir)):
				if name.endswith('.json'):
					code = name[:-5].lower()
					if len(code) == 2 and code.isalpha() and code not in primary:
						primary.append(code)
			if primary:
				return primary
		return ['en','nl']

	def _locale_json_path(lang: str) -> str | None:
		lang = (lang or '').split('-')[0].lower()
		if not lang:
			return None
		lang_dir = os.path.join(project_root, 'languages', lang)
		candidate = os.path.join(lang_dir, 'locale.json')
		if os.path.exists(candidate):
			return candidate
		legacy_locales_dir = os.path.join(project_root, 'languages', 'locales')
		legacy_candidate = os.path.join(legacy_locales_dir, f'{lang}.json')
		if os.path.exists(legacy_candidate):
			return legacy_candidate
		very_legacy_dir = os.path.join(project_root, 'locales')
		very_legacy_candidate = os.path.join(very_legacy_dir, f'{lang}.json')
		if os.path.exists(very_legacy_candidate):
			return very_legacy_candidate
		return None

	def _available_locales() -> list[str]:
		"""Return the exact language codes that have real UI locale files."""
		codes: list[str] = []
		languages_dir = os.path.join(project_root, 'languages')
		if os.path.isdir(languages_dir):
			for name in sorted(os.listdir(languages_dir)):
				path = os.path.join(languages_dir, name)
				if not os.path.isdir(path):
					continue
				if name in {'registry', 'dictionaries'}:
					continue
				if _locale_json_path(name):
					codes.append(name)
		# Fall back to legacy layout if needed
		legacy_locales_dir = os.path.join(project_root, 'languages', 'locales')
		if os.path.isdir(legacy_locales_dir):
			for name in sorted(os.listdir(legacy_locales_dir)):
				if name.endswith('.json'):
					codes.append(name.split('.json')[0])
		return sorted(set(codes))

	def _detect_lang() -> str:
		al = request.headers.get('Accept-Language', '')
		candidates: list[str] = []
		for part in al.split(','):
			lang = part.split(';')[0].strip().lower()
			if not lang:
				continue
			# normalize: zh-CN -> zh, en-US -> en
			lang_primary = lang.split('-')[0]
			candidates.append(lang_primary)
		supported = _supported_langs()
		# Accept-Language is authoritative; if none match, fall back to default without geo guesswork
		for c in candidates:
			if c in supported:
				return c
		# Final fallback with no geo inference
		return 'en'

	def _detect_country() -> str:
		"""Simple country detection from CDN headers only - no fallbacks."""
		# Common CDN/proxy headers for country
		header_candidates = [
			'CF-IPCountry',                # Cloudflare
			'X-AppEngine-Country',         # App Engine / Google Cloud
			'Fastly-Client-Country',       # Fastly
			'Fly-Client-Country',          # Fly.io
			'X-Geo-Country',               # Generic
			'X-Country-Code',              # Generic
			'X-Forwarded-Country',         # Non-standard
			'X-Real-IP-Country',           # Some proxies
		]
		for h in header_candidates:
			val = request.headers.get(h)
			if val and isinstance(val, str):
				cc = val.strip().upper()
				if len(cc) == 2 and cc.isalpha():
					return cc
		
		# No fallbacks - return empty string if unknown
		return ''

	def _vite_manifest():
		manifest_path = os.path.join(static_folder, 'app', '.vite', 'manifest.json')
		# Vite 5 default manifest is in outDir/manifest.json
		if not os.path.exists(manifest_path):
			manifest_path = os.path.join(static_folder, 'app', 'manifest.json')
		if os.path.exists(manifest_path):
			try:
				with open(manifest_path, 'r') as f:
					return json.load(f)
			except Exception:
				return None
		return None

	def _spa_response(lang: str):
		manifest = _vite_manifest() or {}
		# Try to pick index.* entries
		entry = manifest.get('index.html') or manifest.get('src/main.tsx') or {}
		css_files = entry.get('css') if isinstance(entry, dict) else None
		js_file = entry.get('file') if isinstance(entry, dict) else None
		manifest_css = None
		if css_files and len(css_files) > 0:
			manifest_css = f"/static/app/{css_files[0]}" if not css_files[0].startswith('/static/app/') else css_files[0]
		manifest_js = f"/static/app/{js_file}" if js_file and not str(js_file).startswith('/static/app/') else js_file

		def _derive_meta_from_strings(strings: dict[str, Any] | None) -> tuple[str | None, str | None, str | None, str | None]:
			"""Return sensible localized fallbacks for meta title/description/keywords/robots."""
			if not isinstance(strings, dict):
				return (None, None, None, None)
			def _get(key: str) -> str | None:
				val = strings.get(key)
				if isinstance(val, str):
					val = val.strip()
					if val:
						return val
				return None
			search_title = _get('search.title')
			search_hint = _get('search.hint')
			search_button = _get('search.button')
			nav_search = _get('nav.search')
			meta_title = _get('meta.title') or _get('meta_title')
			meta_description = _get('meta.description') or _get('meta_description')
			meta_keywords = _get('meta.keywords') or _get('meta_keywords')
			meta_robots = _get('meta.robots') or _get('meta_robots')
			if not meta_title:
				if search_title:
					meta_title = f"Lucy World — {search_title}"
				else:
					meta_title = "Lucy World"
			if not meta_description:
				parts: list[str] = []
				if search_title:
					parts.append(search_title)
				if search_hint:
					parts.append(search_hint)
				else:
					parts.append("Keyword research made simple with Google data.")
				meta_description = " ".join([p for p in parts if p]) or "Keyword research made simple with Google data."
			if not meta_keywords:
				keywords: list[str] = []
				for candidate in ("Lucy World", search_title, search_button, nav_search, "SEO", "keyword research"):
					if candidate and candidate not in keywords:
						keywords.append(candidate)
				meta_keywords = ", ".join(keywords)
			if not meta_robots:
				meta_robots = 'index, follow'
			# Surface derived values back onto strings so API consumers see them too
			for key, value in (
				('meta.title', meta_title),
				('meta.description', meta_description),
				('meta.keywords', meta_keywords),
				('meta.robots', meta_robots),
			):
				if value and not isinstance(strings.get(key), str):
					strings[key] = value
			return meta_title, meta_description, meta_keywords, meta_robots

		# Build hreflangs for available locales (no fallback)
		hreflangs = {}
		for code in (_available_locales() or _supported_langs()):
			# Only expose two-letter ISO 639-1 codes in hreflang
			c = (code or '').split('-')[0].lower()
			if len(c) == 2 and c.isalpha():
				hreflangs[c] = request.url_root.rstrip('/') + f"/{c}/"
		# x-default points to root (will redirect to detected language)
		hreflangs['x-default'] = request.url_root.rstrip('/') + '/'
		canonical = request.url_root.rstrip('/') + f"/{lang}/"
		# Language direction (rtl for Arabic/Hebrew/Persian/Urdu)
		rtl_langs = {'ar','he','fa','ur'}
		page_dir = 'rtl' if lang in rtl_langs else 'ltr'

		# Load per-locale structured data (for meta + inline JSON-LD)
		def _load_structured(lang_code: str) -> tuple[Any, dict[str, str | None]]:
			# Prefer on-disk override
			override = _lang_asset_path(lang_code, 'structured.json')
			if override:
				try:
					with open(override, 'r', encoding='utf-8') as f:
						structured = json.load(f)
				except Exception:
					structured = None
			else:
				structured = None
			# Fallback: default payload similar to /meta/structured.json but localized
			base = request.url_root.rstrip('/')
			home = f"{base}/{lang_code}/"
			default_structured = {
				"@context": "https://schema.org",
				"@graph": [
					{
						"@type": "Organization",
						"name": "Lucy World",
						"url": base + "/",
						"logo": base + "/static/img/canva/logo-text.png"
					},
					{
						"@type": "WebSite",
						"name": "Lucy World",
						"url": home,
						"inLanguage": lang_code,
						"description": "Keyword research made simple with Google data: suggestions, trends, and insights.",
						"keywords": "keyword research, SEO, Google Trends, suggestions, search volume",
						"publisher": { "@type": "Organization", "name": "Lucy World" },
						"author": { "@type": "Organization", "name": "Lucy World" },
						"potentialAction": {
							"@type": "SearchAction",
							"target": home + "?q={search_term_string}",
							"query-input": "required name=search_term_string"
						}
					},
					{
						"@type": "WebPage",
						"name": "Lucy World",
						"url": home,
						"inLanguage": lang_code,
						"isPartOf": { "@type": "WebSite", "url": home },
						"description": "Keyword research made simple with Google data: suggestions, trends, and insights.",
						"keywords": "keyword research, SEO, Google Trends, suggestions, search volume"
					}
				]
			}

			# If no override structured file, start from default
			if not structured:
				structured = default_structured

			# Try to load locales meta strings and merge into structured nodes
			meta_title = None
			meta_description = None
			meta_keywords = None
			meta_robots = None
			try:
				locales_dir = os.path.join(project_root, 'languages', 'locales')
				locale_path = os.path.join(locales_dir, f"{lang_code}.json")
				strings = None
				if os.path.exists(locale_path):
					with open(locale_path, 'r', encoding='utf-8') as lf:
						ld = json.load(lf)
						strings = ld.get('strings') if isinstance(ld, dict) else None
				meta_title, meta_description, meta_keywords, meta_robots = _derive_meta_from_strings(strings)
				# Patch structured graph with locale meta when provided
				graph = structured.get('@graph') if isinstance(structured, dict) else None
				if isinstance(graph, list):
					for node in graph:
						if not isinstance(node, dict):
							continue
						if node.get('@type') in ('WebSite', 'WebPage'):
							if meta_title:
								node['name'] = meta_title
							if meta_description:
								node['description'] = meta_description
							if meta_keywords:
								node['keywords'] = meta_keywords
			except Exception:
				pass

			return structured, {
				'title': meta_title,
				'description': meta_description,
				'keywords': meta_keywords,
				'robots': meta_robots,
			}

		structured, meta_defaults = _load_structured(lang)
		# Extract meta fields from structured data
		meta_title = meta_defaults.get('title') or "Lucy World"
		meta_description = meta_defaults.get('description')
		meta_keywords = meta_defaults.get('keywords')
		meta_robots = meta_defaults.get('robots') or 'index, follow'
		try:
			graph = structured.get('@graph') if isinstance(structured, dict) else None
			if isinstance(graph, list):
				for node in graph:
					if isinstance(node, dict) and node.get('@type') in ('WebPage','WebSite'):
						meta_title = node.get('name') or meta_title
						meta_description = node.get('description') or meta_description
						mk = node.get('keywords')
						if isinstance(mk, list):
							meta_keywords = ", ".join([str(x) for x in mk])
						elif isinstance(mk, str):
							meta_keywords = mk
		except Exception:
			pass

		return render_template(
			'base_spa.html',
			lang=lang,
			dir=page_dir,
			manifest=True if manifest else False,
			manifest_css=manifest_css,
			manifest_js=(manifest_js or '/static/app/assets/index.js'),
			canonical_url=canonical,
			hreflangs=hreflangs,
			structured_json=structured,
			meta_title=meta_title,
			meta_description=meta_description,
			meta_keywords=meta_keywords,
			meta_robots=meta_robots,
		)

	def _lang_asset_path(lang: str, filename: str) -> str | None:
		"""Return absolute path to per-locale asset file if it exists under languages/<lang>/<filename>."""
		lang = (lang or '').split('-')[0].lower()
		if not lang:
			return None
		dir_path = os.path.join(project_root, 'languages', lang)
		path = os.path.join(dir_path, filename)
		return path if os.path.exists(path) else None

	@app.route('/')
	def index_root():
		"""Detect language and redirect to /<lang>/ with GTM tracking"""
		lang = _detect_lang()
		
		# Create a temporary page with GTM that redirects immediately
		redirect_html = f"""<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>Lucy World - Redirecting...</title>
	<!-- Google Tag Manager -->
	<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
	new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
	j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
	'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
	}})(window,document,'script','dataLayer','GTM-KGMG5JTG');</script>
	<!-- End Google Tag Manager -->
	<meta http-equiv="refresh" content="0; url=/{lang}/">
	<script>
		// Track root page visit
		window.dataLayer = window.dataLayer || [];
		window.dataLayer.push({{
			'event': 'page_view',
			'page_title': 'Lucy World Root Redirect',
			'page_location': window.location.href,
			'redirect_target': '/{lang}/'
		}});
		// Immediate redirect
		window.location.href = '/{lang}/';
	</script>
</head>
<body>
	<!-- Google Tag Manager (noscript) -->
	<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-KGMG5JTG"
	height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
	<!-- End Google Tag Manager (noscript) -->
	<h1>Redirecting...</h1>
	<p>You should be redirected automatically to <a href="/{lang}/">/{lang}/</a>.</p>
</body>
</html>"""
		return redirect_html

	# Redirect '/<lang>' (no trailing slash) to '/<lang>/'
	@app.route('/<lang>')
	def index_lang_redirect(lang: str):
		lang = (lang or '').split('-')[0].lower()
		return redirect(f'/{lang}/', code=301)

	@app.route('/<lang>/')
	def index_lang(lang: str):
		"""Language-specific entry that sets hreflang and canonical; require exact locale."""
		lang = (lang or '').split('-')[0].lower()
		available = set(_available_locales())
		if not available or lang not in available:
			abort(404)
		return _spa_response(lang)

	# --------------------------------------------------------------------
	# Per-locale SEO endpoints under /<lang>/*
	# If languages/<lang>/{robots.txt,sitemap.xml,structured.json} exist,
	# serve those; otherwise generate localized defaults.
	# --------------------------------------------------------------------
	@app.route('/<lang>/robots.txt')
	def robots_lang(lang: str):
		lang = (lang or '').split('-')[0].lower()
		available = set(_available_locales())
		if not available or lang not in available:
			abort(404)
		override = _lang_asset_path(lang, 'robots.txt')
		base = _base_url()
		if override:
			return send_file(override, mimetype='text/plain')
		content = (
			"User-agent: *\n"
			"Allow: /\n\n"
			f"Sitemap: {base}/{lang}/sitemap.xml\n"
		)
		return app.response_class(content, mimetype='text/plain')

	@app.route('/<lang>/sitemap.xml')
	def sitemap_lang(lang: str):
		lang = (lang or '').split('-')[0].lower()
		available = set(_available_locales())
		if not available or lang not in available:
			abort(404)
		override = _lang_asset_path(lang, 'sitemap.xml')
		if override:
			return send_file(override, mimetype='application/xml')
		# Default: include the localized homepage for this language
		base = _base_url()
		now = datetime.utcnow().strftime('%Y-%m-%d')
		loc = f"{base}/{lang}/"
		xml = (
			"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			"<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
			f"<url><loc>{loc}</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>"
			"</urlset>"
		)
		return app.response_class(xml, mimetype='application/xml')

	@app.route('/<lang>/structured.json')
	def structured_lang(lang: str):
		lang = (lang or '').split('-')[0].lower()
		available = set(_available_locales())
		if not available or lang not in available:
			abort(404)
		override = _lang_asset_path(lang, 'structured.json')
		if override:
			return send_file(override, mimetype='application/json')
		# Default: localized website JSON-LD referencing the language homepage
		base = _base_url()
		home = f"{base}/{lang}/"
		payload = {
			"@context": "https://schema.org",
			"@graph": [
				{
					"@type": "Organization",
					"name": "Lucy World",
					"url": base + "/",
					"logo": base + "/static/img/canva/logo-text.png"
				},
				{
					"@type": "WebSite",
					"name": "Lucy World",
					"url": home,
					"inLanguage": lang,
					"potentialAction": {
						"@type": "SearchAction",
						"target": home + "?q={search_term_string}",
						"query-input": "required name=search_term_string"
					}
				}
			]
		}
		return jsonify(payload)

	# Catch-all for SPA routes under a valid language prefix; lets client-side routing work
	@app.route('/<lang>/<path:subpath>')
	def index_lang_catch_all(lang: str, subpath: str):
		lang = (lang or '').split('-')[0].lower()
		available = set(_available_locales())
		if not available or lang not in available:
			abort(404)
		# Allow the SPA to handle any sub-routes under the language prefix
		return _spa_response(lang)

	@app.route('/search', methods=['GET', 'POST'])
	def search_index():
		"""Search pagina (GET) of gratis zoekactie (POST)."""
		if request.method == 'POST':
			# Reuse the free API logic so UI can POST to /search
			return free_search_keywords()
		# GET -> redirect to Lucy UI
		return redirect('/')

	@app.route('/search/free')
	def free_index():
		"""Gratis keyword research tool"""
		# Toon de nieuwe Lucy World UI i.p.v. de oude Canva pagina
		return render_template('lucy_index.html')

	# Convenience shortcuts for legacy links
	@app.route('/free')
	def free_shortcut():
		return index_root()

	@app.route('/search/advanced')
	def advanced_index():
		"""Geavanceerde keyword research tool UI"""
		return index_root()

	@app.route('/advanced')
	def advanced_shortcut():
		return index_root()

	@app.route('/search/scale')
	def scale_index():
		"""Scale pagina"""
		return index_root()

	@app.route('/scale')
	def scale_shortcut():
		return index_root()

	# Serve built React assets under /app/* (convenience)
	@app.route('/app/<path:filename>')
	def app_assets(filename):
		return send_from_directory(os.path.join(app.static_folder or 'static', 'app'), filename)

	# ========================================================================
	# META ENDPOINTS (/meta/*)
	# ========================================================================
	def _base_url() -> str:
		# Ensure trailing slash removed
		return request.url_root.rstrip('/')

	@app.route('/meta/robots.txt')
	def meta_robots():
		"""Robots.txt with sitemap link"""
		base = _base_url()
		content = (
			"User-agent: *\n"
			"Allow: /\n\n"
			f"Sitemap: {base}/meta/sitemap.xml\n"
		)
		return app.response_class(content, mimetype='text/plain')

	# Standard robots.txt alias at the root
	@app.route('/robots.txt')
	@app.route('/robots.txt/')
	def robots_root():
		return meta_robots()

	@app.route('/meta/sitemap.xml')
	def meta_sitemap():
		"""XML sitemap with language-specific home URLs (only available locales)."""
		base = _base_url()
		now = datetime.utcnow().strftime('%Y-%m-%d')
		langs = _available_locales() or _supported_langs()
		urls = [{"loc": f"{base}/{lang}/", "priority": "1.0"} for lang in langs]
		items = "".join(
			f"<url><loc>{u['loc']}</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>{u['priority']}</priority></url>"
			for u in urls
		)
		xml = (
			"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			"<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
			f"{items}</urlset>"
		)
		return app.response_class(xml, mimetype='application/xml')

	# Standard sitemap.xml alias at the root
	@app.route('/sitemap.xml')
	@app.route('/sitemap.xml/')
	def sitemap_root():
		return meta_sitemap()

	# Favicon (avoid 404s); serve project logo as fallback
	@app.route('/favicon.ico')
	def favicon():
		try:
			return send_from_directory(os.path.join(app.static_folder or 'static', 'img', 'canva'), 'logo-text.png')
		except Exception:
			# 1x1 transparent gif
			gif = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
			return send_file(io.BytesIO(gif), mimetype='image/gif')

	@app.route('/meta/feeds.xml')
	def meta_feed():
		"""Minimal Atom feed"""
		base = _base_url()
		now = datetime.utcnow().isoformat() + 'Z'
		feed = f"""
		<?xml version="1.0" encoding="utf-8"?>
		<feed xmlns="http://www.w3.org/2005/Atom">
		  <title>Lucy World Updates</title>
		  <id>{base}/</id>
		  <updated>{now}</updated>
		  <link href="{base}/" />
		  <entry>
		    <title>Welcome to Lucy World</title>
		    <id>{base}/#welcome</id>
		    <updated>{now}</updated>
		    <link href="{base}/" />
		    <summary>Keyword research made simple with Google data.</summary>
		  </entry>
		</feed>
		""".strip()
		return app.response_class(feed, mimetype='application/xml')

	@app.route('/meta/structured.json')
	def meta_structured():
		"""Schema.org JSON-LD for the website and organization."""
		base = _base_url()
		payload = {
			"@context": "https://schema.org",
			"@graph": [
				{
					"@type": "Organization",
					"name": "Lucy World",
					"url": base + "/",
					"logo": base + "/static/img/canva/logo-text.png"
				},
				{
					"@type": "WebSite",
					"name": "Lucy World",
					"url": base + "/",
					"potentialAction": {
						"@type": "SearchAction",
						"target": base + "/?q={search_term_string}",
						"query-input": "required name=search_term_string"
					}
				}
			]
		}
		return jsonify(payload)

	@app.route('/meta/ai.json')
	def meta_ai_manifest():
		"""AI manifest describing available API endpoints and metadata."""
		base = _base_url()
		now = datetime.utcnow().isoformat() + 'Z'
		manifest = {
			"name": "Lucy World",
			"description": "Keyword research tool powered by Google data (Trends, Suggest, Wikipedia).",
			"website": base + "/",
			"api": {
				"auth": "none",
				"base_url": base,
				"endpoints": [
					{
						"path": "/api/free/search",
						"method": "POST",
						"content_type": "application/json",
						"params": {
							"keyword": "string (required)",
							"language": "string, e.g., 'nl'",
							"country": "string, e.g., 'NL'"
						}
					}
				]
			},
			"contact": {
				"email": "support@lucy.world"
			},
			"legal": {
				"privacy_policy": base + "/privacy",
				"terms_of_service": base + "/terms"
			},
			"meta": {
				"last_updated": now,
				"environment": os.getenv('ENV', 'production')
			}
		}
		return jsonify(manifest)

	# ------------------------------------------------------------------------
	# Basic legal pages (minimal HTML) referenced by meta_structured
	# ------------------------------------------------------------------------
	@app.route('/privacy')
	def privacy_page():
		try:
			return render_template('privacy.html')
		except Exception:
			return app.response_class('<!doctype html><title>Privacy Policy</title><h1>Privacy Policy</h1><p>We respect your privacy. No personal data is sold or shared. Contact support@lucy.world for questions.</p>', mimetype='text/html')

	@app.route('/terms')
	def terms_page():
		try:
			return render_template('terms.html')
		except Exception:
			return app.response_class('<!doctype html><title>Terms of Service</title><h1>Terms of Service</h1><p>Use Lucy World at your own risk. No warranties. Contact support@lucy.world for details.</p>', mimetype='text/html')

	@app.route('/meta/detect.json')
	def meta_detect():
		"""Return detected language and country for initial UI defaults."""
		try:
			return jsonify({
				'language': _detect_lang(),
				'country': _detect_country(),
			})
		except Exception:
			return jsonify({'language': 'en', 'country': 'US'})

	@app.route('/meta/content/<lang>.json')
	def meta_content_lang(lang: str):
		"""Serve UI content JSON only for exact available locales; no fallback."""
		lang = (lang or '').split('-')[0].lower()
		content_path = _locale_json_path(lang)
		if not os.path.exists(content_path):
			abort(404)
		try:
			with open(content_path, 'r', encoding='utf-8') as f:
				raw = json.load(f)
			# Accept both our current shape and Shopify-style (keys at root)
			if isinstance(raw, dict) and 'strings' in raw and isinstance(raw['strings'], dict):
				data = raw
			else:
				# Treat the entire file as key->string map
				rtl_langs = {'ar','he','fa','ur'}
				data = { 'lang': lang, 'dir': 'rtl' if lang in rtl_langs else 'ltr', 'strings': raw if isinstance(raw, dict) else {} }
			return jsonify(data)
		except Exception:
			abort(404)

	@app.route('/meta/locales.json')
	def meta_locales():
		"""List available locale codes from locales/ (Shopify-style), with default locale."""
		default_code = 'en'
		codes = _available_locales()
		if 'en' not in codes:
			# attempt to read default from languages.json if present
			try:
				with open(os.path.join(project_root, 'languages', 'languages.json'), 'r', encoding='utf-8') as f:
					data = json.load(f)
					langs = data.get('languages')
					if isinstance(langs, list) and langs:
						default_code = (str(langs[0]).split('-')[0]).lower()
			except Exception:
				pass
		return jsonify({ 'locales': codes, 'default': default_code })

	@app.route('/meta/languages.json')
	def meta_languages():
		"""Return only languages that have real locale files available."""
		try:
			langs = _available_locales()
			return jsonify({"languages": langs})
		except Exception:
			return jsonify({"languages": ['en']})

	@app.route('/meta/countries.json')
	def meta_countries():
		"""Return official ISO 3166-1 alpha-2 country/territory codes."""
		path = os.path.join(project_root, 'languages', 'countries.json')
		try:
			with open(path, 'r', encoding='utf-8') as f:
				data = json.load(f)
			codes = [str(c).upper() for c in (data.get('countries') or []) if isinstance(c, str) and len(c) == 2 and c.isalpha()]
			return jsonify({"countries": codes})
		except Exception:
			# minimal fallback of common markets
			return jsonify({"countries": ["US","GB","NL","DE","FR","ES","IT","CA","AU","IN"]})

	# ========================================================================
	# FREE KEYWORD RESEARCH ENDPOINTS
	# ========================================================================
	@app.route('/api/free/search', methods=['POST'])
	def free_search_keywords():
		"""Gratis keyword research API"""
		try:
			if not free_tool:
				return jsonify({'error': 'Free keyword tool niet beschikbaar'}), 500

			data = request.get_json() or {}
			keyword = data.get('keyword', request.form.get('keyword', '')).strip()
			language = data.get('language', request.form.get('language', '')).strip().lower()
			country = data.get('country', request.form.get('country', '')).strip().upper()

			if not keyword:
				return jsonify({'error': 'Geen zoekwoord opgegeven'}), 400

			if not language:
				# Prefer detected browser language; fallback to tool default
				language = _detect_lang() or getattr(free_tool, 'default_language', 'en')

			if not country:
				country = _detect_country()
			logger.info(f"Free search for keyword: {keyword}, language: {language}, country: {country}")

			# Voer gratis keyword research uit
			raw_keyword_data = free_tool.research_comprehensive(keyword, language=language, country=country or 'US')
			processed_keywords = free_tool.process_keywords_with_data(
				raw_keyword_data,
				keyword,
				language=language,
			)

			trends_data = raw_keyword_data.get('trends_data', {})
			interest_points = trends_data.get('interest', [])

			# Trends summary
			avg_interest = round(sum(interest_points) / len(interest_points), 1) if interest_points else 0
			trend_direction = trends_data.get('trend_direction', 'Stable')

			response_data = {
				'keyword': keyword,
				'language': language,
				'country': country or 'US',
				'categories': {},
				'trends': {
					'interest_over_time': interest_points,
					'trending_searches': trends_data.get('trending_searches', []),
					'related_topics': trends_data.get('related_topics', []),
					'avg_interest': avg_interest,
					'trend_direction': trend_direction,
					'data_points': len(interest_points)
				},
				'stats': {
					'total_keywords': 0,
					'categories_count': 0
				},
				# UI expects a summary block
				'summary': {
					'total_volume': 0,
					'total_keywords': 0,
					'real_data_keywords': 0
				},
				'timestamp': datetime.now().isoformat()
			}

			# Verwerk alle categorieën
			total_keywords = 0
			total_volume = 0
			real_data_keywords = 0
			for category, keywords in processed_keywords.items():
				if keywords:
					category_data = []
					for kw in keywords[:20]:  # Limit to top 20
						# kw may be a dataclass object (KeywordData) or dict
						if hasattr(kw, 'keyword'):
							item = {
								'keyword': getattr(kw, 'keyword', ''),
								'search_volume': getattr(kw, 'search_volume', 0),
								'difficulty': getattr(kw, 'difficulty', None),
								'cpc': getattr(kw, 'cpc', None),
								'competition': getattr(kw, 'competition', 'Unknown'),
								'trend': getattr(kw, 'trend', trend_direction),
								'source': getattr(kw, 'source', None),
							}
						else:
							item = {
								'keyword': kw.get('keyword', ''),
								'search_volume': kw.get('search_volume', kw.get('volume', 0)),
								'difficulty': kw.get('difficulty'),
								'cpc': kw.get('cpc'),
								'competition': kw.get('competition', 'Unknown'),
								'trend': kw.get('trend', trend_direction),
								'source': kw.get('source')
							}
						category_data.append(item)
						total_volume += int(item.get('search_volume') or 0)
						if (item.get('source') == 'Real Data'):
							real_data_keywords += 1
                    
					response_data['categories'][category] = category_data
					total_keywords += len(category_data)

			response_data['stats']['total_keywords'] = total_keywords
			response_data['stats']['categories_count'] = len(response_data['categories'])
			response_data['summary']['total_keywords'] = total_keywords
			response_data['summary']['total_volume'] = total_volume
			response_data['summary']['real_data_keywords'] = real_data_keywords

			return jsonify(response_data)
            
		except Exception as e:
			logger.error(f"Error in free search: {e}")
			return jsonify({'error': f'Er is een fout opgetreden: {str(e)}'}), 500

	# ========================================================================
	# ADVANCED KEYWORD RESEARCH ENDPOINTS
	# ========================================================================
	@app.route('/api/advanced/research', methods=['POST'])
	def advanced_research_keywords():
		"""Geavanceerde keyword research API"""
		try:
			if not advanced_tool:
				return jsonify({'error': 'Advanced keyword tool niet beschikbaar'}), 500
                
			data = request.json
			main_keyword = data.get('keyword', '').strip()
            
			if not main_keyword:
				return jsonify({'error': 'Geen zoekwoord opgegeven'}), 400
            
			logger.info(f"Advanced search for keyword: {main_keyword}")
            
			# Voer keyword research uit
			keyword_categories = advanced_tool.get_comprehensive_keywords(main_keyword)
            
			# Verwerk alle keywords
			all_keywords_data = []
			processed_categories = {}
            
			for category, keywords in keyword_categories.items():
				category_data = []
				for keyword in keywords:
					keyword_data = advanced_tool.get_search_volume_advanced(keyword)
					category_data.append({
						'keyword': keyword_data.keyword,
						'search_volume': keyword_data.search_volume,
						'difficulty': keyword_data.difficulty,
						'cpc': keyword_data.cpc,
						'competition': keyword_data.competition,
						'trend': keyword_data.trend
					})
					all_keywords_data.append(keyword_data)
                
				# Sorteer op zoekvolume
				category_data.sort(key=lambda x: x['search_volume'], reverse=True)
				processed_categories[category] = category_data[:10]  # Top 10 per categorie
            
			# Analyseer opportunities
			opportunities = advanced_tool.analyze_keyword_opportunities(all_keywords_data)
			processed_opportunities = {}
            
			for opp_type, keywords in opportunities.items():
				processed_opportunities[opp_type] = [
					{
						'keyword': kd.keyword,
						'search_volume': kd.search_volume,
						'difficulty': kd.difficulty,
						'cpc': kd.cpc,
						'competition': kd.competition,
						'trend': kd.trend
					} for kd in keywords
				]
            
			# Statistieken
			total_volume = sum(k.search_volume for k in all_keywords_data)
			avg_difficulty = sum(k.difficulty for k in all_keywords_data) / len(all_keywords_data) if all_keywords_data else 0
            
			response = {
				'main_keyword': main_keyword,
				'categories': processed_categories,
				'opportunities': processed_opportunities,
				'stats': {
					'total_keywords': len(all_keywords_data),
					'total_volume': total_volume,
					'avg_difficulty': round(avg_difficulty, 1),
					'avg_volume': total_volume // len(all_keywords_data) if all_keywords_data else 0
				},
				'timestamp': datetime.now().isoformat()
			}
            
			return jsonify(response)
            
		except Exception as e:
			logger.error(f"Error in advanced research: {e}")
			return jsonify({'error': str(e)}), 500

	# ========================================================================
	# EXPORT ENDPOINTS
	# ========================================================================
	@app.route('/api/export/csv', methods=['POST'])
	def export_csv():
		"""Export resultaten naar CSV"""
		try:
			data = request.json
            
			# Maak CSV in geheugen
			output = io.StringIO()
			writer = csv.writer(output)
            
			# Header
			writer.writerow(['Category', 'Keyword', 'Search Volume', 'Difficulty', 'CPC', 'Competition', 'Trend'])
            
			# Data
			for category, keywords in data.get('categories', {}).items():
				for keyword_data in keywords:
					writer.writerow([
						category.replace('_', ' ').title(),
						keyword_data.get('keyword', ''),
						keyword_data.get('search_volume', keyword_data.get('volume', 0)),
						keyword_data.get('difficulty', ''),
						keyword_data.get('cpc', ''),
						keyword_data.get('competition', ''),
						keyword_data.get('trend', '')
					])
            
			# Maak bestand voor download
			output.seek(0)
            
			# Maak bestandsnaam
			filename = f"keyword_research_{data.get('main_keyword', data.get('keyword', 'results')).replace(' ', '_')}.csv"
            
			# Return CSV als download
			return send_file(
				io.BytesIO(output.getvalue().encode('utf-8')),
				mimetype='text/csv',
				as_attachment=True,
				download_name=filename
			)
            
		except Exception as e:
			logger.error(f"Error in CSV export: {e}")
			return jsonify({'error': str(e)}), 500

	# ========================================================================
	# HEALTH CHECK ENDPOINTS
	# ========================================================================
	@app.route('/health')
	def health_check():
		"""Health check voor load balancer"""
		return jsonify({
			'status': 'healthy',
			'timestamp': datetime.now().isoformat(),
			'tools': {
				'advanced': advanced_tool is not None,
				'free': free_tool is not None
			}
		})

	@app.errorhandler(404)
	def not_found(error):
		return jsonify({'error': 'Endpoint niet gevonden'}), 404

	@app.errorhandler(400)
	def bad_request(error):
		# Return JSON for APIs rather than HTML default
		return jsonify({'error': 'Bad request'}), 400

	@app.errorhandler(500)
	def internal_error(error):
		logger.error(f"Internal server error: {error}")
		return jsonify({'error': 'Interne server fout'}), 500

	# Add HSTS over HTTPS responses (does not affect health checks or HTTP traffic)
	@app.after_request
	def add_security_headers(response):
		try:
			# Only set HSTS on secure requests so we don't interfere with internal health checks
			if request.is_secure:
				response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
		except Exception:
			pass
		return response

	# Register blueprints
	app.register_blueprint(projects_bp)
	app.register_blueprint(auth_bp)

	# Create database tables if not exist
	with app.app_context():
		try:
			from . import models  # noqa: F401
			db.create_all()
		except Exception:
			pass

	return app

# Makes 'backend' a package so relative imports work
