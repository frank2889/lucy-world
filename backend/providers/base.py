from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Tuple
import threading


@dataclass(frozen=True)
class SuggestionRequest:
    """Normalized request information shared with providers."""

    keyword: str
    language: str | None = None
    country: str | None = None
    extras: Mapping[str, Any] | None = None

    def cache_key(self) -> Tuple[Any, ...]:
        """Return a hashable cache key that distinguishes this request."""
        extras_items: Iterable[Tuple[str, Any]] = ()
        if self.extras:
            # Normalize extras into a sorted tuple of strings for hashing
            extras_items = tuple(sorted((str(k), str(v)) for k, v in self.extras.items()))
        return (
            self.keyword.lower(),
            (self.language or '').lower(),
            (self.country or '').upper(),
            extras_items,
        )


SuggestionResult = Dict[str, Any]


class SuggestionProvider:
    """Base class for suggestion providers.

    Subclasses must define a unique ``slug`` attribute and implement ``fetch``.
    Optional attributes:
        - display_name: human readable label
        - cache_ttl: recommended TTL in seconds for this provider (dispatcher may override)
    """

    slug: str = ''
    display_name: str = ''
    cache_ttl: int = 300

    def fetch(self, request: SuggestionRequest, session, logger) -> SuggestionResult:
        raise NotImplementedError


class ProviderRegistry:
    """In-memory registry for suggestion providers."""

    def __init__(self) -> None:
        self._providers: Dict[str, SuggestionProvider] = {}
        self._lock = threading.Lock()

    def register(self, provider_cls: type[SuggestionProvider]) -> type[SuggestionProvider]:
        instance = provider_cls()
        slug = getattr(instance, 'slug', '').strip().lower()
        if not slug:
            raise ValueError(f"Provider {provider_cls!r} must define a non-empty slug")
        with self._lock:
            if slug in self._providers:
                raise ValueError(f"Duplicate provider slug detected: {slug}")
            self._providers[slug] = instance
        return provider_cls

    def get(self, slug: str) -> SuggestionProvider | None:
        return self._providers.get(slug.lower())

    def all(self) -> Dict[str, SuggestionProvider]:
        return dict(self._providers)


provider_registry = ProviderRegistry()


def register_provider(provider_cls: type[SuggestionProvider]) -> type[SuggestionProvider]:
    """Class decorator to register suggestion providers."""

    return provider_registry.register(provider_cls)
