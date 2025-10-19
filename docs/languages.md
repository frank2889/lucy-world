# 🌐 languages.md — Translation Policy & Validation Blueprint

## 1. Purpose
This document defines the translation enforcement rules for all locales in `/languages/`.
No default language or English fallback is ever permitted.

---

## 2. Directory Structure

```text
/languages/
  ├── en/
  │   └── locale.json
  ├── zu/
  │   ├── locale.json
  │   ├── missing.json
  │   └── status.json
  ├── fa/
  │   ├── locale.json
  │   ├── missing.json
  │   └── status.json
  └── summary.json
```

---

## 3. Validation Behavior

- **No fallback allowed** — English text is never used as a default.
- **Auto placeholders** — scripts insert `[NEEDS TRANSLATION: …]`
  markers instead of English fallbacks.
- **Per-language logs** — machine runs record progress; regenerate the
  reports after each edit batch.
- **English detection** — ASCII-only strings in non-English files are
  treated as suspect and flagged.
- **Completion tracking** — `status.json` stores total, translated, and
  completion percentage.
- **CI enforcement** — the validator exits with code `1` if any
  translation is missing.

---

## 4. Automation Workflow

### 4.1 Scripts

- `scripts/translations/translate_auto_batch.py` — wraps Google
  Translate, protects placeholders and brands, and fills missing or
  English-looking strings for a list of locales.
- `scripts/auto_translate_all.py` — iterates through every locale, applies
  professional translations when available, and falls back to
  `[NEEDS TRANSLATION]` markers elsewhere.

Legacy batch helpers have been retired; use `translate_auto_batch.py`
for curated runs and delete any ad-hoc scripts once a translation push
lands.

### 4.2 Day-to-day Flow

1. **Refresh English source** — update `languages/en/locale.json` first;
  it is the reference file.
2. **Generate machine assists** — run `python3
  scripts/translations/translate_auto_batch.py <lang1> <lang2> ...`
  for the locales you touched, or execute
  `python3 scripts/auto_translate_all.py` to sweep every language.
3. **Review markers** — search for `[NEEDS TRANSLATION:` and
  `MISSING language for string` in the updated locales; translators
  replace these with production-ready copy.
4. **Sort + lint** — scripts sort keys and ensure UTF-8; manual edits
  must keep alphabetical order and the trailing newline.
5. **Status reporting** — regenerate progress reports (status + missing
  summaries) and commit them alongside locale updates once the tooling
  is available.
6. **CI guardrail** — the translation validator fails the pipeline if
  any placeholder markers remain.

### 4.3 Safeguards Embedded in Scripts

- **Placeholder protection** — tokens like `{{amount}}` and `{{code}}`
  are shielded to avoid mistranslation.
- **Brand list** — Lucy World and partner platform names are locked and
  reinserted verbatim after translation.
- **Legacy language code mapping** — remaps tricky codes (for example
  `he → iw`, `zh → zh-CN`) before calling GoogleTranslator.

### 4.4 Structured Metadata Synchronisation

- Run `python3 scripts/translations/update_structured_data.py` after
  changing any `meta.title`, `meta.description`, or `meta.keywords`
  strings so each locale’s `structured.json` mirrors the translated
  metadata.
- The script removes the `SearchAction` block to stop Google Search
  Console from surfacing fake query URLs (`?q={search_term_string}`).
- Re-run the script before deployments that touch locale metadata to
  avoid regressions across the 100+ language folders.

---

## 5. CI Integration
Add this to `.github/workflows/ci.yml`:

```yaml
- name: Validate translations
  run: python tools/translate.py
```

Build fails if any locale is incomplete.

---

## 6. Developer Notes
- Never add more than one translation handler (`translate.py` only).
- If `missing.json` or `status.json` shows English text, translation batch is invalid.
- Translators work in batches until each locale reaches 100%.

---

✅ **Definition of Done**
- [ ] No `[NEEDS TRANSLATION:` or `MISSING` markers remain in any
  locale.  
- [ ] No English text in non-English files (unless the phrase is a
  protected brand).  
- [ ] All locales synchronized with the English source and sorted
  alphabetically.  
- [ ] CI translation validator exits with `0`.
