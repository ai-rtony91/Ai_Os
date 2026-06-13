"""Paper-only readiness gate for the AI_OS Forex Engine.

This module is deterministic and local-only. It does not import broker,
webhook, network, scheduler, daemon, telemetry, or runtime mutation paths.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from automation.forex_engine.confidence import ConfidenceEngine
from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.models import Direction, EngineMode, ForexSignal
from automation.forex_engine.risk import RiskEngine
from automation.forex_engine.signals import validate_signal


PAPER_READY = "PAPER_READY"
PAPER_REJECTED = "PAPER_REJECTED"

BLOCKED_ACTIONS = (
    "broker_api_call",
    "oanda_api_call",
    "real_order_submission",
    "webhook_execution",
    "secret_or_api_key_load",
    "live_market_data_fetch",
    "scheduler_or_daemon_start",
    "worker_launch",
)

FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "account",
        "account_id",
        "api_key",
        "broker",
        "broker_token",
        "credential",
        "credentials",
        "live",
        "live_order",
        "market_data_url",
        "oanda",
        "order",
        "order_id",
        "password",
        "secret",
        "token",
        "webhook",
        "webhook_url",
    }
)

NEXT_SAFE_ACCEPT_ACTION = (
    "Review the PAPER_ONLY readiness evidence, then continue fixture-based "
    "paper engine build work under human approval."
)
NEXT_SAFE_REJECT_ACTION = (
    "Remove unsafe or invalid signal inputs, keep external execution blocked, "
    "and rerun the paper-only readiness gate."
)


def build_valid_mock_signal() -> ForexSignal:
    """Return a deterministic local fixture signal that can pass the gate."""
    return ForexSignal(
        symbol="EURUSD",
        timeframe="5m",
        direction=Direction.BUY,
        entry_price=1.0800,
        stop_loss=1.0790,
        take_profit=1.0820,
        timestamp="2026-06-12T00:00:00Z",
        strategy_name="paper_readiness_fixture_v1",
        metadata={
            "source": "local_fixture",
            "setup_quality": "clean",
            "session": "london",
            "research_lane": "paper_only_readiness_gate",
        },
    )


def build_unsafe_mock_signal() -> ForexSignal:
    """Return a deterministic fixture that must be rejected by the gate."""
    return ForexSignal(
        symbol="EURUSD",
        timeframe="5m",
        direction=Direction.BUY,
        entry_price=1.0800,
        stop_loss=1.0790,
        take_profit=1.0820,
        timestamp="2026-06-12T00:00:00Z",
        strategy_name="unsafe_external_path_fixture",
        metadata={
            "source": "local_fixture",
            "setup_quality": "clean",
            "session": "london",
            "api_key": "blocked-placeholder",
            "webhook_url": "blocked-placeholder",
        },
    )


def evaluate_paper_readiness(
    signal: ForexSignal,
    *,
    config: ForexEngineConfig | None = None,
    open_trades: Iterable[object] | None = None,
    closed_trades: Iterable[object] | None = None,
    current_balance_usd: float = 500.0,
    current_daily_pnl_usd: float = 0.0,
) -> dict:
    """Evaluate a signal for PAPER_ONLY readiness and return safe evidence."""
    config = config or ForexEngineConfig()
    open_trade_list = list(open_trades or [])
    closed_trade_list = list(closed_trades or [])

    reasons: list[str] = []
    risk_flags: list[str] = []
    validation_reasons: list[str] = []
    confidence_payload = None
    risk_payload = None

    try:
        validation_reasons = list(validate_config(config) or [])
        validation_reasons.extend(validate_signal(signal, config) or [])
    except ValueError as exc:
        risk_flags.append("input_validation_failed")
        reasons.append(str(exc))

    unsafe_metadata = _detect_forbidden_metadata(signal.metadata)
    if unsafe_metadata:
        risk_flags.append("unsafe_external_metadata")
        reasons.append(
            "Signal metadata contains blocked external execution fields: "
            + ", ".join(unsafe_metadata)
        )

    if config.mode != EngineMode.PAPER_ONLY:
        risk_flags.append("non_paper_mode")
        reasons.append("Forex readiness gate only permits PAPER_ONLY mode.")

    if not risk_flags:
        confidence = ConfidenceEngine(config).score_signal(signal)
        confidence_payload = {
            "score": confidence.score,
            "allowed": confidence.allowed,
            "reasons": list(confidence.reasons),
            "blocked_reason": confidence.blocked_reason,
        }
        if not confidence.allowed:
            risk_flags.append("confidence_below_threshold")
            reasons.append(confidence.blocked_reason or "Confidence gate rejected signal.")

    if not risk_flags:
        risk_decision = RiskEngine(config).can_open_new_trade(
            open_trade_list,
            closed_trade_list,
            current_balance_usd,
            current_daily_pnl_usd,
        )
        risk_payload = asdict(risk_decision)
        if not risk_decision.allowed:
            risk_flags.append("risk_gate_rejected")
            reasons.append(risk_decision.blocked_reason or "Paper risk gate rejected signal.")

    accepted_for_paper = not risk_flags
    if accepted_for_paper:
        reasons.append("Signal passed PAPER_ONLY validation, confidence, and risk gates.")

    return {
        "status": PAPER_READY if accepted_for_paper else PAPER_REJECTED,
        "mode": EngineMode.PAPER_ONLY,
        "paper_only": True,
        "accepted_for_paper": accepted_for_paper,
        "execution_allowed": False,
        "reason": reasons[0],
        "reasons": reasons,
        "risk_flags": risk_flags,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "next_safe_action": (
            NEXT_SAFE_ACCEPT_ACTION if accepted_for_paper else NEXT_SAFE_REJECT_ACTION
        ),
        "signal": {
            "symbol": signal.symbol,
            "timeframe": signal.timeframe,
            "direction": signal.direction,
            "timestamp": signal.timestamp,
            "strategy_name": signal.strategy_name,
        },
        "validation_reasons": validation_reasons,
        "confidence": confidence_payload,
        "risk": risk_payload,
        "safety": {
            "no_live_trading": True,
            "no_broker_apis": True,
            "no_oanda": True,
            "no_webhooks": True,
            "no_real_market_data": True,
            "no_real_orders": True,
            "no_api_keys_or_secrets": True,
            "no_network": True,
            "no_scheduler_or_daemon": True,
            "no_worker_launch": True,
        },
    }


def _detect_forbidden_metadata(metadata: dict) -> list[str]:
    lower_keys = {str(key).lower() for key in metadata.keys()}
    return sorted(lower_keys & FORBIDDEN_METADATA_KEYS)
