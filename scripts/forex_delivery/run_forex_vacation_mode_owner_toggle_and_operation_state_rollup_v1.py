"""Run safe sample payloads for Vacation Mode owner toggle rollup."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1 import (  # noqa: E402
    evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1,
)


def _payload(
    sample_name: str,
    command: str = "ON",
    posture: str = "ACTIVE_SUPERVISION",
    *,
    proof_ready: bool = True,
    outstanding_receipts: bool = False,
    balance_ready: bool = True,
    attention_required: bool = False,
    severity: str = "INFO",
    reason: str = "Informational state.",
    next_safe_action: str = "Continue metadata review.",
) -> dict:
    return {
        "sample_name": sample_name,
        "owner_command": {
            "command_id": f"CMD-{sample_name}",
            "requested_toggle_state": command,
            "owner_control_required": True,
            "owner_identity_confirmed": True,
            "command_timestamp_present": True,
            "command_source": "OWNER_DASHBOARD",
            "toggle_is_request_only": True,
            "toggle_does_not_authorize_execution": True,
            "toggle_does_not_authorize_withdrawal": True,
            "kill_switch_is_separate": True,
            "no_banking_requested": True,
            "no_credentials_in_command": True,
        },
        "runtime_calendar_result": {
            "status": f"RUNTIME_{posture}",
            "ready": True,
            "current_runtime_posture": posture,
            "primary_job_lane": "supervise_runtime",
            "next_best_packet": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
            "close_approaching": posture == "CLOSE_PROTECTION",
            "reopen_approaching": posture == "REOPEN_PREPARATION",
            "vacation_mode_toggle_semantics": {
                "toggle_does_not_authorize_withdrawal": True,
                "toggle_does_not_bypass_market_calendar": True,
                "toggle_does_not_bypass_kill_switch": True,
            },
            "kill_switch_semantics": {"kill_switch_is_not_vacation_mode_toggle": True},
            "runtime_product_fit_summary": {"banking_withdrawal_deferred": True},
        },
        "risk_state": {
            "kill_switch_active": command == "KILL_SWITCH_STOP",
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "max_drawdown_pct": 0.08,
            "current_drawdown_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "current_daily_loss_pct": 0.0,
            "no_new_trade_seeking_if_kill_switch": True,
            "no_new_trade_seeking_if_daily_loss_stop": True,
            "no_new_trade_seeking_if_drawdown_breach": True,
        },
        "proof_state": {
            "proof_required": True,
            "proof_ready": proof_ready,
            "fake_proof_blocked": True,
            "repeatability_review_ready": True,
            "owner_review_required_for_live": True,
        },
        "receipt_state": {
            "receipt_required_after_execution": True,
            "outstanding_receipts": outstanding_receipts,
            "post_trade_review_complete": not outstanding_receipts,
            "next_trade_blocked_until_receipts_reviewed": True,
        },
        "balance_state": {
            "balance_memory_ready": balance_ready,
            "compounding_observer_ready": balance_ready,
            "withdrawal_deferred": True,
            "bank_routing_deferred": True,
            "money_moved": False,
        },
        "runtime_boundary": {
            "runtime_session_available": True,
            "broker_session_available": True,
            "credential_values_in_payload": False,
            "account_id_in_payload": False,
            "no_stored_credentials": True,
            "broker_call_allowed_by_this_module": False,
            "execute_allowed_by_this_module": False,
        },
        "permission_policy": {
            "may_scan_metadata_when_on": True,
            "may_prepare_candidates_when_on": True,
            "may_prepare_maintenance_when_closed": True,
            "may_prepare_owner_review_when_ready": True,
            "may_execute_live_by_this_module": False,
            "may_execute_demo_by_this_module": False,
            "may_call_broker_by_this_module": False,
            "may_move_money": False,
            "may_withdraw": False,
            "may_bank_route": False,
            "owner_runtime_packet_required_for_execution": True,
        },
        "attention_policy": {
            "dashboard_summary_required": True,
            "owner_visible_reason_required": True,
            "raw_values_echoed": False,
            "sensitive_values_allowed": False,
            "alert_channel_metadata_only": True,
            "no_alert_runtime_created": True,
        },
        "owner_attention_context": {
            "owner_attention_required": attention_required,
            "severity": severity,
            "reason": reason,
            "next_safe_action": next_safe_action,
            "no_sensitive_values": True,
        },
    }


def _summary(payload: dict) -> dict:
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(payload)
    attention = result.get("owner_attention_summary", {}).get("owner_attention_state", {})
    permission = result.get("runtime_permission_summary", {}).get("permission_snapshot", {})
    return {
        "sample_name": payload["sample_name"],
        "campaign_status": result.get("campaign_status"),
        "vacation_mode_toggle_state": result.get("vacation_mode_toggle_state"),
        "vacation_mode_operation_state": result.get("vacation_mode_operation_state"),
        "owner_attention_required": attention.get("owner_attention_required"),
        "severity": attention.get("severity"),
        "next_best_packet": result.get("next_best_packet"),
        "blocked_actions_summary": permission.get("blocked_actions", ()),
    }


def main() -> None:
    samples = [
        _payload("vacation_mode_on_active_supervision"),
        _payload("vacation_mode_off_idle", command="OFF"),
        _payload("vacation_mode_paused", command="PAUSE"),
        _payload(
            "kill_switch_stop",
            command="KILL_SWITCH_STOP",
            attention_required=True,
            severity="STOP_NOW",
            reason="Kill switch active.",
            next_safe_action="Stop new trade seeking.",
        ),
        _payload("market_closed_maintenance", posture="CLOSED_MAINTENANCE"),
        _payload("close_approaching_protection", posture="CLOSE_PROTECTION"),
        _payload("reopen_preparation", posture="REOPEN_PREPARATION"),
        _payload("weekend_maintenance", posture="WEEKEND_HEAVY_MAINTENANCE"),
        _payload(
            "waiting_proof",
            proof_ready=False,
            attention_required=True,
            severity="REVIEW",
            reason="Proof missing.",
            next_safe_action="Review proof.",
        ),
        _payload(
            "waiting_receipts",
            outstanding_receipts=True,
            attention_required=True,
            severity="REVIEW",
            reason="Receipts missing.",
            next_safe_action="Review receipts.",
        ),
        _payload(
            "balance_memory_review",
            balance_ready=False,
            attention_required=True,
            severity="REVIEW",
            reason="Balance memory review required.",
            next_safe_action="Review balance memory.",
        ),
    ]
    print(json.dumps([_summary(sample) for sample in samples], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
