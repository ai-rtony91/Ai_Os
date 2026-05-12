"""Paper outcome tracking for closed local trades."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class PaperTradeOutcome:
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: int
    status: str
    opened_at: str
    closed_at: str
    pnl: float
    paper_only: bool = True
    live_execution_status: str = "BLOCKED"
    execution_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class _OpenPaperPosition:
    symbol: str
    side: str
    entry_price: float
    quantity: int
    opened_at: str


class PaperOutcomeTracker:
    """Creates closed paper outcomes from paired paper fills.

    v0.2 keeps this intentionally small: BUY_REVIEW opens a local long paper
    position and SELL_REVIEW closes it. Unpaired fills remain open in memory.
    """

    def __init__(self) -> None:
        self._open_positions: dict[str, _OpenPaperPosition] = {}
        self.outcomes: list[PaperTradeOutcome] = []

    def record_fill(self, fill: dict[str, object]) -> PaperTradeOutcome | None:
        if fill.get("paper_only") is not True:
            raise ValueError("Paper outcome tracker accepts paper-only fills only.")
        if fill.get("direction") == "BUY_REVIEW":
            self._open_positions[str(fill["symbol"])] = _OpenPaperPosition(
                symbol=str(fill["symbol"]),
                side="LONG",
                entry_price=float(fill["fill_price"]),
                quantity=int(fill["quantity"]),
                opened_at=str(fill["timestamp"]),
            )
            return None
        if fill.get("direction") != "SELL_REVIEW":
            return None

        symbol = str(fill["symbol"])
        open_position = self._open_positions.pop(symbol, None)
        if open_position is None:
            return None

        quantity = min(open_position.quantity, int(fill["quantity"]))
        exit_price = float(fill["fill_price"])
        pnl = (exit_price - open_position.entry_price) * quantity
        outcome = PaperTradeOutcome(
            symbol=symbol,
            side=open_position.side,
            entry_price=open_position.entry_price,
            exit_price=exit_price,
            quantity=quantity,
            status="CLOSED_PAPER",
            opened_at=open_position.opened_at,
            closed_at=str(fill["timestamp"]),
            pnl=pnl,
        )
        self.outcomes.append(outcome)
        return outcome

    def to_dicts(self) -> list[dict[str, object]]:
        return [outcome.to_dict() for outcome in self.outcomes]

    def daily_paper_loss(self) -> float:
        return abs(sum(outcome.pnl for outcome in self.outcomes if outcome.pnl < 0))
