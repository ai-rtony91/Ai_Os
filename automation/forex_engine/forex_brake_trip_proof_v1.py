"""Deterministic brake-trip proof harness for AIOS Forex."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.stop_pause_resume_engine_v1 import (
    STOP_REQUIRED,
    build_sample_dashboard_state,
    build_sample_operator_halt_state,
    evaluate_stop_pause_resume,
)


SCHEMA = "aios.forex.brake_trip_proof.v1"
LEDGER_RELATIVE_PATH = Path("telemetry/forex/brake_trip_proof_ledger.jsonl")
REPORT_RELATIVE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_BRAKE_TRIP_PROOF_V1_REPORT.md")
SAFETY_CONFIG_RELATIVE_PATH = Path("control/forex/forex_safety_controls_config.json")
SIMULATED_TRIP_PROOF = "SIMULATED_TRIP_PROOF"

T1_READY_STATUS = "RISK_BUDGET_ACCEPTED"
T2_READY_STATUS = "BROKER_HEALTH_REVIEW_READY"
T3_READY_STATUS = "PROFITABILITY_EVIDENCE_REVIEW_READY"


def run_forex_brake_trip_proof_v1(
    repo_root: Path,
    *,
    safety_config_mapping: Mapping[str, Any] | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    safety_config, safety_config_source = _load_safety_config(
        repo_root, safety_config_mapping=safety_config_mapping
    )
    ledger_path = _safe_repo_path(repo_root, LEDGER_RELATIVE_PATH)
    report_path = _safe_repo_path(repo_root, REPORT_RELATIVE_PATH)

    existing_entries = _read_ledger_entries(ledger_path)
    trip_results = [
        _simulate_kill_switch_trip(safety_config),
        _simulate_daily_stop_trip(safety_config),
        _simulate_max_loss_trip(safety_config),
    ]
    appended_entries = list(existing_entries) + trip_results
    all_trips_passed = all(bool(entry["trip_passed"]) for entry in trip_results)

    receipt = {
        "schema": SCHEMA,
        "mode": "APPLY" if apply else "DRY_RUN",
        "repo_root": str(repo_root),
        "ledger_path": str(LEDGER_RELATIVE_PATH).replace("\\", "/"),
        "report_path": str(REPORT_RELATIVE_PATH).replace("\\", "/"),
        "safety_config_source": safety_config_source,
        "safety_controls": _safety_controls_snapshot(safety_config),
        "ledger_entry_count_before": len(existing_entries),
        "ledger_entry_count_after": len(appended_entries),
        "appended_entry_count": len(trip_results) if apply else 0,
        "trip_results": trip_results,
        "all_trips_passed": all_trips_passed,
        "simulated_trip_proof_label": SIMULATED_TRIP_PROOF,
        "live_trading_allowed": False,
        "broker_api_allowed": False,
        "credential_access_allowed": False,
        "account_identifier_persistence_allowed": False,
        "order_execution_allowed": False,
        "money_movement_allowed": False,
        "owner_reset_required": any(
            bool(entry.get("owner_reset_required")) for entry in trip_results
        ),
        "next_safe_action": (
            "Keep this proof simulated; owner approval is required before any later real demo loop."
        ),
    }

    if apply:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(
            json.dumps(appended_entries, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(_render_report(receipt), encoding="utf-8")
        receipt["report_output_path"] = str(REPORT_RELATIVE_PATH).replace("\\", "/")

    return receipt


def _simulate_kill_switch_trip(config: Mapping[str, Any]) -> dict[str, Any]:
    kill_switch = dict(config.get("kill_switch", {}))
    operator_halt = build_sample_operator_halt_state()
    operator_halt["halt_requested"] = True

    result = evaluate_stop_pause_resume(
        {
            "status": T1_READY_STATUS,
            "blockers": [],
            "paper_only": True,
        },
        {
            "status": T2_READY_STATUS,
            "blockers": [],
            "paper_only": True,
        },
        {
            "status": T3_READY_STATUS,
            "blockers": [],
            "paper_only": True,
        },
        build_sample_dashboard_state(),
        operator_halt,
    )

    trip_passed = _text(result.get("status")) == STOP_REQUIRED
    return {
        "schema": "aios.forex.brake_trip_proof_trip.v1",
        "trip_id": "T1",
        "trip_name": "kill_switch_stop_flag",
        "ledger_label": SIMULATED_TRIP_PROOF,
        "recorded_at_utc": _utc_now(),
        "trip_passed": trip_passed,
        "expected_status": STOP_REQUIRED,
        "stop_pause_resume_status": _text(result.get("status")),
        "stop_pause_resume_control_state": _text(result.get("control_state")),
        "stop_pause_resume_blockers": _string_list(result.get("blockers")),
        "simulated_cycle_state_before": "RUNNING_DEMO",
        "simulated_cycle_state_after": "STOPPED",
        "further_simulated_trades_allowed": False,
        "no_further_simulated_trades_occurred": True,
        "halt_requested": True,
        "kill_switch_state": _text(kill_switch.get("state")),
        "kill_switch_mechanism": _text(kill_switch.get("mechanism")),
        "control_actions": ["STOP"],
        "next_safe_action": _text(result.get("next_safe_action")),
        "config_snapshot": {
            "kill_switch_state": _text(kill_switch.get("state")),
            "kill_switch_mechanism": _text(kill_switch.get("mechanism")),
        },
    }


def _simulate_daily_stop_trip(config: Mapping[str, Any]) -> dict[str, Any]:
    daily_stop = dict(config.get("daily_stop", {}))
    warning_threshold = _as_float(
        daily_stop.get("daily_loss_warning_usd"), field_name="daily_loss_warning_usd"
    )
    halt_threshold = _as_float(
        daily_stop.get("daily_loss_stop_usd"), field_name="daily_loss_stop_usd"
    )
    daily_loss_sequence = [6.0, 5.0, 4.0, 8.0, 8.0, 7.0]

    executed_trades: list[dict[str, Any]] = []
    blocked_candidates: list[dict[str, Any]] = []
    daily_loss = 0.0
    warning_triggered_at_loss_usd: float | None = None
    halt_triggered_at_loss_usd: float | None = None
    halt_trade_index: int | None = None

    for trade_index, realized_loss_usd in enumerate(daily_loss_sequence, start=1):
        if halt_triggered_at_loss_usd is not None:
            blocked_candidates.append(
                {
                    "trade_index": trade_index,
                    "realized_loss_usd": realized_loss_usd,
                    "blocked_reason": "HALT_FOR_DAY",
                }
            )
            continue

        daily_loss = round(daily_loss + realized_loss_usd, 2)
        executed_trades.append(
            {
                "trade_index": trade_index,
                "realized_loss_usd": realized_loss_usd,
                "cumulative_daily_loss_usd": daily_loss,
            }
        )
        if warning_triggered_at_loss_usd is None and daily_loss >= warning_threshold:
            warning_triggered_at_loss_usd = daily_loss
        if daily_loss >= halt_threshold:
            halt_triggered_at_loss_usd = daily_loss
            halt_trade_index = trade_index

    trip_passed = (
        warning_triggered_at_loss_usd is not None
        and halt_triggered_at_loss_usd is not None
        and len(blocked_candidates) >= 1
        and all(
            candidate["blocked_reason"] == "HALT_FOR_DAY"
            for candidate in blocked_candidates
        )
    )

    return {
        "schema": "aios.forex.brake_trip_proof_trip.v1",
        "trip_id": "T2",
        "trip_name": "daily_stop_trip",
        "ledger_label": SIMULATED_TRIP_PROOF,
        "recorded_at_utc": _utc_now(),
        "trip_passed": trip_passed,
        "warning_intent_emitted": warning_triggered_at_loss_usd is not None,
        "warning_triggered_at_loss_usd": warning_triggered_at_loss_usd,
        "warning_threshold_usd": warning_threshold,
        "halt_action": "HALT_FOR_DAY",
        "halt_triggered_at_loss_usd": halt_triggered_at_loss_usd,
        "halt_threshold_usd": halt_threshold,
        "halt_trade_index": halt_trade_index,
        "executed_trade_count": len(executed_trades),
        "blocked_trade_count_after_halt": len(blocked_candidates),
        "no_further_simulated_trades_occurred": len(blocked_candidates) >= 1,
        "executed_trades": executed_trades,
        "blocked_candidates_after_halt": blocked_candidates,
        "control_actions": ["WARNING_INTENT", "HALT_FOR_DAY"],
        "next_safe_action": "Stop additional simulated trades for the day after the warning and halt thresholds trip.",
        "config_snapshot": {
            "daily_loss_warning_usd": warning_threshold,
            "daily_loss_stop_usd": halt_threshold,
        },
    }


def _simulate_max_loss_trip(config: Mapping[str, Any]) -> dict[str, Any]:
    max_loss = dict(config.get("max_loss", {}))
    max_total_loss_usd = _as_float(
        max_loss.get("max_total_loss_usd"), field_name="max_total_loss_usd"
    )
    cumulative_loss_sequence = [40.0, 50.0, 61.0, 12.0]

    executed_trades: list[dict[str, Any]] = []
    blocked_candidates: list[dict[str, Any]] = []
    cumulative_loss = 0.0
    halt_triggered_at_loss_usd: float | None = None
    halt_trade_index: int | None = None

    for trade_index, realized_loss_usd in enumerate(cumulative_loss_sequence, start=1):
        if halt_triggered_at_loss_usd is not None:
            blocked_candidates.append(
                {
                    "trade_index": trade_index,
                    "realized_loss_usd": realized_loss_usd,
                    "blocked_reason": "HALT_ALL",
                }
            )
            continue

        cumulative_loss = round(cumulative_loss + realized_loss_usd, 2)
        executed_trades.append(
            {
                "trade_index": trade_index,
                "realized_loss_usd": realized_loss_usd,
                "cumulative_loss_usd": cumulative_loss,
            }
        )
        if cumulative_loss >= max_total_loss_usd:
            halt_triggered_at_loss_usd = cumulative_loss
            halt_trade_index = trade_index

    owner_reset_required = halt_triggered_at_loss_usd is not None
    trip_passed = (
        owner_reset_required
        and len(blocked_candidates) >= 1
        and all(candidate["blocked_reason"] == "HALT_ALL" for candidate in blocked_candidates)
    )

    return {
        "schema": "aios.forex.brake_trip_proof_trip.v1",
        "trip_id": "T3",
        "trip_name": "max_loss_trip",
        "ledger_label": SIMULATED_TRIP_PROOF,
        "recorded_at_utc": _utc_now(),
        "trip_passed": trip_passed,
        "halt_action": "HALT_ALL",
        "owner_reset_required": owner_reset_required,
        "halt_triggered_at_cumulative_loss_usd": halt_triggered_at_loss_usd,
        "max_total_loss_usd": max_total_loss_usd,
        "halt_trade_index": halt_trade_index,
        "executed_trade_count": len(executed_trades),
        "blocked_trade_count_after_halt": len(blocked_candidates),
        "no_further_simulated_trades_occurred": len(blocked_candidates) >= 1,
        "executed_trades": executed_trades,
        "blocked_candidates_after_halt": blocked_candidates,
        "control_actions": ["HALT_ALL", "OWNER_RESET_REQUIRED"],
        "next_safe_action": "Stop all simulated trading and require owner reset after the cumulative loss threshold trips.",
        "config_snapshot": {
            "max_total_loss_usd": max_total_loss_usd,
        },
    }


def _render_report(receipt: Mapping[str, Any]) -> str:
    return (
        "# AIOS Forex Brake Trip Proof V1 Report\n\n"
        "Append-only simulated brake-trip proof only. No broker, live order, credential, network, or money path was used.\n\n"
        "## Safety controls\n\n"
        f"- kill_switch_state: {receipt['safety_controls']['kill_switch_state']}\n"
        f"- daily_loss_warning_usd: {receipt['safety_controls']['daily_loss_warning_usd']}\n"
        f"- daily_loss_stop_usd: {receipt['safety_controls']['daily_loss_stop_usd']}\n"
        f"- max_total_loss_usd: {receipt['safety_controls']['max_total_loss_usd']}\n\n"
        "## Trip summary\n\n"
        f"- T1 kill switch: {'PASS' if receipt['trip_results'][0]['trip_passed'] else 'FAIL'}\n"
        f"- T2 daily stop: {'PASS' if receipt['trip_results'][1]['trip_passed'] else 'FAIL'}\n"
        f"- T3 max loss: {'PASS' if receipt['trip_results'][2]['trip_passed'] else 'FAIL'}\n"
        f"- ledger entries written: {receipt['ledger_entry_count_after']}\n"
        f"- ledger label: {receipt['simulated_trip_proof_label']}\n\n"
        "## Receipt\n\n"
        f"```json\n{json.dumps(dict(receipt), indent=2, sort_keys=True)}\n```\n"
    )


def _load_safety_config(
    repo_root: Path,
    *,
    safety_config_mapping: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], str]:
    if safety_config_mapping is not None:
        return dict(safety_config_mapping), "mapping"
    config_path = _safe_repo_path(repo_root, SAFETY_CONFIG_RELATIVE_PATH)
    loaded = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("forex_safety_controls_config_must_be_object")
    return loaded, str(SAFETY_CONFIG_RELATIVE_PATH).replace("\\", "/")


def _safe_repo_path(repo_root: Path, relative_path: Path) -> Path:
    path = (repo_root / relative_path).resolve()
    repo_root = repo_root.resolve()
    if repo_root not in path.parents and path != repo_root:
        raise RuntimeError(f"path_outside_repo_root:{relative_path}")
    return path


def _read_ledger_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise ValueError("brake_trip_ledger_must_be_array")
    entries: list[dict[str, Any]] = []
    for index, item in enumerate(loaded):
        if not isinstance(item, dict):
            raise ValueError(f"brake_trip_ledger_entry_{index}_must_be_object")
        entries.append(dict(item))
    return entries


def _safety_controls_snapshot(config: Mapping[str, Any]) -> dict[str, Any]:
    kill_switch = dict(config.get("kill_switch", {}))
    daily_stop = dict(config.get("daily_stop", {}))
    max_loss = dict(config.get("max_loss", {}))
    return {
        "schema": "aios.forex.safety_controls_snapshot.v1",
        "mode": _text(config.get("mode"), default="DEMO_ONLY"),
        "kill_switch_state": _text(kill_switch.get("state")),
        "kill_switch_mechanism": _text(kill_switch.get("mechanism")),
        "daily_loss_warning_usd": _as_float(
            daily_stop.get("daily_loss_warning_usd"), field_name="daily_loss_warning_usd"
        ),
        "daily_loss_stop_usd": _as_float(
            daily_stop.get("daily_loss_stop_usd"), field_name="daily_loss_stop_usd"
        ),
        "max_total_loss_usd": _as_float(
            max_loss.get("max_total_loss_usd"), field_name="max_total_loss_usd"
        ),
        "money_movement_allowed": bool(config.get("money_movement_allowed", False)),
        "bank_access_allowed": bool(config.get("bank_access_allowed", False)),
        "live_capital_action_authorized": bool(
            config.get("live_capital_action_authorized", False)
        ),
    }


def _as_float(value: Any, *, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name}_invalid") from exc
    if parsed <= 0:
        raise ValueError(f"{field_name}_must_be_positive")
    return parsed


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _string_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values]
    if isinstance(values, Mapping):
        return []
    if isinstance(values, (list, tuple, set)):
        return [str(value) for value in values]
    return [str(values)]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic Forex brake trip proof simulations.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    receipt = run_forex_brake_trip_proof_v1(Path(args.repo_root).resolve(), apply=args.apply)
    print(json.dumps(receipt, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
