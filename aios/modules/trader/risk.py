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
        paper_cash: float | None = None,
        paper_positions: dict[str, int] | None = None,
        current_price: float | None = None,
        daily_paper_loss: float = 0.0,
    ) -> RiskDecisionEvent:
        paper_positions = paper_positions or {}
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
        if daily_paper_loss >= config.max_daily_loss:
            return self._blocked(signal, "Daily paper loss exceeds maximum daily loss.")
        if signal.direction == "BUY_REVIEW":
            if paper_cash is not None and current_price is not None:
                required_cash = current_price * signal.quantity
                if paper_cash < required_cash:
                    return self._blocked(signal, "Insufficient paper cash for buy review.")
            is_new_symbol = signal.symbol not in paper_positions or paper_positions.get(signal.symbol, 0) == 0
            open_positions = sum(1 for quantity in paper_positions.values() if quantity > 0)
            if is_new_symbol and open_positions >= config.max_open_positions:
                return self._blocked(signal, "Maximum open paper positions reached.")
        if signal.direction == "SELL_REVIEW":
            available_quantity = paper_positions.get(signal.symbol, 0)
            if available_quantity <= 0:
                return self._blocked(signal, "Missing paper position for sell review.")
            if available_quantity < signal.quantity:
                return self._blocked(signal, "Paper position is too small for sell review.")

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
