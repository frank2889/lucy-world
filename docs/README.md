# Lucy.world Documentation Index

Multilingual, privacy-first keyword intelligence SaaS.

## Current Status (Oct 8, 2025)

### Completed
- Language equality system: All languages self-contained, no fallbacks
- Billing UI integration: Plan cards, upgrade/credits buttons, sticky CTA
- SMTP email: Gmail configured for magic link authentication
- Design philosophy: Professional, daily-use tool aesthetic
- Frontend bundle: All 18 platform tools updated

### In Progress
- Translation completion: Fill missing Dutch locale keys
- Email testing: SMTP deployment verification

### Planned
- Fix "Zoeken mislukt" error state bug
- Make search results interactive/clickable
- Add search metrics
- Skeleton loaders
- Top navigation
- Pricing page
- Enterprise trust signals

## Documentation Files

- `design/design.md` — Canonical design specification and automation
  rules
- `ARCHITECTURE.md` — System design, APIs, SEO, Definition of Done
- `DEPLOYMENT-GUIDE.md` — Infrastructure, Gunicorn/Nginx, automation
- `BILLING-INTEGRATION.md` — Stripe integration, entitlements, checkout
- `CHANGELOG.md` — Release notes, updates, dates
- `SMTP_SETUP.md` — Email configuration

## Development Rules

### Translation
- Every user-facing string must be in `languages/{lang}/locale.json`
- No hardcoded text in frontend components
- No fallbacks between languages
- Each language complete or shows `[MISSING: key]`

### Design
- No gradients
- No animations except loading states
- No shadows except minimal elevation
- WCAG AA minimum contrast
- 8px spacing grid
- Professional appearance

### Code
- TypeScript strict mode
- No console.error in production
- Mobile-first responsive
- Performance < 2s initial load

## Release Checklist

1. CRO worksheet documented
2. Journey verification in staging
3. Language sweep, no `[MISSING: *]` in production
4. Accessibility check: WCAG AA, keyboard, screen reader
5. Analytics verification

## References

- Latest status: CHANGELOG.md
- Billing reference: github.com/stripe-samples
- Design rules: design/design.md (canonical spec)
- Translations: `languages/{lang}/locale.json`
