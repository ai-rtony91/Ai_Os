"""Future OANDA demo order approval gate.

This gate evaluates whether a future corrected demo order can be presented for
manual owner decision. It never authorizes execution and performs no broker,
credential, Vault, environment, or dotenv access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-FUTURE-ORDER-APPROVAL-GATE-V1"

OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION = (
    "OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION"
)
BLOCKED_BY_MISSING_CORRECTED_PACKAGE = "BLOCKED_BY_MISSING_CORRECTED_PACKAGE"
BLOCKED_BY_MISSING_SLTP_VALIDATION = "BLOCKED_BY_MISSING_SLTP_VALIDATION"
BLOCKED_BY_PRIOR_CANCEL_NOT_CAPTURED = "BLOCKED_BY_PRIOR_CANCEL_NOT_CAPTURED"
BLOCKED_BY_ORDER_CAP_NOT_ACKNOWLEDGED = "BLOCKED_BY_ORDER_CAP_NOT_ACKNOWLEDGED"
BLOCKED_BY_MISSING_OWNER_APPROVAL = "BLOCKED_BY_MISSING_OWNER_APPROVAL"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_AUTONOMY_REQUEST = "BLOCKED_BY_AUTONOMY_REQUEST"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"


@dataclass(frozen=True)
class FutureOrderApprovalGateInput:
    corrected_order_package_ready: bool = False
    sltp_validation_ready: bool = False
    prior_cancel_evidence_captured: bool = False
    prior_order_cap_consumed_acknowledged: bool = False
    explicit_new_owner_approval: bool = False
    demo_only: bool = False
    one_order_only: bool = False
    no_live_endpoint: bool = False
    no_autonomous_order: bool = False
    post_trade_evidence_required: bool = False
    no_profit_claim: bool = False
    live_endpoint_requested: bool = False
    autonomous_order_requested: bool = False
    profit_claim_made: bool = False


def default_future_order_approval_gate_context_v1() -> dict[str, Any]:
    return {
        "corrected_order_package_ready": False,
        "sltp_validation_ready": False,
        "prior_cancel_evidence_captured": False,
        "prior_order_cap_consumed_acknowledged": False,
        "explicit_new_owner_approval": False,
        "demo_only": False,
        "one_order_only": False,
        "no_live_endpoint": False,
        "no_autonomous_order": False,
        "post_trade_evidence_required": False,
        "no_profit_claim": False,
        "live_endpoint_requested": False,
        "autonomous_order_requested": False,
        "profit_claim_made": False,
    }


def evaluate_oanda_demo_future_order_approval_gate_v1(
    gate_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = default_future_order_approval_gate_context_v1()
    if gate_context:
        context.update(dict(gate_context))

    normalized = _normalize_input(context)
    blockers = _classify_blockers(normalized)
    classification = (
        blockers[0] if blockers else OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION
    )
    ready_for_manual_decision = (
        classification == OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION
    )

    return {
        "packet_id": PACKET_ID,
        "script_status": classification,
        "classification": classification,
        "ready_for_manual_decision": ready_for_manual_decision,
        "blockers": blockers,
        "approval_gate": {
            "owner_manual_decision_required": True,
            "order_execution_authorized": False,
            "automatic_order_authorized": False,
            "broker_command_authorized_for_codex": False,
            "future_demo_order_may_be_considered_by_owner": ready_for_manual_decision,
            "explicit_new_owner_approval_observed": (
                normalized.explicit_new_owner_approval
            ),
            "prior_order_cap_consumed_acknowledged": (
                normalized.prior_order_cap_consumed_acknowledged
            ),
            "post_trade_evidence_required": normalized.post_trade_evidence_required,
        },
        "input_summary": {
            "corrected_order_package_ready": normalized.corrected_order_package_ready,
            "sltp_validation_ready": normalized.sltp_validation_ready,
            "prior_cancel_evidence_captured": (
                normalized.prior_cancel_evidence_captured
            ),
            "prior_order_cap_consumed_acknowledged": (
                normalized.prior_order_cap_consumed_acknowledged
            ),
            "explicit_new_owner_approval": normalized.explicit_new_owner_approval,
            "demo_only": normalized.demo_only,
            "one_order_only": normalized.one_order_only,
            "no_live_endpoint": normalized.no_live_endpoint,
            "no_autonomous_order": normalized.no_autonomous_order,
            "post_trade_evidence_required": normalized.post_trade_evidence_required,
            "no_profit_claim": normalized.no_profit_claim,
        },
        "safety_boundaries": {
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "vault_read_performed": False,
            "environment_read_performed": False,
            "dotenv_read_performed": False,
            "live_endpoint_used": False,
            "scheduler_created": False,
            "daemon_created": False,
            "webhook_created": False,
            "profit_claimed": False,
            "fill_claimed": False,
        },
        "next_safe_action": "owner_manual_decision_only_no_broker_command_by_codex",
    }


def _classify_blockers(normalized: FutureOrderApprovalGateInput) -> list[str]:
    blockers: list[str] = []

    if not normalized.corrected_order_package_ready:
        blockers.append(BLOCKED_BY_MISSING_CORRECTED_PACKAGE)

    if not normalized.sltp_validation_ready:
        blockers.append(BLOCKED_BY_MISSING_SLTP_VALIDATION)

    if not normalized.prior_cancel_evidence_captured:
        blockers.append(BLOCKED_BY_PRIOR_CANCEL_NOT_CAPTURED)

    if (
        not normalized.prior_order_cap_consumed_acknowledged
        or not normalized.one_order_only
    ):
        blockers.append(BLOCKED_BY_ORDER_CAP_NOT_ACKNOWLEDGED)

    if not normalized.explicit_new_owner_approval:
        blockers.append(BLOCKED_BY_MISSING_OWNER_APPROVAL)

    if (
        not normalized.demo_only
        or not normalized.no_live_endpoint
        or normalized.live_endpoint_requested
    ):
        blockers.append(BLOCKED_BY_LIVE_ENDPOINT)

    if (
        not normalized.no_autonomous_order
        or not normalized.post_trade_evidence_required
        or normalized.autonomous_order_requested
    ):
        blockers.append(BLOCKED_BY_AUTONOMY_REQUEST)

    if not normalized.no_profit_claim or normalized.profit_claim_made:
        blockers.append(BLOCKED_BY_PROFIT_CLAIM)

    return _dedupe(blockers)


def _normalize_input(context: Mapping[str, Any]) -> FutureOrderApprovalGateInput:
    return FutureOrderApprovalGateInput(
        corrected_order_package_ready=_bool(
            context.get("corrected_order_package_ready")
        ),
        sltp_validation_ready=_bool(context.get("sltp_validation_ready")),
        prior_cancel_evidence_captured=_bool(
            context.get("prior_cancel_evidence_captured")
        ),
        prior_order_cap_consumed_acknowledged=_bool(
            context.get("prior_order_cap_consumed_acknowledged")
        ),
        explicit_new_owner_approval=_bool(context.get("explicit_new_owner_approval")),
        demo_only=_bool(context.get("demo_only")),
        one_order_only=_bool(context.get("one_order_only")),
        no_live_endpoint=_bool(context.get("no_live_endpoint")),
        no_autonomous_order=_bool(context.get("no_autonomous_order")),
        post_trade_evidence_required=_bool(
            context.get("post_trade_evidence_required")
        ),
        no_profit_claim=_bool(context.get("no_profit_claim")),
        live_endpoint_requested=_bool(context.get("live_endpoint_requested")),
        autonomous_order_requested=_bool(context.get("autonomous_order_requested")),
        profit_claim_made=_bool(context.get("profit_claim_made")),
    )


def _bool(value: Any) -> bool:
    return bool(value)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped
