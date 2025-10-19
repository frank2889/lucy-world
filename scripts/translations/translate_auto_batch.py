#!/usr/bin/env python3
"""
Auto-translate locale files from English reference with NO English fallback.
- Preserves placeholders like {{code}} and {{amount}}
- Preserves brand names (Lucy World, Google, YouTube, Amazon, App Store, Play Store, TikTok, Pinterest, Instagram, Etsy, eBay, Bing, Baidu, Naver, Yandex, DuckDuckGo, Qwant, Brave)
- Translates only keys that are missing or still English/ASCII
- Processes given language codes in batches

Usage:
  python3 scripts/translations/translate_auto_batch.py af am ar az be
"""
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    from deep_translator import GoogleTranslator
except Exception as e:
    print("ERROR: deep_translator not installed. Run: pip install deep-translator")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
LANGS_DIR = ROOT / "languages"
EN_FILE = LANGS_DIR / "en" / "locale.json"

# Brand and proper nouns to preserve
BRANDS = [
    "Lucy World", "Google", "YouTube", "Amazon", "App Store", "Google Play",
    "Play Store", "TikTok", "Pinterest", "Instagram", "Etsy", "eBay", "Bing",
    "Baidu", "Naver", "Yandex", "DuckDuckGo", "Qwant", "Brave", "CSV", "AI"
]

# Map from our codes to GoogleTranslator language codes when they differ
LANG_CODE_MAP = {
    "he": "iw",  # Hebrew legacy code
    "zh": "zh-CN",
    "pt": "pt",
    "sr": "sr",
    "jw": "jv",  # just in case
}

PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}]+\}\}")
ASCII_PATTERN = re.compile(r"^[\s\d\W\x00-\x7F]+$")


def load_json(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(p: Path, data: Dict[str, Any]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def needs_translation(value: str, en_value: str) -> bool:
    if not isinstance(value, str):
        return False
    # Already translated if it contains any non-ascii letter
    if not ASCII_PATTERN.match(value):
        return False
    # If identical to English, translate
    if value.strip() == en_value.strip():
        return True
    # If clearly English words (contains a-z letters) and only ascii, translate
    LETTERS = re.compile(r"[A-Za-z]")
    if LETTERS.search(value):
        return True
    return False


def protect_tokens(text: str):
    """Protect placeholders and brands by swapping them for stable tokens."""
    tokens = {}

    placeholder_index = 0
    for placeholder in PLACEHOLDER_PATTERN.findall(text):
        key = f"@@{placeholder_index}@@"
        tokens[key] = placeholder
        text = text.replace(placeholder, key)
        placeholder_index += 1

    brand_index = 0
    for brand in BRANDS:
        if brand in text:
            key = f"##{brand_index}##"
            tokens[key] = brand
            text = text.replace(brand, key)
            brand_index += 1

    return text, tokens


def restore_tokens(text: str, tokens: Dict[str, str]):
    for k, v in tokens.items():
        text = text.replace(k, v)
    return text


def translate_text(text: str, target_lang: str) -> str:
    if not text:
        return text
    lang = LANG_CODE_MAP.get(target_lang, target_lang)
    protected, tokens = protect_tokens(text)
    translated = GoogleTranslator(source="auto", target=lang).translate(protected)
    return restore_tokens(translated, tokens)


def translate_locale(target_lang: str) -> Dict[str, int]:
    en = load_json(EN_FILE)
    en_strings = en.get("strings", {})

    target_file = LANGS_DIR / target_lang / "locale.json"
    if not target_file.exists():
        print(f"⚠️  {target_lang}: locale.json not found, creating from en")
        data = {"lang": target_lang, "dir": "rtl" if target_lang in {"ar", "he", "fa", "ur"} else "ltr", "strings": {}}
    else:
        data = load_json(target_file)

    strings = data.get("strings", {})
    added = 0
    updated = 0
    skipped = 0

    # Ensure all keys exist
    for key, en_value in en_strings.items():
        current = strings.get(key)
        if current is None:
            # Need translation
            strings[key] = translate_text(str(en_value), target_lang)
            added += 1
        else:
            if needs_translation(str(current), str(en_value)):
                strings[key] = translate_text(str(en_value), target_lang)
                updated += 1
            else:
                skipped += 1

    data["strings"] = dict(sorted(strings.items()))
    save_json(target_file, data)
    return {"added": added, "updated": updated, "skipped": skipped, "total": len(en_strings)}


def main(args: List[str]):
    if not EN_FILE.exists():
        print(f"❌ English reference not found: {EN_FILE}")
        sys.exit(1)

    if not args:
        print("Usage: translate_auto_batch.py <lang1> <lang2> ...")
        sys.exit(1)

    for lang in args:
        try:
            stats = translate_locale(lang)
            print(f"✅ {lang}: +{stats['added']} added, {stats['updated']} updated, {stats['skipped']} kept (out of {stats['total']})")
        except Exception as e:
            print(f"❌ {lang}: {e}")

if __name__ == "__main__":
    main(sys.argv[1:])
