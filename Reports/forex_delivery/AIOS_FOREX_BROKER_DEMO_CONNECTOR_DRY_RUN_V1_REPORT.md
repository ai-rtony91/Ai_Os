SUMMARY:
Created a deterministic broker-demo dry-run connector evaluator with a strict, simulation-only request/response contract, required-state guardrails, alias-aware input parsing, and deterministic blocker/error reporting.

FILES CHANGED:
automation/forex_engine/broker_demo_connector_dry_run.py
tests/forex_engine/test_broker_demo_connector_dry_run.py
Reports/forex_delivery/AIOS_FOREX_BROKER_DEMO_CONNECTOR_DRY_RUN_V1_REPORT.md

BROKER DEMO CONNECTOR DRY-RUN PURPOSE:
Provide a bounded dry-run decision surface that validates upstream review readiness, required proofs, and control evidence before marking a broker-demo dry-run evaluation as ready.

DOMAINS CONSUMED:
runtime plan domain
approval workflow domain
connector gate domain
runtime review domain
runtime connector domain
connector contract domain
review chain domain
certificate domain
one-shot exception domain
proof/control domain

DRY-RUN ENVELOPES:
Request envelope:
- envelope_version: BROKER_DEMO_CONNECTOR_DRY_RUN_REQUEST_V1
- request_type: BROKER_DEMO_DRY_RUN
- dry_run_only: True
- sanitized_payload_only: True
- all privileged requests set to False

Response envelope:
- envelope_version: BROKER_DEMO_CONNECTOR_DRY_RUN_RESPONSE_V1
- response_type: BROKER_DEMO_DRY_RUN_RESULT
- dry_run_only: True
- sanitized_payload_only: True
- all privileged performed flags set to False

RUNTIME CONTROLS:
- Hard requirements for all upstream readiness statuses.
- Hard requirements for mandatory dry-run request inputs.
- Hard requirements for mandatory proofs/controls.
- Alias-aware mapping for 25+ known field aliases.
- Deterministic required next action and required next packets.

PROOFS ENFORCED:
approval_trace
approval_evidence_bundle
runtime_plan_trace
runtime_plan_evidence_bundle
replay_prevention
replay_proof
reconciliation_proof
kill_switch_proof
rollback_proof
freshness_proof
final_disarm_proof
one_shot_controls
post_trade_journal_path
operator_review_required
manual_arming_required
timeout_required
no_retry_loop
no_autonomous_reentry

STATUSES:
BROKER_DEMO_DRY_RUN_READY
BROKER_DEMO_DRY_RUN_INCOMPLETE
BROKER_DEMO_DRY_RUN_BLOCKED
BROKER_DEMO_DRY_RUN_REJECTED
BROKER_DEMO_DRY_RUN_REVOKED
BROKER_DEMO_DRY_RUN_EXPIRED

BLOCKERS:
Missing fields and readiness misses from upstream domains
Upstream explicit rejections
Mandatory proof/control gaps
Unsafe runtime flags including broker/network/credential/account/order/live/execution/capital events

SAFETY INVARIANTS:
broker_connection_active: False
network_access: False
credentials_accessed: False
account_identifiers_accessed: False
order_execution_enabled: False
live_trading_authorized: False
execution_authority_granted: False
capital_allocated: False
broker_demo_dry_run_only: True
sanitized_payload_only: True
broker_demo_connector_not_active: True
operator_review_required: True
manual_arming_required: True
timeout_required: True
no_retry_loop: True
no_autonomous_reentry: True
final_disarm_required: True
revocation_path_required: True
replay_prevention_required: True

VALIDATION COMMANDS:
python -m pytest tests/forex_engine/test_broker_demo_connector_dry_run.py -q
python -m py_compile automation/forex_engine/broker_demo_connector_dry_run.py tests/forex_engine/test_broker_demo_connector_dry_run.py

VALIDATION RESULTS:
PASS: python -m pytest tests/forex_engine/test_broker_demo_connector_dry_run.py -q
PASS: python -m pytest tests/forex_engine/test_broker_demo_connector_dry_run.py -q -> 112 passed
PASS: python -m py_compile automation/forex_engine/broker_demo_connector_dry_run.py tests/forex_engine/test_broker_demo_connector_dry_run.py

NEXT SAFE ACTION:
Wire the dry-run evaluator result into the downstream Forex dry-run orchestration path using deterministic next action packets only.

REMAINING ESTIMATE:
No remaining implementation required for this packet scope.

NO-BROKER-NO-LIVE CONFIRMATION:
Connector enforces broker/network/credential/account/exec/live-trading false in envelopes, contract, and safety output and contains no network/broker SDK/runtime calls.
