from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_post_execution_review_loop_v1 import (  # noqa: E402
    BLOCKED_BY_MISSING_AUDIT_RECORD,
    BLOCKED_BY_MISSING_OWNER_REVIEW,
    BLOCKED_BY_NEXT_ORDER_UNLOCKED,
    BLOCKED_BY_SENSITIVE_DATA,
    POST_EXECUTION_REVIEW_LOOP_READY,
    POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY,
    evaluate_forex_post_execution_review_loop_v1,
)
from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (  # noqa: E402
    HARD_FALSE_FIELDS,
)


def _metadata_only_payload() -> dict:
    return {
        "post_trade_review_required": True,
        "owner_review_required": True,
        "not_applicable_for_metadata_only": True,
        "audit_record_present": True,
        "secret_scan_completed": True,
        "no_raw_secret_logging": True,
        "no_raw_account_identifier_logging": True,
        "next_order_blocked_until_review": True,
    }


def _receipt_payload() -> dict:
    payload = _metadata_only_payload()
    payload["not_applicable_for_metadata_only"] = False
    payload.update(
        {
            "sanitized_execution_receipt_present": True,
            "pnl_review_recorded": True,
            "risk_review_recorded": True,
            "spread_slippage_review_recorded": True,
            "exception_review_recorded": True,
        }
    )
    return payload


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_post_execution_review_loop_v1(payload)


def test_metadata_only_not_applicable_path_passes() -> None:
    result = _run(_metadata_only_payload())
    assert result["post_execution_review_status"] == POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY


def test_sanitized_receipt_path_passes() -> None:
    result = _run(_receipt_payload())
    assert result["post_execution_review_status"] == POST_EXECUTION_REVIEW_LOOP_READY


def test_secret_scan_completed_true_is_allowed() -> None:
    result = _run(_metadata_only_payload())
    assert result["sensitive_data_detected"] is False
    assert result["post_execution_review_summary"]["secret_scan_completed"] is True
    assert result["post_execution_review_status"] == POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY


def test_missing_owner_review_blocks() -> None:
    payload = _receipt_payload()
    payload["owner_review_required"] = False
    assert _run(payload)["post_execution_review_status"] == BLOCKED_BY_MISSING_OWNER_REVIEW


def test_missing_audit_record_blocks() -> None:
    payload = _receipt_payload()
    payload["audit_record_present"] = False
    assert _run(payload)["post_execution_review_status"] == BLOCKED_BY_MISSING_AUDIT_RECORD


def test_next_order_unlocked_blocks() -> None:
    payload = _receipt_payload()
    payload["next_order_blocked_until_review"] = False
    assert _run(payload)["post_execution_review_status"] == BLOCKED_BY_NEXT_ORDER_UNLOCKED


def test_sensitive_data_blocks() -> None:
    payload = _receipt_payload()
    payload["access_token"] = "hidden-token"
    result = _run(payload)
    assert result["post_execution_review_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "hidden-token" not in repr(result)


def test_secret_looking_values_still_block() -> None:
    payload = _receipt_payload()
    payload["review_note"] = "bearer generated-secret"
    result = _run(payload)
    assert result["post_execution_review_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "generated-secret" not in repr(result)


def test_secret_scan_completed_secret_value_blocks() -> None:
    payload = _metadata_only_payload()
    payload["secret_scan_completed"] = "sk-generated-secret"
    result = _run(payload)
    assert result["post_execution_review_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-generated-secret" not in repr(result)


def test_hard_false_fields_remain_false() -> None:
    result = _run(_receipt_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
