from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.next_trade_eligibility_repeat_proof_gate_v1 import (  # noqa: E402
    BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED,
    BUCKET_UPDATE_ELIGIBLE_BREAKEVEN,
    BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS,
    BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
    NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK,
    NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY,
    NEXT_TRADE_BLOCKED_OPEN_EXPOSURE,
    NEXT_TRADE_BLOCKED_OWNER_APPROVAL_MISSING,
    NEXT_TRADE_BLOCKED_PRIOR_TRADE_STILL_OPEN,
    NEXT_TRADE_BLOCKED_RISK_LIMIT,
    NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID,
    NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW,
    OWNER_RUN_CLOSED_BREAKEVEN_OTHER,
    OWNER_RUN_CLOSED_BY_STOP_LOSS,
    OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
    OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
    evaluate_next_trade_eligibility_repeat_proof_gate_v1,
    next_trade_eligibility_repeat_proof_gate_samples_v1,
)
from scripts.forex_delivery.run_next_trade_eligibility_repeat_proof_gate_v1 import (  # noqa: E402
    main as script_main,
)


def owner_decision(status: str, realized_pl: str | None = "0.0012") -> dict:
    return {
        "exercise_status": status,
        "trade_anchor": {"trade_id": "328"},
        "realized_pl": realized_pl,
        "is_closed": status != OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
        "is_open": status == OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
        "classifier_decision": {
            "is_closed": status != OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT
        },
    }


def bucket_decision(status: str = BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT) -> dict:
    return {
        "gate_status": status,
        "trade_id": "328",
        "bucket_update_performed": False,
        "next_trade_authorized": False,
    }


def exposure_state(**overrides) -> dict:
    payload = {
        "open_trade_count": 0,
        "open_position_count": 0,
        "pending_order_count": 0,
    }
    payload.update(overrides)
    return payload


def owner_approval(approved: bool = True) -> dict:
    return {"owner_approved_next_trade_review": approved}


def risk_state(**overrides) -> dict:
    payload = {
        "review_only": True,
        "risk_review_only": True,
        "execution_allowed": False,
        "next_trade_execution_allowed": False,
        "order_placement_allowed": False,
        "risk_limit_breached": False,
        "max_loss_limit_breached": False,
        "daily_stop_triggered": False,
        "kill_switch_active": False,
    }
    payload.update(overrides)
    return payload


def evaluate(
    owner: dict | None = None,
    bucket: dict | None = None,
    exposure: dict | None = None,
    approval: dict | None = None,
    risk: dict | None = None,
) -> dict:
    return evaluate_next_trade_eligibility_repeat_proof_gate_v1(
        owner or owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT),
        bucket or bucket_decision(),
        exposure if exposure is not None else exposure_state(),
        approval if approval is not None else owner_approval(),
        risk if risk is not None else risk_state(),
    )


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        try:
            code = script_main(args)
        except SystemExit as exc:
            code = int(exc.code)
    return code, json.loads(stream.getvalue())


def assert_review_only_safety(result: dict) -> None:
    assert result["next_trade_authorized"] is False
    assert result["order_placement_authorized"] is False
    assert result["broker_call_authorized"] is False
    assert result["live_funding_authorized"] is False
    for flag, value in result["safety_proof"].items():
        assert value is False, flag
        assert result[flag] is False, flag
    for flag, value in result["execution_authority"].items():
        assert value is False, flag


def test_eligible_closed_profit_allows_owner_review_only() -> None:
    result = evaluate()

    assert result["gate_status"] == NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW
    assert result["next_trade_review_authorized"] is True
    assert result["trade_id"] == "328"
    assert result["prior_trade_result_status"] == OWNER_RUN_CLOSED_BY_TAKE_PROFIT
    assert result["bucket_gate_status"] == BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT
    assert_review_only_safety(result)


def test_closed_loss_can_be_eligible_for_owner_review_only() -> None:
    result = evaluate(
        owner_decision(OWNER_RUN_CLOSED_BY_STOP_LOSS, "-0.0010"),
        bucket_decision(BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS),
    )

    assert result["gate_status"] == NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW
    assert result["next_trade_review_authorized"] is True
    assert_review_only_safety(result)


def test_closed_breakeven_can_be_eligible_for_owner_review_only() -> None:
    result = evaluate(
        owner_decision(OWNER_RUN_CLOSED_BREAKEVEN_OTHER, "0.0000"),
        bucket_decision(BUCKET_UPDATE_ELIGIBLE_BREAKEVEN),
    )

    assert result["gate_status"] == NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW
    assert result["next_trade_review_authorized"] is True
    assert_review_only_safety(result)


def test_open_trade_exposure_blocks_next_trade_review() -> None:
    result = evaluate(exposure=exposure_state(open_trade_count=1))

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_OPEN_EXPOSURE
    assert "open_trade_count_must_be_zero" in result["blockers"]
    assert result["next_trade_review_authorized"] is False
    assert_review_only_safety(result)


def test_open_position_exposure_blocks_next_trade_review() -> None:
    result = evaluate(exposure=exposure_state(open_position_count=1))

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_OPEN_EXPOSURE
    assert "open_position_count_must_be_zero" in result["blockers"]


def test_pending_orders_block_next_trade_review() -> None:
    result = evaluate(exposure=exposure_state(pending_order_count=1))

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_OPEN_EXPOSURE
    assert "pending_order_count_must_be_zero" in result["blockers"]


def test_prior_trade_still_open_blocks_review_before_exposure_gate() -> None:
    result = evaluate(
        owner=owner_decision(OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT, None),
        exposure=exposure_state(open_trade_count=1),
    )

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_PRIOR_TRADE_STILL_OPEN
    assert "prior_trade_still_open_no_closed_result_proof" in result["blockers"]


def test_bucket_gate_not_ready_blocks_review() -> None:
    result = evaluate(
        bucket=bucket_decision("BUCKET_UPDATE_BLOCKED_STILL_OPEN")
    )

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY
    assert "bucket_gate_status_not_ready_BUCKET_UPDATE_BLOCKED_STILL_OPEN" in result[
        "blockers"
    ]


def test_already_applied_without_safe_idempotency_blocks_repeat_risk() -> None:
    result = evaluate(
        bucket={
            **bucket_decision(BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED),
            "already_applied": True,
        }
    )

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK
    assert "bucket_gate_already_applied_without_safe_idempotent_state" in result[
        "blockers"
    ]


def test_already_applied_with_safe_idempotency_can_continue_to_review() -> None:
    result = evaluate(
        bucket={
            **bucket_decision(BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED),
            "warnings": ["idempotency_guard_blocked_reapply"],
        }
    )

    assert result["gate_status"] == NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW
    assert "already_applied_bucket_gate_accepted_as_safe_idempotent" in result[
        "warnings"
    ]
    assert_review_only_safety(result)


def test_explicit_repeat_risk_blocks_review() -> None:
    result = evaluate(
        bucket={
            **bucket_decision(BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT),
            "repeat_trade_risk": True,
        }
    )

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK
    assert "repeat_trade_risk_true" in result["blockers"]


def test_owner_approval_missing_blocks_review() -> None:
    result = evaluate(approval=owner_approval(False))

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_OWNER_APPROVAL_MISSING
    assert "owner_approved_next_trade_review_true_required" in result["blockers"]


def test_risk_limit_blocks_review() -> None:
    result = evaluate(risk=risk_state(max_loss_limit_breached=True))

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_RISK_LIMIT
    assert "max_loss_limit_breached_true" in result["blockers"]


def test_missing_review_only_risk_state_blocks_as_risk_limit() -> None:
    result = evaluate(risk={"risk_limit_breached": False})

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_RISK_LIMIT
    assert "risk_state_must_be_review_only" in result["blockers"]


def test_unsafe_authority_flag_blocks_as_invalid() -> None:
    result = evaluate(
        owner={
            **owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT),
            "execution_authority": {"broker_call_allowed": True},
        }
    )

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID
    assert "unsafe_owner_run_decision_broker_call_allowed_true" in result["blockers"]


def test_sensitive_and_raw_broker_fields_block_as_invalid() -> None:
    result = evaluate(
        bucket={
            **bucket_decision(),
            "endpoint_url": "https://example.invalid/orders",
            "raw_payload": {"sample": "payload"},
            "runtime_account_id": "SANITIZED_ACCOUNT",
        }
    )

    assert result["gate_status"] == NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID
    assert "unsafe_bucket_gate_decision_endpoint_url_present" in result["blockers"]
    assert "unsafe_bucket_gate_decision_raw_payload_present" in result["blockers"]
    assert "unsafe_bucket_gate_decision_runtime_account_id_present" in result[
        "blockers"
    ]


def test_inputs_are_not_mutated() -> None:
    owner = owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT)
    bucket = bucket_decision()
    exposure = exposure_state()
    approval = owner_approval()
    risk = risk_state()
    before = deepcopy((owner, bucket, exposure, approval, risk))

    result = evaluate(owner, bucket, exposure, approval, risk)

    assert result["gate_status"] == NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW
    assert (owner, bucket, exposure, approval, risk) == before


def test_samples_cover_required_cli_names_and_statuses() -> None:
    samples = next_trade_eligibility_repeat_proof_gate_samples_v1()

    assert set(samples) == {
        "eligible",
        "open-exposure",
        "still-open",
        "bucket-not-ready",
        "already-applied",
        "owner-missing",
        "risk-limit",
        "unsafe",
    }
    statuses = {
        evaluate_next_trade_eligibility_repeat_proof_gate_v1(
            sample["owner_run_decision"],
            sample["bucket_gate_decision"],
            sample["exposure_state"],
            sample["owner_approval"],
            sample["risk_state"],
        )["gate_status"]
        for sample in samples.values()
    }
    assert statuses == {
        NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW,
        NEXT_TRADE_BLOCKED_OPEN_EXPOSURE,
        NEXT_TRADE_BLOCKED_PRIOR_TRADE_STILL_OPEN,
        NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY,
        NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK,
        NEXT_TRADE_BLOCKED_OWNER_APPROVAL_MISSING,
        NEXT_TRADE_BLOCKED_RISK_LIMIT,
        NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID,
    }


def test_cli_print_template_outputs_json_only_and_false_safety_flags() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert payload["script_status"] == (
        "NEXT_TRADE_ELIGIBILITY_REPEAT_PROOF_GATE_TEMPLATE_ONLY"
    )
    assert payload["template"]["runtime_input_rule"]["review_eligibility_only"] is True
    assert payload["broker_call_performed"] is False
    assert payload["oanda_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["next_trade_authorized"] is False
    assert payload["live_funding_performed"] is False


def test_cli_sample_all_outputs_all_decisions_with_false_safety_flags() -> None:
    code, payload = run_script(["--sample", "all"])

    assert code == 0
    assert payload["script_status"] == (
        "NEXT_TRADE_ELIGIBILITY_REPEAT_PROOF_GATE_DRY_RUN_SAMPLES"
    )
    assert set(payload["decisions"]) == set(
        next_trade_eligibility_repeat_proof_gate_samples_v1()
    )
    for decision in payload["decisions"].values():
        assert_review_only_safety(decision)


def test_cli_sample_owner_missing_returns_owner_missing_block() -> None:
    code, payload = run_script(["--sample", "owner-missing"])

    assert code == 0
    decision = payload["decisions"]["owner-missing"]
    assert decision["gate_status"] == NEXT_TRADE_BLOCKED_OWNER_APPROVAL_MISSING
    assert decision["next_trade_review_authorized"] is False


def test_cli_invalid_argument_prints_json_block() -> None:
    code, payload = run_script(["--unknown"])

    assert code == 2
    assert payload["script_status"] == (
        "NEXT_TRADE_ELIGIBILITY_REPEAT_PROOF_GATE_INPUT_BLOCKED"
    )
    assert payload["broker_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["next_trade_authorized"] is False
