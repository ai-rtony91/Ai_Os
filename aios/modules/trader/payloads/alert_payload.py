"""Mock-only alert payload builder for local paper previews."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime


ALLOWED_PERMISSIONS = {"bullish", "bearish", "neutral", "blocked"}
ALLOWED_SIGNALS = {"BUY", "SELL", "HOLD"}
_FORBIDDEN_PAYLOAD_KEYS = {
    "webhook" + "_url",
    "broker",
    "api" + "_key",
    "secret" + "_key",
    "live" + "_order",
    "real" + "_order",
}


@dataclass(frozen=True)
class MockAlertPayload:
    schema_version: str
    source: str
    symbol: str
    timeframe: str
    permission: str
    signal: str
    confidence: float
    paper_only: bool
    live_execution_status: str
    execution_allowed: bool
    route_status: str
    timestamp: str
    metadata: dict


def build_mock_alert_payload(
    symbol: str,
    timeframe: str,
    permission: str,
    signal: str,
    confidence: float,
    metadata: dict | None = None,
) -> dict:
    """Build a local mock payload; it is never transmitted."""

    _validate_inputs(symbol, timeframe, permission, signal, confidence, metadata)
    payload = MockAlertPayload(
        schema_version="trader.payload.v0.1",
        source="AIOS_TRADER_MOCK",
        symbol=symbol,
        timeframe=timeframe,
        permission=permission,
        signal=signal,
        confidence=confidence,
        paper_only=True,
        live_execution_status="BLOCKED",
        execution_allowed=False,
        route_status="MOCK_ONLY",
        timestamp=datetime.now(UTC).isoformat(),
        metadata=dict(metadata or {}),
    )
    result = asdict(payload)
    _validate_forbidden_keys(result)
    return result


def _validate_inputs(
    symbol: str,
    timeframe: str,
    permission: str,
    signal: str,
    confidence: float,
    metadata: dict | None,
) -> None:
    if not symbol:
        raise ValueError("symbol cannot be empty")
    if not timeframe:
        raise ValueError("timeframe cannot be empty")
    if permission not in ALLOWED_PERMISSIONS:
        raise ValueError(f"permission must be one of {sorted(ALLOWED_PERMISSIONS)}")
    if signal not in ALLOWED_SIGNALS:
        raise ValueError(f"signal must be one of {sorted(ALLOWED_SIGNALS)}")
    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict when provided")
    if metadata:
        _validate_forbidden_keys(metadata)


def _validate_forbidden_keys(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in _FORBIDDEN_PAYLOAD_KEYS:
                raise ValueError("payload contains a blocked routing field")
            _validate_forbidden_keys(item)
    elif isinstance(value, list):
        for item in value:
            _validate_forbidden_keys(item)
