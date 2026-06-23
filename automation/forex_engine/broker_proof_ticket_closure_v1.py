"""Broker-proof and trade-ticket closure audit V1.

This module is deterministic and local-only. It accepts sanitized operator
input, reads only curated local evidence reports, and writes sanitized reports
only when requested. It never calls a broker, reads credentials, reads account
identifiers, reads .env files, starts services, or executes orders.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


BROKER_PROOF_CURRENT = "BROKER_PROOF_CURRENT"
BROKER_PROOF_STALE = "BROKER_PROOF_STALE"
BROKER_PROOF_MISSING = "BROKER_PROOF_MISSING"
BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE = "BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE"

TRADE_TICKET_READY_FROM_EVIDENCE = "TRADE_TICKET_READY_FROM_EVIDENCE"
TRADE_TICKET_MISSING_FIELDS = "TRADE_TICKET_MISSING_FIELDS"
TRADE_TICKET_BLOCKED_BY_RISK = "TRADE_TICKET_BLOCKED_BY_RISK"

TAKE_PROFIT_PROVEN = "TAKE_PROFIT_PROVEN"
TAKE_PROFIT_EVIDENCE_MISSING = "TAKE_PROFIT_EVIDENCE_MISSING"
TAKE_PROFIT_BLOCKED_BY_RISK = "TAKE_PROFIT_BLOCKED_BY_RISK"

RISK_GATES_PASS = "RISK_GATES_PASS"
RISK_GATES_INCOMPLETE = "RISK_GATES_INCOMPLETE"
RISK_GATES_FAIL = "RISK_GATES_FAIL"

INCIDENT_STOP_PROCEDURE_PRESENT = "INCIDENT_STOP_PROCEDURE_PRESENT"
INCIDENT_STOP_PROCEDURE_MISSING = "INCIDENT_STOP_PROCEDURE_MISSING"

READY_FOR_HUMAN_ARMING_CANDIDATE = "READY_FOR_HUMAN_ARMING_CANDIDATE"
BLOCKED_BY_BROKER_PROOF = "BLOCKED_BY_BROKER_PROOF"
BLOCKED_BY_TICKET_FIELDS = "BLOCKED_BY_TICKET_FIELDS"
BLOCKED_BY_TAKE_PROFIT = "BLOCKED_BY_TAKE_PROFIT"
BLOCKED_BY_RISK_GATE = "BLOCKED_BY_RISK_GATE"
BLOCKED_BY_EXPECTANCY_EVIDENCE = "BLOCKED_BY_EXPECTANCY_EVIDENCE"
BLOCKED_BY_INCIDENT_STOP = "BLOCKED_BY_INCIDENT_STOP"

DASHBOARD_DISPLAY_ONLY = "DASHBOARD_DISPLAY_ONLY"
HUMAN_ONLY_CHECKLIST_REQUIRED = "HUMAN_ONLY_CHECKLIST_REQUIRED"
CODEX_EXECUTION_PROHIBITED = "CODEX_EXECUTION_PROHIBITED"

EXPECTANCY_PROVEN = "EXPECTANCY_PROVEN"
EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK = "EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK"
RETURN_120_UNPROVEN = "RETURN_120_UNPROVEN"

EVIDENCE_MISSING = "EVIDENCE_MISSING"
BROKER_PROOF_REQUIRED = "BROKER_PROOF_REQUIRED"
TAKE_PROFIT_REQUIRED = "TAKE_PROFIT_REQUIRED"
RISK_GATE_REQUIRED = "RISK_GATE_REQUIRED"
HUMAN_RUNTIME_INTAKE_REQUIRED = "HUMAN_RUNTIME_INTAKE_REQUIRED"

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "Reports" / "forex_delivery"

CURATED_REPORTS = (
    "AIOS_FOREX_EXPECTANCY_TICKET_GATE_CLOSURE_V1.md",
    "AIOS_FOREX_BROKER_PROOF_INTAKE_V1.md",
    "AIOS_FOREX_TAKE_PROFIT_RISK_GATE_CLOSURE_V1.md",
    "AIOS_FOREX_NEXT_ARMING_CLASSIFICATION_V1.md",
    "AIOS_FOREX_INCIDENT_STOP_PROCEDURE_V1.md",
    "AIOS_FOREX_LIVE_EXECUTION_TO_80_UPTIME_MASTER_V2.md",
)

REPORT_FILENAMES = {
    "broker_proof": "AIOS_FOREX_BROKER_PROOF_RUNTIME_ONLY_HUMAN_INTAKE_V1.md",
    "broker_template": "AIOS_FOREX_BROKER_PROOF_RUNTIME_ONLY_HUMAN_INTAKE_TEMPLATE_V1.md",
    "ticket": "AIOS_FOREX_TRADE_TICKET_CLOSURE_V1.md",
    "take_profit": "AIOS_FOREX_TAKE_PROFIT_EVIDENCE_CLOSURE_V1.md",
    "next_gate": "AIOS_FOREX_NEXT_HUMAN_ARMING_CANDIDATE_GATE_V1.md",
}
OPTIONAL_READY_REPORT = "AIOS_FOREX_READY_FOR_HUMAN_ARMING_CANDIDATE_V3.md"

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

FORBIDDEN_SKIP_PATHS = (
    ".env",
    ".env.*",
    "secrets/",
    "credentials/",
    "config/secrets/",
    "docs/legal/",
    "broker credential files",
    "account identifier files",
    "raw broker payloads",
)

TICKET_FIELDS = (
    "aios_trade_number",
    "session_id",
    "campaign_id",
    "micro_execution_id",
    "candidate_id",
    "setup_id",
    "strategy_id",
    "signal_id",
    "instrument",
    "side",
    "mode",
    "micro_size_units",
    "order_type",
    "planned_entry",
    "stop_loss",
    "take_profit",
    "max_loss_gate",
    "daily_stop_gate",
    "kill_switch_state",
    "one_order_only_rule",
    "broker_proof_reference",
    "credential_handling_rule",
    "post_trade_reconciliation_rule",
    "incident_stop_rule",
    "evidence_path",
)

REQUIRED_TICKET_FIELDS = (
    "aios_trade_number",
    "session_id",
    "candidate_id",
    "setup_id",
    "strategy_id",
    "instrument",
    "side",
    "mode",
    "micro_size_units",
    "stop_loss",
    "take_profit",
    "max_loss_gate",
    "daily_stop_gate",
    "kill_switch_state",
    "one_order_only_rule",
    "broker_proof_reference",
    "credential_handling_rule",
    "post_trade_reconciliation_rule",
    "incident_stop_rule",
    "evidence_path",
)

RISK_FIELDS = (
    "micro_size_units",
    "stop_loss",
    "take_profit",
    "max_loss_gate",
    "daily_stop_gate",
    "kill_switch_state",
    "one_order_only_rule",
)

BROKER_PROOF_REQUIRED_FIELDS = (
    "broker_alias",
    "environment",
    "proof_timestamp",
    "instrument_availability",
    "connection_proof_status",
    "order_placement_disabled_confirmation",
    "account_id_redacted_confirmation",
    "credential_not_pasted_confirmation",
    "credential_not_persisted_confirmation",
    "broker_ui_balance_redacted_confirmation",
    "human_operator_confirmation",
)


def run_broker_proof_ticket_closure(
    input_state: dict[str, Any] | None = None,
    write_reports: bool = False,
) -> dict[str, Any]:
    """Close broker-proof and ticket gates from local sanitized evidence only."""

    sanitized_input, redacted_fields = _sanitize_input(input_state or {})
    evidence = _empty_evidence(redacted_fields)
    evidence["files_skipped_for_safety"].extend(FORBIDDEN_SKIP_PATHS)
    _apply_report_evidence(evidence)
    _apply_input_evidence(evidence, sanitized_input)

    classifications = _classify(evidence)
    missing = _missing_evidence(evidence, classifications)
    result = {
        "schema": "AIOS_FOREX_BROKER_PROOF_TICKET_CLOSURE_V1",
        "write_reports_requested": bool(write_reports),
        "files_inspected": tuple(evidence["files_inspected"]),
        "files_skipped_for_safety": tuple(_unique(evidence["files_skipped_for_safety"])),
        "classifications": classifications,
        "found_evidence": _public_evidence(evidence),
        "missing_evidence": tuple(missing),
        "next_exact_action": _next_exact_action(classifications, missing),
        "reports": {
            "written": tuple(),
            "allowed_output_paths": tuple(f"Reports/forex_delivery/{name}" for name in REPORT_FILENAMES.values()),
            "optional_ready_candidate_report_created": False,
            "optional_ready_candidate_report_reason": "gates_not_all_proven",
        },
        "sanitization": {
            "redacted_fields": tuple(redacted_fields),
            "sensitive_input_rejected_or_redacted": bool(redacted_fields),
            "account_ids_persisted": False,
            "credentials_persisted": False,
            "broker_order_ids_persisted": False,
        },
        "safety_summary": _safety_summary(),
    }

    if write_reports:
        written = _write_reports(result)
        result["reports"] = {
            **result["reports"],
            "written": tuple(_display_path(path) for path in written),
            "optional_ready_candidate_report_created": False,
            "optional_ready_candidate_report_reason": "profit_campaign_wrapup_gate_required",
        }

    return result


def _empty_evidence(redacted_fields: list[str]) -> dict[str, Any]:
    return {
        "files_inspected": [],
        "files_skipped_for_safety": [],
        "redacted_fields": list(redacted_fields),
        "expectancy_status": EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK,
        "return_status": RETURN_120_UNPROVEN,
        "ticket": {field: None for field in TICKET_FIELDS},
        "broker_proof": {},
        "broker_proof_source": None,
        "broker_proof_stale": False,
        "dashboard_fixture_broker_proof": False,
        "take_profit_explicit_none": False,
        "risk_fail_reasons": [],
        "risk_conflicts": [],
        "incident_stop_procedure_present": False,
        "evidence_sources": {},
    }


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


def _apply_report_evidence(evidence: dict[str, Any]) -> None:
    for name in CURATED_REPORTS:
        path = REPORTS_DIR / name
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        evidence["files_inspected"].append(_display_path(path))
        _apply_text_statuses(evidence, text, _display_path(path))


def _apply_text_statuses(evidence: dict[str, Any], text: str, source: str) -> None:
    lower = text.lower()
    for label in (
        "EXPECTANCY_STATUS",
        "RETURN_STATUS",
        "TRADE_TICKET_STATUS",
        "TAKE_PROFIT_STATUS",
        "BROKER_PROOF_STATUS",
        "INCIDENT_STOP_STATUS",
        "NEXT_ARMING_STATUS",
        "UPTIME_80_STATUS",
    ):
        value = _extract_backticked_status(text, label)
        if value == EXPECTANCY_PROVEN:
            evidence["expectancy_status"] = value
        elif label == "EXPECTANCY_STATUS" and value:
            evidence["expectancy_status"] = value
        elif label == "RETURN_STATUS" and value:
            evidence["return_status"] = value

    if "incident stop procedure" in lower:
        evidence["incident_stop_procedure_present"] = True
        evidence["evidence_sources"]["incident_stop_procedure_present"] = source
    if BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE.lower() in lower:
        evidence["broker_proof_source"] = HUMAN_RUNTIME_INTAKE_REQUIRED
    if "historical/demo" in lower or "historical one-unit" in lower or "prior proof does not replace current" in lower:
        evidence["broker_proof_stale"] = True
    if TAKE_PROFIT_EVIDENCE_MISSING.lower() in lower or "take-profit proof is not closed" in lower:
        evidence["take_profit_explicit_none"] = True
    if "max-loss evidence exists but is not conflict-free" in lower or "current exact value conflicts" in lower:
        evidence["risk_conflicts"].append("max_loss_gate_conflict")

    _set_ticket_from_label(evidence, "candidate_id", _extract_table_value(text, "candidate ID"), source)
    _set_ticket_from_label(evidence, "instrument", _extract_table_value(text, "instrument"), source)
    _set_ticket_from_label(evidence, "side", _normalize_side(_extract_table_value(text, "side")), source)
    _set_ticket_from_label(evidence, "stop_loss", _extract_table_value(text, "stop loss"), source)
    _set_ticket_from_label(evidence, "micro_size_units", _extract_table_value(text, "micro-size/units"), source)
    _set_ticket_from_label(evidence, "daily_stop_gate", _extract_table_value(text, "daily-stop gate"), source)
    _set_ticket_from_label(evidence, "kill_switch_state", _extract_table_value(text, "kill-switch"), source)
    _set_ticket_from_label(evidence, "one_order_only_rule", _extract_table_value(text, "one-order-only"), source)


def _apply_input_evidence(evidence: dict[str, Any], input_state: Mapping[str, Any]) -> None:
    if not input_state:
        return

    if input_state.get("expectancy_status"):
        evidence["expectancy_status"] = str(input_state["expectancy_status"])
    if input_state.get("return_status"):
        evidence["return_status"] = str(input_state["return_status"])
    if input_state.get("incident_stop_procedure_present") is True:
        evidence["incident_stop_procedure_present"] = True
        evidence["evidence_sources"]["incident_stop_procedure_present"] = "input_state"

    ticket = input_state.get("ticket", {})
    if isinstance(ticket, Mapping):
        for field in TICKET_FIELDS:
            if field in ticket:
                _set_ticket_from_label(evidence, field, ticket[field], "input_state.ticket")

    for field in TICKET_FIELDS:
        if field in input_state:
            _set_ticket_from_label(evidence, field, input_state[field], "input_state")

    broker_proof = input_state.get("broker_proof") or input_state.get("sanitized_broker_proof") or {}
    if isinstance(broker_proof, Mapping):
        evidence["broker_proof"] = dict(broker_proof)
        evidence["broker_proof_source"] = str(broker_proof.get("source_label") or "input_state.broker_proof")
        if str(broker_proof.get("source_label", "")).lower() == "dashboard_fixture":
            evidence["dashboard_fixture_broker_proof"] = True
        if str(broker_proof.get("source_type", "")).lower() == "dashboard_fixture":
            evidence["dashboard_fixture_broker_proof"] = True
        if broker_proof.get("stale") is True:
            evidence["broker_proof_stale"] = True

    if input_state.get("dashboard_fixture_broker_proof") is True:
        evidence["dashboard_fixture_broker_proof"] = True
    if input_state.get("codex_execution_requested") is True:
        evidence["codex_execution_requested"] = True


def _classify(evidence: Mapping[str, Any]) -> dict[str, str]:
    broker_status = _classify_broker_proof(evidence)
    risk_status = _classify_risk_gates(evidence)
    take_profit_status = _classify_take_profit(evidence, risk_status)
    ticket_status = _classify_ticket(evidence, risk_status)
    incident_status = (
        INCIDENT_STOP_PROCEDURE_PRESENT
        if evidence.get("incident_stop_procedure_present")
        else INCIDENT_STOP_PROCEDURE_MISSING
    )
    human_status = _classify_human_candidate(
        evidence=evidence,
        broker_status=broker_status,
        ticket_status=ticket_status,
        take_profit_status=take_profit_status,
        risk_status=risk_status,
        incident_status=incident_status,
    )
    live_status = _classify_live_authority(evidence, human_status)
    return {
        "BROKER_PROOF_STATUS": broker_status,
        "TRADE_TICKET_STATUS": ticket_status,
        "TAKE_PROFIT_STATUS": take_profit_status,
        "RISK_GATE_STATUS": risk_status,
        "INCIDENT_STOP_STATUS": incident_status,
        "HUMAN_ARMING_CANDIDATE_STATUS": human_status,
        "LIVE_EXECUTION_AUTHORITY_STATUS": live_status,
        "EXPECTANCY_STATUS": str(evidence.get("expectancy_status") or EXPECTANCY_DIRECTIONAL_BUT_SAMPLE_WEAK),
        "RETURN_STATUS": str(evidence.get("return_status") or RETURN_120_UNPROVEN),
    }


def _classify_broker_proof(evidence: Mapping[str, Any]) -> str:
    proof = evidence.get("broker_proof")
    if evidence.get("dashboard_fixture_broker_proof"):
        return BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE
    if not isinstance(proof, Mapping) or not proof:
        return BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE
    if evidence.get("broker_proof_stale") or _proof_timestamp_stale(proof.get("proof_timestamp")):
        return BROKER_PROOF_STALE
    missing = [field for field in BROKER_PROOF_REQUIRED_FIELDS if _missing(proof.get(field))]
    if missing:
        return BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE
    if str(proof.get("environment")).upper() not in {"DEMO", "LIVE_PROOF_ONLY"}:
        return BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE
    confirmations = (
        proof.get("order_placement_disabled_confirmation"),
        proof.get("account_id_redacted_confirmation"),
        proof.get("credential_not_pasted_confirmation"),
        proof.get("credential_not_persisted_confirmation"),
        proof.get("broker_ui_balance_redacted_confirmation"),
        proof.get("human_operator_confirmation"),
    )
    if all(value is True for value in confirmations):
        return BROKER_PROOF_CURRENT
    return BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE


def _classify_risk_gates(evidence: Mapping[str, Any]) -> str:
    ticket = evidence["ticket"]
    if evidence.get("risk_fail_reasons"):
        return RISK_GATES_FAIL
    if any(_risk_value_fails(ticket.get(field)) for field in RISK_FIELDS):
        return RISK_GATES_FAIL
    if evidence.get("risk_conflicts"):
        return RISK_GATES_INCOMPLETE
    missing = [field for field in RISK_FIELDS if _missing(ticket.get(field))]
    if missing:
        return RISK_GATES_INCOMPLETE
    return RISK_GATES_PASS


def _classify_take_profit(evidence: Mapping[str, Any], risk_status: str) -> str:
    if risk_status == RISK_GATES_FAIL:
        return TAKE_PROFIT_BLOCKED_BY_RISK
    value = evidence["ticket"].get("take_profit")
    if _missing(value) or _is_none_value(value) or evidence.get("take_profit_explicit_none"):
        return TAKE_PROFIT_EVIDENCE_MISSING
    return TAKE_PROFIT_PROVEN


def _classify_ticket(evidence: Mapping[str, Any], risk_status: str) -> str:
    if risk_status == RISK_GATES_FAIL:
        return TRADE_TICKET_BLOCKED_BY_RISK
    missing = [field for field in REQUIRED_TICKET_FIELDS if _missing(evidence["ticket"].get(field))]
    if missing:
        return TRADE_TICKET_MISSING_FIELDS
    if _is_none_value(evidence["ticket"].get("take_profit")):
        return TRADE_TICKET_MISSING_FIELDS
    return TRADE_TICKET_READY_FROM_EVIDENCE


def _classify_human_candidate(
    *,
    evidence: Mapping[str, Any],
    broker_status: str,
    ticket_status: str,
    take_profit_status: str,
    risk_status: str,
    incident_status: str,
) -> str:
    expectancy_status = str(evidence.get("expectancy_status") or "")
    micro_exception = evidence.get("expectancy_micro_exception_approved") is True
    if expectancy_status != EXPECTANCY_PROVEN and not micro_exception:
        return BLOCKED_BY_EXPECTANCY_EVIDENCE
    if broker_status != BROKER_PROOF_CURRENT:
        return BLOCKED_BY_BROKER_PROOF
    if risk_status == RISK_GATES_FAIL:
        return BLOCKED_BY_RISK_GATE
    if ticket_status != TRADE_TICKET_READY_FROM_EVIDENCE:
        return BLOCKED_BY_TICKET_FIELDS
    if take_profit_status != TAKE_PROFIT_PROVEN:
        return BLOCKED_BY_TAKE_PROFIT
    if risk_status != RISK_GATES_PASS:
        return BLOCKED_BY_RISK_GATE
    if incident_status != INCIDENT_STOP_PROCEDURE_PRESENT:
        return BLOCKED_BY_INCIDENT_STOP
    return READY_FOR_HUMAN_ARMING_CANDIDATE


def _classify_live_authority(evidence: Mapping[str, Any], human_status: str) -> str:
    if evidence.get("codex_execution_requested"):
        return CODEX_EXECUTION_PROHIBITED
    if human_status == READY_FOR_HUMAN_ARMING_CANDIDATE:
        return HUMAN_ONLY_CHECKLIST_REQUIRED
    return DASHBOARD_DISPLAY_ONLY


def _missing_evidence(evidence: Mapping[str, Any], classifications: Mapping[str, str]) -> list[str]:
    missing: list[str] = []
    ticket = evidence["ticket"]
    for field in REQUIRED_TICKET_FIELDS:
        if _missing(ticket.get(field)) or (field == "take_profit" and _is_none_value(ticket.get(field))):
            missing.append(field)
    if classifications["BROKER_PROOF_STATUS"] != BROKER_PROOF_CURRENT:
        missing.append("current_sanitized_broker_proof")
    if classifications["TAKE_PROFIT_STATUS"] != TAKE_PROFIT_PROVEN:
        missing.append("deterministic_take_profit_evidence")
    if classifications["RISK_GATE_STATUS"] != RISK_GATES_PASS:
        for field in RISK_FIELDS:
            if _missing(ticket.get(field)):
                missing.append(f"risk_gate:{field}")
        missing.extend(str(item) for item in evidence.get("risk_conflicts", ()))
    if classifications["INCIDENT_STOP_STATUS"] != INCIDENT_STOP_PROCEDURE_PRESENT:
        missing.append("incident_stop_procedure")
    if classifications["EXPECTANCY_STATUS"] != EXPECTANCY_PROVEN:
        missing.append("expectancy_proof")
    return _unique(missing)


def _next_exact_action(classifications: Mapping[str, str], missing: Iterable[str]) -> str:
    if classifications["HUMAN_ARMING_CANDIDATE_STATUS"] == READY_FOR_HUMAN_ARMING_CANDIDATE:
        return "Create a human-only checklist packet; Codex and dashboard still must not execute orders."
    if classifications["HUMAN_ARMING_CANDIDATE_STATUS"] == BLOCKED_BY_EXPECTANCY_EVIDENCE:
        return "Produce sufficient paper/demo expectancy evidence with passing walk-forward proof before any arming candidate."
    if classifications["BROKER_PROOF_STATUS"] != BROKER_PROOF_CURRENT:
        return "Anthony must provide sanitized runtime-only broker proof using the intake template; no credentials or account IDs."
    if classifications["TAKE_PROFIT_STATUS"] != TAKE_PROFIT_PROVEN:
        return "Provide deterministic take-profit evidence or a separately approved no-take-profit exception."
    if classifications["RISK_GATE_STATUS"] != RISK_GATES_PASS:
        return "Close conflict-free max-loss, daily-stop, kill-switch, stop-loss, micro-size, and one-order-only risk evidence."
    fields = ", ".join(missing) if missing else "UNKNOWN"
    return f"Close missing evidence fields: {fields}."


def _write_reports(result: Mapping[str, Any]) -> list[Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    renderers = {
        REPORT_FILENAMES["broker_proof"]: _render_broker_proof_report,
        REPORT_FILENAMES["broker_template"]: _render_broker_template,
        REPORT_FILENAMES["ticket"]: _render_ticket_report,
        REPORT_FILENAMES["take_profit"]: _render_take_profit_report,
        REPORT_FILENAMES["next_gate"]: _render_next_gate_report,
    }
    written: list[Path] = []
    for filename, renderer in renderers.items():
        path = REPORTS_DIR / filename
        path.write_text(renderer(result), encoding="utf-8")
        written.append(path)
    return written


def _render_broker_proof_report(result: Mapping[str, Any]) -> str:
    classes = result["classifications"]
    return "\n".join(
        [
            "# AIOS Forex Broker Proof Runtime-Only Human Intake V1",
            "",
            "## Objective",
            "Define the sanitized runtime-only broker proof Anthony must supply before any future arming review. Codex does not call brokers, read credentials, read account IDs, or execute orders.",
            "",
            "## Broker Proof Status",
            f"`{classes['BROKER_PROOF_STATUS']}`",
            "",
            "## Required Sanitized Proof Fields",
            _bullet_lines(BROKER_PROOF_REQUIRED_FIELDS),
            "",
            "## Forbidden Fields",
            _bullet_lines(
                (
                    "API keys",
                    "passwords",
                    "account IDs",
                    "card/bank data",
                    "account balances tied to account IDs",
                    "raw broker secrets",
                    "copied .env content",
                    "live order commands",
                    "auto-trading commands",
                )
            ),
            "",
            "## Credential/Account ID Bans",
            "- credentials must not be pasted, read, persisted, logged, or reported",
            "- account IDs and broker order IDs must not be persisted, logged, or reported",
            "",
            "## Runtime-Only Proof Doctrine",
            "Broker proof must be supplied as sanitized human intake at arming time. Historical/demo proof and dashboard fixtures are not current broker proof.",
            "",
            "## Codex Safety Statements",
            "- no broker call performed",
            "- no credential read",
            "- no account ID read",
            "- no order executed",
            "",
            "## Next Safe Action",
            result["next_exact_action"],
            "",
        ]
    )


def _render_broker_template(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Broker Proof Runtime-Only Human Intake Template V1",
            "",
            "## Sanitized Proof Fields To Provide",
            "- broker alias, not account ID: `BROKER_ALIAS_ONLY`",
            "- environment: `DEMO` or `LIVE_PROOF_ONLY`",
            "- proof timestamp: `ISO-8601`",
            "- instrument availability: `AVAILABLE_OR_BLOCKED`",
            "- spread snapshot, if visible: `SPREAD_ALIAS_OR_WITHIN_CAP`",
            "- connection proof status: `CURRENT_OR_BLOCKED`",
            "- order placement disabled confirmation: `true`",
            "- account ID redacted confirmation: `true`",
            "- credential not pasted confirmation: `true`",
            "- credential not persisted confirmation: `true`",
            "- screenshot/evidence filename alias if applicable: `SANITIZED_ALIAS`",
            "- broker UI balance redacted confirmation: `true`",
            "- risk disclaimer acknowledgement: `true`",
            "- human operator confirmation: `true`",
            "- next safe action: `STOP_OR_REVIEW_PACKET`",
            "",
            "## Explicitly Forbidden",
            "- API keys",
            "- passwords",
            "- account IDs",
            "- card/bank data",
            "- account balances tied to account IDs",
            "- raw broker secrets",
            "- copied .env content",
            "- live order commands",
            "- auto-trading commands",
            "",
            "## Safety Statement",
            "This template is intake-only. It does not authorize broker calls, order placement, money movement, automation, scheduler, daemon, webhook, or dashboard execution authority.",
            "",
        ]
    )


def _render_ticket_report(result: Mapping[str, Any]) -> str:
    classes = result["classifications"]
    evidence = result["found_evidence"]
    ticket = evidence["ticket"]
    return "\n".join(
        [
            "# AIOS Forex Trade Ticket Closure V1",
            "",
            "## Ticket Fields Found",
            _table({field: ticket.get(field) or _fallback_for_field(field) for field in TICKET_FIELDS}),
            "",
            "## Ticket Fields Missing",
            _bullet_lines(field for field in result["missing_evidence"] if field in REQUIRED_TICKET_FIELDS),
            "",
            "## Ticket Closure Classification",
            f"`{classes['TRADE_TICKET_STATUS']}`",
            "",
            "## Execution Authority Status",
            f"`{classes['LIVE_EXECUTION_AUTHORITY_STATUS']}`",
            "",
            "## Evidence Sources",
            _bullet_lines(result["files_inspected"] or ("NONE",)),
            "",
            "## Next Exact Closure Action",
            result["next_exact_action"],
            "",
        ]
    )


def _render_take_profit_report(result: Mapping[str, Any]) -> str:
    classes = result["classifications"]
    ticket = result["found_evidence"]["ticket"]
    return "\n".join(
        [
            "# AIOS Forex Take Profit Evidence Closure V1",
            "",
            "## Take-Profit Evidence Found",
            f"`{ticket.get('take_profit') or TAKE_PROFIT_REQUIRED}`",
            "",
            "## Stop-Loss Evidence Found",
            f"`{ticket.get('stop_loss') or EVIDENCE_MISSING}`",
            "",
            "## Risk/Reward Evidence If Available",
            _table(
                {
                    "max_loss_gate": ticket.get("max_loss_gate") or RISK_GATE_REQUIRED,
                    "daily_stop_gate": ticket.get("daily_stop_gate") or RISK_GATE_REQUIRED,
                    "kill_switch_state": ticket.get("kill_switch_state") or RISK_GATE_REQUIRED,
                    "one_order_only_rule": ticket.get("one_order_only_rule") or RISK_GATE_REQUIRED,
                }
            ),
            "",
            "## Missing Take-Profit Fields",
            _bullet_lines(field for field in result["missing_evidence"] if "take_profit" in field),
            "",
            "## Take-Profit Classification",
            f"`{classes['TAKE_PROFIT_STATUS']}`",
            "",
            "## Next Exact Closure Action",
            "Provide deterministic take-profit evidence or a separately approved no-take-profit exception. Current closure requires take-profit proof.",
            "",
        ]
    )


def _render_next_gate_report(result: Mapping[str, Any]) -> str:
    classes = result["classifications"]
    ready = [key for key, value in classes.items() if value.endswith("_PASS") or value.endswith("_PRESENT") or value.endswith("_CURRENT")]
    blocked = [key for key, value in classes.items() if "BLOCKED" in value or "MISSING" in value or "INCOMPLETE" in value or "STALE" in value or "REQUIRES" in value]
    return "\n".join(
        [
            "# AIOS Forex Next Human Arming Candidate Gate V1",
            "",
            "## All Classifications",
            _table(classes),
            "",
            "## Gates Passing",
            _bullet_lines(ready),
            "",
            "## Gates Blocked",
            _bullet_lines(blocked),
            "",
            "## Missing Evidence",
            _bullet_lines(result["missing_evidence"]),
            "",
            "## Optional Human Arming Candidate Report Created",
            str(result["reports"]["optional_ready_candidate_report_created"]),
            "",
            "## Next Safe Action",
            result["next_exact_action"],
            "",
        ]
    )


def _render_ready_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Ready For Human Arming Candidate V3",
            "",
            "This report is created only when broker proof, trade ticket, take-profit, risk gates, incident stop, and human arming candidate status are all proven.",
            "",
            "## Classifications",
            _table(result["classifications"]),
            "",
            "## Safety",
            "- Human arming candidate only.",
            "- Codex did not place an order.",
            "- Dashboard does not place orders.",
            "- No broker call, credential read, account ID read, or money movement occurred.",
            "",
        ]
    )


def _ready_report_allowed(classes: Mapping[str, str]) -> bool:
    return (
        classes["BROKER_PROOF_STATUS"] == BROKER_PROOF_CURRENT
        and classes["TRADE_TICKET_STATUS"] == TRADE_TICKET_READY_FROM_EVIDENCE
        and classes["TAKE_PROFIT_STATUS"] == TAKE_PROFIT_PROVEN
        and classes["RISK_GATE_STATUS"] == RISK_GATES_PASS
        and classes["INCIDENT_STOP_STATUS"] == INCIDENT_STOP_PROCEDURE_PRESENT
        and classes["HUMAN_ARMING_CANDIDATE_STATUS"] == READY_FOR_HUMAN_ARMING_CANDIDATE
    )


def _public_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ticket": {field: _json_safe(evidence["ticket"].get(field)) for field in TICKET_FIELDS},
        "broker_proof": {
            key: _json_safe(value)
            for key, value in evidence.get("broker_proof", {}).items()
            if not any(part in str(key).lower() for part in SENSITIVE_KEY_PARTS)
        },
        "broker_proof_source": evidence.get("broker_proof_source"),
        "broker_proof_stale": evidence.get("broker_proof_stale"),
        "dashboard_fixture_broker_proof": evidence.get("dashboard_fixture_broker_proof"),
        "take_profit_explicit_none": evidence.get("take_profit_explicit_none"),
        "risk_conflicts": tuple(evidence.get("risk_conflicts", ())),
        "incident_stop_procedure_present": evidence.get("incident_stop_procedure_present"),
        "expectancy_status": evidence.get("expectancy_status"),
        "return_status": evidence.get("return_status"),
    }


def _safety_summary() -> dict[str, bool]:
    return {
        "broker_call_performed": False,
        "bank_payment_call_performed": False,
        "network_call_performed": False,
        "credentials_read": False,
        "account_identifiers_read": False,
        "env_read": False,
        "secret_files_read": False,
        "live_order_executed_by_codex": False,
        "demo_order_executed_by_codex": False,
        "paper_order_mutated_by_codex": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "uptime_80_activated": False,
        "automation_22_5_activated": False,
        "money_movement_performed": False,
    }


def _extract_backticked_status(text: str, label: str) -> str | None:
    match = re.search(rf"{re.escape(label)}\s*\|\s*`([^`]+)`", text)
    if match:
        return match.group(1).strip()
    match = re.search(rf"{re.escape(label)}\s*[:|]\s*`?([A-Z0-9_]+)`?", text)
    return match.group(1).strip() if match else None


def _extract_table_value(text: str, label: str) -> str | None:
    pattern = rf"\|\s*{re.escape(label)}\s*\|\s*`?([^`|\n]+)`?\s*\|"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip()
    return None if value.upper() == "UNKNOWN" else value


def _set_ticket_from_label(evidence: dict[str, Any], field: str, value: Any, source: str) -> None:
    if field not in evidence["ticket"] or _missing(value):
        return
    if evidence["ticket"].get(field) in (None, "", EVIDENCE_MISSING):
        evidence["ticket"][field] = value
        evidence["evidence_sources"][field] = source


def _normalize_side(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if "BUY" in text or "LONG" in text:
        return "BUY"
    if "SELL" in text or "SHORT" in text:
        return "SELL"
    return text or None


def _proof_timestamp_stale(value: Any) -> bool:
    if _missing(value):
        return True
    try:
        text = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        age_seconds = (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds()
        return age_seconds < 0 or age_seconds > 24 * 60 * 60
    except ValueError:
        return True


def _risk_value_fails(value: Any) -> bool:
    if _missing(value):
        return False
    text = str(value).strip().lower()
    return text in {"false", "fail", "failed", "blocked", "breached", "not_clear", "not clear"}


def _missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == "" or value.strip().upper() in {
            EVIDENCE_MISSING,
            BROKER_PROOF_REQUIRED,
            TAKE_PROFIT_REQUIRED,
            RISK_GATE_REQUIRED,
            HUMAN_RUNTIME_INTAKE_REQUIRED,
            "UNKNOWN",
            "LOCKED",
        }
    return False


def _is_none_value(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in {"none", "no", "not used", "explicit none"}


def _fallback_for_field(field: str) -> str:
    if field == "take_profit":
        return TAKE_PROFIT_REQUIRED
    if field == "broker_proof_reference":
        return BROKER_PROOF_REQUIRED
    if field in RISK_FIELDS:
        return RISK_GATE_REQUIRED
    if field in {"mode", "credential_handling_rule", "post_trade_reconciliation_rule", "incident_stop_rule"}:
        return DASHBOARD_DISPLAY_ONLY
    return EVIDENCE_MISSING


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return tuple(_json_safe(item) for item in value)
    return value


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


def _bullet_lines(values: Iterable[Any]) -> str:
    items = [str(value) for value in values]
    if not items:
        return "- NONE"
    return "\n".join(f"- `{item}`" for item in items)


def _table(values: Mapping[str, Any]) -> str:
    lines = ["| Field | Value |", "|---|---|"]
    for key, value in values.items():
        rendered = value if value not in (None, "") else "UNKNOWN"
        lines.append(f"| {key} | `{rendered}` |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(json.dumps(run_broker_proof_ticket_closure(write_reports=True), indent=2, sort_keys=True))
