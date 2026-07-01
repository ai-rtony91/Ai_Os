from automation.forex_engine.forex_basket_risk_exposure_governor_v1 import (
    BASKET_RISK_EXPOSURE_READY,
)
from automation.forex_engine.forex_governed_burst_permission_engine_v1 import (
    BLOCKED_BY_REVIEW_LOCK,
    READY_FOR_DEMO_BURST_RUNTIME_INTENT,
    READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW,
    READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT,
    evaluate_forex_governed_burst_permission_engine_v1,
)


def _basket_result():
    return {
        "status": BASKET_RISK_EXPOSURE_READY,
        "ready": True,
        "approved_basket": [
            {
                "pair": "EUR_USD",
                "side": "BUY",
                "order_type": "MARKET",
                "units": 1000,
                "setup_id": "SETUP-EUR",
                "evidence_id": "EVIDENCE-EUR",
                "risk_pct": 0.005,
            }
        ],
        "total_burst_risk_pct": 0.005,
    }


def _payload(mode="DEMO_BURST", **permission_overrides):
    permission = {
        "mode": mode,
        "owner_review_required": True,
        "owner_live_approval_required_for_live": True,
        "runtime_credentials_required_for_execution": True,
        "proof_required_for_live": True,
        "previous_burst_review_complete": True,
        "receipt_required": True,
        "post_burst_review_required": True,
        "may_execute_by_this_module": False,
        "may_call_broker_by_this_module": False,
        "owner_live_approval_metadata_present": mode == "LIVE_MICRO_RUNTIME_INTENT",
    }
    permission.update(permission_overrides)
    return {
        "governed_burst_requested": True,
        "basket_risk_result": _basket_result(),
        "permission": permission,
        "proof": {
            "demo_proof_ready": True,
            "live_micro_review_ready": True,
            "repeatability_score": 82,
        },
        "runtime_boundary": {
            "runtime_session_available": True,
            "credential_values_in_payload": False,
            "account_id_in_payload": False,
            "no_stored_credentials": True,
        },
    }


def test_missing_previous_burst_review_blocks():
    result = evaluate_forex_governed_burst_permission_engine_v1(
        _payload(previous_burst_review_complete=False)
    )
    assert result["status"] == BLOCKED_BY_REVIEW_LOCK


def test_demo_burst_intent_ready():
    result = evaluate_forex_governed_burst_permission_engine_v1(
        _payload("DEMO_BURST")
    )
    assert result["status"] == READY_FOR_DEMO_BURST_RUNTIME_INTENT
    assert result["governed_burst_intent"]["order_count"] == 1


def test_live_micro_review_ready_only_with_proof():
    result = evaluate_forex_governed_burst_permission_engine_v1(
        _payload("LIVE_MICRO_REVIEW")
    )
    assert result["status"] == READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW


def test_live_runtime_intent_ready_only_with_owner_runtime_boundary():
    result = evaluate_forex_governed_burst_permission_engine_v1(
        _payload("LIVE_MICRO_RUNTIME_INTENT")
    )
    assert result["status"] == READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT


def test_permission_engine_never_executes_or_calls_broker():
    result = evaluate_forex_governed_burst_permission_engine_v1(
        _payload("LIVE_MICRO_RUNTIME_INTENT")
    )
    intent = result["governed_burst_intent"]
    assert intent["execute_by_this_module"] is False
    assert intent["call_broker_by_this_module"] is False
    assert result["broker_api_called_by_this_module"] is False
