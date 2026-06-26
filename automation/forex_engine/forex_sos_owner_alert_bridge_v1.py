"""SOS owner alert bridge gate for build-only AIOS Forex review."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

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


VERSION = "forex_sos_owner_alert_bridge_v1"
PACKET_ID = "AIOS-FOREX-SOS-OWNER-ALERT-BRIDGE-V1"
NEXT_PACKET_PREVIEW = "AIOS-FOREX-VACATION-MODE-FINAL-READINESS-DECISION-V1"

SOS_OWNER_ALERT_BRIDGE_READY = "SOS_OWNER_ALERT_BRIDGE_READY"
SOS_OWNER_ALERT_REQUIRE_MORE_EVIDENCE = "SOS_OWNER_ALERT_REQUIRE_MORE_EVIDENCE"
SOS_OWNER_ALERT_BLOCKED_UNSAFE = "SOS_OWNER_ALERT_BLOCKED_UNSAFE"
SOS_OWNER_ALERT_BLOCKED_SCHEMA_INVALID = "SOS_OWNER_ALERT_BLOCKED_SCHEMA_INVALID"

SOS_ALERT_SURFACES = (
    "source_supervised_compounding_policy_ready",
    "source_statistical_profit_proof_ready",
    "source_evidence_quality_ready",
    "source_vacation_readiness_chain_present",
    "owner_alert_required_for_protected_actions",
    "owner_alert_policy_separated_from_sender",
    "owner_alert_preview_only",
    "no_alert_send_by_default",
    "alert_send_requires_explicit_owner_approval",
    "alert_send_requires_separate_packet",
    "alert_message_sanitization_required",
    "alert_no_credentials_allowed",
    "alert_no_account_ids_allowed",
    "alert_no_broker_payload_allowed",
    "alert_no_raw_transaction_ids_allowed",
    "alert_no_trade_execution_authority_allowed",
    "alert_no_money_movement_authority_allowed",
    "alert_severity_routing_ready",
    "alert_owner_decision_required_state_ready",
    "alert_safe_pause_state_ready",
    "alert_safe_resume_review_state_ready",
    "alert_kill_switch_escalation_ready",
    "alert_drawdown_escalation_ready",
    "alert_broker_health_escalation_ready",
    "alert_evidence_gap_escalation_ready",
    "alert_compounding_review_escalation_ready",
    "alert_vacation_mode_review_escalation_ready",
    "alert_audit_logging_required",
    "alert_evidence_logging_required",
    "alert_duplicate_suppression_required",
    "alert_rate_limit_required",
    "alert_ack_required_for_owner_decision",
    "actual_sos_send_blocked",
    "scheduler_daemon_webhook_blocked",
    "broker_action_blocked",
    "live_execution_blocked",
    "autonomous_execution_blocked",
    "compounding_execution_blocked",
    "bank_movement_blocked",
    "vacation_authorization_blocked",
    "protected_flags_false",
    "unsafe_payload_absent",
)

PROTECTED_FLAG_NAMES = (
    "live_trading_allowed",
    "live_execution_allowed",
    "broker_action_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
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
    "next_trade_authorized",
    "repeat_trade_authorized",
    "selected_packet_execution_authorized",
    "codex_live_execution_authorized",
    "owner_live_execution_approval_present",
    "sos_owner_alert_bridge_authorizes_trading",
    "sos_owner_alert_bridge_authorizes_execution",
    "sos_owner_alert_bridge_authorizes_compounding",
    "sos_owner_alert_bridge_authorizes_vacation_mode",
    "sos_owner_alert_bridge_sends_alert",
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
    "vacation_mode_readiness",
    "autonomous_trading_readiness",
    "compounding_execution_readiness",
    "live_execution_readiness",
    "profitable_22_6_operation_confirmed",
    "unattended_account_management_confirmed",
    "actual_owner_notification_confirmed",
    "owner_approval_captured",
    "vacation_mode_final_ready",
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
    "owner_alert_preview_only",
    "no_alert_send_by_default",
    "alert_send_requires_explicit_owner_approval",
    "alert_send_requires_separate_packet",
    "alert_no_credentials_allowed",
    "alert_no_account_ids_allowed",
    "alert_no_broker_payload_allowed",
    "alert_no_raw_transaction_ids_allowed",
    "alert_no_trade_execution_authority_allowed",
    "alert_no_money_movement_authority_allowed",
    "actual_sos_send_blocked",
    "scheduler_daemon_webhook_blocked",
    "broker_action_blocked",
    "live_execution_blocked",
    "autonomous_execution_blocked",
    "compounding_execution_blocked",
    "bank_movement_blocked",
    "vacation_authorization_blocked",
    "protected_flags_false",
    "unsafe_payload_absent",
)

READY_OWNER_ACTION = (
    "Review the SOS owner alert bridge result and decide whether to request "
    "the separate Vacation Mode final readiness decision packet; do not "
    "approve broker access, live execution, compounding execution, "
    "autonomous execution, bank movement, notification sending, SOS alert "
    "sending, scheduler/daemon/webhook creation, or Vacation Mode execution "
    "from this bridge."
)
PARTIAL_OWNER_ACTION = (
    "Close the missing SOS owner alert surfaces listed in missing_surfaces, "
    "then rerun this local SOS owner alert bridge before requesting any "
    "Vacation Mode final readiness decision packet."
)
UNSAFE_OWNER_ACTION = (
    "Stop and remove the unsafe signals listed in unsafe_fragments_detected "
    "before continuing SOS owner alert bridge work."
)
SCHEMA_OWNER_ACTION = (
    "Fix the source_supervised_compounding_result and sos_alert_surfaces "
    "input schema, then rerun the local SOS owner alert bridge."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Codex may only generate or run a future tokenized Vacation Mode final "
    "readiness decision packet that keeps OANDA, broker calls, credentials, "
    "account IDs, raw transaction/order IDs, live execution, autonomous "
    "execution, compounding execution, bank movement, withdrawal, deposit, "
    "notification sending, actual SOS alert sending, schedulers, daemons, "
    "and webhooks forbidden unless Anthony separately approves a new exact "
    "packet under RISK_POLICY.md."
)


@dataclass(frozen=True)
class SosOwnerAlertBridgeInput:
    source_supervised_compounding_result: Any
    sos_alert_surfaces: Mapping[str, bool] = field(default_factory=dict)
    owner_alert_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class SosOwnerAlertBridgeResult:
    version: str
    packet_id: str
    classification: str
    sos_alert_status: str
    ready_surface_count: int
    total_surface_count: int
    sos_alert_percent: float
    ready_surfaces: tuple[str, ...]
    missing_surfaces: tuple[str, ...]
    blocked_surfaces: tuple[str, ...]
    unsafe_fragments_detected: tuple[str, ...]
    source_supervised_compounding_classification: str
    source_compounding_policy_percent: float
    source_ready_surface_count: int
    source_total_surface_count: int
    protected_flags: Mapping[str, bool]
    blocked_actions: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    exact_next_owner_action: str
    exact_next_codex_packet_policy: str
    one_sentence_answer: str
    next_packet_preview: str
    next_safe_action: str
    broker_action_authorized: bool
    live_trading_authorized: bool
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
    live_trading_allowed: bool
    live_execution_allowed: bool
    broker_action_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
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
    sos_owner_alert_bridge_authorizes_trading: bool
    sos_owner_alert_bridge_authorizes_execution: bool
    sos_owner_alert_bridge_authorizes_compounding: bool
    sos_owner_alert_bridge_authorizes_vacation_mode: bool
    sos_owner_alert_bridge_sends_alert: bool


@dataclass(frozen=True)
class _SchemaState:
    invalid: bool
    missing_or_invalid: tuple[str, ...]


def build_sample_ready_input() -> SosOwnerAlertBridgeInput:
    source_result = evaluate_forex_supervised_compounding_policy_gate(
        build_compounding_sample_ready_input()
    )
    return SosOwnerAlertBridgeInput(
        source_supervised_compounding_result=source_result,
        sos_alert_surfaces=_ready_sos_surface_map(),
        owner_alert_label="pending_owner_review",
        owner_notes_sanitized="sanitized SOS owner alert bridge preview",
    )


def build_sample_partial_input() -> SosOwnerAlertBridgeInput:
    source_result = evaluate_forex_supervised_compounding_policy_gate(
        build_compounding_sample_partial_input()
    )
    alert_surfaces = _ready_sos_surface_map()
    for name in (
        "alert_broker_health_escalation_ready",
        "alert_evidence_gap_escalation_ready",
        "alert_compounding_review_escalation_ready",
        "alert_vacation_mode_review_escalation_ready",
        "alert_duplicate_suppression_required",
        "alert_rate_limit_required",
        "alert_ack_required_for_owner_decision",
    ):
        alert_surfaces.pop(name)
    return SosOwnerAlertBridgeInput(
        source_supervised_compounding_result=source_result,
        sos_alert_surfaces=alert_surfaces,
        owner_alert_label="pending_more_evidence",
        owner_notes_sanitized="safe incomplete SOS owner alert bridge preview",
    )


def build_sample_unsafe_input() -> SosOwnerAlertBridgeInput:
    source_result = evaluate_forex_supervised_compounding_policy_gate(
        build_compounding_sample_unsafe_input()
    )
    alert_surfaces = _ready_sos_surface_map()
    alert_surfaces.update(
        {
            "owner_alert_preview_only": False,
            "no_alert_send_by_default": False,
            "actual_sos_send_blocked": False,
            "scheduler_daemon_webhook_blocked": False,
            "broker_action_blocked": False,
            "live_execution_blocked": False,
            "autonomous_execution_blocked": False,
            "compounding_execution_blocked": False,
            "bank_movement_blocked": False,
            "vacation_authorization_blocked": False,
        }
    )
    return SosOwnerAlertBridgeInput(
        source_supervised_compounding_result=source_result,
        sos_alert_surfaces=alert_surfaces,
        owner_alert_label="pending_owner_review",
        owner_notes_sanitized=(
            "Authorization Bearer blocked sample with account_id, raw_order_id, "
            "raw_transaction_id, live authorization, compounding execution, "
            "withdrawal, deposit, bank movement, send sos, notification send, "
            "sms send, push send, email send, telegram send, tasker send, "
            "adb send, scheduler, daemon, webhook, and uncontrolled retry markers"
        ),
    )


def build_sample_schema_invalid_input() -> Mapping[str, Any]:
    return {
        "source_supervised_compounding_result": {
            "classification": 123,
            "compounding_policy_percent": "one hundred",
            "ready_surface_count": "thirty-six",
            "ready_surfaces": "not-a-list",
            "unsafe_fragments_detected": "schema-invalid",
        },
        "sos_alert_surfaces": {
            "owner_alert_preview_only": "yes",
            "unknown_sos_alert_surface": True,
        },
        "owner_alert_label": "schema-invalid",
        "owner_notes_sanitized": "schema invalid sample",
    }


def evaluate_forex_sos_owner_alert_bridge(
    bridge_input: SosOwnerAlertBridgeInput | Mapping[str, Any] | None = None,
) -> SosOwnerAlertBridgeResult:
    active_input = _coerce_input(bridge_input or build_sample_ready_input())
    schema = _validate_schema(active_input)
    source = active_input.source_supervised_compounding_result
    source_values = _source_values(source)
    surfaces = _sos_surfaces(active_input, source, source_values)
    surface_errors = _validate_sos_surface_values(active_input.sos_alert_surfaces)
    if surface_errors:
        schema = _SchemaState(
            invalid=True,
            missing_or_invalid=_unique_tuple(schema.missing_or_invalid + surface_errors),
        )

    unsafe_fragments = _unsafe_fragments(active_input, source)
    ready_surfaces = tuple(name for name in SOS_ALERT_SURFACES if surfaces.get(name) is True)
    not_ready_surfaces = tuple(
        name for name in SOS_ALERT_SURFACES if surfaces.get(name) is not True
    )

    if schema.invalid:
        classification = SOS_OWNER_ALERT_BLOCKED_SCHEMA_INVALID
        sos_alert_status = "blocked_schema_invalid"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces: tuple[str, ...] = ()
        unsafe_output = schema.missing_or_invalid
        next_owner_action = SCHEMA_OWNER_ACTION
    elif unsafe_fragments:
        classification = SOS_OWNER_ALERT_BLOCKED_UNSAFE
        sos_alert_status = "blocked_unsafe_fail_closed"
        missing_surfaces = ()
        blocked_surfaces = not_ready_surfaces or ("unsafe_payload_absent",)
        unsafe_output = unsafe_fragments
        next_owner_action = UNSAFE_OWNER_ACTION
    elif len(ready_surfaces) == len(SOS_ALERT_SURFACES):
        classification = SOS_OWNER_ALERT_BRIDGE_READY
        sos_alert_status = "all_sos_owner_alert_surfaces_ready_build_only"
        missing_surfaces = ()
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = READY_OWNER_ACTION
    else:
        classification = SOS_OWNER_ALERT_REQUIRE_MORE_EVIDENCE
        sos_alert_status = "safe_more_sos_owner_alert_evidence_required"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = PARTIAL_OWNER_ACTION

    protected_flags = protected_flags_false()
    return SosOwnerAlertBridgeResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        sos_alert_status=sos_alert_status,
        ready_surface_count=len(ready_surfaces),
        total_surface_count=len(SOS_ALERT_SURFACES),
        sos_alert_percent=_sos_alert_percent(len(ready_surfaces)),
        ready_surfaces=ready_surfaces,
        missing_surfaces=missing_surfaces,
        blocked_surfaces=blocked_surfaces,
        unsafe_fragments_detected=unsafe_output,
        source_supervised_compounding_classification=source_values["classification"],
        source_compounding_policy_percent=source_values["compounding_policy_percent"],
        source_ready_surface_count=source_values["ready_surface_count"],
        source_total_surface_count=source_values["total_surface_count"],
        protected_flags=protected_flags,
        blocked_actions=BLOCKED_ACTIONS,
        blocked_claims=BLOCKED_CLAIMS,
        exact_next_owner_action=next_owner_action,
        exact_next_codex_packet_policy=EXACT_NEXT_CODEX_PACKET_POLICY,
        one_sentence_answer=_one_sentence_answer(classification),
        next_packet_preview=NEXT_PACKET_PREVIEW,
        next_safe_action=next_owner_action,
        broker_action_authorized=False,
        live_trading_authorized=False,
        autonomous_execution_authorized=False,
        bank_movement_authorized=False,
        withdrawal_authorized=False,
        deposit_authorized=False,
        vacation_mode_execution_authorized=False,
        sos_alert_sent=False,
        notification_sent=False,
        sms_sent=False,
        push_sent=False,
        email_sent=False,
        telegram_sent=False,
        tasker_sent=False,
        adb_sent=False,
        **protected_flags,
    )


def protected_flags_false() -> dict[str, bool]:
    return {name: False for name in PROTECTED_FLAG_NAMES}


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: SosOwnerAlertBridgeResult) -> str:
    return "\n".join(
        (
            f"SOS owner alert bridge classification: {result.classification}.",
            f"SOS alert surfaces: {result.ready_surface_count}/"
            f"{result.total_surface_count} ({result.sos_alert_percent:.2f}%).",
            result.one_sentence_answer,
            result.next_safe_action,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "No notification or SOS alert was sent by this packet.",
            "No scheduler, daemon, or webhook was created by this packet.",
            "All protected flags remain false.",
        )
    )


def to_markdown(result: SosOwnerAlertBridgeResult) -> str:
    rows = [
        "# AIOS Forex SOS Owner Alert Bridge V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Version: `{result.version}`",
        f"- Classification: `{result.classification}`",
        f"- SOS alert status: `{result.sos_alert_status}`",
        f"- Ready surfaces: `{result.ready_surface_count}`",
        f"- Total surfaces: `{result.total_surface_count}`",
        f"- SOS alert percent: `{result.sos_alert_percent:.2f}`",
        (
            "- Source supervised compounding classification: "
            f"`{result.source_supervised_compounding_classification}`"
        ),
        (
            "- Source compounding policy percent: "
            f"`{result.source_compounding_policy_percent:.2f}`"
        ),
        f"- Source ready surface count: `{result.source_ready_surface_count}`",
        f"- Source total surface count: `{result.source_total_surface_count}`",
        f"- Next packet preview: `{result.next_packet_preview}`",
        "",
        "## Ready Surfaces",
    ]
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
        "- Build-only SOS owner alert bridge evaluation.",
        "- Preview-only alert policy; no actual sender integration.",
        "- No trade placed by this packet.",
        "- No OANDA call was made by this packet.",
        "- No broker call was made by this packet.",
        "- No credential access occurred.",
        "- No .env read occurred.",
        "- No account ID was persisted.",
        "- No raw transaction or order ID access occurred.",
        "- No live approval was granted.",
        "- No autonomous execution was approved.",
        "- No compounding execution approval was granted.",
        "- No bank movement was authorized.",
        "- No withdrawal was authorized.",
        "- No deposit was authorized.",
        "- No Vacation Mode execution was authorized.",
        "- No SOS alert was sent.",
        "- No notification, SMS, push, email, Telegram, Tasker, or ADB send occurred.",
        "- No scheduler, daemon, or webhook was created.",
        "- All protected flags remain false.",
    ]


def _ready_sos_surface_map() -> dict[str, bool]:
    return {name: True for name in SOS_ALERT_SURFACES}


def _coerce_input(
    value: SosOwnerAlertBridgeInput | Mapping[str, Any],
) -> SosOwnerAlertBridgeInput:
    if isinstance(value, SosOwnerAlertBridgeInput):
        return value
    if isinstance(value, Mapping):
        raw = dict(value)
    else:
        raw = {
            "source_supervised_compounding_result": getattr(
                value, "source_supervised_compounding_result", None
            ),
            "sos_alert_surfaces": getattr(value, "sos_alert_surfaces", {}),
            "owner_alert_label": getattr(
                value, "owner_alert_label", "pending_owner_review"
            ),
            "owner_notes_sanitized": getattr(value, "owner_notes_sanitized", ""),
        }
    alert_surfaces = raw.get("sos_alert_surfaces", {})
    return SosOwnerAlertBridgeInput(
        source_supervised_compounding_result=raw.get(
            "source_supervised_compounding_result"
        ),
        sos_alert_surfaces=(
            dict(alert_surfaces) if isinstance(alert_surfaces, Mapping) else alert_surfaces
        ),
        owner_alert_label=_safe_owner_alert_label(
            raw.get("owner_alert_label", "pending_owner_review")
        ),
        owner_notes_sanitized=_text(raw.get("owner_notes_sanitized", "")),
    )


def _validate_schema(active_input: SosOwnerAlertBridgeInput) -> _SchemaState:
    invalid: list[str] = []
    source = active_input.source_supervised_compounding_result
    for field_name in (
        "classification",
        "compounding_policy_percent",
        "ready_surface_count",
        "total_surface_count",
        "ready_surfaces",
        "missing_surfaces",
        "blocked_surfaces",
        "unsafe_fragments_detected",
        "protected_flags",
    ):
        if not _has_field(source, field_name):
            invalid.append(f"source_supervised_compounding_result.{field_name}_missing")

    classification = _field(source, "classification")
    if not isinstance(classification, str):
        invalid.append("source_supervised_compounding_result.classification_not_string")
    elif classification not in (
        SUPERVISED_COMPOUNDING_POLICY_READY,
        SUPERVISED_COMPOUNDING_REQUIRE_MORE_EVIDENCE,
        SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE,
        SUPERVISED_COMPOUNDING_BLOCKED_SCHEMA_INVALID,
    ):
        invalid.append("source_supervised_compounding_result.classification_unknown")
    elif classification == SUPERVISED_COMPOUNDING_BLOCKED_SCHEMA_INVALID:
        invalid.append(
            "source_supervised_compounding_result.classification_schema_invalid"
        )

    if _number_or_none(_field(source, "compounding_policy_percent")) is None:
        invalid.append(
            "source_supervised_compounding_result."
            "compounding_policy_percent_not_numeric"
        )
    for field_name in ("ready_surface_count", "total_surface_count"):
        if not _is_integer(_field(source, field_name)):
            invalid.append(
                f"source_supervised_compounding_result.{field_name}_not_integer"
            )
    if (
        _is_integer(_field(source, "ready_surface_count"))
        and _is_integer(_field(source, "total_surface_count"))
        and _field(source, "ready_surface_count") > _field(source, "total_surface_count")
    ):
        invalid.append("source_supervised_compounding_result.ready_count_exceeds_total")

    for field_name in (
        "ready_surfaces",
        "missing_surfaces",
        "blocked_surfaces",
        "unsafe_fragments_detected",
    ):
        if not isinstance(_field(source, field_name), tuple | list):
            invalid.append(
                f"source_supervised_compounding_result.{field_name}_not_sequence"
            )
    if not isinstance(_field(source, "protected_flags"), Mapping):
        invalid.append("source_supervised_compounding_result.protected_flags_not_mapping")
    if not isinstance(active_input.sos_alert_surfaces, Mapping):
        invalid.append("sos_alert_surfaces_not_mapping")
    return _SchemaState(invalid=bool(invalid), missing_or_invalid=_unique_tuple(invalid))


def _validate_sos_surface_values(alert_surfaces: Any) -> tuple[str, ...]:
    if not isinstance(alert_surfaces, Mapping):
        return ("sos_alert_surfaces_not_mapping",)
    errors: list[str] = []
    for name, value in alert_surfaces.items():
        if name not in SOS_ALERT_SURFACES:
            errors.append(f"sos_alert_surfaces.{name}_unknown")
            continue
        if not isinstance(value, bool):
            errors.append(f"sos_alert_surfaces.{name}_not_boolean")
    return tuple(errors)


def _sos_surfaces(
    active_input: SosOwnerAlertBridgeInput,
    source: Any,
    source_values: Mapping[str, Any],
) -> dict[str, bool]:
    alert_surfaces = (
        active_input.sos_alert_surfaces
        if isinstance(active_input.sos_alert_surfaces, Mapping)
        else {}
    )
    source_ready = set(_unique_tuple(_field(source, "ready_surfaces", ())))
    source_flags = _field(source, "protected_flags", {})
    if not isinstance(source_flags, Mapping):
        source_flags = {}
    source_classification = source_values["classification"]
    source_safe = source_classification not in (
        SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE,
        SUPERVISED_COMPOUNDING_BLOCKED_SCHEMA_INVALID,
    )
    source_is_ready = (
        source_classification == SUPERVISED_COMPOUNDING_POLICY_READY
        and source_values["ready_surface_count"] == source_values["total_surface_count"]
        and source_values["compounding_policy_percent"] == 100.0
    )
    source_protected_false = bool(source_flags) and all(
        value is False for value in source_flags.values()
    )
    source_unsafe_absent = (
        source_safe
        and "unsafe_payload_absent" in source_ready
        and not _field(source, "unsafe_fragments_detected", ())
    )

    return {
        "source_supervised_compounding_policy_ready": source_is_ready,
        "source_statistical_profit_proof_ready": (
            source_is_ready and "source_statistical_profit_proof_ready" in source_ready
        ),
        "source_evidence_quality_ready": (
            source_is_ready and "source_evidence_quality_ready" in source_ready
        ),
        "source_vacation_readiness_chain_present": (
            source_is_ready and "vacation_authorization_blocked" in source_ready
        ),
        "owner_alert_required_for_protected_actions": _alert_true(
            alert_surfaces, "owner_alert_required_for_protected_actions"
        ),
        "owner_alert_policy_separated_from_sender": _alert_true(
            alert_surfaces, "owner_alert_policy_separated_from_sender"
        ),
        "owner_alert_preview_only": _alert_true(
            alert_surfaces, "owner_alert_preview_only"
        ),
        "no_alert_send_by_default": _alert_true(
            alert_surfaces, "no_alert_send_by_default"
        ),
        "alert_send_requires_explicit_owner_approval": _alert_true(
            alert_surfaces, "alert_send_requires_explicit_owner_approval"
        ),
        "alert_send_requires_separate_packet": _alert_true(
            alert_surfaces, "alert_send_requires_separate_packet"
        ),
        "alert_message_sanitization_required": _alert_true(
            alert_surfaces, "alert_message_sanitization_required"
        ),
        "alert_no_credentials_allowed": _alert_true(
            alert_surfaces, "alert_no_credentials_allowed"
        ),
        "alert_no_account_ids_allowed": _alert_true(
            alert_surfaces, "alert_no_account_ids_allowed"
        ),
        "alert_no_broker_payload_allowed": _alert_true(
            alert_surfaces, "alert_no_broker_payload_allowed"
        ),
        "alert_no_raw_transaction_ids_allowed": _alert_true(
            alert_surfaces, "alert_no_raw_transaction_ids_allowed"
        ),
        "alert_no_trade_execution_authority_allowed": _alert_true(
            alert_surfaces, "alert_no_trade_execution_authority_allowed"
        ),
        "alert_no_money_movement_authority_allowed": _alert_true(
            alert_surfaces, "alert_no_money_movement_authority_allowed"
        ),
        "alert_severity_routing_ready": _alert_true(
            alert_surfaces, "alert_severity_routing_ready"
        ),
        "alert_owner_decision_required_state_ready": _alert_true(
            alert_surfaces, "alert_owner_decision_required_state_ready"
        ),
        "alert_safe_pause_state_ready": _alert_true(
            alert_surfaces, "alert_safe_pause_state_ready"
        ),
        "alert_safe_resume_review_state_ready": _alert_true(
            alert_surfaces, "alert_safe_resume_review_state_ready"
        ),
        "alert_kill_switch_escalation_ready": _alert_true(
            alert_surfaces, "alert_kill_switch_escalation_ready"
        ),
        "alert_drawdown_escalation_ready": _alert_true(
            alert_surfaces, "alert_drawdown_escalation_ready"
        ),
        "alert_broker_health_escalation_ready": _alert_true(
            alert_surfaces, "alert_broker_health_escalation_ready"
        ),
        "alert_evidence_gap_escalation_ready": _alert_true(
            alert_surfaces, "alert_evidence_gap_escalation_ready"
        ),
        "alert_compounding_review_escalation_ready": _alert_true(
            alert_surfaces, "alert_compounding_review_escalation_ready"
        ),
        "alert_vacation_mode_review_escalation_ready": _alert_true(
            alert_surfaces, "alert_vacation_mode_review_escalation_ready"
        ),
        "alert_audit_logging_required": _alert_true(
            alert_surfaces, "alert_audit_logging_required"
        ),
        "alert_evidence_logging_required": _alert_true(
            alert_surfaces, "alert_evidence_logging_required"
        ),
        "alert_duplicate_suppression_required": _alert_true(
            alert_surfaces, "alert_duplicate_suppression_required"
        ),
        "alert_rate_limit_required": _alert_true(
            alert_surfaces, "alert_rate_limit_required"
        ),
        "alert_ack_required_for_owner_decision": _alert_true(
            alert_surfaces, "alert_ack_required_for_owner_decision"
        ),
        "actual_sos_send_blocked": _alert_true(
            alert_surfaces, "actual_sos_send_blocked"
        ),
        "scheduler_daemon_webhook_blocked": _alert_true(
            alert_surfaces, "scheduler_daemon_webhook_blocked"
        )
        and source_flags.get("scheduler_allowed") is False
        and source_flags.get("daemon_allowed") is False
        and source_flags.get("webhook_allowed") is False,
        "broker_action_blocked": _alert_true(alert_surfaces, "broker_action_blocked")
        and source_flags.get("broker_action_allowed") is False,
        "live_execution_blocked": _alert_true(alert_surfaces, "live_execution_blocked")
        and source_flags.get("live_execution_allowed") is False,
        "autonomous_execution_blocked": _alert_true(
            alert_surfaces, "autonomous_execution_blocked"
        )
        and source_flags.get("autonomous_execution_allowed") is False,
        "compounding_execution_blocked": _alert_true(
            alert_surfaces, "compounding_execution_blocked"
        )
        and source_flags.get("compounding_execution_authorized") is False,
        "bank_movement_blocked": _alert_true(alert_surfaces, "bank_movement_blocked")
        and source_flags.get("bank_movement_allowed") is False
        and source_flags.get("withdrawal_allowed") is False
        and source_flags.get("deposit_allowed") is False,
        "vacation_authorization_blocked": _alert_true(
            alert_surfaces, "vacation_authorization_blocked"
        )
        and source_flags.get("unattended_vacation_mode_allowed") is False
        and source_flags.get("vacation_profit_trial_allowed") is False,
        "protected_flags_false": _alert_true(alert_surfaces, "protected_flags_false")
        and source_protected_false,
        "unsafe_payload_absent": _alert_true(alert_surfaces, "unsafe_payload_absent")
        and source_unsafe_absent,
    }


def _alert_true(alert_surfaces: Mapping[str, Any], name: str) -> bool:
    return alert_surfaces.get(name) is True


def _source_values(source: Any) -> dict[str, Any]:
    return {
        "classification": _text(_field(source, "classification", "")),
        "compounding_policy_percent": _safe_float(
            _field(source, "compounding_policy_percent", 0)
        ),
        "ready_surface_count": _safe_int(_field(source, "ready_surface_count", 0)),
        "total_surface_count": _safe_int(_field(source, "total_surface_count", 0)),
    }


def _unsafe_fragments(
    active_input: SosOwnerAlertBridgeInput, source: Any
) -> tuple[str, ...]:
    fragments: list[str] = []
    fragments.extend(_source_unsafe_fragments(source))
    source_classification = _field(source, "classification", "")
    if source_classification == SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE:
        fragments.append("source_supervised_compounding_result.classification:block_unsafe")
    source_flags = _field(source, "protected_flags", {})
    if isinstance(source_flags, Mapping):
        fragments.extend(
            f"source_supervised_compounding_result.protected_flags.{name}:true"
            for name, value in source_flags.items()
            if value is True
        )
    alert_surfaces = active_input.sos_alert_surfaces
    if isinstance(alert_surfaces, Mapping):
        fragments.extend(
            f"sos_alert_surfaces.{name}:false"
            for name, value in alert_surfaces.items()
            if name in UNSAFE_FALSE_SURFACES and value is False
        )
    fragments.extend(_scan_string_value("owner_alert_label", active_input.owner_alert_label))
    fragments.extend(
        _scan_string_value("owner_notes_sanitized", active_input.owner_notes_sanitized)
    )
    return _unique_tuple(fragments)


def _source_unsafe_fragments(source: Any) -> tuple[str, ...]:
    raw = _field(source, "unsafe_fragments_detected", ())
    if isinstance(raw, str):
        return (f"source_supervised_compounding_result.unsafe_fragments_detected:{raw}",)
    if isinstance(raw, tuple | list):
        return tuple(
            (
                "source_supervised_compounding_result."
                f"unsafe_fragments_detected:{_text(item)}"
            )
            for item in raw
            if _text(item)
        )
    return ()


def _has_field(value: Any, field_name: str) -> bool:
    if isinstance(value, Mapping):
        return field_name in value
    return hasattr(value, field_name)


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


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


def _safe_owner_alert_label(value: Any) -> str:
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


def _sos_alert_percent(ready_count: int) -> float:
    return round((ready_count / len(SOS_ALERT_SURFACES)) * 100, 2)


def _one_sentence_answer(classification: str) -> str:
    if classification == SOS_OWNER_ALERT_BRIDGE_READY:
        return (
            "AIOS has a build-only SOS owner alert bridge path ready for a "
            "future Vacation Mode final readiness decision review, but this "
            "bridge sends no alerts and authorizes no trading, execution, "
            "money movement, notification sending, or Vacation Mode execution."
        )
    if classification == SOS_OWNER_ALERT_REQUIRE_MORE_EVIDENCE:
        return (
            "AIOS SOS owner alert bridge is safe but incomplete because one "
            "or more alert surfaces need more evidence."
        )
    if classification == SOS_OWNER_ALERT_BLOCKED_UNSAFE:
        return (
            "AIOS SOS owner alert bridge is blocked because unsafe "
            "credential, broker, account, raw ID, live execution, "
            "compounding execution, money movement, notification, SOS, or "
            "automation signals were detected."
        )
    return (
        "AIOS SOS owner alert bridge cannot be evaluated until the required "
        "input schema is complete and valid."
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
