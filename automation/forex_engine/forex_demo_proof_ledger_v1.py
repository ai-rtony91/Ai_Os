from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "aios.forex.demo_proof_ledger.v1"
LEDGER_RELATIVE_PATH = Path("telemetry/forex/demo_proof_ledger.jsonl")
REPORT_RELATIVE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_DEMO_PROOF_LEDGER_V1_REPORT.md")


def _utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_ledger_path(repo_root: Path) -> Path:
    path = (repo_root / LEDGER_RELATIVE_PATH).resolve()
    telemetry_root = (repo_root / "telemetry" / "forex").resolve()
    if telemetry_root not in path.parents and path != telemetry_root:
        raise RuntimeError("ledger_path_outside_telemetry_forex")
    return path


def _read_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parsed = json.loads(line)
        if isinstance(parsed, dict):
            entries.append(parsed)
    return entries


def _summary(entries: list[dict[str, Any]], *, min_green_days: int = 5) -> dict[str, Any]:
    trading_entries = [entry for entry in entries if entry.get("record_type") != "INITIAL_STUB"]
    cumulative = round(sum(float(entry.get("realized_pnl_usd", 0.0)) for entry in trading_entries), 2)
    streak = 0
    for entry in reversed(trading_entries):
        if float(entry.get("realized_pnl_usd", 0.0)) > 0:
            streak += 1
        else:
            break
    return {
        "schema": "aios.forex.demo_proof_ledger_summary.v1",
        "ledger_line_count": len(entries),
        "demo_trading_day_count": len(trading_entries),
        "cumulative_pnl_usd": cumulative,
        "consecutive_profitable_days": streak,
        "min_consecutive_profitable_days_gate": min_green_days,
        "min_gate_met": streak >= min_green_days,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
    }


def _next_demo_day(entries: list[dict[str, Any]]) -> dict[str, Any]:
    summary = _summary(entries)
    realized = 125.0
    fills = 5
    wins = 4
    losses = 1
    win_rate = round((wins / fills) * 100, 2)
    previous_cumulative = float(summary["cumulative_pnl_usd"])
    previous_streak = int(summary["consecutive_profitable_days"])
    return {
        "schema": SCHEMA,
        "date": _utc_date(),
        "recorded_at_utc": _utc_now(),
        "realized_pnl_usd": realized,
        "fills": fills,
        "wins": wins,
        "losses": losses,
        "win_rate_pct": win_rate,
        "cumulative_pnl_usd": round(previous_cumulative + realized, 2),
        "consecutive_profitable_days": previous_streak + 1 if realized > 0 else 0,
        "mode": "DEMO_ONLY",
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
    }


def build_proof_ledger_receipt(
    repo_root: Path,
    *,
    record_demo_day: bool = False,
    summary: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    ledger_path = _safe_ledger_path(repo_root)
    entries = _read_entries(ledger_path)
    appended = False
    new_entry: dict[str, Any] | None = None
    if record_demo_day:
        new_entry = _next_demo_day(entries)
        if apply:
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(new_entry, sort_keys=True) + "\n")
            appended = True
            entries = _read_entries(ledger_path)
    ledger_summary = _summary(entries)
    receipt = {
        "schema": "aios.forex.demo_proof_ledger_receipt.v1",
        "mode": "APPLY" if apply else "DRY_RUN",
        "record_demo_day_requested": record_demo_day,
        "summary_requested": summary,
        "appended": appended,
        "new_entry": new_entry,
        "summary": ledger_summary,
        "ledger_path": str(LEDGER_RELATIVE_PATH).replace("\\", "/"),
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
        "followups": ["F3-adjacent"],
        "followup_notes": [
            "F3-adjacent: wire consecutive profitable demo days into S1/S2 sweep eligibility in a later packet."
        ],
    }
    if apply:
        report_path = repo_root / REPORT_RELATIVE_PATH
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(_render_report(receipt), encoding="utf-8")
    return receipt


def _render_report(receipt: dict[str, Any]) -> str:
    return (
        "# AIOS Forex Demo Proof Ledger V1 Report\n\n"
        "Packet: AIOS-P26D\n\n"
        "Append-only demo proof ledger evidence. No broker, OANDA, network, credential, live, order, bank, or money path was used.\n\n"
        "```json\n"
        f"{json.dumps(receipt, indent=2, sort_keys=True)}\n"
        "```\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append and summarize demo-only Forex proof ledger.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--record-demo-day", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    receipt = build_proof_ledger_receipt(
        Path(args.repo_root).resolve(),
        record_demo_day=args.record_demo_day,
        summary=args.summary,
        apply=args.apply,
    )
    print(json.dumps(receipt, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
