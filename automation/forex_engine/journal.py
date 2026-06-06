"""JSONL journal writer for PAPER_ONLY forex simulation events."""

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from automation.forex_engine.models import EngineMode, JournalEvent, utc_now_iso


class JournalWriter:
    def __init__(self, journal_dir):
        self.journal_dir = Path(journal_dir)
        self.journal_dir.mkdir(parents=True, exist_ok=True)

    @property
    def journal_path(self) -> Path:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        return self.journal_dir / f"forex_paper_journal_{today}.jsonl"

    def write_event(self, event_type, payload):
        event = JournalEvent(
            event_type=event_type,
            timestamp=utc_now_iso(),
            mode=EngineMode.PAPER_ONLY,
            payload=payload,
        )
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")
        return event

    def write_trade_opened(self, trade):
        return self.write_event("paper_trade_opened", self._trade_payload(trade))

    def write_trade_closed(self, trade):
        return self.write_event("paper_trade_closed", self._trade_payload(trade))

    def _trade_payload(self, trade):
        payload = {
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "direction": trade.direction,
            "entry_price": trade.entry_price,
            "stop_loss": trade.stop_loss,
            "take_profit": trade.take_profit,
            "confidence_score": trade.confidence_score,
            "risk_amount_usd": trade.risk_amount_usd,
            "position_size_units": trade.position_size_units,
            "status": trade.status,
        }
        if trade.status == "CLOSED":
            payload["pnl_usd"] = trade.pnl_usd
            payload["outcome"] = trade.outcome
            payload["exit_price"] = trade.exit_price
        return payload
