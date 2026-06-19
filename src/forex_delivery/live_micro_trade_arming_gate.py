"""Dry-run live micro-trade arming gate review.

This module evaluates sanitized read-only and paper evidence before a future
one-shot live micro-trade execution packet can even be considered. It does not
read secrets, call brokers, place orders, close trades, or allow live execution.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "AIOS_FOREX_LIVE_MICRO_TRADE_ARMING_GATE.v1"
REPORT_TITLE = "AIOS Forex Live Micro-Trade Arming Gate Dry Run V1"
REQUIRED_HUMAN_PHRASE = "I AUTHORIZE ONE LIVE MICRO TRADE DRY-RUN ARMING REVIEW"
NEXT_PACKET_CANDIDATE = "AIOS-FOREX-ONE-SHOT-LIVE-MICRO-TRADE-EXECUTION-V1"

READ_ONLY_EVIDENCE_PATH = (
    "Reports/forex_delivery/AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_DRY_RUN_V1.md"
)
PAPER_EVIDENCE_PATH = (
    "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md"
)
ARMING_EVIDENCE_PATH = (
    "Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_TRADE_ARMING_GATE_DRY_RUN_V1.md"
)

DEFAULT_SELECTED_PAIR = "EUR_USD"
DEFAULT_MAX_UNITS = 1
DEFAULT_MAX_TRADE_RISK = 1.0
DEFAULT_DAILY_LOSS_CAP = 5.0

FORBIDDEN_VALUE_MARKERS = (
    "OANDA_API_TOKEN",
    "OANDA_ACCOUNT_ID",
    "Authorization",
    "Bearer ",
    "transactionID",
    "orderID",
    "accountID",
    "rawBroker",
)


def build_live_micro_trade_arming_gate_result(
    *,
    repo_root: Path | None = None,
    read_only_evidence: Mapping[str, Any] | None = None,
    paper_evidence: Mapping[str, Any] | None = None,
    human_phrase: str | None = None,
    selected_pair: str = DEFAULT_SELECTED_PAIR,
    max_units: int = DEFAULT_MAX_UNITS,
    max_trade_risk: float = DEFAULT_MAX_TRADE_RISK,
    daily_loss_cap: float = DEFAULT_DAILY_LOSS_CAP,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    """Build the sanitized dry-run arming gate result."""
    generated_at_utc = generated_at_utc or utc_now_iso()
    repo_root = repo_root or Path.cwd()
    read_only_model = dict(
        read_only_evidence
        if read_only_evidence is not None
        else load_evidence_model(repo_root / READ_ONLY_EVIDENCE_PATH)
    )
    paper_model = dict(
        paper_evidence
        if paper_evidence is not None
        else load_evidence_model(repo_root / PAPER_EVIDENCE_PATH)
    )

    evidence_present: list[str] = []
    evidence_missing: list[str] = []
    blocked_reasons: list[str] = []

    read_only_eval = evaluate_read_only_evidence(read_only_model)
    paper_eval = evaluate_paper_evidence(paper_model)
    risk_eval = evaluate_risk_requirements(
        max_units=max_units,
        max_trade_risk=max_trade_risk,
        daily_loss_cap=daily_loss_cap,
    )
    exit_eval = evaluate_exit_requirements(paper_model)
    human_eval = evaluate_human_arming(human_phrase)

    for evaluation in (read_only_eval, paper_eval, risk_eval, exit_eval, human_eval):
        evidence_present.extend(evaluation["evidence_present"])
        evidence_missing.extend(evaluation["evidence_missing"])
        blocked_reasons.extend(evaluation["blocked_reasons"])

    live_armable = len(blocked_reasons) == 0
    result = {
        "schema": SCHEMA,
        "LIVE_ARMABLE": live_armable,
        "live_execution_allowed": False,
        "selected_pair": normalize_pair(selected_pair),
        "max_units": max_units,
        "max_trade_risk": max_trade_risk,
        "daily_loss_cap": daily_loss_cap,
        "required_human_phrase": REQUIRED_HUMAN_PHRASE,
        "evidence_present": unique(evidence_present),
        "evidence_missing": unique(evidence_missing),
        "blocked_reasons": unique(blocked_reasons),
        "next_safe_action": next_safe_action(live_armable),
        "next_packet_candidate": NEXT_PACKET_CANDIDATE,
        "no_secret_status": "NO_SECRET_VALUES_READ_OR_PRINTED",
        "no_account_id_status": "NO_ACCOUNT_IDS_OUTPUT",
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
        "generated_at_utc": generated_at_utc,
        "evidence_path": ARMING_EVIDENCE_PATH,
        "read_only_evidence": read_only_eval,
        "paper_loop_evidence": paper_eval,
        "risk_requirements": risk_eval,
        "exit_requirements": exit_eval,
        "human_owner_arming": human_eval,
        "safety_confirmations": {
            "no_live_trade_placed": True,
            "no_live_buy": True,
            "no_live_sell": True,
            "no_live_close": True,
            "no_broker_write_calls": True,
            "no_secret_values_recorded": True,
            "no_private_identifiers_recorded": True,
            "no_raw_broker_payload_recorded": True,
        },
    }
    assert_arming_gate_sanitized(result)
    return result


def evaluate_read_only_evidence(model: Mapping[str, Any]) -> dict[str, Any]:
    present: list[str] = []
    missing: list[str] = []
    blockers: list[str] = []
    if not model:
        missing.append("read_only_live_data_bridge_evidence")
        blockers.append("read_only_bridge_evidence_missing")
    else:
        present.append("read_only_live_data_bridge_evidence")

    source_type = model.get("source_type", "UNKNOWN")
    source_label = model.get("source_label", "UNKNOWN")
    stale_status = model.get("stale_status", "UNKNOWN")
    broker_state = dict(model.get("broker_state") or {})
    positions = dict(model.get("positions") or {})
    risk_pl = dict(model.get("risk_pl") or {})
    history = dict(model.get("trading_history") or {})

    if source_type != "broker-live-read-only" or stale_status != "VALID":
        blockers.append("read_only_source_not_live_tradable_or_not_valid")
    else:
        present.append("read_only_source_valid")
    if broker_state.get("account_reachable") is not True:
        blockers.append("broker_account_not_reachable")
    else:
        present.append("broker_account_reachable")
    if positions.get("positions_reconciled") is not True:
        blockers.append("positions_not_reconciled")
    else:
        present.append("positions_reconciled")
    if risk_pl.get("daily_pl_available") is not True:
        blockers.append("daily_pl_not_available")
    else:
        present.append("daily_pl_available")
    if history.get("trading_history_available") is not True:
        blockers.append("real_trading_history_unavailable_or_blocked")
    else:
        present.append("real_trading_history_available")

    return {
        "source_type": source_type,
        "source_label": source_label,
        "freshness_utc": model.get("freshness_utc", "UNKNOWN"),
        "stale_status": stale_status,
        "broker_reachable": broker_state.get("account_reachable", False),
        "positions_reconciled": positions.get("positions_reconciled", False),
        "pl_available": risk_pl.get("daily_pl_available", False),
        "trading_history_available": history.get("trading_history_available", False),
        "evidence_present": present,
        "evidence_missing": missing,
        "blocked_reasons": unique(blockers),
        "live_execution_allowed": False,
    }


def evaluate_paper_evidence(model: Mapping[str, Any]) -> dict[str, Any]:
    present: list[str] = []
    missing: list[str] = []
    blockers: list[str] = []
    if not model:
        missing.append("paper_signal_execution_loop_evidence")
        blockers.append("paper_loop_evidence_missing")
    else:
        present.append("paper_signal_execution_loop_evidence")

    checks = (
        ("signal_side", lambda value: str(value or "NONE").upper() in {"BUY", "SELL"}, "paper_signal_missing"),
        ("risk_approval", lambda value: value is True, "paper_risk_gate_not_approved"),
        ("paper_entry_created", lambda value: value is True, "paper_entry_not_created"),
        ("exit_plan_status", lambda value: str(value or "").upper() == "READY", "paper_exit_plan_not_ready"),
        ("paper_close_reconcile", lambda value: value is True, "paper_close_reconcile_missing"),
        ("realized_paper_pl", lambda value: value not in (None, "", "UNAVAILABLE"), "paper_pl_not_recorded"),
        (
            "trading_history_row_written",
            lambda value: value is True,
            "paper_history_writeback_missing",
        ),
    )
    for field_name, predicate, blocker in checks:
        if predicate(model.get(field_name)):
            present.append(field_name)
        else:
            missing.append(field_name)
            blockers.append(blocker)
    if model.get("live_execution_allowed") is not False:
        blockers.append("paper_loop_live_execution_flag_not_false")

    return {
        "paper_signal_generated": str(model.get("signal_side") or "NONE").upper() in {"BUY", "SELL"},
        "risk_gate_approved": model.get("risk_approval") is True,
        "paper_entry_created": model.get("paper_entry_created") is True,
        "exit_plan_present": str(model.get("exit_plan_status") or "").upper() == "READY",
        "paper_close_reconcile_completed": model.get("paper_close_reconcile") is True,
        "paper_pl_recorded": model.get("realized_paper_pl") not in (None, "", "UNAVAILABLE"),
        "trading_history_row_written": model.get("trading_history_row_written") is True,
        "paper_live_execution_allowed": model.get("live_execution_allowed", False),
        "evidence_present": unique(present),
        "evidence_missing": unique(missing),
        "blocked_reasons": unique(blockers),
        "live_execution_allowed": False,
    }


def evaluate_risk_requirements(
    *,
    max_units: int,
    max_trade_risk: float,
    daily_loss_cap: float,
) -> dict[str, Any]:
    blockers = [
        "human_owner_has_not_armed_live_micro_trade",
        "secret_status_presence_not_verified_by_approved_runtime_gate",
        "broker_account_live_state_not_reconciled_for_execution",
        "no_open_live_position_reconciliation_missing",
    ]
    return {
        "max_units": max_units,
        "max_trade_risk": max_trade_risk,
        "daily_loss_cap": daily_loss_cap,
        "one_position_rule": True,
        "no_duplicate_entry_rule": True,
        "no_revenge_loop_rule": True,
        "kill_switch_required": True,
        "no_open_live_position_unless_reconciled": True,
        "evidence_present": [
            "risk_boundary_declared",
            "one_position_rule_declared",
            "no_duplicate_entry_rule_declared",
            "no_revenge_loop_rule_declared",
            "kill_switch_required_declared",
        ],
        "evidence_missing": [
            "human_owner_live_arming_phrase",
            "approved_secret_presence_status",
            "live_broker_account_execution_reconciliation",
        ],
        "blocked_reasons": blockers,
        "live_execution_allowed": False,
    }


def evaluate_exit_requirements(paper_model: Mapping[str, Any]) -> dict[str, Any]:
    exit_plan = dict(paper_model.get("exit_plan") or {})
    stop_policy = dict(paper_model.get("stop_loss_policy") or exit_plan.get("stop_loss_policy") or {})
    take_profit = dict(
        paper_model.get("take_profit_policy") or exit_plan.get("take_profit_policy") or {}
    )
    max_time = dict(paper_model.get("max_time_policy") or exit_plan.get("max_time_policy") or {})
    stop_present = stop_policy.get("status") == "REQUIRED_PRESENT"
    take_profit_present = take_profit.get("status") == "REQUIRED_PRESENT"
    max_time_present = max_time.get("status") == "REQUIRED_PRESENT"
    blockers: list[str] = []
    if not stop_present:
        blockers.append("stop_loss_policy_missing_for_live_review")
    if not take_profit_present:
        blockers.append("take_profit_policy_missing_for_live_review")
    if not max_time_present:
        blockers.append("max_time_policy_missing_for_live_review")
    blockers.append("auto_exit_readiness_not_separately_implemented_for_live")

    return {
        "stop_loss_required_before_or_with_entry": True,
        "stop_loss_policy_present": stop_present,
        "take_profit_policy_required": True,
        "take_profit_policy_present": take_profit_present,
        "max_time_policy_required": True,
        "max_time_policy_present": max_time_present,
        "manual_broker_ui_fallback_required": True,
        "auto_exit_readiness": "BLOCKED_UNTIL_SEPARATE_IMPLEMENTATION",
        "evidence_present": [
            item
            for item, present in (
                ("paper_stop_loss_policy", stop_present),
                ("paper_take_profit_policy", take_profit_present),
                ("paper_max_time_policy", max_time_present),
                ("manual_fallback_required", True),
            )
            if present
        ],
        "evidence_missing": ["live_auto_exit_readiness"],
        "blocked_reasons": unique(blockers),
        "live_execution_allowed": False,
    }


def evaluate_human_arming(human_phrase: str | None) -> dict[str, Any]:
    phrase_present = human_phrase == REQUIRED_HUMAN_PHRASE
    return {
        "required_human_phrase": REQUIRED_HUMAN_PHRASE,
        "required_phrase_present": phrase_present,
        "no_default_arming": True,
        "this_packet_executes": False,
        "evidence_present": ["required_human_phrase_declared"] if phrase_present else [],
        "evidence_missing": [] if phrase_present else ["required_human_phrase_not_provided"],
        "blocked_reasons": [] if phrase_present else ["required_human_phrase_not_provided"],
        "live_execution_allowed": False,
    }


def build_sanitized_report(result: Mapping[str, Any]) -> str:
    assert_arming_gate_sanitized(result)
    summary = {
        "LIVE_ARMABLE": result.get("LIVE_ARMABLE"),
        "live_execution_allowed": False,
        "selected_pair": result.get("selected_pair"),
        "max_units": result.get("max_units"),
        "max_trade_risk": result.get("max_trade_risk"),
        "blocked_reasons": result.get("blocked_reasons"),
        "next_safe_action": result.get("next_safe_action"),
        "required_human_phrase": result.get("required_human_phrase"),
        "next_packet_candidate": result.get("next_packet_candidate"),
    }
    return (
        f"# {REPORT_TITLE}\n\n"
        "Status: ARMING_REVIEW_ONLY\n\n"
        "This report placed no live trade, no live buy, no live sell, and no live close. "
        "It made no broker write call and recorded no secrets, account identifiers, real "
        "order identifiers, transaction identifiers, or raw broker payloads.\n\n"
        "## Summary\n\n"
        f"```json\n{json.dumps(summary, indent=2, sort_keys=True)}\n```\n\n"
        "## Evidence Evaluated\n\n"
        f"```json\n{json.dumps(result.get('evidence_present'), indent=2, sort_keys=True)}\n```\n\n"
        "## Blockers\n\n"
        f"```json\n{json.dumps(result.get('blocked_reasons'), indent=2, sort_keys=True)}\n```\n\n"
        "## Sanitized Arming Gate Result\n\n"
        f"```json\n{json.dumps(dict(result), indent=2, sort_keys=True)}\n```\n"
    )


def write_live_micro_trade_arming_gate_report(
    result: Mapping[str, Any],
    *,
    repo_root: Path,
    relative_path: str = ARMING_EVIDENCE_PATH,
) -> Path:
    assert_arming_gate_sanitized(result)
    report_path = repo_root / relative_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_sanitized_report(result), encoding="utf-8")
    return report_path


def cli_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_LIVE_MICRO_TRADE_ARMING_GATE_CLI_SUMMARY.v1",
        "LIVE_ARMABLE": result.get("LIVE_ARMABLE"),
        "live_execution_allowed": False,
        "selected_pair": result.get("selected_pair"),
        "max_units": result.get("max_units"),
        "max_trade_risk": result.get("max_trade_risk"),
        "blocked_reason_count": len(result.get("blocked_reasons") or []),
        "next_safe_action": result.get("next_safe_action"),
        "next_packet_candidate": result.get("next_packet_candidate"),
        "evidence_path": result.get("evidence_path"),
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
    }


def load_evidence_model(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    for block in reversed(re.findall(r"```json\s*(.*?)```", text, flags=re.DOTALL)):
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def assert_arming_gate_sanitized(payload: Mapping[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    for marker in FORBIDDEN_VALUE_MARKERS:
        if marker in serialized:
            raise ValueError(f"forbidden_arming_gate_output_marker:{marker}")
    lowered = serialized.lower()
    for forbidden in (
        '"live_execution_allowed": true',
        '"broker_write_calls_allowed": true',
        '"order_placement_allowed": true',
        '"close_trade_allowed": true',
    ):
        if forbidden in lowered:
            raise ValueError(f"forbidden_arming_gate_permission:{forbidden}")


def next_safe_action(live_armable: bool) -> str:
    if live_armable:
        return (
            "Prepare a separate one-shot live micro-trade execution packet for Human Owner "
            "review; do not execute from this arming gate."
        )
    return (
        "Resolve arming blockers, review evidence, and keep live execution blocked until a "
        "separate approved one-shot execution packet exists."
    )


def normalize_pair(value: Any) -> str:
    return str(value or DEFAULT_SELECTED_PAIR).strip().upper().replace("/", "_").replace("-", "_")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def unique(items: list[str]) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return seen
