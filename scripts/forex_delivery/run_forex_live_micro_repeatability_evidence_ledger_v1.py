"""Repeatability evidence ledger for controlled live micro read-only snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

PACKET_ID = "PKT-FOREX-LIVE-MICRO-REPEATABILITY-EVIDENCE-LEDGER-V1"
MODULE = "run_forex_live_micro_repeatability_evidence_ledger_v1"

DEFAULT_EVIDENCE_STATE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EVIDENCE_REVIEW_V1_STATE.json",
)
DEFAULT_STATE_OUTPUT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_REPEATABILITY_EVIDENCE_LEDGER_V1_STATE.json",
)
DEFAULT_REPORT_OUTPUT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_REPEATABILITY_EVIDENCE_LEDGER_V1_REPORT.md",
)

CURRENT_STAGE = "live_micro_repeatability_evidence_ledger"
MIN_SNAPSHOTS_DEFAULT = 1

LIVE_MICRO_REPEATABILITY_LEDGER_READY = "LIVE_MICRO_REPEATABILITY_LEDGER_READY"
LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS = (
    "LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS"
)
LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE = (
    "LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE"
)
LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT = (
    "LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT"
)
LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE = (
    "LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE"
)
LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING = (
    "LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING"
)
LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED = (
    "LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED"
)
LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED = (
    "LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED"
)
LIVE_MICRO_REPEATABILITY_REPAIR_REQUIRED = (
    "LIVE_MICRO_REPEATABILITY_REPAIR_REQUIRED"
)

STATUS_TO_NEXT_STAGE = {
    LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS: "owner_collect_additional_snapshots",
    LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE: "owner_supervised_repeatability_decision",
    LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT: "owner_supervised_repeatability_decision",
    LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE: "owner_supervised_repeatability_decision",
    LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING: "owner_repair_sltp_evidence",
    LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED: "owner_investigate_forbidden_flags",
    LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED: (
        "owner_investigate_money_or_execution_flags"
    ),
    LIVE_MICRO_REPEATABILITY_LEDGER_READY: "owner_supervised_repeatability_decision",
    LIVE_MICRO_REPEATABILITY_REPAIR_REQUIRED: "owner_repair_input_payload",
}

FORBIDDEN_ACTION_FLAGS = (
    "order_endpoint_called",
    "post_request_called",
    "trade_close_called",
    "position_close_called",
)
LIVE_EXECUTION_FLAGS = ("live_order_execution", "demo_order_execution")


def run_forex_live_micro_repeatability_evidence_ledger_v1(
    * ,
    evidence_state_paths: Sequence[Path] | None = None,
    min_snapshots: int = MIN_SNAPSHOTS_DEFAULT,
    state_output: Path = DEFAULT_STATE_OUTPUT_PATH,
    report_output: Path = DEFAULT_REPORT_OUTPUT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    paths = _coerce_evidence_paths(evidence_state_paths)
    snapshots = _load_snapshots(paths)

    runtime_summary = _build_runtime_summary(
        snapshots,
        min_snapshots=min_snapshots,
    )
    repeatability_status = _classify_repeatability(snapshots, min_snapshots=min_snapshots)

    result = {
        "repeatability_status": repeatability_status,
        "current_stage": CURRENT_STAGE,
        "next_stage": STATUS_TO_NEXT_STAGE.get(
            repeatability_status,
            "owner_repair_input_payload",
        ),
        "blockers": runtime_summary["blockers"],
        "safe_next_action": _safe_next_action(
            repeatability_status,
            runtime_summary=runtime_summary,
        ),
    }
    payload = {
        "module": MODULE,
        "packet_id": PACKET_ID,
        "input": _build_input_block(paths, snapshots),
        "result": result,
        "runtime_summary": runtime_summary,
    }
    return _write_artifacts(payload, state_output, report_output, write_report=write_report)


def _coerce_evidence_paths(
    evidence_state_paths: Sequence[Path] | None,
) -> list[Path]:
    if evidence_state_paths:
        return [Path(item) for item in evidence_state_paths if str(item).strip()]
    return [DEFAULT_EVIDENCE_STATE_PATH]


def _load_snapshots(
    paths: Sequence[Path],
) -> list[tuple[Path, dict[str, Any]]]:
    snapshots = []
    for path in paths:
        if not path.exists():
            continue
        try:
            payload = _read_json_object(path)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if isinstance(payload, dict):
            snapshots.append((path, payload))
    return snapshots


def _build_input_block(
    requested_paths: Sequence[Path],
    snapshots: Sequence[tuple[Path, dict[str, Any]]],
) -> dict[str, Any]:
    found = [str(path) for path, _ in snapshots]
    missing = [str(path) for path in requested_paths if not path.exists()]
    aggregated = _aggregate_input_flags(snapshots)
    return {
        "evidence_state_paths": [str(path) for path in requested_paths],
        "evidence_files_found": found,
        "evidence_files_missing": missing,
        "local_only": True,
        # Ledger itself does not call broker or Bitwarden.
        "broker_api_called": False,
        "bitwarden_called": False,
        **aggregated,
    }


def _aggregate_input_flags(snapshots: Sequence[tuple[Path, dict[str, Any]]]) -> dict[str, Any]:
    input_defaults = _empty_input_flags()
    if not snapshots:
        return input_defaults
    for _, snapshot in snapshots:
        runtime_input = _as_mapping(snapshot.get("input", {}))
        for key in input_defaults:
            input_defaults[key] = bool(input_defaults[key] or bool(runtime_input.get(key, False)))
    return input_defaults


def _empty_input_flags() -> dict[str, Any]:
    return {
        "live_order_execution": False,
        "money_movement": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "order_endpoint_called": False,
        "post_request_called": False,
        "trade_close_called": False,
        "position_close_called": False,
    }


def _build_runtime_summary(
    snapshots: Sequence[tuple[Path, dict[str, Any]]],
    *,
    min_snapshots: int,
) -> dict[str, Any]:
    snapshot_count = len(snapshots)
    if snapshot_count == 0:
        return {
            "snapshot_count": 0,
            "open_trade_seen_count": 0,
            "closed_or_not_visible_count": 0,
            "profit_positive_count": 0,
            "profit_flat_count": 0,
            "profit_negative_count": 0,
            "pnl_values": [],
            "latest_pnl_value": None,
            "latest_pnl_classification": "unavailable",
            "sltp_complete_count": 0,
            "sltp_missing_count": 0,
            "sltp_latest_complete": False,
            "risk_controls_consistent": False,
            "forbidden_action_flags_clear": False,
            "live_execution_flags_clear": False,
            "money_movement_clear": False,
            "readiness_for_next_supervised_decision": False,
            "evidence_fingerprints": [],
            "safe_next_action": "Add or point to a valid evidence snapshot file.",
            "blockers": ["insufficient snapshots"],
            "latest_snapshot_path": None,
        }

    open_trade_seen_count = 0
    closed_or_not_visible_count = 0
    profit_positive_count = 0
    profit_flat_count = 0
    profit_negative_count = 0
    pnl_values: list[float | int] = []
    sltp_complete_count = 0
    sltp_missing_count = 0
    latest_snapshot_path = str(snapshots[-1][0])
    latest_runtime = _as_mapping(snapshots[-1][1].get("runtime_summary", {}))
    latest_pnl_value = _coerce_float(latest_runtime.get("unrealized_pl_value"))
    latest_pnl_classification = _coerce_pnl_classification(
        latest_runtime.get("pnl_classification"),
        latest_pnl_value,
    )

    forbidden_action_flags_clear = True
    live_execution_flags_clear = True
    money_movement_clear = True
    risk_controls_seen = []
    fingerprints = []
    for path, payload in snapshots:
        input_block = _as_mapping(payload.get("input", {}))
        runtime = _as_mapping(payload.get("runtime_summary", {}))

        if bool(input_block.get("order_endpoint_called")):
            forbidden_action_flags_clear = False
        if bool(input_block.get("post_request_called")):
            forbidden_action_flags_clear = False
        if bool(input_block.get("trade_close_called")):
            forbidden_action_flags_clear = False
        if bool(input_block.get("position_close_called")):
            forbidden_action_flags_clear = False

        if bool(input_block.get("live_order_execution")):
            live_execution_flags_clear = False
            money_movement_clear = False
        if bool(input_block.get("money_movement")):
            money_movement_clear = False
            live_execution_flags_clear = False
        if bool(input_block.get("demo_order_execution")):
            live_execution_flags_clear = False

        open_trade_found = bool(runtime.get("open_trade_found", False))
        open_position_found = bool(runtime.get("open_position_found", False))
        if open_trade_found:
            open_trade_seen_count += 1
        elif open_position_found:
            # Open position without openTrades still indicates active exposure in legacy payloads.
            open_trade_seen_count += 1
        else:
            closed_or_not_visible_count += 1

        pnl_value = _coerce_float(runtime.get("unrealized_pl_value"))
        if pnl_value is not None:
            pnl_values.append(pnl_value)

        classification = _coerce_pnl_classification(
            runtime.get("pnl_classification"),
            pnl_value,
        )
        if classification == "positive":
            profit_positive_count += 1
        elif classification == "flat":
            profit_flat_count += 1
        elif classification == "negative":
            profit_negative_count += 1

        sltp_complete = bool(runtime.get("sltp_evidence_complete", False))
        if sltp_complete:
            sltp_complete_count += 1
        else:
            sltp_missing_count += 1

        risk_controls = runtime.get("risk_controls_observed")
        if isinstance(risk_controls, bool):
            risk_controls_seen.append(risk_controls)

        snapshot_fingerprint = _snapshot_fingerprint(payload)
        if snapshot_fingerprint:
            fingerprints.append(snapshot_fingerprint)
        runtime_fingerprints = _extract_fingerprints(runtime)
        for fp in runtime_fingerprints:
            if fp not in fingerprints:
                fingerprints.append(fp)
    risk_controls_consistent = all(risk_controls_seen) if risk_controls_seen else False
    if not risk_controls_seen:
        risk_controls_consistent = False

    blockers: list[str] = []
    readiness_for_next_supervised_decision = False
    if latest_pnl_classification not in {"positive", "flat", "negative"}:
        blockers.append("latest pnl classification unavailable")
    if not forbidden_action_flags_clear:
        blockers.append("forbidden API flag observed in one or more snapshots")
    if not live_execution_flags_clear:
        blockers.append("live/demo execution flag observed in one or more snapshots")
    if not money_movement_clear:
        blockers.append("money movement flag observed in one or more snapshots")

    readiness_for_next_supervised_decision = (
        latest_pnl_classification in {"positive", "flat", "negative"}
        and forbidden_action_flags_clear
        and live_execution_flags_clear
        and money_movement_clear
        and snapshot_count >= min_snapshots
        and not blockers
        and latest_pnl_value is not None
    )

    return {
        "snapshot_count": snapshot_count,
        "open_trade_seen_count": open_trade_seen_count,
        "closed_or_not_visible_count": closed_or_not_visible_count,
        "profit_positive_count": profit_positive_count,
        "profit_flat_count": profit_flat_count,
        "profit_negative_count": profit_negative_count,
        "pnl_values": pnl_values,
        "latest_pnl_value": latest_pnl_value,
        "latest_pnl_classification": latest_pnl_classification,
        "sltp_complete_count": sltp_complete_count,
        "sltp_missing_count": sltp_missing_count,
        "sltp_latest_complete": bool(
            latest_runtime.get("sltp_evidence_complete", False),
        ),
        "risk_controls_consistent": risk_controls_consistent,
        "forbidden_action_flags_clear": forbidden_action_flags_clear,
        "live_execution_flags_clear": live_execution_flags_clear,
        "money_movement_clear": money_movement_clear,
        "readiness_for_next_supervised_decision": readiness_for_next_supervised_decision,
        "evidence_fingerprints": fingerprints,
        "safe_next_action": _safe_next_action(
            _classify_repeatability(snapshots, min_snapshots=min_snapshots),
            runtime_summary=None,
        ),
        "blockers": blockers,
        "latest_snapshot_path": latest_snapshot_path,
    }


def _classify_repeatability(
    snapshots: Sequence[tuple[Path, dict[str, Any]]],
    *,
    min_snapshots: int,
) -> str:
    if len(snapshots) < min_snapshots:
        return LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS
    if not snapshots:
        return LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS
    latest_input = _as_mapping(snapshots[-1][1].get("input", {}))
    latest_runtime = _as_mapping(snapshots[-1][1].get("runtime_summary", {}))
    for snapshot in snapshots:
        runtime_input = _as_mapping(snapshot[1].get("input", {}))
        for field in FORBIDDEN_ACTION_FLAGS:
            if runtime_input.get(field):
                return LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED
        if any(
            bool(runtime_input.get(flag))
            for flag in LIVE_EXECUTION_FLAGS
        ):
            return LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED
        if runtime_input.get("money_movement"):
            return LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED
    if not bool(latest_input.get("order_endpoint_called")) and not bool(
        latest_input.get("post_request_called"),
    ):
        sltp_complete = bool(latest_runtime.get("sltp_evidence_complete", False))
        if not sltp_complete:
            return LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING

    latest_pnl_classification = _coerce_pnl_classification(
        latest_runtime.get("pnl_classification"),
        _coerce_float(latest_runtime.get("unrealized_pl_value")),
    )
    if latest_pnl_classification == "negative":
        return LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE
    if latest_pnl_classification == "flat":
        return LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT
    if latest_pnl_classification == "positive":
        return LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE
    if latest_pnl_classification == "unavailable":
        return LIVE_MICRO_REPEATABILITY_REPAIR_REQUIRED
    return LIVE_MICRO_REPEATABILITY_LEDGER_READY


def _safe_next_action(
    status: str,
    runtime_summary: dict[str, Any] | None,
) -> str:
    if status == LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS:
        return "Add another redacted evidence snapshot, then rerun repeatability ledger."
    if status == LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED:
        return (
            "Stop and resolve forbidden endpoint/action flags before next supervised review."
        )
    if status == LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED:
        return "Stop and investigate live execution or movement flags before continuing."
    if status == LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING:
        return "Re-run evidence review with full SL/TP observations and compare again."
    if status == LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE:
        return "Capture a later snapshot to confirm whether P/L recovers or degrades."
    if status == LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT:
        return "Capture a later snapshot to test if any movement develops."
    if status == LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE:
        return "Proceed to supervised repeatability decision with preserved snapshots."
    if status == LIVE_MICRO_REPEATABILITY_LEDGER_READY:
        return (
            "Proceed to supervised repeatability decision and prepare manual execution permission."
        )
    if status == LIVE_MICRO_REPEATABILITY_REPAIR_REQUIRED:
        return "Repair snapshot payload fields (P/L classification unavailable) and rerun."
    return "Repair evidence snapshot payload and rerun ledger."


def _coerce_pnl_classification(
    raw: Any,
    pnl: float | int | None,
) -> str:
    raw_str = str(raw).strip().lower()
    if raw_str in {"positive", "flat", "negative"}:
        return raw_str
    if pnl is None:
        return "unavailable"
    if pnl > 0:
        return "positive"
    if pnl < 0:
        return "negative"
    return "flat"


def _extract_fingerprints(runtime: Mapping[str, Any]) -> list[str]:
    fingerprints: list[str] = []
    for key in (
        "trade_fingerprints",
        "position_fingerprints",
        "sl_fingerprint",
        "tp_fingerprint",
        "trailing_sl_fingerprint",
    ):
        if key not in runtime:
            continue
        value = runtime[key]
        if isinstance(value, list):
            for item in value:
                fp = _as_fingerprint(item)
                if fp:
                    fingerprints.append(fp)
        else:
            fp = _as_fingerprint(value)
            if fp:
                fingerprints.append(fp)
    return fingerprints


def _as_fingerprint(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text.startswith("sha256:"):
        return None
    if not _is_valid_sha256_fingerprint(text):
        return None
    return text


def _is_valid_sha256_fingerprint(value: str) -> bool:
    return bool(
        re.fullmatch(
            r"sha256:[0-9a-f]{64}",
            value.lower().strip(),
        ),
    )


def _snapshot_fingerprint(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        _normalize_for_fingerprint(payload),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _normalize_for_fingerprint(payload: Mapping[str, Any]) -> dict[str, Any]:
    copy = dict(payload)
    copy.pop("input", None)
    copy.pop("runtime_summary", None)
    copy.pop("result", None)
    return copy

def _coerce_float(value: Any) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("state payload is not a dict")
    return payload


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _build_report(payload: Mapping[str, Any]) -> str:
    input_payload = payload["input"]
    result = payload["result"]
    runtime_summary = payload["runtime_summary"]
    blockers = "\n".join(f"- {item}" for item in result["blockers"]) or "- none"
    return (
        "# AIOS Forex Live Micro Repeatability Evidence Ledger V1\n\n"
        "## Purpose\n"
        "Local-only repeatability evidence ledger that compares redacted read-only snapshots. "
        "This packet does not place trades and does not send orders.\n\n"
        "## Input\n"
        f"- evidence_state_paths: {input_payload.get('evidence_state_paths')}\n"
        f"- evidence_files_found: {input_payload.get('evidence_files_found')}\n"
        f"- evidence_files_missing: {input_payload.get('evidence_files_missing')}\n"
        f"- local_only: {input_payload.get('local_only')}\n"
        f"- broker_api_called: {input_payload.get('broker_api_called')}\n"
        f"- bitwarden_called: {input_payload.get('bitwarden_called')}\n"
        f"- order_endpoint_called: {input_payload.get('order_endpoint_called')}\n"
        f"- post_request_called: {input_payload.get('post_request_called')}\n"
        f"- trade_close_called: {input_payload.get('trade_close_called')}\n"
        f"- position_close_called: {input_payload.get('position_close_called')}\n"
        f"- live_order_execution: {input_payload.get('live_order_execution')}\n"
        f"- demo_order_execution: {input_payload.get('demo_order_execution')}\n"
        f"- money_movement: {input_payload.get('money_movement')}\n"
        f"- scheduler_started: {input_payload.get('scheduler_started')}\n"
        f"- daemon_started: {input_payload.get('daemon_started')}\n"
        f"- webhook_started: {input_payload.get('webhook_started')}\n\n"
        "## Result\n"
        f"- repeatability_status: {result['repeatability_status']}\n"
        f"- current_stage: {result['current_stage']}\n"
        f"- next_stage: {result['next_stage']}\n"
        f"- safe_next_action: {result['safe_next_action']}\n\n"
        "## Blockers\n"
        f"{blockers}\n\n"
        "## Runtime summary\n"
        f"- snapshot_count: {runtime_summary['snapshot_count']}\n"
        f"- open_trade_seen_count: {runtime_summary['open_trade_seen_count']}\n"
        f"- closed_or_not_visible_count: {runtime_summary['closed_or_not_visible_count']}\n"
        f"- profit_positive_count: {runtime_summary['profit_positive_count']}\n"
        f"- profit_flat_count: {runtime_summary['profit_flat_count']}\n"
        f"- profit_negative_count: {runtime_summary['profit_negative_count']}\n"
        f"- pnl_values: {runtime_summary['pnl_values']}\n"
        f"- latest_pnl_value: {runtime_summary['latest_pnl_value']}\n"
        f"- latest_pnl_classification: {runtime_summary['latest_pnl_classification']}\n"
        f"- sltp_complete_count: {runtime_summary['sltp_complete_count']}\n"
        f"- sltp_missing_count: {runtime_summary['sltp_missing_count']}\n"
        f"- sltp_latest_complete: {runtime_summary['sltp_latest_complete']}\n"
        f"- risk_controls_consistent: {runtime_summary['risk_controls_consistent']}\n"
        f"- forbidden_action_flags_clear: {runtime_summary['forbidden_action_flags_clear']}\n"
        f"- live_execution_flags_clear: {runtime_summary['live_execution_flags_clear']}\n"
        f"- money_movement_clear: {runtime_summary['money_movement_clear']}\n"
        f"- readiness_for_next_supervised_decision: {runtime_summary['readiness_for_next_supervised_decision']}\n"
        f"- evidence_fingerprints: {runtime_summary['evidence_fingerprints']}\n\n"
        "## Classification taxonomy\n"
        f"- {LIVE_MICRO_REPEATABILITY_LEDGER_READY}\n"
        f"- {LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS}\n"
        f"- {LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE}\n"
        f"- {LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT}\n"
        f"- {LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE}\n"
        f"- {LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING}\n"
        f"- {LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED}\n"
        f"- {LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED}\n"
        f"- {LIVE_MICRO_REPEATABILITY_REPAIR_REQUIRED}\n\n"
        "## Safety invariants\n"
        "- No broker API calls.\n"
        "- No Bitwarden reads.\n"
        "- No order POSTs or /orders endpoint use.\n"
        "- No trade/position close calls.\n"
        "- No money movement or live scheduler/daemon/webhook actions.\n\n"
        "## Validation\n"
        "- python -m py_compile scripts/forex_delivery/run_forex_live_micro_repeatability_evidence_ledger_v1.py\n"
        "- python -m pytest tests/forex_engine/test_forex_live_micro_repeatability_evidence_ledger_v1.py -q\n"
        "- python scripts/forex_delivery/run_forex_live_micro_repeatability_evidence_ledger_v1.py\n"
        f"- repeatability_status: {result['repeatability_status']}\n"
        "- safe_next_action: continue only if repeatability status supports supervised progression.\n"
    )


def _write_artifacts(
    payload: Mapping[str, Any],
    state_output: Path,
    report_output: Path,
    *,
    write_report: bool,
) -> dict[str, Any]:
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if write_report:
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(_build_report(payload), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return dict(payload)


def _parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build repeatability evidence ledger from one or more read-only evidence snapshots."
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--evidence-state",
        action="append",
        default=None,
        help="Path to read-only evidence state file. Can be passed multiple times.",
    )
    parser.add_argument(
        "--min-snapshots",
        type=int,
        default=MIN_SNAPSHOTS_DEFAULT,
        help="Minimum snapshot count required for repeatability classification.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write report file.",
    )
    parser.add_argument(
        "--no-report",
        dest="write_report",
        action="store_false",
        help="Do not write report file.",
    )
    parser.set_defaults(write_report=True)
    parser.add_argument(
        "--state-output",
        default=str(DEFAULT_STATE_OUTPUT_PATH),
        help="Path for output JSON state.",
    )
    parser.add_argument(
        "--report-output",
        default=str(DEFAULT_REPORT_OUTPUT_PATH),
        help="Path for output markdown report.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_arguments(argv)
    run_forex_live_micro_repeatability_evidence_ledger_v1(
        evidence_state_paths=[Path(path) for path in args.evidence_state or []],
        min_snapshots=max(0, int(args.min_snapshots)),
        state_output=Path(args.state_output),
        report_output=Path(args.report_output),
        write_report=getattr(args, "write_report", True),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "run_forex_live_micro_repeatability_evidence_ledger_v1",
    "main",
]
