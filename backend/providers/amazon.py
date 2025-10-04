from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from requests import HTTPError, Session

from .base import SuggestionProvider, SuggestionRequest, SuggestionResult, register_provider


MARKETPLACES: Dict[str, tuple[str, str]] = {
    'US': ('ATVPDKIKX0DER', 'completion.amazon.com'),
    'CA': ('A2EUQ1WTGCTBG2', 'completion.amazon.ca'),
    'MX': ('A1AM78C64UM0Y8', 'completion.amazon.com.mx'),
    'BR': ('A2Q3Y263D00KWC', 'completion.amazon.com.br'),
    'GB': ('A1F83G8C2ARO7P', 'completion.amazon.co.uk'),
    'UK': ('A1F83G8C2ARO7P', 'completion.amazon.co.uk'),
    'DE': ('A1PA6795UKMFR9', 'completion.amazon.de'),
    'FR': ('A13V1IB3VIYZZH', 'completion.amazon.fr'),
    'IT': ('APJ6JRA9NG5V4', 'completion.amazon.it'),
    'ES': ('A1RKKUPIHCS9HS', 'completion.amazon.es'),
    'NL': ('A1805IZSGTT6HS', 'completion.amazon.nl'),
    'BE': ('AMEN7PMS3EDWL', 'completion.amazon.com.be'),
    'SE': ('A2NODRKZP88ZB9', 'completion.amazon.se'),
    'PL': ('A1C3SOZRARQ6R3', 'completion.amazon.pl'),
    'TR': ('A33AVAJ2PDY3EV', 'completion.amazon.com.tr'),
    'AE': ('A2VIGQ35RCS4UG', 'completion.amazon.ae'),
    'SA': ('A17E79C6D8DWNP', 'completion.amazon.sa'),
    'EG': ('A15E5T13P8WH5F', 'completion.amazon.eg'),
    'SG': ('A19VAU5U5O7RUS', 'completion.amazon.sg'),
    'AU': ('A39IBJ37TRP1C6', 'completion.amazon.com.au'),
    'JP': ('A1VC38T7YXB528', 'completion.amazon.co.jp'),
    'IN': ('A21TJRUUN4KGV', 'completion.amazon.in'),
}

MARKETPLACE_ID_MAP: Dict[str, str] = {code: data[0] for code, data in MARKETPLACES.items()}
HOST_BY_COUNTRY: Dict[str, str] = {code: data[1] for code, data in MARKETPLACES.items()}

MARKETPLACE_ID_FALLBACKS: Dict[str, List[str]] = {
    'EG': ['A2VIGQ35RCS4UG', 'A17E79C6D8DWNP'],
}

DEFAULT_ALIAS = 'aps'
DEFAULT_LIMIT = 10
MAX_LIMIT = 20


def _coerce_str(value: Any) -> Optional[str]:
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, list) and value:
        return _coerce_str(value[0])
    return None


def _sanitize_country(value: Optional[str]) -> str:
    if not value:
        return 'US'
    country = re.sub(r'[^A-Z]', '', value.upper())
    return country[:2] or 'US'


def _sanitize_alias(value: Optional[str]) -> str:
    alias = (value or '').strip().lower()
    alias = re.sub(r'[^a-z0-9_-]', '', alias)
    return alias or DEFAULT_ALIAS


def _sanitize_marketplace(value: Optional[str], fallback_country: str) -> str:
    candidate = (value or '').strip().upper()
    candidate = re.sub(r'[^A-Z0-9]', '', candidate)
    if candidate:
        return candidate
    return MARKETPLACE_ID_MAP.get(fallback_country, MARKETPLACE_ID_MAP['US'])


def _normalize_limit(extras: Dict[str, Any] | None) -> int:
    if extras:
        for key in ('limit', 'max', 'results', 'n', 'nresults'):
            candidate = _coerce_str(extras.get(key))
            if candidate and candidate.isdigit():
                try:
                    return max(1, min(int(candidate), MAX_LIMIT))
                except Exception:
                    continue
    return DEFAULT_LIMIT


def _normalize_locale(language: Optional[str], country: str) -> Optional[str]:
    lang = re.sub(r'[^a-z]', '', (language or '').lower())[:2]
    if not lang:
        lang = 'en'
    if not country:
        return None
    return f"{lang}_{country}"


@register_provider
class AmazonProvider(SuggestionProvider):
    slug = 'amazon'
    display_name = 'Amazon'
    cache_ttl = 300

    def _resolve_country(self, request: SuggestionRequest) -> str:
        return _sanitize_country(request.country)

    def _resolve_marketplace(self, country: str, extras: Dict[str, Any] | None) -> str:
        if extras:
            candidate = _coerce_str(
                extras.get('mid')
                or extras.get('marketplace')
                or extras.get('marketplace_id')
                or extras.get('marketplace-id')
            )
            if candidate:
                return _sanitize_marketplace(candidate, country)
        return MARKETPLACE_ID_MAP.get(country, MARKETPLACE_ID_MAP['US'])

    def _resolve_host(self, country: str, extras: Dict[str, Any] | None) -> str:
        if extras:
            candidate = _coerce_str(extras.get('host') or extras.get('endpoint'))
            if candidate:
                return candidate
        return HOST_BY_COUNTRY.get(country, HOST_BY_COUNTRY['US'])

    def _resolve_alias(self, extras: Dict[str, Any] | None) -> str:
        alias_keys = ('alias', 'search_alias', 'search-alias', 'department', 'dept')
        if extras:
            for key in alias_keys:
                candidate = _coerce_str(extras.get(key))
                if candidate:
                    return _sanitize_alias(candidate)
        return DEFAULT_ALIAS

    def fetch(self, request: SuggestionRequest, session: Session, logger) -> SuggestionResult:
        keyword = request.keyword.strip()
        if not keyword:
            return {
                'keyword': '',
                'country': None,
                'alias': DEFAULT_ALIAS,
                'marketplace': None,
                'suggestions': [],
                'metadata': {
                    'approx_volume': 0,
                    'computed_from': 'amazon_autocomplete',
                },
            }

        extras = request.extras if isinstance(request.extras, dict) else None
        country = self._resolve_country(request)
        marketplace_id = self._resolve_marketplace(country, extras)
        host = self._resolve_host(country, extras)
        alias = self._resolve_alias(extras)
        requested_alias = alias
        requested_marketplace = marketplace_id
        limit = _normalize_limit(extras)
        locale = _normalize_locale(request.language, country)

        candidate_marketplaces: List[str] = []
        if marketplace_id and marketplace_id not in candidate_marketplaces:
            candidate_marketplaces.append(marketplace_id)
        for fallback_mid in MARKETPLACE_ID_FALLBACKS.get(country, []):
            if fallback_mid not in candidate_marketplaces:
                candidate_marketplaces.append(fallback_mid)
        if not candidate_marketplaces:
            candidate_marketplaces.append(MARKETPLACE_ID_MAP.get('US', DEFAULT_ALIAS))

        def perform_request(active_alias: str, marketplace: str) -> Dict[str, Any]:
            params = {
                'alias': active_alias,
                'prefix': keyword,
                'mid': marketplace,
                'limit': str(limit),
            }
            if locale:
                params['lop'] = locale
            if extras:
                for key in ('page-type', 'client', 'client-info'):
                    value = _coerce_str(extras.get(key))
                    if value:
                        params[key] = value

            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; LucyWorldBot/1.0; +https://lucy.world)',
                'Accept': 'application/json, text/javascript;q=0.9,*/*;q=0.8',
            }

            url = f"https://{host}/api/2017/suggestions"
            try:
                resp = session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=6,
                )
                resp.raise_for_status()
                return resp.json()
            except HTTPError as exc:
                logger.warning(
                    "Amazon suggestion HTTP error for marketplace %s (alias=%s, status=%s)",
                    marketplace,
                    active_alias,
                    getattr(exc.response, 'status_code', None),
                )
                raise
            except Exception as exc:  # pragma: no cover - network errors handled upstream
                logger.error("Amazon suggestion fetch failed: %s", exc)
                raise

        def parse_payload(payload: Dict[str, Any]) -> tuple[List[str], List[Dict[str, Any]]]:
            out_suggestions: List[str] = []
            structured: List[Dict[str, Any]] = []
            if isinstance(payload, dict):
                raw_suggestions = payload.get('suggestions')
                if isinstance(raw_suggestions, list):
                    for index, item in enumerate(raw_suggestions):
                        text = None
                        suggestion_type = None
                        source = None
                        if isinstance(item, dict):
                            text = _coerce_str(item.get('value'))
                            suggestion_type = _coerce_str(item.get('type'))
                            source = _coerce_str(item.get('suggType'))
                        else:
                            text = _coerce_str(item)
                        if not text:
                            continue
                        out_suggestions.append(text)
                        structured.append({
                            'phrase': text,
                            'rank': index + 1,
                            'type': suggestion_type,
                            'source': source,
                        })
            return out_suggestions, structured

        payload: Dict[str, Any] | None = None
        suggestions: List[str] = []
        structured: List[Dict[str, Any]] = []
        alias_fallback_used = False
        marketplace_fallback_used = False
        used_marketplace = requested_marketplace

        for idx, mid in enumerate(candidate_marketplaces):
            try:
                payload = perform_request(alias, mid)
            except HTTPError as exc:
                status = getattr(exc.response, 'status_code', None)
                if status in (400, 403) and idx + 1 < len(candidate_marketplaces):
                    marketplace_fallback_used = True
                    continue
                raise

            suggestions, structured = parse_payload(payload)
            current_alias = alias
            alias_fallback_used = False
            if not suggestions and alias != DEFAULT_ALIAS:
                try:
                    payload = perform_request(DEFAULT_ALIAS, mid)
                    parsed_suggestions, parsed_structured = parse_payload(payload)
                    if parsed_suggestions:
                        suggestions = parsed_suggestions
                        structured = parsed_structured
                        current_alias = DEFAULT_ALIAS
                        alias_fallback_used = True
                except HTTPError as exc:
                    status = getattr(exc.response, 'status_code', None)
                    if status in (400, 403) and idx + 1 < len(candidate_marketplaces):
                        marketplace_fallback_used = True
                        continue
                    raise

            if suggestions:
                alias = current_alias
                used_marketplace = mid
                if idx > 0:
                    marketplace_fallback_used = True
                break

            if idx + 1 < len(candidate_marketplaces):
                marketplace_fallback_used = True
                continue
            else:
                used_marketplace = mid
                break

        metadata: Dict[str, Any] = {
            'approx_volume': len(suggestions),
            'computed_from': 'amazon_autocomplete',
            'marketplace_code': used_marketplace,
            'alias': alias,
            'requested_alias': requested_alias,
            'endpoint': host,
            'requested_marketplace': requested_marketplace,
        }
        if alias_fallback_used:
            metadata['fallback'] = 'alias'
        if marketplace_fallback_used and used_marketplace and used_marketplace != requested_marketplace:
            metadata['fallback_marketplace'] = used_marketplace
        if structured:
            metadata['structured'] = structured
        if isinstance(payload, dict):
            slim_extra = {
                key: payload[key]
                for key in ('alias', 'prefix')
                if key in payload
            }
            if slim_extra:
                metadata['extra'] = slim_extra

        return {
            'keyword': keyword,
            'country': country,
            'alias': alias,
            'marketplace': used_marketplace,
            'suggestions': suggestions,
            'metadata': metadata,
        }