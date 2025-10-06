# Lucy.world documentation index

Lucy.world is a multilingual, privacy-first keyword intelligence SaaS.

- 📐 **System design:** `ARCHITECTURE.md` — single source of truth for domains, locales, APIs, SEO, and Definition of Done checklists.
- 🚀 **Infrastructure & deployment:** `DEPLOYMENT-GUIDE.md` — droplet bootstrap, Gunicorn/Nginx layout, and automation flow.
- 💳 **Billing integrations:** Follow Stripe's official samples on [github.com/stripe-samples](https://github.com/stripe-samples) for reference implementations; our production flow lives in `backend/routes_billing.py`.
- 🔐 **Latest status (Oct 6 2025):** Search results now emit `noindex, nofollow` meta tags and locale robots files include `Disallow: /*?q=`; see Section 11 of `ARCHITECTURE.md` for crawl discipline and `DEPLOYMENT-GUIDE.md` for regeneration + validation steps.

All other guidance should be consolidated into `ARCHITECTURE.md` to keep the blueprint authoritative.
