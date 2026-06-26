from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal

from automation.forex_engine import oanda_demo_read_only_pl_result_intake_v1 as m


PROTECTED_FLAGS = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)


def _json(evidence=None):
    result = m.intake_oanda_demo_read_only_pl_result(
        evidence or m.build_sample_profit_pl_evidence()
    )
    return m.oanda_demo_read_only_pl_result_intake_to_jsonable_dict(result)


def _sample(**changes):
    return replace(m.build_sample_profit_pl_evidence(), **changes)


def test_profit_intake_accepted():
    data = _json(m.build_sample_profit_pl_evidence())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT"
    assert data["safe_to_route"] is True


def test_loss_intake_accepted():
    data = _json(m.build_sample_loss_pl_evidence())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS"
    assert data["safe_to_route"] is True


def test_breakeven_intake_accepted():
    data = _json(m.build_sample_breakeven_pl_evidence())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN"
    assert data["safe_to_route"] is True


def test_incomplete_intake_blocked():
    data = _json(m.build_sample_incomplete_pl_evidence())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE"
    assert data["safe_to_route"] is False


def test_unsafe_intake_blocked():
    data = _json(m.build_sample_unsafe_pl_evidence())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert data["safe_to_route"] is False


def test_not_sanitized_blocked():
    data = _json(_sample(sanitized=False))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_NOT_SANITIZED"


def test_missing_reconciliation_blocked():
    data = _json(_sample(broker_reconciled=False))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_MISSING_RECONCILIATION"


def test_wrong_broker_blocked():
    data = _json(_sample(**{"broker": "OTHER_DEMO"}))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert "broker_must_be_oanda_demo" in data["blockers"]


def test_wrong_environment_blocked():
    data = _json(_sample(environment="PRACTICE"))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert "environment_must_be_demo" in data["blockers"]


def test_read_only_false_blocked():
    data = _json(_sample(read_only_capture=False))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert "read_only_capture_required" in data["blockers"]


def test_raw_payload_present_blocked():
    data = _json(_sample(raw_payload_included=True))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert "raw_payload_included" in data["blockers"]


def test_account_id_present_blocked():
    data = _json(_sample(account_id_included=True))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert "account_id_included" in data["blockers"]


def test_credential_present_blocked():
    data = _json(_sample(credential_included=True))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert "credential_included" in data["blockers"]


def test_broker_order_id_present_blocked():
    data = _json(_sample(broker_order_id_included=True))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert "broker_order_id_included" in data["blockers"]


def test_private_account_data_present_blocked():
    data = _json(_sample(private_account_data_included=True))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    assert "private_account_data_included" in data["blockers"]


def test_result_bucket_profit():
    assert _json(m.build_sample_profit_pl_evidence())["result_bucket"] == "PROFIT"


def test_result_bucket_loss():
    assert _json(m.build_sample_loss_pl_evidence())["result_bucket"] == "LOSS"


def test_result_bucket_breakeven():
    assert _json(m.build_sample_breakeven_pl_evidence())["result_bucket"] == "BREAKEVEN"


def test_realized_r_multiple_calculated():
    assert _json()["realized_r_multiple"] == "0.6000"


def test_planned_vs_actual_includes_units_match():
    assert _json()["planned_vs_actual"]["units_match"] is True


def test_planned_vs_actual_includes_entry_slippage():
    assert _json()["planned_vs_actual"]["entry_slippage"] == "0.00010"


def test_intake_json_serializable():
    json.dumps(_json(), sort_keys=True)


def test_intake_markdown_title():
    result = m.intake_oanda_demo_read_only_pl_result(m.build_sample_profit_pl_evidence())
    assert m.oanda_demo_read_only_pl_result_intake_to_markdown(result).startswith(
        "# AIOS Forex OANDA Demo Read Only P/L Result Intake V1"
    )


def test_intake_operator_text_plain():
    result = m.intake_oanda_demo_read_only_pl_result(m.build_sample_profit_pl_evidence())
    text = m.oanda_demo_read_only_pl_result_intake_to_operator_text(result)
    assert "Read-only P/L intake status:" in text
    assert "No broker call made by this packet." in text


def test_intake_permissions_false():
    data = _json()
    assert all(data[flag] is False for flag in PROTECTED_FLAGS)
    assert all(data["permissions"][flag] is False for flag in PROTECTED_FLAGS)


def test_owner_warning_present():
    assert _json()["owner_warning"] == "Do not execute unless Anthony explicitly approves."


def test_read_only_warning_present():
    assert _json()["read_only_warning"] == (
        "Read-only P/L evidence intake only. Codex is not authorized to execute, "
        "call a broker, access credentials, or place orders."
    )


def test_planned_risk_cannot_be_zero():
    data = _json(_sample(planned_risk=Decimal("0")))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE"
    assert "planned_risk_must_be_positive" in data["blockers"]


def test_realized_pl_required_for_accepted_result():
    data = _json(_sample(realized_pl=None))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE"
    assert data["result_bucket"] == "INCOMPLETE"


def test_result_string_normalized_from_pl():
    data = _json(_sample(result="WRONG_TEXT_BUT_PL_POSITIVE"))
    assert data["result_bucket"] == "PROFIT"
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT"


def test_direction_preserved():
    assert _json()["sanitized_evidence"]["direction"] == "BUY"


def test_instrument_preserved():
    assert _json()["sanitized_evidence"]["instrument"] == "EUR_USD"


def test_candidate_id_preserved():
    assert _json()["sanitized_evidence"]["candidate_id"] == "candidate_oanda_demo_pl_001"


def test_strategy_id_preserved():
    assert _json()["sanitized_evidence"]["strategy_id"] == "strategy_supertrend_review_ready_v1"


def test_no_raw_account_data_appears_in_json():
    payload = json.dumps(_json(), sort_keys=True)
    assert "RAW_ACCOUNT" not in payload
    assert "private account value" not in payload.lower()


def test_no_raw_credential_data_appears_in_json():
    payload = json.dumps(_json(), sort_keys=True)
    assert "RAW_CREDENTIAL" not in payload
    assert "sk-" not in payload


def test_no_raw_broker_order_id_appears_in_json():
    payload = json.dumps(_json(), sort_keys=True)
    assert "RAW_BROKER_ORDER" not in payload


def test_no_live_endpoint_text_appears_in_output():
    assert "live endpoint" not in json.dumps(_json(), sort_keys=True).lower()


def test_profit_output_deterministic():
    assert _json(m.build_sample_profit_pl_evidence()) == _json(m.build_sample_profit_pl_evidence())


def test_loss_output_deterministic():
    assert _json(m.build_sample_loss_pl_evidence()) == _json(m.build_sample_loss_pl_evidence())


def test_unsafe_output_deterministic():
    assert _json(m.build_sample_unsafe_pl_evidence()) == _json(m.build_sample_unsafe_pl_evidence())


def test_actual_units_cannot_be_zero():
    data = _json(_sample(actual_units=0))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE"
    assert "actual_units_must_be_positive" in data["blockers"]


def test_timestamps_required():
    data = _json(_sample(open_time="", close_time=""))
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE"
    assert "timestamps_required" in data["blockers"]
