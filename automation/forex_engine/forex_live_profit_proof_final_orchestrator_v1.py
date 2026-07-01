"""Final owner-facing orchestrator for live profit proof readiness."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from automation.forex_engine import (
    forex_broker_verified_live_profit_proof_milestone_v1 as milestone,
)
from automation.forex_engine import (
    forex_live_micro_trade_owner_final_decision_packet_v1 as owner_packet,
)
from automation.forex_engine import (
    forex_live_receipt_evidence_intake_contract_v1 as receipt_contract,
)

SCHEMA = "AIOS_FOREX_LIVE_PROFIT_PROOF_FINAL_ORCHESTRATOR_V1"
MODE = "READ_ONLY_METADATA_ONLY_FINAL_OWNER_HANDOFF_ORCHESTRATOR"
MILESTONE_NAME = "AIOS Forex Broker-Verified Live Profit Proof Milestone V1"

FINAL_MILESTONE_READY_FOR_OWNER_ACTION = "FINAL_MILESTONE_READY_FOR_OWNER_ACTION"
FINAL_MILESTONE_READY_FOR_READ_ONLY_BROKER_VERIFICATION = (
    "FINAL_MILESTONE_READY_FOR_READ_ONLY_BROKER_VERIFICATION"
)
FINAL_MILESTONE_BLOCKED_BY_GOVERNANCE = "FINAL_MILESTONE_BLOCKED_BY_GOVERNANCE"
FINAL_MILESTONE_BLOCKED_BY_RISK = "FINAL_MILESTONE_BLOCKED_BY_RISK"
FINAL_MILESTONE_BLOCKED_BY_MARKET = "FINAL_MILESTONE_BLOCKED_BY_MARKET"
FINAL_MILESTONE_BLOCKED_BY_BROKER_READ_ONLY = (
    "FINAL_MILESTONE_BLOCKED_BY_BROKER_READ_ONLY"
)
FINAL_MILESTONE_BLOCKED_BY_PROOF = "FINAL_MILESTONE_BLOCKED_BY_PROOF"
FINAL_MILESTONE_BLOCKED_BY_OWNER_REVIEW = "FINAL_MILESTONE_BLOCKED_BY_OWNER_REVIEW"
FINAL_MILESTONE_BLOCKED_BY_SAFETY = "FINAL_MILESTONE_BLOCKED_BY_SAFETY"
FINAL_MILESTONE_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY = (
    "FINAL_MILESTONE_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY"
)
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

HARD_FALSE_FIELDS = milestone.HARD_FALSE_FIELDS


def evaluate_forex_live_profit_proof_final_orchestrator_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    if not source:
        return _build(
            status=INCOMPLETE_INPUTS,
            milestone_result=milestone.evaluate_forex_broker_verified_live_profit_proof_milestone_v1(
                None
            ),
            owner_packet_result=owner_packet.evaluate_forex_live_micro_trade_owner_final_decision_packet_v1(
                None
            ),
            receipt_contract_result=receipt_contract.evaluate_forex_live_receipt_evidence_intake_contract_v1(
                None
            ),
        )

    milestone_payload = _mapping(source.get("milestone_payload"))
    milestone_result = milestone.evaluate_forex_broker_verified_live_profit_proof_milestone_v1(
        dict(milestone_payload)
    )

    owner_payload = dict(_mapping(source.get("owner_packet_payload")))
    if owner_payload and "milestone_result" not in owner_payload:
        owner_payload["milestone_result"] = milestone_result
    owner_packet_result = (
        owner_packet.evaluate_forex_live_micro_trade_owner_final_decision_packet_v1(
            owner_payload
        )
    )

    receipt_payload = _mapping(source.get("receipt_contract_payload"))
    receipt_contract_result = (
        receipt_contract.evaluate_forex_live_receipt_evidence_intake_contract_v1(
            dict(receipt_payload)
        )
    )

    final_status = _final_status(
        milestone_result=milestone_result,
        owner_packet_result=owner_packet_result,
        receipt_contract_result=receipt_contract_result,
    )
    return _build(
        status=final_status,
        milestone_result=milestone_result,
        owner_packet_result=owner_packet_result,
        receipt_contract_result=receipt_contract_result,
    )


def _build(
    *,
    status: str,
    milestone_result: Mapping[str, Any],
    owner_packet_result: Mapping[str, Any],
    receipt_contract_result: Mapping[str, Any],
) -> dict[str, Any]:
    ready = status == FINAL_MILESTONE_READY_FOR_OWNER_ACTION
    hard_false = {field: False for field in HARD_FALSE_FIELDS}
    exact_blockers = _exact_blockers(
        milestone_result, owner_packet_result, receipt_contract_result
    )
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "milestone_name": MILESTONE_NAME,
        "current_phase": "FINAL_OWNER_HANDOFF_REVIEW_ONLY",
        "owner_next_action": _owner_next_action(status),
        "exact_blockers": exact_blockers,
        "local_work_complete": status
        in {
            FINAL_MILESTONE_READY_FOR_OWNER_ACTION,
            FINAL_MILESTONE_READY_FOR_READ_ONLY_BROKER_VERIFICATION,
        },
        "external_evidence_required": status
        != FINAL_MILESTONE_READY_FOR_OWNER_ACTION,
        "read_only_broker_verification_required": status
        == FINAL_MILESTONE_READY_FOR_READ_ONLY_BROKER_VERIFICATION,
        "live_micro_trade_owner_action_required": ready,
        "post_live_evidence_required": ready,
        "milestone_result": dict(milestone_result),
        "owner_packet_result": dict(owner_packet_result),
        "receipt_contract_result": dict(receipt_contract_result),
        "final_scorecard": _scorecard(
            status, milestone_result, owner_packet_result, receipt_contract_result
        ),
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


def _final_status(
    *,
    milestone_result: Mapping[str, Any],
    owner_packet_result: Mapping[str, Any],
    receipt_contract_result: Mapping[str, Any],
) -> str:
    milestone_status = str(milestone_result.get("status", ""))
    owner_status = str(owner_packet_result.get("status", ""))
    receipt_status = str(receipt_contract_result.get("status", ""))

    if milestone_status == milestone.INCOMPLETE_INPUTS:
        return INCOMPLETE_INPUTS
    if milestone_status == milestone.READY_FOR_READ_ONLY_LIVE_BROKER_VERIFICATION:
        return FINAL_MILESTONE_READY_FOR_READ_ONLY_BROKER_VERIFICATION
    if milestone_status == milestone.BLOCKED_BY_GOVERNANCE:
        return FINAL_MILESTONE_BLOCKED_BY_GOVERNANCE
    if milestone_status == milestone.BLOCKED_BY_RISK:
        return FINAL_MILESTONE_BLOCKED_BY_RISK
    if milestone_status == milestone.BLOCKED_BY_MARKET_STATE:
        return FINAL_MILESTONE_BLOCKED_BY_MARKET
    if milestone_status == milestone.BLOCKED_BY_BROKER_READ_ONLY_STATE:
        return FINAL_MILESTONE_BLOCKED_BY_BROKER_READ_ONLY
    if milestone_status in {
        milestone.BLOCKED_BY_PROOF_STATE,
        milestone.BLOCKED_BY_ATM_MILESTONE_STATE,
    }:
        return FINAL_MILESTONE_BLOCKED_BY_PROOF
    if milestone_status == milestone.BLOCKED_BY_OWNER_STATE:
        return FINAL_MILESTONE_BLOCKED_BY_OWNER_REVIEW
    if milestone_status == milestone.BLOCKED_BY_SAFETY_POLICY:
        return FINAL_MILESTONE_BLOCKED_BY_SAFETY
    if milestone_status == milestone.BLOCKED_BY_LIVE_EXECUTION_BOUNDARY:
        return FINAL_MILESTONE_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY

    if owner_status == owner_packet.INCOMPLETE_INPUTS:
        return INCOMPLETE_INPUTS
    if owner_status == owner_packet.OWNER_PACKET_BLOCKED_BY_SAFETY:
        return FINAL_MILESTONE_BLOCKED_BY_SAFETY
    if owner_status != owner_packet.OWNER_PACKET_READY_REVIEW_ONLY:
        return FINAL_MILESTONE_BLOCKED_BY_OWNER_REVIEW

    if receipt_status == receipt_contract.INCOMPLETE_INPUTS:
        return INCOMPLETE_INPUTS
    if receipt_status in {
        receipt_contract.BLOCKED_BY_SENSITIVE_DATA,
        receipt_contract.BLOCKED_BY_RAW_PAYLOAD,
    }:
        return FINAL_MILESTONE_BLOCKED_BY_SAFETY
    if receipt_status not in {
        receipt_contract.LIVE_RECEIPT_EVIDENCE_CONTRACT_READY,
        receipt_contract.LIVE_RECEIPT_EVIDENCE_COMPLETE,
    }:
        return FINAL_MILESTONE_BLOCKED_BY_PROOF

    return FINAL_MILESTONE_READY_FOR_OWNER_ACTION


def _scorecard(
    status: str,
    milestone_result: Mapping[str, Any],
    owner_packet_result: Mapping[str, Any],
    receipt_contract_result: Mapping[str, Any],
) -> dict[str, Any]:
    milestone_ready = milestone_result.get("status") in {
        milestone.READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION,
        milestone.READY_FOR_READ_ONLY_LIVE_BROKER_VERIFICATION,
    }
    owner_ready = owner_packet_result.get("status") == owner_packet.OWNER_PACKET_READY_REVIEW_ONLY
    receipt_ready = receipt_contract_result.get("status") in {
        receipt_contract.LIVE_RECEIPT_EVIDENCE_CONTRACT_READY,
        receipt_contract.LIVE_RECEIPT_EVIDENCE_COMPLETE,
    }
    return {
        "governance_readiness": _band(
            milestone_result.get("status") != milestone.BLOCKED_BY_GOVERNANCE
        ),
        "risk_readiness": _band(
            milestone_result.get("status") != milestone.BLOCKED_BY_RISK
        ),
        "market_readiness": _band(
            milestone_result.get("status") != milestone.BLOCKED_BY_MARKET_STATE
        ),
        "broker_read_only_readiness": _band(
            milestone_result.get("status")
            != milestone.BLOCKED_BY_BROKER_READ_ONLY_STATE
        ),
        "atm_milestone_readiness": _band(
            milestone_result.get("status")
            != milestone.BLOCKED_BY_ATM_MILESTONE_STATE
        ),
        "proof_ledger_readiness": _band(
            milestone_result.get("status") != milestone.BLOCKED_BY_PROOF_STATE
        ),
        "live_micro_trade_owner_packet_readiness": _band(owner_ready),
        "receipt_intake_contract_readiness": _band(receipt_ready),
        "post_trade_review_readiness": _band(receipt_ready),
        "repeat_attempt_gate_readiness": _band(receipt_ready),
        "final_milestone_readiness": {
            "percent": 100 if status == FINAL_MILESTONE_READY_FOR_OWNER_ACTION else 80,
            "status": status,
        },
        "local_control_plane_ready": milestone_ready and owner_ready and receipt_ready,
    }


def _band(ready: bool) -> dict[str, Any]:
    return {"percent": 100 if ready else 0, "status": "READY" if ready else "BLOCKED"}


def _exact_blockers(
    milestone_result: Mapping[str, Any],
    owner_packet_result: Mapping[str, Any],
    receipt_contract_result: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    for prefix, result in (
        ("milestone", milestone_result),
        ("owner_packet", owner_packet_result),
        ("receipt_contract", receipt_contract_result),
    ):
        for blocker in result.get("exact_blockers", []):
            blockers.append(f"{prefix}:{blocker}")
    return sorted(set(blockers))


def _owner_next_action(status: str) -> str:
    return {
        FINAL_MILESTONE_READY_FOR_OWNER_ACTION: (
            "Owner may review the one-order packet outside Codex; Codex stops here."
        ),
        FINAL_MILESTONE_READY_FOR_READ_ONLY_BROKER_VERIFICATION: (
            "Owner supplies sanitized read-only broker verification evidence."
        ),
        FINAL_MILESTONE_BLOCKED_BY_GOVERNANCE: "Repair governance evidence.",
        FINAL_MILESTONE_BLOCKED_BY_RISK: "Repair risk gate evidence.",
        FINAL_MILESTONE_BLOCKED_BY_MARKET: "Wait for safe market window evidence.",
        FINAL_MILESTONE_BLOCKED_BY_BROKER_READ_ONLY: (
            "Supply sanitized read-only broker state with no private identifiers."
        ),
        FINAL_MILESTONE_BLOCKED_BY_PROOF: "Repair proof, ATM, or receipt evidence.",
        FINAL_MILESTONE_BLOCKED_BY_OWNER_REVIEW: "Complete owner review packet inputs.",
        FINAL_MILESTONE_BLOCKED_BY_SAFETY: "Remove unsafe or private data inputs.",
        FINAL_MILESTONE_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY: (
            "Remove live execution flags and stop."
        ),
        INCOMPLETE_INPUTS: "Provide all orchestrator payload sections.",
    }.get(status, "Stop and review final orchestrator inputs.")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
