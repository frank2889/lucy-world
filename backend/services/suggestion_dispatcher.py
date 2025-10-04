from __future__ import annotations

import copy
import threading
import time
from typing import Any, Dict, Iterable, Tuple

import requests

from backend.providers import (
    SuggestionRequest,
    provider_registry,
)


class _InMemoryTTLCache:
    """Lightweight TTL cache for provider responses."""

    def __init__(self, max_entries: int = 2048) -> None:
        self._data: Dict[Tuple[Any, ...], Tuple[float, Dict[str, Any]]] = {}
        self._lock = threading.Lock()
        self._max_entries = max_entries

    def get(self, key: Tuple[Any, ...]) -> Dict[str, Any] | None:
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            expires_at, value = item
            if expires_at < time.time():
                self._data.pop(key, None)
                return None
            return copy.deepcopy(value)

    def set(self, key: Tuple[Any, ...], value: Dict[str, Any], ttl: int) -> None:
        expires_at = time.time() + max(ttl, 0)
        with self._lock:
            if len(self._data) >= self._max_entries:
                # Drop the oldest item (approx) by popping an arbitrary key.
                self._data.pop(next(iter(self._data)), None)
            self._data[key] = (expires_at, copy.deepcopy(value))

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


class SuggestionDispatcher:
    """Dispatches suggestion requests to registered providers with smart caching."""

    def __init__(self, cache_ttl: int = 300, cache_size: int = 2048) -> None:
        self._session = requests.Session()
        self._cache = _InMemoryTTLCache(max_entries=cache_size)
        self._default_ttl = cache_ttl

    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        providers = {}
        for slug, provider in provider_registry.all().items():
            providers[slug] = {
                'slug': slug,
                'display_name': getattr(provider, 'display_name', slug.title()),
                'cache_ttl': getattr(provider, 'cache_ttl', self._default_ttl),
            }
        return providers

    def get_provider(self, slug: str):
        return provider_registry.get(slug)

    def fetch(self, slug: str, request: SuggestionRequest, logger) -> Dict[str, Any]:
        provider = self.get_provider(slug)
        if not provider:
            raise KeyError(f'Unknown provider: {slug}')

        cache_key = (slug, request.cache_key())
        ttl = getattr(provider, 'cache_ttl', self._default_ttl)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return {
                **cached,
                'metadata': {
                    **cached.get('metadata', {}),
                    'cached': True,
                    'cached_ttl': ttl,
                },
            }

        result = provider.fetch(request, self._session, logger)
        if not isinstance(result, dict):
            raise TypeError(f"Provider '{slug}' returned an invalid response")

        metadata = result.get('metadata') or {}
        metadata = {
            **metadata,
            'cached': False,
            'cache_ttl': ttl,
        }
        result['metadata'] = metadata

        if ttl > 0:
            self._cache.set(cache_key, result, ttl=ttl)

        return result

    def fetch_many(
        self,
        slugs: Iterable[str],
        request: SuggestionRequest,
        logger,
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch suggestions from multiple providers.

        Returns a mapping of provider slug to either the provider response or an
        object with an ``error`` key when a provider fails.
        """

        responses: Dict[str, Dict[str, Any]] = {}
        for slug in slugs:
            normalized_slug = (slug or '').strip().lower()
            if not normalized_slug:
                continue
            try:
                responses[normalized_slug] = {
                    'data': self.fetch(normalized_slug, request, logger),
                    'error': None,
                }
            except Exception as exc:  # pragma: no cover - defensive path
                logger.error("Provider %s failed during aggregate fetch: %s", normalized_slug, exc)
                responses[normalized_slug] = {
                    'data': None,
                    'error': str(exc),
                }
        return responses

    def close(self) -> None:
        self._session.close()
        self._cache.clear()
