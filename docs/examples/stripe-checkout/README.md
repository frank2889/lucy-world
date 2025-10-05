# Stripe Checkout reference sample

This directory mirrors Stripe's official "Prebuilt payment page with subscriptions" sample. We keep it vendor-authored so engineers can spin up the reference implementation while validating API keys, webhook configuration, or new billing flows before wiring changes into the Flask backend.

> The production billing surface lives in `backend/routes_billing.py`. Use this sample strictly for local experiments—never deploy it alongside the main app.

## Quick start

1. Install the Ruby dependencies:

	```bash
	bundle install
	```

2. Start the sample server:

	```bash
	ruby server.rb -o 0.0.0.0
	```

3. Visit [http://localhost:4242/checkout.html](http://localhost:4242/checkout.html) and test with Stripe's provided card numbers.

Refer to the upstream README at [stripe-samples](https://github.com/stripe-samples) for deeper configuration and feature toggles.
