"""Local-only supervised demo operational validation runner for AIOS Forex.

The runner decides whether a selected review-ready candidate is eligible to
enter supervised demo validation. It does not connect to brokers, read
credentials, access environment files, activate runtime, place orders, or move
money.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


PACKET_ID = "PKT-FOREX-001"
MISSION_ID = "MISSION-AIOS-001"
PROGRAM_ID = "PRG-FOREX-001"
EPIC_ID = "EPC-FOREX-001"
BUCKET_ID = "BKT-FOREX-001"

READY_FOR_SUPERVISED_DEMO_VALIDATION = "READY_FOR_SUPERVISED_DEMO_VALIDATION"
REQUIRE_MORE_EVIDENCE = "REQUIRE_MORE_EVIDENCE"
BLOCKED_BY_SAFETY_BOUNDARY = "BLOCKED_BY_SAFETY_BOUNDARY"
REJECTED_FOR_DEMO_VALIDATION = "REJECTED_FOR_DEMO_VALIDATION"

RESULT_KEYS = (
    "packet_id",
    "mission_id",
    "program_id",
    "epic_id",
    "bucket_id",
    "candidate_id",
    "candidate_status",
    "operational_validation_status",
    "allowed_to_enter_supervised_demo_validation",
    "blockers",
    "required_evidence",
    "safety_boundary",
    "next_action",
)

READINESS_FIELDS = (
    "selected_candidate_present",
    "candidate_review_ready",
    "owner_review_required",
    "risk_boundary_confirmed",
    "evidence_collection_ready",
    "operational_health_ready",
    "no_open_trade",
    "no_pending_order",
    "no_live_endpoint",
    "no_credential_access",
    "no_account_id_access",
    "no_money_movement",
    "no_scheduler_activation",
    "no_daemon_activation",
    "no_webhook_activation",
)

HARD_SAFETY_FIELDS = (
    "no_live_endpoint",
    "no_credential_access",
    "no_account_id_access",
    "no_money_movement",
    "no_scheduler_activation",
    "no_daemon_activation",
    "no_webhook_activation",
)

OWNER_APPROVAL_READY_STATUSES = frozenset(
    ("APPROVED_FOR_SUPERVISED_DEMO_VALIDATION", "APPROVED_REVIEW_ONLY")
)
KILL_SWITCH_READY_STATES = frozenset(("ARMED", "READY"))
REVIEW_READY_STATUSES = frozenset(
    ("REVIEW_READY", "READY_FOR_REVIEW", "REVIEW_READY_CANDIDATE")
)
REJECTION_STATUS_FRAGMENTS = frozenset(("REJECT", "BLOCKED", "FAILED", "FAIL"))
EXPLICIT_REJECTION_STATUSES = frozenset(
    ("NOT_REVIEW_READY", "NOT_READY", "REJECTED_FOR_DEMO_VALIDATION")
)

TRUE_VALUES = frozenset(("1", "true", "yes", "y", "pass", "passed", "ready", "armed"))
FALSE_VALUES = frozenset(
    ("0", "false", "no", "n", "fail", "failed", "blocked", "active", "detected")
)

REPORT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_SUPERVISED_DEMO_OPERATIONAL_VALIDATION_RUNNER_V1.md"
)


def evaluate_supervised_demo_operational_validation(input_data: dict) -> dict:
    """Evaluate whether a local candidate may enter supervised demo validation."""

    data = input_data if isinstance(input_data, dict) else {}
    normalized = _normalize_input(data)
    flags = normalized["flags"]
    candidate_status = _candidate_status(normalized)

    hard_safety_failures = [
        field for field in HARD_SAFETY_FIELDS if flags[field] is False
    ]
    rejection_reasons = _candidate_rejection_reasons(normalized)
    readiness_gaps = _readiness_gaps(normalized)

    if hard_safety_failures:
        operational_status = BLOCKED_BY_SAFETY_BOUNDARY
        blockers = [
            f"safety boundary false: {field}" for field in hard_safety_failures
        ]
        required_evidence = [
            f"{field} must be restored to true" for field in hard_safety_failures
        ]
        next_action = (
            "Stop and repair safety boundary evidence before any supervised "
            "demo validation review."
        )
    elif rejection_reasons:
        operational_status = REJECTED_FOR_DEMO_VALIDATION
        blockers = rejection_reasons
        required_evidence = [
            "selected candidate must be review-ready and not explicitly rejected"
        ]
        next_action = (
            "Replace or repair the candidate evidence before rerunning "
            "PKT-FOREX-001."
        )
    elif not readiness_gaps:
        operational_status = READY_FOR_SUPERVISED_DEMO_VALIDATION
        blockers = []
        required_evidence = []
        next_action = (
            "Create the PKT-FOREX-002 Demo Trade Evidence Collector packet; "
            "do not route or place trades."
        )
    else:
        operational_status = REQUIRE_MORE_EVIDENCE
        blockers = [f"missing or incomplete evidence: {gap}" for gap in readiness_gaps]
        required_evidence = readiness_gaps
        next_action = (
            "Collect missing local readiness evidence and rerun this validator "
            "before supervised demo validation."
        )

    return {
        "packet_id": PACKET_ID,
        "mission_id": MISSION_ID,
        "program_id": PROGRAM_ID,
        "epic_id": EPIC_ID,
        "bucket_id": BUCKET_ID,
        "candidate_id": normalized["candidate_id"],
        "candidate_status": candidate_status,
        "operational_validation_status": operational_status,
        "allowed_to_enter_supervised_demo_validation": (
            operational_status == READY_FOR_SUPERVISED_DEMO_VALIDATION
        ),
        "blockers": blockers,
        "required_evidence": required_evidence,
        "safety_boundary": _safety_boundary(flags, hard_safety_failures),
        "next_action": next_action,
    }


def run_supervised_demo_operational_validation(
    input_data: dict | None = None, write_report: bool = False
) -> dict:
    """Run the local validator with supplied input or safe sample input."""

    result = evaluate_supervised_demo_operational_validation(
        safe_sample_input() if input_data is None else input_data
    )
    if write_report:
        REPORT_PATH.write_text(_report_markdown(result), encoding="utf-8")
    return result


def safe_sample_input() -> dict:
    """Return a safe deterministic sample that requires more evidence."""

    return {
        "candidate_id": "sample-review-ready-candidate",
        "candidate_status": "REVIEW_READY",
        "selected_candidate_present": True,
        "candidate_review_ready": True,
        "owner_review_required": True,
        "risk_boundary_confirmed": True,
        "evidence_collection_ready": False,
        "operational_health_ready": False,
        "no_open_trade": True,
        "no_pending_order": True,
        "no_live_endpoint": True,
        "no_credential_access": True,
        "no_account_id_access": True,
        "no_money_movement": True,
        "no_scheduler_activation": True,
        "no_daemon_activation": True,
        "no_webhook_activation": True,
        "owner_approval_status": "PENDING_OWNER_REVIEW",
        "kill_switch_state": "READY",
    }


def _normalize_input(input_data: Mapping[str, Any]) -> dict[str, Any]:
    candidate_payload = _mapping_or_empty(
        _first_value(input_data, "selected_candidate", "candidate")[0]
    )
    sources: tuple[Mapping[str, Any], ...] = (input_data, candidate_payload)

    candidate_id = _text(
        _first_from_sources(
            sources,
            "candidate_id",
            "selected_candidate_id",
            "id",
        )[0]
    )

    raw_status, status_provided = _first_from_sources(
        sources, "candidate_status", "status"
    )
    candidate_status = _canonical_status(raw_status)

    flags: dict[str, bool | None] = {}
    selected_value, selected_provided = _first_from_sources(
        sources, "selected_candidate_present", "selected_candidate_found", "selected"
    )
    flags["selected_candidate_present"] = (
        _flag_state(selected_value)
        if selected_provided
        else bool(candidate_id or candidate_payload)
    )

    review_value, review_provided = _first_from_sources(
        sources, "candidate_review_ready", "review_ready"
    )
    if review_provided:
        candidate_review_ready = _flag_state(review_value)
        review_ready_explicit = True
    elif candidate_status in REVIEW_READY_STATUSES:
        candidate_review_ready = True
        review_ready_explicit = True
    elif _status_rejects(candidate_status):
        candidate_review_ready = False
        review_ready_explicit = True
    else:
        candidate_review_ready = None
        review_ready_explicit = False
    flags["candidate_review_ready"] = candidate_review_ready

    for field in READINESS_FIELDS:
        if field in flags:
            continue
        value, provided = _first_from_sources(sources, field)
        flags[field] = _flag_state(value) if provided else None

    owner_approval_status = _canonical_status(
        _first_from_sources(sources, "owner_approval_status")[0]
    )
    kill_switch_state = _canonical_status(
        _first_from_sources(sources, "kill_switch_state")[0]
    )

    return {
        "candidate_id": candidate_id or None,
        "candidate_status": candidate_status,
        "status_provided": status_provided,
        "flags": flags,
        "candidate_review_ready_explicit": review_ready_explicit,
        "owner_approval_status": owner_approval_status,
        "kill_switch_state": kill_switch_state,
        "candidate_rejected": _any_truthy(
            sources,
            "candidate_rejected",
            "explicitly_rejected",
            "rejected_for_demo_validation",
        ),
    }


def _candidate_status(normalized: Mapping[str, Any]) -> str:
    status = normalized["candidate_status"]
    flags = normalized["flags"]
    if status:
        return status
    if not flags["selected_candidate_present"]:
        return "MISSING"
    if flags["candidate_review_ready"] is True:
        return "REVIEW_READY"
    if (
        flags["candidate_review_ready"] is False
        and normalized["candidate_review_ready_explicit"]
    ):
        return "NOT_REVIEW_READY"
    return "UNKNOWN"


def _candidate_rejection_reasons(normalized: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    flags = normalized["flags"]
    status = normalized["candidate_status"]

    if normalized["candidate_rejected"]:
        reasons.append("candidate is explicitly rejected")
    if _status_rejects(status):
        reasons.append(f"candidate status rejects demo validation: {status}")
    if (
        flags["selected_candidate_present"] is True
        and flags["candidate_review_ready"] is False
        and normalized["candidate_review_ready_explicit"]
    ):
        reasons.append("candidate is explicitly not review-ready")

    return reasons


def _readiness_gaps(normalized: Mapping[str, Any]) -> list[str]:
    flags = normalized["flags"]
    gaps = [
        f"{field} must be true"
        for field in READINESS_FIELDS
        if flags[field] is not True
    ]

    if normalized["owner_approval_status"] not in OWNER_APPROVAL_READY_STATUSES:
        gaps.append(
            "owner_approval_status must be "
            "APPROVED_FOR_SUPERVISED_DEMO_VALIDATION or APPROVED_REVIEW_ONLY"
        )
    if normalized["kill_switch_state"] not in KILL_SWITCH_READY_STATES:
        gaps.append("kill_switch_state must be ARMED or READY")

    return gaps


def _safety_boundary(
    flags: Mapping[str, bool | None], hard_safety_failures: list[str]
) -> dict[str, Any]:
    return {
        "hard_boundary_status": (
            "FAILED"
            if hard_safety_failures
            else (
                "CONFIRMED"
                if all(flags[field] is True for field in HARD_SAFETY_FIELDS)
                else "INCOMPLETE"
            )
        ),
        "false_safety_fields": list(hard_safety_failures),
        "missing_safety_fields": [
            field for field in HARD_SAFETY_FIELDS if flags[field] is None
        ],
        "checks": {
            field: _state_label(flags[field]) for field in HARD_SAFETY_FIELDS
        },
        "broker_access_allowed": False,
        "oanda_access_allowed": False,
        "credential_access_allowed": False,
        "account_id_access_allowed": False,
        "trade_allowed": False,
        "live_routing_allowed": False,
        "demo_routing_allowed": False,
        "paper_routing_allowed": False,
        "runtime_activation_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "production_activation_allowed": False,
        "money_movement_allowed": False,
    }


def _report_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex Supervised Demo Operational Validation Runner V1",
        "",
        "## Packet Identity",
        "",
        f"- Mission ID: {MISSION_ID}",
        "- Mission Name: AIOS Governed Self-Building Operating System",
        f"- Program ID: {PROGRAM_ID}",
        "- Program Name: AIOS Forex Supervised Operational Validation Program V1",
        f"- Epic ID: {EPIC_ID}",
        "- Epic Name: Demo Operations",
        f"- Bucket ID: {BUCKET_ID}",
        "- Bucket Name: Demo Runtime",
        f"- Packet ID: {PACKET_ID}",
        "- Packet Name: Supervised Demo Operational Validation Runner",
        "",
        "## Purpose",
        "",
        "This runner decides whether a selected review-ready Forex candidate is eligible to enter supervised demo validation.",
        "",
        "## Scope",
        "",
        "In scope: deterministic local validation of supplied candidate readiness, owner review state, operational evidence, and hard safety boundaries.",
        "",
        "Out of scope: broker access, OANDA access, credential access, .env access, account ID access, live routing, demo routing, paper routing, runtime activation, scheduler creation, daemon creation, webhook creation, production activation, compounding execution, and money movement.",
        "",
        "## Implementation Summary",
        "",
        "- Created a pure Python local validator with deterministic result keys.",
        "- Created a CLI runner that prints JSON and can write this report when explicitly requested.",
        "- Added focused tests for ready, blocked, rejected, incomplete-evidence, report-write, deterministic-key, and no external behavior paths.",
        f"- Latest default sample status: {result['operational_validation_status']}",
        "",
        "## Decision Statuses",
        "",
        f"- {READY_FOR_SUPERVISED_DEMO_VALIDATION}: all readiness, owner approval, kill switch, and safety checks are satisfied.",
        f"- {REQUIRE_MORE_EVIDENCE}: hard safety boundaries are intact, but readiness evidence is incomplete.",
        f"- {BLOCKED_BY_SAFETY_BOUNDARY}: one or more hard safety boundary checks is explicitly false.",
        f"- {REJECTED_FOR_DEMO_VALIDATION}: the candidate is explicitly not review-ready or explicitly rejected.",
        "",
        "## Safety Boundary",
        "",
        "This packet does not authorize broker access, OANDA access, credential access, .env access, account ID access, live routing, demo routing, paper routing, runtime activation, scheduler, daemon, webhook, production activation, compounding execution, or money movement.",
        "",
        "## Validation",
        "",
        "- Validator chain: py_compile, focused pytest, CLI JSON smoke run, CLI report-write smoke run, git diff --check, and git status.",
        "- The default run is intentionally REQUIRE_MORE_EVIDENCE unless explicit supplied input proves readiness.",
        "",
        "## Remaining Work",
        "",
        "This completes PKT-FOREX-001 only.",
        "Remaining declared implementation/evidence packets after this: 9.",
        "",
        "## Next Packet",
        "",
        "PKT-FOREX-002 Demo Trade Evidence Collector.",
    ]
    return "\n".join(lines) + "\n"


def _first_value(source: Mapping[str, Any], *names: str) -> tuple[Any, bool]:
    for name in names:
        if name in source:
            return source[name], True
    return None, False


def _first_from_sources(
    sources: tuple[Mapping[str, Any], ...], *names: str
) -> tuple[Any, bool]:
    for source in sources:
        value, found = _first_value(source, *names)
        if found:
            return value, True
    return None, False


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _any_truthy(sources: tuple[Mapping[str, Any], ...], *names: str) -> bool:
    value, found = _first_from_sources(sources, *names)
    return _flag_state(value) is True if found else False


def _flag_state(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, str):
        text = value.strip().lower()
        if not text:
            return None
        if text in TRUE_VALUES:
            return True
        if text in FALSE_VALUES:
            return False
        return None
    return bool(value)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value).strip()


def _canonical_status(value: Any) -> str:
    return _text(value).upper().replace("-", "_").replace(" ", "_")


def _status_rejects(status: str) -> bool:
    if not status:
        return False
    if status in EXPLICIT_REJECTION_STATUSES:
        return True
    return any(fragment in status for fragment in REJECTION_STATUS_FRAGMENTS)


def _state_label(value: bool | None) -> str:
    if value is True:
        return "TRUE"
    if value is False:
        return "FALSE"
    return "MISSING"
