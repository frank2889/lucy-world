# Support Runbook — Entitlements & Credits

This runbook guides support engineers through diagnosing and resolving issues with customer plans, AI credit balances, and Stripe billing state.

## Quick reference

| Scenario | Primary Tooling | Escalation Path |
| --- | --- | --- |
| Missing upgrade / wrong tier | Stripe Dashboard → Customer → Subscriptions | Billing engineering after 2 failed retries |
| AI credits not granted | `payments` table, credit event log, Stripe invoice | Backend engineering if grant event is absent |
| AI credits not decrementing | Audit credit events, `ai_usage` ledger | Data platform team |
| Billing portal error | Stripe Billing Portal logs | Stripe support |

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

## 4. Stripe reconciliation

1. Locate the customer in Stripe via email.
2. Re-run the most recent webhook events with Stripe CLI:

```bash
stripe events resend EVENT_ID --forward-to https://staging.lucy.world/api/billing/webhook
```

3. Check application logs for successful handling (`"action":"subscription_updated"`).
4. If the event fails twice, escalate to the billing engineering rotation.

## 5. Escalation criteria

- Correlation ID missing or logs unavailable → notify DevOps.
- Stripe reports successful payment but no `entitlement_change` log → billing engineering.
- Credit balance negative or stuck → data platform.
- Repeated webhook signature failures → open Stripe support ticket.

## 6. Post-resolution checklist

- Confirm the customer sees the correct tier/credits in the UI.
- Add a summary of actions (including CLI commands) to the support ticket.
- Update this runbook if new remediation steps were required.
