"""Profit campaign go-live wrap-up V1.

This orchestrator combines sanitized broker proof, ticket closure, campaign
ledger, repeatability targets, and uptime range planning. It is evidence-only:
it never calls brokers, reads credentials, moves money, starts automation, or
authorizes live execution.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from automation.forex_engine import broker_proof_ticket_closure_v1 as broker_closure
from automation.forex_engine import forex_uptime_range_planner_v1 as uptime_planner
from automation.forex_engine import micro_batch_campaign_ladder_v1 as campaign_ladder


WRAPUP_CREATED = "WRAPUP_CREATED"
WRAPUP_BLOCKED_BY_EVIDENCE = "WRAPUP_BLOCKED_BY_EVIDENCE"
WRAPUP_READY_FOR_HUMAN_INTAKE = "WRAPUP_READY_FOR_HUMAN_INTAKE"
WRAPUP_READY_FOR_HUMAN_ARMING_CANDIDATE = "WRAPUP_READY_FOR_HUMAN_ARMING_CANDIDATE"

EXPECTANCY_PROVEN = "EXPECTANCY_PROVEN"
EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK = "EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK"
EXPECTANCY_EVIDENCE_INSUFFICIENT = "EXPECTANCY_EVIDENCE_INSUFFICIENT"
EXPECTANCY_NEGATIVE_OR_REJECTED = "EXPECTANCY_NEGATIVE_OR_REJECTED"

CAMPAIGN_LEDGER_CREATED = "CAMPAIGN_LEDGER_CREATED"
CAMPAIGN_LEDGER_MISSING_EVIDENCE = "CAMPAIGN_LEDGER_MISSING_EVIDENCE"
CAMPAIGN_LEDGER_READY_FOR_PAPER_REPLAY = "CAMPAIGN_LEDGER_READY_FOR_PAPER_REPLAY"

TARGET_50_PLANNING_ONLY = "TARGET_50_PLANNING_ONLY"
TARGET_50_EVIDENCE_MISSING = "TARGET_50_EVIDENCE_MISSING"
TARGET_50_PAPER_CANDIDATE = "TARGET_50_PAPER_CANDIDATE"
TARGET_50_REPEATABILITY_REQUIRED = "TARGET_50_REPEATABILITY_REQUIRED"

TARGET_100_PLANNING_ONLY = "TARGET_100_PLANNING_ONLY"
TARGET_100_REQUIRES_TWO_50_CAMPAIGNS = "TARGET_100_REQUIRES_TWO_50_CAMPAIGNS"
TARGET_100_EVIDENCE_MISSING = "TARGET_100_EVIDENCE_MISSING"
TARGET_100_REPEATABILITY_REQUIRED = "TARGET_100_REPEATABILITY_REQUIRED"

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "Reports" / "forex_delivery"
WRAPUP_REPORT = REPORTS_DIR / "AIOS_FOREX_PROFIT_CAMPAIGN_GO_LIVE_WRAPUP_V1.md"
OPTIONAL_READY_REPORT = REPORTS_DIR / "AIOS_FOREX_READY_FOR_HUMAN_ARMING_CANDIDATE_V3.md"

SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "password",
    "passwd",
    "secret",
    "token",
    "credential",
    "credentials",
    "account_id",
    "accountid",
    "account_identifier",
    "account_number",
    "broker_order_id",
    "order_id",
    "transaction_id",
    "raw_payload",
    "raw_request",
    "raw_response",
    "authorization",
)

SANITIZED_ALLOWED_KEYS = frozenset(
    {
        "account_id_redacted_confirmation",
        "credential_not_pasted_confirmation",
        "credential_not_persisted_confirmation",
        "credential_handling_rule",
    }
)


def run_profit_campaign_go_live_wrapup(
    input_state: dict[str, Any] | None = None,
    write_reports: bool = False,
) -> dict[str, Any]:
    """Combine local proof lanes into one profit-campaign wrap-up result."""

    sanitized_input, redacted_fields = _sanitize_input(input_state or {})
    broker_result = broker_closure.run_broker_proof_ticket_closure(sanitized_input, write_reports=write_reports)
    campaign_result = campaign_ladder.run_micro_batch_campaign_ladder(
        _campaign_input(sanitized_input),
        write_reports=write_reports,
    )
    uptime_result = uptime_planner.run_forex_uptime_range_planner(
        _uptime_input(sanitized_input),
        write_reports=write_reports,
    )

    classifications = _classify_wrapup(
        sanitized_input=sanitized_input,
        broker_result=broker_result,
        campaign_result=campaign_result,
        uptime_result=uptime_result,
    )
    blocked_gates = _blocked_gates(classifications)
    optional_ready_allowed = _optional_ready_allowed(classifications)

    result = {
        "schema": "AIOS_FOREX_PROFIT_CAMPAIGN_GO_LIVE_WRAPUP_V1",
        "write_reports_requested": bool(write_reports),
        "classifications": classifications,
        "blocked_gates": tuple(blocked_gates),
        "broker_proof_ticket_closure": broker_result,
        "micro_batch_campaign_ladder": campaign_result,
        "uptime_range_planner": uptime_result,
        "visible_money_facts": {
            "campaign_count": campaign_result["campaign_count"],
            "micro_execution_count": campaign_result["micro_execution_count"],
            "best_return_percent": campaign_result["target_evidence"]["best_return_percent"],
            "campaigns_at_or_above_50_percent": campaign_result["target_evidence"]["campaigns_at_or_above_50_percent"],
            "evidence_ready_50_percent_campaigns": campaign_result["target_evidence"]["evidence_ready_50_percent_campaigns"],
            "trading_hours_per_week": uptime_result["calculations"]["trading_hours_per_week"],
            "minimum_maintenance_budget": uptime_result["calculations"]["minimum_maintenance_budget"],
        },
        "technical_noise_policy": "Money-relevant facts stay visible. Technical detail stays collapsed unless it blocks money, risk, broker proof, execution, uptime, monitoring, or reconciliation.",
        "optional_ready_report": {
            "path": _display_path(OPTIONAL_READY_REPORT),
            "created": False,
            "skipped_because": tuple(blocked_gates),
        },
        "sanitization": {
            "redacted_fields": tuple(redacted_fields),
            "sensitive_input_rejected_or_redacted": bool(redacted_fields),
            "account_ids_persisted": False,
            "credentials_persisted": False,
            "broker_order_ids_persisted": False,
        },
        "safety_summary": _safety_summary(),
        "reports": {
            "written": tuple(),
            "allowed_output_paths": tuple(
                sorted(
                    set(
                        broker_result["reports"]["allowed_output_paths"]
                        + campaign_result["reports"]["allowed_output_paths"]
                        + uptime_result["reports"]["allowed_output_paths"]
                        + (_display_path(WRAPUP_REPORT), _display_path(OPTIONAL_READY_REPORT))
                    )
                )
            ),
        },
    }

    if write_reports:
        written = [WRAPUP_REPORT]
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        WRAPUP_REPORT.write_text(_render_wrapup_report(result), encoding="utf-8", newline="\n")
        if optional_ready_allowed:
            OPTIONAL_READY_REPORT.write_text(_render_ready_report(result), encoding="utf-8", newline="\n")
            written.append(OPTIONAL_READY_REPORT)
        result["optional_ready_report"] = {
            **result["optional_ready_report"],
            "created": optional_ready_allowed,
            "skipped_because": tuple() if optional_ready_allowed else tuple(blocked_gates),
        }
        result["reports"] = {
            **result["reports"],
            "written": tuple(
                _unique(
                    list(broker_result["reports"]["written"])
                    + list(campaign_result["reports"]["written"])
                    + list(uptime_result["reports"]["written"])
                    + [_display_path(path) for path in written]
                )
            ),
        }

    return result


def _sanitize_input(payload: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    redacted: list[str] = []

    def scrub(value: Any, path: tuple[str, ...] = ()) -> Any:
        if isinstance(value, Mapping):
            output: dict[str, Any] = {}
            for key, item in value.items():
                key_text = str(key)
                normalized = key_text.lower().strip()
                if normalized not in SANITIZED_ALLOWED_KEYS and any(
                    part in normalized for part in SENSITIVE_KEY_PARTS
                ):
                    redacted.append(".".join(path + (key_text,)))
                    continue
                output[key_text] = scrub(item, path + (key_text,))
            return output
        if isinstance(value, list):
            return [scrub(item, path + (str(index),)) for index, item in enumerate(value)]
        if isinstance(value, tuple):
            return tuple(scrub(item, path + (str(index),)) for index, item in enumerate(value))
        return value

    return scrub(payload), _unique(redacted)


def _campaign_input(input_state: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(input_state.get("campaign_ladder"), Mapping):
        return dict(input_state["campaign_ladder"])
    keys = ("campaigns", "campaign", "micro_execution_ids", "requested_profit_proof")
    return {key: input_state[key] for key in keys if key in input_state}


def _uptime_input(input_state: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(input_state.get("uptime_range"), Mapping):
        return dict(input_state["uptime_range"])
    keys = (
        "uptime_80_requested",
        "uptime_target_percent",
        "requested_range",
        "range_request",
        "trading_hours_per_day",
        "trading_days_per_week",
        "maintenance_hours_per_day",
        "broker_session_proof",
        "market_session_proof",
        "incident_stop_proof",
        "monitoring_proof",
        "reconciliation_proof",
        "live_evidence_proof",
        "human_approval_proof",
        "demo_review_requested",
    )
    return {key: input_state[key] for key in keys if key in input_state}


def _classify_wrapup(
    *,
    sanitized_input: Mapping[str, Any],
    broker_result: Mapping[str, Any],
    campaign_result: Mapping[str, Any],
    uptime_result: Mapping[str, Any],
) -> dict[str, str]:
    broker_classes = broker_result["classifications"]
    campaign_classes = campaign_result["classifications"]
    uptime_classes = uptime_result["classifications"]

    expectancy_status = _expectancy_status(sanitized_input, broker_classes)
    campaign_ledger_status = _campaign_ledger_status(campaign_result)
    target_50_status = _target_50_status(campaign_result)
    target_100_status = _target_100_status(campaign_result)
    uptime_status = uptime_classes["UPTIME_RANGE_STATUS"]
    human_status = _human_candidate_status(
        broker_classes=broker_classes,
        expectancy_status=expectancy_status,
        campaign_ledger_status=campaign_ledger_status,
        target_50_status=target_50_status,
        target_100_status=target_100_status,
        uptime_status=uptime_status,
    )
    go_live_status = _go_live_status(
        broker_classes=broker_classes,
        expectancy_status=expectancy_status,
        campaign_ledger_status=campaign_ledger_status,
        target_50_status=target_50_status,
        uptime_status=uptime_status,
        human_status=human_status,
    )

    return {
        "GO_LIVE_WRAPUP_STATUS": go_live_status,
        "EXPECTANCY_STATUS": expectancy_status,
        "BROKER_PROOF_STATUS": broker_classes["BROKER_PROOF_STATUS"],
        "TRADE_TICKET_STATUS": broker_classes["TRADE_TICKET_STATUS"],
        "TAKE_PROFIT_STATUS": broker_classes["TAKE_PROFIT_STATUS"],
        "RISK_GATE_STATUS": broker_classes["RISK_GATE_STATUS"],
        "INCIDENT_STOP_STATUS": broker_classes["INCIDENT_STOP_STATUS"],
        "CAMPAIGN_LEDGER_STATUS": campaign_ledger_status,
        "TARGET_50_STATUS": target_50_status,
        "TARGET_100_STATUS": target_100_status,
        "UPTIME_RANGE_STATUS": uptime_status,
        "HUMAN_ARMING_CANDIDATE_STATUS": human_status,
        "LIVE_EXECUTION_AUTHORITY_STATUS": broker_classes["LIVE_EXECUTION_AUTHORITY_STATUS"],
        "CAMPAIGN_TARGET_STATUS": campaign_classes["CAMPAIGN_TARGET_STATUS"],
        "REPEATABILITY_STATUS": campaign_classes["REPEATABILITY_STATUS"],
        "PROFIT_PROOF_STATUS": campaign_classes["PROFIT_PROOF_STATUS"],
    }


def _expectancy_status(input_state: Mapping[str, Any], broker_classes: Mapping[str, str]) -> str:
    explicit = str(input_state.get("expectancy_status", "")).upper().strip()
    if explicit in {
        EXPECTANCY_PROVEN,
        EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK,
        EXPECTANCY_EVIDENCE_INSUFFICIENT,
        EXPECTANCY_NEGATIVE_OR_REJECTED,
    }:
        return explicit
    broker_expectancy = str(broker_classes.get("EXPECTANCY_STATUS", "")).upper().strip()
    if broker_expectancy in {
        EXPECTANCY_PROVEN,
        EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK,
        EXPECTANCY_EVIDENCE_INSUFFICIENT,
        EXPECTANCY_NEGATIVE_OR_REJECTED,
    }:
        return broker_expectancy
    return EXPECTANCY_EVIDENCE_INSUFFICIENT


def _campaign_ledger_status(campaign_result: Mapping[str, Any]) -> str:
    if campaign_result["campaign_count"] == 0 or campaign_result["micro_execution_count"] == 0:
        return CAMPAIGN_LEDGER_MISSING_EVIDENCE
    if campaign_result["micro_execution_count"] >= 12:
        return CAMPAIGN_LEDGER_READY_FOR_PAPER_REPLAY
    return CAMPAIGN_LEDGER_CREATED


def _target_50_status(campaign_result: Mapping[str, Any]) -> str:
    evidence = campaign_result["target_evidence"]
    if campaign_result["campaign_count"] == 0:
        return TARGET_50_EVIDENCE_MISSING
    if evidence["campaigns_at_or_above_50_percent"] <= 0:
        return TARGET_50_PLANNING_ONLY
    if evidence["evidence_ready_50_percent_campaigns"] <= 0:
        return TARGET_50_EVIDENCE_MISSING
    if campaign_result["classifications"]["REPEATABILITY_STATUS"] == campaign_ladder.REPEATABILITY_CANDIDATE:
        return TARGET_50_REPEATABILITY_REQUIRED
    return TARGET_50_PAPER_CANDIDATE


def _target_100_status(campaign_result: Mapping[str, Any]) -> str:
    evidence = campaign_result["target_evidence"]
    if campaign_result["campaign_count"] == 0:
        return TARGET_100_EVIDENCE_MISSING
    if evidence["campaigns_at_or_above_100_percent"] <= 0 and evidence["evidence_ready_50_percent_campaigns"] < 2:
        return TARGET_100_PLANNING_ONLY
    if evidence["evidence_ready_50_percent_campaigns"] < 2:
        return TARGET_100_REQUIRES_TWO_50_CAMPAIGNS
    if campaign_result["classifications"]["REPEATABILITY_STATUS"] != campaign_ladder.REPEATABILITY_PROVEN:
        return TARGET_100_REPEATABILITY_REQUIRED
    return TARGET_100_REPEATABILITY_REQUIRED


def _human_candidate_status(
    *,
    broker_classes: Mapping[str, str],
    expectancy_status: str,
    campaign_ledger_status: str,
    target_50_status: str,
    target_100_status: str,
    uptime_status: str,
) -> str:
    broker_human_status = broker_classes["HUMAN_ARMING_CANDIDATE_STATUS"]
    if broker_human_status != broker_closure.READY_FOR_HUMAN_ARMING_CANDIDATE:
        return broker_human_status
    if expectancy_status != EXPECTANCY_PROVEN:
        return broker_closure.BLOCKED_BY_EXPECTANCY_EVIDENCE
    if campaign_ledger_status == CAMPAIGN_LEDGER_MISSING_EVIDENCE:
        return broker_closure.BLOCKED_BY_EXPECTANCY_EVIDENCE
    if target_50_status not in {TARGET_50_PAPER_CANDIDATE, TARGET_50_REPEATABILITY_REQUIRED}:
        return broker_closure.BLOCKED_BY_EXPECTANCY_EVIDENCE
    if target_100_status != TARGET_100_REPEATABILITY_REQUIRED:
        return broker_closure.BLOCKED_BY_EXPECTANCY_EVIDENCE
    if uptime_status == uptime_planner.UPTIME_RANGE_BLOCKED_BY_LIVE_EVIDENCE:
        return broker_closure.BLOCKED_BY_BROKER_PROOF
    return broker_closure.READY_FOR_HUMAN_ARMING_CANDIDATE


def _go_live_status(
    *,
    broker_classes: Mapping[str, str],
    expectancy_status: str,
    campaign_ledger_status: str,
    target_50_status: str,
    uptime_status: str,
    human_status: str,
) -> str:
    if human_status == broker_closure.READY_FOR_HUMAN_ARMING_CANDIDATE:
        return WRAPUP_READY_FOR_HUMAN_ARMING_CANDIDATE
    broker_only_blocked = (
        broker_classes["BROKER_PROOF_STATUS"] != broker_closure.BROKER_PROOF_CURRENT
        and expectancy_status == EXPECTANCY_PROVEN
        and campaign_ledger_status != CAMPAIGN_LEDGER_MISSING_EVIDENCE
        and target_50_status != TARGET_50_EVIDENCE_MISSING
    )
    if broker_only_blocked:
        return WRAPUP_READY_FOR_HUMAN_INTAKE
    if (
        expectancy_status != EXPECTANCY_PROVEN
        or campaign_ledger_status == CAMPAIGN_LEDGER_MISSING_EVIDENCE
        or target_50_status == TARGET_50_EVIDENCE_MISSING
        or uptime_status == uptime_planner.UPTIME_RANGE_BLOCKED_BY_LIVE_EVIDENCE
        or human_status != broker_closure.READY_FOR_HUMAN_ARMING_CANDIDATE
        or broker_classes["BROKER_PROOF_STATUS"] != broker_closure.BROKER_PROOF_CURRENT
        or broker_classes["TRADE_TICKET_STATUS"] != broker_closure.TRADE_TICKET_READY_FROM_EVIDENCE
        or broker_classes["TAKE_PROFIT_STATUS"] != broker_closure.TAKE_PROFIT_PROVEN
        or broker_classes["RISK_GATE_STATUS"] != broker_closure.RISK_GATES_PASS
    ):
        return WRAPUP_BLOCKED_BY_EVIDENCE
    return WRAPUP_CREATED


def _blocked_gates(classes: Mapping[str, str]) -> list[str]:
    passing_values = {
        WRAPUP_READY_FOR_HUMAN_ARMING_CANDIDATE,
        EXPECTANCY_PROVEN,
        broker_closure.BROKER_PROOF_CURRENT,
        broker_closure.TRADE_TICKET_READY_FROM_EVIDENCE,
        broker_closure.TAKE_PROFIT_PROVEN,
        broker_closure.RISK_GATES_PASS,
        broker_closure.INCIDENT_STOP_PROCEDURE_PRESENT,
        CAMPAIGN_LEDGER_READY_FOR_PAPER_REPLAY,
        TARGET_50_PAPER_CANDIDATE,
        TARGET_50_REPEATABILITY_REQUIRED,
        TARGET_100_REPEATABILITY_REQUIRED,
        uptime_planner.UPTIME_RANGE_READY_FOR_PAPER_SIMULATION,
        uptime_planner.UPTIME_RANGE_READY_FOR_DEMO_REVIEW,
        uptime_planner.UPTIME_RANGE_READY_FOR_FUTURE_APPROVAL_REVIEW,
        broker_closure.READY_FOR_HUMAN_ARMING_CANDIDATE,
        broker_closure.HUMAN_ONLY_CHECKLIST_REQUIRED,
        broker_closure.DASHBOARD_DISPLAY_ONLY,
    }
    blocked = []
    for key, value in classes.items():
        if key in {"CAMPAIGN_TARGET_STATUS", "REPEATABILITY_STATUS", "PROFIT_PROOF_STATUS"}:
            continue
        if value not in passing_values:
            blocked.append(f"{key}={value}")
    return blocked


def _optional_ready_allowed(classes: Mapping[str, str]) -> bool:
    return (
        classes["GO_LIVE_WRAPUP_STATUS"] == WRAPUP_READY_FOR_HUMAN_ARMING_CANDIDATE
        and classes["HUMAN_ARMING_CANDIDATE_STATUS"] == broker_closure.READY_FOR_HUMAN_ARMING_CANDIDATE
        and classes["LIVE_EXECUTION_AUTHORITY_STATUS"] == broker_closure.HUMAN_ONLY_CHECKLIST_REQUIRED
    )


def _render_wrapup_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Profit Campaign Go-Live Wrapup V1",
            "",
            "## Go-Live Wrapup Status",
            f"`{result['classifications']['GO_LIVE_WRAPUP_STATUS']}`",
            "",
            "## Classifications",
            _table(result["classifications"]),
            "",
            "## Visible Money Facts",
            _table(result["visible_money_facts"]),
            "",
            "## Campaign Doctrine",
            "- Profits are targets and evidence goals, not guarantees.",
            "- AIOS must never hide micro execution count.",
            "- Use campaign, not misleading one trade, when grouping 12 to 99 micro executions.",
            "- Campaign reports show both campaign count and micro execution count.",
            "",
            "## Uptime Doctrine",
            "- 22/5, 22/6, and 80 percent uptime remain planning-only until evidence, broker proof, risk gates, incident stop, reconciliation, monitoring, and human approval pass.",
            "- AIOS calculates allowed trading range from evidence and broker/session rules instead of hardcoding 22/6.",
            "",
            "## Blocked Gates For Optional Human Arming Candidate Report",
            _bullets(result["blocked_gates"]),
            "",
            "## Optional Human Arming Candidate Report",
            _table(result["optional_ready_report"]),
            "",
            "## Safety",
            _table(result["safety_summary"]),
            "",
            "## Next Safe Action",
            _next_safe_action(result["classifications"], result["blocked_gates"]),
            "",
        ]
    )


def _render_ready_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Ready For Human Arming Candidate V3",
            "",
            "This report is created only when all wrap-up gates are proven. It is a human arming candidate only and does not authorize Codex, dashboard, scheduler, daemon, webhook, broker, or automated-trading execution.",
            "",
            "## Classifications",
            _table(result["classifications"]),
            "",
            "## Visible Counts",
            _table(
                {
                    "campaign_count": result["visible_money_facts"]["campaign_count"],
                    "micro_execution_count": result["visible_money_facts"]["micro_execution_count"],
                }
            ),
            "",
            "## Safety",
            _table(result["safety_summary"]),
            "",
        ]
    )


def _next_safe_action(classes: Mapping[str, str], blocked_gates: Iterable[str]) -> str:
    if classes["GO_LIVE_WRAPUP_STATUS"] == WRAPUP_READY_FOR_HUMAN_ARMING_CANDIDATE:
        return "Prepare a separate human-only arming checklist; Codex and dashboard still must not execute orders."
    if classes["BROKER_PROOF_STATUS"] != broker_closure.BROKER_PROOF_CURRENT:
        return "Anthony can provide sanitized runtime-only broker proof using the intake template; no credentials, account IDs, balances tied to IDs, or order commands."
    if classes["TARGET_50_STATUS"] in {TARGET_50_EVIDENCE_MISSING, TARGET_50_PLANNING_ONLY}:
        return "Produce a sanitized campaign ledger with visible campaign count, micro execution count, P/L, costs, risk, broker proof, and reconciliation evidence."
    if classes["TARGET_100_STATUS"] in {TARGET_100_REQUIRES_TWO_50_CAMPAIGNS, TARGET_100_EVIDENCE_MISSING}:
        return "Prove repeatability with two validated 50 percent campaign profiles or equivalent evidence before treating 100 percent as more than planning."
    return "Close blocked gates before any future arming review: " + ", ".join(blocked_gates)


def _safety_summary() -> dict[str, bool]:
    return {
        "broker_api_called": False,
        "bank_payment_call_performed": False,
        "network_call_performed": False,
        "credentials_read": False,
        "account_identifiers_read": False,
        "env_read": False,
        "secret_files_read": False,
        "live_order_executed": False,
        "demo_order_executed": False,
        "money_movement_performed": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "uptime_80_activated": False,
        "range_22_5_activated": False,
        "range_22_6_activated": False,
        "automated_trading_activated": False,
        "profit_guaranteed": False,
    }


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _bullets(values: Iterable[Any]) -> str:
    items = [str(value) for value in values]
    return "\n".join(f"- `{item}`" for item in items) if items else "- `NONE`"


def _table(values: Mapping[str, Any]) -> str:
    lines = ["| Field | Value |", "|---|---|"]
    for key, value in values.items():
        lines.append(f"| {key} | `{value}` |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(json.dumps(run_profit_campaign_go_live_wrapup(write_reports=True), indent=2, sort_keys=True))
