"""Paper-only risk manager."""

from __future__ import annotations

from aios.modules.trader.config import TraderConfig
from aios.modules.trader.events import PermissionEvent, RiskDecisionEvent, SignalEvent


class RiskManager:
    def evaluate(
        self,
        signal: SignalEvent,
        permission: PermissionEvent,
        config: TraderConfig,
    ) -> RiskDecisionEvent:
        try:
            config.validate_safety()
        except ValueError as exc:
            return self._blocked(signal, str(exc))

        if config.execution_allowed:
            return self._blocked(signal, "Execution flag is not allowed in paper-only mode.")
        if config.live_execution_status != "BLOCKED":
            return self._blocked(signal, "Live execution status is not blocked.")
        if permission.permission == "blocked":
            return self._blocked(signal, "Permission filter blocked the signal.")
        if signal.direction == "BLOCKED":
            return self._blocked(signal, "Signal direction is blocked.")
        if signal.direction == "HOLD":
            return self._blocked(signal, "Hold signal does not create a paper order.")
        if signal.direction == "BUY_REVIEW" and permission.permission != "bullish":
            return self._blocked(signal, "Buy review requires bullish permission.")
        if signal.direction == "SELL_REVIEW" and permission.permission != "bearish":
            return self._blocked(signal, "Sell review requires bearish permission.")
        if config.allowed_symbols is not None and signal.symbol not in config.allowed_symbols:
            return self._blocked(signal, "Symbol is not allowed.")
        if config.allowed_timeframes is not None and signal.timeframe not in config.allowed_timeframes:
            return self._blocked(signal, "Timeframe is not allowed.")
        if signal.quantity > config.max_position_size:
            return self._blocked(signal, "Requested quantity exceeds maximum position size.")
        if signal.quantity <= 0:
            return self._blocked(signal, "Requested quantity must be positive.")

        return RiskDecisionEvent(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            timestamp=signal.timestamp,
            approved=True,
            direction=signal.direction,
            quantity=signal.quantity,
            reason="Approved for paper order only.",
        )

    def _blocked(self, signal: SignalEvent, reason: str) -> RiskDecisionEvent:
        return RiskDecisionEvent(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            timestamp=signal.timestamp,
            approved=False,
            direction="BLOCKED",
            quantity=0,
            reason=reason,
        )
