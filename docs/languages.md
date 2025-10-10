# 🌐 languages.md — Translation Policy & Validation Blueprint

## 1. Purpose
This document defines the translation enforcement rules for all locales in `/languages/`.
No default language or English fallback is ever permitted.

---

## 2. Directory Structure
```
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

| Function | Description |
|-----------|--------------|
| **No fallback allowed** | English text is never used as default. |
| **Auto placeholders** | Missing strings replaced with `MISSING language for string 'xyz'`. |
| **Per-language logs** | Each locale folder has `missing.json` and `status.json`. |
| **English detection** | Flags any English-looking word in non-English files. |
| **Completion tracking** | `status.json` stores total, translated, and completion %. |
| **CI enforcement** | Exits with code `1` if any translation is missing. |

---

## 4. Example of Missing Log
```json
[
  "cta.upgrade_button",
  "entitlements.sidebar.ai_locked",
  "billing.status.loading_credit_packs"
]
```

---

## 5. Example of Status Log
```json
{
  "language": "zu",
  "total_keys": 850,
  "translated": 814,
  "missing": 36,
  "completion_percent": 95.76
}
```

---

## 6. CI Integration
Add this to `.github/workflows/ci.yml`:
```yaml
- name: Validate translations
  run: python tools/translate.py
```

Build fails if any locale is incomplete.

---

## 7. Developer Notes
- Never add more than one translation handler (`translate.py` only).
- If `missing.json` or `status.json` shows English text, translation batch is invalid.
- Translators work in batches until each locale reaches 100%.

---

✅ **Definition of Done**
- [ ] No `MISSING` entries remain.  
- [ ] No English text in non-English files.  
- [ ] `completion_percent` = 100% for all active locales.  
- [ ] CI passes `translate.py` check with exit code `0`.
