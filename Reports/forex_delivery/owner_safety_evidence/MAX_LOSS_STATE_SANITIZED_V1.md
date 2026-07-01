# MAX LOSS STATE SANITIZED V1

Control: max_loss_state

Attested state: ENABLED

Evidence type: owner attestation tied to a committed configuration artifact

Sanitized: yes

Contains secrets: no

Contains broker account identifiers: no

Broker API used: no

Credentials used: no

Order execution: no

Live trading authorized: no

Owner statement:

I reviewed and attested the demo-scope max loss configuration on 2026-07-01: cumulative max total loss cap of 150 USD (15% of the 1000 USD baseline, matching the governor max_drawdown threshold 0.15), recorded in control/forex/forex_safety_controls_config.json. This artifact is sanitized and contains no credentials, account identifiers, broker tokens, or live-order data.

Evidence:

Max loss state is ENABLED for demo-scope operation per control/forex/forex_safety_controls_config.json (max_total_loss_usd=150). Reaching the cap halts all operation and requires owner reset. A brake trip-proof test remains REQUIRED before any live arming. This attestation covers demo scope only.

Owner attestation:

Owner (Anthony) explicitly attested this configuration and this value on 2026-07-01.
