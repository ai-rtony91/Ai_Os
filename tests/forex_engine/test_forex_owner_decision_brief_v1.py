from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from automation.forex_engine.broker_health_readonly_v1 import (  # noqa: E402
    BROKER_HEALTH_REVIEW_READY,
    build_sample_snapshot,
    evaluate_broker_health_readonly,
)
from automation.forex_engine.demo_owner_approval_phrase_gate_v1 import (  # noqa: E402
    DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_MISSING,
    DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW,
    build_sample_missing_owner_approval_phrase_input,
    build_sample_valid_owner_approval_phrase_input,
    evaluate_demo_owner_approval_phrase_gate,
)
from automation.forex_engine.demo_trade_readiness_bridge_v1 import (  # noqa: E402
    DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW,
    run_demo_trade_readiness_bridge,
)
from automation.forex_engine.final_closure_evidence_v1 import FINAL_CLOSURE_REVIEW_READY  # noqa: E402
from automation.forex_engine.final_evidence_bundle_v1 import (  # noqa: E402
    FINAL_EVIDENCE_CHAIN_REVIEW_READY,
    build_replay_walkforward_profitability_evidence_chain,
)
from automation.forex_engine.forex_closure_integration_bridge_v1 import (  # noqa: E402
    FOREX_CLOSURE_CHAIN_BLOCKED,
    FOREX_CLOSURE_CHAIN_REVIEW_READY,
    build_sample_integration_input,
    run_forex_closure_integration_bridge,
)
from automation.forex_engine.forex_final_readiness_checker_v1 import (  # noqa: E402
    FOREX_FINAL_READINESS_BLOCKED,
    FOREX_FINAL_READINESS_REVIEW_READY,
    build_sample_evidence_age_metadata,
    build_sample_validator_evidence,
    evaluate_forex_final_readiness,
)
from automation.forex_engine.forex_owner_decision_brief_v1 import (  # noqa: E402
    OWNER_DECISION_BRIEF_BLOCKED,
    OWNER_DECISION_BRIEF_INCOMPLETE,
    OWNER_DECISION_BRIEF_REVIEW_READY,
    build_forex_owner_decision_brief,
)
from automation.forex_engine.risk_budget_engine_v1 import (  # noqa: E402
    RISK_BUDGET_ACCEPTED,
    RISK_BUDGET_BLOCKED,
    evaluate_risk_budget,
)
from automation.forex_engine.stop_pause_resume_engine_v1 import REVIEW_ONLY_RESUME, STOP_REQUIRED  # noqa: E402
from automation.forex_engine.supervised_demo_intent_card_v1 import DEMO_INTENT_OWNER_REVIEW_READY  # noqa: E402
from forex_delivery.read_only_live_data_bridge import build_read_only_live_data_bridge_read_model  # noqa: E402


PROTECTED_FLAGS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
)


def assert_permissions_false(result: dict) -> None:
    for flag in PROTECTED_FLAGS:
        assert result[flag] is False
        assert result["permissions"][flag] is False


def ready_chain_and_readiness() -> tuple[dict, dict]:
    chain = run_forex_closure_integration_bridge()
    readiness = evaluate_forex_final_readiness(
        chain,
        build_sample_validator_evidence(),
        build_sample_evidence_age_metadata(),
    )
    return chain, readiness


def owner_decision_from(
    payload: dict | None = None,
    evidence: dict | None = None,
) -> tuple[dict, dict, dict]:
    chain = run_forex_closure_integration_bridge(payload)
    readiness = evaluate_forex_final_readiness(
        chain,
        evidence or build_sample_validator_evidence(),
        build_sample_evidence_age_metadata(),
    )
    owner_brief = build_forex_owner_decision_brief(chain, readiness)
    return chain, readiness, owner_brief


def test_safe_review_path_builds_owner_brief_without_approval() -> None:
    chain, readiness = ready_chain_and_readiness()

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_REVIEW_READY
    assert result["decision_brief"]["approval_created"] is False
    assert result["decision_brief"]["execution_authority"] == "none"
    assert_permissions_false(result)


def test_broker_demo_readiness_lane_proves_review_only_chain() -> None:
    broker = evaluate_broker_health_readonly(build_sample_snapshot())
    read_only_model = build_read_only_live_data_bridge_read_model(
        env={},
        now_utc="2026-06-27T00:00:00Z",
    )
    demo_readiness = run_demo_trade_readiness_bridge()
    owner_approval = evaluate_demo_owner_approval_phrase_gate(
        build_sample_valid_owner_approval_phrase_input()
    )
    chain = run_forex_closure_integration_bridge()
    demo_intent = chain["stage_results"]["demo_intent"]
    final_readiness = evaluate_forex_final_readiness(
        chain,
        build_sample_validator_evidence(),
        build_sample_evidence_age_metadata(),
    )
    owner_brief = build_forex_owner_decision_brief(chain, final_readiness)

    assert broker["status"] == BROKER_HEALTH_REVIEW_READY
    assert read_only_model["mode"] == "READ_ONLY"
    assert read_only_model["execution_readiness"]["LIVE_READY"] is False
    assert read_only_model["capabilities"]["broker_write_calls_allowed"] is False
    assert read_only_model["capabilities"]["order_placement_allowed"] is False
    assert read_only_model["secret_status"]["SECRET_VALUES_PRINTED"] is False
    assert read_only_model["secret_status"]["ACCOUNT_ID_RECORDED"] is False
    assert read_only_model["secret_status"]["RAW_BROKER_PAYLOAD_RECORDED"] is False
    assert demo_readiness.classification == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW
    assert owner_approval.classification == DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW
    assert owner_approval.approval_phrase_review_allowed is True
    assert demo_intent["status"] == DEMO_INTENT_OWNER_REVIEW_READY
    assert final_readiness["status"] == FOREX_FINAL_READINESS_REVIEW_READY
    assert owner_brief["status"] == OWNER_DECISION_BRIEF_REVIEW_READY
    assert owner_brief["decision_brief"]["execution_authority"] == "none"

    for flag in (
        "demo_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "live_trading_allowed",
        "credential_access_allowed",
        "account_id_persistence_allowed",
    ):
        assert getattr(demo_readiness, flag) is False
        assert getattr(owner_approval, flag) is False
    assert_permissions_false(broker)
    assert_permissions_false(demo_intent)
    assert_permissions_false(final_readiness)
    assert_permissions_false(owner_brief)


def test_demo_trade_decision_dry_run_rehearsal_proves_review_ready_and_blockers(
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "complete_evidence"
    _write_demo_decision_complete_report_set(report_root)

    final_evidence = build_replay_walkforward_profitability_evidence_chain(report_root)
    payload = build_sample_integration_input()
    risk = evaluate_risk_budget(payload["candidate"], payload["risk_caps"])
    broker = evaluate_broker_health_readonly(payload["broker_snapshot"])
    chain = run_forex_closure_integration_bridge(payload)
    stop = chain["stage_results"]["stop"]
    demo_readiness = run_demo_trade_readiness_bridge()
    demo_intent = chain["stage_results"]["demo_intent"]
    owner_phrase = evaluate_demo_owner_approval_phrase_gate(
        build_sample_valid_owner_approval_phrase_input()
    )
    final_readiness = evaluate_forex_final_readiness(
        chain,
        build_sample_validator_evidence(),
        build_sample_evidence_age_metadata(),
    )
    owner_brief = build_forex_owner_decision_brief(chain, final_readiness)

    assert final_evidence["status"] == FINAL_EVIDENCE_CHAIN_REVIEW_READY
    assert final_evidence["final_closure_result"]["final_closure_status"] == FINAL_CLOSURE_REVIEW_READY
    assert risk["status"] == RISK_BUDGET_ACCEPTED
    assert broker["status"] == BROKER_HEALTH_REVIEW_READY
    assert stop["status"] == REVIEW_ONLY_RESUME
    assert demo_readiness.classification == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW
    assert demo_intent["status"] == DEMO_INTENT_OWNER_REVIEW_READY
    assert owner_phrase.classification == DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW
    assert final_readiness["status"] == FOREX_FINAL_READINESS_REVIEW_READY
    assert owner_brief["status"] == OWNER_DECISION_BRIEF_REVIEW_READY
    assert owner_brief["decision_brief"]["execution_authority"] == "none"
    assert_permissions_false(final_evidence)
    assert_permissions_false(risk)
    assert_permissions_false(broker)
    assert_permissions_false(chain)
    assert_permissions_false(demo_intent)
    assert_permissions_false(final_readiness)
    assert_permissions_false(owner_brief)
    _assert_demo_permissions_false(demo_readiness)
    _assert_demo_permissions_false(owner_phrase)

    missing_phrase = evaluate_demo_owner_approval_phrase_gate(
        build_sample_missing_owner_approval_phrase_input()
    )
    missing_phrase_evidence = build_sample_validator_evidence()
    missing_phrase_evidence["owner_approval_phrase_gate"] = False
    missing_phrase_readiness = _final_readiness_for(chain, missing_phrase_evidence)

    assert missing_phrase.classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_MISSING
    assert missing_phrase_readiness["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert "owner_approval_phrase_gate" in missing_phrase_readiness["missing_evidence"]
    _assert_demo_permissions_false(missing_phrase)
    assert_permissions_false(missing_phrase_readiness)

    missing_broker_evidence = build_sample_validator_evidence()
    missing_broker_evidence["sanitized_broker_readonly_evidence"] = False
    missing_broker_readiness = _final_readiness_for(chain, missing_broker_evidence)

    assert missing_broker_readiness["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert "sanitized_broker_readonly_evidence" in missing_broker_readiness["missing_evidence"]
    assert_permissions_false(missing_broker_readiness)

    missing_bundle_evidence = build_sample_validator_evidence()
    missing_bundle_evidence["final_evidence_bundle"] = False
    missing_bundle_readiness = _final_readiness_for(chain, missing_bundle_evidence)

    assert missing_bundle_readiness["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert "final_evidence_bundle" in missing_bundle_readiness["missing_evidence"]
    assert_permissions_false(missing_bundle_readiness)

    risk_payload = build_sample_integration_input()
    risk_payload["candidate"]["risk_per_trade_pct"] = 5.0
    risk_cap_result = evaluate_risk_budget(risk_payload["candidate"], risk_payload["risk_caps"])
    risk_blocked_chain = run_forex_closure_integration_bridge(risk_payload)
    risk_blocked_readiness = _final_readiness_for(
        risk_blocked_chain,
        build_sample_validator_evidence(),
    )

    assert risk_cap_result["status"] == RISK_BUDGET_BLOCKED
    assert risk_blocked_chain["status"] == FOREX_CLOSURE_CHAIN_BLOCKED
    assert risk_blocked_chain["stage_statuses"]["risk"] == RISK_BUDGET_BLOCKED
    assert risk_blocked_readiness["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert any("integrated chain" in item for item in risk_blocked_readiness["closure_blockers"])
    assert_permissions_false(risk_cap_result)
    assert_permissions_false(risk_blocked_chain)
    assert_permissions_false(risk_blocked_readiness)

    stop_payload = build_sample_integration_input()
    stop_payload["operator_halt_state"]["halt_requested"] = True
    stop_blocked_chain = run_forex_closure_integration_bridge(stop_payload)
    stop_blocked_readiness = _final_readiness_for(
        stop_blocked_chain,
        build_sample_validator_evidence(),
    )

    assert stop_blocked_chain["status"] == FOREX_CLOSURE_CHAIN_BLOCKED
    assert stop_blocked_chain["stage_statuses"]["stop"] == STOP_REQUIRED
    assert stop_blocked_readiness["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert any("operator halt" in item for item in stop_blocked_chain["blockers"])
    assert_permissions_false(stop_blocked_chain)
    assert_permissions_false(stop_blocked_readiness)

    for unsafe_flag in (
        "broker_execution_allowed",
        "broker_connection_allowed",
        "broker_api_call_allowed",
        "live_trading_allowed",
        "credential_access_allowed",
        "account_access_allowed",
        "order_submission_allowed",
        "money_movement_allowed",
        "compounding_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "webhook_allowed",
    ):
        unsafe_evidence = build_sample_validator_evidence()
        unsafe_evidence[unsafe_flag] = True
        unsafe_readiness = _final_readiness_for(chain, unsafe_evidence)

        assert unsafe_readiness["status"] == FOREX_FINAL_READINESS_BLOCKED
        assert any(unsafe_flag in item for item in unsafe_readiness["closure_blockers"])
        assert_permissions_false(unsafe_readiness)


def test_missing_input_blocks_as_incomplete() -> None:
    result = build_forex_owner_decision_brief(None, None)

    assert result["status"] == OWNER_DECISION_BRIEF_INCOMPLETE
    assert result["blockers"]
    assert_permissions_false(result)


def test_conflicting_readiness_status_blocks_brief() -> None:
    chain, readiness = ready_chain_and_readiness()
    readiness["status"] = "FOREX_FINAL_READINESS_BLOCKED"

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert any("final readiness" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_stale_evidence_gap_blocks_brief() -> None:
    chain, readiness = ready_chain_and_readiness()
    readiness["status"] = "FOREX_FINAL_READINESS_BLOCKED"
    readiness["stale_evidence"] = ["walk_forward_proof age 20 exceeds max 7"]

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert result["evidence_gaps"]
    assert_permissions_false(result)


def test_unsafe_chain_flag_blocks_brief() -> None:
    chain, readiness = ready_chain_and_readiness()
    chain["live_trading_allowed"] = True

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert any("unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_integration_fail_closed_reaches_brief_block() -> None:
    chain, readiness = ready_chain_and_readiness()
    chain["status"] = "FOREX_CLOSURE_CHAIN_BLOCKED"
    readiness["status"] = "FOREX_FINAL_READINESS_BLOCKED"

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert result["owner_approval_created"] is False
    assert_permissions_false(result)


def test_final_system_closure_decision_matrix() -> None:
    chain, readiness, owner_brief = owner_decision_from()

    assert chain["status"] == "FOREX_CLOSURE_CHAIN_REVIEW_READY"
    assert readiness["status"] == "FOREX_FINAL_READINESS_REVIEW_READY"
    assert owner_brief["status"] == OWNER_DECISION_BRIEF_REVIEW_READY
    assert owner_brief["decision_brief"]["execution_authority"] == "none"
    assert_permissions_false(owner_brief)

    missing_evidence = build_sample_validator_evidence()
    missing_evidence["persistent_profitability_proof"] = False
    _, missing_readiness, missing_owner_brief = owner_decision_from(
        evidence=missing_evidence
    )
    assert missing_readiness["status"] == "FOREX_FINAL_READINESS_BLOCKED"
    assert missing_owner_brief["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert "persistent_profitability_proof" in missing_readiness["missing_evidence"]

    missing_broker = build_sample_validator_evidence()
    missing_broker["sanitized_broker_readonly_evidence"] = False
    _, broker_readiness, broker_owner_brief = owner_decision_from(
        evidence=missing_broker
    )
    assert broker_readiness["status"] == "FOREX_FINAL_READINESS_BLOCKED"
    assert broker_owner_brief["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert "sanitized_broker_readonly_evidence" in broker_readiness["missing_evidence"]

    insufficient_profit = build_sample_integration_input()
    insufficient_profit["persistent_profitability_summary"]["expectancy"] = -0.1
    profit_chain, profit_readiness, profit_owner_brief = owner_decision_from(
        insufficient_profit
    )
    assert profit_chain["status"] == "FOREX_CLOSURE_CHAIN_BLOCKED"
    assert profit_readiness["status"] == "FOREX_FINAL_READINESS_BLOCKED"
    assert profit_owner_brief["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert any("persistent_profitability" in item for item in profit_chain["blockers"])

    compounding_request = deepcopy(insufficient_profit)
    compounding_request["persistent_profitability_summary"]["expectancy"] = 0.42
    compounding_request["compounding_policy"]["compounding_requested"] = True
    compounding_request["compounding_policy"]["owner_compounding_approval_present"] = False
    comp_chain, comp_readiness, comp_owner_brief = owner_decision_from(compounding_request)
    assert comp_chain["status"] == "FOREX_CLOSURE_CHAIN_BLOCKED"
    assert comp_readiness["status"] == "FOREX_FINAL_READINESS_BLOCKED"
    assert comp_owner_brief["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert any("compounding requested without owner approval" in item for item in comp_chain["blockers"])

    stop_condition = deepcopy(compounding_request)
    stop_condition["compounding_policy"]["compounding_requested"] = False
    stop_condition["operator_halt_state"]["halt_requested"] = True
    stop_chain, stop_readiness, stop_owner_brief = owner_decision_from(stop_condition)
    assert stop_chain["status"] == "FOREX_CLOSURE_CHAIN_BLOCKED"
    assert stop_readiness["status"] == "FOREX_FINAL_READINESS_BLOCKED"
    assert stop_owner_brief["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert any("operator halt" in item for item in stop_chain["blockers"])

    for flag in (
        "broker_execution_allowed",
        "live_trading_allowed",
        "credential_access_allowed",
        "account_access_allowed",
        "money_movement_allowed",
    ):
        unsafe_payload = build_sample_integration_input()
        unsafe_payload["compounding_policy"][flag] = True
        unsafe_chain, unsafe_readiness, unsafe_owner_brief = owner_decision_from(
            unsafe_payload
        )
        assert unsafe_chain["status"] == "FOREX_CLOSURE_CHAIN_BLOCKED"
        assert unsafe_readiness["status"] == "FOREX_FINAL_READINESS_BLOCKED"
        assert unsafe_owner_brief["status"] == OWNER_DECISION_BRIEF_BLOCKED
        assert any(f"{flag} is unsafe true" in item for item in unsafe_chain["blockers"])
        assert_permissions_false(unsafe_owner_brief)


def _final_readiness_for(chain: dict, validator_evidence: dict) -> dict:
    return evaluate_forex_final_readiness(
        chain,
        validator_evidence,
        build_sample_evidence_age_metadata(),
    )


def _assert_demo_permissions_false(result: object) -> None:
    for flag in (
        "demo_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "live_trading_allowed",
        "credential_access_allowed",
        "account_id_persistence_allowed",
    ):
        assert getattr(result, flag) is False


def _write_demo_decision_complete_report_set(report_root: Path) -> None:
    report_root.mkdir()
    (report_root / "AIOS_FOREX_SESSION_REPLAY_V1_REPORT.md").write_text(
        "\n".join(
            [
                "- replay_id: replay-direct-001",
                "- run_count: 2",
                "- event_count: 30",
                "- mismatch_count: 0",
                "- deterministic_replay: true",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md").write_text(
        "\n".join(
            [
                "- windows_total: 4",
                "- windows_passed: 4",
                "- oos_segments_total: 3",
                "- oos_segments_passed: 3",
                "- min_pass_rate: 0.75",
                "- max_drawdown: 0.02",
                "- max_allowed_drawdown: 0.05",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_PROFITABILITY_VERDICT_V1.md").write_text(
        "\n".join(
            [
                "- closed_trade_count: 40",
                "- min_closed_trade_count: 30",
                "- expectancy: 0.40",
                "- min_expectancy: 0.05",
                "- profit_factor: 1.50",
                "- min_profit_factor: 1.25",
                "- max_drawdown: 0.02",
                "- max_allowed_drawdown: 0.05",
                "- consecutive_profitable_periods: 5",
                "- min_profitable_periods: 4",
                "- after_costs: true",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_TRUSTED_PROFIT_22_6_READINESS_V1.md").write_text(
        "\n".join(
            [
                "- observed_hours: 23",
                "- required_hours: 22",
                "- observed_sessions: 6",
                "- required_sessions: 6",
                "- observed_days: 6",
                "- required_days: 6",
                "- interruption_count: 0",
                "- max_interruption_count: 2",
                "- manual_override_count: 0",
                "- max_manual_override_count: 1",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_DYNAMIC_OWNER_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "# Dynamic Owner Review Source",
                "",
                "- Owner packet status: `SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW`",
                "- Anthony may review the local packet manually.",
                "- This does not authorize execution.",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_DYNAMIC_VALIDATOR_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "# Dynamic Validator Source",
                "",
                "## VALIDATORS RUN",
                "- `python -m pytest tests/forex_engine -q`",
                "",
                "## VALIDATORS PASSED",
                "- `python -m pytest tests/forex_engine -q`: PASS.",
                "- `git diff --check`: PASS.",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_DYNAMIC_BROKER_READONLY_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "# Dynamic Broker Read-Only Source",
                "",
                "- READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW: True",
                "- source_type: broker read-only sanitized evidence",
                "- source_label: SANITIZED_DEMO_READONLY",
                "- broker_account_reachable: True",
                "- open_positions_reconciled: True",
                "- daily_pl_available: True",
                "- realized_pl_available: True",
                "- unrealized_pl_available: True",
                "- margin_risk_available: True",
                "- trading_history_writeback_verified: True",
            ]
        ),
        encoding="utf-8",
    )
