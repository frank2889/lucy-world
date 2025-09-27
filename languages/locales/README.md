# Locales (App UI)

Editable per-language UI files live here. English is the source of truth.

- en.json: English base (source)
- `<lang>.json`: Only add when you translate a language; otherwise the app falls back to English.

Schema:

```json
{
  "lang": "en",
  "dir": "ltr",
  "strings": { "nav.search": "Search" }
}
```
