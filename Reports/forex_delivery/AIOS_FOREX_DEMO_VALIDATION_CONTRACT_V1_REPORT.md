SUMMARY:
Created a canonical Demo Validation Contract in `automation/forex_engine/demo_validation_contract.py` and a deterministic evaluator `evaluate_demo_validation_contract` that centralizes demo candidate readiness checks, threshold evaluation, blocker detection, deterministic status outputs, and safety assertions.

FILES CHANGED:
- automation/forex_engine/demo_validation_contract.py
- tests/forex_engine/test_demo_validation_contract.py
- Reports/forex_delivery/AIOS_FOREX_DEMO_VALIDATION_CONTRACT_V1_REPORT.md

WHY THIS REDUCES SESSION COUNT:
This packet replaces duplicated rule handling for demo validation by enforcing one alias-aware contract for all callers. It removes status/blocker drift between supervisors and reduces retries caused by inconsistent threshold or blocker interpretation. The ranked `required_next_packets` and deterministic output shape make downstream automation and manual review steps repeatable.

DOMAINS UNIFIED:
- Demo validation state/approval checks
- Validation metrics thresholds (sessions, trades, expectancy, profit factor, drawdown, evidence score)
- Candidate state/approval gating
- Safety/invariant enforcement

BLOCKERS ENFORCED:
- missing_candidate_record
- missing_validation_results
- minimum_validation_sessions_not_met
- minimum_validation_trades_not_met
- negative_expectancy
- expectancy_below_threshold
- profit_factor_below_threshold
- drawdown_above_threshold
- evidence_score_below_threshold
- candidate_not_approved_for_demo_validation
- candidate_state_blocked
- risk_failures_present
- unsafe_broker_connection_detected
- unsafe_credential_access_detected
- unsafe_account_identifier_detected
- unsafe_order_execution_detected
- unsafe_live_trading_detected

THRESHOLDS:
- minimum_validation_sessions: 3
- minimum_validation_trades: 20
- minimum_positive_expectancy: 0.01
- minimum_profit_factor: 1.10
- maximum_drawdown: 10.0
- minimum_evidence_score: 0.75

VALIDATION COMMANDS:
- python -m pytest tests/forex_engine/test_demo_validation_contract.py -q
- python -m py_compile automation/forex_engine/demo_validation_contract.py tests/forex_engine/test_demo_validation_contract.py

VALIDATION RESULTS:
- python -m pytest tests/forex_engine/test_demo_validation_contract.py -q -> PASS (25 passed)
- python -m py_compile automation/forex_engine/demo_validation_contract.py tests/forex_engine/test_demo_validation_contract.py -> PASS

CONTRACT STATUS:
- Canonical contract module and tests added, and validation passed.

REMAINING BLOCKERS:
- Not applicable to this packet; module now enforces the above blockers deterministically.

NEXT SAFE ACTION:
- Integrate `evaluate_demo_validation_contract` as the single validator input for demo-to-live review routing.

NO-LIVE-EXECUTION CONFIRMATION:
- This packet did not perform broker access, network calls, credential/account lookup, order execution, live trading, deployment, commit, push, PR creation, or merge.
- No scheduler, daemon, or external service execution was invoked.

STATUS: COMPLETE
