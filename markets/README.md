# Market configuration

This directory centralises country-level market metadata that can be used to
power hreflang tags, alternate links, and per-market SEO settings.

Each market lives in its own folder named after the ISO 3166-1 alpha-2 country
code (for example `US/`, `NL/`). Inside that folder you will find:

- `hreflang.json` — locale and alternate URL configuration.
- `payments.json` — optional include/exclude lists for payment providers.

`hreflang.json` uses the following structure:

```json
{
  "country": "US",
  "defaultLocale": "en-US",
  "locales": [
    {
      "code": "en",
      "hreflang": "en-us",
      "path": "/en",
      "canonical": "https://lucy.world/en"
    }
  ],
  "alternate": [
    {
      "hreflang": "x-default",
      "href": "https://lucy.world/"
    }
  ]
}
```

- `country` — ISO country code.
- `defaultLocale` — locale code that should be the canonical representation for
  the market.
- `locales` — the list of locale variations that should be available for the
  market, including the relative path and absolute canonical URL. Paths use the
  language-only route (`/en`, `/nl`, etc.) that the frontend already serves.
- `alternate` — additional hreflang entries. Keep this to `x-default` when no
  cross-market links are required.

`payments.json` uses this structure:

```json
{
  "enabled": ["stripe"],
  "disabled": ["klarna"]
}
```

- `enabled` — providers available in the market.
- `disabled` — providers to explicitly disable for the market.

An index file (`index.json`) enumerates all available markets alongside their
canonical locale so that clients can pre-load configuration without scanning
the directory.
