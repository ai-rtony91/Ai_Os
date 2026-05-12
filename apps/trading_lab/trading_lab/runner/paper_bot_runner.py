from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_lab.execution.risk_gate import check_paper_risk


REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_ROOT = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "fixtures" / "paper_runner"
RESULT_ROOT = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "results" / "paper_runner"
DASHBOARD_FIXTURE = REPO_ROOT / "apps" / "dashboard" / "mock-data" / "trading-lab-paper-runner.example.json"


SAFETY_STATUS = {
    "live_execution_status": "BLOCKED",
    "broker_status": "BLOCKED",
    "oanda_status": "BLOCKED",
    "api_key_status": "BLOCKED",
    "secrets_status": "BLOCKED",
    "real_webhook_status": "BLOCKED",
    "real_order_status": "BLOCKED",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def now_utc_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def check_staleness(signal: dict[str, Any], validation_time: datetime) -> dict[str, Any]:
    generated_at = parse_utc(signal["generated_at"])
    age_seconds = int((validation_time - generated_at).total_seconds())
    max_age_seconds = int(signal.get("max_age_seconds", 900))
    is_stale = age_seconds > max_age_seconds
    return {
        "generated_at": signal["generated_at"],
        "validated_at": validation_time.isoformat().replace("+00:00", "Z"),
        "age_seconds": age_seconds,
        "max_age_seconds": max_age_seconds,
        "stale_signal_status": "BLOCKED" if is_stale else "PASS",
        "blocked_reason": "Signal is stale." if is_stale else "",
    }


def check_regime(signal: dict[str, Any], candle: dict[str, Any], regime: dict[str, Any]) -> dict[str, Any]:
    expected = signal.get("expected_regime")
    observed = regime.get("regime_status")
    trend_alignment = candle.get("trend_alignment")
    passed = observed == expected and trend_alignment == "aligned"
    return {
        "regime_result_id": "PAPER_REGIME_RESULT_001",
        "mode": "paper_only",
        "signal_id": signal["signal_id"],
        "expected_regime": expected,
        "observed_regime": observed,
        "trend_alignment": trend_alignment,
        "regime_check_status": "PASS" if passed else "BLOCKED",
        "blocked_reason": "" if passed else "Regime fixture does not match signal requirements.",
        **SAFETY_STATUS,
    }


def build_scorecard(decision: str, signal: dict[str, Any], risk_result: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    simulated = decision == "PAPER_SIMULATED"
    return {
        "scorecard_id": "PAPER_SCORECARD_001",
        "mode": "paper_only",
        "signal_id": signal["signal_id"],
        "paper_decision": decision,
        "trade_count": 1 if simulated else 0,
        "simulated_count": 1 if simulated else 0,
        "blocked_count": 0 if simulated else 1,
        "evidence_score": evidence.get("evidence_score", 0),
        "risk_gate_status": risk_result["risk_gate_status"],
        "review_status": "READY_FOR_REVIEW" if simulated else "BLOCKED",
        "blocked_reason": "" if simulated else risk_result["blocked_reason"],
        "next_safe_action": "Review the paper result ledger; keep all execution paper-only.",
        **SAFETY_STATUS,
    }


def run_paper_runner() -> dict[str, Any]:
    signal = load_json(FIXTURE_ROOT / "PAPER_SIGNAL_FIXTURE_001.json")
    candle = load_json(FIXTURE_ROOT / "PAPER_CANDLE_FIXTURE_001.json")
    regime = load_json(FIXTURE_ROOT / "PAPER_REGIME_FIXTURE_001.json")
    evidence = load_json(FIXTURE_ROOT / "PAPER_EVIDENCE_FIXTURE_001.json")

    validation_time = datetime.now(UTC).replace(microsecond=0)
    validation_time_text = validation_time.isoformat().replace("+00:00", "Z")

    stale_result = check_staleness(signal, validation_time)
    regime_result = check_regime(signal, candle, regime)
    risk_gate = check_paper_risk(
        symbol=signal.get("symbol"),
        side=signal.get("side"),
        quantity=float(signal.get("quantity", 0)),
        regime_status=regime_result["observed_regime"],
        evidence_score=evidence.get("evidence_score", 0),
    )

    blockers: list[str] = []
    if stale_result["stale_signal_status"] != "PASS":
        blockers.append(stale_result["blocked_reason"])
    if regime_result["regime_check_status"] != "PASS":
        blockers.append(regime_result["blocked_reason"])
    if not risk_gate["approved"]:
        blockers.append(risk_gate["reason"])

    paper_decision = "BLOCKED" if blockers else "PAPER_SIMULATED"
    blocked_reason = " ".join(blocker for blocker in blockers if blocker)

    latency_report = {
        "latency_report_id": "PAPER_LATENCY_REPORT_001",
        "mode": "paper_only",
        "signal_id": signal["signal_id"],
        "candle_fixture_id": candle["candle_fixture_id"],
        "validation_started_at": validation_time_text,
        "validation_completed_at": now_utc_iso(),
        "stale_signal_check": stale_result,
        **SAFETY_STATUS,
    }

    risk_report = {
        "risk_gate_result_id": "PAPER_RISK_GATE_RESULT_001",
        "mode": "paper_only",
        "signal_id": signal["signal_id"],
        "risk_gate_status": "PASS" if risk_gate["approved"] else "BLOCKED",
        "risk_gate_source": "trading_lab.execution.risk_gate.check_paper_risk",
        "approved_for": "paper_simulation_only" if risk_gate["approved"] else "none",
        "blocked_reason": "" if risk_gate["approved"] else risk_gate["reason"],
        "risk_gate_detail": risk_gate,
        **SAFETY_STATUS,
    }

    ledger = {
        "ledger_id": "PAPER_RESULT_LEDGER_001",
        "mode": "paper_only",
        "signal_id": signal["signal_id"],
        "symbol": signal["symbol"],
        "side": signal["side"],
        "quantity": signal["quantity"],
        "paper_decision": paper_decision,
        "paper_result": "paper_fill_recorded" if paper_decision == "PAPER_SIMULATED" else "not_simulated",
        "paper_entry_price": candle["close"],
        "paper_exit_price": None,
        "blocked_reason": blocked_reason,
        "validated_at": validation_time_text,
        **SAFETY_STATUS,
    }

    scorecard = build_scorecard(paper_decision, signal, risk_report, evidence)
    validation_report = {
        "validation_report_id": "PAPER_VALIDATION_REPORT_001",
        "phase": "15.4",
        "mode": "paper_only",
        "result": "PASS",
        "paper_decision": paper_decision,
        "required_flow": [
            "signal fixture",
            "candle fixture",
            "latency stamp",
            "stale signal check",
            "regime check",
            "risk gate",
            "paper decision",
            "paper result",
            "scorecard",
            "validator report",
            "next action",
        ],
        "blocked_reason": blocked_reason,
        "validated_at": validation_time_text,
        **SAFETY_STATUS,
    }

    next_action = (
        "# Paper Runner Next Action\n\n"
        "Review `PAPER_RESULT_LEDGER_001.json` and `PAPER_SCORECARD_001.json`, then decide whether the next APPLY should add more fixture scenarios.\n\n"
        "Safety: paper-only, local fixture-only, no broker, no external account connection, no real webhook, no real order.\n"
    )

    dashboard = {
        "fixture_name": "trading-lab-paper-runner.example.json",
        "phase": "15.4",
        "mode": "paper_only",
        "runner_status": "PASS",
        "paper_decision": paper_decision,
        "blocked_reason": blocked_reason,
        "latest_signal_id": signal["signal_id"],
        "result_paths": {
            "ledger": "apps/trading_lab/trading_lab/results/paper_runner/PAPER_RESULT_LEDGER_001.json",
            "scorecard": "apps/trading_lab/trading_lab/results/paper_runner/PAPER_SCORECARD_001.json",
            "validation": "apps/trading_lab/trading_lab/results/paper_runner/PAPER_VALIDATION_REPORT_001.json",
            "next_action": "apps/trading_lab/trading_lab/results/paper_runner/PAPER_NEXT_ACTION.md",
        },
        "next_safe_action": "Review paper runner outputs before adding more fixture cases.",
        **SAFETY_STATUS,
    }

    write_json(RESULT_ROOT / "PAPER_LATENCY_REPORT_001.json", latency_report)
    write_json(RESULT_ROOT / "PAPER_REGIME_RESULT_001.json", regime_result)
    write_json(RESULT_ROOT / "PAPER_RISK_GATE_RESULT_001.json", risk_report)
    write_json(RESULT_ROOT / "PAPER_RESULT_LEDGER_001.json", ledger)
    write_json(RESULT_ROOT / "PAPER_SCORECARD_001.json", scorecard)
    write_json(RESULT_ROOT / "PAPER_VALIDATION_REPORT_001.json", validation_report)
    write_text(RESULT_ROOT / "PAPER_NEXT_ACTION.md", next_action)
    write_json(DASHBOARD_FIXTURE, dashboard)

    return validation_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the AI_OS Trading Lab paper-only runner.")
    parser.add_argument("--json", action="store_true", help="Print the validation report as JSON.")
    args = parser.parse_args()
    report = run_paper_runner()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"AI_OS Trading Lab Paper Runner: {report['result']}")
        print(f"Paper decision: {report['paper_decision']}")
        print("Safety: paper-only local fixtures; execution remains blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
