"""Paper-only route preview formatter."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True)
class PaperRoutePreview:
    route_id: str
    symbol: str
    timeframe: str
    permission: str
    signal: str
    action: str
    route_status: str
    paper_only: bool
    live_execution_status: str
    execution_allowed: bool
    blocked_reason: str
    timestamp: str
    payload: dict


def build_paper_route_preview(payload: dict) -> dict:
    """Return a local route preview only; no external side effects occur."""

    permission = payload.get("permission", "")
    signal = payload.get("signal", "")
    action, blocked_reason = _resolve_action(permission, signal)
    preview = PaperRoutePreview(
        route_id=str(uuid4()),
        symbol=payload.get("symbol", ""),
        timeframe=payload.get("timeframe", ""),
        permission=permission,
        signal=signal,
        action=action,
        route_status="PAPER_PREVIEW_ONLY",
        paper_only=True,
        live_execution_status="BLOCKED",
        execution_allowed=False,
        blocked_reason=blocked_reason,
        timestamp=datetime.now(UTC).isoformat(),
        payload=dict(payload),
    )
    return asdict(preview)


def _resolve_action(permission: str, signal: str) -> tuple[str, str]:
    if permission == "blocked":
        return "BLOCKED", "Permission is blocked."
    if signal == "HOLD":
        return "NO_TRADE", "Signal is HOLD."
    if permission == "bullish" and signal == "BUY":
        return "PAPER_BUY_PREVIEW", ""
    if permission == "bearish" and signal == "SELL":
        return "PAPER_SELL_PREVIEW", ""
    return "BLOCKED", "Permission and signal do not match a paper preview action."
