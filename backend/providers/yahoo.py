from __future__ import annotations

import re
from typing import List

from requests import Session

from .base import SuggestionProvider, SuggestionRequest, SuggestionResult, register_provider


@register_provider
class YahooProvider(SuggestionProvider):
    slug = 'yahoo'
    display_name = 'Yahoo'
    cache_ttl = 240

    def fetch(self, request: SuggestionRequest, session: Session, logger) -> SuggestionResult:
        keyword = request.keyword.strip()
        language = (request.language or '').lower()
        language = re.sub(r'[^a-z]', '', language)[:2] or 'en'
        country = (request.country or '').upper()
        country = re.sub(r'[^A-Z]', '', country)
        if len(country) > 2:
            country = country[:2]

        limit_param = '10'
        if request.extras and 'limit' in request.extras:
            limit_param = str(request.extras.get('limit'))
        elif request.extras:
            for alias in ('nresults', 'n', 'results'):
                if alias in request.extras:
                    limit_param = str(request.extras[alias])
                    break

        try:
            limit = max(1, min(int(limit_param), 20))
        except Exception:
            limit = 10

        params = {
            'output': 'json',
            'command': keyword,
            'nresults': str(limit),
            'intl': language,
            'region': (country or '').lower(),
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; LucyWorldBot/1.0; +https://lucy.world)',
            'Accept': 'application/json, text/javascript;q=0.9,*/*;q=0.8',
            'Referer': 'https://search.yahoo.com/',
        }

        try:
            resp = session.get('https://sugg.search.yahoo.net/sg/', params=params, headers=headers, timeout=6)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:  # pragma: no cover
            logger.error("Yahoo suggestion fetch failed: %s", exc)
            raise

        gossip = payload.get('gossip', {}) if isinstance(payload, dict) else {}
        results = gossip.get('results') if isinstance(gossip, dict) else None
        suggestions: List[str] = []
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict) and item.get('key'):
                    suggestions.append(str(item['key']).strip())

        return {
            'keyword': keyword,
            'language': language,
            'country': country or None,
            'suggestions': suggestions,
            'metadata': {
                'approx_volume': len(suggestions),
                'computed_from': 'yahoo_autocomplete',
            },
        }
