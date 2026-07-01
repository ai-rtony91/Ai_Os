"""Build the final owner review packet for a single live micro action."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_LIVE_MICRO_TRADE_OWNER_FINAL_DECISION_PACKET_V1"
MODE = "READ_ONLY_METADATA_ONLY_OWNER_FINAL_DECISION_PACKET"
NO_TRADE_STATEMENT = (
    "Codex did not place a trade. AIOS did not place a trade. "
    "This packet is a final owner review packet only."
)

OWNER_PACKET_READY_REVIEW_ONLY = "OWNER_PACKET_READY_REVIEW_ONLY"
OWNER_PACKET_BLOCKED_BY_MILESTONE = "OWNER_PACKET_BLOCKED_BY_MILESTONE"
OWNER_PACKET_BLOCKED_BY_RISK_ACK = "OWNER_PACKET_BLOCKED_BY_RISK_ACK"
OWNER_PACKET_BLOCKED_BY_EVIDENCE_PLAN = "OWNER_PACKET_BLOCKED_BY_EVIDENCE_PLAN"
OWNER_PACKET_BLOCKED_BY_SAFETY = "OWNER_PACKET_BLOCKED_BY_SAFETY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

MILESTONE_READY_STATUS = "READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION"

REQUIRED_SECTIONS = (
    "milestone_result",
    "owner_decision_context",
    "risk_acknowledgement",
    "evidence_capture_plan",
    "safety_policy",
)

RISK_TRUE_FIELDS = (
    "owner_understands_loss_possible",
    "owner_understands_no_profit_guarantee",
    "stop_loss_required",
    "take_profit_or_exit_plan_required",
    "one_order_only",
    "no_repeat_without_review",
    "account_protection_priority",
)

EVIDENCE_TRUE_FIELDS = (
    "broker_receipt_required",
    "entry_receipt_required",
    "exit_receipt_required",
    "realized_pnl_required",
    "cost_reconciliation_required",
    "post_trade_review_required",
    "sanitized_receipts_only",
    "repeat_attempt_blocked_until_review",
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
    "review_only",
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


def evaluate_forex_live_micro_trade_owner_final_decision_packet_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    if not source:
        return _build(
            status=INCOMPLETE_INPUTS,
            blockers=("payload_missing",),
            milestone_result={},
            owner_context={},
            risk_ack={},
            evidence_plan={},
        )

    missing_sections = [
        section for section in REQUIRED_SECTIONS if not _mapping(source.get(section))
    ]
    if missing_sections:
        return _build(
            status=INCOMPLETE_INPUTS,
            blockers=tuple(f"{section}_missing" for section in missing_sections),
            milestone_result=_mapping(source.get("milestone_result")),
            owner_context=_mapping(source.get("owner_decision_context")),
            risk_ack=_mapping(source.get("risk_acknowledgement")),
            evidence_plan=_mapping(source.get("evidence_capture_plan")),
        )

    milestone = _mapping(source.get("milestone_result"))
    owner_context = _mapping(source.get("owner_decision_context"))
    risk_ack = _mapping(source.get("risk_acknowledgement"))
    evidence_plan = _mapping(source.get("evidence_capture_plan"))
    safety = _mapping(source.get("safety_policy"))

    if milestone.get("status") != MILESTONE_READY_STATUS:
        return _build(
            status=OWNER_PACKET_BLOCKED_BY_MILESTONE,
            blockers=(f"milestone_status_{milestone.get('status', 'UNKNOWN')}",),
            milestone_result=milestone,
            owner_context=owner_context,
            risk_ack=risk_ack,
            evidence_plan=evidence_plan,
        )

    risk_blockers = _risk_ack_blockers(risk_ack)
    if risk_blockers:
        return _build(
            status=OWNER_PACKET_BLOCKED_BY_RISK_ACK,
            blockers=risk_blockers,
            milestone_result=milestone,
            owner_context=owner_context,
            risk_ack=risk_ack,
            evidence_plan=evidence_plan,
        )

    evidence_blockers = _evidence_plan_blockers(evidence_plan)
    if evidence_blockers:
        return _build(
            status=OWNER_PACKET_BLOCKED_BY_EVIDENCE_PLAN,
            blockers=evidence_blockers,
            milestone_result=milestone,
            owner_context=owner_context,
            risk_ack=risk_ack,
            evidence_plan=evidence_plan,
        )

    safety_blockers = _true_field_blockers(safety, SAFETY_TRUE_FIELDS)
    if safety_blockers:
        return _build(
            status=OWNER_PACKET_BLOCKED_BY_SAFETY,
            blockers=safety_blockers,
            milestone_result=milestone,
            owner_context=owner_context,
            risk_ack=risk_ack,
            evidence_plan=evidence_plan,
        )

    return _build(
        status=OWNER_PACKET_READY_REVIEW_ONLY,
        blockers=(),
        milestone_result=milestone,
        owner_context=owner_context,
        risk_ack=risk_ack,
        evidence_plan=evidence_plan,
    )


def _build(
    *,
    status: str,
    blockers: Sequence[str],
    milestone_result: Mapping[str, Any],
    owner_context: Mapping[str, Any],
    risk_ack: Mapping[str, Any],
    evidence_plan: Mapping[str, Any],
) -> dict[str, Any]:
    ready = status == OWNER_PACKET_READY_REVIEW_ONLY
    hard_false = {field: False for field in HARD_FALSE_FIELDS}
    max_risk = _number(risk_ack.get("max_risk_per_trade_pct"))
    max_daily = _number(risk_ack.get("max_daily_loss_pct"))
    expected_evidence = evidence_plan.get("expected_evidence_after_action")
    if not isinstance(expected_evidence, list):
        expected_evidence = [
            "sanitized_broker_receipt",
            "sanitized_exit_receipt",
            "realized_pnl_after_costs",
            "post_trade_review",
        ]
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "final_status": status,
        "status": status,
        "ready": ready,
        "trade_scope": owner_context.get(
            "trade_scope", "single_owner_governed_live_micro_trade_review_only"
        ),
        "max_risk_per_trade_pct": max_risk,
        "max_daily_loss_pct": max_daily,
        "one_order_only": risk_ack.get("one_order_only") is True,
        "stop_loss_required": risk_ack.get("stop_loss_required") is True,
        "take_profit_or_exit_plan_required": risk_ack.get(
            "take_profit_or_exit_plan_required"
        )
        is True,
        "no_repeat_without_review": risk_ack.get("no_repeat_without_review") is True,
        "expected_evidence_after_action": list(expected_evidence),
        "owner_must_confirm": [
            "one_order_only",
            "loss_possible",
            "no_profit_guarantee",
            "stop_after_attempt",
            "collect_sanitized_evidence",
        ],
        "owner_denial_option": "Owner may deny or defer the live micro action.",
        "exact_stop_conditions": list(
            evidence_plan.get(
                "exact_stop_conditions",
                [
                    "after_fill_or_rejection",
                    "after_timeout",
                    "after_error",
                    "after_owner_denial",
                    "after_any_rule_mismatch",
                ],
            )
        ),
        "no_profit_guarantee_statement": (
            "Profit is not guaranteed. Loss is possible even when all gates pass."
        ),
        "no_autonomous_execution_statement": (
            "AIOS must not autonomously execute, repeat, or re-enter live action."
        ),
        "no_money_movement_statement": (
            "This packet does not authorize deposit, withdrawal, or bank access."
        ),
        "no_trade_statement": NO_TRADE_STATEMENT,
        "milestone_status": milestone_result.get("status", "UNKNOWN"),
        "exact_blockers": list(blockers),
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


def _risk_ack_blockers(risk_ack: Mapping[str, Any]) -> tuple[str, ...]:
    blockers = _true_field_blockers(risk_ack, RISK_TRUE_FIELDS)
    if "max_risk_per_trade_pct" not in risk_ack:
        blockers.append("max_risk_per_trade_pct_missing")
    elif _number(risk_ack.get("max_risk_per_trade_pct")) > 0.005:
        blockers.append("max_risk_per_trade_pct_above_0_005")
    if "max_daily_loss_pct" not in risk_ack:
        blockers.append("max_daily_loss_pct_missing")
    elif _number(risk_ack.get("max_daily_loss_pct")) > 0.02:
        blockers.append("max_daily_loss_pct_above_0_02")
    return tuple(_unique(blockers))


def _evidence_plan_blockers(plan: Mapping[str, Any]) -> tuple[str, ...]:
    blockers = _true_field_blockers(plan, EVIDENCE_TRUE_FIELDS)
    expected = plan.get("expected_evidence_after_action")
    if not isinstance(expected, list) or not expected:
        blockers.append("expected_evidence_after_action_missing")
    stop_conditions = plan.get("exact_stop_conditions")
    if not isinstance(stop_conditions, list) or not stop_conditions:
        blockers.append("exact_stop_conditions_missing")
    return tuple(_unique(blockers))


def _true_field_blockers(data: Mapping[str, Any], fields: Sequence[str]) -> list[str]:
    blockers = [f"{field}_missing" for field in fields if field not in data]
    for field in fields:
        if field in data and data.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    return _unique(blockers)


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


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))
