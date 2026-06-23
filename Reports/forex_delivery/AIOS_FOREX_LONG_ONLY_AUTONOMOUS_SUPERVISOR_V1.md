# AIOS Forex Long-Only Autonomous Supervisor V1

- packet_id: AIOS-FOREX-LONG-ONLY-AUTONOMOUS-SUPERVISOR-V1
- milestone: profitable live Forex bot
- current_status: AUTONOMOUS_BLOCKED_BY_BROKER_GATE
- live_for_keeps_ready: false
- execution_mode: DEMO_SANDBOX_ONLY
- order_execution: false

## Blockers

- broker_gate: blocked until sanitized demo/sandbox broker proof and explicit account-permission fields are provided.
- policy_gate: blocked until owner live-exception request, approval, arming, and evidence-bundle contracts are present.
- live_autonomy: blocked; this supervisor prepares a demo plan only and does not execute orders.

## Autonomy Doctrine

- trading_window_intent: 22 hours per day, 6 days per week.
- autonomy_scope: prepare-only contract for demo/sandbox supervision.
- live_execution: not enabled.
- scheduler: not enabled.
- daemon: not enabled.
- webhook: not enabled.
- background_execution: not enabled.
- operator_review_before_live: required.

## Long-Only Status

- current_candidate: c1-eur-buy
- activation_side: LONG
- long_only_activation: required
- short_side_enabled: false
- short_side_status: SHORT_SIDE_DISABLED

## Demo-Only Status

- demo_sandbox_only: true
- one_active_order_max: 1
- max_live_micro_units: inherited from final readiness threshold, default 1000
- effective_leverage_cap: inherited from final readiness threshold, default 2.0
- stop_loss_required: true
- take_profit_required: true
- max_loss_cap_required: true
- daily_stop_cap_required: true
- kill_switch_required: true
- audit_log_required: true

## Broker Gate Status

- broker_gate_required: true
- current_broker_gate: blocked
- broker_demo_sandbox_proof: missing in current default state
- account_permission_fields: unknown in current default state
- broker_mutation: false
- credential_read: false
- account_id_read: false
- network_call: false

## Policy Gate Status

- policy_live_exception_gate_required: true
- current_policy_gate: blocked after broker gate
- owner_live_exception_request: missing in current default state
- owner_approval: missing in current default state
- arming_contract: missing in current default state
- no_scheduler_daemon_webhook_background: true

## Safety Guarantees

- no live order placement.
- no broker mutation.
- no credential read or write.
- no .env read or write.
- no account ID read or write.
- no network trading automation.
- no scheduler, daemon, webhook, or background process creation.
- no commit, push, or merge performed.

## Exact Next Command

```powershell
python -c "from automation.forex_engine.long_only_autonomous_supervisor_v1 import build_long_only_autonomous_supervisor_contract; import pprint; pprint.pp(build_long_only_autonomous_supervisor_contract())"
```

## Validators Run

- python -m compileall automation/forex_engine/long_only_autonomous_supervisor_v1.py tests/forex_engine/test_long_only_autonomous_supervisor_v1.py: passed
- python -m pytest tests/forex_engine/test_long_only_autonomous_supervisor_v1.py -q: 12 passed
- python -m compileall automation/forex_engine tests/forex_engine scripts: passed
- python -m pytest tests/forex_engine -q: 2622 passed
- git diff --check: passed
- git diff --name-only: Reports/forex_delivery/readiness_state_recalculation_v1_report.json
- git status --short --branch: feature/forex-long-only-autonomous-supervisor-v1 with expected new Forex files untracked, preserved unrelated dashboard/legal artifacts untracked, and validation-generated Forex report noise present

## Files Changed

- automation/forex_engine/long_only_autonomous_supervisor_v1.py
- tests/forex_engine/test_long_only_autonomous_supervisor_v1.py
- Reports/forex_delivery/AIOS_FOREX_LONG_ONLY_AUTONOMOUS_SUPERVISOR_V1.md
- validation-generated report noise observed and minimized:
  - Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md: status-dirty after pytest, no content diff after timestamp restoration
  - Reports/forex_delivery/readiness_state_recalculation_v1_report.json: newline-at-EOF diff after pytest

## Git Status

- branch: feature/forex-long-only-autonomous-supervisor-v1
- expected new Forex files are untracked until Anthony approves staging.
- unrelated dashboard/legal artifacts remain untracked and preserved.
- no commit, push, merge, scheduler, daemon, webhook, broker call, credential read, account ID read, or live order was performed.
