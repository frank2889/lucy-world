from __future__ import annotations

import importlib
import pkgutil
from typing import Dict

from .base import SuggestionProvider, SuggestionRequest, SuggestionResult, provider_registry, register_provider


def _auto_discover() -> None:
    """Import all submodules so providers register themselves automatically."""

    package_name = __name__
    for module_info in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
        if module_info.name in {'base', '__pycache__'}:
            continue
        importlib.import_module(f"{package_name}.{module_info.name}")


# Automatically discover built-in providers on import
_auto_discover()


__all__ = [
    'SuggestionProvider',
    'SuggestionRequest',
    'SuggestionResult',
    'provider_registry',
    'register_provider',
]
