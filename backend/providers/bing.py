from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from requests import Session

from .base import SuggestionProvider, SuggestionRequest, SuggestionResult, register_provider


def _sanitize_language(value: Optional[str]) -> str:
    lang = re.sub(r'[^a-z]', '', (value or '').lower())
    return lang[:2] or 'en'


def _sanitize_country(value: Optional[str]) -> str:
    country = re.sub(r'[^A-Z]', '', (value or '').upper())
    if len(country) >= 2:
        return country[:2]
    return 'US'


def _coerce_str(value: Any) -> Optional[str]:
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, list) and value:
        return _coerce_str(value[0])
    return None


@register_provider
class BingProvider(SuggestionProvider):
    slug = 'bing'
    display_name = 'Bing'
    cache_ttl = 300

    def _normalize_market(self, extras: Dict[str, Any] | None, language: str, country: str) -> str:
        candidate = None
        if extras:
            for key in ('mkt', 'market', 'market_code'):
                candidate = _coerce_str(extras.get(key))
                if candidate:
                    break

        if candidate:
            candidate = candidate.replace('_', '-').strip()
            parts = [part for part in candidate.split('-') if part]
            if len(parts) >= 2:
                lang_part = _sanitize_language(parts[0])
                country_part = _sanitize_country(parts[1])
                return f"{lang_part}-{country_part}"
            if parts:
                lang_part = _sanitize_language(parts[0])
                return f"{lang_part}-{country}" if country else lang_part

        return f"{language}-{country}" if country else language

    def fetch(self, request: SuggestionRequest, session: Session, logger) -> SuggestionResult:
        keyword = request.keyword.strip()
        if not keyword:
            return {
                'keyword': '',
                'language': None,
                'country': None,
                'market': None,
                'suggestions': [],
                'metadata': {
                    'approx_volume': 0,
                    'computed_from': 'bing_autocomplete',
                    'api_market': None,
                },
            }

        language = _sanitize_language(request.language)
        country = _sanitize_country(request.country)
        extras = request.extras if isinstance(request.extras, dict) else None
        market = self._normalize_market(extras, language, country)
        api_market = market.replace('_', '-').lower() if market else None

        params = {
            'query': keyword,
        }
        if api_market:
            params['mkt'] = api_market

        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; LucyWorldBot/1.0; +https://lucy.world)',
            'Accept': 'application/json, text/javascript;q=0.9,*/*;q=0.8',
        }

        try:
            resp = session.get('https://api.bing.com/osjson.aspx', params=params, headers=headers, timeout=6)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:  # pragma: no cover - network failure handled upstream
            logger.error("Bing suggestion fetch failed: %s", exc)
            raise

        suggestions: List[Dict[str, Any]] = []
        if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
            supplemental = payload[2] if len(payload) > 2 and isinstance(payload[2], list) else None
            for index, item in enumerate(payload[1]):
                if not isinstance(item, str):
                    continue
                text = item.strip()
                if not text:
                    continue
                suggestion: Dict[str, Any] = {
                    'phrase': text,
                    'rank': index + 1,
                }
                if isinstance(supplemental, list) and index < len(supplemental):
                    supplement = supplemental[index]
                    if isinstance(supplement, str) and supplement.strip():
                        suggestion['snippet'] = supplement.strip()
                    elif isinstance(supplement, dict):
                        clean_meta = {k: v for k, v in supplement.items() if isinstance(k, str)}
                        if clean_meta:
                            suggestion['meta'] = clean_meta
                suggestions.append(suggestion)

        return {
            'keyword': keyword,
            'language': language,
            'country': country,
            'market': market,
            'suggestions': suggestions,
            'metadata': {
                'approx_volume': len(suggestions),
                'computed_from': 'bing_autocomplete',
                'api_market': api_market,
            },
        }