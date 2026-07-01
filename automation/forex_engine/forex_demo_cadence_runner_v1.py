from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SCHEMA = "aios.forex.demo_cadence_runner.v1"
RUNTIME_OBJECTIVE = "22_HOURS_PER_DAY_6_DAYS_PER_WEEK"
CONTROLLER_RELATIVE_PATH = Path("automation/forex_engine/forex_continuous_bridge_to_profit_controller_v1.py")
REPORT_RELATIVE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_DEMO_CADENCE_RUNNER_V1_REPORT.md")

MOCK_FILLS = [
    {"fill_id": "MOCK-FILL-001", "symbol": "EUR_USD", "realized_demo_pnl": 42.50, "outcome": "WIN"},
    {"fill_id": "MOCK-FILL-002", "symbol": "GBP_USD", "realized_demo_pnl": -8.25, "outcome": "LOSS"},
    {"fill_id": "MOCK-FILL-003", "symbol": "USD_JPY", "realized_demo_pnl": 37.75, "outcome": "WIN"},
    {"fill_id": "MOCK-FILL-004", "symbol": "AUD_USD", "realized_demo_pnl": 18.00, "outcome": "WIN"},
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _load_module(repo_root: Path, relative_path: Path, module_name: str):
    module_path = repo_root / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{module_name}_unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _controller_runtime_objective(repo_root: Path) -> str:
    controller = _load_module(repo_root, CONTROLLER_RELATIVE_PATH, "forex_continuous_bridge_to_profit_controller")
    result = controller.evaluate_forex_continuous_bridge_to_profit_controller()
    return str(result.get("runtime_objective", ""))


def _window_fill_set(index: int) -> list[dict[str, Any]]:
    first = MOCK_FILLS[index % len(MOCK_FILLS)]
    second = MOCK_FILLS[(index + 1) % len(MOCK_FILLS)]
    return [dict(first), dict(second)]


def build_cadence_receipt(repo_root: Path, *, cycles: int = 1, apply: bool = False) -> dict[str, Any]:
    if cycles < 1:
        cycles = 1
    runtime_objective_observed = _controller_runtime_objective(repo_root)
    start = _utc_now()
    windows: list[dict[str, Any]] = []
    cumulative = 0.0
    for index in range(cycles):
        trading_day_index = index % 7
        open_at = start + timedelta(days=index)
        close_at = open_at + timedelta(hours=22)
        rest_until = open_at + timedelta(days=1)
        fills = [] if trading_day_index == 6 else _window_fill_set(index)
        realized = round(sum(float(fill["realized_demo_pnl"]) for fill in fills), 2)
        cumulative = round(cumulative + realized, 2)
        windows.append(
            {
                "cycle": index + 1,
                "trading_day_index": trading_day_index + 1,
                "window_status": "REST_DAY" if trading_day_index == 6 else "DEMO_WINDOW_CLOSED",
                "open_at_utc": _iso(open_at),
                "close_at_utc": _iso(close_at),
                "rest_until_utc": _iso(rest_until),
                "mock_fills": fills,
                "fill_count": len(fills),
                "realized_demo_pnl": realized,
                "bucket_feed_usd": realized,
                "cumulative_bucket_feed_usd": cumulative,
            }
        )
    receipt = {
        "schema": SCHEMA,
        "mode": "APPLY" if apply else "DRY_RUN",
        "runtime_objective": RUNTIME_OBJECTIVE,
        "runtime_objective_observed": runtime_objective_observed,
        "runtime_objective_aligned": runtime_objective_observed == RUNTIME_OBJECTIVE,
        "cycles_requested": cycles,
        "windows": windows,
        "bucket_feed_receipt": {
            "would_consume_keys": ["profit_bucket", "min_profit_to_sweep", "realized_profit_month"],
            "cumulative_bucket_feed_usd": cumulative,
            "s2_mutated": False,
        },
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
        "broker_used": False,
        "oanda_used": False,
        "network_used": False,
        "scheduler_registered": False,
        "daemon_started": False,
        "written": False,
        "followups": ["F3"],
        "followup_notes": ["F3: wire S2 to consume the emitted bucket-feed in a later packet that owns S2."],
    }
    if apply:
        report_path = repo_root / REPORT_RELATIVE_PATH
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(_render_report(receipt), encoding="utf-8")
        receipt["written"] = True
    return receipt


def _render_report(receipt: dict[str, Any]) -> str:
    return (
        "# AIOS Forex Demo Cadence Runner V1 Report\n\n"
        "Packet: AIOS-P26C\n\n"
        "Demo/mock cadence receipt only. No scheduler, daemon, broker, OANDA, network, credential, live, order, or money path was used.\n\n"
        "```json\n"
        f"{json.dumps(receipt, indent=2, sort_keys=True)}\n"
        "```\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run demo-only Forex cadence windows with mock fills.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    receipt = build_cadence_receipt(Path(args.repo_root).resolve(), cycles=args.cycles, apply=args.apply)
    print(json.dumps(receipt, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
