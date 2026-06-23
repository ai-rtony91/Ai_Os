# AIOS Forex OANDA Long-Only Broker Proof Intake V1

- packet_id: AIOS-FOREX-OANDA-LONG-ONLY-BROKER-PROOF-INTAKE-V1
- lane: OANDA_LONG_ONLY_BROKER_PROOF_INTAKE
- current_status_before_work: AUTONOMOUS_BLOCKED_BY_BROKER_GATE
- current_broker_proof_intake_status: OANDA_BROKER_PROOF_BLOCKED because no Anthony-supplied sanitized OANDA proof was provided in this packet
- valid_sanitized_proof_result: OANDA_LONG_ONLY_BROKER_PROOF_READY when a complete sanitized OANDA demo/practice proof dictionary is supplied
- autonomous_status_with_valid_sanitized_proof: AUTONOMOUS_BLOCKED_BY_POLICY
- execution_allowed: false
- ready_to_execute: false
- live_autonomy_allowed: false

## Long-Only Broker Proof Requirements

- broker_name must identify OANDA.
- broker_environment must be demo, sandbox, or practice.
- asset_class must be forex.
- long_permission must be true.
- short_permission may be false; short side remains disabled.
- instrument_tradable must be true.
- stop_loss_supported must be true.
- take_profit_supported must be true.
- one_order_only_supported must be true.
- demo_sandbox_order_preview_supported must be true.
- effective_leverage_limit must be positive and at or below 2.0.
- sanitized_evidence_only must be true.

## Short-Side Disabled Status

- short_side_enabled: false
- short_permission_false_blocks_long_only: false
- short_activation: not allowed by this intake

## Demo / Sandbox Only Status

- accepted_environments: demo, sandbox, practice
- live_environment: blocked
- demo_order_placement: blocked
- live_order_placement: blocked
- broker_mutation: blocked
- network_call: blocked

## Safety Guarantees

- accepts in-memory sanitized dictionaries only.
- no credential read or write.
- no .env read or write.
- no account ID read or write.
- no broker connection.
- no network call.
- no demo order.
- no live order.
- no scheduler, daemon, webhook, or background execution.
- no commit, push, or merge performed.

## Remaining Blockers

- current repo default still requires Anthony-supplied sanitized OANDA demo/practice proof evidence.
- after valid broker proof, policy/live exception remains blocked until owner request, approval, and arming contracts exist.
- live-for-keeps remains false.

## Next Exact Command

```powershell
python -c "from automation.forex_engine.oanda_long_only_broker_proof_intake_v1 import evaluate_oanda_long_only_broker_proof; import pprint; pprint.pp(evaluate_oanda_long_only_broker_proof({}))"
```

## Validators Run

- python -m compileall automation/forex_engine/oanda_long_only_broker_proof_intake_v1.py tests/forex_engine/test_oanda_long_only_broker_proof_intake_v1.py: passed
- python -m pytest tests/forex_engine/test_oanda_long_only_broker_proof_intake_v1.py -q: 17 passed
- python -m compileall automation/forex_engine tests/forex_engine scripts: passed
- python -m pytest tests/forex_engine -q: 2639 passed
- git diff --check: passed
- git diff --name-only: Reports/forex_delivery/readiness_state_recalculation_v1_report.json after validation-generated newline-only noise
- git status --short --branch: feature/forex-oanda-long-only-broker-proof-intake-v1 with expected new Forex files untracked, preserved unrelated dashboard/legal artifacts untracked, and validation-generated Forex report noise present

## Files Changed

- automation/forex_engine/oanda_long_only_broker_proof_intake_v1.py
- tests/forex_engine/test_oanda_long_only_broker_proof_intake_v1.py
- Reports/forex_delivery/AIOS_FOREX_OANDA_LONG_ONLY_BROKER_PROOF_INTAKE_V1.md
- validation-generated report noise observed and minimized:
  - Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md: status-dirty after pytest, no content diff after timestamp restoration
  - Reports/forex_delivery/readiness_state_recalculation_v1_report.json: newline-at-EOF diff after pytest

## Git Status

- branch: feature/forex-oanda-long-only-broker-proof-intake-v1
- expected new Forex files are untracked until Anthony approves staging.
- unrelated dashboard/legal artifacts remain untracked and preserved.
- no commit, push, merge, scheduler, daemon, webhook, broker call, credential read, account ID read, demo order, or live order was performed.
