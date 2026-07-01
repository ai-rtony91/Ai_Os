"""Metadata-only entry authority gate for AIOS Forex Vacation Mode."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_VACATION_MODE_ENTRY_AUTHORITY_GATE_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_ENTRY_AUTHORITY_GATE"

ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW = "ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW"
ENTRY_BLOCKED_BY_PRODUCT_POLICY = "ENTRY_BLOCKED_BY_PRODUCT_POLICY"
ENTRY_BLOCKED_BY_OWNER_AUTHORITY = "ENTRY_BLOCKED_BY_OWNER_AUTHORITY"
ENTRY_BLOCKED_BY_SETUP_SIGNAL = "ENTRY_BLOCKED_BY_SETUP_SIGNAL"
ENTRY_BLOCKED_BY_RISK = "ENTRY_BLOCKED_BY_RISK"
ENTRY_BLOCKED_BY_MARKET = "ENTRY_BLOCKED_BY_MARKET"
ENTRY_BLOCKED_BY_BROKER_READ_ONLY = "ENTRY_BLOCKED_BY_BROKER_READ_ONLY"
ENTRY_BLOCKED_BY_PROOF = "ENTRY_BLOCKED_BY_PROOF"
ENTRY_BLOCKED_BY_SAFETY = "ENTRY_BLOCKED_BY_SAFETY"
ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY = "ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

REQUIRED_SECTIONS = (
    "product_policy_state",
    "owner_authority_state",
    "setup_signal_state",
    "risk_state",
    "market_state",
    "broker_read_only_state",
    "proof_state",
    "safety_policy",
)

HARD_FALSE_FIELDS = (
    "live_trade_executed_by_this_module",
    "demo_trade_executed_by_this_module",
    "paper_trade_executed_by_this_module",
    "broker_api_called_by_this_module",
    "oanda_api_called_by_this_module",
    "credential_read",
    "credential_stored",
    "account_id_read",
    "account_id_stored",
    "order_placed",
    "order_closed",
    "money_moved",
    "bank_access_used",
    "withdrawal_initiated",
    "notification_sent",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "profit_guaranteed",
    "play_store_ready_claimed",
    "legal_compliance_ready_claimed",
    "sell_ready_claimed",
    "unbounded_autonomy_allowed",
    "repeat_without_review_allowed",
)


def evaluate_forex_vacation_mode_entry_authority_gate_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate whether an entry recommendation can be prepared for owner review."""

    source = _mapping(payload)
    if not source:
        return _entry_result(INCOMPLETE_INPUTS, False, ("payload_missing",), source)

    missing = _missing_sections(source, REQUIRED_SECTIONS)
    if missing:
        return _entry_result(INCOMPLETE_INPUTS, False, missing, source)

    product = _mapping(source.get("product_policy_state"))
    owner = _mapping(source.get("owner_authority_state"))
    setup = _mapping(source.get("setup_signal_state"))
    risk = _mapping(source.get("risk_state"))
    market = _mapping(source.get("market_state"))
    broker_read_only = _mapping(source.get("broker_read_only_state"))
    proof = _mapping(source.get("proof_state"))
    safety = _mapping(source.get("safety_policy"))

    live_boundary = _live_boundary_blockers(owner, broker_read_only, safety)
    if live_boundary:
        return _entry_result(
            ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY,
            False,
            live_boundary,
            source,
        )

    product_blockers = _product_policy_blockers(product)
    if product_blockers:
        return _entry_result(ENTRY_BLOCKED_BY_PRODUCT_POLICY, False, product_blockers, source)

    owner_blockers = _owner_authority_blockers(owner)
    if owner_blockers:
        return _entry_result(ENTRY_BLOCKED_BY_OWNER_AUTHORITY, False, owner_blockers, source)

    setup_blockers = _setup_signal_blockers(setup)
    if setup_blockers:
        return _entry_result(ENTRY_BLOCKED_BY_SETUP_SIGNAL, False, setup_blockers, source)

    risk_blockers = _risk_blockers(risk)
    if risk_blockers:
        return _entry_result(ENTRY_BLOCKED_BY_RISK, False, risk_blockers, source)

    market_blockers = _market_blockers(market)
    if market_blockers:
        return _entry_result(ENTRY_BLOCKED_BY_MARKET, False, market_blockers, source)

    read_only_blockers = _read_only_blockers(broker_read_only)
    if read_only_blockers:
        return _entry_result(
            ENTRY_BLOCKED_BY_BROKER_READ_ONLY,
            False,
            read_only_blockers,
            source,
        )

    proof_blockers = _proof_blockers(proof)
    if proof_blockers:
        return _entry_result(ENTRY_BLOCKED_BY_PROOF, False, proof_blockers, source)

    safety_blockers = _safety_blockers(safety)
    if safety_blockers:
        return _entry_result(ENTRY_BLOCKED_BY_SAFETY, False, safety_blockers, source)

    return _entry_result(ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW, True, (), source)


def base_hard_false_fields() -> dict[str, bool]:
    return {field: False for field in HARD_FALSE_FIELDS}


def hard_false_violations(result: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(field for field in HARD_FALSE_FIELDS if result.get(field) is not False)


def _entry_result(
    status: str,
    ready: bool,
    blockers: Sequence[str],
    source: Mapping[str, Any],
) -> dict[str, Any]:
    blocker_list = _unique(blockers)
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "metadata_only": True,
        "read_only": True,
        "owner_review_required": True,
        "entry_recommendation": {
            "type": "metadata_only_owner_review_entry_recommendation",
            "prepared": ready,
            "owner_visible_reason": _entry_reason(status),
            "order_intent": "none",
            "broker_action": "none",
        },
        "owner_next_action": _owner_next_action(status),
        "blockers": blocker_list,
        "source_sections_seen": sorted(str(key) for key in source.keys()),
        "safety": {
            "no_trade_execution": True,
            "no_broker_call": True,
            "no_oanda_call": True,
            "no_credential_access": True,
            "no_account_identifier_access": True,
            "repeat_attempt_requires_review": True,
        },
        **base_hard_false_fields(),
    }


def _product_policy_blockers(product: Mapping[str, Any]) -> tuple[str, ...]:
    return _required_true(
        product,
        (
            "policy_docs_present",
            "financial_risk_disclosure_present",
            "no_profit_guarantee_acknowledged",
            "no_passive_income_claim_acknowledged",
            "metadata_only_readiness_separated_from_live_authority",
            "owner_review_required_before_release",
        ),
    ) + _required_false(
        product,
        (
            "play_store_ready_claimed",
            "legal_compliance_ready_claimed",
            "sell_ready_claimed",
            "profit_ready_claimed",
        ),
    )


def _owner_authority_blockers(owner: Mapping[str, Any]) -> tuple[str, ...]:
    return _required_true(
        owner,
        (
            "owner_authority_approved",
            "owner_identity_confirmed",
            "owner_approval_current",
            "one_action_stop_acknowledged",
            "repeat_attempt_blocked_until_review",
        ),
    )


def _setup_signal_blockers(setup: Mapping[str, Any]) -> tuple[str, ...]:
    return _required_true(
        setup,
        (
            "setup_signal_valid",
            "entry_review_candidate_present",
            "strategy_metadata_present",
            "owner_visible_reason_present",
        ),
    )


def _risk_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    blockers = list(
        _required_true(
            risk,
            (
                "risk_per_trade_limit_defined",
                "daily_loss_limit_defined",
                "risk_within_limits",
                "stop_loss_ready",
                "exit_plan_ready",
                "max_loss_visible_to_owner",
            ),
        )
    )
    blockers.extend(_required_false(risk, ("daily_loss_stop_active", "kill_switch_active")))
    return tuple(blockers)


def _market_blockers(market: Mapping[str, Any]) -> tuple[str, ...]:
    return _required_true(
        market,
        (
            "market_open",
            "calendar_ready",
            "spread_within_limit",
            "supervision_window_ready",
        ),
    )


def _read_only_blockers(broker_read_only: Mapping[str, Any]) -> tuple[str, ...]:
    return _required_true(
        broker_read_only,
        ("metadata_only", "read_only", "execution_permission_false"),
    ) + _required_false(
        broker_read_only,
        ("execution_permission", "order_permission", "close_permission"),
    )


def _proof_blockers(proof: Mapping[str, Any]) -> tuple[str, ...]:
    return _required_true(
        proof,
        (
            "proof_ledger_ready",
            "receipt_contract_ready",
            "post_action_evidence_plan_ready",
            "sanitized_evidence_required",
        ),
    )


def _safety_blockers(safety: Mapping[str, Any]) -> tuple[str, ...]:
    return _required_true(
        safety,
        (
            "metadata_only",
            "no_trade_execution",
            "no_broker_call",
            "no_oanda_call",
            "no_credential_access",
            "no_account_identifier_access",
            "no_money_movement",
            "no_notification_send",
            "no_background_runtime",
        ),
    )


def _live_boundary_blockers(
    owner: Mapping[str, Any],
    broker_read_only: Mapping[str, Any],
    safety: Mapping[str, Any],
) -> tuple[str, ...]:
    return (
        _required_bool_false(
            owner,
            (
                "live_execution_authorized",
                "live_trade_authorized",
                "next_trade_authorized",
                "repeat_trade_authorized",
            ),
        )
        + _required_bool_false(
            broker_read_only,
            (
                "execution_permission",
                "order_permission",
                "close_permission",
            ),
        )
        + _required_bool_false(
            safety,
            (
                "trade_execution_allowed",
                "broker_call_allowed",
                "oanda_call_allowed",
            ),
        )
    )


def _required_true(source: Mapping[str, Any], fields: Sequence[str]) -> tuple[str, ...]:
    return tuple(f"{field}_required_true" for field in fields if source.get(field) is not True)


def _required_false(source: Mapping[str, Any], fields: Sequence[str]) -> tuple[str, ...]:
    return tuple(f"{field}_required_false" for field in fields if source.get(field) is not False)


def _required_bool_false(
    source: Mapping[str, Any],
    fields: Sequence[str],
) -> tuple[str, ...]:
    blockers: list[str] = []
    for name in fields:
        if name not in source or not isinstance(source.get(name), bool):
            blockers.append(f"{name}_required_bool")
        elif source.get(name) is True:
            blockers.append(f"{name}_must_remain_false")
    return tuple(blockers)


def _missing_sections(source: Mapping[str, Any], sections: Sequence[str]) -> tuple[str, ...]:
    return tuple(f"{section}_missing" for section in sections if not _mapping(source.get(section)))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _entry_reason(status: str) -> str:
    return {
        ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW: (
            "All metadata gates allow an owner-reviewed entry recommendation."
        ),
        ENTRY_BLOCKED_BY_PRODUCT_POLICY: "Product policy readiness is incomplete.",
        ENTRY_BLOCKED_BY_OWNER_AUTHORITY: "Owner authority metadata is incomplete.",
        ENTRY_BLOCKED_BY_SETUP_SIGNAL: "Setup signal metadata is incomplete.",
        ENTRY_BLOCKED_BY_RISK: "Risk metadata blocks entry review.",
        ENTRY_BLOCKED_BY_MARKET: "Market metadata blocks entry review.",
        ENTRY_BLOCKED_BY_BROKER_READ_ONLY: "Broker state is not read-only metadata.",
        ENTRY_BLOCKED_BY_PROOF: "Proof or receipt readiness is incomplete.",
        ENTRY_BLOCKED_BY_SAFETY: "Safety policy metadata is incomplete.",
        ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY: "Live execution boundary was not hard false.",
    }.get(status, "Inputs are incomplete.")


def _owner_next_action(status: str) -> str:
    if status == ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW:
        return "Owner may review the metadata-only entry recommendation; no order is placed."
    return "Repair blockers before preparing any entry recommendation."


__all__ = [
    "HARD_FALSE_FIELDS",
    "ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW",
    "ENTRY_BLOCKED_BY_PRODUCT_POLICY",
    "ENTRY_BLOCKED_BY_OWNER_AUTHORITY",
    "ENTRY_BLOCKED_BY_SETUP_SIGNAL",
    "ENTRY_BLOCKED_BY_RISK",
    "ENTRY_BLOCKED_BY_MARKET",
    "ENTRY_BLOCKED_BY_BROKER_READ_ONLY",
    "ENTRY_BLOCKED_BY_PROOF",
    "ENTRY_BLOCKED_BY_SAFETY",
    "ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY",
    "INCOMPLETE_INPUTS",
    "base_hard_false_fields",
    "hard_false_violations",
    "evaluate_forex_vacation_mode_entry_authority_gate_v1",
]
