from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_practice_closed_trade_receipt_intake_v1 import (  # noqa: E402
    intake_receipt,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and optionally append one owner-reviewed, sanitized, closed OANDA "
            "practice trade receipt. This command never calls the broker or places an order."
        )
    )
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--receipt-json", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--i-confirm-receipt-reviewed", action="store_true")
    parser.add_argument("--i-confirm-demo-practice-only", action="store_true")
    parser.add_argument("--i-confirm-closed-trade-only", action="store_true")
    parser.add_argument("--i-confirm-no-credentials-or-account-id", action="store_true")
    parser.add_argument("--i-confirm-no-raw-broker-payload", action="store_true")
    parser.add_argument("--i-confirm-no-order-created-by-intake", action="store_true")
    parser.add_argument("--i-confirm-append-only", action="store_true")
    return parser


def _load_receipt(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("receipt_json_root_must_be_object")
    return value


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    receipt_path = Path(args.receipt_json).expanduser().resolve()
    if not receipt_path.exists() or not receipt_path.is_file():
        print(
            json.dumps(
                {
                    "schema": "aios.forex.oanda_practice_receipt_intake_cli_error.v1",
                    "status": "BLOCKED_RECEIPT_FILE_MISSING",
                    "blockers": ["receipt_json_file_missing"],
                },
                sort_keys=True,
            )
        )
        return 2

    try:
        receipt = _load_receipt(receipt_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "schema": "aios.forex.oanda_practice_receipt_intake_cli_error.v1",
                    "status": "BLOCKED_RECEIPT_FILE_INVALID",
                    "blockers": [f"receipt_json_invalid:{type(exc).__name__}"],
                },
                sort_keys=True,
            )
        )
        return 2

    confirmations = {
        "owner_confirmed_receipt_reviewed": args.i_confirm_receipt_reviewed,
        "owner_confirmed_demo_practice_only": args.i_confirm_demo_practice_only,
        "owner_confirmed_closed_trade_only": args.i_confirm_closed_trade_only,
        "owner_confirmed_no_credentials_or_account_id": args.i_confirm_no_credentials_or_account_id,
        "owner_confirmed_no_raw_broker_payload": args.i_confirm_no_raw_broker_payload,
        "owner_confirmed_no_order_created_by_intake": args.i_confirm_no_order_created_by_intake,
        "owner_confirmed_append_only": args.i_confirm_append_only,
    }

    result = intake_receipt(
        Path(args.repo_root).expanduser().resolve(),
        receipt,
        confirmations=confirmations,
        apply=args.apply,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if bool(result.get("passed")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
