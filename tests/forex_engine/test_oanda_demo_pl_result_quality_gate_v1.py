from __future__ import annotations

import json
from decimal import Decimal

from automation.forex_engine import oanda_demo_pl_result_quality_gate_v1 as q
from automation.forex_engine import oanda_demo_read_only_pl_result_intake_v1 as i


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


def _json(input_obj=None):
    result = q.evaluate_oanda_demo_pl_result_quality(
        input_obj or q.build_sample_profit_quality_input()
    )
    return q.oanda_demo_pl_result_quality_to_jsonable_dict(result)


def _intake_json(evidence):
    return i.oanda_demo_read_only_pl_result_intake_to_jsonable_dict(
        i.intake_oanda_demo_read_only_pl_result(evidence)
    )


def test_quality_proof_ready_for_strong_profit():
    data = _json(q.build_sample_profit_quality_input())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY"
    assert data["proof_routing_allowed"] is True


def test_quality_review_ready_for_loss():
    data = _json(q.build_sample_loss_quality_input())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY"
    assert data["quality_review_allowed"] is True


def test_quality_review_ready_for_breakeven():
    data = _json(q.build_sample_breakeven_quality_input())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY"
    assert data["quality_review_allowed"] is True


def test_quality_blocked_incomplete():
    data = _json(q.build_sample_incomplete_quality_input())
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE"
    assert data["quality_review_allowed"] is False


def test_quality_blocked_unsafe():
    unsafe_intake = _intake_json(i.build_sample_unsafe_pl_evidence())
    data = _json({"intake_result": unsafe_intake})
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_UNSAFE"


def test_quality_low_signal_handling_review_by_default():
    low_signal = _intake_json(
        i.OandaDemoReadOnlyPlEvidence(
            **{
                **i.build_sample_profit_pl_evidence().__dict__,
                "realized_pl": Decimal("0.10"),
            }
        )
    )
    data = _json({"intake_result": low_signal})
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY"
    assert data["proof_routing_allowed"] is False


def test_quality_low_signal_handling_strict_blocked():
    low_signal = _intake_json(
        i.OandaDemoReadOnlyPlEvidence(
            **{
                **i.build_sample_profit_pl_evidence().__dict__,
                "realized_pl": Decimal("0.10"),
            }
        )
    )
    data = _json(
        {"intake_result": low_signal, "strict_low_signal_blocks_profit": True}
    )
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL"


def test_quality_r_multiple_propagated():
    assert _json(q.build_sample_profit_quality_input())["realized_r_multiple"] == "0.6000"


def test_quality_json_serializable():
    json.dumps(_json(), sort_keys=True)


def test_quality_markdown_title():
    result = q.evaluate_oanda_demo_pl_result_quality(q.build_sample_profit_quality_input())
    assert q.oanda_demo_pl_result_quality_to_markdown(result).startswith(
        "# AIOS Forex OANDA Demo P/L Result Quality Gate V1"
    )


def test_quality_operator_text_plain():
    result = q.evaluate_oanda_demo_pl_result_quality(q.build_sample_profit_quality_input())
    text = q.oanda_demo_pl_result_quality_to_operator_text(result)
    assert "P/L quality status:" in text
    assert "No trade placed by this packet." in text


def test_quality_permissions_false():
    data = _json()
    assert all(data[flag] is False for flag in PROTECTED_FLAGS)
    assert all(data["permissions"][flag] is False for flag in PROTECTED_FLAGS)


def test_quality_requires_reconciliation_when_configured():
    intake = _intake_json(
        i.OandaDemoReadOnlyPlEvidence(
            **{
                **i.build_sample_profit_pl_evidence().__dict__,
                "broker_reconciled": False,
            }
        )
    )
    data = _json({"intake_result": intake, "require_reconciliation": True})
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE"


def test_quality_requires_sanitized_when_configured():
    intake = _intake_json(
        i.OandaDemoReadOnlyPlEvidence(
            **{
                **i.build_sample_profit_pl_evidence().__dict__,
                "sanitized": False,
            }
        )
    )
    data = _json({"intake_result": intake, "require_sanitized": True})
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_UNSAFE"


def test_quality_profit_threshold_exactly_met():
    intake = _intake_json(
        i.OandaDemoReadOnlyPlEvidence(
            **{
                **i.build_sample_profit_pl_evidence().__dict__,
                "realized_pl": Decimal("0.50"),
            }
        )
    )
    data = _json({"intake_result": intake, "min_abs_r_for_proof_ready": Decimal("0.25")})
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY"


def test_quality_review_allowed_false_for_blocked_low_signal():
    intake = _intake_json(
        i.OandaDemoReadOnlyPlEvidence(
            **{
                **i.build_sample_profit_pl_evidence().__dict__,
                "realized_pl": Decimal("0.10"),
            }
        )
    )
    data = _json({"intake_result": intake, "strict_low_signal_blocks_profit": True})
    assert data["quality_review_allowed"] is False


def test_quality_review_allowed_for_loss_when_configured():
    loss_intake = _intake_json(i.build_sample_loss_pl_evidence())
    data = _json({"intake_result": loss_intake, "allow_loss_for_review": True})
    assert data["quality_review_allowed"] is True


def test_quality_review_blocked_for_loss_when_not_configured():
    loss_intake = _intake_json(i.build_sample_loss_pl_evidence())
    data = _json({"intake_result": loss_intake, "allow_loss_for_review": False})
    assert data["classification"] == "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL"


def test_quality_notes_explain_repeated_sample_gap():
    data = _json(q.build_sample_profit_quality_input())
    assert any("one result" in note.lower() for note in data["quality_notes"])


def test_quality_blockers_empty_for_proof_ready():
    assert _json(q.build_sample_profit_quality_input())["blockers"] == []


def test_quality_blockers_present_for_incomplete():
    assert _json(q.build_sample_incomplete_quality_input())["blockers"]


def test_quality_result_bucket_profit():
    assert _json(q.build_sample_profit_quality_input())["result_bucket"] == "PROFIT"


def test_quality_result_bucket_loss():
    assert _json(q.build_sample_loss_quality_input())["result_bucket"] == "LOSS"


def test_quality_result_bucket_breakeven():
    assert _json(q.build_sample_breakeven_quality_input())["result_bucket"] == "BREAKEVEN"


def test_quality_realized_pl_propagated():
    assert _json(q.build_sample_loss_quality_input())["realized_pl"] == "-0.80"


def test_quality_next_safe_action_for_proof_ready():
    assert "Route" in _json(q.build_sample_profit_quality_input())["next_safe_action"]


def test_quality_next_safe_action_for_review_ready():
    assert "review" in _json(q.build_sample_loss_quality_input())["next_safe_action"].lower()


def test_quality_next_safe_action_for_blocked():
    assert "Repair" in _json(q.build_sample_incomplete_quality_input())["next_safe_action"]


def test_quality_version_constant_present():
    assert q.VERSION == "oanda_demo_pl_result_quality_gate_v1"
    assert q.OANDA_DEMO_PL_RESULT_QUALITY_GATE_VERSION == q.VERSION
