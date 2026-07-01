from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_22h6d_supervised_operation_readiness_v1 import (  # noqa: E402
    BLOCKED_BY_SENSITIVE_DATA,
    READINESS_COMPONENTS,
    TWENTY_TWO_HOUR_SIX_DAY_READINESS_INCOMPLETE,
    TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED,
    evaluate_forex_22h6d_supervised_operation_readiness_v1,
)
from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (  # noqa: E402
    HARD_FALSE_FIELDS,
)


def _payload(value: bool = True) -> dict:
    return {component: value for component in READINESS_COMPONENTS}


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_22h6d_supervised_operation_readiness_v1(payload)


def test_incomplete_readiness_blocks() -> None:
    result = _run({"broker_session_readiness": True})
    assert result["readiness_status"] == TWENTY_TWO_HOUR_SIX_DAY_READINESS_INCOMPLETE


def test_all_ten_components_pass_with_score_100() -> None:
    result = _run(_payload())
    assert result["readiness_status"] == TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED
    assert result["total_score"] == 100
    assert result["readiness_passed"] is True


def test_one_missing_component_gives_score_90_and_incomplete() -> None:
    payload = _payload()
    payload["recovery_readiness"] = False
    result = _run(payload)
    assert result["total_score"] == 90
    assert result["readiness_status"] == TWENTY_TWO_HOUR_SIX_DAY_READINESS_INCOMPLETE


def test_owner_action_queue_identifies_missing_component() -> None:
    payload = _payload()
    payload["monitoring_readiness"] = False
    result = _run(payload)
    queue_item = [
        item
        for item in result["owner_action_queue"]
        if item["action_id"] == "REVIEW_MONITORING_READINESS"
    ][0]
    assert queue_item["blocked_by"] == ["monitoring_readiness_missing_or_false"]


def test_sensitive_data_blocks() -> None:
    payload = _payload()
    payload["broker_token"] = "hidden-token"
    result = _run(payload)
    assert result["readiness_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "hidden-token" not in repr(result)


def test_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
