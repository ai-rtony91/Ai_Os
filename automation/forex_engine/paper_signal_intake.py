"""Deterministic paper-only Forex signal intake ledger helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Sequence

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import Direction, EngineMode, ForexSignal, utc_now_iso
from automation.forex_engine.readiness import (
    PAPER_REJECTED,
    PAPER_READY,
    evaluate_paper_readiness,
)


PAPER_SIGNAL_INTAKE_SCHEMA = "forex_signal_intake_ledger_v1"


def _normalise_signal_payload(signal: Mapping[str, Any] | ForexSignal) -> Dict[str, Any]:
    if isinstance(signal, ForexSignal):
        return {
            "symbol": signal.symbol,
            "timeframe": signal.timeframe,
            "direction": signal.direction,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "timestamp": signal.timestamp,
            "strategy_name": signal.strategy_name,
            "metadata": dict(signal.metadata),
        }

    if isinstance(signal, Mapping):
        return {
            "symbol": signal["symbol"],
            "timeframe": signal["timeframe"],
            "direction": signal["direction"],
            "entry_price": float(signal["entry_price"]),
            "stop_loss": float(signal["stop_loss"]),
            "take_profit": float(signal["take_profit"]),
            "timestamp": str(signal["timestamp"]),
            "strategy_name": str(signal["strategy_name"]),
            "metadata": dict(signal.get("metadata", {})),
        }

    raise TypeError("signal_input must be a ForexSignal object or a mapping.")


def _build_signal_id(signal: Mapping[str, Any], signal_id: str | None) -> str:
    if signal_id:
        return signal_id

    return hashlib.md5(
        json.dumps(
            {
                "symbol": signal["symbol"],
                "timeframe": signal["timeframe"],
                "direction": signal["direction"],
                "entry_price": signal["entry_price"],
                "stop_loss": signal["stop_loss"],
                "take_profit": signal["take_profit"],
                "timestamp": signal["timestamp"],
                "strategy_name": signal["strategy_name"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8"),
    ).hexdigest()


def _safe_ledger_id(
    generated_at_utc: str,
    signal_id: str,
    readiness_status: str,
    accepted_for_paper: bool,
) -> str:
    return hashlib.sha256(
        f"{generated_at_utc}|{signal_id}|{readiness_status}|{accepted_for_paper}".encode(
            "utf-8"
        ),
    ).hexdigest()


def _as_forex_signal(signal_payload: Dict[str, Any]) -> ForexSignal:
    return ForexSignal(
        symbol=signal_payload["symbol"],
        timeframe=signal_payload["timeframe"],
        direction=str(signal_payload["direction"]).upper(),
        entry_price=float(signal_payload["entry_price"]),
        stop_loss=float(signal_payload["stop_loss"]),
        take_profit=float(signal_payload["take_profit"]),
        timestamp=str(signal_payload["timestamp"]),
        strategy_name=str(signal_payload["strategy_name"]),
        metadata=dict(signal_payload.get("metadata", {})),
    )


def _signal_summary(signal_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": signal_payload["symbol"],
        "timeframe": signal_payload["timeframe"],
        "direction": signal_payload["direction"],
        "strategy_name": signal_payload["strategy_name"],
        "timestamp": signal_payload["timestamp"],
        "metadata": dict(signal_payload.get("metadata", {})),
    }


def evaluate_local_signal_for_ledger(
    signal: Mapping[str, Any] | ForexSignal,
    *,
    signal_id: str | None = None,
    generated_at_utc: str | None = None,
    config: ForexEngineConfig | None = None,
    open_trades: Sequence[object] | None = None,
    closed_trades: Sequence[object] | None = None,
    current_balance_usd: float = 500.0,
    current_daily_pnl_usd: float = 0.0,
) -> Dict[str, Any]:
    """Convert a local/mock signal to a deterministic paper ledger record."""
    payload = _normalise_signal_payload(signal)
    payload_signal_id = _build_signal_id(payload, signal_id)

    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    forex_signal = _as_forex_signal(payload)
    if str(forex_signal.direction).upper() not in (Direction.BUY, Direction.SELL):
        raise ValueError("Signal direction must be BUY or SELL.")

    readiness = evaluate_paper_readiness(
        forex_signal,
        config=config,
        open_trades=open_trades,
        closed_trades=closed_trades,
        current_balance_usd=current_balance_usd,
        current_daily_pnl_usd=current_daily_pnl_usd,
    )

    accepted_for_paper = bool(readiness["accepted_for_paper"])
    readiness_status = (
        PAPER_READY if accepted_for_paper else PAPER_REJECTED
    )

    blocked_actions = list(readiness["blocked_actions"])

    ledger_record_id = _safe_ledger_id(
        generated_at_utc,
        payload_signal_id,
        readiness_status,
        accepted_for_paper,
    )

    return {
        "schema": PAPER_SIGNAL_INTAKE_SCHEMA,
        "mode": EngineMode.PAPER_ONLY,
        "ledger_record_id": ledger_record_id,
        "signal_id": payload_signal_id,
        "generated_at_utc": generated_at_utc,
        "signal_summary": _signal_summary(payload),
        "readiness_status": readiness_status,
        "accepted_for_paper": accepted_for_paper,
        "execution_allowed": False,
        "blocked_actions": blocked_actions,
        "reason": readiness["reason"],
        "reasons": list(readiness["reasons"]),
        "risk_flags": list(readiness["risk_flags"]),
        "safety": dict(readiness["safety"]),
        "next_safe_action": readiness["next_safe_action"],
    }


def build_demo_local_signal(signal_id: str = "demo_signal_001") -> Dict[str, Any]:
    """Return a deterministic local dict-based signal for demo/tests."""
    return {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "direction": Direction.BUY,
        "entry_price": 1.0800,
        "stop_loss": 1.0790,
        "take_profit": 1.0820,
        "timestamp": utc_now_iso(),
        "strategy_name": "paper_signal_intake_fixture_v1",
        "metadata": {
            "source": "local_fixture",
            "lane": "paper_signal_intake",
            "signal_id": signal_id,
        },
    }


def build_unsafe_demo_local_signal() -> Dict[str, Any]:
    signal = build_demo_local_signal(signal_id="unsafe_demo_signal")
    signal["metadata"] = dict(signal["metadata"])
    signal["metadata"]["api_key"] = "blocked-key"
    signal["metadata"]["webhook_url"] = "https://example.local/webhook"
    signal["metadata"]["oanda"] = "blocked-broker-flag"
    signal["metadata"]["broker"] = "blocked-broker-flag"
    return signal
