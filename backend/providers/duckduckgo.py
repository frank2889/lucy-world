from __future__ import annotations

import re
from typing import Any, Dict, List

from requests import Session

from .base import SuggestionProvider, SuggestionRequest, SuggestionResult, register_provider


@register_provider
class DuckDuckGoProvider(SuggestionProvider):
    slug = 'duckduckgo'
    display_name = 'DuckDuckGo'
    cache_ttl = 300

    def fetch(self, request: SuggestionRequest, session: Session, logger) -> SuggestionResult:
        keyword = request.keyword.strip()
        language = (request.language or '').lower()
        language = re.sub(r'[^a-z]', '', language)[:2] or 'en'
        country = (request.country or '').upper()
        country = re.sub(r'[^A-Z]', '', country)
        if len(country) > 2:
            country = country[:2]

        language_country_map = {
            'en': 'us-en',
            'nl': 'nl-nl',
            'fr': 'fr-fr',
            'de': 'de-de',
            'es': 'es-es',
            'it': 'it-it',
            'pt': 'br-pt',
            'ru': 'ru-ru',
            'ja': 'jp-jp',
            'hi': 'in-hi',
        }

        kl_candidates: List[str] = []
        if country and language:
            kl_candidates.append(f"{country.lower()}-{language}")
        if language and language in language_country_map:
            kl_candidates.append(language_country_map[language])
        if language:
            kl_candidates.append(f"{language}-{language}")
        kl_candidates.append('wt-wt')

        kl = 'wt-wt'
        seen: set[str] = set()
        for candidate in kl_candidates:
            if candidate and candidate not in seen:
                seen.add(candidate)
                kl = candidate
                break

        params = {
            'q': keyword,
            'type': str(request.extras.get('type', 'list') if request.extras else 'list'),
            'kl': kl,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; LucyWorldBot/1.0; +https://lucy.world)',
            'Accept': 'application/json, text/javascript;q=0.9,*/*;q=0.8',
            'Referer': 'https://duckduckgo.com/',
        }

        try:
            resp = session.get('https://duckduckgo.com/ac/', params=params, headers=headers, timeout=6)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:  # pragma: no cover - network failures handled upstream
            logger.error("DuckDuckGo suggestion fetch failed: %s", exc)
            raise

        suggestions: List[Dict[str, Any]] = []
        if isinstance(payload, list):
            if payload and isinstance(payload[0], dict):
                for item in payload:
                    if not isinstance(item, dict):
                        continue
                    phrase = item.get('phrase') or item.get('q') or item.get('text')
                    if not phrase:
                        continue
                    suggestions.append(
                        {
                            'phrase': str(phrase),
                            'snippet': item.get('snippet') or item.get('desc') or None,
                            'score': item.get('score'),
                            'type': item.get('type') or None,
                            'image': item.get('image') or None,
                        }
                    )
            elif len(payload) >= 2 and isinstance(payload[1], list):
                # Newer DuckDuckGo response structure: ["query", [suggestions...], ...]
                for index, phrase in enumerate(payload[1]):
                    if not isinstance(phrase, str) or not phrase.strip():
                        continue
                    suggestions.append(
                        {
                            'phrase': phrase.strip(),
                            'snippet': None,
                            'score': None,
                            'type': None,
                            'image': None,
                            'rank': index + 1,
                        }
                    )

        return {
            'keyword': keyword,
            'language': language,
            'country': country or None,
            'kl': kl,
            'suggestions': suggestions,
            'metadata': {
                'approx_volume': len(suggestions),
                'computed_from': 'duckduckgo_autocomplete',
            },
        }
