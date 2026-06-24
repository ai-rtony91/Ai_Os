from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-RUNTIME-ONLY-ORDER-TICKET-V1"
TICKET_VERSION = "v1"

ORDER_TICKET_BLOCKED_MISSING_TRADE_PLAN = "ORDER_TICKET_BLOCKED_MISSING_TRADE_PLAN"
ORDER_TICKET_BLOCKED_PROFITABILITY_BRIDGE = "ORDER_TICKET_BLOCKED_PROFITABILITY_BRIDGE"
ORDER_TICKET_BLOCKED_OWNER_EVIDENCE = "ORDER_TICKET_BLOCKED_OWNER_EVIDENCE"
ORDER_TICKET_BLOCKED_COMPOUNDING_BUCKET = "ORDER_TICKET_BLOCKED_COMPOUNDING_BUCKET"
ORDER_TICKET_BLOCKED_RUNTIME_CONTEXT = "ORDER_TICKET_BLOCKED_RUNTIME_CONTEXT"
ORDER_TICKET_BLOCKED_RISK = "ORDER_TICKET_BLOCKED_RISK"
ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW = "ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW"
ORDER_TICKET_REJECTED = "ORDER_TICKET_REJECTED"

PROFITABILITY_READY_STATUS = "MICRO_TRADE_READY_FOR_OWNER_REVIEW"
OWNER_EVIDENCE_READY_STATUSES = {
    "EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW",
    "EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT",
}
COMPOUNDING_READY_STATUSES = {
    "BUCKET_ACTIVE_ACCUMULATING",
    "BUCKET_TARGET_REACHED_COLLECT_PROFIT",
    "BUCKET_READY_FOR_REDISTRIBUTION_REVIEW",
}

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)

TRADE_PLAN_REQUIRED_FIELDS = (
    "candidate_id",
    "strategy_id",
    "instrument",
    "direction",
    "order_type",
    "time_in_force",
    "planned_entry",
    "stop_loss",
    "take_profit",
    "position_size_units",
    "risk_amount",
    "expected_reward_amount",
    "reward_risk_ratio",
    "max_spread_allowed",
    "hold_allowed_overnight",
    "overnight_risk_note",
)

NUMERIC_TRADE_FIELDS = (
    "planned_entry",
    "stop_loss",
    "take_profit",
    "position_size_units",
    "risk_amount",
    "expected_reward_amount",
    "reward_risk_ratio",
    "max_spread_allowed",
)


def evaluate_oanda_demo_runtime_only_order_ticket_v1(
    trade_plan: dict | None = None,
    profitability_bridge_result: dict | None = None,
    owner_approval_evidence_result: dict | None = None,
    compounding_bucket_result: dict | None = None,
    runtime_context: dict | None = None,
) -> dict:
    plan = _mapping(trade_plan)
    if not plan:
        return _result(
            status=ORDER_TICKET_BLOCKED_MISSING_TRADE_PLAN,
            blockers=["missing_trade_plan"],
            warnings=_warnings(ORDER_TICKET_BLOCKED_MISSING_TRADE_PLAN),
            plan=plan,
            bridge=_mapping(profitability_bridge_result),
            owner_evidence=_mapping(owner_approval_evidence_result),
            compounding=_mapping(compounding_bucket_result),
            runtime=_mapping(runtime_context),
        )

    bridge = _mapping(profitability_bridge_result)
    owner_evidence = _mapping(owner_approval_evidence_result)
    compounding = _mapping(compounding_bucket_result)
    runtime = _mapping(runtime_context)

    plan_blockers = _trade_plan_blockers(plan)
    bridge_blockers = _profitability_bridge_blockers(bridge)
    owner_evidence_blockers = _owner_evidence_blockers(owner_evidence)
    compounding_blockers = _compounding_blockers(compounding, _text(plan.get("instrument")))
    runtime_blockers = _runtime_context_blockers(runtime)
    overnight_blockers = _overnight_blockers(plan, runtime)

    blockers = _unique(
        plan_blockers
        + bridge_blockers
        + owner_evidence_blockers
        + compounding_blockers
        + runtime_blockers
        + overnight_blockers
    )
    status = _status(
        plan_blockers=plan_blockers,
        bridge_blockers=bridge_blockers,
        owner_evidence_blockers=owner_evidence_blockers,
        compounding_blockers=compounding_blockers,
        runtime_blockers=runtime_blockers,
        overnight_blockers=overnight_blockers,
        all_blockers=blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        plan=plan,
        bridge=bridge,
        owner_evidence=owner_evidence,
        compounding=compounding,
        runtime=runtime,
    )


def _status(
    *,
    plan_blockers: list[str],
    bridge_blockers: list[str],
    owner_evidence_blockers: list[str],
    compounding_blockers: list[str],
    runtime_blockers: list[str],
    overnight_blockers: list[str],
    all_blockers: list[str],
) -> str:
    if any(blocker.startswith("unsafe_") for blocker in all_blockers):
        return ORDER_TICKET_REJECTED
    if plan_blockers:
        return ORDER_TICKET_BLOCKED_RISK
    if bridge_blockers:
        return ORDER_TICKET_BLOCKED_PROFITABILITY_BRIDGE
    if owner_evidence_blockers:
        return ORDER_TICKET_BLOCKED_OWNER_EVIDENCE
    if compounding_blockers:
        return ORDER_TICKET_BLOCKED_COMPOUNDING_BUCKET
    if runtime_blockers:
        return ORDER_TICKET_BLOCKED_RUNTIME_CONTEXT
    if overnight_blockers:
        return ORDER_TICKET_BLOCKED_RISK
    return ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW


def _trade_plan_blockers(plan: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in TRADE_PLAN_REQUIRED_FIELDS:
        if not _present(plan.get(field)):
            blockers.append(f"missing_trade_plan_{field}")

    for field in NUMERIC_TRADE_FIELDS:
        if _present(plan.get(field)) and _number(plan.get(field)) is None:
            blockers.append(f"trade_plan_{field}_must_be_numeric")

    direction = _text(plan.get("direction")).upper()
    order_type = _text(plan.get("order_type")).upper()
    if direction and direction not in {"BUY", "SELL"}:
        blockers.append("direction_must_be_buy_or_sell")
    if order_type and order_type not in {"MARKET", "LIMIT", "STOP"}:
        blockers.append("order_type_must_be_market_limit_or_stop")

    planned_entry = _number(plan.get("planned_entry"))
    stop_loss = _number(plan.get("stop_loss"))
    take_profit = _number(plan.get("take_profit"))
    if direction == "BUY" and None not in (planned_entry, stop_loss, take_profit):
        if not stop_loss < planned_entry < take_profit:
            blockers.append("buy_geometry_requires_stop_loss_below_entry_below_take_profit")
    if direction == "SELL" and None not in (planned_entry, stop_loss, take_profit):
        if not take_profit < planned_entry < stop_loss:
            blockers.append("sell_geometry_requires_take_profit_below_entry_below_stop_loss")

    risk_amount = _number(plan.get("risk_amount"))
    if risk_amount is not None and risk_amount <= 0:
        blockers.append("risk_amount_must_be_positive")
    position_size_units = _number(plan.get("position_size_units"))
    if position_size_units is not None and position_size_units <= 0:
        blockers.append("position_size_units_must_be_positive")
    expected_reward_amount = _number(plan.get("expected_reward_amount"))
    if expected_reward_amount is not None and expected_reward_amount <= 0:
        blockers.append("expected_reward_amount_must_be_positive")

    min_reward_risk = _number(plan.get("min_reward_risk_ratio"))
    if min_reward_risk is None:
        min_reward_risk = 1.5
    reward_risk_ratio = _number(plan.get("reward_risk_ratio"))
    if reward_risk_ratio is not None and reward_risk_ratio < min_reward_risk:
        blockers.append("reward_risk_ratio_below_minimum")

    return blockers


def _profitability_bridge_blockers(bridge: Mapping[str, Any]) -> list[str]:
    if not bridge:
        return ["missing_profitability_bridge_result"]

    blockers: list[str] = []
    if bridge.get("status") != PROFITABILITY_READY_STATUS:
        blockers.append("profitability_bridge_status_not_ready")
    blockers.extend(_execution_authority_blockers(bridge, "profitability_bridge"))
    return blockers


def _owner_evidence_blockers(owner_evidence: Mapping[str, Any]) -> list[str]:
    if not owner_evidence:
        return ["missing_owner_approval_evidence_result"]

    blockers: list[str] = []
    if owner_evidence.get("status") not in OWNER_EVIDENCE_READY_STATUSES:
        blockers.append("owner_evidence_status_not_ready_for_runtime_review")
    blockers.extend(_execution_authority_blockers(owner_evidence, "owner_evidence"))

    owner_summary = _mapping(owner_evidence.get("owner_decision_summary"))
    if not _bool(owner_summary.get("owner_approved_runtime_only_demo_review")):
        blockers.append("owner_runtime_only_demo_review_approval_required")
    if _bool(owner_summary.get("owner_approved_live_trading")):
        blockers.append("owner_approved_live_trading_must_remain_false")
    if _bool(owner_summary.get("owner_approved_autonomous_execution")):
        blockers.append("owner_approved_autonomous_execution_must_remain_false")
    return blockers


def _compounding_blockers(compounding: Mapping[str, Any], instrument: str) -> list[str]:
    if not compounding:
        return ["missing_compounding_bucket_result"]

    blockers: list[str] = []
    if compounding.get("status") not in COMPOUNDING_READY_STATUSES:
        blockers.append("compounding_bucket_status_not_ready")
    blockers.extend(_execution_authority_blockers(compounding, "compounding_bucket"))

    cycle_summary = _mapping(compounding.get("cycle_summary"))
    if _bool(cycle_summary.get("force_trades_to_hit_quota")):
        blockers.append("compounding_force_trades_to_hit_quota_must_be_false")

    risk_summary = _mapping(compounding.get("risk_summary"))
    for field in ("risk_gate_passed", "kill_switch_ready", "daily_stop_ready", "max_loss_gate_ready", "margin_safe"):
        if field in risk_summary and not _bool(risk_summary.get(field)):
            blockers.append(f"compounding_{field}_required")

    supported_instruments = _supported_instruments(compounding)
    if supported_instruments and instrument not in supported_instruments:
        blockers.append("instrument_not_supported_by_compounding_plan")
    elif not supported_instruments and compounding.get("status") != "BUCKET_ACTIVE_ACCUMULATING":
        blockers.append("compounding_allocation_or_active_cycle_required")

    return blockers


def _runtime_context_blockers(runtime: Mapping[str, Any]) -> list[str]:
    if not runtime:
        return ["missing_runtime_context"]

    required_true = (
        "demo_environment",
        "runtime_only_credentials_required",
        "owner_runtime_review_required",
    )
    required_false = (
        "live_environment",
        "credential_persistence_allowed",
        "account_id_persistence_allowed",
        "broker_network_call_performed",
        "order_placement_performed",
    )

    blockers: list[str] = []
    if runtime.get("broker") != "OANDA_DEMO":
        blockers.append("runtime_broker_must_be_oanda_demo")
    for field in required_true:
        if not _bool(runtime.get(field)):
            blockers.append(f"runtime_{field}_required")
    for field in required_false:
        if _bool(runtime.get(field)):
            blockers.append(f"runtime_{field}_must_be_false")
    return blockers


def _overnight_blockers(plan: Mapping[str, Any], runtime: Mapping[str, Any]) -> list[str]:
    if not _bool(plan.get("hold_allowed_overnight")):
        return []

    blockers: list[str] = []
    for field in ("stop_loss", "take_profit", "overnight_risk_note"):
        if not _present(plan.get(field)):
            blockers.append(f"overnight_{field}_required")

    for field in ("daily_stop_ready", "max_loss_gate_ready", "kill_switch_ready"):
        if not _bool(runtime.get(field)):
            blockers.append(f"overnight_{field}_required")

    max_overnight_risk_amount = _number(runtime.get("max_overnight_risk_amount"))
    risk_amount = _number(plan.get("risk_amount"))
    if max_overnight_risk_amount is None:
        blockers.append("overnight_max_overnight_risk_amount_required")
    elif risk_amount is not None and risk_amount > max_overnight_risk_amount:
        blockers.append("overnight_risk_amount_exceeds_max_overnight_risk_amount")

    return blockers


def _execution_authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    authority = _mapping(payload.get("execution_authority"))
    blockers: list[str] = []
    for field in EXECUTION_AUTHORITY_FIELDS:
        if _bool(authority.get(field)):
            blockers.append(f"unsafe_{label}_{field}_true")
        if _bool(payload.get(field)):
            blockers.append(f"unsafe_{label}_{field}_true")
    return blockers


def _supported_instruments(compounding: Mapping[str, Any]) -> set[str]:
    instruments: set[str] = set()
    for section_name in ("allocation_plan", "redistribution_plan"):
        section = _mapping(compounding.get(section_name))
        for key in ("selected_pairs", "candidate_pairs_for_next_cycle", "active_pairs", "eligible_pairs"):
            pairs = section.get(key)
            if isinstance(pairs, list):
                for pair in pairs:
                    pair_mapping = _mapping(pair)
                    instrument = _text(pair_mapping.get("instrument"))
                    if instrument:
                        instruments.add(instrument)
    return instruments


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    plan: Mapping[str, Any],
    bridge: Mapping[str, Any],
    owner_evidence: Mapping[str, Any],
    compounding: Mapping[str, Any],
    runtime: Mapping[str, Any],
) -> dict:
    return {
        "packet_id": PACKET_ID,
        "ticket_version": TICKET_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "order_ticket": _order_ticket(status, plan),
        "runtime_requirements": _runtime_requirements(runtime),
        "overnight_requirements": _overnight_requirements(plan, runtime),
        "risk_summary": _risk_summary(plan, runtime),
        "compounding_summary": _compounding_summary(compounding),
        "evidence_summary": _evidence_summary(bridge, owner_evidence),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _order_ticket(status: str, plan: Mapping[str, Any]) -> dict[str, Any]:
    if status != ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW:
        return {
            "status": "NOT_READY",
            "broker": "OANDA_DEMO",
            "environment": "DEMO",
            "review_only": True,
            "executable": False,
        }

    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "instrument": _text(plan.get("instrument")),
        "direction": _text(plan.get("direction")).upper(),
        "order_type": _text(plan.get("order_type")).upper(),
        "time_in_force": _text(plan.get("time_in_force")),
        "planned_entry": _number(plan.get("planned_entry")),
        "stop_loss": _number(plan.get("stop_loss")),
        "take_profit": _number(plan.get("take_profit")),
        "position_size_units": _number(plan.get("position_size_units")),
        "risk_amount": _number(plan.get("risk_amount")),
        "reward_risk_ratio": _number(plan.get("reward_risk_ratio")),
        "hold_allowed_overnight": _bool(plan.get("hold_allowed_overnight")),
        "pre_trade_evidence_required": True,
        "post_trade_evidence_required": True,
        "owner_final_click_required": True,
        "runtime_only_credentials_required": True,
        "live_trading_allowed": False,
        "autonomous_order_allowed": False,
        "status": "REVIEW_ONLY_NOT_EXECUTABLE",
    }


def _runtime_requirements(runtime: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(runtime.get("broker"), "MISSING"),
        "demo_environment_required": True,
        "live_environment_allowed": False,
        "runtime_only_credentials_required": True,
        "credential_persistence_allowed": False,
        "account_id_persistence_allowed": False,
        "broker_network_call_performed": _bool(runtime.get("broker_network_call_performed")),
        "order_placement_performed": _bool(runtime.get("order_placement_performed")),
        "owner_runtime_review_required": True,
    }


def _overnight_requirements(plan: Mapping[str, Any], runtime: Mapping[str, Any]) -> dict[str, Any]:
    overnight = _bool(plan.get("hold_allowed_overnight"))
    return {
        "hold_allowed_overnight": overnight,
        "stop_loss_required": overnight,
        "take_profit_required": overnight,
        "daily_stop_ready": _bool(runtime.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(runtime.get("max_loss_gate_ready")),
        "kill_switch_ready": _bool(runtime.get("kill_switch_ready")),
        "max_overnight_risk_amount": _number(runtime.get("max_overnight_risk_amount")),
        "overnight_risk_note_present": _present(plan.get("overnight_risk_note")),
    }


def _risk_summary(plan: Mapping[str, Any], runtime: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "direction": _text(plan.get("direction")).upper(),
        "order_type": _text(plan.get("order_type")).upper(),
        "risk_amount": _number(plan.get("risk_amount")),
        "position_size_units": _number(plan.get("position_size_units")),
        "reward_risk_ratio": _number(plan.get("reward_risk_ratio")),
        "min_reward_risk_ratio": _number(plan.get("min_reward_risk_ratio")) or 1.5,
        "max_spread_allowed": _number(plan.get("max_spread_allowed")),
        "hard_stop_loss_required": True,
        "hard_take_profit_required": True,
        "daily_stop_ready": _bool(runtime.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(runtime.get("max_loss_gate_ready")),
        "kill_switch_ready": _bool(runtime.get("kill_switch_ready")),
    }


def _compounding_summary(compounding: Mapping[str, Any]) -> dict[str, Any]:
    cycle_summary = _mapping(compounding.get("cycle_summary"))
    return {
        "status": _text(compounding.get("status"), "MISSING"),
        "force_trades_to_hit_quota": _bool(cycle_summary.get("force_trades_to_hit_quota")),
        "supported_instruments": sorted(_supported_instruments(compounding)),
        "execution_authority": _execution_authority(),
    }


def _evidence_summary(bridge: Mapping[str, Any], owner_evidence: Mapping[str, Any]) -> dict[str, Any]:
    owner_summary = _mapping(owner_evidence.get("owner_decision_summary"))
    return {
        "profitability_bridge_status": _text(bridge.get("status"), "MISSING"),
        "owner_evidence_status": _text(owner_evidence.get("status"), "MISSING"),
        "owner_approved_runtime_only_demo_review": _bool(
            owner_summary.get("owner_approved_runtime_only_demo_review")
        ),
        "owner_approved_live_trading": _bool(owner_summary.get("owner_approved_live_trading")),
        "owner_approved_autonomous_execution": _bool(
            owner_summary.get("owner_approved_autonomous_execution")
        ),
        "pre_trade_evidence_required": True,
        "post_trade_evidence_required": True,
    }


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "review_only_not_executable",
        "execution_authority_false",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read",
        "owner_final_click_still_required",
    ]
    if status == ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW:
        warnings.append("runtime_process_must_remain_demo_only_and_owner_reviewed")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        ORDER_TICKET_BLOCKED_MISSING_TRADE_PLAN: "provide_sanitized_trade_plan_for_review",
        ORDER_TICKET_BLOCKED_PROFITABILITY_BRIDGE: "repair_profitability_bridge_readiness_before_ticket_review",
        ORDER_TICKET_BLOCKED_OWNER_EVIDENCE: "complete_owner_approval_and_evidence_capture_before_ticket_review",
        ORDER_TICKET_BLOCKED_COMPOUNDING_BUCKET: "confirm_compounding_bucket_supports_this_instrument_without_forced_quota_chasing",
        ORDER_TICKET_BLOCKED_RUNTIME_CONTEXT: "provide_sanitized_demo_runtime_context_without_credentials_or_account_ids",
        ORDER_TICKET_BLOCKED_RISK: "repair_stop_take_profit_reward_risk_or_overnight_controls",
        ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW: "review_non_executable_demo_order_ticket_before_separate_owner_final_click_lane",
        ORDER_TICKET_REJECTED: "remove_unsafe_execution_authority_request_before_review",
    }.get(status, "stop_and_review_runtime_order_ticket_state")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
