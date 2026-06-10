"""Paper signal replay loop (dry-run first)."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aios.modules.trader.execution_quality import build_execution_quality_metrics

from automation.trading.bridge.tradingview_signal_bridge import (
    normalize_signal_to_mock_payload,
    read_signal_fixture,
)
from automation.trading.reporting.paper_output_reports import build_operator_report, write_json
from automation.trading.runner.paper_route_preview_runner import run_paper_route_previews
from automation.trading.safety.paper_only_validator import (
    FORBIDDEN_TOKENS,
    is_regime_approved,
    validate_paper_payload,
)


def _repo_root_path(repo_root: Path | None) -> Path:
    if repo_root is not None:
        return Path(repo_root)
    return Path(__file__).resolve().parents[3]


def _to_iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: object, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class PaperSignalReplayResult:
    signal_id: str
    symbol: str
    permission: str
    signal: str
    paper_decision: str
    blocked_reason: str
    paper_only: bool
    live_execution_status: str
    execution_allowed: bool
    latency_ms: int
    route_action: str


def _build_execution_record(price: float, signal_id: str) -> dict[str, Any]:
    return {
        "signal_id": signal_id,
        "paper_only": True,
        "expected_fill_price": price,
        "actual_paper_fill_price": price,
        "paper_slippage": 0.0,
        "spread_estimate": 0.0,
        "fill_latency_ms": 40,
    }


def _build_ledger_entry(payload: dict[str, Any], blockers: list[str], route_preview: dict[str, Any]) -> dict[str, Any]:
    return {
        "signal_id": payload["signal_id"],
        "symbol": payload["symbol"],
        "timeframe": payload["timeframe"],
        "permission": payload["permission"],
        "signal": payload["signal"],
        "paper_decision": "BLOCKED" if blockers else "PAPER_SIMULATE",
        "blocked_reason": " ".join(blockers),
        "route_action": route_preview["action"],
        "route_status": route_preview["route_status"],
        "paper_only": payload["paper_only"],
        "live_execution_status": payload["live_execution_status"],
        "execution_allowed": payload["execution_allowed"],
        "safety_blocked_tokens": sorted(FORBIDDEN_TOKENS),
        "updated_utc": _to_iso_now(),
    }


def _build_latency_entry(payload: dict[str, Any], started_at: str) -> dict[str, Any]:
    age_seconds = 0
    if payload.get("generated_at"):
        try:
            age_seconds = int(
                (
                    datetime.fromisoformat(_to_iso_now().replace("Z", "+00:00")).astimezone(UTC)
                    - datetime.fromisoformat(str(payload["generated_at"]).replace("Z", "+00:00"))
                ).total_seconds()
            )
        except (TypeError, ValueError):
            age_seconds = 0
    return {
        "signal_id": payload["signal_id"],
        "age_seconds": max(age_seconds, 0),
        "started_at": started_at,
        "completed_at": _to_iso_now(),
        "status": "PASS" if payload.get("paper_only") else "BLOCKED",
        "paper_replay": True,
    }


def run_paper_replay(
    *,
    fixture_path: Path,
    repo_root: Path | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    root = _repo_root_path(repo_root)
    raw_fixture = read_signal_fixture(fixture_path)
    signals = raw_fixture if isinstance(raw_fixture, list) else [raw_fixture]
    started_at = _to_iso_now()
    previews = []
    ledger = []
    latency = []
    rejected_order_count = 0
    risk_block_count = 0

    for raw in signals:
        payload = normalize_signal_to_mock_payload(raw)
        blockers = validate_paper_payload(payload)
        regime_ok = is_regime_approved(
            permission=payload["permission"],
            regime=payload.get("regime", "trend_up"),
            trend_score=_safe_float(payload.get("trend_score", 0.0), 0.0),
        )
        if not regime_ok:
            blockers.append("regime_filter_blocked")

        if blockers:
            risk_block_count += 1
            if "live_execution_status must be BLOCKED in paper mode" in blockers:
                rejected_order_count += 1

        preview = run_paper_route_previews([payload])[0]
        previews.append(preview)

        ledger.append(_build_ledger_entry(payload, blockers, preview))
        latency.append(_build_latency_entry(payload, started_at))

    quality_records = [_build_execution_record(_safe_float(item.get("metadata", {}).get("fill_price", 0.0), 0.0), item["signal_id"]) for item in [normalize_signal_to_mock_payload(item) for item in signals]]
    quality = build_execution_quality_metrics(quality_records, rejected_order_count, risk_block_count)

    latencies_ms = [item["fill_latency_ms"] for item in quality_records]
    median_latency = sorted(latencies_ms)[len(latencies_ms) // 2] if latencies_ms else 0
    latency_summary = {
        "lane": "AIOS_PAPER_TRADING_COMPLETION_SWEEP",
        "paper_only": True,
        "runs": len(signals),
        "latency_count": len(latency),
        "median_fill_latency_ms": median_latency,
        "items": latency,
    }
    quality_summary = {
        "run_id": "AIOS-PAPER-TRADING-COMPLETION-SWEEP-001",
        "paper_only": True,
        "generated_at": _to_iso_now(),
        "mode": "paper_only",
        "execution_quality_score": quality["execution_quality_score"],
        "average_paper_slippage": quality["average_paper_slippage"],
        "rejected_order_count": rejected_order_count,
        "risk_block_count": risk_block_count,
        "entries": quality_records,
    }

    results = {
        "run_id": "AIOS-PAPER-TRADING-COMPLETION-SWEEP-001",
        "lane": "AIOS_PAPER_TRADING_COMPLETION_SWEEP",
        "paper_only": True,
        "mode": "paper_only",
        "started_at": started_at,
        "completed_at": _to_iso_now(),
        "previews": previews,
        "ledger": ledger,
        "latency_summary": latency_summary,
        "execution_quality": quality_summary,
    }

    if dry_run is False:
        telemetry_root = root / "telemetry" / "trading_lab"
        report_root = root / "Reports" / "trading_lab"
        telemetry_root.mkdir(parents=True, exist_ok=True)
        report_root.mkdir(parents=True, exist_ok=True)
        write_json(telemetry_root / "paper_execution_ledger.json", {"entries": [dict(item) for item in ledger], "run_id": results["run_id"]})
        write_json(telemetry_root / "paper_latency_summary.json", latency_summary)
        write_json(telemetry_root / "paper_execution_quality_report.json", quality_summary)
        (report_root / "operator_paper_status_report.md").write_text(
            build_operator_report(
                run_id=results["run_id"],
                lane=results["lane"],
                ledger_path=telemetry_root / "paper_execution_ledger.json",
                quality=quality_summary,
                latency=latency_summary,
            ),
            encoding="utf-8",
        )

    return results


def build_replay_result(results: dict[str, Any]) -> list[PaperSignalReplayResult]:
    return [
        PaperSignalReplayResult(
            signal_id=item["signal_id"],
            symbol=item["symbol"],
            permission=item["permission"],
            signal=item["signal"],
            paper_decision=item["paper_decision"],
            blocked_reason=item["blocked_reason"],
            paper_only=item["paper_only"],
            live_execution_status=item["live_execution_status"],
            execution_allowed=item["execution_allowed"],
            latency_ms=latency["age_seconds"],
            route_action=item["route_action"],
        )
        for item, latency in zip(results["ledger"], results["latency_summary"]["items"], strict=False)
    ]

