from __future__ import annotations

from typing import Any

from automation.forex_engine import broker_paper_dryrun_intent_ledger
from automation.forex_engine import schema_contracts as schemas


DRYRUN_RISK_GOVERNOR_READY = "DRYRUN_RISK_GOVERNOR_READY"
RISK_GOVERNOR_REPAIR_PACKET = "PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-REPAIR-V1"
DRYRUN_REPLAY_HARNESS_PACKET = "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1"
PACKET_ID = "PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1"
ALLOWED_RISK_GOVERNOR_CLASSIFICATIONS = {"FAIL", "WATCHLIST", DRYRUN_RISK_GOVERNOR_READY}
FORBIDDEN_RISK_GOVERNOR_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}


def build_broker_paper_dryrun_risk_policy() -> dict[str, Any]:
    policy = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_RISK_GOVERNOR_POLICY.v1",
        "packet_id": PACKET_ID,
        "mode": "PAPER_ONLY_DRYRUN_RISK_GOVERNOR",
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "manual_approval_required": True,
        "presecurity_gate_required": True,
        "stub_contract_required": True,
        "dryrun_ledger_required": True,
        "kill_switch_required": True,
        "kill_switch_armed": True,
        "max_loss_guard_required": True,
        "daily_stop_required": True,
        "audit_log_required": True,
        "max_loss_usd_per_intent": 2.00,
        "max_daily_loss_usd": 5.00,
        "max_intents_per_day": 3,
        "max_quantity_units": 1000,
        "approved_symbol_allowlist": [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "EURUSD_FAKE",
            "GBPUSD_FAKE",
            "USDJPY_FAKE",
        ],
        "rejected_symbol_blocklist": [
            "BTCUSD",
            "ETHUSD",
            "AAPL",
            "TSLA",
            "SPY",
            "UNKNOWN",
            "UNKNOWN_SYMBOL",
        ],
        "require_stop_loss_pips": True,
        "require_dry_run_true": True,
        "require_operator_approval_true": True,
        "require_stub_no_order_flags_true": True,
        "risk_decision_schema": {
            "accepted_by_risk_governor": "bool",
            "risk_decision": "ACCEPTED_DRYRUN_ONLY or REJECTED",
            "would_place_order": False,
            "order_placed": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "broker_paper_orders_allowed": False,
            "rejection_reasons": "list[str]",
            "audit_notes": "list[str]",
            "safety_flags": "dict[str, bool]",
        },
        "rejection_reasons": [
            "dry_run_required",
            "operator_approval_required",
            "max_loss_usd_required",
            "max_loss_usd_exceeds_per_intent_cap",
            "stop_loss_pips_required",
            "quantity_units_required",
            "quantity_units_exceeds_cap",
            "symbol_not_in_risk_allowlist",
            "symbol_blocklisted",
            "side_must_be_buy_or_sell",
            "order_type_must_be_stub_only",
            "would_place_order_must_be_false",
            "order_placed_must_be_false",
            "broker_request_sent_must_be_false",
            "network_used_must_be_false",
            "credentials_used_must_be_false",
            "live_ready_must_be_false",
            "broker_paper_orders_allowed_must_be_false",
            "kill_switch_must_remain_armed",
        ],
        "safety_invariants": _risk_safety_invariants(),
        "next_safe_action": (
            "If the dry-run risk governor is ready, proceed only to "
            "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1; broker SDKs, "
            "credentials, network/API, broker-paper orders, and live trading remain blocked."
        ),
    }
    schemas.assert_no_live_permissions(policy)
    return policy


def evaluate_dryrun_intent_risk(
    record: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = dict(policy or build_broker_paper_dryrun_risk_policy())
    active_record = _ensure_ledger_record(record)
    reasons = _intent_risk_rejection_reasons(active_record, active_policy)
    accepted = not reasons
    result = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_RISK_DECISION.v1",
        "packet_id": PACKET_ID,
        "mode": active_policy["mode"],
        "record_id": str(active_record.get("record_id") or "unknown"),
        "symbol": _symbol(active_record),
        "side": _side(active_record),
        "quantity_units": _int_or_none(active_record.get("quantity_units")),
        "order_type": _order_type(active_record),
        "max_loss_usd": _float_or_none(active_record.get("max_loss_usd")),
        "stop_loss_pips": _float_or_none(active_record.get("stop_loss_pips")),
        "dry_run": active_record.get("dry_run") is True,
        "approved_by_operator": active_record.get("approved_by_operator") is True,
        "accepted_for_simulation": active_record.get("accepted_for_simulation") is True,
        "accepted_by_risk_governor": accepted,
        "risk_decision": "ACCEPTED_DRYRUN_ONLY" if accepted else "REJECTED",
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "broker_paper_orders_allowed": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "rejection_reasons": reasons,
        "audit_notes": _decision_audit_notes(accepted),
        "safety_flags": _forced_safety_flags(active_policy),
        "classification": DRYRUN_RISK_GOVERNOR_READY if accepted else "WATCHLIST",
        "next_safe_action": _decision_next_safe_action(accepted),
    }
    schemas.assert_no_live_permissions(result)
    return result


def evaluate_dryrun_ledger_risk(
    ledger: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = dict(policy or build_broker_paper_dryrun_risk_policy())
    active_ledger = dict(ledger or _demo_risk_ledger())
    records = [dict(item) for item in list(active_ledger.get("records") or []) if isinstance(item, dict)]
    decisions = [evaluate_dryrun_intent_risk(record, active_policy) for record in records]
    records_count = len(records)
    risk_accepted = sum(1 for item in decisions if item.get("accepted_by_risk_governor") is True)
    risk_rejected = records_count - risk_accepted
    aggregate_max_loss = round(
        sum(float(item.get("max_loss_usd") or 0.0) for item in decisions if item.get("accepted_by_risk_governor") is True),
        4,
    )
    blockers = _ledger_risk_blockers(active_ledger, active_policy, records_count, risk_accepted, aggregate_max_loss)
    result = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_RISK_GOVERNOR_RESULT.v1",
        "packet_id": PACKET_ID,
        "mode": active_policy["mode"],
        "ledger_storage": str(active_ledger.get("ledger_storage") or "IN_MEMORY_ONLY"),
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "manual_approval_required": True,
        "presecurity_gate_required": True,
        "stub_contract_required": True,
        "dryrun_ledger_required": True,
        "kill_switch_required": True,
        "kill_switch_armed": active_policy.get("kill_switch_armed") is True,
        "max_loss_guard_required": True,
        "daily_stop_required": True,
        "audit_log_required": True,
        "records_count": records_count,
        "dryrun_risk_records": records_count,
        "risk_accepted": risk_accepted,
        "dryrun_risk_accepted": risk_accepted,
        "risk_rejected": risk_rejected,
        "dryrun_risk_rejected": risk_rejected,
        "aggregate_max_loss_usd": aggregate_max_loss,
        "max_daily_loss_usd": float(active_policy["max_daily_loss_usd"]),
        "max_loss_usd_per_intent": float(active_policy["max_loss_usd_per_intent"]),
        "max_intents_per_day": int(active_policy["max_intents_per_day"]),
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "risk_decisions": decisions,
        "rejection_reasons": _unique(
            [
                *blockers,
                *[
                    str(reason)
                    for decision in decisions
                    for reason in list(decision.get("rejection_reasons") or [])
                ],
            ]
        ),
        "blockers": blockers,
        "audit_summary": _ledger_audit_summary(records_count, risk_accepted, risk_rejected),
        "safety_flags": _forced_safety_flags(active_policy),
        "policy": active_policy,
    }
    result["classification"] = classify_dryrun_risk_governor(result)
    result["broker_paper_dryrun_risk_governor_classification"] = result["classification"]
    result["broker_paper_dryrun_risk_governor_ready"] = (
        result["classification"] == DRYRUN_RISK_GOVERNOR_READY
    )
    result["next_safe_packet"] = (
        DRYRUN_REPLAY_HARNESS_PACKET
        if result["classification"] == DRYRUN_RISK_GOVERNOR_READY
        else RISK_GOVERNOR_REPAIR_PACKET
    )
    result["next_safe_action"] = _summary_next_safe_action(result["classification"])
    schemas.assert_no_live_permissions(result)
    return result


def summarize_dryrun_risk_governor(result: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(result or {})
    if not payload:
        payload = evaluate_dryrun_ledger_risk()
    records_count = int(payload.get("records_count", payload.get("dryrun_risk_records", 0)))
    accepted = int(payload.get("risk_accepted", payload.get("dryrun_risk_accepted", 0)))
    rejected = int(payload.get("risk_rejected", payload.get("dryrun_risk_rejected", 0)))
    summary = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_RISK_GOVERNOR_SUMMARY.v1",
        "packet_id": PACKET_ID,
        "mode": str(payload.get("mode") or "PAPER_ONLY_DRYRUN_RISK_GOVERNOR"),
        "classification": str(payload.get("classification") or "WATCHLIST"),
        "broker_paper_dryrun_risk_governor_classification": str(
            payload.get("broker_paper_dryrun_risk_governor_classification")
            or payload.get("classification")
            or "WATCHLIST"
        ),
        "broker_paper_dryrun_risk_governor_ready": bool(
            payload.get("broker_paper_dryrun_risk_governor_ready", False)
        ),
        "records_count": records_count,
        "dryrun_risk_records": records_count,
        "risk_accepted": accepted,
        "dryrun_risk_accepted": accepted,
        "risk_rejected": rejected,
        "dryrun_risk_rejected": rejected,
        "aggregate_max_loss_usd": float(payload.get("aggregate_max_loss_usd", 0.0)),
        "max_daily_loss_usd": float(payload.get("max_daily_loss_usd", 5.0)),
        "kill_switch_armed": payload.get("kill_switch_armed") is True,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "blockers": list(payload.get("blockers") or []),
        "rejection_reasons": list(payload.get("rejection_reasons") or []),
        "next_safe_packet": str(payload.get("next_safe_packet") or RISK_GOVERNOR_REPAIR_PACKET),
        "next_safe_action": str(
            payload.get("next_safe_action")
            or _summary_next_safe_action(str(payload.get("classification") or "WATCHLIST"))
        ),
    }
    summary["classification"] = classify_dryrun_risk_governor(summary)
    summary["broker_paper_dryrun_risk_governor_classification"] = summary["classification"]
    summary["broker_paper_dryrun_risk_governor_ready"] = (
        summary["classification"] == DRYRUN_RISK_GOVERNOR_READY
    )
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_dryrun_risk_governor(summary: dict[str, Any] | None = None) -> str:
    payload = dict(summary or {})
    candidate = str(
        payload.get("classification")
        or payload.get("broker_paper_dryrun_risk_governor_classification")
        or "WATCHLIST"
    )
    if candidate in FORBIDDEN_RISK_GOVERNOR_CLASSIFICATIONS:
        return "FAIL"
    if candidate not in ALLOWED_RISK_GOVERNOR_CLASSIFICATIONS:
        return "FAIL"
    if _has_forbidden_effect(payload):
        return "FAIL"
    if list(payload.get("blockers") or []):
        return "WATCHLIST"
    if payload.get("accepted_by_risk_governor") is True:
        return DRYRUN_RISK_GOVERNOR_READY
    if int(payload.get("risk_accepted", payload.get("dryrun_risk_accepted", 0)) or 0) > 0:
        return DRYRUN_RISK_GOVERNOR_READY
    return "WATCHLIST"


def broker_paper_dryrun_risk_governor_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_RISK_GOVERNOR_BOUNDARY.v1",
        "mode": "PAPER_ONLY_DRYRUN_RISK_GOVERNOR",
        "risk_governor_only": True,
        "ledger_storage": "IN_MEMORY_ONLY",
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "manual_approval_required": True,
        "presecurity_gate_required": True,
        "stub_contract_required": True,
        "dryrun_ledger_required": True,
        "kill_switch_required": True,
        "kill_switch_armed": True,
        "max_loss_guard_required": True,
        "daily_stop_required": True,
        "audit_log_required": True,
        "next_safe_packet_after_dryrun_risk_governor": DRYRUN_REPLAY_HARNESS_PACKET,
    }


def _ensure_ledger_record(record: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(record or _demo_risk_intent(1.0))
    ledger_record_fields = {
        "record_id",
        "accepted_for_simulation",
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
    }
    if any(field in payload for field in ledger_record_fields):
        return payload
    return broker_paper_dryrun_intent_ledger.create_dryrun_intent_record(payload)


def _demo_risk_ledger() -> dict[str, Any]:
    return broker_paper_dryrun_intent_ledger.replay_dryrun_intent_batch(
        [
            _demo_risk_intent(1.0),
            {
                **_demo_risk_intent(3.5),
                "symbol": "BTCUSD",
                "stop_loss_pips": None,
            },
        ]
    )


def _demo_risk_intent(max_loss_usd: float) -> dict[str, Any]:
    return {
        "symbol": "EURUSD_FAKE",
        "side": "buy",
        "quantity_units": 500,
        "order_type": "market_stub",
        "stop_loss_pips": 8.0,
        "take_profit_pips": 12.0,
        "max_loss_usd": max_loss_usd,
        "dry_run": True,
        "approved_by_operator": True,
    }


def _intent_risk_rejection_reasons(record: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    symbol = _symbol(record)
    side = _side(record)
    order_type = _order_type(record)
    quantity = _int_or_none(record.get("quantity_units"))
    max_loss = _float_or_none(record.get("max_loss_usd"))
    stop_loss = _float_or_none(record.get("stop_loss_pips"))
    if record.get("dry_run") is not True:
        reasons.append("dry_run_required")
    if record.get("approved_by_operator") is not True:
        reasons.append("operator_approval_required")
    if record.get("accepted_for_simulation") is not True:
        reasons.append("ledger_record_must_be_accepted_for_simulation")
    if max_loss is None or max_loss <= 0:
        reasons.append("max_loss_usd_required")
    elif max_loss > float(policy["max_loss_usd_per_intent"]):
        reasons.append("max_loss_usd_exceeds_per_intent_cap")
    if stop_loss is None or stop_loss <= 0:
        reasons.append("stop_loss_pips_required")
    if quantity is None or quantity <= 0:
        reasons.append("quantity_units_required")
    elif quantity > int(policy["max_quantity_units"]):
        reasons.append("quantity_units_exceeds_cap")
    if symbol in set(str(item).upper() for item in policy["rejected_symbol_blocklist"]):
        reasons.append("symbol_blocklisted")
    if symbol not in set(str(item).upper() for item in policy["approved_symbol_allowlist"]):
        reasons.append("symbol_not_in_risk_allowlist")
    if side not in {"buy", "sell"}:
        reasons.append("side_must_be_buy_or_sell")
    if order_type not in {"market_stub", "limit_stub"}:
        reasons.append("order_type_must_be_stub_only")
    for field in (
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
        "broker_paper_orders_allowed",
    ):
        if record.get(field) is True:
            reasons.append(f"{field}_must_be_false")
    if policy.get("kill_switch_armed") is not True:
        reasons.append("kill_switch_must_remain_armed")
    for field in _blocked_capability_fields():
        if record.get(field) is True:
            reasons.append(f"{field}_must_be_false")
    if str(record.get("classification") or "") in FORBIDDEN_RISK_GOVERNOR_CLASSIFICATIONS:
        reasons.append("forbidden_record_classification")
    return _unique(reasons)


def _ledger_risk_blockers(
    ledger: dict[str, Any],
    policy: dict[str, Any],
    records_count: int,
    risk_accepted: int,
    aggregate_max_loss_usd: float,
) -> list[str]:
    blockers: list[str] = []
    if str(ledger.get("ledger_storage") or "IN_MEMORY_ONLY") != "IN_MEMORY_ONLY":
        blockers.append("ledger_storage_must_be_in_memory_only")
    if records_count <= 0:
        blockers.append("no_dryrun_ledger_records")
    if records_count > int(policy["max_intents_per_day"]):
        blockers.append("max_intents_per_day_exceeded")
    if aggregate_max_loss_usd > float(policy["max_daily_loss_usd"]):
        blockers.append("aggregate_max_loss_exceeds_daily_cap")
    if risk_accepted <= 0:
        blockers.append("no_risk_accepted_dryrun_records")
    if policy.get("kill_switch_armed") is not True:
        blockers.append("kill_switch_must_remain_armed")
    return _unique(blockers)


def _risk_safety_invariants() -> dict[str, Any]:
    return {
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "kill_switch_armed": True,
    }


def _forced_safety_flags(policy: dict[str, Any]) -> dict[str, Any]:
    flags = dict(_risk_safety_invariants())
    flags["manual_approval_required"] = True
    flags["max_loss_usd_per_intent"] = float(policy["max_loss_usd_per_intent"])
    flags["max_daily_loss_usd"] = float(policy["max_daily_loss_usd"])
    flags["max_intents_per_day"] = int(policy["max_intents_per_day"])
    flags["max_quantity_units"] = int(policy["max_quantity_units"])
    return flags


def _blocked_capability_fields() -> tuple[str, ...]:
    return (
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "env_secret_read_allowed",
        "webhook_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
        "file_writes_allowed",
        "reports_writes_allowed",
    )


def _has_forbidden_effect(payload: dict[str, Any]) -> bool:
    true_forbidden_fields = (
        *_blocked_capability_fields(),
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
        "live_trade_ready",
        "execution_allowed",
        "orders_allowed",
    )
    return any(payload.get(field) is True for field in true_forbidden_fields)


def _ledger_audit_summary(records_count: int, risk_accepted: int, risk_rejected: int) -> dict[str, Any]:
    return {
        "records_evaluated": records_count,
        "risk_accepted": risk_accepted,
        "risk_rejected": risk_rejected,
        "unsafe_intents_are_rejected_not_executed": True,
        "orders_placed": 0,
        "network_requests_sent": 0,
        "credentials_used": False,
    }


def _decision_audit_notes(accepted: bool) -> list[str]:
    if accepted:
        return [
            "accepted for dry-run risk accounting only",
            "order placement remains blocked",
            "broker/network/credential use remains blocked",
        ]
    return [
        "rejected by dry-run risk governor",
        "unsafe intent was not placed or transmitted",
    ]


def _decision_next_safe_action(accepted: bool) -> str:
    if accepted:
        return "Record risk decision locally in memory only; no broker-paper order is allowed."
    return "Reject the fake dry-run intent and preserve the audit reason before any future replay harness."


def _summary_next_safe_action(classification: str) -> str:
    if classification == DRYRUN_RISK_GOVERNOR_READY:
        return (
            "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1; "
            "broker-paper orders, broker SDKs, credentials, and network/API remain blocked."
        )
    return "Repair PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1 before any replay-harness work."


def _symbol(record: dict[str, Any]) -> str:
    return str(record.get("symbol") or "").strip().upper()


def _side(record: dict[str, Any]) -> str:
    return str(record.get("side") or "").strip().lower()


def _order_type(record: dict[str, Any]) -> str:
    return str(record.get("order_type") or "").strip().lower()


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
