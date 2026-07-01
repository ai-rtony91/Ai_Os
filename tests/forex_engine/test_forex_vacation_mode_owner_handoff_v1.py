from automation.forex_engine.forex_vacation_mode_entry_authority_gate_v1 import (
    ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW,
)
from automation.forex_engine.forex_vacation_mode_exit_authority_gate_v1 import (
    EXIT_AUTHORITY_HOLD_ALLOWED,
)
from automation.forex_engine.forex_vacation_mode_owner_handoff_v1 import (
    INCOMPLETE_INPUTS,
    OWNER_HANDOFF_BLOCKED_BY_ALERTING,
    OWNER_HANDOFF_READY,
    evaluate_forex_vacation_mode_owner_handoff_v1,
)
from automation.forex_engine.forex_vacation_mode_position_supervisor_v1 import (
    POSITION_SUPERVISION_HOLD,
)
from automation.forex_engine.forex_vacation_mode_release_candidate_scorecard_v1 import (
    SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW,
)


def _handoff_payload(**overrides):
    payload = {
        "entry_result": {"status": ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW, "ready": True},
        "supervisor_result": {"status": POSITION_SUPERVISION_HOLD, "ready": True},
        "exit_result": {"status": EXIT_AUTHORITY_HOLD_ALLOWED, "ready": True},
        "scorecard_result": {
            "status": SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW,
            "ready": True,
        },
        "owner_alert_state": {"alerting_safe": True, "owner_visible": True},
        "safety_policy": {
            "metadata_only": True,
            "no_live_execution": True,
            "no_profit_guarantee": True,
            "legal_compliance_not_complete": True,
            "not_play_store_ready": True,
            "not_sell_ready": True,
        },
    }
    for section, values in overrides.items():
        payload[section].update(values)
    return payload


def test_incomplete_input_blocks():
    result = evaluate_forex_vacation_mode_owner_handoff_v1()

    assert result["status"] == INCOMPLETE_INPUTS


def test_owner_handoff_is_visible_and_states_no_live_execution():
    result = evaluate_forex_vacation_mode_owner_handoff_v1(_handoff_payload())

    assert result["status"] == OWNER_HANDOFF_READY
    assert "No live execution occurred" in result["no_live_execution_statement"]
    assert result["profit_guaranteed"] is False


def test_owner_handoff_blocks_on_unsafe_alert_state():
    result = evaluate_forex_vacation_mode_owner_handoff_v1(
        _handoff_payload(owner_alert_state={"alerting_safe": False})
    )

    assert result["status"] == OWNER_HANDOFF_BLOCKED_BY_ALERTING
