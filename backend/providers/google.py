from __future__ import annotations

import re
from typing import Any, Dict, List

from requests import Session

from .base import SuggestionProvider, SuggestionRequest, SuggestionResult, register_provider


@register_provider
class GoogleProvider(SuggestionProvider):
    slug = 'google'
    display_name = 'Google'
    cache_ttl = 180

    def fetch(self, request: SuggestionRequest, session: Session, logger) -> SuggestionResult:
        keyword = request.keyword.strip()
        if not keyword:
            raise ValueError('Keyword is required for Google suggestions')

        language = (request.language or '').lower()
        language = re.sub(r'[^a-z]', '', language)
        if len(language) > 2:
            language = language[:2]
        if not language:
            language = 'en'

        country = (request.country or '').upper()
        country = re.sub(r'[^A-Z]', '', country)
        if len(country) > 2:
            country = country[:2]

        params = {
            'client': 'firefox',
            'q': keyword,
            'hl': language,
        }
        if country:
            params['gl'] = country

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36 LucyWorldBot/1.0',
            'Accept': 'application/json, text/javascript;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.google.com/',
        }

        try:
            response = session.get(
                'https://suggestqueries.google.com/complete/search',
                params=params,
                headers=headers,
                timeout=6,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # pragma: no cover - network failures handled upstream
            logger.error('Google suggestion fetch failed: %s', exc)
            raise

        suggestions: List[Dict[str, Any]] = []
        if isinstance(payload, list) and payload:
            # Firefox client returns: [query, [suggestions, ...], ...]
            suggestion_list = payload[1] if len(payload) > 1 else []
            if isinstance(suggestion_list, list):
                for entry in suggestion_list:
                    if isinstance(entry, str):
                        suggestions.append({'phrase': entry})
                    elif isinstance(entry, list) and entry and isinstance(entry[0], str):
                        suggestions.append({'phrase': entry[0]})

        return {
            'keyword': keyword,
            'language': language,
            'country': country or None,
            'suggestions': suggestions,
            'metadata': {
                'approx_volume': len(suggestions),
                'computed_from': 'google_autocomplete',
                'hl': language,
                'gl': country or None,
            },
        }
