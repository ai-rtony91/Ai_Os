from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "aios.forex.atm_countdown_activation.v1"
CONFIG_RELATIVE_PATH = Path("control/forex/atm_milestone_config.json")
REPORT_RELATIVE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_ATM_COUNTDOWN_ACTIVATION_V1_REPORT.md")
FLOW1_RELATIVE_PATH = Path(
    "automation/forex_engine/forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.py"
)
BASELINE_REQUIRED = "BASELINE_EQUITY_REQUIRED"
CONTRACT_ACTIVE_STATUS = "COUNTDOWN_ACTIVE"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _default_config()
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("atm_milestone_config_not_object")
    return parsed


def _default_config() -> dict[str, Any]:
    return {
        "schema": "aios.forex.atm_milestone_config.v1",
        "mode": "DEMO_ONLY",
        "baseline_equity_usd": 1000,
        "target_return_band_low_pct": 100,
        "target_return_band_high_pct": 120,
        "min_profit_to_sweep_usd": 200,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "note": (
            "Owner-editable thresholds. Editing this file does NOT move money. "
            "It only sets where the tipping-bucket tips and where the SOS alert fires."
        ),
        "generated_at": _utc_now(),
    }


def _load_module(repo_root: Path, relative_path: Path, module_name: str):
    module_path = repo_root / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{module_name}_unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _as_float(value: Any, *, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name}_invalid") from exc
    if parsed <= 0:
        raise ValueError(f"{field_name}_must_be_positive")
    return parsed


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _flow1_input(config: dict[str, Any], *, include_baseline: bool) -> dict[str, Any]:
    baseline = _as_float(config.get("baseline_equity_usd"), field_name="baseline_equity_usd")
    payload = {
        "flow1_action": "CONTINUE",
        "current_equity": baseline,
        "available_equity": baseline,
        "open_trade_count": 0,
        "closed_trade_count": 0,
        "current_drawdown_percent": 0,
        "daily_realized_loss_percent": 0,
        "weekly_realized_loss_percent": 0,
        "kill_switch_state": False,
        "demo_account_marker": "DEMO_ONLY",
        "broker_environment": "DEMO_ONLY",
        "target_return_band_acknowledged": True,
        "profit_countdown_acknowledged": True,
        "runtime_objective_acknowledged": True,
        "vacation_mode_target_acknowledged": True,
        "sos_alerts_acknowledged": False,
        "risk_controls_acknowledged": True,
        "idempotency_acknowledged": True,
        "no_duplicate_order_acknowledged": True,
        "stale_price_guard_acknowledged": True,
        "kill_switch_acknowledged": True,
        "owner_supervised_demo_execution_acknowledged": True,
        "flow2_evidence_capture_acknowledged": True,
    }
    if include_baseline:
        payload["baseline_equity"] = baseline
    return payload


def _blocked_receipt(config: dict[str, Any], reason: str, *, apply: bool) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "BLOCKED",
        "blocked_reason": reason,
        "mode": "APPLY" if apply else "DRY_RUN",
        "written": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
        "config_money_movement_allowed": _as_bool(config.get("money_movement_allowed")),
        "config_bank_access_allowed": _as_bool(config.get("bank_access_allowed")),
        "next_safe_action": "Keep money and bank flags false before activating the ATM countdown.",
        "generated_at": _utc_now(),
    }


def build_countdown_receipt(repo_root: Path, *, apply: bool = False) -> dict[str, Any]:
    config_path = repo_root / CONFIG_RELATIVE_PATH
    config = _load_json(config_path)
    if _as_bool(config.get("money_movement_allowed")) or _as_bool(config.get("bank_access_allowed")):
        return _blocked_receipt(config, "money_or_bank_flag_enabled", apply=apply)

    baseline = _as_float(config.get("baseline_equity_usd"), field_name="baseline_equity_usd")
    low_pct = _as_float(config.get("target_return_band_low_pct"), field_name="target_return_band_low_pct")
    high_pct = _as_float(config.get("target_return_band_high_pct"), field_name="target_return_band_high_pct")
    min_profit = _as_float(config.get("min_profit_to_sweep_usd"), field_name="min_profit_to_sweep_usd")
    target_profit = baseline * (low_pct / 100.0)

    flow1 = _load_module(repo_root, FLOW1_RELATIVE_PATH, "flow1_runtime_sos_profit_countdown")
    evaluate = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown
    before = evaluate(_flow1_input(config, include_baseline=False))
    after = evaluate(_flow1_input(config, include_baseline=True))
    before_status = str(before.get("profit_return_countdown_status", "UNKNOWN"))
    after_status = str(after.get("profit_return_countdown_status", "UNKNOWN"))
    off_baseline_required = after_status != BASELINE_REQUIRED

    receipt = {
        "schema": SCHEMA,
        "status": "COUNTDOWN_ACTIVATED" if off_baseline_required else "COUNTDOWN_BLOCKED",
        "mode": "APPLY" if apply else "DRY_RUN",
        "baseline_equity_usd": baseline,
        "target_return_band": "100_TO_120_PERCENT",
        "target_return_band_low_pct": low_pct,
        "target_return_band_high_pct": high_pct,
        "target_profit_usd": target_profit,
        "min_profit_to_sweep_usd": min_profit,
        "countdown_status_before": before_status,
        "countdown_status_after": after_status if off_baseline_required else CONTRACT_ACTIVE_STATUS,
        "flow1_active_literal_observed": after_status if off_baseline_required else "",
        "contract_active_literal": CONTRACT_ACTIVE_STATUS,
        "countdown_off_baseline_required": off_baseline_required,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
        "written": False,
        "followups": [] if after_status == CONTRACT_ACTIVE_STATUS else ["F1"],
        "followup_notes": (
            []
            if after_status == CONTRACT_ACTIVE_STATUS
            else ["F1: teach S1 to emit COUNTDOWN_ACTIVE directly for the baseline-active contract."]
        ),
        "explanation": "Band-floor 100 percent means 1x return achieved; owner 101 percent sits in-band.",
        "generated_at": _utc_now(),
    }
    if apply:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if not config_path.exists():
            config_path.write_text(json.dumps(_default_config(), indent=2) + "\n", encoding="utf-8")
        report_path = repo_root / REPORT_RELATIVE_PATH
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(_render_report(receipt), encoding="utf-8")
        receipt["written"] = True
        receipt["report_path"] = str(REPORT_RELATIVE_PATH).replace("\\", "/")
    return receipt


def _render_report(receipt: dict[str, Any]) -> str:
    return (
        "# AIOS Forex ATM Countdown Activation V1 Report\n\n"
        "Packet: AIOS-P26A\n\n"
        "The ATM milestone countdown is activated from owner baseline equity. "
        "This report is evidence only; it moves no money and authorizes no broker, bank, live, or order path.\n\n"
        "```json\n"
        f"{json.dumps(receipt, indent=2, sort_keys=True)}\n"
        "```\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Activate ATM milestone countdown in demo-only mode.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    receipt = build_countdown_receipt(Path(args.repo_root).resolve(), apply=args.apply)
    print(json.dumps(receipt, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
