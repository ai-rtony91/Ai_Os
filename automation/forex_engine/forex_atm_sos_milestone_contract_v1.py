from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "aios.forex.atm_milestone_contract.v1"
CONFIG_RELATIVE_PATH = Path("control/forex/atm_milestone_config.json")
COUNTDOWN_REPORT_RELATIVE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_ATM_COUNTDOWN_ACTIVATION_V1_REPORT.md")
REPORT_RELATIVE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_ATM_SOS_CONTRACT_V1_REPORT.md")
MESSAGE_RELATIVE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_ATM_OWNER_SOS_MESSAGE.example.txt")
NOTIFIER_RELATIVE_PATH = Path("automation/orchestration/aios_sos_local_notifier.py")
ACTION_OWNER_REVIEW_PROFIT_SWEEP = "OWNER_REVIEW_PROFIT_SWEEP"
SOS_CONTRACT_READY_FOR_FLOW2 = "SOS_CONTRACT_READY_FOR_FLOW2"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path}_not_object")
    return parsed


def _load_module(repo_root: Path, relative_path: Path, module_name: str):
    module_path = repo_root / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{module_name}_unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _extract_json_block(text: str) -> dict[str, Any]:
    if "```json" not in text:
        return {}
    body = text.split("```json", 1)[1].split("```", 1)[0].strip()
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _load_countdown_receipt(repo_root: Path) -> dict[str, Any]:
    path = repo_root / COUNTDOWN_REPORT_RELATIVE_PATH
    if not path.exists():
        return {}
    return _extract_json_block(path.read_text(encoding="utf-8"))


def render_owner_message(*, profit_bucket: float, min_profit: float, baseline: float) -> str:
    return (
        "[AIOS SOS - ATM MILESTONE REACHED]  #AIOS_SOS\n"
        f"Your demo profit bucket tipped: ${profit_bucket:.2f} (threshold ${min_profit:.2f}).\n"
        f"Target band 100-120% reached on baseline ${baseline:.2f}.\n"
        "NOTHING HAS MOVED. This is an instruction, not an action.\n\n"
        "WHAT TO DO NEXT - reply with ONE:\n"
        "  APPROVE  -> AIOS logs an owner-reviewed withdrawal proposal (still no money moves;\n"
        "              it queues a proposal you action by hand at your broker/bank).\n"
        "  HOLD     -> keep compounding in-account; bucket keeps filling.\n"
        "  ADJUST   -> reply ADJUST <number> to set a new tip threshold in USD.\n\n"
        "Nothing further happens until you reply. Money movement stays OFF by policy.\n"
    )


def build_sos_contract_receipt(
    repo_root: Path,
    *,
    profit_bucket_usd: float = 0.0,
    capital_action: str = "NO_TRANSFER",
    owner_ack: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    config = _load_json(repo_root / CONFIG_RELATIVE_PATH)
    if _as_bool(config.get("money_movement_allowed")) or _as_bool(config.get("bank_access_allowed")):
        return {
            "schema": SCHEMA,
            "contract_status": "BLOCKED",
            "blocked_reason": "money_or_bank_flag_enabled",
            "mode": "APPLY" if apply else "DRY_RUN",
            "tip_detected": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "written": False,
            "generated_at": _utc_now(),
        }

    baseline = _as_float(config.get("baseline_equity_usd"), 1000.0)
    min_profit = _as_float(config.get("min_profit_to_sweep_usd"), 200.0)
    countdown = _load_countdown_receipt(repo_root)
    countdown_status = str(countdown.get("countdown_status_after", "COUNTDOWN_ACTIVE"))
    countdown_active = countdown_status != "BASELINE_EQUITY_REQUIRED"
    tip_detected = (
        capital_action == ACTION_OWNER_REVIEW_PROFIT_SWEEP
        and profit_bucket_usd >= min_profit
        and countdown_active
    )
    owner_message = render_owner_message(profit_bucket=profit_bucket_usd, min_profit=min_profit, baseline=baseline)
    notifier_plan: dict[str, Any] = {}
    sos_routed = False
    if tip_detected and owner_ack:
        notifier = _load_module(repo_root, NOTIFIER_RELATIVE_PATH, "aios_sos_local_notifier")
        notifier_plan = notifier.build_sos_local_notifier_plan(
            sos_policy={
                "sos_required": True,
                "severity": "critical",
                "next_safe_action": "Owner reviews APPROVE, HOLD, or ADJUST instruction. No money moves.",
            },
            stop_report={},
            core_status={},
            notifier_options={},
        )
        sos_routed = bool(notifier_plan.get("notifier_status") == "alert_ready")

    contract = {
        "schema": SCHEMA,
        "milestone": "ATM_MILESTONE",
        "tip_detected": tip_detected,
        "profit_bucket_usd": round(profit_bucket_usd, 2),
        "min_profit_to_sweep_usd": round(min_profit, 2),
        "target_band": "100_TO_120_PERCENT",
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
        "sos_alert_integration_status": SOS_CONTRACT_READY_FOR_FLOW2,
        "owner_next_step": owner_message,
        "generated_at": _utc_now(),
    }
    receipt = {
        "schema": SCHEMA,
        "contract_status": "SOS_CONTRACT_READY_FOR_FLOW2",
        "mode": "APPLY" if apply else "DRY_RUN",
        "tip_detected": tip_detected,
        "owner_ack_present": owner_ack,
        "sos_routed_file_first": sos_routed,
        "sos_sent": False,
        "contract": contract,
        "notifier_plan": notifier_plan,
        "message_rendered": True,
        "message_written": False,
        "report_written": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
        "followups": ["F2"],
        "followup_notes": ["F2: S3 may need a separate owned packet to honor this contract directly."],
    }
    if apply:
        report_path = repo_root / REPORT_RELATIVE_PATH
        message_path = repo_root / MESSAGE_RELATIVE_PATH
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(_render_report(receipt), encoding="utf-8")
        message_path.write_text(owner_message, encoding="utf-8")
        receipt["message_written"] = True
        receipt["report_written"] = True
    return receipt


def _render_report(receipt: dict[str, Any]) -> str:
    return (
        "# AIOS Forex ATM SOS Contract V1 Report\n\n"
        "Packet: AIOS-P26B\n\n"
        "This contract is instruction-only. No money moved and no broker, bank, live, credential, order, or webhook path was used.\n\n"
        "```json\n"
        f"{json.dumps(receipt, indent=2, sort_keys=True)}\n"
        "```\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build demo-only ATM milestone SOS contract.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--profit-bucket-usd", type=float, default=0.0)
    parser.add_argument("--capital-action", default="NO_TRANSFER")
    parser.add_argument("--owner-ack", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    receipt = build_sos_contract_receipt(
        Path(args.repo_root).resolve(),
        profit_bucket_usd=args.profit_bucket_usd,
        capital_action=args.capital_action,
        owner_ack=args.owner_ack,
        apply=args.apply,
    )
    print(json.dumps(receipt, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
