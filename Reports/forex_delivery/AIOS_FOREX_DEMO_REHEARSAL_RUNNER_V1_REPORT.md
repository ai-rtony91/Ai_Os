# AIOS_FOREX_DEMO_REHEARSAL_RUNNER_V1

## Summary

Implemented the first paper/demo-review rehearsal runner after `AIOS_FOREX_DEMO_REHEARSAL_EVIDENCE_BUNDLE_V1`.

The runner creates an in-memory evidence bundle from fixture or supplied sample inputs. It produces evidence, not trades. It does not call a broker, read credentials, submit orders, authorize live trading, or write runtime files.

## Implemented Artifact

```text
automation/forex_engine/demo_rehearsal_evidence_bundle.py
```

Primary function:

```text
run_demo_rehearsal_evidence_bundle(...)
```

The function returns a deterministic structured evidence bundle with:

- bundle identity
- input summary
- normalized market state
- strategy candidates
- rejected candidates
- selected candidate IDs
- risk sizing evidence
- order preview evidence
- paper fill evidence
- lifecycle summary
- balance summary
- evidence ledger summary
- session replay summary
- safety boundary
- approval gates
- pass/fail criteria
- blockers
- next action

## Safety Boundary

This runner is paper/demo-review only.

It explicitly reports:

```text
live_trading_allowed = false
broker_submit_allowed = false
credentials_used = false
account_id_used = false
network_calls = false
live_order_submitted = false
runtime_file_written = false
```

## Tests Added

```text
tests/forex_engine/test_demo_rehearsal_evidence_bundle.py
```

Coverage includes default bundle creation, required output sections, safety boundary flags, deterministic IDs, bad-market blocker behavior, and source scanning for dangerous runtime behavior.

## Next Safe Objective

Review a generated rehearsal bundle.

The next safe objective is not live trading. Any future live micro-trade consideration remains behind evidence review, risk limits, kill switch proof, rollback plan, broker boundary review, credential isolation review, human approval, and the single-live-micro-trade exception checklist.

