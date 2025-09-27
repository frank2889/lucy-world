#!/usr/bin/env python3
"""
Generate per-language registry files under languages/registry/ based on languages/languages.json
and Google RTL conventions. It only writes files that don't exist yet unless --force is passed.
"""
import json
import os
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG_LIST = os.path.join(ROOT, 'languages', 'languages.json')
REG_DIR = os.path.join(ROOT, 'languages', 'registry')

RTL_LANGS = { 'ar','he','fa','ur' }
ALIASES = {
    # legacy/alternate codes that Google sometimes uses
    'iw': 'he',  # old Hebrew
    'ji': 'yi',  # old Yiddish
    'in': 'id',  # old Indonesian
}

DISPLAY_NAMES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian', 'az': 'Azerbaijani',
    'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'my': 'Burmese',
    'ca': 'Catalan', 'zh': 'Chinese', 'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
    'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'fi': 'Finnish', 'fr': 'French',
    'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati',
    'ht': 'Haitian Creole', 'ha': 'Hausa', 'he': 'Hebrew', 'hi': 'Hindi', 'hu': 'Hungarian', 'is': 'Icelandic',
    'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese', 'jv': 'Javanese',
    'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer', 'rw': 'Kinyarwanda', 'ko': 'Korean', 'ku': 'Kurdish',
    'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish',
    'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori',
    'mr': 'Marathi', 'mn': 'Mongolian', 'ne': 'Nepali', 'no': 'Norwegian', 'ny': 'Nyanja (Chichewa)',
    'or': 'Odia (Oriya)', 'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi',
    'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scottish Gaelic', 'sr': 'Serbian', 'st': 'Sesotho',
    'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali',
    'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish', 'tl': 'Tagalog (Filipino)',
    'tg': 'Tajik', 'ta': 'Tamil', 'tt': 'Tatar', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'tk': 'Turkmen',
    'uk': 'Ukrainian', 'ur': 'Urdu', 'ug': 'Uyghur', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh',
    'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true', help='Overwrite existing files')
    args = ap.parse_args()

    os.makedirs(REG_DIR, exist_ok=True)

    with open(LANG_LIST, 'r', encoding='utf-8') as f:
        langs = (json.load(f).get('languages') or [])

    # keep only unique 2-letter codes
    uniq = []
    for l in langs:
        c = str(l).split('-')[0].lower()
        if len(c) == 2 and c.isalpha() and c not in uniq:
            uniq.append(c)

    for code in uniq:
        path = os.path.join(REG_DIR, f'{code}.json')
        if os.path.exists(path) and not args.force:
            continue
        data = {
            'code': code,
            'name': DISPLAY_NAMES.get(code, code),
            'rtl': code in RTL_LANGS,
            'aliases': [alias for alias, target in ALIASES.items() if target == code],
            'hreflang': code,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Generated/updated {len(uniq)} registry files in {REG_DIR}")

if __name__ == '__main__':
    main()
