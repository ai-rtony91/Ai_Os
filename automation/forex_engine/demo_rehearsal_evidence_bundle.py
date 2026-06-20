"""Deterministic paper/demo-review rehearsal evidence bundle builder."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from automation.forex_engine.balance_compounding import calculate_risk_base
from automation.forex_engine.evidence_ledger import append_ledger_event, build_ledger_event, replay_ledger
from automation.forex_engine.market_data_normalizer import normalize_market_snapshot
from automation.forex_engine.multi_trade_queue import build_multi_trade_queue
from automation.forex_engine.order_preview import build_order_preview
from automation.forex_engine.paper_fill_simulator import simulate_paper_fill
from automation.forex_engine.strategy_candidates import generate_strategy_candidates
from automation.forex_engine.trade_lifecycle_manager import process_trade_update

BUNDLE_VERSION = "AIOS_FOREX_DEMO_REHEARSAL_RUNNER_V1"
DEMO_REHEARSAL_MODE = "PAPER_DEMO_REVIEW_ONLY"
DEFAULT_TIMESTAMP = 1_700_000_200.0


def _fixture_market_snapshot(timestamp: float) -> dict[str, Any]:
    return {
        "pair": "EURUSD",
        "source_mode": "paper",
        "bid": 1.1024,
        "ask": 1.1026,
        "timestamp": timestamp,
        "candles": [
            {"open": 1.0960, "high": 1.0980, "low": 1.0950, "close": 1.0965, "volume": 100.0, "timestamp": timestamp - 50},
            {"open": 1.0965, "high": 1.1000, "low": 1.0960, "close": 1.0985, "volume": 110.0, "timestamp": timestamp - 40},
            {"open": 1.0985, "high": 1.1020, "low": 1.0980, "close": 1.1005, "volume": 120.0, "timestamp": timestamp - 30},
            {"open": 1.1005, "high": 1.1040, "low": 1.1000, "close": 1.1025, "volume": 130.0, "timestamp": timestamp - 20},
            {"open": 1.1025, "high": 1.1060, "low": 1.1020, "close": 1.1045, "volume": 140.0, "timestamp": timestamp - 10},
        ],
        "paper_only": True,
    }


def _fixture_account_state() -> dict[str, Any]:
    return {
        "starting_balance": 10000.0,
        "current_balance": 10000.0,
        "cash_balance": 10000.0,
        "equity": 10000.0,
        "realized_pnl": 0.0,
        "daily_loss_used": 0.0,
        "trade_count": 0,
        "session_count": 1,
        "peak_balance": 10000.0,
        "drawdown_percent": 0.0,
        "compounding_enabled": True,
    }


def _fixture_session_state() -> dict[str, Any]:
    return {"session_id": "demo-rehearsal-session-1", "cycle_number": 1}


def _fixture_limits() -> dict[str, Any]:
    return {
        "market_limits": {"max_spread_pips": 5.0, "require_timestamp": True},
        "queue_limits": {"max_selected_trades": 1, "require_risk_governor": False},
        "preview_limits": {
            "max_risk_percent": 5.0,
            "max_risk_dollars": 500.0,
            "min_units": 1.0,
            "rounding_increment": 1.0,
            "default_risk_percent": 1.0,
        },
        "fill_config": {"max_spread": 0.01, "max_slippage": 0.01, "slippage": 0.0},
    }


def _as_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _stable_bundle_id(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]
    return f"demo-rehearsal-{digest}"


def _safety_boundary() -> dict[str, bool]:
    return {
        "paper_only": True,
        "demo_review_only": True,
        "live_trading_allowed": False,
        "broker_submit_allowed": False,
        "credentials_used": False,
        "account_id_used": False,
        "network_calls": False,
        "live_order_submitted": False,
        "runtime_file_written": False,
        "broker_write": False,
        "real_orders": False,
    }


def _approval_gates(bundle_complete: bool) -> dict[str, Any]:
    return {
        "regression_suite_green_required": True,
        "demo_rehearsal_evidence_bundle_complete": bundle_complete,
        "risk_limits_present": True,
        "kill_switch_required": True,
        "rollback_plan_required": True,
        "broker_boundary_review_required": True,
        "credential_isolation_review_required": True,
        "human_approval_required": True,
        "single_live_micro_trade_exception_required": True,
        "live_trade_authorized": False,
    }


def _first_selected_candidate(queue_result: Mapping[str, Any]) -> dict[str, Any]:
    selected = queue_result.get("selected_candidates")
    if isinstance(selected, list) and selected and isinstance(selected[0], Mapping):
        return dict(selected[0])
    return {}


def _append_event(ledger: list[dict[str, Any]], event_type: str, session_id: str, payload: Mapping[str, Any], timestamp: float) -> list[dict[str, Any]]:
    event = build_ledger_event(
        event_type=event_type,
        payload=dict(payload),
        session_id=session_id,
        timestamp=timestamp,
    )
    appended = append_ledger_event(ledger, event)
    if appended.get("allowed") is True:
        return list(appended.get("ledger", ledger))
    return ledger


def run_demo_rehearsal_evidence_bundle(
    market_snapshot: Any = None,
    account_state: Any = None,
    session_state: Any = None,
    limits: Any = None,
    timestamp: Any = None,
) -> dict[str, Any]:
    ts = float(timestamp) if isinstance(timestamp, (int, float)) and not isinstance(timestamp, bool) else DEFAULT_TIMESTAMP
    market_input = _fixture_market_snapshot(ts) if market_snapshot is None else market_snapshot
    account = _fixture_account_state() if account_state is None else _as_mapping(account_state)
    session = _fixture_session_state() if session_state is None else _as_mapping(session_state)
    cfg = _fixture_limits()
    if isinstance(limits, Mapping):
        for key, value in limits.items():
            cfg[key] = value

    session_id = str(session.get("session_id") or "demo-rehearsal-session-1")
    blockers: list[str] = []
    ledger: list[dict[str, Any]] = []

    normalized = normalize_market_snapshot(
        market_input,
        limits=cfg.get("market_limits"),
        now_timestamp=ts,
    )
    if normalized.get("allowed") is not True:
        blockers.append(str(normalized.get("blocked_reason") or "market_normalization_blocked"))

    normalized_strategy_input = normalized.get("normalized_for_strategy") if isinstance(normalized, Mapping) else {}
    strategy_result = (
        generate_strategy_candidates(normalized_strategy_input, now_timestamp=ts)
        if normalized.get("allowed") is True
        else {"allowed": False, "candidates": [], "rejected_candidates": [], "blocked_reason": "market_normalization_blocked"}
    )
    if strategy_result.get("allowed") is False:
        blockers.append(str(strategy_result.get("blocked_reason") or "strategy_generation_blocked"))

    queue_result = build_multi_trade_queue(
        strategy_result,
        account_state=account,
        limits=cfg.get("queue_limits"),
        now_timestamp=ts,
    )
    if queue_result.get("allowed") is not True:
        blockers.append(str(queue_result.get("blocked_reason") or "queue_selection_blocked"))

    selected_candidate = _first_selected_candidate(queue_result)
    preview = (
        build_order_preview(
            selected_candidate,
            account_state=account,
            limits=cfg.get("preview_limits"),
            now_timestamp=ts,
        )
        if selected_candidate
        else {"allowed": False, "blocked_reason": "no_selected_candidate", "blocked_reasons": ["no_selected_candidate"]}
    )
    if preview.get("allowed") is not True:
        blockers.append(str(preview.get("blocked_reason") or "order_preview_blocked"))

    paper_fill = (
        simulate_paper_fill(
            preview,
            market_state=market_input if isinstance(market_input, Mapping) else None,
            fill_config=cfg.get("fill_config"),
            timestamp=ts,
        )
        if preview.get("allowed") is True
        else {"allowed": False, "blocked_reason": "preview_not_ready", "blocked_reasons": ["preview_not_ready"]}
    )
    if paper_fill.get("allowed") is not True:
        blockers.append(str(paper_fill.get("blocked_reason") or "paper_fill_blocked"))

    lifecycle = (
        process_trade_update(
            paper_fill.get("trade"),
            price_update={"bid": normalized.get("bid"), "ask": normalized.get("ask")},
            timestamp=ts,
        )
        if paper_fill.get("allowed") is True
        else {"allowed": False, "blocked_reason": "no_paper_trade", "blocked_reasons": ["no_paper_trade"]}
    )

    balance = calculate_risk_base(account, {"compounding_enabled": True, "compounding_cap_percent": 10.0})
    if balance.get("allowed") is not True:
        blockers.append(str(balance.get("blocked_reason") or "balance_review_blocked"))

    if normalized.get("allowed") is True:
        ledger = _append_event(ledger, "market_data_accepted", session_id, {"pair": normalized.get("pair"), "spread_pips": normalized.get("spread_pips")}, ts)
    if strategy_result.get("allowed") is True:
        ledger = _append_event(ledger, "strategy_candidate_created", session_id, {"candidate_count": len(strategy_result.get("candidates", []))}, ts)
    if preview.get("allowed") is True:
        ledger = _append_event(ledger, "preview_created", session_id, {"preview_id": preview.get("preview_id"), "pair": preview.get("pair")}, ts)
    if paper_fill.get("allowed") is True:
        ledger = _append_event(ledger, "paper_trade_opened", session_id, {"fill_id": paper_fill.get("fill_id"), "pair": paper_fill.get("pair")}, ts)

    replay = replay_ledger(ledger, session_id=session_id)
    if replay.get("valid") is not True:
        blockers.append(str(replay.get("blocked_reason") or "session_replay_invalid"))

    selected_ids = [
        item.get("candidate_id")
        for item in queue_result.get("selected_candidates", [])
        if isinstance(item, Mapping)
    ]
    bundle_complete = not blockers and bool(selected_ids) and preview.get("allowed") is True and paper_fill.get("allowed") is True
    safety = _safety_boundary()
    pass_fail = {
        "passed": bundle_complete,
        "paper_demo_review_only": True,
        "protected_boundary_crossed": False,
        "all_required_artifacts_present": bundle_complete,
        "blockers_explicit": True,
        "next_action_deterministic": True,
        "live_trading_remains_false": safety["live_trading_allowed"] is False,
        "broker_submit_remains_false": safety["broker_submit_allowed"] is False,
    }

    id_payload = {
        "timestamp": ts,
        "pair": normalized.get("pair"),
        "selected_candidate_ids": selected_ids,
        "blockers": blockers,
    }
    next_action = (
        "review_demo_rehearsal_evidence_bundle"
        if bundle_complete
        else "resolve_demo_rehearsal_blockers_before_review"
    )

    return {
        "allowed": bundle_complete,
        "decision": "REHEARSAL_EVIDENCE_READY" if bundle_complete else "REHEARSAL_EVIDENCE_BLOCKED",
        "bundle_id": _stable_bundle_id(id_payload),
        "bundle_version": BUNDLE_VERSION,
        "generated_at": ts,
        "mode": DEMO_REHEARSAL_MODE,
        "input_summary": {
            "market_snapshot_present": isinstance(market_input, Mapping),
            "account_state_present": bool(account),
            "session_id": session_id,
            "timestamp": ts,
        },
        "normalized_market_state": normalized,
        "strategy_candidates": strategy_result.get("candidates", []),
        "rejected_candidates": strategy_result.get("rejected_candidates", []) + queue_result.get("rejected_candidates", []),
        "selected_candidate_ids": selected_ids,
        "risk_sizing": preview.get("sizing_result", {}) if isinstance(preview, Mapping) else {},
        "order_preview": preview,
        "paper_fill": paper_fill,
        "lifecycle_summary": lifecycle,
        "balance_summary": balance,
        "evidence_ledger_summary": {
            "event_count": len(ledger),
            "event_types": [event.get("event_type") for event in ledger],
            "valid": replay.get("valid"),
        },
        "session_replay_summary": replay,
        "safety_boundary": safety,
        "approval_gates": _approval_gates(bundle_complete),
        "pass_fail": pass_fail,
        "blockers": list(dict.fromkeys(blockers)),
        "next_action": next_action,
        "live_trading_allowed": False,
        "broker_submit_allowed": False,
        "credentials_used": False,
        "account_id_used": False,
        "network_calls": False,
        "live_order_submitted": False,
        "runtime_file_written": False,
    }

