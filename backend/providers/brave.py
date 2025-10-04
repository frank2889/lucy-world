from __future__ import annotations

import re
from typing import List

from requests import Session

from .base import SuggestionProvider, SuggestionRequest, SuggestionResult, register_provider


@register_provider
class BraveProvider(SuggestionProvider):
    slug = 'brave'
    display_name = 'Brave Search'
    cache_ttl = 240

    def fetch(self, request: SuggestionRequest, session: Session, logger) -> SuggestionResult:
        keyword = request.keyword.strip()
        language = (request.language or '').lower()
        language = re.sub(r'[^a-z]', '', language)[:2] or 'en'
        source = 'web'
        if request.extras:
            source = str(request.extras.get('source', source)).strip().lower() or 'web'

        params = {
            'q': keyword,
            'source': source,
            'lang': language,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; LucyWorldBot/1.0; +https://lucy.world)',
            'Accept': 'application/json, text/javascript;q=0.9,*/*;q=0.8',
            'Referer': 'https://search.brave.com/',
        }

        try:
            resp = session.get('https://search.brave.com/api/suggest', params=params, headers=headers, timeout=6)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:  # pragma: no cover
            logger.error("Brave suggestion fetch failed: %s", exc)
            raise

        suggestions: List[str] = []
        if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
            suggestions = [str(item).strip() for item in payload[1] if isinstance(item, str)]

        return {
            'keyword': keyword,
            'language': language,
            'suggestions': suggestions,
            'metadata': {
                'approx_volume': len(suggestions),
                'computed_from': 'brave_autocomplete',
                'source': source,
            },
        }
