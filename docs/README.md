# Lucy.world documentation index

Lucy.world is a multilingual, privacy-first keyword intelligence SaaS.

- 📐 **System design:** `ARCHITECTURE.md` — single source of truth for domains, locales, APIs, SEO, and Definition of Done checklists.
- 🚀 **Infrastructure & deployment:** `DEPLOYMENT-GUIDE.md` — droplet bootstrap, Gunicorn/Nginx layout, and automation flow.
- 💳 **Billing integrations:** Follow Stripe's official samples on [github.com/stripe-samples](https://github.com/stripe-samples) for reference implementations; our production flow lives in `backend/routes_billing.py`.
- 🔐 **Latest status (Oct 5 2025):** Entitlement-driven sidebar, plan card, and 20 s premium search timeout are documented in Section 5 of `ARCHITECTURE.md`; deployment considerations appear in `DEPLOYMENT-GUIDE.md`.

All other guidance should be consolidated into `ARCHITECTURE.md` to keep the blueprint authoritative.
