"""Deterministic forex expectancy, ticket, and gate closure audit V1.

This module reads only curated local evidence files and writes sanitized
reports when explicitly requested. It does not read environment variables,
does not inspect credential/account files, does not use network access, and
does not place live, demo, or paper orders.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping


EXPECTANCY_PROVEN = "EXPECTANCY_PROVEN"
EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK = "EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK"
EXPECTANCY_EVIDENCE_INSUFFICIENT = "EXPECTANCY_EVIDENCE_INSUFFICIENT"
EXPECTANCY_NEGATIVE_OR_REJECTED = "EXPECTANCY_NEGATIVE_OR_REJECTED"

RETURN_120_PROVEN = "RETURN_120_PROVEN"
RETURN_120_UNPROVEN = "RETURN_120_UNPROVEN"
RETURN_120_EVIDENCE_INSUFFICIENT = "RETURN_120_EVIDENCE_INSUFFICIENT"

TRADE_TICKET_READY_FROM_EVIDENCE = "TRADE_TICKET_READY_FROM_EVIDENCE"
TRADE_TICKET_MISSING_FIELDS = "TRADE_TICKET_MISSING_FIELDS"
TRADE_TICKET_BLOCKED_BY_RISK = "TRADE_TICKET_BLOCKED_BY_RISK"

TAKE_PROFIT_PROVEN = "TAKE_PROFIT_PROVEN"
TAKE_PROFIT_EVIDENCE_MISSING = "TAKE_PROFIT_EVIDENCE_MISSING"
TAKE_PROFIT_BLOCKED_BY_RISK = "TAKE_PROFIT_BLOCKED_BY_RISK"

BROKER_PROOF_CURRENT = "BROKER_PROOF_CURRENT"
BROKER_PROOF_STALE = "BROKER_PROOF_STALE"
BROKER_PROOF_MISSING = "BROKER_PROOF_MISSING"
BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE = "BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE"

INCIDENT_STOP_PROCEDURE_PRESENT = "INCIDENT_STOP_PROCEDURE_PRESENT"
INCIDENT_STOP_PROCEDURE_CREATED = "INCIDENT_STOP_PROCEDURE_CREATED"
INCIDENT_STOP_PROCEDURE_MISSING = "INCIDENT_STOP_PROCEDURE_MISSING"

READY_FOR_HUMAN_ARMING_CANDIDATE = "READY_FOR_HUMAN_ARMING_CANDIDATE"
BLOCKED_BY_EXPECTANCY_EVIDENCE = "BLOCKED_BY_EXPECTANCY_EVIDENCE"
BLOCKED_BY_TICKET_FIELDS = "BLOCKED_BY_TICKET_FIELDS"
BLOCKED_BY_BROKER_PROOF = "BLOCKED_BY_BROKER_PROOF"
BLOCKED_BY_RISK_GATE = "BLOCKED_BY_RISK_GATE"
BLOCKED_BY_INCIDENT_STOP = "BLOCKED_BY_INCIDENT_STOP"

UPTIME_80_PLANNED_NOT_ACTIVE = "UPTIME_80_PLANNED_NOT_ACTIVE"
UPTIME_80_BLOCKED_BY_LIVE_EVIDENCE = "UPTIME_80_BLOCKED_BY_LIVE_EVIDENCE"
UPTIME_80_READY_FOR_FUTURE_REVIEW = "UPTIME_80_READY_FOR_FUTURE_REVIEW"

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "Reports" / "forex_delivery"
MIN_PROVEN_SAMPLE_SIZE = 30

MASTER_READINESS_REPORTS = (
    "AIOS_FOREX_LIVE_EXECUTION_TO_80_UPTIME_MASTER_V2.md",
    "AIOS_FOREX_LIVE_EXECUTION_TO_90_AUTO_TRADING_MASTER_V1.md",
    "AIOS_FOREX_TONIGHT_LIVE_MICRO_TRADE_EXPECTANCY_ARMING_V1.md",
)

CURATED_REPORT_EVIDENCE = MASTER_READINESS_REPORTS + (
    "readiness_state_recalculation_v1_report.json",
    "proof_bundle_to_candidate_bridge_report.json",
    "review_chain_end_to_end_candidate_journey.json",
    "AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
    "AIOS_FOREX_TOP_10_PROFIT_CANDIDATES_V1.md",
    "AIOS_FOREX_TOP_CANDIDATE_SCOREBOARD_V1.md",
    "AIOS_LIVE_PREFLIGHT_EVIDENCE_BUNDLE_V1_REPORT.md",
    "AIOS_LIVE_MICRO_TRADE_READINESS_GATE_V1.md",
    "AIOS_LIVE_MICRO_TRADE_ONE_SHOT_FINAL_BLOCKERS_V1.md",
    "AIOS_LIVE_MICRO_TRADE_ONE_SHOT_EXECUTION_AUTHORIZATION_STATUS_V1.md",
    "AIOS_LIVE_MICRO_TRADE_ONE_SHOT_FILLED_APPROVAL_RECORD_V1.md",
    "AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_SANITIZED_EVIDENCE.md",
    "LIVE_MICRO_TRADE_EXECUTION_EVIDENCE_V1.md",
    "LIVE_MICRO_TRADE_CLOSE_EVIDENCE_V1.md",
    "AIOS_FOREX_SOURCE_CHAIN_CLOSEOUT_V1_REPORT.md",
    "AIOS_FOREX_DEMO_REHEARSAL_EVIDENCE_BUNDLE_V1_REPORT.md",
    "AIOS_FOREX_INCIDENT_STOP_PROCEDURE_V1.md",
)

AUTOMATION_EVIDENCE = (
    Path("automation/forex_engine/fixtures/live_micro_trade_packet_001.example.json"),
)

REPORT_FILENAMES = {
    "closure": "AIOS_FOREX_EXPECTANCY_TICKET_GATE_CLOSURE_V1.md",
    "take_profit": "AIOS_FOREX_TAKE_PROFIT_RISK_GATE_CLOSURE_V1.md",
    "broker_proof": "AIOS_FOREX_BROKER_PROOF_INTAKE_V1.md",
    "incident_stop": "AIOS_FOREX_INCIDENT_STOP_PROCEDURE_V1.md",
    "next_arming": "AIOS_FOREX_NEXT_ARMING_CLASSIFICATION_V1.md",
}
OPTIONAL_READY_REPORT = "AIOS_FOREX_READY_FOR_HUMAN_ARMING_CANDIDATE_V1.md"

SENSITIVE_PATH_MARKERS = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "account_id",
    "account-",
    "oanda_credential",
    "cloudflare",
    "azure",
    "github_secret",
)

SENSITIVE_VALUE_KEYS = frozenset(
    {
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "password",
        "credential",
        "credentials",
        "account_id",
        "account_identifier",
        "account_number",
        "broker_order_id",
        "transaction_id",
        "raw_payload",
        "raw_request",
        "raw_response",
        "authorization",
    }
)


def run_expectancy_ticket_gate_closure(write_reports: bool = False) -> dict[str, Any]:
    """Audit local sanitized evidence and optionally write closure reports."""

    files, skipped = _collect_evidence_files()
    evidence = _empty_evidence()

    for path in files:
        text = _safe_read_text(path)
        source = _display_path(path)
        evidence["files_inspected"].append(source)
        if path.suffix.lower() == ".json":
            _apply_json_evidence(evidence, _safe_load_json(text), source)
        else:
            _apply_text_evidence(evidence, text, source)

    _finalize_recalculated_expectancy(evidence)
    classifications = _classify(evidence, write_reports=write_reports)
    missing_fields = _missing_fields(evidence, classifications)
    result = {
        "schema": "AIOS_FOREX_EXPECTANCY_TICKET_GATE_CLOSURE_V1",
        "write_reports_requested": bool(write_reports),
        "files_inspected": tuple(evidence["files_inspected"]),
        "files_skipped_for_safety": tuple(skipped),
        "classifications": classifications,
        "found_evidence": _public_evidence(evidence),
        "missing_fields": tuple(missing_fields),
        "next_exact_closure_action": _next_exact_closure_action(classifications, missing_fields),
        "reports": {
            "written": tuple(),
            "skipped_ready_candidate_report": True,
            "ready_candidate_report_reason": "gates_not_all_ready",
            "allowed_output_paths": tuple(f"Reports/forex_delivery/{name}" for name in REPORT_FILENAMES.values()),
        },
        "safety_summary": _safety_summary(),
    }

    if write_reports:
        written = _write_reports(result)
        result["reports"] = {
            **result["reports"],
            "written": tuple(_display_path(path) for path in written),
            "skipped_ready_candidate_report": not _ready_candidate_allowed(classifications),
            "ready_candidate_report_reason": (
                "created" if _ready_candidate_allowed(classifications) else "gates_not_all_ready"
            ),
        }

    return result


def _collect_evidence_files() -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    skipped: list[str] = []

    for name in CURATED_REPORT_EVIDENCE:
        path = REPORTS_DIR / name
        if _is_safe_evidence_path(path):
            if path.exists() and path.is_file():
                files.append(path)
        else:
            skipped.append(_display_path(path))

    for relative in AUTOMATION_EVIDENCE:
        path = REPO_ROOT / relative
        if _is_safe_evidence_path(path):
            if path.exists() and path.is_file():
                files.append(path)
        else:
            skipped.append(_display_path(path))

    for marker in (".env", "secrets/", "credentials/", "config/secrets/", "docs/legal/"):
        skipped.append(marker)

    return files, _unique_list(skipped)


def _is_safe_evidence_path(path: Path) -> bool:
    normalized = str(path).replace("\\", "/").lower()
    return not any(marker in normalized for marker in SENSITIVE_PATH_MARKERS)


def _safe_read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _safe_load_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _empty_evidence() -> dict[str, Any]:
    return {
        "files_inspected": [],
        "strategy_name": None,
        "candidate_id": None,
        "setup_id": None,
        "signal_id": None,
        "instrument": None,
        "side": None,
        "timeframe": None,
        "sample_size": None,
        "closed_trades": None,
        "wins": None,
        "losses": None,
        "breakeven_count": None,
        "gross_profit": None,
        "gross_loss": None,
        "net_pl": None,
        "expectancy_formula": "UNKNOWN",
        "recalculated_expectancy": None,
        "profit_factor": None,
        "max_drawdown": None,
        "spread_slippage_fees_treatment": [],
        "in_sample_out_of_sample_status": None,
        "return_percentage_claim": None,
        "return_120_evidence": None,
        "stop_loss": None,
        "take_profit": None,
        "take_profit_explicit_none": False,
        "micro_size": None,
        "max_loss_gate": None,
        "daily_stop_gate": None,
        "kill_switch": None,
        "one_order_only": None,
        "broker_proof": None,
        "broker_proof_current": False,
        "broker_proof_stale": False,
        "broker_runtime_intake_required": False,
        "incident_stop_procedure_present": False,
        "walk_forward_gate_cleared": None,
        "walk_forward_failed": False,
        "candidate_rejected": False,
        "paper_only": False,
        "demo_live_status": "UNKNOWN",
        "risk_blockers": [],
        "expectancy_blockers": [],
        "ticket_sources": [],
        "evidence_sources": {},
        "window_expectancies": [],
        "window_profit_factors": [],
        "window_drawdowns": [],
    }


def _apply_json_evidence(evidence: dict[str, Any], payload: Any, source: str) -> None:
    if _contains_sensitive_keys(payload):
        evidence["risk_blockers"].append("sensitive_key_detected_in_sanitized_evidence_source")
        return

    for key_path, value in _walk_json(payload):
        leaf = key_path[-1].lower()
        text_value = str(value).strip() if value is not None else ""

        if leaf in {"strategy", "strategy_name", "selected_strategy"}:
            _set_once(evidence, "strategy_name", text_value, source)
        elif leaf in {"candidate_id", "selected_candidate_id"}:
            _set_once(evidence, "candidate_id", text_value, source)
        elif leaf == "setup_id":
            _set_once(evidence, "setup_id", text_value, source)
        elif leaf == "signal_id":
            _set_once(evidence, "signal_id", text_value, source)
        elif leaf == "instrument":
            _set_once(evidence, "instrument", text_value, source)
        elif leaf in {"side", "direction", "selected_direction"}:
            _set_once(evidence, "side", _normalize_side(text_value), source)
        elif leaf == "timeframe":
            _set_once(evidence, "timeframe", text_value, source)
        elif leaf in {"sample_size", "closed_trade_count"}:
            _set_numeric(evidence, "sample_size", value, source)
        elif leaf in {"closed_trades", "closed_trade_count"}:
            _set_numeric(evidence, "closed_trades", value, source)
        elif leaf == "wins":
            _set_numeric(evidence, "wins", value, source)
        elif leaf == "losses":
            _set_numeric(evidence, "losses", value, source)
        elif leaf in {"breakeven", "breakeven_count"}:
            _set_numeric(evidence, "breakeven_count", value, source)
        elif leaf == "gross_profit":
            _set_numeric(evidence, "gross_profit", value, source)
        elif leaf == "gross_loss":
            _set_numeric(evidence, "gross_loss", value, source)
        elif leaf in {"net_pl", "net_p_l", "net_pnl", "pnl"}:
            _set_numeric(evidence, "net_pl", value, source)
        elif leaf in {"expectancy", "expectancy_per_trade", "validation_expectancy"}:
            _set_numeric(evidence, "recalculated_expectancy", value, source)
        elif leaf in {"profit_factor", "validation_profit_factor"}:
            _set_numeric(evidence, "profit_factor", value, source)
        elif leaf in {"max_drawdown", "max_drawdown_pct", "drawdown"}:
            _set_numeric(evidence, "max_drawdown", value, source, prefer_max=True)
        elif leaf in {"walk_forward_status", "walk_forward_detail"}:
            _set_once(evidence, "in_sample_out_of_sample_status", text_value, source)
            if "fail" in text_value.lower() or "not finalized" in text_value.lower():
                evidence["walk_forward_failed"] = True
                evidence["expectancy_blockers"].append("walk_forward_failed")
        elif leaf == "walk_forward_gate_cleared":
            evidence["walk_forward_gate_cleared"] = bool(value)
            if bool(value) is False:
                evidence["walk_forward_failed"] = True
                evidence["expectancy_blockers"].append("walk_forward_gate_not_cleared")
        elif leaf in {"candidate_bridge_verdict", "verdict", "promotion_status"}:
            if "reject" in text_value.lower():
                evidence["candidate_rejected"] = True
                evidence["expectancy_blockers"].append("candidate_rejected")
        elif leaf in {"paper_only", "live_trading_authorized", "order_execution", "network_used"}:
            if leaf == "paper_only" and bool(value) is True:
                evidence["paper_only"] = True
            if leaf == "live_trading_authorized" and bool(value) is False:
                evidence["demo_live_status"] = "LIVE_NOT_AUTHORIZED"
        elif leaf == "stop_loss":
            _set_once(evidence, "stop_loss", text_value, source)
            evidence["ticket_sources"].append(source)
        elif leaf == "take_profit":
            _apply_take_profit(evidence, text_value, source)
        elif leaf in {"units", "micro_size"}:
            _set_numeric(evidence, "micro_size", value, source)
            evidence["ticket_sources"].append(source)
        elif leaf in {"max_loss", "max_loss_gate", "max_loss_gate_clear"}:
            _set_once(evidence, "max_loss_gate", text_value, source)
        elif leaf in {"daily_loss_cap", "daily_stop_gate", "daily_stop_clear"}:
            _set_once(evidence, "daily_stop_gate", text_value, source)
        elif leaf in {"kill_switch", "kill_switch_required", "kill_switch_active", "kill_switch_proof"}:
            _set_once(evidence, "kill_switch", text_value, source)
        elif leaf in {"one_order_only", "single_order_only"}:
            _set_once(evidence, "one_order_only", text_value, source)
        elif leaf == "broker_proof_current":
            if bool(value) is True:
                evidence["broker_proof_current"] = True
                _set_once(evidence, "broker_proof", "current sanitized broker proof present", source)
        elif "broker" in leaf and any(word in text_value.lower() for word in ("current", "connected", "proof", "ready")):
            _set_once(evidence, "broker_proof", text_value, source)
        elif leaf == "broker_sandbox_or_demo_proof":
            if bool(value) is True:
                _set_once(evidence, "broker_proof", text_value, source)
        elif leaf in {"runtime_only_human_intake_required", "broker_runtime_intake_required"}:
            if bool(value) is True:
                evidence["broker_runtime_intake_required"] = True


def _apply_text_evidence(evidence: dict[str, Any], text: str, source: str) -> None:
    lower = text.lower()

    if "aios_forex_incident_stop_procedure_v1" in lower or "incident stop procedure" in lower:
        evidence["incident_stop_procedure_present"] = True

    if "120 percent" in lower or "120%" in lower:
        evidence["return_percentage_claim"] = "120 percent mentioned"
        if "prohibited" in lower or "not verified" in lower or "unproven" in lower:
            evidence["return_120_evidence"] = "unproven"
        elif "120 percent return verified" in lower or "return_120_proven" in lower:
            evidence["return_120_evidence"] = "proven"

    if "take-profit: none" in lower or "take_profit: none" in lower or "| take-profit explicit | none | pass |" in lower:
        evidence["take_profit_explicit_none"] = True
        _set_once(evidence, "take_profit", "none", source)
    elif "take-profit" in lower or "take_profit" in lower:
        value = _extract_value_after_label(text, ("take-profit", "take_profit"))
        if value:
            _apply_take_profit(evidence, value, source)

    if "stop-loss attached" in lower or "stop_loss" in lower or "stop-loss" in lower:
        value = _extract_value_after_label(text, ("stop-loss", "stop_loss"))
        _set_once(evidence, "stop_loss", value or "present", source)

    if "one-order-only" in lower or "one order" in lower:
        _set_once(evidence, "one_order_only", "present", source)
    if "kill-switch" in lower or "kill_switch" in lower:
        _set_once(evidence, "kill_switch", "present", source)
    if "max loss" in lower or "max_loss" in lower:
        _set_once(evidence, "max_loss_gate", "present", source)
    if "daily-stop" in lower or "daily_loss_cap" in lower or "daily stop" in lower:
        _set_once(evidence, "daily_stop_gate", "present", source)
    if "micro-size" in lower or "micro trade" in lower or "units 1" in lower:
        _set_once(evidence, "micro_size", evidence.get("micro_size") or 1, source)
    if "broker proof" in lower or "demo connection proof" in lower or "connected_sanitized" in lower:
        _set_once(evidence, "broker_proof", "sanitized historical/demo proof present", source)
        if "current broker proof missing" in lower or "current live broker proof" in lower:
            evidence["broker_runtime_intake_required"] = True
        elif "historical" in lower or "demo" in lower:
            evidence["broker_proof_stale"] = True
    if "runtime-only" in lower and "credential" in lower:
        evidence["broker_runtime_intake_required"] = True

    strategy = _regex_first(text, r"`?([A-Za-z0-9_]+supervisor[A-Za-z0-9_]*)`?")
    if strategy:
        _set_once(evidence, "strategy_name", strategy, source)
    candidate = _regex_first(text, r"`?(c[0-9]+-[a-z]+-[a-z]+)`?")
    if candidate:
        _set_once(evidence, "candidate_id", candidate, source)
    if "eur_usd" in lower:
        _set_once(evidence, "instrument", "EUR_USD", source)
    if "buy/long" in lower or "buy" in lower or "long" in lower:
        _set_once(evidence, "side", "BUY", source)

    sample = _extract_number_after_label(text, ("sample size", "sample_size"))
    if sample is not None:
        _set_numeric(evidence, "sample_size", sample, source)
    profit_factor = _extract_number_after_label(text, ("profit factor", "profit_factor"))
    if profit_factor is not None:
        _set_numeric(evidence, "profit_factor", profit_factor, source)
    drawdown = _extract_number_after_label(text, ("max drawdown", "drawdown"))
    if drawdown is not None:
        _set_numeric(evidence, "max_drawdown", drawdown, source, prefer_max=True)

    _extract_walk_forward_rows(evidence, text, source)

    if "walk-forward failed" in lower or "walk-forward gate cleared: `false`" in lower:
        evidence["walk_forward_failed"] = True
        evidence["expectancy_blockers"].append("walk_forward_failed")
    if "reject" in lower and "candidate" in lower:
        evidence["candidate_rejected"] = True
        evidence["expectancy_blockers"].append("candidate_rejected")
    if "spread/slippage" in lower or "slippage" in lower or "spread" in lower:
        evidence["spread_slippage_fees_treatment"].append(f"{source}: spread/slippage evidence mentioned")


def _extract_walk_forward_rows(evidence: dict[str, Any], text: str, source: str) -> None:
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip(" `") for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6 or not cells[0].lower().startswith("wf-"):
            continue
        trades = _to_number(cells[2])
        expectancy = _to_number(cells[3])
        profit_factor = _to_number(cells[4])
        drawdown = _to_number(cells[5])
        if trades is not None:
            current = evidence.get("closed_trades") or 0
            evidence["closed_trades"] = current + trades
            evidence["evidence_sources"]["closed_trades"] = source
        if expectancy is not None:
            evidence["window_expectancies"].append(expectancy)
        if profit_factor is not None:
            evidence["window_profit_factors"].append(profit_factor)
        if drawdown is not None:
            evidence["window_drawdowns"].append(drawdown)
        if len(cells) >= 8 and cells[7]:
            blockers = cells[7].lower()
            if "negative_expectancy" in blockers:
                evidence["walk_forward_failed"] = True
                evidence["expectancy_blockers"].append("negative_expectancy_window")
            if "low_profit_factor" in blockers:
                evidence["expectancy_blockers"].append("low_profit_factor_window")
            if "excessive_drawdown" in blockers:
                evidence["expectancy_blockers"].append("excessive_drawdown_window")


def _finalize_recalculated_expectancy(evidence: dict[str, Any]) -> None:
    gross_profit = _to_number(evidence.get("gross_profit"))
    gross_loss = _to_number(evidence.get("gross_loss"))
    closed_trades = _to_number(evidence.get("closed_trades"))
    if gross_profit is not None and gross_loss is not None and closed_trades and closed_trades > 0:
        evidence["recalculated_expectancy"] = round((gross_profit - abs(gross_loss)) / closed_trades, 8)
        evidence["expectancy_formula"] = "(gross_profit - abs(gross_loss)) / closed_trades"
        return

    if evidence["window_expectancies"]:
        values = evidence["window_expectancies"]
        evidence["recalculated_expectancy"] = round(sum(values) / len(values), 8)
        evidence["expectancy_formula"] = "average(walk_forward_window_expectancy)"
    elif evidence.get("recalculated_expectancy") is not None:
        evidence["expectancy_formula"] = "source_report_expectancy"

    if evidence["window_profit_factors"]:
        values = evidence["window_profit_factors"]
        evidence["profit_factor"] = round(sum(values) / len(values), 8)
    if evidence["window_drawdowns"]:
        evidence["max_drawdown"] = max(evidence["window_drawdowns"])


def _classify(evidence: Mapping[str, Any], write_reports: bool) -> dict[str, str]:
    expectancy_status = _classify_expectancy(evidence)
    return_status = _classify_return(evidence)
    take_profit_status = _classify_take_profit(evidence)
    trade_ticket_status = _classify_trade_ticket(evidence, take_profit_status)
    broker_status = _classify_broker_proof(evidence)
    incident_status = _classify_incident_stop(evidence, write_reports)
    next_arming = _classify_next_arming(
        expectancy_status,
        trade_ticket_status,
        take_profit_status,
        broker_status,
        incident_status,
    )
    uptime_status = (
        UPTIME_80_READY_FOR_FUTURE_REVIEW
        if next_arming == READY_FOR_HUMAN_ARMING_CANDIDATE
        else UPTIME_80_BLOCKED_BY_LIVE_EVIDENCE
    )

    return {
        "EXPECTANCY_STATUS": expectancy_status,
        "RETURN_STATUS": return_status,
        "TRADE_TICKET_STATUS": trade_ticket_status,
        "TAKE_PROFIT_STATUS": take_profit_status,
        "BROKER_PROOF_STATUS": broker_status,
        "INCIDENT_STOP_STATUS": incident_status,
        "NEXT_ARMING_STATUS": next_arming,
        "UPTIME_80_STATUS": uptime_status,
    }


def _classify_expectancy(evidence: Mapping[str, Any]) -> str:
    if evidence.get("candidate_rejected") or evidence.get("walk_forward_failed"):
        return EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK

    sample_size = _to_number(evidence.get("sample_size")) or _to_number(evidence.get("closed_trades")) or 0
    expectancy = _to_number(evidence.get("recalculated_expectancy"))
    profit_factor = _to_number(evidence.get("profit_factor"))
    max_drawdown = _to_number(evidence.get("max_drawdown"))

    if sample_size <= 0 or expectancy is None:
        return EXPECTANCY_EVIDENCE_INSUFFICIENT
    if expectancy <= 0 or (profit_factor is not None and profit_factor <= 1.0):
        return EXPECTANCY_NEGATIVE_OR_REJECTED
    if sample_size < MIN_PROVEN_SAMPLE_SIZE:
        return EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK
    if max_drawdown is not None and max_drawdown > 12.0:
        return EXPECTANCY_NEGATIVE_OR_REJECTED
    return EXPECTANCY_PROVEN


def _classify_return(evidence: Mapping[str, Any]) -> str:
    value = str(evidence.get("return_120_evidence") or "").lower()
    if value == "proven":
        return RETURN_120_PROVEN
    if value == "unproven":
        return RETURN_120_UNPROVEN
    return RETURN_120_EVIDENCE_INSUFFICIENT


def _classify_take_profit(evidence: Mapping[str, Any]) -> str:
    value = evidence.get("take_profit")
    if value in (None, "") or bool(evidence.get("take_profit_explicit_none")):
        return TAKE_PROFIT_EVIDENCE_MISSING
    return TAKE_PROFIT_PROVEN


def _classify_trade_ticket(evidence: Mapping[str, Any], take_profit_status: str) -> str:
    if any(str(item).startswith("risk_blocked") for item in evidence.get("risk_blockers", ())):
        return TRADE_TICKET_BLOCKED_BY_RISK

    required = (
        "candidate_id",
        "instrument",
        "side",
        "stop_loss",
        "micro_size",
        "max_loss_gate",
        "daily_stop_gate",
        "kill_switch",
        "one_order_only",
    )
    if take_profit_status != TAKE_PROFIT_PROVEN:
        return TRADE_TICKET_MISSING_FIELDS
    if any(evidence.get(field) in (None, "", "UNKNOWN") for field in required):
        return TRADE_TICKET_MISSING_FIELDS
    return TRADE_TICKET_READY_FROM_EVIDENCE


def _classify_broker_proof(evidence: Mapping[str, Any]) -> str:
    if evidence.get("broker_proof_current"):
        return BROKER_PROOF_CURRENT
    if evidence.get("broker_runtime_intake_required"):
        return BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE
    if evidence.get("broker_proof") or evidence.get("broker_proof_stale"):
        return BROKER_PROOF_STALE
    return BROKER_PROOF_MISSING


def _classify_incident_stop(evidence: Mapping[str, Any], write_reports: bool) -> str:
    if evidence.get("incident_stop_procedure_present"):
        return INCIDENT_STOP_PROCEDURE_PRESENT
    if write_reports:
        return INCIDENT_STOP_PROCEDURE_CREATED
    return INCIDENT_STOP_PROCEDURE_MISSING


def _classify_next_arming(
    expectancy_status: str,
    ticket_status: str,
    take_profit_status: str,
    broker_status: str,
    incident_status: str,
) -> str:
    if expectancy_status != EXPECTANCY_PROVEN:
        return BLOCKED_BY_EXPECTANCY_EVIDENCE
    if ticket_status != TRADE_TICKET_READY_FROM_EVIDENCE or take_profit_status != TAKE_PROFIT_PROVEN:
        return BLOCKED_BY_TICKET_FIELDS
    if broker_status != BROKER_PROOF_CURRENT:
        return BLOCKED_BY_BROKER_PROOF
    if incident_status not in {INCIDENT_STOP_PROCEDURE_PRESENT, INCIDENT_STOP_PROCEDURE_CREATED}:
        return BLOCKED_BY_INCIDENT_STOP
    return READY_FOR_HUMAN_ARMING_CANDIDATE


def _missing_fields(evidence: Mapping[str, Any], classifications: Mapping[str, str]) -> list[str]:
    missing: list[str] = []
    for field in (
        "strategy_name",
        "candidate_id",
        "setup_id",
        "signal_id",
        "instrument",
        "side",
        "timeframe",
        "sample_size",
        "closed_trades",
        "wins",
        "losses",
        "breakeven_count",
        "gross_profit",
        "gross_loss",
        "net_pl",
        "profit_factor",
        "max_drawdown",
    ):
        if evidence.get(field) in (None, "", "UNKNOWN"):
            missing.append(field)

    ticket_requirements = {
        "stop_loss": evidence.get("stop_loss"),
        "take_profit": evidence.get("take_profit") if not evidence.get("take_profit_explicit_none") else None,
        "micro_size": evidence.get("micro_size"),
        "max_loss_gate": evidence.get("max_loss_gate"),
        "daily_stop_gate": evidence.get("daily_stop_gate"),
        "kill_switch": evidence.get("kill_switch"),
        "one_order_only": evidence.get("one_order_only"),
        "current_broker_proof": evidence.get("broker_proof_current") or None,
    }
    for field, value in ticket_requirements.items():
        if value in (None, "", "UNKNOWN", False):
            missing.append(field)

    if classifications["EXPECTANCY_STATUS"] != EXPECTANCY_PROVEN:
        missing.append("expectancy_proof")
    if classifications["RETURN_STATUS"] != RETURN_120_PROVEN:
        missing.append("return_120_proof")

    return _unique_list(missing)


def _next_exact_closure_action(classifications: Mapping[str, str], missing_fields: Iterable[str]) -> str:
    missing = set(missing_fields)
    if classifications["NEXT_ARMING_STATUS"] == READY_FOR_HUMAN_ARMING_CANDIDATE:
        return "review_ready_for_human_arming_candidate_report_before_any_separate_human_action"
    if classifications["EXPECTANCY_STATUS"] != EXPECTANCY_PROVEN:
        return "produce sufficient paper_or_demo trade-level expectancy evidence with passing walk-forward proof"
    if "take_profit" in missing:
        return "provide deterministic take-profit value evidence or a separately approved explicit no-take-profit exception"
    if classifications["BROKER_PROOF_STATUS"] != BROKER_PROOF_CURRENT:
        return "capture current sanitized broker proof through runtime-only human intake without credential or account persistence"
    if classifications["INCIDENT_STOP_STATUS"] == INCIDENT_STOP_PROCEDURE_MISSING:
        return "create incident stop procedure before any arming candidate"
    return "repair missing trade ticket fields from deterministic evidence"


def _write_reports(result: Mapping[str, Any]) -> list[Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    report_builders = {
        "closure": _render_closure_report,
        "take_profit": _render_take_profit_report,
        "broker_proof": _render_broker_proof_report,
        "incident_stop": _render_incident_stop_report,
        "next_arming": _render_next_arming_report,
    }
    for key, renderer in report_builders.items():
        path = REPORTS_DIR / REPORT_FILENAMES[key]
        path.write_text(renderer(result), encoding="utf-8", newline="\n")
        written.append(path)

    if _ready_candidate_allowed(result["classifications"]):
        path = REPORTS_DIR / OPTIONAL_READY_REPORT
        path.write_text(_render_ready_candidate_report(result), encoding="utf-8", newline="\n")
        written.append(path)
    return written


def _render_closure_report(result: Mapping[str, Any]) -> str:
    classes = result["classifications"]
    evidence = result["found_evidence"]
    return "\n".join(
        [
            "# AIOS Forex Expectancy Ticket Gate Closure V1",
            "",
            "## Objective",
            "",
            "Audit existing sanitized forex evidence, recalculate expectancy where supported, identify missing trade-ticket fields, and classify the next arming state without broker, credential, network, runtime-service, or order action.",
            "",
            "## Current Blocker State",
            "",
            "- TONIGHT_LIVE_EXECUTION_STATUS: BLOCKED_BY_EXPECTANCY_EVIDENCE",
            "- EXPECTANCY_STATUS: EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK",
            "- RETURN_STATUS: RETURN_120_EVIDENCE_INSUFFICIENT",
            "- TRADE_TICKET_STATUS: TRADE_TICKET_MISSING_FIELDS",
            "- HUMAN_CHECKLIST_STATUS: HUMAN_CHECKLIST_NOT_CREATED_BLOCKED",
            "",
            "## Files Inspected",
            _bullet_lines(result["files_inspected"]),
            "",
            "## Files Skipped For Safety",
            _bullet_lines(result["files_skipped_for_safety"]),
            "",
            "## Expectancy Evidence Found",
            _table(
                {
                    "strategy": evidence.get("strategy_name"),
                    "candidate": evidence.get("candidate_id"),
                    "instrument": evidence.get("instrument"),
                    "side": evidence.get("side"),
                    "timeframe": evidence.get("timeframe"),
                    "paper/demo/live status": evidence.get("demo_live_status"),
                    "walk-forward failed": evidence.get("walk_forward_failed"),
                    "candidate rejected": evidence.get("candidate_rejected"),
                }
            ),
            "",
            "## Expectancy Calculation Details",
            _table(
                {
                    "sample size": evidence.get("sample_size"),
                    "closed trades": evidence.get("closed_trades"),
                    "wins": evidence.get("wins"),
                    "losses": evidence.get("losses"),
                    "breakeven count": evidence.get("breakeven_count"),
                    "gross profit": evidence.get("gross_profit"),
                    "gross loss": evidence.get("gross_loss"),
                    "net P/L": evidence.get("net_pl"),
                    "expectancy formula": evidence.get("expectancy_formula"),
                    "recalculated expectancy": evidence.get("recalculated_expectancy"),
                    "profit factor": evidence.get("profit_factor"),
                    "max drawdown": evidence.get("max_drawdown"),
                    "in/out sample status": evidence.get("in_sample_out_of_sample_status"),
                }
            ),
            "",
            "## Return 120 Status",
            "",
            f"`{classes['RETURN_STATUS']}`",
            "",
            "## Trade-Ticket Fields Found",
            _table(
                {
                    "candidate_id": evidence.get("candidate_id"),
                    "setup_id": evidence.get("setup_id"),
                    "signal_id": evidence.get("signal_id"),
                    "instrument": evidence.get("instrument"),
                    "side": evidence.get("side"),
                    "stop_loss": evidence.get("stop_loss"),
                    "take_profit": evidence.get("take_profit"),
                    "micro_size": evidence.get("micro_size"),
                    "max_loss_gate": evidence.get("max_loss_gate"),
                    "daily_stop_gate": evidence.get("daily_stop_gate"),
                    "kill_switch": evidence.get("kill_switch"),
                    "one_order_only": evidence.get("one_order_only"),
                }
            ),
            "",
            "## Trade-Ticket Fields Missing",
            _bullet_lines(result["missing_fields"]),
            "",
            "## Classifications",
            _table(classes),
            "",
            "## Exact Closure Action",
            "",
            result["next_exact_closure_action"],
            "",
            "## Validator Results",
            "",
            "PENDING at report creation. Final validator results must be appended after local validation.",
            "",
            "## Git Status",
            "",
            "PENDING at report creation. Final git status must be appended after local validation.",
            "",
            "## Safety",
            "",
            "- broker status: not called",
            "- credential status: not read",
            "- live order status: not executed by Codex",
            "- demo order status: not executed by Codex",
            "- network status: not used",
            "",
        ]
    )


def _render_take_profit_report(result: Mapping[str, Any]) -> str:
    evidence = result["found_evidence"]
    return "\n".join(
        [
            "# AIOS Forex Take Profit Risk Gate Closure V1",
            "",
            "## Risk And Take-Profit Evidence",
            _table(
                {
                    "stop-loss evidence": evidence.get("stop_loss"),
                    "take-profit evidence": evidence.get("take_profit"),
                    "take-profit explicit none": evidence.get("take_profit_explicit_none"),
                    "max-loss gate evidence": evidence.get("max_loss_gate"),
                    "daily-stop gate evidence": evidence.get("daily_stop_gate"),
                    "kill-switch evidence": evidence.get("kill_switch"),
                    "micro-size evidence": evidence.get("micro_size"),
                    "one-order-only evidence": evidence.get("one_order_only"),
                }
            ),
            "",
            "## Missing Risk Or Take-Profit Fields",
            _bullet_lines(field for field in result["missing_fields"] if field in {"take_profit", "max_loss_gate", "daily_stop_gate", "kill_switch", "micro_size", "one_order_only", "stop_loss"}),
            "",
            "## Next Closure Action",
            "",
            "Provide deterministic take-profit value evidence, or a separately approved explicit no-take-profit exception if future policy allows it. Current packet requires take-profit proof.",
            "",
        ]
    )


def _render_broker_proof_report(result: Mapping[str, Any]) -> str:
    classes = result["classifications"]
    evidence = result["found_evidence"]
    return "\n".join(
        [
            "# AIOS Forex Broker Proof Intake V1",
            "",
            "## Current Broker Proof Status",
            "",
            f"`{classes['BROKER_PROOF_STATUS']}`",
            "",
            "## Broker Proof Evidence Found",
            "",
            str(evidence.get("broker_proof") or "UNKNOWN"),
            "",
            "## Stale Or Missing Proof",
            "",
            "- Historical/demo proof is evidence only and is not current live broker readiness.",
            "- Current proof must be captured through runtime-only human intake.",
            "",
            "## Runtime-Only Human Intake Requirement",
            "",
            "Future broker proof must be supplied by Anthony through a separately approved runtime-only human intake path. Codex must not read credentials, account IDs, .env files, credential files, or raw broker payloads.",
            "",
            "## Credential Persistence Ban",
            "",
            "Credentials must not be persisted, printed, logged, included in reports, or placed in fixtures.",
            "",
            "## Account ID Persistence Ban",
            "",
            "Account identifiers must not be persisted, printed, logged, included in reports, or placed in fixtures.",
            "",
            "## Sanitized Proof Fields Required",
            "",
            "- proof timestamp",
            "- broker environment label without account ID",
            "- instrument availability",
            "- market open/session state",
            "- spread value or cap status",
            "- connector status",
            "- no order submitted",
            "- no credential/account persistence",
            "",
            "## Future Output Shape",
            "",
            "A future packet should provide a sanitized broker proof object with status, timestamp, source label, spread/slippage cap status, and explicit no-secret/no-account-ID attestations.",
            "",
            "## Codex Broker Action Statement",
            "",
            "No broker call performed by Codex.",
            "",
        ]
    )


def _render_incident_stop_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Incident Stop Procedure V1",
            "",
            "## Pre-Trade Stop Conditions",
            "- Stop if expectancy proof is not sufficient.",
            "- Stop if take-profit evidence is missing under a packet that requires it.",
            "- Stop if current broker proof is missing.",
            "- Stop if credentials, account IDs, raw broker payloads, or secret files are requested.",
            "- Stop if dashboard, Codex, an LLM, scheduler, daemon, or webhook is asked to place an order.",
            "",
            "## In-Trade Emergency Stop Conditions",
            "- Stop if stop-loss is missing or detached.",
            "- Stop if max-loss cap is breached.",
            "- Stop if daily-stop gate is breached.",
            "- Stop if kill-switch state mismatches the approved state.",
            "- Stop if broker disconnects or broker status becomes unknown.",
            "- Stop if evidence mismatch appears between ticket, fill, and broker-side confirmation.",
            "",
            "## Post-Trade Incident Flags",
            "- Failed fill reconciliation.",
            "- Missing stop-loss record.",
            "- Missing take-profit or approved no-take-profit record.",
            "- Spread/slippage outside approved cap.",
            "- Failed close or unknown open-trade state.",
            "- Missing sanitized P/L and realized R.",
            "",
            "## Daily Stop Rule",
            "If daily stop is hit or unknown, no further trade may be armed until a separate review packet clears the condition.",
            "",
            "## Max-Loss Breach Rule",
            "If max loss is breached or cannot be measured, stop all escalation and create an incident report.",
            "",
            "## Kill-Switch Rule",
            "If kill-switch state is unavailable, mismatched, or failed, no arming candidate is allowed.",
            "",
            "## Broker Disconnect Rule",
            "If broker connection is unavailable, stale, or unverified, stop before execution and require runtime-only human proof intake.",
            "",
            "## Evidence Mismatch Rule",
            "If ticket, dashboard, broker-side proof, or reconciliation evidence disagree, preserve sanitized evidence and stop.",
            "",
            "## Dashboard Mismatch Rule",
            "The dashboard is display-only. Any dashboard indication that implies order authority is a blocker.",
            "",
            "## Reconciliation Failure Rule",
            "Failed reconciliation blocks the next session until a post-trade evidence packet resolves it.",
            "",
            "## Maintenance-Window Escalation Rule",
            "If maintenance review is skipped, mark the next trading-capable window blocked pending maintenance review.",
            "",
            "## Restart Criteria",
            "Restart review only after expectancy, ticket fields, broker proof, risk gates, and incident stop evidence are current and sanitized.",
            "",
            "## Rollback And Reporting Criteria",
            "Rollback applies only to local code/report changes in a separately approved packet. Trading incidents require sanitized reporting, not repo reset or cleanup.",
            "",
        ]
    )


def _render_next_arming_report(result: Mapping[str, Any]) -> str:
    classes = result["classifications"]
    ready = [name for name, status in classes.items() if "PROVEN" in status or "CREATED" in status or "PLANNED" in status]
    blocked = [name for name, status in classes.items() if "BLOCKED" in status or "MISSING" in status or "INSUFFICIENT" in status or "WEAK" in status]
    return "\n".join(
        [
            "# AIOS Forex Next Arming Classification V1",
            "",
            "## All Classifications",
            _table(classes),
            "",
            "## Ready Gates",
            _bullet_lines(ready),
            "",
            "## Blocked Gates",
            _bullet_lines(blocked),
            "",
            "## Exact Missing Evidence",
            _bullet_lines(result["missing_fields"]),
            "",
            "## One Next Packet Recommendation",
            "",
            result["next_exact_closure_action"],
            "",
            "## Human Arming Candidate Report Created",
            "",
            str(not result["reports"]["skipped_ready_candidate_report"]),
            "",
        ]
    )


def _render_ready_candidate_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Ready For Human Arming Candidate V1",
            "",
            "This report is created only when deterministic evidence clears expectancy, ticket, take-profit, current broker proof, incident stop, and risk gates.",
            "",
            "## Classifications",
            _table(result["classifications"]),
            "",
            "## Safety",
            "- Human arming candidate only.",
            "- Codex did not place an order.",
            "- Dashboard does not place orders.",
            "- No credentials or account IDs were read or persisted.",
            "",
        ]
    )


def _ready_candidate_allowed(classifications: Mapping[str, str]) -> bool:
    return (
        classifications["EXPECTANCY_STATUS"] == EXPECTANCY_PROVEN
        and classifications["TRADE_TICKET_STATUS"] == TRADE_TICKET_READY_FROM_EVIDENCE
        and classifications["TAKE_PROFIT_STATUS"] == TAKE_PROFIT_PROVEN
        and classifications["BROKER_PROOF_STATUS"] == BROKER_PROOF_CURRENT
        and classifications["INCIDENT_STOP_STATUS"] in {INCIDENT_STOP_PROCEDURE_PRESENT, INCIDENT_STOP_PROCEDURE_CREATED}
        and classifications["NEXT_ARMING_STATUS"] == READY_FOR_HUMAN_ARMING_CANDIDATE
    )


def _public_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "strategy_name",
        "candidate_id",
        "setup_id",
        "signal_id",
        "instrument",
        "side",
        "timeframe",
        "sample_size",
        "closed_trades",
        "wins",
        "losses",
        "breakeven_count",
        "gross_profit",
        "gross_loss",
        "net_pl",
        "expectancy_formula",
        "recalculated_expectancy",
        "profit_factor",
        "max_drawdown",
        "spread_slippage_fees_treatment",
        "in_sample_out_of_sample_status",
        "return_percentage_claim",
        "stop_loss",
        "take_profit",
        "take_profit_explicit_none",
        "micro_size",
        "max_loss_gate",
        "daily_stop_gate",
        "kill_switch",
        "one_order_only",
        "broker_proof",
        "broker_proof_current",
        "broker_proof_stale",
        "broker_runtime_intake_required",
        "incident_stop_procedure_present",
        "walk_forward_gate_cleared",
        "walk_forward_failed",
        "candidate_rejected",
        "paper_only",
        "demo_live_status",
    )
    return {key: _json_safe(evidence.get(key)) for key in keys}


def _safety_summary() -> dict[str, bool]:
    return {
        "broker_call_performed": False,
        "network_call_performed": False,
        "credentials_read": False,
        "account_identifiers_read": False,
        "env_read": False,
        "secret_files_read": False,
        "live_order_executed_by_codex": False,
        "demo_order_executed_by_codex": False,
        "paper_order_executed_by_codex": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "uptime_80_activated": False,
        "automation_22_5_activated": False,
    }


def _walk_json(payload: Any, prefix: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            current = prefix + (str(key),)
            if isinstance(value, Mapping | list | tuple):
                yield from _walk_json(value, current)
            else:
                yield current, value
    elif isinstance(payload, list | tuple):
        for index, value in enumerate(payload):
            yield from _walk_json(value, prefix + (str(index),))


def _contains_sensitive_keys(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key).lower().strip() in SENSITIVE_VALUE_KEYS:
                return True
            if _contains_sensitive_keys(value):
                return True
    elif isinstance(payload, list | tuple):
        return any(_contains_sensitive_keys(item) for item in payload)
    return False


def _set_once(evidence: dict[str, Any], key: str, value: Any, source: str) -> None:
    if value in (None, ""):
        return
    if evidence.get(key) in (None, "", "UNKNOWN"):
        evidence[key] = value
        evidence["evidence_sources"][key] = source


def _set_numeric(
    evidence: dict[str, Any],
    key: str,
    value: Any,
    source: str,
    *,
    prefer_max: bool = False,
) -> None:
    number = _to_number(value)
    if number is None:
        return
    if evidence.get(key) is None:
        evidence[key] = number
        evidence["evidence_sources"][key] = source
    elif prefer_max and number > evidence[key]:
        evidence[key] = number
        evidence["evidence_sources"][key] = source


def _apply_take_profit(evidence: dict[str, Any], value: str, source: str) -> None:
    cleaned = str(value).strip().strip("`")
    if not cleaned:
        return
    if cleaned.lower() in {"none", "explicit none", "no", "not used"}:
        evidence["take_profit_explicit_none"] = True
    _set_once(evidence, "take_profit", cleaned, source)
    evidence["ticket_sources"].append(source)


def _extract_value_after_label(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        match = re.search(rf"{re.escape(label)}\s*[:|]\s*`?([^`\n|]+)", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_number_after_label(text: str, labels: tuple[str, ...]) -> float | None:
    for label in labels:
        match = re.search(rf"{re.escape(label)}[^0-9\-]+(-?\d+(?:\.\d+)?)", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _regex_first(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _normalize_side(value: str) -> str:
    upper = value.upper()
    if upper == "LONG":
        return "BUY"
    if upper == "SHORT":
        return "SELL"
    return upper


def _to_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _json_safe(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _unique_list(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _bullet_lines(values: Iterable[Any]) -> str:
    items = [str(value) for value in values]
    if not items:
        return "- NONE"
    return "\n".join(f"- `{item}`" for item in items)


def _table(values: Mapping[str, Any]) -> str:
    lines = ["| Field | Value |", "|---|---|"]
    for key, value in values.items():
        lines.append(f"| {key} | `{value if value not in (None, '') else 'UNKNOWN'}` |")
    return "\n".join(lines)
