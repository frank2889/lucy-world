# Per-language language registry

Per-language registry files for Lucy World.

One file per ISO 639-1 language code, e.g. `en.json`, `nl.json`, `de.json`.

Schema:
{
  "code": "en",
  "name": "English",
  "rtl": false,
  "aliases": [],
  "hreflang": "en"
}

- code: ISO 639-1 primary language code
- name: Native/English display name
- rtl: whether UI direction should be RTL for this language
- aliases: optional alias codes we accept as input (e.g., ["iw" -> "he"]). Keep ISO639-1 preferred.
- hreflang: what to emit in `link rel="alternate" hreflang="…"` (usually same as code)
