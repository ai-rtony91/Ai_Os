"""Build-only Vacation Mode readiness orchestrator for AIOS Forex."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


VERSION = "forex_vacation_mode_readiness_orchestrator_v1"
PACKET_ID = "AIOS-FOREX-VACATION-MODE-READINESS-ORCHESTRATOR-V1"

VACATION_MODE_READY = "VACATION_MODE_READY"
VACATION_MODE_REQUIRE_MORE_EVIDENCE = "VACATION_MODE_REQUIRE_MORE_EVIDENCE"
VACATION_MODE_BLOCKED_UNSAFE = "VACATION_MODE_BLOCKED_UNSAFE"
VACATION_MODE_BLOCKED_SCHEMA_INVALID = "VACATION_MODE_BLOCKED_SCHEMA_INVALID"

READINESS_SURFACES = (
    "statistical_profit_proof_ready",
    "evidence_depth_ready",
    "quality_gate_ready",
    "risk_engine_ready",
    "position_sizing_ready",
    "daily_loss_cap_ready",
    "max_drawdown_cap_ready",
    "kill_switch_ready",
    "one_order_only_ready",
    "duplicate_order_prevention_ready",
    "broker_health_monitor_ready",
    "market_hours_filter_ready",
    "spread_filter_ready",
    "slippage_filter_ready",
    "high_impact_news_filter_ready",
    "trade_quality_threshold_ready",
    "confidence_scoring_ready",
    "entry_validation_ready",
    "exit_management_ready",
    "take_profit_stop_loss_ready",
    "stale_position_detection_ready",
    "restart_recovery_ready",
    "runtime_recovery_ready",
    "evidence_logging_ready",
    "audit_logging_ready",
    "telemetry_projection_ready",
    "sos_alert_ready",
    "owner_approval_gate_ready",
    "owner_intervention_workflow_ready",
    "safe_pause_ready",
    "safe_resume_ready",
    "compounding_policy_ready",
    "capital_preservation_ready",
    "vacation_arming_ready",
    "vacation_disarming_ready",
    "fail_closed_ready",
)

PROTECTED_FLAG_NAMES = (
    "live_trading_allowed",
    "live_execution_allowed",
    "broker_action_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "unattended_vacation_mode_allowed",
    "vacation_profit_trial_allowed",
    "next_trade_authorized",
    "repeat_trade_authorized",
    "selected_packet_execution_authorized",
    "codex_live_execution_authorized",
    "owner_live_execution_approval_present",
)

UNSAFE_SIGNAL_NAMES = (
    "unsafe_action_detected",
    "credential_signal_detected",
    "broker_payload_detected",
    "account_id_detected",
    "live_authorization_detected",
    "live_execution_detected",
    "autonomous_execution_detected",
    "compounding_authorization_detected",
    "bank_movement_detected",
    "scheduler_detected",
    "daemon_detected",
    "webhook_detected",
    "uncontrolled_retry_detected",
    "broker_action_detected",
    "oanda_call_detected",
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
    "fxtrade",
    "raw_transaction_id",
    "raw_order_id",
    "broker_order_id",
    "account_number",
    "live authorization",
    "live execution",
    "autonomous execution",
    "compound profits",
    "bank transfer",
    "webhook",
    "daemon",
    "scheduler",
    "uncontrolled retry",
)

BLOCKED_ACTIONS = (
    "broker_call",
    "oanda_api_call",
    "credential_access",
    "env_file_read",
    "account_id_access",
    "account_id_persistence",
    "order_placement",
    "live_trading",
    "live_execution",
    "next_trade_authorization",
    "repeat_trade_authorization",
    "selected_packet_execution",
    "autonomous_execution",
    "unattended_vacation_mode",
    "vacation_profit_trial",
    "compounding",
    "bank_movement",
    "scheduler",
    "daemon",
    "webhook",
    "uncontrolled_retry",
    "commit",
    "push",
    "pr_create",
    "merge",
)

BLOCKED_CLAIMS = (
    "profit_guarantee",
    "statistical_profitability_proven_for_live_trading",
    "live_trading_authorized",
    "broker_execution_authorized",
    "vacation_mode_armed",
    "unattended_operation_authorized",
    "autonomous_compounding_authorized",
    "bank_movement_authorized",
    "next_trade_authorized",
    "repeat_trade_authorized",
)

READY_OWNER_ACTION = (
    "Review the build-only Vacation Mode readiness result and decide whether to "
    "request a separate supervised DRY_RUN proof packet; do not approve live "
    "execution, OANDA access, credentials, compounding, bank movement, or "
    "unattended Vacation Mode."
)
PARTIAL_OWNER_ACTION = (
    "Close the missing readiness surfaces listed in missing_surfaces, then rerun "
    "this build-only readiness orchestrator before requesting any future "
    "supervised proof packet."
)
UNSAFE_OWNER_ACTION = (
    "Stop and remove the unsafe signals listed in unsafe_fragments_detected "
    "before any further Vacation Mode readiness work."
)
SCHEMA_OWNER_ACTION = (
    "Fix the required readiness_surfaces and protected_flags input fields, then "
    "rerun the local build-only sample."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Codex may only generate or run a future tokenized packet that keeps OANDA, "
    "broker calls, credentials, account IDs, live execution, autonomous "
    "execution, compounding, bank movement, schedulers, daemons, and webhooks "
    "forbidden unless Anthony separately approves a new exact packet under "
    "RISK_POLICY.md."
)


@dataclass(frozen=True)
class VacationModeReadinessInput:
    readiness_surfaces: Mapping[str, bool]
    protected_flags: Mapping[str, bool] = field(default_factory=dict)
    unsafe_signals: Mapping[str, bool] = field(default_factory=dict)
    operator_notes_sanitized: str = ""


@dataclass(frozen=True)
class VacationModeReadinessResult:
    version: str
    packet_id: str
    classification: str
    readiness_status: str
    ready_surface_count: int
    total_surface_count: int
    readiness_percent: float
    ready_surfaces: tuple[str, ...]
    missing_surfaces: tuple[str, ...]
    blocked_surfaces: tuple[str, ...]
    unsafe_fragments_detected: tuple[str, ...]
    protected_flags: Mapping[str, bool]
    blocked_actions: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    exact_next_owner_action: str
    exact_next_codex_packet_policy: str
    one_sentence_answer: str
    next_safe_action: str
    sos_alert_evaluated: bool
    sos_alert_sent: bool
    broker_action_authorized: bool
    live_trading_authorized: bool
    compounding_authorized: bool
    autonomous_execution_authorized: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
    broker_action_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool
    next_trade_authorized: bool
    repeat_trade_authorized: bool
    selected_packet_execution_authorized: bool
    codex_live_execution_authorized: bool
    owner_live_execution_approval_present: bool


@dataclass(frozen=True)
class _SchemaState:
    invalid: bool
    missing_or_invalid: tuple[str, ...]


def build_sample_ready_input() -> VacationModeReadinessInput:
    return VacationModeReadinessInput(
        readiness_surfaces={name: True for name in READINESS_SURFACES},
        protected_flags=protected_flags_false(),
        unsafe_signals={name: False for name in UNSAFE_SIGNAL_NAMES},
        operator_notes_sanitized="build-only readiness preview",
    )


def build_sample_partial_input() -> VacationModeReadinessInput:
    surfaces = {name: True for name in READINESS_SURFACES}
    for name in (
        "statistical_profit_proof_ready",
        "quality_gate_ready",
        "broker_health_monitor_ready",
        "high_impact_news_filter_ready",
        "restart_recovery_ready",
        "runtime_recovery_ready",
        "telemetry_projection_ready",
        "safe_resume_ready",
        "compounding_policy_ready",
        "vacation_arming_ready",
        "vacation_disarming_ready",
    ):
        surfaces[name] = False
    return VacationModeReadinessInput(
        readiness_surfaces=surfaces,
        protected_flags=protected_flags_false(),
        unsafe_signals={name: False for name in UNSAFE_SIGNAL_NAMES},
        operator_notes_sanitized="safe incomplete build-only readiness preview",
    )


def build_sample_unsafe_input() -> VacationModeReadinessInput:
    surfaces = {name: True for name in READINESS_SURFACES}
    for name in (
        "one_order_only_ready",
        "duplicate_order_prevention_ready",
        "kill_switch_ready",
        "compounding_policy_ready",
        "fail_closed_ready",
    ):
        surfaces[name] = False
    protected_flags = protected_flags_false()
    attempted_flags = dict(protected_flags)
    attempted_flags.update(
        {
            "broker_action_allowed": True,
            "live_trading_allowed": True,
            "autonomous_execution_allowed": True,
            "compounding_allowed": True,
        }
    )
    unsafe_signals = {name: False for name in UNSAFE_SIGNAL_NAMES}
    unsafe_signals.update(
        {
            "broker_payload_detected": True,
            "credential_signal_detected": True,
            "account_id_detected": True,
            "live_authorization_detected": True,
            "autonomous_execution_detected": True,
            "compounding_authorization_detected": True,
            "uncontrolled_retry_detected": True,
        }
    )
    return VacationModeReadinessInput(
        readiness_surfaces=surfaces,
        protected_flags=attempted_flags,
        unsafe_signals=unsafe_signals,
        operator_notes_sanitized=(
            "Authorization Bearer blocked sample with account_id and live "
            "authorization markers"
        ),
    )


def build_sample_schema_invalid_input() -> Mapping[str, Any]:
    return {
        "readiness_surfaces": {
            "statistical_profit_proof_ready": "yes",
            "evidence_depth_ready": True,
        },
        "unsafe_signals": {"credential_signal_detected": False},
        "operator_notes_sanitized": "schema invalid sample",
    }


def evaluate_forex_vacation_mode_readiness(
    readiness_input: VacationModeReadinessInput | Mapping[str, Any] | None = None,
) -> VacationModeReadinessResult:
    active_input = _coerce_input(readiness_input or build_sample_ready_input())
    schema = _validate_schema(active_input)
    protected_flag_attempts = _protected_flag_attempts(active_input.protected_flags)
    unsafe_fragments = _unsafe_fragments(active_input, protected_flag_attempts)

    surfaces = dict(active_input.readiness_surfaces)
    ready_surfaces = tuple(name for name in READINESS_SURFACES if surfaces.get(name) is True)
    not_ready_surfaces = tuple(
        name for name in READINESS_SURFACES if surfaces.get(name) is not True
    )
    unsafe_detected = bool(unsafe_fragments)

    if schema.invalid:
        classification = VACATION_MODE_BLOCKED_SCHEMA_INVALID
        readiness_status = "blocked_schema_invalid"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces: tuple[str, ...] = ()
        next_owner_action = SCHEMA_OWNER_ACTION
    elif unsafe_detected:
        classification = VACATION_MODE_BLOCKED_UNSAFE
        readiness_status = "blocked_unsafe_fail_closed"
        missing_surfaces = ()
        blocked_surfaces = not_ready_surfaces or ("fail_closed_ready",)
        next_owner_action = UNSAFE_OWNER_ACTION
    elif len(ready_surfaces) == len(READINESS_SURFACES):
        classification = VACATION_MODE_READY
        readiness_status = "all_readiness_surfaces_ready_build_only"
        missing_surfaces = ()
        blocked_surfaces = ()
        next_owner_action = READY_OWNER_ACTION
    else:
        classification = VACATION_MODE_REQUIRE_MORE_EVIDENCE
        readiness_status = "safe_more_evidence_required"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces = ()
        next_owner_action = PARTIAL_OWNER_ACTION

    if schema.invalid:
        unsafe_output = schema.missing_or_invalid
    else:
        unsafe_output = unsafe_fragments

    protected_flags = protected_flags_false()
    one_sentence = _one_sentence_answer(classification)
    return VacationModeReadinessResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        readiness_status=readiness_status,
        ready_surface_count=len(ready_surfaces),
        total_surface_count=len(READINESS_SURFACES),
        readiness_percent=_readiness_percent(len(ready_surfaces)),
        ready_surfaces=ready_surfaces,
        missing_surfaces=missing_surfaces,
        blocked_surfaces=blocked_surfaces,
        unsafe_fragments_detected=unsafe_output,
        protected_flags=protected_flags,
        blocked_actions=BLOCKED_ACTIONS,
        blocked_claims=BLOCKED_CLAIMS,
        exact_next_owner_action=next_owner_action,
        exact_next_codex_packet_policy=EXACT_NEXT_CODEX_PACKET_POLICY,
        one_sentence_answer=one_sentence,
        next_safe_action=next_owner_action,
        sos_alert_evaluated="sos_alert_ready" in READINESS_SURFACES,
        sos_alert_sent=False,
        broker_action_authorized=False,
        live_trading_authorized=False,
        compounding_authorized=False,
        autonomous_execution_authorized=False,
        **protected_flags,
    )


def protected_flags_false() -> dict[str, bool]:
    return {name: False for name in PROTECTED_FLAG_NAMES}


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: VacationModeReadinessResult) -> str:
    return "\n".join(
        (
            f"Vacation Mode readiness classification: {result.classification}.",
            f"Readiness: {result.ready_surface_count}/{result.total_surface_count} "
            f"surfaces ({result.readiness_percent:.2f}%).",
            result.one_sentence_answer,
            result.next_safe_action,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "All protected flags remain false.",
        )
    )


def to_markdown(result: VacationModeReadinessResult) -> str:
    rows = [
        "# AIOS Forex Vacation Mode Readiness Orchestrator V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Version: `{result.version}`",
        f"- Classification: `{result.classification}`",
        f"- Readiness status: `{result.readiness_status}`",
        f"- Ready surfaces: `{result.ready_surface_count}`",
        f"- Total surfaces: `{result.total_surface_count}`",
        f"- Readiness percent: `{result.readiness_percent:.2f}`",
        f"- SOS alert evaluated: `{str(result.sos_alert_evaluated).lower()}`",
        f"- SOS alert sent: `{str(result.sos_alert_sent).lower()}`",
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
        "- Build-only readiness evaluation.",
        "- No trade placed by this packet.",
        "- No OANDA call was made by this packet.",
        "- No broker call was made by this packet.",
        "- No credential access occurred.",
        "- No .env read occurred.",
        "- No account ID was persisted.",
        "- No live approval was granted.",
        "- No unattended Vacation Mode approval was granted.",
        "- No vacation profit trial was approved.",
        "- No next trade was authorized.",
        "- No repeat trade was authorized.",
        "- No selected packet execution was authorized.",
        "- No compounding approval was granted.",
        "- No bank movement approval was granted.",
        "- No scheduler, daemon, or webhook was created.",
        "- SOS readiness is evaluated only; no alert is sent.",
        "- All protected flags remain false.",
    ]


def _coerce_input(
    value: VacationModeReadinessInput | Mapping[str, Any],
) -> VacationModeReadinessInput:
    if isinstance(value, VacationModeReadinessInput):
        return value
    raw = dict(value)
    readiness_surfaces = raw.get("readiness_surfaces", {})
    protected_flags = raw.get("protected_flags", {})
    unsafe_signals = raw.get("unsafe_signals", {})
    return VacationModeReadinessInput(
        readiness_surfaces=(
            dict(readiness_surfaces) if isinstance(readiness_surfaces, Mapping) else {}
        ),
        protected_flags=dict(protected_flags) if isinstance(protected_flags, Mapping) else {},
        unsafe_signals=dict(unsafe_signals) if isinstance(unsafe_signals, Mapping) else {},
        operator_notes_sanitized=_text(raw.get("operator_notes_sanitized", "")),
    )


def _validate_schema(active_input: VacationModeReadinessInput) -> _SchemaState:
    invalid: list[str] = []
    if not isinstance(active_input.readiness_surfaces, Mapping):
        invalid.append("readiness_surfaces_missing_or_not_mapping")
    if not isinstance(active_input.protected_flags, Mapping):
        invalid.append("protected_flags_missing_or_not_mapping")
    for surface in READINESS_SURFACES:
        if surface not in active_input.readiness_surfaces:
            invalid.append(f"readiness_surfaces.{surface}_missing")
        elif not isinstance(active_input.readiness_surfaces.get(surface), bool):
            invalid.append(f"readiness_surfaces.{surface}_not_boolean")
    for flag_name in PROTECTED_FLAG_NAMES:
        if flag_name not in active_input.protected_flags:
            invalid.append(f"protected_flags.{flag_name}_missing")
        elif not isinstance(active_input.protected_flags.get(flag_name), bool):
            invalid.append(f"protected_flags.{flag_name}_not_boolean")
    for signal_name, value in active_input.unsafe_signals.items():
        if signal_name not in UNSAFE_SIGNAL_NAMES:
            invalid.append(f"unsafe_signals.{signal_name}_unknown")
        elif not isinstance(value, bool):
            invalid.append(f"unsafe_signals.{signal_name}_not_boolean")
    return _SchemaState(invalid=bool(invalid), missing_or_invalid=_unique_tuple(invalid))


def _protected_flag_attempts(flags: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        f"protected_flags.{name}:true"
        for name in PROTECTED_FLAG_NAMES
        if flags.get(name) is True
    )


def _unsafe_fragments(
    active_input: VacationModeReadinessInput,
    protected_flag_attempts: tuple[str, ...],
) -> tuple[str, ...]:
    fragments: list[str] = list(protected_flag_attempts)
    fragments.extend(
        f"unsafe_signals.{name}:true"
        for name in UNSAFE_SIGNAL_NAMES
        if active_input.unsafe_signals.get(name) is True
    )
    fragments.extend(
        _scan_string_value(
            "operator_notes_sanitized", active_input.operator_notes_sanitized
        )
    )
    return _unique_tuple(fragments)


def _scan_string_value(path: str, value: Any) -> tuple[str, ...]:
    if not isinstance(value, str):
        return ()
    hits = []
    lowered = value.lower()
    for fragment in UNSAFE_STRING_FRAGMENTS:
        if fragment.lower() in lowered:
            hits.append(f"{path}:{fragment}")
    return tuple(hits)


def _readiness_percent(ready_count: int) -> float:
    return round((ready_count / len(READINESS_SURFACES)) * 100, 2)


def _one_sentence_answer(classification: str) -> str:
    if classification == VACATION_MODE_READY:
        return (
            "AIOS is build-ready for future supervised Vacation Mode review, "
            "but this packet does not arm, execute, compound, call a broker, "
            "or approve unattended trading."
        )
    if classification == VACATION_MODE_REQUIRE_MORE_EVIDENCE:
        return (
            "AIOS is safe but not yet build-ready for Vacation Mode because "
            "one or more required readiness surfaces need more evidence."
        )
    if classification == VACATION_MODE_BLOCKED_UNSAFE:
        return (
            "AIOS Vacation Mode readiness is blocked because unsafe execution, "
            "credential, broker, live authorization, autonomy, compounding, or "
            "automation signals were detected."
        )
    return (
        "AIOS Vacation Mode readiness cannot be evaluated until the required "
        "readiness schema is complete and valid."
    )


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
    return value
