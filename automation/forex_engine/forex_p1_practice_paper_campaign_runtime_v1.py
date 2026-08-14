"""GET-only OANDA Practice runtime bridge for the bounded P1 paper campaign."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from automation.forex_engine.forex_p1_eurusd_m5_history_capture_v1 import (
    build_canonical_history_artifact,
    extract_canonical_completed_candles,
    resolve_canonical_practice_transport,
    validate_canonical_history_artifact,
)
from automation.forex_engine.forex_p1_eurusd_market_history_signal_v1 import (
    build_signal_state,
)
from automation.forex_engine.forex_p1_oanda_practice_snapshot_capture_v1 import (
    extract_sanitized_price_snapshot,
)
from automation.forex_engine.forex_p1_supervised_paper_campaign_v1 import (
    CampaignHalt,
    CampaignWait,
)
from automation.forex_engine.forex_p1_supervised_paper_session_v1 import (
    build_completed_trade_record,
    load_active_session,
    open_paper_session,
)
from automation.forex_engine.oanda_read_only_client import (
    OandaReadOnlyClient,
    OandaReadOnlyClientError,
)

VERSION = "forex_p1_practice_paper_campaign_runtime_v1"
INSTRUMENT = "EUR_USD"
GRANULARITY = "M5"
CANDLE_COUNT = 50
POLL_INTERVAL_SECONDS = 300
DEFAULT_PAPER_UNITS = 100
SAFETY = {
    "broker_write_performed": False,
    "practice_order_performed": False,
    "live_trade_performed": False,
    "money_movement_performed": False,
    "credentials_persisted": False,
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _candidate_from_signal(signal: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any] | None:
    """Transform only a canonical BUY decision into the session candidate contract."""
    if signal.get("status") != "BUY":
        return None
    stop = float(signal["stop_price"])
    target = float(signal["target_price"])
    entry = float(snapshot["ask"])
    if not stop < entry < target:
        return None
    identity = json.dumps(
        {"signal_id": signal["signal_id"], "observed_at_utc": snapshot["observed_at_utc"]},
        sort_keys=True,
    )
    return {
        "strategy_id": signal["strategy_id"],
        "candidate_id": "p1-runtime-" + hashlib.sha256(identity.encode()).hexdigest()[:24],
        "instrument": INSTRUMENT,
        "direction": "BUY",
        "units": DEFAULT_PAPER_UNITS,
        "stop_price": stop,
        "target_price": target,
        "risk_amount": round((entry - stop) * DEFAULT_PAPER_UNITS, 8),
        "entry_rationale": "genuine observed EUR USD M5 canonical strategy signal",
        "status": "PAPER_ELIGIBLE",
        "sanitized": True,
        "current": True,
        "broker_call_performed": False,
        "broker_write_performed": False,
        "order_submission_allowed": False,
        "demo_execution_allowed": False,
        "live_execution_allowed": False,
        "money_movement_allowed": False,
    }


def _capture(
    client: OandaReadOnlyClient,
    now: datetime,
    *,
    pricing_now: Callable[[], datetime] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    transport = resolve_canonical_practice_transport(client)
    candle_payload = transport.candles(INSTRUMENT, granularity=GRANULARITY, count=CANDLE_COUNT)
    candles = extract_canonical_completed_candles(candle_payload)
    history = validate_canonical_history_artifact(
        build_canonical_history_artifact(candles, requested_count=CANDLE_COUNT), now=now
    )
    signal = build_signal_state(history, generated_at_utc=_stamp(now))
    pricing = transport.pricing((INSTRUMENT,))
    pricing_validation_time = (pricing_now or _utc_now)().astimezone(timezone.utc)
    snapshot = extract_sanitized_price_snapshot(
        pricing,
        broker_call_performed=True,
        credentials_loaded_runtime_only=True,
        now=pricing_validation_time,
    )
    # The paper-session controller deliberately receives only its narrower,
    # sanitized snapshot schema; runtime credential metadata never crosses it.
    session_snapshot = {
        key: snapshot[key]
        for key in (
            "schema", "evidence_type", "provenance", "instrument", "observed_at_utc",
            "bid", "ask", "mid", "spread", "source_status", "stale_status",
            "read_only", "broker_write_performed", "account_identifier_included",
            "raw_payload_included",
        )
    }
    session_snapshot["credentials_included"] = False
    return signal, session_snapshot


def completed_paper_records(
    client: OandaReadOnlyClient,
    *,
    cycles: int,
    reviewer_identity: str,
    runtime_path: Path,
    now: Callable[[], datetime] = _utc_now,
    sleep: Callable[[float], None],
    owner_cancelled: Callable[[], bool] = lambda: False,
    kill_switch_active: Callable[[], bool] = lambda: False,
    risk_halt_active: Callable[[], bool] = lambda: False,
) -> Iterator[dict[str, Any] | CampaignHalt | CampaignWait]:
    """Yield legitimate closed paper records, or one explicit fail-closed halt."""
    if isinstance(cycles, bool) or not isinstance(cycles, int) or cycles <= 0:
        raise ValueError("positive_cycle_count_required")
    if not reviewer_identity.strip():
        raise ValueError("owner_reviewer_required")
    resolve_canonical_practice_transport(client)

    for index in range(cycles):
        if owner_cancelled():
            yield CampaignHalt("OWNER_CANCELLATION")
            return
        if kill_switch_active():
            yield CampaignHalt("KILL_SWITCH_ACTIVE")
            return
        if risk_halt_active():
            yield CampaignHalt("RISK_HALT")
            return
        current = now().astimezone(timezone.utc)
        try:
            signal, snapshot = _capture(client, current, pricing_now=now)
        except OandaReadOnlyClientError:
            yield CampaignHalt("PRACTICE_DATA_UNAVAILABLE")
            return
        except ValueError as exc:
            reason = "STALE_MARKET_DATA" if "stale" in str(exc).lower() else "INVALID_MARKET_DATA"
            yield CampaignHalt(reason)
            return

        active = load_active_session(runtime_path)
        if active is None:
            candidate = _candidate_from_signal(signal, snapshot)
            if candidate is None:
                yield CampaignWait(index + 1, cycles)
            else:
                open_paper_session(snapshot, candidate, reviewer_identity, _stamp(current), runtime_path)
        else:
            bid = float(snapshot["bid"])
            if bid >= float(active["target_price"]) or bid <= float(active["stop_price"]):
                reason = "paper_target" if bid >= float(active["target_price"]) else "paper_stop"
                record = build_completed_trade_record(
                    active, snapshot, reason, reviewer_identity, _stamp(current)
                )
                runtime_path.unlink(missing_ok=True)
                yield record
        if index + 1 < cycles:
            sleep(POLL_INTERVAL_SECONDS)

    yield CampaignHalt("OWNER_SESSION_CYCLE_LIMIT")


def runtime_safety_state() -> dict[str, Any]:
    return {
        "version": VERSION,
        "environment": "PRACTICE",
        "http_methods": ["GET"],
        "instrument": INSTRUMENT,
        "granularity": GRANULARITY,
        "maximum_open_paper_positions": 1,
        **SAFETY,
    }
