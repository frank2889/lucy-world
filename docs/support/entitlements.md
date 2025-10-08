# Support Runbook — Entitlements & Credits

This runbook guides support engineers through diagnosing and resolving issues with customer plans, AI credit balances, and Stripe billing state.

## Quick reference

| Scenario | Primary Tooling | Escalation Path |
| --- | --- | --- |
| Missing upgrade / wrong tier | Stripe Dashboard → Customer → Subscriptions | Billing engineering after 2 failed retries |
| AI credits not granted | `payments` table, credit event log, Stripe invoice | Backend engineering if grant event is absent |
| AI credits not decrementing | Audit credit events, `ai_usage` ledger | Data platform team |
| Billing portal error | Stripe Billing Portal logs | Stripe support |
| `/pricing` won’t load | CDN logs, Flask access logs, Vite build hash | Frontend on-call |
| `/billing/credits` blank page | Stripe session logs, entitlements payload | Billing engineering |

## 1. Collect essentials

1. Ask the customer for their login email and the approximate time of the issue.
2. Grab the `X-Request-ID` header from the support ticket or logs to correlate backend requests.
3. Search in the centralized log index for `event:"entitlement_change"` with the correlation ID to locate mutation history.

## 2. Verify account state

Run the following within a Flask shell (`flask shell`):

```python
from backend.models import User
from backend.services.credits import ensure_plan_metadata

user = User.query.filter_by(email="customer@example.com").one()
meta = ensure_plan_metadata(user)
print({
    "tier": user.plan,
    "stripe_customer": user.stripe_customer_id,
    "ai_credits": meta.get("ai_credits"),
    "credit_events": meta.get("credit_events", [])[-5:],
})
```

Ensure the `tier` matches the expected subscription. If not, replay the relevant Stripe webhook (see Section 4).

## 3. Adjustments & remediation

### Grant or revoke credits manually

```bash
flask entitlements adjust --user EMAIL --grant-credits 100
flask entitlements adjust --user EMAIL --consume-credits 50 --reason "support-adjustment"
```

Log the adjustment in the ticket and include the correlation ID from the CLI output.

### Reset plan tier

```bash
flask entitlements adjust --user EMAIL --set-tier pro
```

Confirm the change by querying the user again and watching for the `entitlement_change` log entry.

### Validate pricing + credit surfaces

- **Pricing page** (`/pricing`): ensure localized tier cards load, CTA URLs align with the customer’s entitlements (`upgrade_url`, `buy_credits_url`), and sticky sidebar CTA remains visible.
- **Credit packs** (`/billing/credits`): confirm the template renders localized copy (`Koop AI-credits` for Dutch) and that Stripe Checkout buttons resolve; if the page shows JSON or 404, escalate to backend immediately.
- **Premium overlay**: after the first search, the overlay should appear once per session and log `premium_overlay_impression`; verify the customer sees it if they are eligible for upgrade prompts.

## 4. Stripe reconciliation

1. Locate the customer in Stripe via email.
2. Re-run the most recent webhook events with Stripe CLI:

```bash
stripe events resend EVENT_ID --forward-to https://staging.lucy.world/api/billing/webhook
```

- Check application logs for successful handling (`"action":"subscription_updated"`).
- If the event fails twice, escalate to the billing engineering rotation.

### Linking payments to credit balance

When investigating credit discrepancies:

- Locate the payment intent or invoice in Stripe.
- Verify the webhook replay shows the `grant_ai_credits` helper executing with the correct quantity.
- In the Flask shell, call `ensure_plan_metadata(user)` and confirm the `ai_credits` total reflects the purchase; if not, re-run the webhook and attach logs to the ticket.
- Update the analytics event (`credit_purchase_completed`) manually if the automated emitter missed it; attach evidence to the runbook for future triage.

## 5. Escalation criteria

- Correlation ID missing or logs unavailable → notify DevOps.
- Stripe reports successful payment but no `entitlement_change` log → billing engineering.
- Credit balance negative or stuck → data platform.
- Repeated webhook signature failures → open Stripe support ticket.

## 6. Observability quick check

Run the metrics service from a Flask shell when you need a snapshot of plan upgrade velocity or payment volume:

```python
from backend.services.metrics import collect_entitlement_metrics

metrics = collect_entitlement_metrics()
print({
    "plan_breakdown": metrics["users"]["plans"],
    "recent_payments": metrics["payments"],
})
```

The call executes a single aggregation query set (covers plan counts, expiring trials, and payment rollups over the default seven-day window). Share notable anomalies in the #billing-support channel and attach the JSON snippet to the ticket.

### CRO instrumentation quick check

Use the analytics backend (`SELECT * FROM analytics_events WHERE name IN ('cta_upgrade_click','premium_overlay_impression') ORDER BY occurred_at DESC LIMIT 20;`) to confirm CRO events fired after a deploy. If counts drop to zero, alert the growth engineering channel and re-run the frontend smoke suite.

## 7. Post-resolution checklist

- Confirm the customer sees the correct tier/credits in the UI.
- Add a summary of actions (including CLI commands) to the support ticket.
- Update this runbook if new remediation steps were required.
