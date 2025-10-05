from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from markdown import markdown as md_to_html
from sqlalchemy.exc import SQLAlchemyError

try:  # pragma: no cover - optional dependency guard
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore

from backend.extensions import db
from backend.models import CandidateQuery, ContentDraft


class DraftGenerationError(RuntimeError):
    """Raised when the AI blog pipeline cannot generate a draft."""


def _slugify(value: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return base or "post"


class AIBlogPipeline:
    """Generate, store, and publish blog drafts from high-potential candidate queries."""

    def __init__(
        self,
        *,
        project_root: str,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = os.environ.get("BASE_URL", "https://lucy.world").rstrip("/")
        self.content_dir = self.project_root / "content"
        self.drafts_dir = self.content_dir / "drafts"
        self.published_dir = self.content_dir / "published"
        self.static_blog_dir = self.project_root / "static" / "blog"
        self.model_name = os.environ.get("OPENAI_BLOG_MODEL", "gpt-4o-mini")
        self._client = self._bootstrap_client()
        self._ensure_directories()

    def _bootstrap_client(self):  # pragma: no cover - relies on env configuration
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
        if not api_key:
            return None
        if OpenAI is None:
            self.logger.warning("openai package not available; falling back to template drafts")
            return None
        try:
            return OpenAI(api_key=api_key)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("Failed to initialise OpenAI client: %s", exc)
            return None

    def _ensure_directories(self) -> None:
        for target in (self.content_dir, self.drafts_dir, self.published_dir, self.static_blog_dir):
            target.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Draft generation helpers
    # ------------------------------------------------------------------
    def _build_prompt(self, candidate: CandidateQuery) -> str:
        context_lines = [
            f"Keyword: {candidate.keyword}",
            f"Audience score (0-100): {candidate.audience_score}",
        ]
        if candidate.threshold_reason:
            context_lines.append(f"Threshold reason: {candidate.threshold_reason}")
        if candidate.language:
            context_lines.append(f"Language: {candidate.language}")
        if candidate.country:
            context_lines.append(f"Country: {candidate.country}")

        context_lines.append(
            "Output must be JSON with keys: title (string), summary (string), outline (array of section objects with heading + insight), markdown (string), language (ISO 639-1), country (ISO 3166-1 alpha-2 or null), tags (array of 3-6 SEO tags)."
        )
        context_lines.append(
            "Markdown must include: H1 title, concise intro, three detailed H2 sections with tactical advice, one ROI section, bullet list with examples, and a conclusion with call-to-action for Lucy World."
        )
        context_lines.append("Tone: data-backed, actionable, and privacy-first.")

        return "\n".join(context_lines)

    def _invoke_model(self, candidate: CandidateQuery) -> Optional[Dict[str, Any]]:  # pragma: no cover - network call
        if not self._client:
            return None
        prompt = self._build_prompt(candidate)
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Lucy, an expert B2B growth strategist. Respond in compact JSON only. "
                            "Never include markdown fences or commentary outside the JSON object."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=1800,
            )
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("OpenAI generation failed for '%s': %s", candidate.keyword, exc)
            return None

        try:
            content = response.choices[0].message.content if response.choices else None
            return json.loads(content) if content else None
        except (KeyError, json.JSONDecodeError) as exc:  # pragma: no cover
            self.logger.warning("Failed to parse AI response for '%s': %s", candidate.keyword, exc)
            return None

    def _fallback_payload(self, candidate: CandidateQuery) -> Dict[str, Any]:
        year = datetime.utcnow().year
        title = f"{candidate.keyword.title()} Strategy Playbook for {year}"
        summary = (
            f"See how privacy-first teams can turn interest in '{candidate.keyword}' into pipeline and revenue. "
            "This playbook combines on-page SEO, campaign messaging, and audience activation tips."
        )
        outline: List[Dict[str, str]] = [
            {
                "heading": "Why this keyword matters",
                "insight": "Quantify the demand using Google suggestions and highlight user intent trends.",
            },
            {
                "heading": "Build a privacy-first funnel",
                "insight": "Map campaign ideas across owned, earned, and paid channels with compliant tracking.",
            },
            {
                "heading": "Measure revenue impact",
                "insight": "Define leading indicators and attribution guardrails that respect user consent.",
            },
            {
                "heading": "Turn insights into experiments",
                "insight": "Prioritise agile experiments for the next 30/60/90 days with clear success metrics.",
            },
        ]

        reason_suffix = f" **{candidate.threshold_reason}**." if candidate.threshold_reason else " demand signals."
        md_sections = [
            f"# {title}",
            "",
            summary,
            "",
            "## Why this keyword matters",
            "- Capture long-tail variants surfaced by Lucy's aggregated providers.",
            "- Cluster the topics by stage (awareness, consideration, decision).",
            "- Compare branded vs non-branded intent by geography.",
            "",
            "## Build a privacy-first funnel",
            "1. Launch zero-party data assets (calculators, benchmarks, ROI tools).",
            "2. Orchestrate campaigns across search, newsletters, and privacy-friendly ads.",
            "3. Align messaging with strict data minimisation and consent practices.",
            "",
            "## Measure revenue impact",
            "- Track queries meeting Lucy's threshold reason:" + reason_suffix,
            "- Tie keyword cohorts to influenced pipeline (SQLs, closed-won).",
            "- Share dashboards weekly with growth, product marketing, and RevOps.",
            "",
            "## Turn insights into experiments",
            "| Sprint | Experiment | Owner | KPI |",
            "| --- | --- | --- | --- |",
            "| Next 30 days | Publish insight article and gated ROI worksheet | Content | Qualified leads |",
            "| Next 60 days | Test multi-language landing pages | Localisation | Conversion rate |",
            "| Next 90 days | Launch partner co-marketing kit | Partnerships | Influenced revenue |",
            "",
            "### Call to action",
            "Ready to 10x discovery for this topic? Launch Lucy's AI research workspace to ship the next draft in minutes.",
        ]

        markdown_content = "\n".join(md_sections)
        tags = [candidate.keyword.lower(), "growth", "seo", "privacy"]
        if candidate.country:
            tags.append(candidate.country.lower())

        return {
            "title": title,
            "summary": summary,
            "outline": outline,
            "markdown": markdown_content,
            "language": candidate.language or "en",
            "country": candidate.country,
            "tags": tags,
            "author": "Lucy Growth Team",
        }

    def _compose_payload(self, candidate: CandidateQuery) -> Dict[str, Any]:
        model_payload = self._invoke_model(candidate)
        if model_payload:
            return model_payload
        return self._fallback_payload(candidate)

    def _markdown_to_html(self, markdown_content: str) -> str:
        return md_to_html(markdown_content, extensions=["abbr", "tables", "fenced_code", "sane_lists"])

    def _write_markdown_file(self, draft: ContentDraft, directory: Path) -> Path:
        metadata = {
            "id": draft.id,
            "candidate_id": draft.candidate_id,
            "title": draft.title,
            "summary": draft.summary,
            "slug": draft.slug,
            "language": draft.language,
            "country": draft.country,
            "status": draft.status,
            "audience_score": draft.candidate.audience_score if draft.candidate else None,
            "tags": draft.tags or [],
            "created_at": draft.created_at.isoformat(),
            "updated_at": draft.updated_at.isoformat(),
            "published_at": draft.published_at.isoformat() if draft.published_at else None,
        }
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{draft.slug}.md"
        payload = f"<!--lucy.metadata {json.dumps(metadata, ensure_ascii=False)}-->\n\n{draft.markdown.strip()}\n"
        path.write_text(payload, encoding="utf-8")
        return path

    def _write_html_file(self, draft: ContentDraft, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        html_path = directory / f"{draft.slug}.html"
        published_meta = (
            f'<meta name="published" content="{draft.published_at.isoformat()}" />'
            if draft.published_at
            else ""
        )
        description = (draft.summary or "").replace('"', "'")
        doc = f"""<!doctype html>
<html lang=\"{draft.language or 'en'}\">
<head>
  <meta charset=\"utf-8\" />
  <title>{draft.title}</title>
  <meta name=\"description\" content=\"{description}\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  {published_meta}
  <link rel=\"canonical\" href=\"{self.base_url}/blog/{draft.slug}/\" />
</head>
<body>
  <main class=\"lucy-blog\">
    <article>{draft.html}</article>
  </main>
</body>
</html>
"""
        html_path.write_text(doc, encoding="utf-8")
        return html_path

    def _write_manifest(self) -> None:
        posts = (
            ContentDraft.query.filter_by(status="published")
            .order_by(ContentDraft.published_at.desc())
            .all()
        )
        payload = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "posts": [
                {
                    "id": post.id,
                    "slug": post.slug,
                    "title": post.title,
                    "summary": post.summary,
                    "language": post.language,
                    "country": post.country,
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "url": f"{self.base_url}/blog/{post.slug}/",
                    "tags": post.tags or [],
                }
                for post in posts
            ],
        }
        manifest_path = self.published_dir / "feed.json"
        manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_from_candidate(self, candidate: CandidateQuery) -> ContentDraft:
        if candidate.status not in {"pending", "failed", "drafting"}:
            raise DraftGenerationError(f"Candidate {candidate.id} already processed (status={candidate.status})")

        candidate.status = "drafting"
        db.session.commit()

        payload = self._compose_payload(candidate)
        title = str(payload.get("title") or candidate.keyword.title())
        markdown_content = str(payload.get("markdown") or "")
        if not markdown_content.strip():
            raise DraftGenerationError("Generated markdown content is empty")

        summary = payload.get("summary")
        outline = payload.get("outline") if isinstance(payload.get("outline"), list) else None
        tags = payload.get("tags") if isinstance(payload.get("tags"), list) else None
        language = (payload.get("language") or candidate.language or "en").split("-")[0].lower()
        country_value = payload.get("country") or candidate.country
        country = country_value.strip().upper() if isinstance(country_value, str) and country_value else None

        base_slug = payload.get("slug") or title
        slug_seed = _slugify(str(base_slug))
        slug = ContentDraft.next_slug(slug_seed)

        html_content = self._markdown_to_html(markdown_content)

        draft = ContentDraft(
            candidate_id=candidate.id,
            slug=slug,
            title=title,
            summary=summary,
            outline=outline,
            markdown=markdown_content,
            html=html_content,
            language=language,
            country=country,
            tags=tags,
            author_name=str(payload.get("author")) if payload.get("author") else None,
            status="draft",
        )

        try:
            db.session.add(draft)
            candidate.status = "drafted"
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DraftGenerationError(f"Failed to persist draft: {exc}") from exc

        self._write_markdown_file(draft, self.drafts_dir)
        return draft

    def publish_draft(self, draft: ContentDraft, *, author: Optional[str] = None, tags: Optional[List[str]] = None, language: Optional[str] = None, country: Optional[str] = None) -> ContentDraft:
        if draft.status == "published":
            return draft
        if draft.status not in {"draft", "review", "ready"}:
            raise DraftGenerationError(f"Draft {draft.id} cannot transition from {draft.status} to published")

        if author:
            draft.author_name = author
        if tags:
            draft.tags = sorted({t.strip() for t in tags if t and isinstance(t, str)})
        if language:
            draft.language = language.strip().split("-")[0].lower()
        if country:
            draft.country = country.strip().upper()

        draft.status = "published"
        draft.published_at = datetime.utcnow()
        if draft.candidate:
            draft.candidate.status = "published"

        try:
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DraftGenerationError(f"Failed to publish draft: {exc}") from exc

        # Refresh persisted files
        if (self.drafts_dir / f"{draft.slug}.md").exists():
            self._write_markdown_file(draft, self.drafts_dir)
        self._write_markdown_file(draft, self.published_dir)
        self._write_html_file(draft, self.static_blog_dir)
        self._write_manifest()

        # Remove stale draft artefact now that a published version exists
        stale_path = self.drafts_dir / f"{draft.slug}.md"
        if stale_path.exists():
            stale_path.unlink(missing_ok=True)  # type: ignore[attr-defined]

        return draft

    def latest_manifest(self) -> Dict[str, Any]:
        manifest_path = self.published_dir / "feed.json"
        if not manifest_path.exists():
            return {"generated_at": None, "posts": []}
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:  # pragma: no cover - defensive
            return {"generated_at": None, "posts": []}