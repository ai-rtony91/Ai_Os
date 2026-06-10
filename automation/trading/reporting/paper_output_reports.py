"""Paper-only output generators."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(__import__("json").dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_operator_report(run_id: str, lane: str, ledger_path: Path, quality: dict, latency: dict) -> str:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return (
        "# AI_OS Paper Trading Completion Sweep\n\n"
        f"- Run ID: {run_id}\n"
        f"- Lane: {lane}\n"
        f"- Completed UTC: {timestamp}\n"
        f"- Ledger: `{ledger_path.as_posix()}`\n"
        f"- Paper decision quality score: {quality.get('execution_quality_score', 0.0)}\n"
        f"- Median latency ms: {latency.get('median_fill_latency_ms', 0)}\n"
        "- Safety gates: paper_only=true, live_execution_status=BLOCKED, execution_allowed=false\n"
        "- Next action: review operator report and ledger for additional fixture cases.\n"
    )

