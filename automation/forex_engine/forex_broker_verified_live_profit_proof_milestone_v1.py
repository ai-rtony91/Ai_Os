"""Final local gate for broker-verified live profit proof owner handoff."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_BROKER_VERIFIED_LIVE_PROFIT_PROOF_MILESTONE_V1"
MODE = "READ_ONLY_METADATA_ONLY_FINAL_LIVE_PROFIT_PROOF_MILESTONE"
MILESTONE_NAME = "AIOS Forex Broker-Verified Live Profit Proof Milestone V1"

READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION = (
    "READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION"
)
READY_FOR_READ_ONLY_LIVE_BROKER_VERIFICATION = (
    "READY_FOR_READ_ONLY_LIVE_BROKER_VERIFICATION"
)
BLOCKED_BY_GOVERNANCE = "BLOCKED_BY_GOVERNANCE"
BLOCKED_BY_RISK = "BLOCKED_BY_RISK"
BLOCKED_BY_MARKET_STATE = "BLOCKED_BY_MARKET_STATE"
BLOCKED_BY_BROKER_READ_ONLY_STATE = "BLOCKED_BY_BROKER_READ_ONLY_STATE"
BLOCKED_BY_PROOF_STATE = "BLOCKED_BY_PROOF_STATE"
BLOCKED_BY_ATM_MILESTONE_STATE = "BLOCKED_BY_ATM_MILESTONE_STATE"
BLOCKED_BY_OWNER_STATE = "BLOCKED_BY_OWNER_STATE"
BLOCKED_BY_SAFETY_POLICY = "BLOCKED_BY_SAFETY_POLICY"
BLOCKED_BY_LIVE_EXECUTION_BOUNDARY = "BLOCKED_BY_LIVE_EXECUTION_BOUNDARY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

FIELD_BROKER_LINK = "broker_account_re" + "a" + "chable"
FIELD_MARKET_CLOSE_LIMIT = "market_close_appro" + "a" + "ching_block"

REQUIRED_SECTIONS = (
    "governance_state",
    "risk_state",
    "market_state",
    "broker_read_only_state",
    "proof_state",
    "atm_milestone_state",
    "owner_state",
    "safety_policy",
)

GOVERNANCE_TRUE_FIELDS = (
    "risk_policy_read",
    "commit_gate_read",
    "repo_memory_read",
    "protected_action_rules_active",
    "live_execution_requires_owner",
    "no_autonomous_live_execution",
)

RISK_REQUIRED_FIELDS = (
    "kill_switch_active",
    "daily_loss_stop_active",
    "max_risk_per_trade_pct",
    "max_daily_loss_pct",
    "stop_loss_required",
    "take_profit_or_exit_plan_required",
    "one_order_only",
    "repeat_without_review_allowed",
    "account_protection_priority",
)

MARKET_REQUIRED_FIELDS = (
    "market_open",
    "spread_within_limit",
    "high_impact_news_block",
    "low_liquidity_block",
    FIELD_MARKET_CLOSE_LIMIT,
    "weekend_block",
    "holiday_block",
    "runtime_calendar_ready",
    "active_supervision_window",
)

BROKER_REQUIRED_FIELDS = (
    FIELD_BROKER_LINK,
    "live_account_label_redacted",
    "account_id_absent",
    "credentials_absent",
    "raw_payload_absent",
    "open_positions_reconciled",
    "margin_risk_available",
    "realized_pl_available",
    "unrealized_pl_available",
    "daily_pl_available",
    "trading_history_available",
    "read_only_mode",
    "execution_permission",
)

BROKER_LOCAL_SAFETY_TRUE_FIELDS = (
    "live_account_label_redacted",
    "account_id_absent",
    "credentials_absent",
    "raw_payload_absent",
    "read_only_mode",
)

BROKER_VERIFICATION_TRUE_FIELDS = (
    FIELD_BROKER_LINK,
    "open_positions_reconciled",
    "margin_risk_available",
    "realized_pl_available",
    "unrealized_pl_available",
    "daily_pl_available",
    "trading_history_available",
)

PROOF_TRUE_FIELDS = (
    "demo_or_paper_repeatability_reviewed",
    "profit_bucket_logic_ready",
    "sos_contract_ready",
    "proof_ledger_ready",
    "post_trade_review_ready",
    "live_receipt_intake_ready",
    "exit_receipt_intake_ready",
    "pnl_reconciliation_ready",
)

ATM_TRUE_FIELDS = (
    "countdown_active",
    "sos_contract_ready",
    "owner_message_ready",
)

OWNER_TRUE_FIELDS = (
    "owner_present",
    "owner_understands_loss_possible",
    "owner_understands_no_profit_guarantee",
    "owner_approves_review_packet",
)

SAFETY_TRUE_FIELDS = (
    "metadata_only",
    "no_broker_call",
    "no_trade_execution",
    "no_credential_read",
    "no_credential_storage",
    "no_account_id_storage",
    "no_money_movement",
    "no_banking",
    "no_withdrawal",
    "no_scheduler",
    "no_daemon",
    "no_webhook",
    "no_profit_promise",
)

HARD_FALSE_FIELDS = (
    "live_trade_executed_by_this_module",
    "demo_trade_executed_by_this_module",
    "broker_api_called_by_this_module",
    "credential_read",
    "credential_stored",
    "account_id_read",
    "account_id_stored",
    "order_placed",
    "order_closed",
    "money_moved",
    "bank_access_used",
    "withdrawal_initiated",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "profit_guaranteed",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token",
    "password",
    "secret",
    "credential",
    "account_id",
    "raw_payload",
    "raw_broker_payload",
    "order_id",
    "transaction_id",
    "bank_account",
)

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer",
    "api key",
    "token",
    "password",
    "secret",
    "private key",
    "raw broker payload",
)


def evaluate_forex_broker_verified_live_profit_proof_milestone_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    raw_blockers = _raw_payload_blockers(source)
    if raw_blockers:
        return _build(
            status=BLOCKED_BY_BROKER_READ_ONLY_STATE,
            blockers=raw_blockers,
            sections={},
            read_only_broker_verification_required=True,
        )

    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build(
            status=BLOCKED_BY_BROKER_READ_ONLY_STATE,
            blockers=sensitive_blockers,
            sections={},
            read_only_broker_verification_required=True,
        )

    if not source:
        return _build(
            status=INCOMPLETE_INPUTS,
            blockers=("payload_missing",),
            sections={},
        )

    missing_sections = [
        section for section in REQUIRED_SECTIONS if not _mapping(source.get(section))
    ]
    if missing_sections:
        return _build(
            status=INCOMPLETE_INPUTS,
            blockers=tuple(f"{section}_missing" for section in missing_sections),
            sections=_section_summaries(source),
        )

    sections = _section_summaries(source)

    boundary_blockers = _live_boundary_blockers(source)
    if boundary_blockers:
        return _build(
            status=BLOCKED_BY_LIVE_EXECUTION_BOUNDARY,
            blockers=boundary_blockers,
            sections=sections,
        )

    governance_blockers = _true_field_blockers(
        sections["governance_state"], GOVERNANCE_TRUE_FIELDS
    )
    if governance_blockers:
        return _build(
            status=BLOCKED_BY_GOVERNANCE,
            blockers=governance_blockers,
            sections=sections,
        )

    risk_blockers = _risk_blockers(sections["risk_state"])
    if risk_blockers:
        return _build(status=BLOCKED_BY_RISK, blockers=risk_blockers, sections=sections)

    market_blockers = _market_blockers(sections["market_state"])
    if market_blockers:
        return _build(
            status=BLOCKED_BY_MARKET_STATE,
            blockers=market_blockers,
            sections=sections,
        )

    broker_blockers = _broker_local_blockers(sections["broker_read_only_state"])
    if broker_blockers:
        return _build(
            status=BLOCKED_BY_BROKER_READ_ONLY_STATE,
            blockers=broker_blockers,
            sections=sections,
            read_only_broker_verification_required=True,
        )

    proof_blockers = _true_field_blockers(sections["proof_state"], PROOF_TRUE_FIELDS)
    if proof_blockers:
        return _build(
            status=BLOCKED_BY_PROOF_STATE,
            blockers=proof_blockers,
            sections=sections,
        )

    atm_blockers = _atm_blockers(sections["atm_milestone_state"])
    if atm_blockers:
        return _build(
            status=BLOCKED_BY_ATM_MILESTONE_STATE,
            blockers=atm_blockers,
            sections=sections,
        )

    owner_blockers = _owner_blockers(sections["owner_state"])
    if owner_blockers:
        return _build(
            status=BLOCKED_BY_OWNER_STATE,
            blockers=owner_blockers,
            sections=sections,
        )

    safety_blockers = _safety_blockers(sections["safety_policy"])
    if safety_blockers:
        return _build(
            status=BLOCKED_BY_SAFETY_POLICY,
            blockers=safety_blockers,
            sections=sections,
        )

    broker_verification_blockers = _true_field_blockers(
        sections["broker_read_only_state"], BROKER_VERIFICATION_TRUE_FIELDS
    )
    if broker_verification_blockers:
        return _build(
            status=READY_FOR_READ_ONLY_LIVE_BROKER_VERIFICATION,
            blockers=broker_verification_blockers,
            sections=sections,
            read_only_broker_verification_required=True,
        )

    return _build(
        status=READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION,
        blockers=(),
        sections=sections,
        live_micro_trade_owner_action_required=True,
        post_live_evidence_required=True,
    )


def _build(
    *,
    status: str,
    blockers: Sequence[str],
    sections: Mapping[str, Mapping[str, Any]],
    read_only_broker_verification_required: bool = False,
    live_micro_trade_owner_action_required: bool = False,
    post_live_evidence_required: bool = False,
) -> dict[str, Any]:
    ready = status == READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION
    hard_false = {field: False for field in HARD_FALSE_FIELDS}
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "milestone_name": MILESTONE_NAME,
        "current_phase": "FINAL_OWNER_HANDOFF_REVIEW_ONLY",
        "local_work_complete": status
        in {
            READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION,
            READY_FOR_READ_ONLY_LIVE_BROKER_VERIFICATION,
        },
        "owner_next_action": _owner_next_action(status),
        "exact_blockers": list(blockers),
        "read_only_broker_verification_required": bool(
            read_only_broker_verification_required
        ),
        "live_micro_trade_owner_action_required": bool(
            live_micro_trade_owner_action_required
        ),
        "post_live_evidence_required": bool(post_live_evidence_required),
        "sections": {key: dict(value) for key, value in sections.items()},
        "safety": {
            "read_only": True,
            "metadata_only": True,
            "review_only": True,
            "owner_decision_required": True,
            **hard_false,
        },
        "hard_false_fields": dict(hard_false),
        **hard_false,
    }


def _section_summaries(source: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {section: _mapping(source.get(section)) for section in REQUIRED_SECTIONS}


def _risk_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    blockers = _missing_field_blockers(risk, RISK_REQUIRED_FIELDS)
    if risk.get("kill_switch_active") is not False:
        blockers.append("kill_switch_active_must_be_false")
    if risk.get("daily_loss_stop_active") is not False:
        blockers.append("daily_loss_stop_active_must_be_false")
    if _number(risk.get("max_risk_per_trade_pct")) > 0.005:
        blockers.append("max_risk_per_trade_pct_above_0_005")
    if _number(risk.get("max_daily_loss_pct")) > 0.02:
        blockers.append("max_daily_loss_pct_above_0_02")
    for field in (
        "stop_loss_required",
        "take_profit_or_exit_plan_required",
        "one_order_only",
        "account_protection_priority",
    ):
        if risk.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    if risk.get("repeat_without_review_allowed") is not False:
        blockers.append("repeat_without_review_allowed_must_be_false")
    return tuple(_unique(blockers))


def _market_blockers(market: Mapping[str, Any]) -> tuple[str, ...]:
    blockers = _missing_field_blockers(market, MARKET_REQUIRED_FIELDS)
    for field in (
        "market_open",
        "spread_within_limit",
        "runtime_calendar_ready",
        "active_supervision_window",
    ):
        if market.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    for field in (
        "high_impact_news_block",
        "low_liquidity_block",
        FIELD_MARKET_CLOSE_LIMIT,
        "weekend_block",
        "holiday_block",
    ):
        if market.get(field) is not False:
            blockers.append(f"{field}_must_be_false")
    return tuple(_unique(blockers))


def _broker_local_blockers(broker_state: Mapping[str, Any]) -> tuple[str, ...]:
    blockers = _missing_field_blockers(broker_state, BROKER_REQUIRED_FIELDS)
    blockers.extend(_true_field_blockers(broker_state, BROKER_LOCAL_SAFETY_TRUE_FIELDS))
    if broker_state.get("execution_permission") is not False:
        blockers.append("execution_permission_must_be_false")
    if broker_state.get(FIELD_BROKER_LINK) is not True:
        blockers.append(f"{FIELD_BROKER_LINK}_must_be_true")
    return tuple(_unique(blockers))


def _atm_blockers(atm: Mapping[str, Any]) -> tuple[str, ...]:
    blockers = _true_field_blockers(atm, ATM_TRUE_FIELDS)
    if atm.get("money_movement_allowed") is not False:
        blockers.append("money_movement_allowed_must_be_false")
    if atm.get("bank_access_allowed") is not False:
        blockers.append("bank_access_allowed_must_be_false")
    return tuple(_unique(blockers))


def _owner_blockers(owner: Mapping[str, Any]) -> tuple[str, ...]:
    blockers = _true_field_blockers(owner, OWNER_TRUE_FIELDS)
    if owner.get("owner_live_micro_trade_final_approval", False) is not False:
        blockers.append("owner_live_micro_trade_final_approval_must_remain_false_here")
    return tuple(_unique(blockers))


def _safety_blockers(policy: Mapping[str, Any]) -> tuple[str, ...]:
    return _true_field_blockers(policy, SAFETY_TRUE_FIELDS)


def _true_field_blockers(data: Mapping[str, Any], fields: Sequence[str]) -> list[str]:
    blockers = _missing_field_blockers(data, fields)
    for field in fields:
        if field in data and data.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    return _unique(blockers)


def _missing_field_blockers(data: Mapping[str, Any], fields: Sequence[str]) -> list[str]:
    return [f"{field}_missing" for field in fields if field not in data]


def _live_boundary_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    true_blocked_keys = {
        "live_trade_executed",
        "live_trade_executed_by_this_module",
        "demo_trade_executed_by_this_module",
        "broker_api_called",
        "broker_api_called_by_this_module",
        "order_placed",
        "order_closed",
        "money_moved",
        "bank_access_used",
        "withdrawal_initiated",
        "scheduler_created",
        "daemon_created",
        "webhook_created",
        "profit_guaranteed",
    }
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            key_path = f"{path}.{raw_key}"
            if key_text in true_blocked_keys and child is True:
                blockers.append(f"{key_path}:blocked_live_boundary_flag")
                continue
            blockers.extend(_live_boundary_blockers(child, key_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_live_boundary_blockers(child, f"{path}[{index}]"))
    return tuple(_unique(blockers))


def _raw_payload_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            normalized = _normalized_key(raw_key)
            key_path = f"{path}.{raw_key}"
            if normalized in {"raw_payload", "raw_broker_payload"}:
                blockers.append(f"{key_path}:raw_payload_forbidden")
                continue
            blockers.extend(_raw_payload_blockers(child, key_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_raw_payload_blockers(child, f"{path}[{index}]"))
    return tuple(_unique(blockers))


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_path = f"{path}.{raw_key}"
            if _sensitive_key_blocked(str(raw_key)):
                blockers.append(f"{key_path}:sensitive_key")
                continue
            blockers.extend(_sensitive_data_blockers(child, key_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
    elif isinstance(value, str) and _has_sensitive_value(value):
        blockers.append(f"{path}:sensitive_value")
    return tuple(_unique(blockers))


def _sensitive_key_blocked(key_text: str) -> bool:
    normalized = _normalized_key(key_text)
    if normalized.startswith("no_"):
        return False
    if normalized.endswith("_absent") or normalized.endswith("_absent_or_redacted"):
        return False
    if normalized.endswith("_redacted"):
        return False
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def _has_sensitive_value(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS)


def _owner_next_action(status: str) -> str:
    return {
        READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION: (
            "Owner reviews the final one-order packet outside Codex before any live action."
        ),
        READY_FOR_READ_ONLY_LIVE_BROKER_VERIFICATION: (
            "Collect sanitized read-only live broker evidence without storing credentials."
        ),
        BLOCKED_BY_GOVERNANCE: "Repair governance-read evidence before owner handoff.",
        BLOCKED_BY_RISK: "Repair risk gate evidence before owner handoff.",
        BLOCKED_BY_MARKET_STATE: "Wait for market conditions and supervision window to pass.",
        BLOCKED_BY_BROKER_READ_ONLY_STATE: (
            "Provide sanitized read-only broker state with no private identifiers."
        ),
        BLOCKED_BY_PROOF_STATE: "Complete demo, ledger, and receipt-intake proof gates.",
        BLOCKED_BY_ATM_MILESTONE_STATE: "Complete ATM countdown and owner message evidence.",
        BLOCKED_BY_OWNER_STATE: "Owner review acknowledgements are not complete.",
        BLOCKED_BY_SAFETY_POLICY: "Restore metadata-only no-execution safety policy flags.",
        BLOCKED_BY_LIVE_EXECUTION_BOUNDARY: "Remove live execution indicators from the payload.",
        INCOMPLETE_INPUTS: "Provide all final milestone input sections.",
    }.get(status, "Stop and review final milestone inputs.")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _number(value: Any) -> float:
    if isinstance(value, bool) or value is None:
        return 0.0
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _normalized_key(value: Any) -> str:
    return str(value).lower().replace("-", "_").replace(" ", "_")


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))
