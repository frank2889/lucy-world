#!/usr/bin/env python3
"""Update market hreflang configurations using CLDR official language data.

This script trims each market's hreflang.json to the intersection of
(1) languages that have official status in the territory according to the
    Unicode CLDR supplemental data, and
(2) languages that Lucy World currently supports (languages/ directories).

It also refreshes markets/index.json so downstream clients can rely on the
same source of truth. Markets that end up with no supported official language
retain only an x-default alternate entry, and their defaultLocale is set to
null so that follow-up work can add the missing translation.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
from xml.etree import ElementTree as ET

import language_data
from langcodes import Language

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LANGUAGES_ROOT = PROJECT_ROOT / "languages"
MARKETS_ROOT = PROJECT_ROOT / "markets"
LANG_LIST_FILE = LANGUAGES_ROOT / "languages.json"
INDEX_FILE = MARKETS_ROOT / "index.json"
CLDR_SUPPLEMENTAL = Path(language_data.__file__).resolve().parent / "data" / "supplementalData.xml"

# Manual overrides for territories that lack explicit official languages in CLDR or
# where we want to express a pragmatic default that is still justifiable.
MANUAL_LANGUAGE_OVERRIDES: Dict[str, Sequence[str]] = {
    # Antarctica: treaty system works in English and French.
    "AQ": ("en", "fr"),
    # Bouvet Island: dependency of Norway, no permanent population, default to Norwegian.
    "BV": ("no",),
    # Faroe Islands: Faroese and Danish are official; we currently support Danish only.
    "FO": ("da",),
    # South Georgia and South Sandwich Islands: administered by UK, English de facto official.
    "GS": ("en",),
    # Heard Island and McDonald Islands: Australian external territory, English used officially.
    "HM": ("en",),
    # French Southern Territories: administered by France, French is official.
    "TF": ("fr",),
}

# Map certain CLDR language subtags to Lucy World's canonical two-letter codes.
LANGUAGE_ALIASES: Dict[str, str] = {
    "nb": "no",  # Norwegian Bokmål → generic Norwegian
    "nn": "no",  # Norwegian Nynorsk → generic Norwegian
    "fil": "tl",  # Filipino → Tagalog (our supported locale)
    "ckb": "ku",  # Central Kurdish → Kurdish
    "sd": "sd",  # ensure consistency when variant scripts appear
}

STATUS_PRIORITY = {
    "official": 0,
    "de_facto_official": 1,
    "official_regional": 2,
}


@dataclass(frozen=True)
class LocaleConfig:
    code: str
    hreflang: str
    path: str
    canonical: str


def load_supported_languages() -> set[str]:
    with LANG_LIST_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    languages = data.get("languages") if isinstance(data, dict) else []
    return {str(code).lower() for code in languages}


def _normalize_language_tag(tag: str) -> str:
    """Return Lucy World's canonical two-letter language code for a CLDR tag."""
    tag = tag or ""
    tag = tag.replace("_", "-")
    try:
        language = Language.get(tag)
        base = language.language or ""
    except Exception:
        base = tag.split("-")[0]
    base = (base or "").lower()
    if base in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[base]
    return base


def _load_cldr_territory_info() -> Dict[str, ET.Element]:
    tree = ET.parse(CLDR_SUPPLEMENTAL)
    root = tree.getroot()
    territory_info = root.find("territoryInfo")
    if territory_info is None:
        raise RuntimeError("Could not locate <territoryInfo> in CLDR supplemental data")
    info: Dict[str, ET.Element] = {}
    for territory in territory_info.findall("territory"):
        code = territory.attrib.get("type", "").upper()
        if len(code) == 2 and code.isalpha():
            info[code] = territory
    return info


def _official_languages_for(
    code: str,
    territory_node: ET.Element | None,
    supported: set[str],
) -> List[str]:
    if code in MANUAL_LANGUAGE_OVERRIDES:
        langs = [lang for lang in MANUAL_LANGUAGE_OVERRIDES[code] if lang in supported]
        return list(dict.fromkeys(langs))

    if territory_node is None:
        return []

    candidates: Dict[str, tuple[int, float]] = {}
    for lang_node in territory_node.findall("languagePopulation"):
        status = lang_node.attrib.get("officialStatus")
        if not status:
            continue
        normalized = _normalize_language_tag(lang_node.attrib.get("type", ""))
        if not normalized or normalized not in supported:
            continue
        percent = float(lang_node.attrib.get("populationPercent", "0") or 0.0)
        rank = STATUS_PRIORITY.get(status, 99)
        current = candidates.get(normalized)
        if current is None or (rank, -percent) < (current[0], -current[1]):
            candidates[normalized] = (rank, percent)
    ordered = sorted(
        candidates.items(),
        key=lambda item: (item[1][0], -item[1][1], item[0])
    )
    return [code for code, _ in ordered]


def _build_locale_entries(code: str, languages: Iterable[str]) -> List[LocaleConfig]:
    entries: List[LocaleConfig] = []
    for lang in languages:
        lang_code = lang.lower()
        hreflang = f"{lang_code}-{code}"
        path = f"/{lang_code}"
        canonical = f"https://lucy.world/{lang_code}"
        entries.append(LocaleConfig(code=lang_code, hreflang=hreflang, path=path, canonical=canonical))
    return entries


def _write_hreflang_file(code: str, locales: Sequence[LocaleConfig]) -> None:
    market_dir = MARKETS_ROOT / code
    market_dir.mkdir(parents=True, exist_ok=True)
    default_locale = f"{locales[0].code}-{code}" if locales else None
    data = {
        "country": code,
        "defaultLocale": default_locale,
        "locales": [
            {
                "code": locale.code,
                "hreflang": locale.hreflang,
                "path": locale.path,
                "canonical": locale.canonical,
            }
            for locale in locales
        ],
        "alternate": [
            {
                "hreflang": "x-default",
                "href": "https://lucy.world/",
            }
        ],
    }
    with (market_dir / "hreflang.json").open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def _write_index(index_payload: List[dict]) -> None:
    with INDEX_FILE.open("w", encoding="utf-8") as f:
        json.dump({"markets": index_payload}, f, indent=2)
        f.write("\n")


def main() -> None:
    supported = load_supported_languages()
    territory_info = _load_cldr_territory_info()

    market_codes = [
        name.upper() for name in os.listdir(MARKETS_ROOT)
        if len(name) == 2 and name.isalpha() and (MARKETS_ROOT / name).is_dir()
    ]
    market_codes.sort()

    updated: List[str] = []
    missing: List[str] = []
    index_payload: List[dict] = []

    for code in market_codes:
        territory_node = territory_info.get(code)
        languages = _official_languages_for(code, territory_node, supported)
        locales = _build_locale_entries(code, languages)
        _write_hreflang_file(code, locales)
        if locales:
            default_locale = f"{locales[0].code}-{code}"
            canonical = locales[0].canonical
            updated.append(code)
        else:
            default_locale = None
            canonical = None
            missing.append(code)
        index_payload.append({
            "code": code,
            "defaultLocale": default_locale,
            "canonical": canonical,
            "locales": [locale.code for locale in locales],
        })

    _write_index(index_payload)

    if missing:
        print("Markets without supported official languages:")
        for code in missing:
            print(f"  - {code}")
    else:
        print("All markets updated with at least one supported official language.")


if __name__ == "__main__":
    main()
