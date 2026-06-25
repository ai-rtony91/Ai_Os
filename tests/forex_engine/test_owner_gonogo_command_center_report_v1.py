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

from automation.forex_engine.owner_gonogo_command_center_report_v1 import (  # noqa: E402
    OWNER_GONOGO_BLOCKED_BUCKET_GATE,
    OWNER_GONOGO_BLOCKED_FUNDING,
    OWNER_GONOGO_BLOCKED_NEXT_TRADE,
    OWNER_GONOGO_BLOCKED_NO_CLOSED_RESULT,
    OWNER_GONOGO_BLOCKED_RISK,
    OWNER_GONOGO_BLOCKED_TRADE_STILL_OPEN,
    OWNER_GONOGO_BLOCKED_UNSAFE_INPUT,
    OWNER_GONOGO_READY_FOR_REVIEW,
    SAFETY_AUTHORITY_FIELDS,
    build_owner_gonogo_command_center_report_v1,
    owner_gonogo_command_center_report_samples_v1,
    owner_gonogo_command_center_report_template_v1,
)
from scripts.forex_delivery.run_owner_gonogo_command_center_report_v1 import (  # noqa: E402
    main as script_main,
)


def ready_payload() -> dict:
    return deepcopy(owner_gonogo_command_center_report_template_v1())


def evaluate(**overrides) -> dict:
    payload = ready_payload()
    payload.update(overrides)
    return build_owner_gonogo_command_center_report_v1(
        closed_result=payload.get("closed_result"),
        bucket_gate_decision=payload.get("bucket_gate_decision"),
        next_trade_eligibility=payload.get("next_trade_eligibility"),
        funding_readiness=payload.get("funding_readiness"),
        account_separation=payload.get("account_separation"),
        risk_state=payload.get("risk_state"),
        owner_context=payload.get("owner_context"),
    )


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        try:
            code = script_main(args)
        except SystemExit as exc:
            code = int(exc.code)
    return code, json.loads(stream.getvalue())


def assert_safety_authority_false(result: dict) -> None:
    for flag in SAFETY_AUTHORITY_FIELDS:
        assert result[flag] is False, flag
        assert result["safety_authority"][flag] is False, flag


def test_ready_case_returns_ready_for_owner_review() -> None:
    result = evaluate()

    assert result["command_status"] == OWNER_GONOGO_READY_FOR_REVIEW
    assert result["readiness_matrix"]["trade_closed"] is True
    assert result["next_safe_action"] == (
        "owner_review_command_center_report_no_trade_no_transfer"
    )
    assert_safety_authority_false(result)


def test_still_open_trade_blocks() -> None:
    payload = ready_payload()
    payload["closed_result"]["exercise_status"] = (
        "OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT"
    )
    payload["closed_result"]["is_closed"] = False
    payload["closed_result"]["is_open"] = True

    result = evaluate(closed_result=payload["closed_result"])

    assert result["command_status"] == OWNER_GONOGO_BLOCKED_TRADE_STILL_OPEN
    assert "closed_result_reports_trade_still_open" in result["blockers"]
    assert_safety_authority_false(result)


def test_missing_closed_result_blocks() -> None:
    result = evaluate(closed_result=None)

    assert result["command_status"] == OWNER_GONOGO_BLOCKED_NO_CLOSED_RESULT
    assert "closed_result_required" in result["blockers"]
    assert_safety_authority_false(result)


def test_bucket_blocked_blocks() -> None:
    result = evaluate(
        bucket_gate_decision={
            "gate_status": "BUCKET_UPDATE_BLOCKED_STILL_OPEN",
            "bucket_update_authorized": False,
            "blockers": ["owner_run_trade_still_open_no_realized_result"],
        }
    )

    assert result["command_status"] == OWNER_GONOGO_BLOCKED_BUCKET_GATE
    assert "owner_run_trade_still_open_no_realized_result" in result["blockers"]
    assert_safety_authority_false(result)


def test_next_trade_blocked_blocks() -> None:
    payload = ready_payload()
    payload["next_trade_eligibility"]["gate_status"] = (
        "NEXT_TRADE_BLOCKED_OPEN_EXPOSURE"
    )
    payload["next_trade_eligibility"]["next_trade_review_authorized"] = False
    payload["next_trade_eligibility"]["open_trade_count"] = 1

    result = evaluate(next_trade_eligibility=payload["next_trade_eligibility"])

    assert result["command_status"] == OWNER_GONOGO_BLOCKED_NEXT_TRADE
    assert "open_trade_count_must_be_zero" in result["blockers"]
    assert_safety_authority_false(result)


def test_account_separation_open_exposure_blocks_next_trade() -> None:
    payload = ready_payload()
    payload["account_separation"]["open_trade_count"] = 1

    result = evaluate(account_separation=payload["account_separation"])

    assert result["command_status"] == OWNER_GONOGO_BLOCKED_NEXT_TRADE
    assert "open_trade_count_must_be_zero" in result["blockers"]
    assert_safety_authority_false(result)


def test_funding_blocked_blocks() -> None:
    payload = ready_payload()
    payload["funding_readiness"]["gate_status"] = (
        "FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE"
    )
    payload["funding_readiness"]["funding_review_authorized"] = False
    payload["funding_readiness"]["open_position_count"] = 1

    result = evaluate(funding_readiness=payload["funding_readiness"])

    assert result["command_status"] == OWNER_GONOGO_BLOCKED_FUNDING
    assert "open_position_count_must_be_zero" in result["blockers"]
    assert_safety_authority_false(result)


def test_risk_blocked_blocks() -> None:
    payload = ready_payload()
    payload["risk_state"]["max_loss_limit_breached"] = True

    result = evaluate(risk_state=payload["risk_state"])

    assert result["command_status"] == OWNER_GONOGO_BLOCKED_RISK
    assert "max_loss_limit_breached_true" in result["blockers"]
    assert_safety_authority_false(result)


def test_unsafe_input_blocks() -> None:
    payload = ready_payload()
    payload["owner_context"]["api_key"] = "sk-test-not-real"
    payload["closed_result"]["headers"] = {"Authorization": "Bearer x"}
    payload["funding_readiness"]["endpoint_url"] = "https://broker.invalid/orders"

    result = evaluate(
        owner_context=payload["owner_context"],
        closed_result=payload["closed_result"],
        funding_readiness=payload["funding_readiness"],
    )

    assert result["command_status"] == OWNER_GONOGO_BLOCKED_UNSAFE_INPUT
    assert "unsafe_owner_context_api_key_present" in result["blockers"]
    assert "unsafe_closed_result_headers_present" in result["blockers"]
    assert "unsafe_funding_readiness_endpoint_url_present" in result["blockers"]
    assert_safety_authority_false(result)


def test_all_authority_flags_are_always_false_across_samples() -> None:
    for sample in owner_gonogo_command_center_report_samples_v1().values():
        result = build_owner_gonogo_command_center_report_v1(
            closed_result=sample.get("closed_result"),
            bucket_gate_decision=sample.get("bucket_gate_decision"),
            next_trade_eligibility=sample.get("next_trade_eligibility"),
            funding_readiness=sample.get("funding_readiness"),
            account_separation=sample.get("account_separation"),
            risk_state=sample.get("risk_state"),
            owner_context=sample.get("owner_context"),
        )
        assert_safety_authority_false(result)


def test_input_dictionaries_are_not_mutated() -> None:
    payload = ready_payload()
    before = deepcopy(payload)

    result = build_owner_gonogo_command_center_report_v1(
        closed_result=payload["closed_result"],
        bucket_gate_decision=payload["bucket_gate_decision"],
        next_trade_eligibility=payload["next_trade_eligibility"],
        funding_readiness=payload["funding_readiness"],
        account_separation=payload["account_separation"],
        risk_state=payload["risk_state"],
        owner_context=payload["owner_context"],
    )

    assert result["command_status"] == OWNER_GONOGO_READY_FOR_REVIEW
    assert payload == before


def test_cli_samples_run() -> None:
    expected_samples = {
        "ready",
        "trade-open",
        "no-closed-result",
        "bucket-blocked",
        "next-trade-blocked",
        "funding-blocked",
        "risk-blocked",
        "unsafe",
    }
    assert set(owner_gonogo_command_center_report_samples_v1()) == expected_samples

    for sample in ["all", *sorted(expected_samples)]:
        code, payload = run_script(["--sample", sample])

        assert code == 0
        assert payload["script_status"] == (
            "OWNER_GONOGO_COMMAND_CENTER_REPORT_DRY_RUN_SAMPLES"
        )
        assert payload["json_only"] is True
        if sample == "all":
            assert set(payload["decisions"]) == expected_samples
        else:
            assert set(payload["decisions"]) == {sample}
        for decision in payload["decisions"].values():
            assert_safety_authority_false(decision)


def test_cli_print_template_runs() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert payload["script_status"] == (
        "OWNER_GONOGO_COMMAND_CENTER_REPORT_TEMPLATE_ONLY"
    )
    assert payload["template"]["runtime_input_rule"]["broker_or_oanda_call_supported"] is False
    for flag in SAFETY_AUTHORITY_FIELDS:
        assert payload[flag] is False


def test_cli_rejects_unsafe_input_path() -> None:
    code, payload = run_script(["--input-json", ".env"])

    assert code == 2
    assert payload["script_status"] == (
        "OWNER_GONOGO_COMMAND_CENTER_REPORT_INPUT_BLOCKED"
    )
    assert "unsafe_input_json_path_rejected" in payload["blockers"]
    for flag in SAFETY_AUTHORITY_FIELDS:
        assert payload[flag] is False


def test_result_is_json_serializable() -> None:
    result = evaluate()

    encoded = json.dumps(result, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded["command_status"] == OWNER_GONOGO_READY_FOR_REVIEW
