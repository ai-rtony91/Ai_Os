"""Safety-first configuration for the AIOS paper trader."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TraderConfig:
    mode: str = "paper_only"
    live_execution_status: str = "BLOCKED"
    execution_allowed: bool = False
    broker_status: str = "PAPER_ONLY"
    external_routing_enabled: bool = False
    api_keys_required: bool = False
    leverage_enabled: bool = False
    margin_enabled: bool = False
    options_enabled: bool = False
    live_broker_enabled: bool = False
    starting_cash: float = 100000.0
    max_position_size: int = 1
    max_open_positions: int = 3
    max_daily_loss: float = 1000.0
    allowed_symbols: list[str] | None = field(default=None)
    allowed_timeframes: list[str] | None = field(default=None)

    def validate_safety(self) -> None:
        if self.mode != "paper_only":
            raise ValueError("TraderConfig mode must remain paper_only.")
        if self.live_execution_status != "BLOCKED":
            raise ValueError("Live execution must remain BLOCKED.")
        if self.execution_allowed:
            raise ValueError("Execution allowed must remain false for v0.1.")
        if self.broker_status != "PAPER_ONLY":
            raise ValueError("Broker status must remain PAPER_ONLY.")
        if self.external_routing_enabled:
            raise ValueError("External routing must remain disabled.")
        if self.api_keys_required:
            raise ValueError("API keys must not be required.")
        if self.leverage_enabled:
            raise ValueError("Leverage must remain disabled.")
        if self.margin_enabled:
            raise ValueError("Margin must remain disabled.")
        if self.options_enabled:
            raise ValueError("Options must remain disabled.")
        if self.live_broker_enabled:
            raise ValueError("Live broker support must remain disabled.")
