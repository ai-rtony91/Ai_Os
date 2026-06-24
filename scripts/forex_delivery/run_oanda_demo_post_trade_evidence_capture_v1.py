from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_post_trade_evidence_capture_v1 import (  # noqa: E402
    evaluate_oanda_demo_post_trade_evidence_capture_v1,
)


REQUIRED_CAPTURE_CONFIRMATIONS = {
    "i_confirm_post_trade_evidence_reviewed": (
        "--i-confirm-post-trade-evidence-reviewed"
    ),
    "i_confirm_no_second_order": "--i-confirm-no-second-order",
    "i_confirm_no_credentials_in_evidence": (
        "--i-confirm-no-credentials-in-evidence"
    ),
    "i_confirm_no_account_ids_in_evidence": (
        "--i-confirm-no-account-ids-in-evidence"
    ),
    "i_confirm_stop_loss_checked": "--i-confirm-stop-loss-checked",
    "i_confirm_take_profit_checked": "--i-confirm-take-profit-checked",
    "i_confirm_pl_recorded": "--i-confirm-pl-recorded",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.print_template:
        _print_json(
            {
                "script_status": "POST_TRADE_EVIDENCE_TEMPLATE_ONLY",
                "broker_network_call_performed": False,
                "order_placement_performed": False,
                "credential_read_performed": False,
                "account_id_read_performed": False,
                "template": _sanitized_evidence_template(),
            }
        )
        return 0

    if args.capture_evidence:
        missing_confirmations = [
            flag
            for attr, flag in REQUIRED_CAPTURE_CONFIRMATIONS.items()
            if not getattr(args, attr)
        ]
        if missing_confirmations:
            _print_json(
                {
                    "script_status": "BLOCKED_MISSING_EVIDENCE_CONFIRMATIONS",
                    "missing_confirmations": missing_confirmations,
                    "broker_network_call_performed": False,
                    "order_placement_performed": False,
                    "credential_read_performed": False,
                    "account_id_read_performed": False,
                }
            )
            return 1

    decision = evaluate_oanda_demo_post_trade_evidence_capture_v1(
        owner_command_result=_ready_owner_command_result(),
        broker_call_result=_dry_run_broker_call_result(),
        post_trade_evidence=_dry_run_post_trade_evidence(),
        owner_evidence_confirmation=_owner_confirmation_from_flags(),
    )
    _print_json(
        {
            "script_status": decision["status"]
            if args.capture_evidence
            else "POST_TRADE_EVIDENCE_DRY_RUN_PACKAGE",
            "dry_run": args.capture_evidence is False,
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "decision": decision,
        }
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIOS OANDA demo post-trade evidence capture safety shell."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print JSON evidence package only. This is the default behavior.",
    )
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="Print the sanitized post-trade evidence template.",
    )
    parser.add_argument(
        "--capture-evidence",
        action="store_true",
        help="Capture example dry-run evidence only after all confirmations.",
    )
    parser.add_argument("--i-confirm-post-trade-evidence-reviewed", action="store_true")
    parser.add_argument("--i-confirm-no-second-order", action="store_true")
    parser.add_argument("--i-confirm-no-credentials-in-evidence", action="store_true")
    parser.add_argument("--i-confirm-no-account-ids-in-evidence", action="store_true")
    parser.add_argument("--i-confirm-stop-loss-checked", action="store_true")
    parser.add_argument("--i-confirm-take-profit-checked", action="store_true")
    parser.add_argument("--i-confirm-pl-recorded", action="store_true")
    return parser


def _sanitized_evidence_template() -> dict:
    return {
        "evidence_mode": "DRY_RUN_REHEARSAL | ORDER_REJECTED | ORDER_SUBMITTED | ORDER_FILLED | ORDER_CLOSED",
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "order_attempted": "boolean",
        "order_id_or_sanitized_reference": "sanitized reference only, no account ID",
        "filled_or_rejected": "FILLED | REJECTED | SUBMITTED | PENDING | CLOSED | DRY_RUN",
        "fill_price_or_rejection_reason": "sanitized price or reason",
        "stop_loss_attached": "boolean",
        "take_profit_attached": "boolean",
        "realized_pl_when_closed": "number or null",
        "unrealized_pl_snapshot": "number or null",
        "close_reason": "required when ORDER_CLOSED",
        "post_balance": "number or null",
        "post_nav": "number or null",
        "timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ",
        "one_order_only": True,
        "max_order_attempts": 1,
        "no_second_order": True,
        "hold_allowed_overnight": "boolean",
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
    }


def _ready_owner_command_result() -> dict:
    return {
        "status": "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND",
        "execution_authority": _execution_authority_false(),
    }


def _dry_run_broker_call_result() -> dict:
    return {
        "status": "BROKER_CALL_DRY_RUN_READY",
        "order_attempt_count": 0,
        "live_order_allowed": False,
        "autonomous_order_allowed": False,
        "execution_authority": _execution_authority_false(),
    }


def _dry_run_post_trade_evidence() -> dict:
    return {
        "evidence_mode": "DRY_RUN_REHEARSAL",
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "order_attempted": False,
        "order_id_or_sanitized_reference": "",
        "filled_or_rejected": "DRY_RUN",
        "fill_price_or_rejection_reason": "dry_run_rehearsal_no_broker_call",
        "stop_loss_attached": False,
        "take_profit_attached": False,
        "realized_pl_when_closed": None,
        "unrealized_pl_snapshot": None,
        "close_reason": None,
        "post_balance": None,
        "post_nav": None,
        "timestamp_utc": "DRY_RUN_TIMESTAMP_UTC",
        "one_order_only": True,
        "max_order_attempts": 1,
        "no_second_order": True,
        "hold_allowed_overnight": False,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
    }


def _owner_confirmation_from_flags() -> dict:
    return {
        "owner_confirmed_post_trade_evidence_reviewed": True,
        "owner_confirmed_no_second_order": True,
        "owner_confirmed_no_credentials_in_evidence": True,
        "owner_confirmed_no_account_ids_in_evidence": True,
        "owner_confirmed_stop_loss_checked": True,
        "owner_confirmed_take_profit_checked": True,
        "owner_confirmed_pl_recorded": True,
    }


def _execution_authority_false() -> dict:
    return {
        "execution_allowed": False,
        "demo_order_allowed": False,
        "live_order_allowed": False,
        "broker_write_allowed": False,
        "autonomous_order_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
    }


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
