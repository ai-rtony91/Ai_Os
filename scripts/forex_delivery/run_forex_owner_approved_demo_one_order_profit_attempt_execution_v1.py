from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_owner_approved_demo_one_order_profit_attempt_execution_v1 import (  # noqa: E402
    PACKET_ID,
    evaluate_forex_owner_approved_demo_one_order_profit_attempt_execution_v1,
)


def safe_sample_payload() -> dict:
    return {
        "owner_approval": {
            "approval_text_present": True,
            "approval_packet_id": PACKET_ID,
            "owner_name": "Anthony",
            "approval_scope_demo_only": True,
            "approval_scope_one_order_only": True,
            "approval_scope_no_live_trade": True,
            "approval_scope_no_money_movement": True,
            "approval_scope_no_banking_transfer": True,
        },
        "protected_demo_attempt_result": {
            "protected_demo_attempt_status": "READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET",
            "protected_demo_attempt_ready": True,
            "actual_demo_execution_authorized": False,
            "actual_live_execution_authorized": False,
            "broker_api_called": False,
            "credential_read": False,
            "money_moved": False,
        },
        "runtime_boundary": {
            "runtime_credential_session_available": True,
            "credential_values_in_payload": False,
            "account_id_in_payload": False,
            "credential_session_scope": "ONE_ORDER_DEMO_ONLY",
            "session_unexpired": True,
            "no_stored_api_key": True,
            "no_stored_account_id": True,
            "no_raw_secret_logging": True,
            "redaction_required": True,
        },
        "existing_runtime_interface": {
            "repo_runtime_interface_identified": True,
            "interface_name": "oanda_demo_owner_approved_one_order_protected_runtime_execution_v1",
            "interface_is_demo_only": True,
            "interface_supports_one_order": True,
            "interface_does_not_store_credentials": True,
            "interface_does_not_allow_live_trade": True,
        },
        "order_candidate": {
            "instrument": "EUR_USD",
            "side": "buy",
            "order_type": "market",
            "units": 1000,
            "stop_loss_present": True,
            "take_profit_present": True,
            "stop_loss_value_or_distance_present": True,
            "take_profit_value_or_distance_present": True,
            "setup_id": "setup-001",
            "evidence_id": "evidence-001",
            "duplicate_candidate": False,
        },
        "risk_plan": {
            "max_risk_per_trade_pct": "0.01",
            "max_daily_loss_pct": "0.03",
            "one_order_only": True,
            "max_order_count_this_packet": 1,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "next_order_blocked_until_review": True,
        },
        "oanda_demo_boundary": {
            "broker_name": "OANDA",
            "mode": "OANDA_DEMO",
            "live_trading_allowed": False,
            "real_money_allowed": False,
            "money_movement_allowed": False,
            "account_id_in_payload": False,
        },
        "post_trade_review": {
            "post_trade_review_required": True,
            "daily_pnl_record_required": True,
            "sanitized_receipt_required": True,
            "owner_review_required": True,
            "no_second_trade_without_review": True,
        },
    }


def main() -> int:
    result = evaluate_forex_owner_approved_demo_one_order_profit_attempt_execution_v1(
        safe_sample_payload()
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
