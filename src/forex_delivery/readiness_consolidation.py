"""Repository-only Forex readiness consolidation helpers.

This module builds sanitized, no-broker-write evidence summaries from existing
read-only fixture/replay paths. It deliberately does not read credentials,
connect to brokers, submit orders, or arm live execution.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .auto_exit_live_readiness import build_auto_exit_live_readiness_model
from .paper_signal_execution_loop import build_paper_signal_execution_loop_result
from .read_only_live_data_bridge import build_read_only_live_data_bridge_read_model

SCHEMA = "AIOS_FOREX_READINESS_CONSOLIDATION.v1"
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_READINESS_CONSOLIDATION_APPLY_V1_REPORT.md"
)


def build_readiness_consolidation_evidence(
    *, now_utc: str | None = None
) -> dict[str, Any]:
    """Build one sanitized owner-review evidence packet from repository fixtures."""

    timestamp = now_utc or datetime.now(timezone.utc).isoformat()
    bridge = build_read_only_live_data_bridge_read_model(env={}, now_utc=timestamp)
    auto_exit = build_auto_exit_live_readiness_model(generated_at_utc=timestamp)
    paper_loop = build_paper_signal_execution_loop_result(
        entry_time_utc=timestamp, exit_time_utc=timestamp
    )

    reconciliation = {
        "account_reachability_status": bridge["broker_state"]["account_reachable"],
        "open_position_consistency": bridge["positions"]["positions_reconciled"],
        "daily_pl_availability": bridge["risk_pl"]["daily_pl_available"],
        "margin_and_risk_availability": bridge["risk_pl"]["margin_risk_available"],
        "evidence_freshness": bridge["stale_status"],
    }
    preflight_bundle = {
        "execution_requested": False,
        "order_executed": False,
        "broker_call_performed": False,
        "live_execution_allowed": False,
        "broker_write_calls_allowed": False,
        "credential_persistence_allowed": False,
        "raw_broker_payload_recorded": False,
        "account_identifier_recorded": False,
        "reconciliation": reconciliation,
    }
    protected_command = {
        "status": "SEALED_FOR_OWNER_REVIEW_ONLY",
        "command_released": False,
        "owner_must_review_before_use": True,
        "live_execution_allowed": False,
        "broker_call_performed": False,
    }
    post_trade_package = {
        "ledger_template_status": "SANITIZED_TEMPLATE_READY",
        "receipt_template_status": "SANITIZED_TEMPLATE_READY",
        "replay_template_status": "SANITIZED_TEMPLATE_READY",
        "closeout_template_status": "SANITIZED_TEMPLATE_READY",
        "owner_review_template_status": "SANITIZED_TEMPLATE_READY",
        "real_trade_claimed": False,
    }
    remaining_blockers = _unique(
        list(bridge["execution_readiness"]["blocked_reasons"])
        + list(auto_exit.get("blocked_reasons", []))
    )
    evidence = {
        "schema": SCHEMA,
        "packet_id": "AIOS-FOREX-READINESS-CONSOLIDATION-APPLY-V1",
        "generated_at_utc": timestamp,
        "sanitized": True,
        "no_secrets": True,
        "no_account_identifiers": True,
        "no_raw_broker_payloads": True,
        "no_broker_writes": True,
        "no_order_endpoints": True,
        "no_credential_persistence": True,
        "read_only_reconciliation": reconciliation,
        "auto_exit_status": auto_exit.get("auto_exit_status", "BLOCKED"),
        "history_writeback_status": paper_loop.get("dashboard_status", {}).get(
            "history_writeback_status"
        ),
        "preflight_bundle": preflight_bundle,
        "protected_command_package": protected_command,
        "stop_after_one_order_procedure": {
            "status": "DRAFTED_NOT_RUN",
            "repeat_attempt_allowed": False,
            "requires_owner_review": True,
        },
        "post_trade_package": post_trade_package,
        "live_execution_allowed": False,
        "remaining_blockers": remaining_blockers,
        "next_exact_packet": "AIOS-FOREX-OWNER-SUPPLIED-SANITIZED-READONLY-EVIDENCE-INTAKE-APPLY-V1",
    }
    _assert_sanitized(evidence)
    return evidence


def render_readiness_consolidation_report(evidence: Mapping[str, Any]) -> str:
    _assert_sanitized(evidence)
    return (
        "# AIOS Forex Readiness Consolidation Apply V1\n\n"
        "This is sanitized repository-only evidence. It does not approve or perform live execution.\n\n"
        f"```json\n{json.dumps(dict(evidence), indent=2, sort_keys=True)}\n```\n"
    )


def write_readiness_consolidation_report(path: Path = REPORT_PATH) -> dict[str, Any]:
    evidence = build_readiness_consolidation_evidence()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_readiness_consolidation_report(evidence), encoding="utf-8")
    return {**evidence, "report_path": str(path)}


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _assert_sanitized(payload: Mapping[str, Any]) -> None:
    text = json.dumps(payload, sort_keys=True).lower()
    forbidden = (
        "oanda_" + "api_token",
        "oanda_" + "account_id",
        "authorization",
        "bearer" + " ",
        "raw_" + "payload",
    )
    for marker in forbidden:
        if marker in text:
            raise ValueError(f"forbidden sanitized evidence marker: {marker}")
    if any(
        payload.get(flag) is not True
        for flag in (
            "no_secrets",
            "no_account_identifiers",
            "no_raw_broker_payloads",
            "no_broker_writes",
            "no_order_endpoints",
            "no_credential_persistence",
        )
    ):
        raise ValueError("sanitized evidence flags are not all enforced")
    if payload.get("live_execution_allowed") is not False:
        raise ValueError("live execution must remain blocked")
