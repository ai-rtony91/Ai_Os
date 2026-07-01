"""Roll up the Forex proof data pipeline from receipt intake to live micro review."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_demo_receipt_proof_router_v1 import (
    BLOCKED_BY_BANKING_FOCUS as ROUTER_BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_OANDA_DEMO_BOUNDARY,
    BLOCKED_BY_ORDER_COUNT,
    BLOCKED_BY_RECEIPT_MISSING,
    BLOCKED_BY_RECEIPT_UNSANITIZED,
    BLOCKED_BY_SENSITIVE_DATA as ROUTER_BLOCKED_BY_SENSITIVE_DATA,
    DEMO_RECEIPT_PROOF_ROUTED,
    INCOMPLETE_INPUTS as ROUTER_INCOMPLETE_INPUTS,
    PROOF_DATA_WAITING_FOR_DEMO_RECEIPT,
    evaluate_forex_demo_receipt_proof_router_v1,
)
from automation.forex_engine.forex_profit_repeatability_evidence_v1 import (
    BLOCKED_BY_DRAWDOWN,
    BLOCKED_BY_INSUFFICIENT_SAMPLE,
    BLOCKED_BY_NEGATIVE_EXPECTANCY,
    BLOCKED_BY_BANKING_FOCUS as REPEATABILITY_BLOCKED_BY_BANKING,
    BLOCKED_BY_SENSITIVE_DATA as REPEATABILITY_BLOCKED_BY_SENSITIVE_DATA,
    BLOCKED_BY_UNREALISTIC_RETURN_CLAIM,
    CONTINUE_DEMO_PROOF_CAPTURE,
    REPEATABILITY_EVIDENCE_READY_FOR_REVIEW,
    evaluate_forex_profit_repeatability_evidence_v1,
)
from automation.forex_engine.forex_proof_data_intake_v1 import (
    BLOCKED_BY_BANKING_FOCUS as INTAKE_BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_FAKE_PROOF_CLAIM,
    BLOCKED_BY_SENSITIVE_DATA as INTAKE_BLOCKED_BY_SENSITIVE_DATA,
    INCOMPLETE_INPUTS as INTAKE_INCOMPLETE_INPUTS,
    PROOF_DATA_READY_FOR_ROUTING,
    PROOF_DATA_WAITING_FOR_DEMO_RECEIPT,
    BLOCKED_BY_UNSANITIZED_PROOF_DATA,
    evaluate_forex_proof_data_intake_v1,
)
from automation.forex_engine.forex_proof_to_live_micro_gate_v1 import (
    BLOCKED_BY_DEMO_RECEIPT_REQUIRED,
    BLOCKED_BY_OWNER_APPROVAL,
    BLOCKED_BY_REPEATABILITY,
    BLOCKED_BY_RISK_GATES,
    CONTINUE_DEMO_PROOF_CAPTURE as LIVE_CONTINUE_DEMO_PROOF_CAPTURE,
    READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW,
    INCOMPLETE_INPUTS as LIVE_INCOMPLETE_INPUTS,
    BLOCKED_BY_SENSITIVE_DATA as LIVE_BLOCKED_BY_SENSITIVE_DATA,
    BLOCKED_BY_BANKING_FOCUS as LIVE_BLOCKED_BY_BANKING_FOCUS,
    evaluate_forex_proof_to_live_micro_gate_v1,
)
from automation.forex_engine.forex_post_trade_proof_journal_v1 import (
    BLOCKED_BY_BANKING_FOCUS as JOURNAL_BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_PNL_RECORD,
    BLOCKED_BY_POST_TRADE_REVIEW,
    BLOCKED_BY_RECEIPT_PROOF,
    BLOCKED_BY_SENSITIVE_DATA as JOURNAL_BLOCKED_BY_SENSITIVE_DATA,
    INCOMPLETE_INPUTS as JOURNAL_INCOMPLETE_INPUTS,
    POST_TRADE_PROOF_JOURNAL_READY,
    evaluate_forex_post_trade_proof_journal_v1,
)

SCHEMA = "AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1"
MODE = "READ_ONLY_METADATA_ONLY_PROOF_PIPELINE_PAUSE_AND_CONTINUE"

PROOF_PIPELINE_READY_TO_CONTINUE = "PROOF_PIPELINE_READY_TO_CONTINUE"
PROOF_DATA_WAITING_FOR_DEMO_RECEIPT = "PROOF_DATA_WAITING_FOR_DEMO_RECEIPT"
CONTINUE_DEMO_PROOF_CAPTURE = "CONTINUE_DEMO_PROOF_CAPTURE"
READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW = (
    "READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW"
)
BLOCKED_BY_PROOF_INTAKE = "BLOCKED_BY_PROOF_INTAKE"
BLOCKED_BY_RECEIPT_ROUTING = "BLOCKED_BY_RECEIPT_ROUTING"
BLOCKED_BY_POST_TRADE_JOURNAL = "BLOCKED_BY_POST_TRADE_JOURNAL"
BLOCKED_BY_REPEATABILITY = "BLOCKED_BY_REPEATABILITY"
BLOCKED_BY_LIVE_MICRO_GATE = "BLOCKED_BY_LIVE_MICRO_GATE"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_OANDA_DEMO_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW_V1"

HARD_FALSE_FIELDS = (
    "live_trade_executed",
    "live_execution_authorized",
    "demo_trade_executed_by_this_module",
    "broker_api_called",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "money_moved",
    "bank_access_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token_value",
    "password",
    "master_password",
    "vault_password",
    "account_number",
    "routing_number",
    "card_number",
    "debit_card_number",
    "cvv",
    "account_id",
    "oanda_account_id",
    "bearer",
    "broker_token",
    "access_token",
    "private_key",
)

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer",
    "api key",
    "token value",
    "broker token",
    "access token",
    "private key",
    "password",
    "secret",
    "-----begin",
)

BANKING_KEY_PARTS = (
    "bank",
    "banking",
    "withdraw",
    "withdrawal",
    "transfer",
    "debit",
    "card",
    "rail",
    "ach",
    "wire",
    "sweep",
    "bucket_purge",
    "money_movement",
    "deposit",
)

BANKING_ALLOWED_FALSE_FIELDS = frozenset(
    {
        "money_moved",
        "money_movement_allowed",
        "bank_access_used",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
    }
)


def evaluate_forex_proof_pipeline_pause_and_continue_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build_result(
            campaign_status=BLOCKED_BY_SENSITIVE_DATA,
            blockers=tuple(sensitive_blockers),
            proof_data_present=False,
            proof_data_sanitized=False,
            campaign_ready=False,
            proof_intake_summary={},
            receipt_router_summary={},
            post_trade_journal_summary={},
            repeatability_summary={},
            live_micro_gate_summary={},
            next_best_packet=NEXT_BEST_PACKET,
            proof_data_destination_map=_destination_map(
                intake_status=BLOCKED_BY_SENSITIVE_DATA,
                router_status=None,
                journal_status=None,
                repeatability_status=None,
                live_status=None,
                receipt_present=False,
            ),
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build_result(
            campaign_status=BLOCKED_BY_BANKING_FOCUS,
            blockers=tuple(banking_blockers),
            proof_data_present=False,
            proof_data_sanitized=False,
            campaign_ready=False,
            proof_intake_summary={},
            receipt_router_summary={},
            post_trade_journal_summary={},
            repeatability_summary={},
            live_micro_gate_summary={},
            next_best_packet=NEXT_BEST_PACKET,
            proof_data_destination_map=_destination_map(
                intake_status=BLOCKED_BY_BANKING_FOCUS,
                router_status=None,
                journal_status=None,
                repeatability_status=None,
                live_status=None,
                receipt_present=False,
            ),
        )

    if not source:
        return _build_result(
            campaign_status=INCOMPLETE_INPUTS,
            blockers=("payload_missing",),
            proof_data_present=False,
            proof_data_sanitized=False,
            campaign_ready=False,
            proof_intake_summary={},
            receipt_router_summary={},
            post_trade_journal_summary={},
            repeatability_summary={},
            live_micro_gate_summary={},
            next_best_packet=NEXT_BEST_PACKET,
            proof_data_destination_map=_destination_map(
                intake_status=INCOMPLETE_INPUTS,
                router_status=None,
                journal_status=None,
                repeatability_status=None,
                live_status=None,
                receipt_present=False,
            ),
        )

    intake_result = evaluate_forex_proof_data_intake_v1(
        {"proof_source": _mapping(source.get("proof_source"))}
    )
    if intake_result["status"] == PROOF_DATA_WAITING_FOR_DEMO_RECEIPT:
        return _build_result(
            campaign_status=PROOF_DATA_WAITING_FOR_DEMO_RECEIPT,
            blockers=intake_result.get("blockers", []),
            proof_data_present=False,
            proof_data_sanitized=False,
            campaign_ready=False,
            proof_intake_summary=_redact_payload(intake_result),
            receipt_router_summary={},
            post_trade_journal_summary={},
            repeatability_summary={},
            live_micro_gate_summary={},
            next_best_packet=NEXT_BEST_PACKET,
            proof_data_destination_map=_destination_map(
                intake_status=intake_result["status"],
                router_status=None,
                journal_status=None,
                repeatability_status=None,
                live_status=None,
                receipt_present=False,
            ),
        )

    if intake_result["status"] not in {PROOF_DATA_READY_FOR_ROUTING}:
        return _build_result(
            campaign_status=BLOCKED_BY_PROOF_INTAKE,
            blockers=intake_result.get("blockers", []),
            proof_data_present=bool(intake_result.get("proof_data_present", False)),
            proof_data_sanitized=bool(intake_result.get("proof_data_sanitized", False)),
            campaign_ready=False,
            proof_intake_summary=_redact_payload(intake_result),
            receipt_router_summary={},
            post_trade_journal_summary={},
            repeatability_summary={},
            live_micro_gate_summary={},
            next_best_packet=_next_packet_from_status(intake_result["status"]),
            proof_data_destination_map=_destination_map(
                intake_status=intake_result["status"],
                router_status=None,
                journal_status=None,
                repeatability_status=None,
                live_status=None,
                receipt_present=False,
            ),
        )

    router_result = evaluate_forex_demo_receipt_proof_router_v1(
        {"receipt": _mapping(source.get("receipt"))}
    )
    if router_result["status"] == PROOF_DATA_WAITING_FOR_DEMO_RECEIPT:
        return _build_result(
            campaign_status=PROOF_DATA_WAITING_FOR_DEMO_RECEIPT,
            blockers=router_result.get("blockers", []),
            proof_data_present=bool(router_result.get("proof_data_present", False)),
            proof_data_sanitized=bool(router_result.get("proof_data_sanitized", False)),
            campaign_ready=False,
            proof_intake_summary=_redact_payload(intake_result),
            receipt_router_summary=_redact_payload(router_result),
            post_trade_journal_summary={},
            repeatability_summary={},
            live_micro_gate_summary={},
            next_best_packet=NEXT_BEST_PACKET,
            proof_data_destination_map=_destination_map(
                intake_status=intake_result["status"],
                router_status=router_result["status"],
                journal_status=None,
                repeatability_status=None,
                live_status=None,
                receipt_present=False,
            ),
        )

    if router_result["status"] != DEMO_RECEIPT_PROOF_ROUTED:
        return _build_result(
            campaign_status=BLOCKED_BY_RECEIPT_ROUTING,
            blockers=router_result.get("blockers", []),
            proof_data_present=bool(router_result.get("proof_data_present", False)),
            proof_data_sanitized=bool(router_result.get("proof_data_sanitized", False)),
            campaign_ready=False,
            proof_intake_summary=_redact_payload(intake_result),
            receipt_router_summary=_redact_payload(router_result),
            post_trade_journal_summary={},
            repeatability_summary={},
            live_micro_gate_summary={},
            next_best_packet=_next_packet_from_status(router_result["status"]),
            proof_data_destination_map=_destination_map(
                intake_status=intake_result["status"],
                router_status=router_result["status"],
                journal_status=None,
                repeatability_status=None,
                live_status=None,
                receipt_present=False,
            ),
        )

    journal_result = evaluate_forex_post_trade_proof_journal_v1(
        {
            "receipt_proof": _mapping(router_result.get("routed_proof_packet")),
            "post_trade_review": _mapping(source.get("post_trade_review")),
        }
    )
    if journal_result["status"] != POST_TRADE_PROOF_JOURNAL_READY:
        campaign_status = BLOCKED_BY_POST_TRADE_JOURNAL
        if journal_result["status"] in {BLOCKED_BY_PNL_RECORD}:
            campaign_status = BLOCKED_BY_POST_TRADE_JOURNAL
        elif journal_result["status"] == BLOCKED_BY_POST_TRADE_REVIEW:
            campaign_status = BLOCKED_BY_POST_TRADE_JOURNAL
        elif journal_result["status"] == BLOCKED_BY_RECEIPT_PROOF:
            campaign_status = BLOCKED_BY_POST_TRADE_JOURNAL
        elif journal_result["status"] == JOURNAL_INCOMPLETE_INPUTS:
            campaign_status = INCOMPLETE_INPUTS
        return _build_result(
            campaign_status=campaign_status,
            blockers=journal_result.get("blockers", []),
            proof_data_present=bool(journal_result.get("proof_data_present", False)),
            proof_data_sanitized=bool(journal_result.get("proof_data_sanitized", False)),
            campaign_ready=False,
            proof_intake_summary=_redact_payload(intake_result),
            receipt_router_summary=_redact_payload(router_result),
            post_trade_journal_summary=_redact_payload(journal_result),
            repeatability_summary={},
            live_micro_gate_summary={},
            next_best_packet=_next_packet_from_status(journal_result["status"]),
            proof_data_destination_map=_destination_map(
                intake_status=intake_result["status"],
                router_status=router_result["status"],
                journal_status=journal_result["status"],
                repeatability_status=None,
                live_status=None,
                receipt_present=True,
            ),
        )

    repeatability_result = evaluate_forex_profit_repeatability_evidence_v1(
        {"evidence": _mapping(source.get("evidence"))}
    )
    if repeatability_result["status"] != REPEATABILITY_EVIDENCE_READY_FOR_REVIEW:
        if repeatability_result["status"] == CONTINUE_DEMO_PROOF_CAPTURE:
            campaign_status = CONTINUE_DEMO_PROOF_CAPTURE
        elif repeatability_result["status"] == BLOCKED_BY_INSUFFICIENT_SAMPLE:
            campaign_status = CONTINUE_DEMO_PROOF_CAPTURE
        else:
            campaign_status = BLOCKED_BY_REPEATABILITY
        return _build_result(
            campaign_status=campaign_status,
            blockers=repeatability_result.get("blockers", []),
            proof_data_present=bool(repeatability_result.get("proof_data_present", False)),
            proof_data_sanitized=bool(repeatability_result.get("proof_data_sanitized", False)),
            campaign_ready=False,
            proof_intake_summary=_redact_payload(intake_result),
            receipt_router_summary=_redact_payload(router_result),
            post_trade_journal_summary=_redact_payload(journal_result),
            repeatability_summary=_redact_payload(repeatability_result),
            live_micro_gate_summary={},
            next_best_packet=NEXT_BEST_PACKET,
            proof_data_destination_map=_destination_map(
                intake_status=intake_result["status"],
                router_status=router_result["status"],
                journal_status=journal_result["status"],
                repeatability_status=repeatability_result["status"],
                live_status=None,
                receipt_present=True,
            ),
        )

    live_gate_result = evaluate_forex_proof_to_live_micro_gate_v1(
        {
            "demo_receipt_review": {
                "demo_receipt_ready": True,
                "post_trade_review_ready": bool(
                    _mapping(journal_result.get("journal_entry")).get(
                        "proof_ready_for_repeatability_scoring"
                    )
                ),
                "demo_order_count": int(_mapping(router_result.get("routed_proof_packet")).get(
                    "order_count", 1
                )),
            },
            "repeatability_evidence": {
                "repeatability_score": int(
                    repeatability_result.get("repeatability_score", 0)
                ),
                "expectancy_positive": bool(
                    repeatability_result.get("evidence_summary", {}).get("expectancy_positive")
                ),
                "drawdown_within_limit": bool(
                    repeatability_result.get("evidence_summary", {}).get("drawdown_within_limit")
                ),
                "profit_factor_meets_threshold": bool(
                    repeatability_result.get("evidence_summary", {}).get(
                        "profit_factor_meets_threshold"
                    )
                ),
            },
            "risk": _mapping(source.get("risk")),
            "owner": _mapping(source.get("owner")),
        }
    )

    if live_gate_result["status"] == READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW:
        return _build_result(
            campaign_status=READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW,
            blockers=tuple(),
            proof_data_present=True,
            proof_data_sanitized=True,
            campaign_ready=True,
            proof_intake_summary=_redact_payload(intake_result),
            receipt_router_summary=_redact_payload(router_result),
            post_trade_journal_summary=_redact_payload(journal_result),
            repeatability_summary=_redact_payload(repeatability_result),
            live_micro_gate_summary=_redact_payload(live_gate_result),
            next_best_packet=live_gate_result["live_micro_review_packet"].get(
                "next_best_packet",
                NEXT_BEST_PACKET,
            ),
            proof_data_destination_map=_destination_map(
                intake_status=intake_result["status"],
                router_status=router_result["status"],
                journal_status=journal_result["status"],
                repeatability_status=repeatability_result["status"],
                live_status=live_gate_result["status"],
                receipt_present=True,
            ),
        )

    if live_gate_result["status"] in {LIVE_CONTINUE_DEMO_PROOF_CAPTURE}:
        campaign_status = CONTINUE_DEMO_PROOF_CAPTURE
    elif live_gate_result["status"] in {
        LIVE_BLOCKED_BY_BANKING_FOCUS,
        LIVE_BLOCKED_BY_SENSITIVE_DATA,
    }:
        campaign_status = BLOCKED_BY_LIVE_MICRO_GATE
    else:
        campaign_status = BLOCKED_BY_LIVE_MICRO_GATE

    return _build_result(
        campaign_status=campaign_status,
        blockers=live_gate_result.get("blockers", []),
        proof_data_present=bool(live_gate_result.get("proof_data_present", False)),
        proof_data_sanitized=bool(live_gate_result.get("proof_data_sanitized", False)),
        campaign_ready=False,
        proof_intake_summary=_redact_payload(intake_result),
        receipt_router_summary=_redact_payload(router_result),
        post_trade_journal_summary=_redact_payload(journal_result),
        repeatability_summary=_redact_payload(repeatability_result),
        live_micro_gate_summary=_redact_payload(live_gate_result),
        next_best_packet=_next_packet_from_status(live_gate_result["status"]),
        proof_data_destination_map=_destination_map(
            intake_status=intake_result["status"],
            router_status=router_result["status"],
            journal_status=journal_result["status"],
            repeatability_status=repeatability_result["status"],
            live_status=live_gate_result["status"],
            receipt_present=True,
        ),
    )


def _destination_map(
    *,
    intake_status: str,
    router_status: str | None,
    journal_status: str | None,
    repeatability_status: str | None,
    live_status: str | None,
    receipt_present: bool,
) -> dict[str, Any]:
    return {
        "demo receipt -> receipt router": (
            "ROUTED" if intake_status == PROOF_DATA_READY_FOR_ROUTING else intake_status
        ),
        "receipt router -> post-trade journal": (
            "ROUTED" if router_status == DEMO_RECEIPT_PROOF_ROUTED else router_status
        ),
        "post-trade journal -> repeatability evidence": (
            "READY" if journal_status == POST_TRADE_PROOF_JOURNAL_READY else journal_status
        ),
        "repeatability evidence -> live micro gate": (
            "READY" if repeatability_status == REPEATABILITY_EVIDENCE_READY_FOR_REVIEW else repeatability_status
        ),
        "live micro gate -> owner live micro exception review packet": (
            "READY"
            if live_status == READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW
            else live_status
        ),
        "no proof": PROOF_DATA_WAITING_FOR_DEMO_RECEIPT if not receipt_present else None,
    }


def _build_result(
    *,
    campaign_status: str,
    blockers: Sequence[str],
    proof_data_present: bool,
    proof_data_sanitized: bool,
    campaign_ready: bool,
    proof_intake_summary: Mapping[str, Any],
    receipt_router_summary: Mapping[str, Any],
    post_trade_journal_summary: Mapping[str, Any],
    repeatability_summary: Mapping[str, Any],
    live_micro_gate_summary: Mapping[str, Any],
    proof_data_destination_map: Mapping[str, Any],
    next_best_packet: str,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "campaign_status": campaign_status,
        "campaign_ready": bool(campaign_ready),
        "ready": campaign_status == READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW,
        "owner_decision_required": True,
        "read_only": True,
        "metadata_only": True,
        "proof_data_present": bool(proof_data_present),
        "proof_data_sanitized": bool(proof_data_sanitized),
        "proof_intake_summary": dict(proof_intake_summary),
        "receipt_router_summary": dict(receipt_router_summary),
        "post_trade_journal_summary": dict(post_trade_journal_summary),
        "repeatability_summary": dict(repeatability_summary),
        "live_micro_gate_summary": dict(live_micro_gate_summary),
        "proof_data_destination_map": dict(proof_data_destination_map),
        "owner_action_queue": [
            {
                "action_id": campaign_status,
                "blocked_by": list(_unique(blockers)),
                "next_best_packet": _next_best_packet_for_status(campaign_status),
                "owner_decision_required": True,
            }
        ],
        "blockers": list(blockers),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(campaign_status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "campaign_status": campaign_status,
            "campaign_ready": bool(campaign_ready),
            "proof_data_present": bool(proof_data_present),
            "proof_data_sanitized": bool(proof_data_sanitized),
            "blockers": list(blockers),
            "next_best_packet": next_best_packet,
        },
        "safety": {
            "read_only": True,
            "metadata_only": True,
            "owner_decision_required": True,
            **{field: False for field in HARD_FALSE_FIELDS},
        },
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _next_packet_from_status(status: str) -> str:
    if status in {
        INTAKE_INCOMPLETE_INPUTS,
        INTAKE_BLOCKED_BY_SENSITIVE_DATA,
        INTAKE_BLOCKED_BY_BANKING_FOCUS,
        BLOCKED_BY_BANKING_FOCUS,
        BLOCKED_BY_SENSITIVE_DATA,
        PROOF_DATA_WAITING_FOR_DEMO_RECEIPT,
        BLOCKED_BY_UNSANITIZED_PROOF_DATA,
        BLOCKED_BY_FAKE_PROOF_CLAIM,
    }:
        return NEXT_BEST_PACKET
    if status in {
        ROUTER_INCOMPLETE_INPUTS,
        ROUTER_BLOCKED_BY_SENSITIVE_DATA,
        ROUTER_BLOCKED_BY_BANKING_FOCUS,
        ROUTER_BLOCKED_BY_ORDER_COUNT,
        BLOCKED_BY_RECEIPT_MISSING,
        BLOCKED_BY_RECEIPT_UNSANITIZED,
        BLOCKED_BY_OANDA_DEMO_BOUNDARY,
    }:
        return NEXT_BEST_PACKET
    if status in {JOURNAL_INCOMPLETE_INPUTS, JOURNAL_BLOCKED_BY_BANKING_FOCUS, JOURNAL_BLOCKED_BY_SENSITIVE_DATA, BLOCKED_BY_RECEIPT_PROOF, BLOCKED_BY_POST_TRADE_REVIEW, BLOCKED_BY_PNL_RECORD}:
        return NEXT_BEST_PACKET
    if status in {BLOCKED_BY_DRAWDOWN, BLOCKED_BY_NEGATIVE_EXPECTANCY, REPEATABILITY_BLOCKED_BY_SENSITIVE_DATA, REPEATABILITY_BLOCKED_BY_BANKING,}:
        return NEXT_BEST_PACKET
    if status in {LIVE_INCOMPLETE_INPUTS, LIVE_BLOCKED_BY_SENSITIVE_DATA, LIVE_BLOCKED_BY_BANKING_FOCUS}:
        return NEXT_BEST_PACKET
    return NEXT_BEST_PACKET


def _safe_manual_next_action(status: str) -> str:
    if status == PROOF_PIPELINE_READY_TO_CONTINUE:
        return "Review and continue to next packet."
    if status == PROOF_DATA_WAITING_FOR_DEMO_RECEIPT:
        return "Collect a sanitized OANDA demo receipt and rerun."
    if status == CONTINUE_DEMO_PROOF_CAPTURE:
        return "Continue capture and rerun proof pipeline."
    if status == READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW:
        return "Open owner live micro exception review packet."
    if status in {
        BLOCKED_BY_PROOF_INTAKE,
        BLOCKED_BY_RECEIPT_ROUTING,
        BLOCKED_BY_POST_TRADE_JOURNAL,
        BLOCKED_BY_REPEATABILITY,
        BLOCKED_BY_LIVE_MICRO_GATE,
        BLOCKED_BY_BANKING_FOCUS,
        BLOCKED_BY_SENSITIVE_DATA,
        INCOMPLETE_INPUTS,
    }:
        return "Resolve blockers and rerun this pipeline module."
    return "Address blockers and continue."


def _next_best_packet_for_status(status: str) -> str:
    if status == READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW:
        return NEXT_BEST_PACKET
    if status == CONTINUE_DEMO_PROOF_CAPTURE:
        return NEXT_BEST_PACKET
    return NEXT_BEST_PACKET


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            key_path = f"{path}.{raw_key}"
            if _sensitive_key_blocked(key_text):
                blockers.append(f"{key_path}:sensitive_key")
                continue
            blockers.extend(_sensitive_data_blockers(child, key_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    if isinstance(value, str) and _has_secret_value(value):
        blockers.append(f"{path}:secret_like_value")
    elif isinstance(value, int) and not isinstance(value, bool) and _has_long_digit_run(
        str(value)
    ):
        blockers.append(f"{path}:long_digit_run")
    return tuple(_unique(blockers))


def _banking_focus_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key).lower().replace("-", "_")
            key_path = f"{path}.{raw_key}"
            if key_text in BANKING_ALLOWED_FALSE_FIELDS and child is False:
                continue
            if any(part in key_text for part in BANKING_KEY_PARTS):
                blockers.append(f"{key_path}:banking_focus")
                continue
            blockers.extend(_banking_focus_blockers(child, key_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_banking_focus_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    return tuple(_unique(blockers))


def _sensitive_key_blocked(key_text: str) -> bool:
    normalized = str(key_text).lower().replace("-", "_")
    if normalized.endswith("_redacted"):
        return False
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def _has_secret_value(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS) or _has_long_digit_run(
        lowered
    )


def _has_long_digit_run(text: str, minimum: int = 8) -> bool:
    run = 0
    for char in text:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))


def _redact_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    return dict(payload)
