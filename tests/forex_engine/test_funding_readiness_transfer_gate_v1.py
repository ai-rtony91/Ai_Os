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

from automation.forex_engine.funding_readiness_transfer_gate_v1 import (  # noqa: E402
    FUNDING_REVIEW_BLOCKED_BUCKET_NOT_READY,
    FUNDING_REVIEW_BLOCKED_INVALID_AMOUNT,
    FUNDING_REVIEW_BLOCKED_NEXT_TRADE_NOT_READY,
    FUNDING_REVIEW_BLOCKED_NO_OWNER_INTENT,
    FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE,
    FUNDING_REVIEW_BLOCKED_OWNER_APPROVAL_MISSING,
    FUNDING_REVIEW_BLOCKED_RISK_LIMIT,
    FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT,
    FUNDING_REVIEW_READY,
    evaluate_funding_readiness_transfer_gate_v1,
    funding_readiness_transfer_gate_samples_v1,
    funding_readiness_transfer_gate_template_v1,
)
from scripts.forex_delivery.run_funding_readiness_transfer_gate_v1 import (  # noqa: E402
    main as script_main,
)


ALWAYS_FALSE_FLAGS = (
    "funding_transfer_authorized",
    "deposit_authorized",
    "withdrawal_authorized",
    "broker_call_authorized",
    "oanda_call_authorized",
    "order_placement_authorized",
    "live_trading_authorized",
    "runtime_mutation_authorized",
)


def ready_payload() -> dict:
    return deepcopy(funding_readiness_transfer_gate_template_v1())


def evaluate(**overrides) -> dict:
    payload = ready_payload()
    payload.update(overrides)
    return evaluate_funding_readiness_transfer_gate_v1(
        funding_intent=payload.get("funding_intent"),
        account_separation=payload.get("account_separation"),
        bucket_gate_decision=payload.get("bucket_gate_decision"),
        next_trade_eligibility=payload.get("next_trade_eligibility"),
        risk_state=payload.get("risk_state"),
        owner_approval=payload.get("owner_approval"),
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
    for flag in ALWAYS_FALSE_FLAGS:
        assert result[flag] is False, flag
    for flag, value in result["safety_proof"].items():
        assert value is False, flag
        assert result[flag] is False, flag
    for flag, value in result["execution_authority"].items():
        assert value is False, flag
        assert result[flag] is False, flag


def test_ready_case_authorizes_owner_funding_review_only() -> None:
    result = evaluate()

    assert result["gate_status"] == FUNDING_REVIEW_READY
    assert result["funding_review_authorized"] is True
    assert result["proposed_amount"] == "100.00"
    assert result["proposed_currency"] == "USD"
    assert result["funding_mode"] == "review_only"
    assert_review_only_safety(result)


def test_no_intent_blocks() -> None:
    result = evaluate(funding_intent=None)

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_NO_OWNER_INTENT
    assert result["funding_review_authorized"] is False
    assert "explicit_funding_intent_required" in result["blockers"]
    assert_review_only_safety(result)


def test_missing_owner_approval_blocks() -> None:
    result = evaluate(owner_approval={"owner_approved_funding_review": False})

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_OWNER_APPROVAL_MISSING
    assert "owner_approved_funding_review_true_required" in result["blockers"]
    assert result["funding_review_authorized"] is False
    assert_review_only_safety(result)


def test_open_trade_blocks() -> None:
    payload = ready_payload()
    payload["next_trade_eligibility"]["open_trade_count"] = 1

    result = evaluate(next_trade_eligibility=payload["next_trade_eligibility"])

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE
    assert "open_trade_count_must_be_zero" in result["blockers"]
    assert_review_only_safety(result)


def test_open_position_blocks() -> None:
    payload = ready_payload()
    payload["account_separation"]["open_position_count"] = 1

    result = evaluate(account_separation=payload["account_separation"])

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE
    assert "open_position_count_must_be_zero" in result["blockers"]
    assert_review_only_safety(result)


def test_pending_order_blocks() -> None:
    payload = ready_payload()
    payload["account_separation"]["pending_order_count"] = 1

    result = evaluate(account_separation=payload["account_separation"])

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE
    assert "pending_order_count_must_be_zero" in result["blockers"]
    assert_review_only_safety(result)


def test_bucket_not_ready_blocks() -> None:
    result = evaluate(
        bucket_gate_decision={
            "gate_status": "BUCKET_UPDATE_BLOCKED_STILL_OPEN",
            "bucket_update_authorized": False,
        }
    )

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_BUCKET_NOT_READY
    assert "bucket_gate_status_not_ready_BUCKET_UPDATE_BLOCKED_STILL_OPEN" in result[
        "blockers"
    ]
    assert_review_only_safety(result)


def test_account_separation_missing_blocks_as_bucket_not_ready() -> None:
    result = evaluate(account_separation=None)

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_BUCKET_NOT_READY
    assert "account_separation_state_required" in result["blockers"]
    assert_review_only_safety(result)


def test_next_trade_not_ready_blocks() -> None:
    result = evaluate(
        next_trade_eligibility={
            "gate_status": "NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY",
            "next_trade_review_authorized": False,
            "open_trade_count": 0,
            "open_position_count": 0,
            "pending_order_count": 0,
        }
    )

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_NEXT_TRADE_NOT_READY
    assert (
        "next_trade_status_not_ready_NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY"
        in result["blockers"]
    )
    assert_review_only_safety(result)


def test_risk_limit_blocks() -> None:
    payload = ready_payload()
    payload["risk_state"]["max_loss_limit_breached"] = True

    result = evaluate(risk_state=payload["risk_state"])

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_RISK_LIMIT
    assert "max_loss_limit_breached_true" in result["blockers"]
    assert_review_only_safety(result)


def test_risk_not_review_only_blocks() -> None:
    payload = ready_payload()
    payload["risk_state"]["review_only"] = False
    payload["risk_state"]["risk_review_only"] = False

    result = evaluate(risk_state=payload["risk_state"])

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_RISK_LIMIT
    assert "risk_state_must_be_review_only" in result["blockers"]
    assert_review_only_safety(result)


def test_zero_and_negative_amount_block() -> None:
    for amount in ("0", "-1"):
        payload = ready_payload()
        payload["funding_intent"]["proposed_amount"] = amount

        result = evaluate(funding_intent=payload["funding_intent"])

        assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_INVALID_AMOUNT
        assert "proposed_amount_must_be_positive" in result["blockers"]
        assert_review_only_safety(result)


def test_missing_currency_blocks() -> None:
    payload = ready_payload()
    payload["funding_intent"]["proposed_currency"] = ""

    result = evaluate(funding_intent=payload["funding_intent"])

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_INVALID_AMOUNT
    assert "proposed_currency_required" in result["blockers"]
    assert_review_only_safety(result)


def test_non_review_only_mode_blocks_as_unsafe_input() -> None:
    payload = ready_payload()
    payload["funding_intent"]["funding_mode"] = "transfer_now"

    result = evaluate(funding_intent=payload["funding_intent"])

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT
    assert "funding_mode_must_be_review_only" in result["blockers"]
    assert_review_only_safety(result)


def test_unsafe_input_blocks() -> None:
    payload = ready_payload()
    payload["funding_intent"]["api_key"] = "sk-test-not-real"
    payload["account_separation"]["endpoint_url"] = "https://broker.invalid/orders"
    payload["next_trade_eligibility"]["headers"] = {"Authorization": "Bearer x"}

    result = evaluate(
        funding_intent=payload["funding_intent"],
        account_separation=payload["account_separation"],
        next_trade_eligibility=payload["next_trade_eligibility"],
    )

    assert result["gate_status"] == FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT
    assert "unsafe_funding_intent_api_key_present" in result["blockers"]
    assert "unsafe_account_separation_endpoint_url_present" in result["blockers"]
    assert "unsafe_next_trade_eligibility_headers_present" in result["blockers"]
    assert_review_only_safety(result)


def test_transfer_deposit_withdraw_broker_oanda_order_live_flags_always_false() -> None:
    payloads = [
        ready_payload(),
        {"funding_intent": None},
        {
            **ready_payload(),
            "owner_approval": {"owner_approved_funding_review": False},
        },
        {
            **ready_payload(),
            "bucket_gate_decision": {"gate_status": "BLOCKED"},
        },
    ]

    for payload in payloads:
        result = evaluate_funding_readiness_transfer_gate_v1(
            funding_intent=payload.get("funding_intent"),
            account_separation=payload.get("account_separation"),
            bucket_gate_decision=payload.get("bucket_gate_decision"),
            next_trade_eligibility=payload.get("next_trade_eligibility"),
            risk_state=payload.get("risk_state"),
            owner_approval=payload.get("owner_approval"),
        )
        assert_review_only_safety(result)


def test_input_dictionaries_are_not_mutated() -> None:
    payload = ready_payload()
    before = deepcopy(payload)

    result = evaluate_funding_readiness_transfer_gate_v1(
        funding_intent=payload["funding_intent"],
        account_separation=payload["account_separation"],
        bucket_gate_decision=payload["bucket_gate_decision"],
        next_trade_eligibility=payload["next_trade_eligibility"],
        risk_state=payload["risk_state"],
        owner_approval=payload["owner_approval"],
    )

    assert result["gate_status"] == FUNDING_REVIEW_READY
    assert payload == before


def test_cli_samples_run() -> None:
    expected_samples = {
        "ready",
        "no-intent",
        "approval-missing",
        "open-exposure",
        "invalid-amount",
        "unsafe",
    }
    assert set(funding_readiness_transfer_gate_samples_v1()) == expected_samples

    for sample in ["all", *sorted(expected_samples)]:
        code, payload = run_script(["--sample", sample])

        assert code == 0
        assert payload["script_status"] == (
            "FUNDING_READINESS_TRANSFER_GATE_DRY_RUN_SAMPLES"
        )
        assert payload["json_only"] is True
        if sample == "all":
            assert set(payload["decisions"]) == expected_samples
        else:
            assert set(payload["decisions"]) == {sample}
        for decision in payload["decisions"].values():
            assert_review_only_safety(decision)


def test_cli_print_template_runs() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert payload["script_status"] == "FUNDING_READINESS_TRANSFER_GATE_TEMPLATE_ONLY"
    assert payload["template"]["runtime_input_rule"]["owner_review_only"] is True
    for flag in ALWAYS_FALSE_FLAGS:
        assert payload[flag] is False


def test_cli_rejects_unsafe_input_path() -> None:
    code, payload = run_script(["--input-json", ".env"])

    assert code == 2
    assert payload["script_status"] == "FUNDING_READINESS_TRANSFER_GATE_INPUT_BLOCKED"
    assert "unsafe_input_json_path_rejected" in payload["blockers"]
    for flag in ALWAYS_FALSE_FLAGS:
        assert payload[flag] is False
