# Billing Integration Guide

**Last Updated**: October 8, 2025

## Overview

Lucy World implements a hybrid billing system using Stripe Checkout for both subscription plans and one-time credit purchases. The frontend displays real-time plan information, AI credits, and contextual upgrade prompts.

## Architecture

### Backend APIs

#### `/api/entitlements` (GET)
Returns user's current plan state and billing URLs.

**Request**:
```http
GET /api/entitlements
Authorization: Bearer <token>
```

**Response**:
```json
{
  "tier": "free|pro|enterprise",
  "ai_credits": 0,
  "expires_at": "2025-12-31T23:59:59Z",
  "sidebar_groups": ["google", "social", "ecommerce", "ai"],
  "upgrade_url": "https://billing.stripe.com/...",
  "buy_credits_url": "https://billing.stripe.com/..."
}
```

#### `/api/billing/credit-packs` (GET)
Fetches available credit pack offerings from Stripe.

**Request**:
```http
GET /api/billing/credit-packs
Authorization: Bearer <token>
```

**Response**:
```json
{
  "packs": [
    {
      "price_id": "price_1234567890",
      "credits": 100,
      "currency": "eur",
      "unit_amount": 990,
      "nickname": "100 AI Credits",
      "description": "One-time purchase of 100 AI credits"
    }
  ]
}
```

#### `/api/billing/upgrade-checkout` (POST)
Creates Stripe Checkout session for plan upgrade.

**Request**:
```http
POST /api/billing/upgrade-checkout
Authorization: Bearer <token>
Content-Type: application/json

{}
```

**Response**:
```json
{
  "url": "https://checkout.stripe.com/c/pay/cs_..."
}
```

#### `/api/billing/credit-checkout` (POST)
Creates Stripe Checkout session for credit purchase.

**Request**:
```http
POST /api/billing/credit-checkout
Authorization: Bearer <token>
Content-Type: application/json

{
  "price_id": "price_1234567890",
  "quantity": 1
}
```

**Response**:
```json
{
  "url": "https://checkout.stripe.com/c/pay/cs_..."
}
```

## Frontend Integration

### Plan Summary Component

Displays user's current plan tier, AI credits, and expiry date in both desktop header and mobile topbar.

**Location**: `App.tsx` → `renderPlanSummary(variant: 'desktop' | 'mobile')`

**Features**:
- Shows tier label (Free, Pro, Enterprise) translated per user's locale
- Displays AI credits count with real-time updates
- Shows renewal/expiry date if available
- Indicates AI workspace unlock status (✨ unlocked / ⚡ locked)
- Responsive sizing for mobile and desktop contexts

**States**:
- `loading`: Shows skeleton with "Loading plan…" message
- `error`: Displays error message in red
- `success`: Shows full plan details

### Billing Actions Component

Renders upgrade and credit purchase buttons with proper loading states.

**Location**: `App.tsx` → `renderBillingActions(variant: 'desktop' | 'mobile')`

**Features**:
- "Upgrade plan" button with ⬆️ emoji
- "Get AI credits" button with 💡 emoji and formatted price
- Loading state shows "Opening checkout…" during Stripe redirect
- Disabled state during active checkout flows
- Falls back to legacy `buy_credits_url` if credit packs unavailable

### Sticky CTA Banner

Contextual call-to-action that appears for anonymous users and users with low AI credits.

**Location**: `App.tsx` → `showStickyCta` condition

**Display Logic**:
```typescript
const LOW_CREDITS_THRESHOLD = 25
const isLowCredits = isSignedIn && ai_credits >= 0 && ai_credits < LOW_CREDITS_THRESHOLD
const showStickyCta = (!isSignedIn || isLowCredits) && !stickyCtaDismissed
```

**Features**:
- **Anonymous users**: Shows sign-in prompt with "Unlock full keyword intelligence" message
- **Low credit users**: Shows credit warning with "Almost out of AI credits?" message
- Session-based dismissal via `sessionStorage` (resets on browser close)
- Auto-reappears when credits drop below threshold
- Translatable content via locale strings

**Dismissal Behavior**:
- User can click ✕ to dismiss
- Dismissal persists in `sessionStorage` as `lw_sticky_cta_dismissed = '1'`
- For low-credit users, dismissal is cleared when condition resolves
- Separate dismiss states for sign-in vs. low-credit variants

### Credit Pack Pricing

Formats credit pack prices according to user's UI language preference.

**Implementation**:
```typescript
const formatCreditPackPrice = (pack: CreditPack | null) => {
  // ... amount calculation from unit_amount (Stripe cents)
  const currency = (pack.currency || 'EUR').toUpperCase()
  const localeCandidates = [
    language === 'nl' ? 'nl-NL' : null,
    language === 'en' ? 'en-US' : null,
    `${DEFAULT_LANGUAGE}-${DEFAULT_LANGUAGE.toUpperCase()}`,
    // ... fallbacks
  ]
  
  for (const locale of localeCandidates) {
    try {
      return new Intl.NumberFormat(locale, { style: 'currency', currency }).format(amount)
    } catch {
      continue
    }
  }
  
  return `${amount.toFixed(2)} ${currency}` // ultimate fallback
}
```

**Supported Formats**:
- Dutch (nl-NL): `€ 9,90`
- English (en-US): `$9.90`
- Other locales: Intl.NumberFormat with appropriate fallbacks

### Checkout Flow

**Plan Upgrade Flow**:
1. User clicks "Upgrade plan" button
2. `handleUpgradeClick()` called
3. Validates `upgrade_url` exists
4. POSTs to `/api/billing/upgrade-checkout`
5. Redirects to Stripe Checkout URL
6. User completes payment
7. Stripe webhook updates user's plan
8. User redirected back to site with updated entitlements

**Credit Purchase Flow**:
1. User clicks "Get AI credits · €9,90" button
2. `handleBuyCreditsClick()` called
3. Validates user is signed in
4. Validates `price_id` exists from credit packs
5. POSTs to `/api/billing/credit-checkout` with price_id
6. Redirects to Stripe Checkout URL
7. User completes payment
8. Stripe webhook adds credits to user account
9. User redirected back to site with updated credits

**Error Handling**:
- 401 responses trigger sign-in modal
- Missing upgrade_url shows localized error message
- Missing credit packs fall back to legacy buy_credits_url
- Network failures display user-friendly error messages
- All errors respect user's locale for translations

## Localization

All billing-related UI strings are translatable via `languages/{lang}/locale.json`:

**Required Keys**:
```json
{
  "entitlements.sidebar.plan_label": "Your plan",
  "entitlements.tier.free": "Free",
  "entitlements.tier.pro": "Pro",
  "entitlements.tier.enterprise": "Enterprise",
  "entitlements.sidebar.ai_credits": "AI credits",
  "entitlements.actions.upgrade": "Upgrade plan",
  "entitlements.actions.buy_credits": "Get AI credits",
  "entitlements.sidebar.ai_unlocked": "AI workspace unlocked",
  "entitlements.sidebar.ai_locked": "Unlock AI workspace with credits",
  "entitlements.sidebar.expires": "Renews on {date}",
  "entitlements.status.loading": "Loading plan…",
  "entitlements.status.error": "Unable to load plan",
  "billing.error.buy_credits_signin": "Sign in to buy AI credits.",
  "billing.error.buy_credits_unavailable": "AI credit purchase is unavailable right now. Please contact support.",
  "billing.error.upgrade_unavailable": "Upgrade is currently unavailable. Please contact support.",
  "billing.error.signin_required": "Please sign in to upgrade.",
  "billing.status.launching_checkout": "Opening checkout…",
  "billing.status.loading_credit_packs": "Loading credit packs…",
  "billing.error.checkout_failed": "Unable to open checkout. Please try again.",
  "billing.cta.low_credits.title": "Almost out of AI credits?",
  "billing.cta.low_credits.subtitle": "Top up to keep premium keyword data flowing.",
  "billing.cta.low_credits.counter": "Remaining credits: {amount}",
  "billing.cta.signin.title": "Unlock full keyword intelligence",
  "billing.cta.signin.subtitle": "Sign in to access premium searches, saved projects, and AI credits.",
  "billing.cta.signin.eyebrow": "Lucy World account",
  "billing.cta.dismiss": "Hide this message"
}
```

## Testing

### Manual Testing Checklist

**Plan Summary**:
- [ ] Desktop header shows plan card with tier, credits, expiry
- [ ] Mobile topbar shows compact plan card
- [ ] Loading state displays while entitlements fetch
- [ ] Error state shows when API fails
- [ ] Credits update in real-time after purchase

**Billing Actions**:
- [ ] Upgrade button launches Stripe checkout
- [ ] Credits button shows formatted price
- [ ] Loading states prevent double-clicks
- [ ] Fallback to legacy URLs when credit packs unavailable
- [ ] 401 responses trigger sign-in modal

**Sticky CTA**:
- [ ] Appears for anonymous users
- [ ] Appears when credits < 25
- [ ] Dismisses and persists to sessionStorage
- [ ] Reappears when credits drop below threshold
- [ ] Different messaging for sign-in vs. low-credit states

**Localization**:
- [ ] All billing strings translate correctly
- [ ] Credit pack prices format per locale (€9,90 vs $9.90)
- [ ] Date formatting respects locale
- [ ] RTL languages display correctly

### Integration Testing

```bash
# Run frontend unit tests
cd frontend
npm test

# Test entitlements API
curl -H "Authorization: Bearer <token>" \
  https://lucy.world/api/entitlements

# Test credit packs API
curl -H "Authorization: Bearer <token>" \
  https://lucy.world/api/billing/credit-packs

# Test upgrade checkout (returns redirect URL)
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  https://lucy.world/api/billing/upgrade-checkout

# Test credit checkout
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"price_id":"price_1234567890","quantity":1}' \
  https://lucy.world/api/billing/credit-checkout
```

## Deployment Notes

After updating billing-related frontend code:

1. **Rebuild frontend**:

  ```bash
  cd frontend
  npm run build
  cd ..
  ```

1. **Commit static assets**:

  ```bash
  git add app
  git commit -m "chore: rebuild frontend with billing UI updates"
  ```

1. **Deploy to server**:

  ```bash
  git push origin main
  ```

1. **Restart backend** (if needed):

  ```bash
  ssh user@server
  sudo systemctl restart lucy-world-search
  ```

1. **Verify deployment**:

  - Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
  - Check Network tab for latest `app-*.js` bundle
  - Verify plan summary and billing buttons appear
  - Test checkout flows end-to-end

## Troubleshooting

### Plan Summary Not Appearing

**Symptoms**: Plan cards missing from header/topbar

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify `useEntitlements` hook returning data
3. Check `/api/entitlements` response in Network tab
4. Ensure Bearer token valid (not expired)
5. Hard refresh to clear bundle cache

### Billing Buttons Not Working

**Symptoms**: Clicking upgrade/credits does nothing

**Solutions**:
1. Check `billingLoading` state not stuck
2. Verify checkout APIs returning valid URLs
3. Check browser popup blocker settings
4. Review console for CORS or network errors
5. Confirm Stripe keys configured in backend `.env`

### Credit Pack Pricing Wrong

**Symptoms**: Prices display incorrectly or in wrong currency

**Solutions**:
1. Verify Stripe price objects have `unit_amount` and `currency`
2. Check user's UI language setting
3. Review `formatCreditPackPrice` locale fallback logic
4. Ensure `Intl.NumberFormat` supported in browser
5. Check for TypeScript type mismatches in price data

### Sticky CTA Won't Dismiss

**Symptoms**: CTA reappears immediately after dismiss

**Solutions**:
1. Check sessionStorage for `lw_sticky_cta_dismissed` key
2. Verify `setStickyCtaDismissed(true)` callback firing
3. Check for conflicting `useEffect` resetting state
4. Review low-credit threshold logic (credits < 25)
5. Test with browser DevTools sessionStorage inspector

## Future Enhancements

- [ ] Usage-based billing for premium API calls
- [ ] Team/workspace billing with seat management
- [ ] Invoice generation and download
- [ ] Billing history and receipt archive
- [ ] Annual billing with discount incentives
- [ ] Regional pricing based on user's country
- [ ] Apple Pay / Google Pay integration
- [ ] Cryptocurrency payment options
- [ ] Gift credit packs for referrals
- [ ] Enterprise custom pricing and MSAs
