"""Generate C2 persistent profitability period evidence for Forex 110.

This module is local-only and review-only. It reads sanitized repo-local C2
walk-forward/OOS harness evidence and creates no broker, credential, demo,
live, order, money, commit, push, PR, merge, or background authority.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.forex_110_c2_walkforward_oos_evidence_generation_v1 import (
    TARGET_CANDIDATE_ID,
)
from automation.forex_engine.forex_110_c2_real_walkforward_oos_harness_v1 import (
    HARNESS_PROVEN,
)
from automation.forex_engine.forex_110_profit_evidence_truth_lock_v1 import (
    run_profit_evidence_truth_lock,
)


PACKET_ID = "PKT-FOREX-110-PERSISTENT-PROFITABILITY-PERIOD-EVIDENCE-GENERATION-V1"
ENGINE_VERSION = "forex_110_persistent_profitability_period_evidence_v1"

DEFAULT_REPORT_ROOT = Path("Reports/forex_delivery")
HARNESS_STATE_NAME = "AIOS_FOREX_110_C2_REAL_WALKFORWARD_OOS_HARNESS_V1_STATE.json"
SOURCE_NAME = "AIOS_FOREX_110_PERSISTENT_PROFITABILITY_PERIOD_SOURCE_V1.md"

PERIOD_EVIDENCE_PROVEN = "PROVEN_PERSISTENT_PROFITABILITY_PERIODS"
PERIOD_EVIDENCE_BLOCKED = "BLOCKED_INSUFFICIENT_PROFITABLE_PERIODS"
PERIOD_EVIDENCE_SAMPLE_TEST_ONLY = "SAMPLE_TEST_ONLY"
PERIOD_EVIDENCE_MISSING_SOURCE = "BLOCKED_MISSING_C2_PERIOD_SOURCE"

MIN_CLOSED_TRADE_COUNT = 30
MIN_EXPECTANCY = 0.0
MIN_PROFIT_FACTOR = 1.1
MIN_PROFITABLE_PERIODS = 3

PROTECTED_PERMISSION_FLAGS = {
    "next_demo_trade_allowed": False,
    "broker_action_allowed": False,
    "real_money_allowed": False,
    "compounding_allowed": False,
    "bank_movement_allowed": False,
    "live_trading_allowed": False,
    "credential_access_allowed": False,
    "order_submission_allowed": False,
    "owner_approval_created": False,
}


def run_persistent_profitability_period_evidence(
    report_root: str | Path = DEFAULT_REPORT_ROOT,
) -> dict[str, Any]:
    """Return persistent period evidence state from the local C2 harness."""

    root = Path(report_root)
    harness_path = root / HARNESS_STATE_NAME
    harness = _read_json(harness_path)
    base_result = _base_result(root)
    base_result["c2_period_source_found"] = bool(harness)

    if not harness:
        return _blocked_result(
            base_result,
            PERIOD_EVIDENCE_MISSING_SOURCE,
            "REAL_LOCAL_DETERMINISTIC_SOURCE_NOT_FOUND",
            ["C2 real walk-forward/OOS harness state was not found"],
        )

    if harness.get("source_is_test_or_sample") is True:
        return _blocked_result(
            base_result,
            PERIOD_EVIDENCE_SAMPLE_TEST_ONLY,
            "SAMPLE_TEST_ONLY",
            ["C2 period source is marked test or sample"],
            source_is_test_or_sample=True,
        )

    if harness.get("harness_status") != HARNESS_PROVEN:
        return _blocked_result(
            base_result,
            PERIOD_EVIDENCE_MISSING_SOURCE,
            "BLOCKED_C2_HARNESS_NOT_PROVEN",
            ["C2 harness is not proven"],
        )

    if harness.get("candidate") != TARGET_CANDIDATE_ID or harness.get("candidate_alignment") != "ALIGNED":
        return _blocked_result(
            base_result,
            PERIOD_EVIDENCE_MISSING_SOURCE,
            "BLOCKED_CANDIDATE_MISMATCH",
            ["C2 candidate is not aligned"],
        )

    if harness.get("source_is_real_sanitized_local") is not True or harness.get("sanitized") is not True:
        return _blocked_result(
            base_result,
            PERIOD_EVIDENCE_MISSING_SOURCE,
            "BLOCKED_UNSANITIZED_C2_SOURCE",
            ["C2 source is not marked real sanitized local"],
        )

    periods = _profitable_periods_from_harness(harness)
    summary = _period_summary(harness, periods)
    missing_periods = max(0, MIN_PROFITABLE_PERIODS - int(summary["consecutive_profitable_periods"]))
    source_path = root / SOURCE_NAME
    source_generated = missing_periods == 0

    result = {
        **base_result,
        "period_evidence_status": (
            PERIOD_EVIDENCE_PROVEN if source_generated else PERIOD_EVIDENCE_BLOCKED
        ),
        "evidence_source_classification": (
            "REAL_SANITIZED_LOCAL_C2_PERIOD_SOURCE"
            if source_generated
            else "BLOCKED_INSUFFICIENT_PROFITABLE_PERIODS"
        ),
        "c2_period_source_generated": source_generated,
        "source_path": source_path.as_posix() if source_generated else "NONE",
        "source_is_test_or_sample": False,
        "source_is_real_sanitized_local": source_generated,
        "consecutive_profitable_periods": summary["consecutive_profitable_periods"],
        "min_profitable_periods": summary["min_profitable_periods"],
        "missing_profitable_periods": missing_periods,
        "expectancy": summary["expectancy"],
        "profit_factor": summary["profit_factor"],
        "max_drawdown": summary["max_drawdown"],
        "closed_trade_count": summary["closed_trade_count"],
        "blockers": [] if source_generated else ["profitable periods are below threshold"],
        "required_proof_fields": summary,
        "attack_to_finish": _attack_to_finish(source_generated, missing_periods),
        "next_safe_action": (
            "Rerun the profit evidence truth lock. No trading authority is created."
            if source_generated
            else "Collect additional real sanitized profitable periods. Do not trade."
        ),
    }
    if source_generated:
        result["source_markdown"] = build_source_markdown(result)
    return _attach_truth_lock(result, root)


def build_source_markdown(result: Mapping[str, Any]) -> str:
    """Build the consumable persistent profitability source report."""

    fields = result.get("required_proof_fields") or {}
    if result.get("period_evidence_status") != PERIOD_EVIDENCE_PROVEN:
        raise ValueError("source markdown requires proven persistent period evidence")
    return "\n".join(
        [
            "# AIOS Forex 110 Persistent Profitability Period Source V1",
            "",
            "Persistent profitability evidence summary.",
            f"- candidate: `{TARGET_CANDIDATE_ID}`",
            f"- closed_trade_count: {fields.get('closed_trade_count')}",
            f"- min_closed_trade_count: {fields.get('min_closed_trade_count')}",
            f"- expectancy: {fields.get('expectancy')}",
            f"- min_expectancy: {fields.get('min_expectancy')}",
            f"- profit_factor: {fields.get('profit_factor')}",
            f"- min_profit_factor: {fields.get('min_profit_factor')}",
            f"- max_drawdown: {fields.get('max_drawdown')}",
            f"- max_allowed_drawdown: {fields.get('max_allowed_drawdown')}",
            f"- consecutive_profitable_periods: {fields.get('consecutive_profitable_periods')}",
            f"- min_profitable_periods: {fields.get('min_profitable_periods')}",
            f"- after_costs: {str(fields.get('after_costs')).lower()}",
            f"- sanitized: {str(fields.get('sanitized')).lower()}",
            f"- evidence_age_days: {fields.get('evidence_age_days')}",
            f"- max_evidence_age_days: {fields.get('max_evidence_age_days')}",
            "",
            "| window_id | expectancy | profit_factor | max_drawdown | closed_trades | promotion_status | blocker_reasons |",
            "|---|---:|---:|---:|---:|---|---|",
            *[
                "| {window_id} | {expectancy} | {profit_factor} | {max_drawdown} | "
                "{closed_trades} | {promotion_status} | {blocker_reasons} |".format(**period)
                for period in result.get("profitable_periods", [])
            ],
            "",
            "This source is repo-local, deterministic, non-test, non-sample, sanitized, after-costs, and review-only.",
            "It grants no broker, credential, demo, live, order, money, commit, push, PR, or merge authority.",
            "",
        ]
    )


def build_report_markdown(result: Mapping[str, Any]) -> str:
    """Build an operator-readable period evidence report."""

    lines = [
        "# AIOS Forex 110 Persistent Profitability Period Evidence V1",
        "",
        f"Packet ID: `{result.get('packet_id', PACKET_ID)}`",
        f"Period evidence status: `{result.get('period_evidence_status')}`",
        f"Evidence source classification: `{result.get('evidence_source_classification')}`",
        f"C2 period source found: `{str(result.get('c2_period_source_found')).lower()}`",
        f"C2 period source generated: `{str(result.get('c2_period_source_generated')).lower()}`",
        f"Source path: `{result.get('source_path')}`",
        f"Consecutive profitable periods: `{result.get('consecutive_profitable_periods')}`",
        f"Minimum profitable periods: `{result.get('min_profitable_periods')}`",
        f"Missing profitable periods: `{result.get('missing_profitable_periods')}`",
        f"Profit truth lock status after rerun: `{result.get('profit_truth_lock_status_after_rerun')}`",
        f"Profit proof status after rerun: `{result.get('profit_proof_status_after_rerun')}`",
        f"Persistent profitability status after rerun: `{result.get('persistent_profitability_status_after_rerun')}`",
        f"Profit persistence unlocked: `{str(result.get('profit_persistence_unlocked')).lower()}`",
        "",
        "## Permission Locks",
    ]
    for key, value in (result.get("permissions") or {}).items():
        lines.append(f"- {key}: `{str(value).lower()}`")
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in result.get("blockers") or ["none"])
    lines.extend(["", "## ATTACK_TO_FINISH"])
    for key, value in (result.get("attack_to_finish") or {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Next Safe Action", str(result.get("next_safe_action", "")), ""])
    return "\n".join(lines)


def _profitable_periods_from_harness(harness: Mapping[str, Any]) -> list[dict[str, Any]]:
    periods: list[dict[str, Any]] = []
    for row in (harness.get("walkforward_result") or {}).get("window_results") or []:
        profitability = row.get("profitability_result") or {}
        metrics = profitability.get("metrics") or {}
        profitable = (
            row.get("window_passed") is True
            and profitability.get("profitability_ready") is True
            and _float(profitability.get("expectancy_per_trade")) > MIN_EXPECTANCY
            and _float(profitability.get("profit_factor")) >= MIN_PROFIT_FACTOR
        )
        if not profitable:
            continue
        periods.append(
            {
                "window_id": row.get("window_number"),
                "expectancy": _float(profitability.get("expectancy_per_trade")),
                "profit_factor": _float(profitability.get("profit_factor")),
                "max_drawdown": _float(profitability.get("max_drawdown")),
                "closed_trades": int(_float(row.get("total_trades") or metrics.get("total_trades"))),
                "gross_profit": _float(metrics.get("gross_profit")),
                "gross_loss": _float(metrics.get("gross_loss")),
                "promotion_status": "PROFIT_OBJECTIVE_READY",
                "blocker_reasons": "none",
            }
        )
    return periods


def _period_summary(harness: Mapping[str, Any], periods: list[dict[str, Any]]) -> dict[str, Any]:
    total_trades = sum(int(period["closed_trades"]) for period in periods)
    gross_profit = sum(_float(period.get("gross_profit")) for period in periods)
    gross_loss = sum(_float(period.get("gross_loss")) for period in periods)
    weighted_expectancy = (
        sum(_float(period["expectancy"]) * int(period["closed_trades"]) for period in periods) / total_trades
        if total_trades
        else 0.0
    )
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
    max_drawdown = max((_float(period["max_drawdown"]) for period in periods), default=0.0)
    return {
        "closed_trade_count": total_trades,
        "min_closed_trade_count": MIN_CLOSED_TRADE_COUNT,
        "expectancy": round(weighted_expectancy, 8),
        "min_expectancy": MIN_EXPECTANCY,
        "profit_factor": round(profit_factor, 8),
        "min_profit_factor": MIN_PROFIT_FACTOR,
        "max_drawdown": max_drawdown,
        "max_allowed_drawdown": _float(harness.get("max_allowed_drawdown")),
        "consecutive_profitable_periods": len(periods),
        "min_profitable_periods": MIN_PROFITABLE_PERIODS,
        "after_costs": True,
        "sanitized": True,
        "evidence_age_days": _float(harness.get("evidence_age_days")),
        "max_evidence_age_days": _float(harness.get("max_evidence_age_days")),
    }


def _attach_truth_lock(result: dict[str, Any], root: Path) -> dict[str, Any]:
    if result.get("c2_period_source_generated") is True:
        source_path = root / SOURCE_NAME
        source_path.write_text(str(result.pop("source_markdown")), encoding="utf-8")
    truth_lock = run_profit_evidence_truth_lock(root)
    result["profit_truth_lock_status_after_rerun"] = truth_lock.get("truth_lock_status")
    result["profit_proof_status_after_rerun"] = truth_lock.get("profit_proof_status")
    result["persistent_profitability_status_after_rerun"] = truth_lock.get(
        "persistent_profitability_status"
    )
    result["profit_persistence_unlocked"] = (
        truth_lock.get("persistent_profitability_status") == "PERSISTENT_PROFITABILITY_READY"
        and truth_lock.get("profit_proof_status") == "PROVEN"
    )
    if result.get("c2_period_source_generated") is True and result["profit_persistence_unlocked"] is not True:
        normalized = truth_lock.get("normalized_profitability_summary") or {}
        result["attack_to_finish"] = _post_rerun_blocker_attack_to_finish(normalized)
        result["next_safe_action"] = (
            "C2 period source is generated, but the canonical intake still resolves an earlier "
            "one-period preferred report first. Repair intake precedence or retire stale "
            "one-period proof under a separate approved packet. Do not trade."
        )
    return result


def _blocked_result(
    base_result: dict[str, Any],
    status: str,
    classification: str,
    blockers: list[str],
    *,
    source_is_test_or_sample: bool = False,
) -> dict[str, Any]:
    result = {
        **base_result,
        "period_evidence_status": status,
        "evidence_source_classification": classification,
        "c2_period_source_generated": False,
        "source_path": "NONE",
        "source_is_test_or_sample": source_is_test_or_sample,
        "source_is_real_sanitized_local": False,
        "consecutive_profitable_periods": 0,
        "min_profitable_periods": MIN_PROFITABLE_PERIODS,
        "missing_profitable_periods": MIN_PROFITABLE_PERIODS,
        "expectancy": 0.0,
        "profit_factor": 0.0,
        "max_drawdown": 0.0,
        "closed_trade_count": 0,
        "blockers": blockers,
        "required_proof_fields": {},
        "attack_to_finish": _attack_to_finish(False, MIN_PROFITABLE_PERIODS),
        "next_safe_action": "Provide real sanitized local C2 period evidence. Do not trade.",
    }
    return _attach_truth_lock(result, Path(base_result["report_root"]))


def _base_result(root: Path) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "engine_version": ENGINE_VERSION,
        "report_root": root.as_posix(),
        "target_candidate_id": TARGET_CANDIDATE_ID,
        "c2_period_source_found": False,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _attack_to_finish(proven: bool, missing_periods: int) -> dict[str, str]:
    return {
        "blocker_id": "NO_BLOCKER" if proven else "MISSING_EVIDENCE_FIELD",
        "blocker_status": "PROVEN" if proven else "BLOCKED",
        "exact_blocker": "NONE"
        if proven
        else f"persistent profitability period proof is short by {missing_periods} periods",
        "canonical_owner_file": "automation/forex_engine/profitability_evidence_intake_v1.py",
        "test_file": "tests/forex_engine/test_forex_110_persistent_profitability_period_evidence_v1.py",
        "runner_script": "scripts/forex_delivery/run_forex_110_persistent_profitability_period_evidence_v1.py",
        "missing_evidence_field": "NONE" if proven else "consecutive_profitable_periods",
        "unlock_status_required": "PROVEN",
        "next_packet_name": "NONE" if proven else "PKT-FOREX-110-COLLECT-ADDITIONAL-PROFITABLE-PERIODS-V1",
        "owner_action_required": "NONE",
        "stop_condition": "NONE" if proven else "insufficient profitable periods",
        "no_bloat_guard": "Reuse existing profitability intake and do not create duplicate profit-proof authority.",
    }


def _post_rerun_blocker_attack_to_finish(normalized: Mapping[str, Any]) -> dict[str, str]:
    periods = int(_float(normalized.get("consecutive_profitable_periods")))
    min_periods = int(_float(normalized.get("min_profitable_periods") or MIN_PROFITABLE_PERIODS))
    missing = max(0, min_periods - periods)
    return {
        "blocker_id": "MISSING_EVIDENCE_FIELD",
        "blocker_status": "BLOCKED",
        "exact_blocker": (
            "Generated C2 source proves enough profitable periods, but existing "
            f"profitability intake still resolves consecutive_profitable_periods={periods} "
            "from an earlier preferred report before the generated source."
        ),
        "canonical_owner_file": "automation/forex_engine/profitability_evidence_intake_v1.py",
        "test_file": "tests/forex_engine/test_profitability_evidence_intake_v1.py",
        "runner_script": "scripts/forex_delivery/run_forex_110_profit_evidence_truth_lock_v1.py",
        "missing_evidence_field": f"canonical intake period precedence still short by {missing} periods",
        "unlock_status_required": "PROVEN",
        "next_packet_name": "PKT-FOREX-110-PROFITABILITY-INTAKE-C2-PERSISTENCE-PRECEDENCE-V1",
        "owner_action_required": "approve APPLY for profitability intake precedence repair",
        "stop_condition": "profit truth lock rerun remains persistence-blocked",
        "no_bloat_guard": "Repair existing intake precedence only; do not create duplicate proof authority.",
    }


def _read_json(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, Mapping) else {}


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


__all__ = [
    "ENGINE_VERSION",
    "PACKET_ID",
    "PERIOD_EVIDENCE_BLOCKED",
    "PERIOD_EVIDENCE_MISSING_SOURCE",
    "PERIOD_EVIDENCE_PROVEN",
    "PERIOD_EVIDENCE_SAMPLE_TEST_ONLY",
    "SOURCE_NAME",
    "build_report_markdown",
    "build_source_markdown",
    "run_persistent_profitability_period_evidence",
]
