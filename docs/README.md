# Lucy.world documentation index

 Lucy.world is a multilingual, privacy-first keyword intelligence SaaS.

## UX & CRO release ritual (Oct 2025)

Every deployment now includes a structured UX & CRO pass based on the Lucy.World expert review:

- **Run the CRO worksheet** – capture findings in this docs folder before merging (`ARCHITECTURE.md` for system impact, `CHANGELOG.md` for timeline, `DEPLOYMENT-GUIDE.md` for release steps).
- **Verify customer journeys** – `/billing/credits`, `/billing/upgrade` → `/pricing`, login magic-links, and the first-search premium overlay must all work in staging *before* production.
- **Language sweep** – confirm Dutch defaults (language `nl`, market `NL`) render while preserving translations for all other locales.
- **Accessibility + analytics** – contrast ratios meet WCAG 2.1 AA, loader + feedback strings exist in every locale, and CTA clicks emit the new analytics events.

Document anything learned from the UX/CRO session in the Markdown files referenced above so the next release inherits the improvements automatically.

- 📐 **System design:** `ARCHITECTURE.md` — single source of truth for domains, locales, APIs, SEO, and Definition of Done checklists.
- 🚀 **Infrastructure & deployment:** `DEPLOYMENT-GUIDE.md` — droplet bootstrap, Gunicorn/Nginx layout, and automation flow.
- 💳 **Billing integrations:** Follow Stripe's official samples on [github.com/stripe-samples](https://github.com/stripe-samples) for reference implementations; our production flow lives in `backend/routes_billing.py`.
- �️ **Release notes:** `CHANGELOG.md` — latest engineering, observability, and automation updates with test evidence.
- �🔐 **Latest status (Oct 6 2025):** Search results now emit `noindex, nofollow` meta tags, locale robots files include `Disallow: /*?q=`, Stripe webhook replays are covered by automated tests, and entitlement changes log structured events with correlation IDs. See Section 11 of `ARCHITECTURE.md` for crawl discipline, Section 8 for lifecycle observability, and `DEPLOYMENT-GUIDE.md` for regeneration + validation steps.

All other guidance should be consolidated into `ARCHITECTURE.md` to keep the blueprint authoritative.
