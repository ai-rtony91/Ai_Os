"""Final build-only Vacation Mode readiness decision for AIOS Forex."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.forex_evidence_depth_quality_gate_v1 import (
    EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID,
    EVIDENCE_DEPTH_BLOCKED_UNSAFE,
    EVIDENCE_DEPTH_QUALITY_READY,
    EVIDENCE_DEPTH_REQUIRE_MORE_EVIDENCE,
    build_sample_partial_input as build_evidence_sample_partial_input,
    build_sample_ready_input as build_evidence_sample_ready_input,
    build_sample_unsafe_input as build_evidence_sample_unsafe_input,
    evaluate_forex_evidence_depth_quality_gate,
)
from automation.forex_engine.forex_sos_owner_alert_bridge_v1 import (
    SOS_OWNER_ALERT_BLOCKED_SCHEMA_INVALID,
    SOS_OWNER_ALERT_BLOCKED_UNSAFE,
    SOS_OWNER_ALERT_BRIDGE_READY,
    SOS_OWNER_ALERT_REQUIRE_MORE_EVIDENCE,
    build_sample_partial_input as build_sos_sample_partial_input,
    build_sample_ready_input as build_sos_sample_ready_input,
    build_sample_unsafe_input as build_sos_sample_unsafe_input,
    evaluate_forex_sos_owner_alert_bridge,
)
from automation.forex_engine.forex_statistical_profit_proof_gate_v1 import (
    STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID,
    STATISTICAL_PROFIT_BLOCKED_UNSAFE,
    STATISTICAL_PROFIT_PROOF_READY,
    STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE,
    build_sample_partial_input as build_statistical_sample_partial_input,
    build_sample_ready_input as build_statistical_sample_ready_input,
    build_sample_unsafe_input as build_statistical_sample_unsafe_input,
    evaluate_forex_statistical_profit_proof_gate,
)
from automation.forex_engine.forex_supervised_compounding_policy_gate_v1 import (
    SUPERVISED_COMPOUNDING_BLOCKED_SCHEMA_INVALID,
    SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE,
    SUPERVISED_COMPOUNDING_POLICY_READY,
    SUPERVISED_COMPOUNDING_REQUIRE_MORE_EVIDENCE,
    build_sample_partial_input as build_compounding_sample_partial_input,
    build_sample_ready_input as build_compounding_sample_ready_input,
    build_sample_unsafe_input as build_compounding_sample_unsafe_input,
    evaluate_forex_supervised_compounding_policy_gate,
)
from automation.forex_engine.forex_vacation_mode_readiness_orchestrator_v1 import (
    VACATION_MODE_BLOCKED_SCHEMA_INVALID as SOURCE_VACATION_SCHEMA_INVALID,
    VACATION_MODE_BLOCKED_UNSAFE as SOURCE_VACATION_BLOCKED_UNSAFE,
    VACATION_MODE_READY as SOURCE_VACATION_READY,
    VACATION_MODE_REQUIRE_MORE_EVIDENCE as SOURCE_VACATION_MORE_EVIDENCE,
    build_sample_partial_input as build_vacation_sample_partial_input,
    build_sample_ready_input as build_vacation_sample_ready_input,
    build_sample_unsafe_input as build_vacation_sample_unsafe_input,
    evaluate_forex_vacation_mode_readiness,
)


VERSION = "forex_vacation_mode_final_readiness_decision_v1"
PACKET_ID = "AIOS-FOREX-VACATION-MODE-FINAL-READINESS-DECISION-V1"
EXACT_NEXT_PHASE = "SUPERVISED_DEMO_OPERATIONAL_VALIDATION_PHASE"

VACATION_MODE_READY = "VACATION_MODE_READY"
VACATION_MODE_REQUIRE_MORE_EVIDENCE = "VACATION_MODE_REQUIRE_MORE_EVIDENCE"
VACATION_MODE_BLOCKED_UNSAFE = "VACATION_MODE_BLOCKED_UNSAFE"
VACATION_MODE_BLOCKED_SCHEMA_INVALID = "VACATION_MODE_BLOCKED_SCHEMA_INVALID"

FINAL_DECISION_SURFACES = (
    "vacation_readiness_orchestrator_ready",
    "evidence_depth_quality_ready",
    "statistical_profit_proof_ready",
    "supervised_compounding_policy_ready",
    "sos_owner_alert_bridge_ready",
    "all_source_packets_present",
    "all_source_packets_build_only",
    "all_source_classifications_ready",
    "all_source_percentages_100",
    "all_source_missing_surfaces_zero",
    "all_source_blocked_surfaces_zero",
    "all_source_unsafe_fragments_zero",
    "all_source_protected_flags_false",
    "broker_action_blocked",
    "oanda_api_call_blocked",
    "credential_access_blocked",
    "env_read_blocked",
    "account_id_access_blocked",
    "raw_transaction_id_access_blocked",
    "order_placement_blocked",
    "live_execution_blocked",
    "autonomous_execution_blocked",
    "compounding_execution_blocked",
    "bank_movement_blocked",
    "withdrawal_blocked",
    "deposit_blocked",
    "sos_alert_send_blocked",
    "notification_send_blocked",
    "scheduler_daemon_webhook_blocked",
    "owner_approval_required",
    "owner_approval_not_captured_by_packet",
    "vacation_mode_execution_blocked",
    "production_readiness_claim_blocked",
    "profitable_22_6_claim_blocked",
    "unattended_account_management_claim_blocked",
    "final_decision_build_only",
    "exact_next_phase_declared",
    "protected_flags_false",
    "unsafe_payload_absent",
    "schema_integrity_ready",
)

SOURCE_SPECS = (
    {
        "key": "vacation_readiness_orchestrator",
        "input_field": "source_vacation_readiness_result",
        "ready_classification": SOURCE_VACATION_READY,
        "more_evidence_classification": SOURCE_VACATION_MORE_EVIDENCE,
        "unsafe_classification": SOURCE_VACATION_BLOCKED_UNSAFE,
        "schema_invalid_classification": SOURCE_VACATION_SCHEMA_INVALID,
        "percent_field": "readiness_percent",
        "packet_id": "AIOS-FOREX-VACATION-MODE-READINESS-ORCHESTRATOR-V1",
    },
    {
        "key": "evidence_depth_quality",
        "input_field": "source_evidence_depth_quality_result",
        "ready_classification": EVIDENCE_DEPTH_QUALITY_READY,
        "more_evidence_classification": EVIDENCE_DEPTH_REQUIRE_MORE_EVIDENCE,
        "unsafe_classification": EVIDENCE_DEPTH_BLOCKED_UNSAFE,
        "schema_invalid_classification": EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID,
        "percent_field": "quality_percent",
        "packet_id": "AIOS-FOREX-EVIDENCE-DEPTH-QUALITY-GATE-V1",
    },
    {
        "key": "statistical_profit_proof",
        "input_field": "source_statistical_profit_result",
        "ready_classification": STATISTICAL_PROFIT_PROOF_READY,
        "more_evidence_classification": STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE,
        "unsafe_classification": STATISTICAL_PROFIT_BLOCKED_UNSAFE,
        "schema_invalid_classification": STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID,
        "percent_field": "statistical_percent",
        "packet_id": "AIOS-FOREX-STATISTICAL-PROFIT-PROOF-GATE-V1",
    },
    {
        "key": "supervised_compounding_policy",
        "input_field": "source_supervised_compounding_result",
        "ready_classification": SUPERVISED_COMPOUNDING_POLICY_READY,
        "more_evidence_classification": SUPERVISED_COMPOUNDING_REQUIRE_MORE_EVIDENCE,
        "unsafe_classification": SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE,
        "schema_invalid_classification": SUPERVISED_COMPOUNDING_BLOCKED_SCHEMA_INVALID,
        "percent_field": "compounding_policy_percent",
        "packet_id": "AIOS-FOREX-SUPERVISED-COMPOUNDING-POLICY-GATE-V1",
    },
    {
        "key": "sos_owner_alert_bridge",
        "input_field": "source_sos_owner_alert_result",
        "ready_classification": SOS_OWNER_ALERT_BRIDGE_READY,
        "more_evidence_classification": SOS_OWNER_ALERT_REQUIRE_MORE_EVIDENCE,
        "unsafe_classification": SOS_OWNER_ALERT_BLOCKED_UNSAFE,
        "schema_invalid_classification": SOS_OWNER_ALERT_BLOCKED_SCHEMA_INVALID,
        "percent_field": "sos_alert_percent",
        "packet_id": "AIOS-FOREX-SOS-OWNER-ALERT-BRIDGE-V1",
    },
)

SOURCE_KEYS = tuple(str(spec["key"]) for spec in SOURCE_SPECS)

PROTECTED_FLAG_NAMES = (
    "live_trading_allowed",
    "live_execution_allowed",
    "broker_action_allowed",
    "oanda_api_call_allowed",
    "credential_access_allowed",
    "env_read_allowed",
    "account_id_access_allowed",
    "account_id_persistence_allowed",
    "raw_transaction_id_access_allowed",
    "raw_order_id_access_allowed",
    "order_placement_allowed",
    "autonomous_execution_allowed",
    "compounding_allowed",
    "compounding_execution_authorized",
    "bank_movement_allowed",
    "withdrawal_allowed",
    "deposit_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "sos_alert_send_allowed",
    "notification_send_allowed",
    "sms_send_allowed",
    "push_send_allowed",
    "email_send_allowed",
    "telegram_send_allowed",
    "tasker_send_allowed",
    "adb_send_allowed",
    "unattended_vacation_mode_allowed",
    "vacation_profit_trial_allowed",
    "vacation_mode_execution_authorized",
    "next_trade_authorized",
    "repeat_trade_authorized",
    "selected_packet_execution_authorized",
    "codex_live_execution_authorized",
    "owner_live_execution_approval_present",
    "owner_final_vacation_approval_present",
    "final_decision_authorizes_trading",
    "final_decision_authorizes_execution",
    "final_decision_authorizes_compounding",
    "final_decision_authorizes_vacation_mode",
    "final_decision_sends_alert",
    "final_decision_moves_money",
)

BLOCKED_ACTIONS = (
    "broker_call",
    "oanda_api_call",
    "credential_access",
    "env_read",
    "account_id_access",
    "account_id_persistence",
    "raw_transaction_id_access",
    "raw_order_id_access",
    "order_placement",
    "live_execution",
    "autonomous_execution",
    "compounding_execution",
    "bank_movement",
    "withdrawal",
    "deposit",
    "scheduler",
    "daemon",
    "webhook",
    "uncontrolled_retry",
    "sos_alert_send",
    "notification_send",
    "sms_send",
    "push_send",
    "email_send",
    "telegram_send",
    "tasker_send",
    "adb_send",
    "selected_packet_execution",
    "commit",
    "push",
    "pr",
    "merge",
    "vacation_mode_execution",
)

BLOCKED_CLAIMS = (
    "guaranteed_profit",
    "future_profit",
    "final_statistical_profitability",
    "production_readiness",
    "vacation_mode_execution_readiness",
    "autonomous_trading_readiness",
    "compounding_execution_readiness",
    "live_execution_readiness",
    "profitable_22_6_operation_confirmed",
    "unattended_account_management_confirmed",
    "actual_owner_notification_confirmed",
    "owner_approval_captured",
    "owner_final_vacation_approval_captured",
    "live_capital_safe_unattended_confirmed",
)

UNSAFE_STRING_FRAGMENTS = (
    "Authorization",
    "Bearer",
    "access_token",
    "refresh_token",
    "api_key",
    "password",
    "secret",
    "credential",
    ".env",
    "accountID",
    "account_id",
    "AccountID",
    "OANDA-ACCOUNT",
    "v3/accounts/",
    "api-fxtrade.oanda.com",
    "api-fxpractice.oanda.com",
    "raw_transaction_id",
    "raw_order_id",
    "broker_order_id",
    "account_number",
    "live authorization",
    "live execution",
    "autonomous execution",
    "compounding execution",
    "bank movement",
    "bank transfer",
    "withdrawal",
    "deposit",
    "send sos",
    "sos alert send",
    "notification send",
    "sms send",
    "push send",
    "email send",
    "telegram send",
    "tasker send",
    "adb send",
    "scheduler",
    "daemon",
    "webhook",
    "uncontrolled retry",
)

UNSAFE_FALSE_SURFACES = (
    "broker_action_blocked",
    "oanda_api_call_blocked",
    "credential_access_blocked",
    "env_read_blocked",
    "account_id_access_blocked",
    "raw_transaction_id_access_blocked",
    "order_placement_blocked",
    "live_execution_blocked",
    "autonomous_execution_blocked",
    "compounding_execution_blocked",
    "bank_movement_blocked",
    "withdrawal_blocked",
    "deposit_blocked",
    "sos_alert_send_blocked",
    "notification_send_blocked",
    "scheduler_daemon_webhook_blocked",
    "owner_approval_required",
    "owner_approval_not_captured_by_packet",
    "vacation_mode_execution_blocked",
    "production_readiness_claim_blocked",
    "profitable_22_6_claim_blocked",
    "unattended_account_management_claim_blocked",
    "final_decision_build_only",
    "protected_flags_false",
    "unsafe_payload_absent",
)

READY_OWNER_ACTION = (
    "Review the final build-only Vacation Mode readiness decision and decide "
    "whether to request the separate supervised demo operational validation "
    "phase; do not approve broker access, OANDA access, live execution, "
    "compounding execution, autonomous execution, bank movement, notification "
    "sending, SOS alert sending, scheduler/daemon/webhook creation, or "
    "Vacation Mode execution from this packet."
)
PARTIAL_OWNER_ACTION = (
    "Close the missing final decision surfaces listed in missing_surfaces, "
    "then rerun this local final readiness decision before requesting the "
    "supervised demo operational validation phase."
)
UNSAFE_OWNER_ACTION = (
    "Stop and remove the unsafe signals listed in unsafe_fragments_detected "
    "before continuing final Vacation Mode readiness decision work."
)
SCHEMA_OWNER_ACTION = (
    "Fix all source gate result schemas and final_decision_surfaces, then "
    "rerun the local final Vacation Mode readiness decision."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Codex may only generate or run a future supervised demo operational "
    "validation packet that remains build-only or demo-only and keeps OANDA, "
    "broker calls, credentials, .env reads, account IDs, raw transaction/order "
    "IDs, live execution, autonomous execution, compounding execution, bank "
    "movement, withdrawal, deposit, notification sending, SOS alert sending, "
    "schedulers, daemons, webhooks, commits, pushes, PRs, merges, and "
    "Vacation Mode execution forbidden unless Anthony separately approves a "
    "new exact packet under RISK_POLICY.md."
)


@dataclass(frozen=True)
class VacationModeFinalReadinessDecisionInput:
    source_vacation_readiness_result: Any
    source_evidence_depth_quality_result: Any
    source_statistical_profit_result: Any
    source_supervised_compounding_result: Any
    source_sos_owner_alert_result: Any
    final_decision_surfaces: Mapping[str, bool] = field(default_factory=dict)
    owner_final_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class VacationModeFinalReadinessDecisionResult:
    version: str
    packet_id: str
    classification: str
    final_readiness_status: str
    ready_surface_count: int
    total_surface_count: int
    final_readiness_percent: float
    ready_surfaces: tuple[str, ...]
    missing_surfaces: tuple[str, ...]
    blocked_surfaces: tuple[str, ...]
    unsafe_fragments_detected: tuple[str, ...]
    source_summary: Mapping[str, Mapping[str, Any]]
    source_classifications: Mapping[str, str]
    source_percentages: Mapping[str, float]
    source_ready_surface_counts: Mapping[str, int]
    source_total_surface_counts: Mapping[str, int]
    protected_flags: Mapping[str, bool]
    blocked_actions: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    exact_next_owner_action: str
    exact_next_codex_packet_policy: str
    one_sentence_answer: str
    exact_next_phase: str
    next_safe_action: str
    broker_action_authorized: bool
    oanda_api_call_authorized: bool
    credential_access_authorized: bool
    env_read_authorized: bool
    account_id_access_authorized: bool
    account_id_persistence_authorized: bool
    raw_transaction_id_access_authorized: bool
    raw_order_id_access_authorized: bool
    order_placement_authorized: bool
    live_trading_authorized: bool
    live_execution_authorized: bool
    autonomous_execution_authorized: bool
    bank_movement_authorized: bool
    withdrawal_authorized: bool
    deposit_authorized: bool
    vacation_mode_execution_authorized: bool
    sos_alert_sent: bool
    notification_sent: bool
    sms_sent: bool
    push_sent: bool
    email_sent: bool
    telegram_sent: bool
    tasker_sent: bool
    adb_sent: bool
    production_readiness_claimed: bool
    profitable_22_6_claimed: bool
    unattended_account_management_claimed: bool
    owner_final_approval_captured: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
    broker_action_allowed: bool
    oanda_api_call_allowed: bool
    credential_access_allowed: bool
    env_read_allowed: bool
    account_id_access_allowed: bool
    account_id_persistence_allowed: bool
    raw_transaction_id_access_allowed: bool
    raw_order_id_access_allowed: bool
    order_placement_allowed: bool
    autonomous_execution_allowed: bool
    compounding_allowed: bool
    compounding_execution_authorized: bool
    bank_movement_allowed: bool
    withdrawal_allowed: bool
    deposit_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    sos_alert_send_allowed: bool
    notification_send_allowed: bool
    sms_send_allowed: bool
    push_send_allowed: bool
    email_send_allowed: bool
    telegram_send_allowed: bool
    tasker_send_allowed: bool
    adb_send_allowed: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool
    next_trade_authorized: bool
    repeat_trade_authorized: bool
    selected_packet_execution_authorized: bool
    codex_live_execution_authorized: bool
    owner_live_execution_approval_present: bool
    owner_final_vacation_approval_present: bool
    final_decision_authorizes_trading: bool
    final_decision_authorizes_execution: bool
    final_decision_authorizes_compounding: bool
    final_decision_authorizes_vacation_mode: bool
    final_decision_sends_alert: bool
    final_decision_moves_money: bool


@dataclass(frozen=True)
class _SchemaState:
    invalid: bool
    missing_or_invalid: tuple[str, ...]


def build_sample_ready_input() -> VacationModeFinalReadinessDecisionInput:
    return VacationModeFinalReadinessDecisionInput(
        source_vacation_readiness_result=evaluate_forex_vacation_mode_readiness(
            build_vacation_sample_ready_input()
        ),
        source_evidence_depth_quality_result=evaluate_forex_evidence_depth_quality_gate(
            build_evidence_sample_ready_input()
        ),
        source_statistical_profit_result=evaluate_forex_statistical_profit_proof_gate(
            build_statistical_sample_ready_input()
        ),
        source_supervised_compounding_result=(
            evaluate_forex_supervised_compounding_policy_gate(
                build_compounding_sample_ready_input()
            )
        ),
        source_sos_owner_alert_result=evaluate_forex_sos_owner_alert_bridge(
            build_sos_sample_ready_input()
        ),
        final_decision_surfaces=_ready_final_decision_surface_map(),
        owner_final_label="pending_owner_review",
        owner_notes_sanitized="sanitized final readiness decision preview",
    )


def build_sample_partial_input() -> VacationModeFinalReadinessDecisionInput:
    surfaces = _ready_final_decision_surface_map()
    for name in (
        "exact_next_phase_declared",
        "all_source_percentages_100",
        "all_source_missing_surfaces_zero",
    ):
        surfaces.pop(name)
    return VacationModeFinalReadinessDecisionInput(
        source_vacation_readiness_result=evaluate_forex_vacation_mode_readiness(
            build_vacation_sample_partial_input()
        ),
        source_evidence_depth_quality_result=evaluate_forex_evidence_depth_quality_gate(
            build_evidence_sample_partial_input()
        ),
        source_statistical_profit_result=evaluate_forex_statistical_profit_proof_gate(
            build_statistical_sample_partial_input()
        ),
        source_supervised_compounding_result=(
            evaluate_forex_supervised_compounding_policy_gate(
                build_compounding_sample_partial_input()
            )
        ),
        source_sos_owner_alert_result=evaluate_forex_sos_owner_alert_bridge(
            build_sos_sample_partial_input()
        ),
        final_decision_surfaces=surfaces,
        owner_final_label="pending_more_evidence",
        owner_notes_sanitized="safe incomplete final readiness decision preview",
    )


def build_sample_unsafe_input() -> VacationModeFinalReadinessDecisionInput:
    surfaces = _ready_final_decision_surface_map()
    surfaces.update(
        {
            "broker_action_blocked": False,
            "oanda_api_call_blocked": False,
            "credential_access_blocked": False,
            "env_read_blocked": False,
            "account_id_access_blocked": False,
            "raw_transaction_id_access_blocked": False,
            "order_placement_blocked": False,
            "live_execution_blocked": False,
            "autonomous_execution_blocked": False,
            "compounding_execution_blocked": False,
            "bank_movement_blocked": False,
            "withdrawal_blocked": False,
            "deposit_blocked": False,
            "sos_alert_send_blocked": False,
            "notification_send_blocked": False,
            "scheduler_daemon_webhook_blocked": False,
            "vacation_mode_execution_blocked": False,
        }
    )
    return VacationModeFinalReadinessDecisionInput(
        source_vacation_readiness_result=evaluate_forex_vacation_mode_readiness(
            build_vacation_sample_unsafe_input()
        ),
        source_evidence_depth_quality_result=evaluate_forex_evidence_depth_quality_gate(
            build_evidence_sample_unsafe_input()
        ),
        source_statistical_profit_result=evaluate_forex_statistical_profit_proof_gate(
            build_statistical_sample_unsafe_input()
        ),
        source_supervised_compounding_result=(
            evaluate_forex_supervised_compounding_policy_gate(
                build_compounding_sample_unsafe_input()
            )
        ),
        source_sos_owner_alert_result=evaluate_forex_sos_owner_alert_bridge(
            build_sos_sample_unsafe_input()
        ),
        final_decision_surfaces=surfaces,
        owner_final_label="pending_owner_review",
        owner_notes_sanitized=(
            "Authorization Bearer blocked sample with .env, account_id, "
            "raw_order_id, raw_transaction_id, OANDA live authorization, "
            "compounding execution, withdrawal, deposit, bank movement, "
            "notification send, sos alert send, scheduler, daemon, webhook, "
            "and uncontrolled retry markers"
        ),
    )


def build_sample_schema_invalid_input() -> Mapping[str, Any]:
    invalid_source = {
        "classification": 123,
        "ready_surface_count": "forty",
        "ready_surfaces": "not-a-list",
        "unsafe_fragments_detected": "schema-invalid",
    }
    return {
        "source_vacation_readiness_result": invalid_source,
        "source_evidence_depth_quality_result": invalid_source,
        "source_statistical_profit_result": invalid_source,
        "source_supervised_compounding_result": invalid_source,
        "source_sos_owner_alert_result": invalid_source,
        "final_decision_surfaces": {
            "broker_action_blocked": "yes",
            "unknown_final_decision_surface": True,
        },
        "owner_final_label": "schema-invalid",
        "owner_notes_sanitized": "schema invalid sample",
    }


def evaluate_forex_vacation_mode_final_readiness_decision(
    decision_input: VacationModeFinalReadinessDecisionInput | Mapping[str, Any] | None = None,
) -> VacationModeFinalReadinessDecisionResult:
    active_input = _coerce_input(decision_input or build_sample_ready_input())
    source_map = _source_map(active_input)
    schema = _validate_schema(active_input, source_map)
    source_summary = _source_summary(source_map)
    surfaces = _final_decision_surfaces(active_input, source_summary)
    surface_errors = _validate_final_surface_values(active_input.final_decision_surfaces)
    if surface_errors:
        schema = _SchemaState(
            invalid=True,
            missing_or_invalid=_unique_tuple(schema.missing_or_invalid + surface_errors),
        )

    unsafe_fragments = _unsafe_fragments(active_input, source_map, source_summary)
    ready_surfaces = tuple(
        name for name in FINAL_DECISION_SURFACES if surfaces.get(name) is True
    )
    not_ready_surfaces = tuple(
        name for name in FINAL_DECISION_SURFACES if surfaces.get(name) is not True
    )

    if schema.invalid:
        classification = VACATION_MODE_BLOCKED_SCHEMA_INVALID
        final_readiness_status = "blocked_schema_invalid"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces: tuple[str, ...] = ()
        unsafe_output = schema.missing_or_invalid
        next_owner_action = SCHEMA_OWNER_ACTION
    elif unsafe_fragments:
        classification = VACATION_MODE_BLOCKED_UNSAFE
        final_readiness_status = "blocked_unsafe_fail_closed"
        missing_surfaces = ()
        blocked_surfaces = not_ready_surfaces or ("unsafe_payload_absent",)
        unsafe_output = unsafe_fragments
        next_owner_action = UNSAFE_OWNER_ACTION
    elif len(ready_surfaces) == len(FINAL_DECISION_SURFACES):
        classification = VACATION_MODE_READY
        final_readiness_status = "all_final_decision_surfaces_ready_build_only"
        missing_surfaces = ()
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = READY_OWNER_ACTION
    else:
        classification = VACATION_MODE_REQUIRE_MORE_EVIDENCE
        final_readiness_status = "safe_more_final_readiness_evidence_required"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = PARTIAL_OWNER_ACTION

    protected_flags = protected_flags_false()
    return VacationModeFinalReadinessDecisionResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        final_readiness_status=final_readiness_status,
        ready_surface_count=len(ready_surfaces),
        total_surface_count=len(FINAL_DECISION_SURFACES),
        final_readiness_percent=_final_readiness_percent(len(ready_surfaces)),
        ready_surfaces=ready_surfaces,
        missing_surfaces=missing_surfaces,
        blocked_surfaces=blocked_surfaces,
        unsafe_fragments_detected=unsafe_output,
        source_summary=source_summary,
        source_classifications={
            key: str(summary["classification"])
            for key, summary in source_summary.items()
        },
        source_percentages={
            key: float(summary["percent"]) for key, summary in source_summary.items()
        },
        source_ready_surface_counts={
            key: int(summary["ready_surface_count"])
            for key, summary in source_summary.items()
        },
        source_total_surface_counts={
            key: int(summary["total_surface_count"])
            for key, summary in source_summary.items()
        },
        protected_flags=protected_flags,
        blocked_actions=BLOCKED_ACTIONS,
        blocked_claims=BLOCKED_CLAIMS,
        exact_next_owner_action=next_owner_action,
        exact_next_codex_packet_policy=EXACT_NEXT_CODEX_PACKET_POLICY,
        one_sentence_answer=_one_sentence_answer(classification),
        exact_next_phase=EXACT_NEXT_PHASE,
        next_safe_action=next_owner_action,
        broker_action_authorized=False,
        oanda_api_call_authorized=False,
        credential_access_authorized=False,
        env_read_authorized=False,
        account_id_access_authorized=False,
        account_id_persistence_authorized=False,
        raw_transaction_id_access_authorized=False,
        raw_order_id_access_authorized=False,
        order_placement_authorized=False,
        live_trading_authorized=False,
        live_execution_authorized=False,
        autonomous_execution_authorized=False,
        bank_movement_authorized=False,
        withdrawal_authorized=False,
        deposit_authorized=False,
        sos_alert_sent=False,
        notification_sent=False,
        sms_sent=False,
        push_sent=False,
        email_sent=False,
        telegram_sent=False,
        tasker_sent=False,
        adb_sent=False,
        production_readiness_claimed=False,
        profitable_22_6_claimed=False,
        unattended_account_management_claimed=False,
        owner_final_approval_captured=False,
        **protected_flags,
    )


def protected_flags_false() -> dict[str, bool]:
    return {name: False for name in PROTECTED_FLAG_NAMES}


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: VacationModeFinalReadinessDecisionResult) -> str:
    return "\n".join(
        (
            f"Vacation Mode final readiness classification: {result.classification}.",
            f"Final readiness surfaces: {result.ready_surface_count}/"
            f"{result.total_surface_count} "
            f"({result.final_readiness_percent:.2f}%).",
            result.one_sentence_answer,
            f"Exact next phase: {result.exact_next_phase}.",
            result.next_safe_action,
            "No trade placed by this packet.",
            "No broker or OANDA call was made by this packet.",
            "No notification or SOS alert was sent by this packet.",
            "No Vacation Mode execution was authorized by this packet.",
            "All protected flags remain false.",
        )
    )


def to_markdown(result: VacationModeFinalReadinessDecisionResult) -> str:
    rows = [
        "# AIOS Forex Vacation Mode Final Readiness Decision V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Version: `{result.version}`",
        f"- Classification: `{result.classification}`",
        f"- Final readiness status: `{result.final_readiness_status}`",
        f"- Ready surfaces: `{result.ready_surface_count}`",
        f"- Total surfaces: `{result.total_surface_count}`",
        f"- Final readiness percent: `{result.final_readiness_percent:.2f}`",
        f"- Exact next phase: `{result.exact_next_phase}`",
        "",
        "## Source Classifications",
    ]
    for key, classification in result.source_classifications.items():
        rows.append(f"- `{key}`: `{classification}`")
    rows.extend(("", "## Source Percentages"))
    for key, percent in result.source_percentages.items():
        rows.append(f"- `{key}`: `{percent:.2f}`")
    rows.extend(("", "## Ready Surfaces"))
    rows.extend(f"- `{name}`" for name in result.ready_surfaces)
    rows.extend(("", "## Missing Surfaces"))
    rows.extend(f"- `{name}`" for name in result.missing_surfaces)
    rows.extend(("", "## Blocked Surfaces"))
    rows.extend(f"- `{name}`" for name in result.blocked_surfaces)
    rows.extend(("", "## Unsafe Fragments Detected"))
    rows.extend(f"- `{name}`" for name in result.unsafe_fragments_detected)
    rows.extend(("", "## Protected Flags"))
    rows.extend(_markdown_bool_map(result.protected_flags))
    rows.extend(("", "## Blocked Actions"))
    rows.extend(f"- `{name}`" for name in result.blocked_actions)
    rows.extend(("", "## Blocked Claims"))
    rows.extend(f"- `{name}`" for name in result.blocked_claims)
    rows.extend(
        (
            "",
            "## Next Actions",
            f"- Owner: {result.exact_next_owner_action}",
            f"- Codex packet policy: {result.exact_next_codex_packet_policy}",
            f"- Next safe action: {result.next_safe_action}",
            "",
            f"One sentence answer: {result.one_sentence_answer}",
        )
    )
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def markdown_safety_lines() -> list[str]:
    return [
        "",
        "## Safety",
        "- Build-only final readiness decision.",
        "- No trade placed by this packet.",
        "- No OANDA call was made by this packet.",
        "- No broker call was made by this packet.",
        "- No credential access occurred.",
        "- No .env read occurred.",
        "- No account ID access or persistence occurred.",
        "- No raw transaction or order ID access occurred.",
        "- No live approval was granted.",
        "- No autonomous execution was approved.",
        "- No compounding execution approval was granted.",
        "- No bank movement, withdrawal, or deposit was authorized.",
        "- No notification or SOS alert was sent.",
        "- No scheduler, daemon, or webhook was created.",
        "- No Vacation Mode execution was authorized.",
        "- No production readiness, profitable 22/6, or unattended account management claim was made.",
        "- No owner final Vacation Mode approval was captured.",
        "- All protected flags remain false.",
    ]


def _ready_final_decision_surface_map() -> dict[str, bool]:
    return {name: True for name in FINAL_DECISION_SURFACES}


def _coerce_input(
    value: VacationModeFinalReadinessDecisionInput | Mapping[str, Any],
) -> VacationModeFinalReadinessDecisionInput:
    if isinstance(value, VacationModeFinalReadinessDecisionInput):
        return value
    if isinstance(value, Mapping):
        raw = dict(value)
    else:
        raw = {
            str(spec["input_field"]): getattr(value, str(spec["input_field"]), None)
            for spec in SOURCE_SPECS
        }
        raw.update(
            {
                "final_decision_surfaces": getattr(
                    value, "final_decision_surfaces", {}
                ),
                "owner_final_label": getattr(
                    value, "owner_final_label", "pending_owner_review"
                ),
                "owner_notes_sanitized": getattr(value, "owner_notes_sanitized", ""),
            }
        )
    surfaces = raw.get("final_decision_surfaces", {})
    return VacationModeFinalReadinessDecisionInput(
        source_vacation_readiness_result=raw.get("source_vacation_readiness_result"),
        source_evidence_depth_quality_result=raw.get(
            "source_evidence_depth_quality_result"
        ),
        source_statistical_profit_result=raw.get("source_statistical_profit_result"),
        source_supervised_compounding_result=raw.get(
            "source_supervised_compounding_result"
        ),
        source_sos_owner_alert_result=raw.get("source_sos_owner_alert_result"),
        final_decision_surfaces=(
            dict(surfaces) if isinstance(surfaces, Mapping) else surfaces
        ),
        owner_final_label=_safe_owner_final_label(
            raw.get("owner_final_label", "pending_owner_review")
        ),
        owner_notes_sanitized=_text(raw.get("owner_notes_sanitized", "")),
    )


def _source_map(active_input: VacationModeFinalReadinessDecisionInput) -> dict[str, Any]:
    return {
        str(spec["key"]): _field(active_input, str(spec["input_field"]))
        for spec in SOURCE_SPECS
    }


def _validate_schema(
    active_input: VacationModeFinalReadinessDecisionInput,
    source_map: Mapping[str, Any],
) -> _SchemaState:
    invalid: list[str] = []
    for spec in SOURCE_SPECS:
        key = str(spec["key"])
        source = source_map[key]
        input_field = str(spec["input_field"])
        required_fields = (
            "version",
            "packet_id",
            "classification",
            spec["percent_field"],
            "ready_surface_count",
            "total_surface_count",
            "ready_surfaces",
            "missing_surfaces",
            "blocked_surfaces",
            "unsafe_fragments_detected",
            "protected_flags",
        )
        for field_name in required_fields:
            if not _has_field(source, str(field_name)):
                invalid.append(f"{input_field}.{field_name}_missing")
        classification = _field(source, "classification")
        if not isinstance(classification, str):
            invalid.append(f"{input_field}.classification_not_string")
        elif classification not in (
            spec["ready_classification"],
            spec["more_evidence_classification"],
            spec["unsafe_classification"],
            spec["schema_invalid_classification"],
        ):
            invalid.append(f"{input_field}.classification_unknown")
        elif classification == spec["schema_invalid_classification"]:
            invalid.append(f"{input_field}.classification_schema_invalid")
        if _text(_field(source, "packet_id")) != spec["packet_id"]:
            invalid.append(f"{input_field}.packet_id_unexpected")
        if _number_or_none(_field(source, str(spec["percent_field"]))) is None:
            invalid.append(f"{input_field}.{spec['percent_field']}_not_numeric")
        for field_name in ("ready_surface_count", "total_surface_count"):
            if not _is_integer(_field(source, field_name)):
                invalid.append(f"{input_field}.{field_name}_not_integer")
        if (
            _is_integer(_field(source, "ready_surface_count"))
            and _is_integer(_field(source, "total_surface_count"))
            and _field(source, "ready_surface_count") > _field(source, "total_surface_count")
        ):
            invalid.append(f"{input_field}.ready_count_exceeds_total")
        for field_name in (
            "ready_surfaces",
            "missing_surfaces",
            "blocked_surfaces",
            "unsafe_fragments_detected",
        ):
            if not isinstance(_field(source, field_name), tuple | list):
                invalid.append(f"{input_field}.{field_name}_not_sequence")
        if not isinstance(_field(source, "protected_flags"), Mapping):
            invalid.append(f"{input_field}.protected_flags_not_mapping")
    if not isinstance(active_input.final_decision_surfaces, Mapping):
        invalid.append("final_decision_surfaces_not_mapping")
    return _SchemaState(invalid=bool(invalid), missing_or_invalid=_unique_tuple(invalid))


def _validate_final_surface_values(surfaces: Any) -> tuple[str, ...]:
    if not isinstance(surfaces, Mapping):
        return ("final_decision_surfaces_not_mapping",)
    errors: list[str] = []
    for name, value in surfaces.items():
        if name not in FINAL_DECISION_SURFACES:
            errors.append(f"final_decision_surfaces.{name}_unknown")
            continue
        if not isinstance(value, bool):
            errors.append(f"final_decision_surfaces.{name}_not_boolean")
    return tuple(errors)


def _source_summary(source_map: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for spec in SOURCE_SPECS:
        key = str(spec["key"])
        source = source_map[key]
        protected_flags = _field(source, "protected_flags", {})
        if not isinstance(protected_flags, Mapping):
            protected_flags = {}
        summary[key] = {
            "packet_id": _text(_field(source, "packet_id", "")),
            "classification": _text(_field(source, "classification", "")),
            "percent": _safe_float(_field(source, str(spec["percent_field"]), 0)),
            "ready_surface_count": _safe_int(_field(source, "ready_surface_count", 0)),
            "total_surface_count": _safe_int(_field(source, "total_surface_count", 0)),
            "missing_surface_count": len(_sequence(_field(source, "missing_surfaces", ()))),
            "blocked_surface_count": len(_sequence(_field(source, "blocked_surfaces", ()))),
            "unsafe_fragment_count": len(
                _sequence(_field(source, "unsafe_fragments_detected", ()))
            ),
            "protected_flags_false": bool(protected_flags)
            and all(value is False for value in protected_flags.values()),
            "ready_classification": str(spec["ready_classification"]),
            "unsafe_classification": str(spec["unsafe_classification"]),
            "schema_invalid_classification": str(spec["schema_invalid_classification"]),
            "expected_packet_id": str(spec["packet_id"]),
        }
    return summary


def _final_decision_surfaces(
    active_input: VacationModeFinalReadinessDecisionInput,
    source_summary: Mapping[str, Mapping[str, Any]],
) -> dict[str, bool]:
    configured = (
        active_input.final_decision_surfaces
        if isinstance(active_input.final_decision_surfaces, Mapping)
        else {}
    )
    source_ready = {
        key: summary["classification"] == summary["ready_classification"]
        and summary["percent"] == 100.0
        and summary["ready_surface_count"] == summary["total_surface_count"]
        for key, summary in source_summary.items()
    }
    all_present = all(bool(summary["classification"]) for summary in source_summary.values())
    all_build_only = all(
        summary["packet_id"] == summary["expected_packet_id"]
        for summary in source_summary.values()
    )
    all_ready = all(source_ready.values())
    all_percent_100 = all(summary["percent"] == 100.0 for summary in source_summary.values())
    all_missing_zero = all(
        summary["missing_surface_count"] == 0 for summary in source_summary.values()
    )
    all_blocked_zero = all(
        summary["blocked_surface_count"] == 0 for summary in source_summary.values()
    )
    all_unsafe_zero = all(
        summary["unsafe_fragment_count"] == 0 for summary in source_summary.values()
    )
    all_source_flags_false = all(
        bool(summary["protected_flags_false"]) for summary in source_summary.values()
    )

    return {
        "vacation_readiness_orchestrator_ready": source_ready[
            "vacation_readiness_orchestrator"
        ],
        "evidence_depth_quality_ready": source_ready["evidence_depth_quality"],
        "statistical_profit_proof_ready": source_ready["statistical_profit_proof"],
        "supervised_compounding_policy_ready": source_ready[
            "supervised_compounding_policy"
        ],
        "sos_owner_alert_bridge_ready": source_ready["sos_owner_alert_bridge"],
        "all_source_packets_present": all_present,
        "all_source_packets_build_only": all_build_only,
        "all_source_classifications_ready": all_ready,
        "all_source_percentages_100": all_percent_100
        and _surface_true(configured, "all_source_percentages_100"),
        "all_source_missing_surfaces_zero": all_missing_zero
        and _surface_true(configured, "all_source_missing_surfaces_zero"),
        "all_source_blocked_surfaces_zero": all_blocked_zero,
        "all_source_unsafe_fragments_zero": all_unsafe_zero,
        "all_source_protected_flags_false": all_source_flags_false,
        "broker_action_blocked": _surface_true(configured, "broker_action_blocked"),
        "oanda_api_call_blocked": _surface_true(configured, "oanda_api_call_blocked"),
        "credential_access_blocked": _surface_true(configured, "credential_access_blocked"),
        "env_read_blocked": _surface_true(configured, "env_read_blocked"),
        "account_id_access_blocked": _surface_true(
            configured, "account_id_access_blocked"
        ),
        "raw_transaction_id_access_blocked": _surface_true(
            configured, "raw_transaction_id_access_blocked"
        ),
        "order_placement_blocked": _surface_true(configured, "order_placement_blocked"),
        "live_execution_blocked": _surface_true(configured, "live_execution_blocked"),
        "autonomous_execution_blocked": _surface_true(
            configured, "autonomous_execution_blocked"
        ),
        "compounding_execution_blocked": _surface_true(
            configured, "compounding_execution_blocked"
        ),
        "bank_movement_blocked": _surface_true(configured, "bank_movement_blocked"),
        "withdrawal_blocked": _surface_true(configured, "withdrawal_blocked"),
        "deposit_blocked": _surface_true(configured, "deposit_blocked"),
        "sos_alert_send_blocked": _surface_true(configured, "sos_alert_send_blocked"),
        "notification_send_blocked": _surface_true(configured, "notification_send_blocked"),
        "scheduler_daemon_webhook_blocked": _surface_true(
            configured, "scheduler_daemon_webhook_blocked"
        ),
        "owner_approval_required": _surface_true(configured, "owner_approval_required"),
        "owner_approval_not_captured_by_packet": _surface_true(
            configured, "owner_approval_not_captured_by_packet"
        ),
        "vacation_mode_execution_blocked": _surface_true(
            configured, "vacation_mode_execution_blocked"
        ),
        "production_readiness_claim_blocked": _surface_true(
            configured, "production_readiness_claim_blocked"
        ),
        "profitable_22_6_claim_blocked": _surface_true(
            configured, "profitable_22_6_claim_blocked"
        ),
        "unattended_account_management_claim_blocked": _surface_true(
            configured, "unattended_account_management_claim_blocked"
        ),
        "final_decision_build_only": _surface_true(configured, "final_decision_build_only"),
        "exact_next_phase_declared": EXACT_NEXT_PHASE
        == "SUPERVISED_DEMO_OPERATIONAL_VALIDATION_PHASE"
        and _surface_true(configured, "exact_next_phase_declared"),
        "protected_flags_false": all_source_flags_false
        and _surface_true(configured, "protected_flags_false"),
        "unsafe_payload_absent": all_unsafe_zero
        and _surface_true(configured, "unsafe_payload_absent"),
        "schema_integrity_ready": all_present and all_build_only,
    }


def _surface_true(surfaces: Mapping[str, Any], name: str) -> bool:
    return surfaces.get(name) is True


def _unsafe_fragments(
    active_input: VacationModeFinalReadinessDecisionInput,
    source_map: Mapping[str, Any],
    source_summary: Mapping[str, Mapping[str, Any]],
) -> tuple[str, ...]:
    fragments: list[str] = []
    for spec in SOURCE_SPECS:
        key = str(spec["key"])
        input_field = str(spec["input_field"])
        source = source_map[key]
        fragments.extend(_source_unsafe_fragments(input_field, source))
        if source_summary[key]["classification"] == spec["unsafe_classification"]:
            fragments.append(f"{input_field}.classification:block_unsafe")
        source_flags = _field(source, "protected_flags", {})
        if isinstance(source_flags, Mapping):
            fragments.extend(
                f"{input_field}.protected_flags.{name}:true"
                for name, value in source_flags.items()
                if value is True
            )
    surfaces = active_input.final_decision_surfaces
    if isinstance(surfaces, Mapping):
        fragments.extend(
            f"final_decision_surfaces.{name}:false"
            for name, value in surfaces.items()
            if name in UNSAFE_FALSE_SURFACES and value is False
        )
    fragments.extend(_scan_string_value("owner_final_label", active_input.owner_final_label))
    fragments.extend(
        _scan_string_value("owner_notes_sanitized", active_input.owner_notes_sanitized)
    )
    return _unique_tuple(fragments)


def _source_unsafe_fragments(input_field: str, source: Any) -> tuple[str, ...]:
    raw = _field(source, "unsafe_fragments_detected", ())
    if isinstance(raw, str):
        return (f"{input_field}.unsafe_fragments_detected:{raw}",)
    if isinstance(raw, tuple | list):
        return tuple(
            f"{input_field}.unsafe_fragments_detected:{_text(item)}"
            for item in raw
            if _text(item)
        )
    return ()


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _has_field(value: Any, field_name: str) -> bool:
    if isinstance(value, Mapping):
        return field_name in value
    return hasattr(value, field_name)


def _sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return ()


def _is_integer(value: Any) -> bool:
    return type(value) is int


def _safe_int(value: Any) -> int:
    return value if _is_integer(value) else 0


def _number_or_none(value: Any) -> Decimal | None:
    if isinstance(value, bool):
        return None
    return _decimal_or_none(value)


def _safe_float(value: Any) -> float:
    number = _number_or_none(value)
    if number is None:
        return 0.0
    return float(round(number, 2))


def _safe_owner_final_label(value: Any) -> str:
    text = _text(value, "pending_owner_review")
    if not text:
        return "pending_owner_review"
    return text


def _scan_string_value(path: str, value: Any) -> tuple[str, ...]:
    if not isinstance(value, str):
        return ()
    lowered = value.lower()
    return tuple(
        f"{path}:{fragment}"
        for fragment in UNSAFE_STRING_FRAGMENTS
        if fragment.lower() in lowered
    )


def _final_readiness_percent(ready_count: int) -> float:
    return round((ready_count / len(FINAL_DECISION_SURFACES)) * 100, 2)


def _one_sentence_answer(classification: str) -> str:
    if classification == VACATION_MODE_READY:
        return (
            "AIOS has a build-only final Vacation Mode readiness decision "
            "ready for supervised demo operational validation, but this "
            "packet authorizes no trading, execution, money movement, alerts, "
            "notifications, or Vacation Mode execution."
        )
    if classification == VACATION_MODE_REQUIRE_MORE_EVIDENCE:
        return (
            "AIOS final Vacation Mode readiness is safe but incomplete "
            "because one or more final decision surfaces need more evidence."
        )
    if classification == VACATION_MODE_BLOCKED_UNSAFE:
        return (
            "AIOS final Vacation Mode readiness is blocked because unsafe "
            "broker, OANDA, credential, account, raw ID, live execution, "
            "compounding, money movement, notification, SOS, or automation "
            "signals were detected."
        )
    return (
        "AIOS final Vacation Mode readiness cannot be evaluated until the "
        "required source gate schemas are complete and valid."
    )


def _decimal_or_none(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _decimal_string(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _markdown_bool_map(values: Mapping[str, bool]) -> list[str]:
    return [f"- `{key}`: `{str(value).lower()}`" for key, value in values.items()]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _unique_tuple(values: Any) -> tuple[str, ...]:
    unique: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in unique:
            unique.append(text)
    return tuple(unique)


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, Decimal):
        return _decimal_string(value)
    return value
