SUMMARY:
Implemented a deterministic one-shot live micro-trade exception package assembler that evaluates sanitized governance inputs and emits a single review-readiness decision with required blockers, safety hardening, and deterministic follow-up actions.

FILES CHANGED:
- automation/forex_engine/one_shot_exception_assembler.py
- tests/forex_engine/test_one_shot_exception_assembler.py
- Reports/forex_delivery/AIOS_FOREX_ONE_SHOT_EXCEPTION_ASSEMBLER_V1_REPORT.md

WHY THIS REDUCES SESSION COUNT:
- Collapses one-shot exception readiness checks into a single reusable contract decision instead of checking proof domains in separate ad-hoc tests.
- Standardizes blocker names, status transitions, and next-action ordering for one-shot review assembly.

PACKAGE DOMAINS:
- demo_validation_contract
- live_readiness_candidate
- approval_trace
- risk_limits
- kill_switch_proof
- rollback_proof
- reconciliation_proof
- external_runtime_connector_proof
- credential_boundary_proof
- account_boundary_proof
- one_shot_controls
- evidence_freshness
- replayability_proof
- final_disarm_proof
- post_trade_journal_path

STATUSES:
- ONE_SHOT_EXCEPTION_BLOCKED
- ONE_SHOT_EXCEPTION_INCOMPLETE
- ONE_SHOT_EXCEPTION_REVIEW_READY
- ONE_SHOT_EXCEPTION_REJECTED

BLOCKERS ENFORCED:
- Missing/insufficient domain proofs and approvals
- Approval window required (active or status ACTIVE)
- Risk limits required (maximum_loss, daily_loss_cap, stop_loss, order_type, units_or_notional_limit)
- Evidence freshness required (fresh or age within limit)
- Retry/autonomous reentry controls required
- Unsafe flags block review-readiness
- Negative expectancy or contract-rejection returns rejected

RISK LIMITS ENFORCED:
- Maximum loss
- Daily loss cap
- Stop loss
- Order type
- Units or notional cap

ONE-SHOT CONTROLS ENFORCED:
- one_order_only
- no_retry_loop
- no_autonomous_reentry
- manual_arming_required
- timeout_required
- final_disarm_required
- operator_review_required

SAFETY CONFIRMATIONS:
- broker_connection_active exposed and defaults false unless unsafe input indicates true
- network_access exposed and defaults false unless unsafe input indicates true
- credentials_accessed exposed and defaults false unless unsafe input indicates true
- account_identifiers_accessed exposed and defaults false unless unsafe input indicates true
- order_execution_enabled returned as False
- live_trading_authorized returned as False
- capital_allocated returned as False
- one_shot_only returned as True
- no_retry_loop/no_autonomous_reentry flags returned explicitly
- operator_review_required set to True
- manual_arming_required and final_disarm_required preserved in safety output

VALIDATION COMMANDS:
- python -m pytest tests/forex_engine/test_one_shot_exception_assembler.py -q
- python -m py_compile automation/forex_engine/one_shot_exception_assembler.py tests/forex_engine/test_one_shot_exception_assembler.py

VALIDATION RESULTS:
- pytest: 38 passed
- py_compile: success

NEXT SAFE ACTION:
- Run the two required validator commands and then route remaining packets only if results pass.

REMAINING PACKETS ESTIMATE:
- One to three packets for governance hardening and bridge-to-live review integration.

NO-LIVE-EXECUTION CONFIRMATION:
- This packet enforces zero live broker connectivity, no credential/account access behavior, no order execution, and no live trading authorization.
