#!/usr/bin/env python3
"""Clean up locale files that contain unresolved translation tokens.

Some of our automated translation runs left intermediate tokens such as
"__BR_123__" or "__ פ_0__" when the translation engine tried to localise the
protective markers we wrap around brand names or ICU-style placeholders. This
script scans every non-English locale, compares it to the English reference,
and restores any lingering tokens back to their intended text (brand names or
placeholders like {{amount}}).
"""
from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANG_DIR = ROOT / "languages"
EN_FILE = LANG_DIR / "en" / "locale.json"

BRANDS = [
    "Lucy World",
    "Google",
    "YouTube",
    "Amazon",
    "App Store",
    "Google Play",
    "Play Store",
    "TikTok",
    "Pinterest",
    "Instagram",
    "Etsy",
    "eBay",
    "Bing",
    "Baidu",
    "Naver",
    "Yandex",
    "DuckDuckGo",
    "Qwant",
    "Brave",
    "CSV",
    "AI",
]

# Anything wrapped in double braces should remain untouched.
ICU_PATTERN = re.compile(r"\{\{[^}]+\}\}")
# Residual tokens always keep a double-underscore prefix/suffix – even when the
# interior characters were transliterated. The minimal, non-greedy match keeps
# each token separate (e.g. '__BR_123__', '__ פ_0__').
TOKEN_PATTERN = re.compile(r"__.*?__")


def load_locale(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_locale(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def normalise_value(en_text: str, local_text: str) -> tuple[str, bool, bool]:
    """Replace leftover tokens in *local_text* using cues from *en_text*.

    Returns the normalised string, a flag indicating if the value changed, and
    a flag signalling that unresolved tokens remain."""
    if not isinstance(local_text, str):
        return local_text, False, False

    tokens = deque(TOKEN_PATTERN.findall(local_text))

    updated_text = local_text
    changed = False

    placeholders = ICU_PATTERN.findall(en_text)
    brands_in_en = [brand for brand in BRANDS if brand in en_text]

    def replace_from_queue(items: list[str]) -> None:
        nonlocal updated_text, changed
        for item in items:
            if item in updated_text:
                continue
            while tokens:
                token = tokens.popleft()
                updated_text = updated_text.replace(token, item, 1)
                changed = True
                break

    # Placeholders are positional – restore them first.
    replace_from_queue(placeholders)
    # Then restore any protected brand names.
    replace_from_queue(brands_in_en)

    leftovers = bool(tokens) or bool(TOKEN_PATTERN.search(updated_text)) or "_" in updated_text
    if not leftovers:
        for item in placeholders + brands_in_en:
            if item and (re.search(fr"{re.escape(item)}\d+", updated_text) or re.search(fr"\d+{re.escape(item)}", updated_text)):
                leftovers = True
                break
    if not leftovers and re.search(r"\d{5,}", updated_text):
        leftovers = True


    if leftovers:
        cleaned_text = TOKEN_PATTERN.sub("", updated_text)
        if "_" in cleaned_text:
            cleaned_text = cleaned_text.replace("_", "")

        for item in placeholders + brands_in_en:
            if item:
                pattern_after = re.compile(fr"{re.escape(item)}\d+")
                pattern_before = re.compile(fr"\d+{re.escape(item)}")
                cleaned = pattern_after.sub(item, cleaned_text)
                cleaned = pattern_before.sub(item, cleaned)
                cleaned_text = cleaned

        # Replace leftover hashed markers (phXXXX / brXXXX) with placeholders or brands.
        placeholder_queue = (p for p in placeholders if p not in cleaned_text)
        for match in re.finditer(r"(?i)ph\d+", cleaned_text):
            try:
                replacement = next(placeholder_queue)
            except StopIteration:
                break
            cleaned_text = cleaned_text.replace(match.group(0), replacement, 1)

        brand_queue = (b for b in brands_in_en if b not in cleaned_text)
        for match in re.finditer(r"(?i)br\d+", cleaned_text):
            try:
                replacement = next(brand_queue)
            except StopIteration:
                break
            cleaned_text = cleaned_text.replace(match.group(0), replacement, 1)

        cleaned_text = re.sub(r"\d{5,}", "", cleaned_text)
        cleaned_text = re.sub(r"\b(br|ph|fh)\b", "", cleaned_text, flags=re.IGNORECASE)

        leftovers = bool(TOKEN_PATTERN.search(cleaned_text))
        if cleaned_text != updated_text:
            updated_text = cleaned_text
            changed = True

    return updated_text, changed, leftovers


def main() -> None:
    if not EN_FILE.exists():
        raise SystemExit(f"English reference missing at {EN_FILE}")

    en_data = load_locale(EN_FILE)
    en_strings = en_data.get("strings", {})

    touched_files = 0

    for locale_dir in sorted(LANG_DIR.iterdir()):
        if not locale_dir.is_dir() or locale_dir.name == "en":
            continue
        locale_file = locale_dir / "locale.json"
        if not locale_file.exists():
            continue

        data = load_locale(locale_file)
        strings = data.get("strings", {})
        file_changed = False

        for key, value in list(strings.items()):
            en_value = en_strings.get(key)
            if not isinstance(en_value, str):
                continue
            new_value, changed, leftovers = normalise_value(en_value, value)
            if changed:
                strings[key] = new_value
                file_changed = True
                if leftovers:
                    print(f"⚠️  Residual token in {locale_dir.name}:{key} -> {new_value}")

        if file_changed:
            data["strings"] = strings
            save_locale(locale_file, data)
            touched_files += 1
            print(f"✅ Fixed tokens in {locale_dir.name}/locale.json")

    if touched_files == 0:
        print("All locale files already clean – nothing to do.")
    else:
        print(f"Done. Updated {touched_files} locale file(s).")


if __name__ == "__main__":
    main()
