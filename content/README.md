# Content architecture

This folder stores all user-facing content by language to build the site internationally from the ground up.

Structure:
- `content/i18n/<lang>.json` – UI strings per language (authoritative source)
- `languages/` – global language list and per-language dictionaries for analysis features

Why:
- Single source of truth for UI copy, easy to localize and edit without touching code
- Backend can serve the right content to the frontend and expose it to external clients if needed

Conventions:
- Use ISO 639-1 codes for <lang>
- Keep placeholders intact (e.g., {name}, {0})
- Don’t include markup in strings unless necessary; if included, keep tags simple and consistent
