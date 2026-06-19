"""Deterministic PAPER_SIMULATION forex execution loop primitives.

This module is local-only. It does not read secrets, call a broker, place real
orders, close real trades, or use network APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


DEFAULT_SELECTED_PAIR = "EUR_USD"
DEFAULT_STRATEGY_NAME = "paper_fixture_expectancy_probe_v1"
DEFAULT_ENTRY_TIME_UTC = "2026-06-19T12:00:00Z"
DEFAULT_EXIT_TIME_UTC = "2026-06-19T12:30:00Z"

PAPER_SIGNAL_LABEL = "PAPER_SIGNAL_ONLY"
PAPER_SIMULATION_LABEL = "PAPER_SIMULATION"
PAPER_ONLY_LABEL = "PAPER_ONLY"

SAFE_EVIDENCE_PATH = (
    "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md"
)

FIXTURE_PRICE_BY_PAIR: dict[str, dict[str, float]] = {
    "EUR_USD": {
        "entry": 1.1000,
        "exit": 1.1012,
        "stop_loss": 1.0988,
        "take_profit": 1.1024,
        "spread_pips": 1.2,
        "slippage_pips": 0.1,
    },
    "GBP_USD": {
        "entry": 1.2700,
        "exit": 1.2688,
        "stop_loss": 1.2712,
        "take_profit": 1.2676,
        "spread_pips": 1.4,
        "slippage_pips": 0.1,
    },
}


@dataclass(frozen=True)
class PaperRiskPolicy:
    max_paper_units: int = 1000
    max_paper_trade_risk: float = 25.0
    daily_paper_loss_cap: float = 50.0
    min_confidence: float = 0.55
    one_position_rule: bool = True
    no_duplicate_entry_rule: bool = True
    no_revenge_loop_rule: bool = True
    kill_switch_required: bool = True


class PaperSignalEngine:
    """Build deterministic paper-only signals for loop validation."""

    def __init__(
        self,
        *,
        selected_pair: str = DEFAULT_SELECTED_PAIR,
        strategy_name: str = DEFAULT_STRATEGY_NAME,
        explicit_paper_fixture_mode: bool = True,
    ) -> None:
        self.selected_pair = normalize_pair(selected_pair)
        self.strategy_name = strategy_name
        self.explicit_paper_fixture_mode = explicit_paper_fixture_mode

    def evaluate(self, read_model: Mapping[str, Any] | None = None) -> dict[str, Any]:
        source = _source_context(read_model, self.explicit_paper_fixture_mode)
        if source["stale_status"] != "VALID" and not self.explicit_paper_fixture_mode:
            return {
                **source,
                "label": PAPER_SIGNAL_LABEL,
                "selected_pair": self.selected_pair,
                "strategy_name": self.strategy_name,
                "signal_side": "NONE",
                "confidence": 0.0,
                "signal_reason": "Source is stale or blocked; paper fixture mode is not active.",
                "expected_edge_evidence_path": "UNAVAILABLE",
                "backtest_paper_evidence_required": True,
                "spread_slippage_status": "BLOCKED",
                "block_reason": source["block_reason"],
                "live_execution_allowed": False,
            }

        side = _deterministic_signal_side(self.selected_pair)
        prices = FIXTURE_PRICE_BY_PAIR.get(self.selected_pair)
        if side == "NONE" or prices is None:
            return {
                **source,
                "label": PAPER_SIGNAL_LABEL,
                "selected_pair": self.selected_pair,
                "strategy_name": self.strategy_name,
                "signal_side": "NONE",
                "confidence": 0.0,
                "signal_reason": "No deterministic fixture setup is available for this pair.",
                "expected_edge_evidence_path": "UNAVAILABLE",
                "backtest_paper_evidence_required": True,
                "spread_slippage_status": "BLOCKED",
                "block_reason": "paper_fixture_signal_unavailable",
                "live_execution_allowed": False,
            }

        return {
            **source,
            "label": PAPER_SIGNAL_LABEL,
            "selected_pair": self.selected_pair,
            "strategy_name": self.strategy_name,
            "signal_side": side,
            "confidence": 0.62 if side == "BUY" else 0.59,
            "signal_reason": (
                "Deterministic fixture signal for paper loop validation only; "
                "not a claim of profitable live expectancy."
            ),
            "expected_edge_evidence_path": SAFE_EVIDENCE_PATH,
            "backtest_paper_evidence_required": True,
            "entry_price": prices["entry"],
            "fixture_exit_price": prices["exit"],
            "spread_slippage_status": (
                f"PAPER_VALID spread={prices['spread_pips']}p slippage={prices['slippage_pips']}p"
            ),
            "block_reason": "PAPER_SIGNAL_ONLY; live execution remains blocked.",
            "live_execution_allowed": False,
        }


class PaperRiskGate:
    """Evaluate hard paper risk controls before simulated entry."""

    def __init__(self, policy: PaperRiskPolicy | None = None) -> None:
        self.policy = policy or PaperRiskPolicy()

    def evaluate(
        self,
        signal: Mapping[str, Any],
        *,
        requested_units: int = 1000,
        daily_paper_pl: float = 0.0,
        existing_open_trades: Sequence[Mapping[str, Any]] | None = None,
        recent_entry_signatures: Sequence[str] | None = None,
        revenge_loop_detected: bool = False,
        kill_switch_enabled: bool = True,
    ) -> dict[str, Any]:
        blockers: list[str] = []
        side = str(signal.get("signal_side") or "NONE").upper()
        pair = normalize_pair(signal.get("selected_pair"))
        signature = paper_entry_signature(pair, side, signal.get("strategy_name"))
        recent_signatures = set(str(item) for item in (recent_entry_signatures or ()))
        open_trades = list(existing_open_trades or ())
        estimated_trade_risk = estimate_trade_risk(signal, requested_units)

        if side not in {"BUY", "SELL"}:
            blockers.append("paper_signal_side_not_actionable")
        if requested_units <= 0:
            blockers.append("paper_units_must_be_positive")
        if requested_units > self.policy.max_paper_units:
            blockers.append("max_paper_units_exceeded")
        if estimated_trade_risk > self.policy.max_paper_trade_risk:
            blockers.append("max_paper_trade_risk_exceeded")
        if daily_paper_pl <= -abs(self.policy.daily_paper_loss_cap):
            blockers.append("daily_paper_loss_cap_reached")
        if self.policy.one_position_rule and open_trades:
            blockers.append("one_position_rule_blocks_new_paper_entry")
        if self.policy.no_duplicate_entry_rule and signature in recent_signatures:
            blockers.append("no_duplicate_entry_rule_blocks_signal")
        if self.policy.no_revenge_loop_rule and revenge_loop_detected:
            blockers.append("no_revenge_loop_rule_blocks_signal")
        if self.policy.kill_switch_required and not kill_switch_enabled:
            blockers.append("kill_switch_required_before_paper_entry")
        if float(signal.get("confidence") or 0.0) < self.policy.min_confidence:
            blockers.append("paper_signal_confidence_below_minimum")

        approved = not blockers
        return {
            "mode": PAPER_ONLY_LABEL,
            "risk_approval": approved,
            "paper_risk_approved": approved,
            "max_paper_units": self.policy.max_paper_units,
            "requested_units": requested_units,
            "estimated_paper_trade_risk": round(estimated_trade_risk, 2),
            "max_paper_trade_risk": self.policy.max_paper_trade_risk,
            "daily_paper_loss_cap": self.policy.daily_paper_loss_cap,
            "daily_paper_pl": daily_paper_pl,
            "one_position_rule": self.policy.one_position_rule,
            "no_duplicate_entry_rule": self.policy.no_duplicate_entry_rule,
            "no_revenge_loop_rule": self.policy.no_revenge_loop_rule,
            "kill_switch_required": self.policy.kill_switch_required,
            "kill_switch_enabled": kill_switch_enabled,
            "paper_entry_signature": signature,
            "block_reason_list": blockers,
            "block_reason": "NONE" if approved else "; ".join(blockers),
            "live_execution_allowed": False,
            "broker_write_calls_allowed": False,
        }


class PaperExitPlanner:
    """Build the required paper exit plan before simulated entry."""

    def plan(
        self,
        signal: Mapping[str, Any],
        *,
        stop_loss_required: bool = True,
        take_profit_required: bool = True,
        max_time_required: bool = True,
    ) -> dict[str, Any]:
        side = str(signal.get("signal_side") or "NONE").upper()
        pair = normalize_pair(signal.get("selected_pair"))
        prices = FIXTURE_PRICE_BY_PAIR.get(pair, {})
        entry = float(signal.get("entry_price") or prices.get("entry") or 0.0)
        blockers: list[str] = []

        if side not in {"BUY", "SELL"}:
            blockers.append("paper_signal_side_not_actionable_for_exit_plan")
        if entry <= 0:
            blockers.append("entry_price_required_for_exit_plan")

        stop_loss = float(prices.get("stop_loss") or 0.0)
        take_profit = float(prices.get("take_profit") or 0.0)
        if stop_loss_required and stop_loss <= 0:
            blockers.append("stop_loss_required_before_or_with_entry")
        if take_profit_required and take_profit <= 0:
            blockers.append("take_profit_policy_required")
        if max_time_required is not True:
            blockers.append("max_time_policy_required")

        ready = not blockers
        return {
            "mode": PAPER_ONLY_LABEL,
            "exit_plan_status": "READY" if ready else "BLOCKED",
            "exit_plan_ready": ready,
            "stop_loss_required_before_or_with_entry": True,
            "stop_loss_policy": {
                "status": "REQUIRED_PRESENT" if stop_loss > 0 else "MISSING",
                "price": round(stop_loss, 5) if stop_loss > 0 else "UNAVAILABLE",
            },
            "take_profit_policy": {
                "status": "REQUIRED_PRESENT" if take_profit > 0 else "MISSING",
                "price": round(take_profit, 5) if take_profit > 0 else "UNAVAILABLE",
                "policy": "paper_two_r_fixture_target",
            },
            "trailing_stop_policy": {
                "status": "OPTIONAL_PRESENT",
                "policy": "paper_fixture_trailing_review_only",
            },
            "max_time_policy": {
                "status": "REQUIRED_PRESENT" if max_time_required else "MISSING",
                "duration": "PT30M",
            },
            "auto_exit_readiness": "PAPER_READY" if ready else "BLOCKED",
            "manual_close_fallback": "PAPER_RECONCILER_ONLY_NO_LIVE_CLOSE",
            "block_reason_list": blockers,
            "block_reason": "NONE" if ready else "; ".join(blockers),
            "live_execution_allowed": False,
            "close_trade_allowed": False,
        }


class PaperExecutionSimulator:
    """Create paper entry records only after signal, risk, and exit gates pass."""

    def create_entry(
        self,
        signal: Mapping[str, Any],
        risk: Mapping[str, Any],
        exit_plan: Mapping[str, Any],
        *,
        now_utc: str = DEFAULT_ENTRY_TIME_UTC,
    ) -> dict[str, Any]:
        blockers: list[str] = []
        if str(signal.get("signal_side") or "NONE").upper() not in {"BUY", "SELL"}:
            blockers.append("paper_signal_required_before_entry")
        if risk.get("risk_approval") is not True:
            blockers.append("risk_gate_must_approve_before_entry")
        if exit_plan.get("exit_plan_ready") is not True:
            blockers.append("exit_plan_required_before_entry_completion")

        if blockers:
            return {
                "mode": PAPER_SIMULATION_LABEL,
                "paper_entry_created": False,
                "paper_trade_status": "PAPER_ENTRY_BLOCKED",
                "block_reason_list": blockers,
                "block_reason": "; ".join(blockers),
                "live_execution_allowed": False,
                "broker_write_calls_allowed": False,
                "order_placement_allowed": False,
            }

        pair = normalize_pair(signal.get("selected_pair"))
        side = str(signal.get("signal_side")).upper()
        units = int(risk.get("requested_units") or 0)
        entry_price = float(signal.get("entry_price") or 0.0)
        synthetic_id = f"PAPER_SIM_{pair}_{now_utc.replace(':', '').replace('-', '')}"
        return {
            "mode": PAPER_SIMULATION_LABEL,
            "paper_entry_created": True,
            "paper_trade_status": "PAPER_OPEN_SIMULATED",
            "paper_execution_id": synthetic_id,
            "pair": pair,
            "side": side,
            "units": units,
            "entry_time": now_utc,
            "entry_price": round(entry_price, 5),
            "strategy": signal.get("strategy_name"),
            "risk_approved": True,
            "source_label": signal.get("source_label", "PAPER_FIXTURE"),
            "exit_plan_status": exit_plan.get("exit_plan_status"),
            "block_reason_list": [],
            "block_reason": "NONE",
            "live_execution_allowed": False,
            "broker_write_calls_allowed": False,
            "order_placement_allowed": False,
        }


class PaperReconciler:
    """Simulate paper close/reconcile and produce sanitized history evidence."""

    def close_and_reconcile(
        self,
        entry: Mapping[str, Any],
        exit_plan: Mapping[str, Any],
        *,
        now_utc: str = DEFAULT_EXIT_TIME_UTC,
        exit_reason: str = "PAPER_MAX_TIME_FIXTURE_RECONCILE",
    ) -> dict[str, Any]:
        if entry.get("paper_entry_created") is not True:
            return {
                "mode": PAPER_SIMULATION_LABEL,
                "paper_close_reconcile": False,
                "block_reason": "paper_entry_must_exist_before_reconcile",
                "live_execution_allowed": False,
                "close_trade_allowed": False,
            }

        pair = normalize_pair(entry.get("pair"))
        side = str(entry.get("side") or "NONE").upper()
        prices = FIXTURE_PRICE_BY_PAIR.get(pair, {})
        entry_price = float(entry.get("entry_price") or prices.get("entry") or 0.0)
        exit_price = float(prices.get("exit") or entry_price)
        units = int(entry.get("units") or 0)
        realized_pl = calculate_paper_pl(side, units, entry_price, exit_price)
        row = {
            "pair": pair,
            "side": side,
            "units": units,
            "entry_time": entry.get("entry_time"),
            "exit_time": now_utc,
            "duration": "PT30M",
            "entry_price": round(entry_price, 5),
            "exit_price": round(exit_price, 5),
            "realized_paper_pl": realized_pl,
            "exit_reason": exit_reason,
            "strategy": entry.get("strategy"),
            "risk_approved": entry.get("risk_approved") is True,
            "source_label": entry.get("source_label", "PAPER_FIXTURE"),
            "freshness_utc": now_utc,
            "evidence_status": "PAPER_HISTORY_ROW_READY",
            "stop_loss_policy": exit_plan.get("stop_loss_policy"),
            "take_profit_policy": exit_plan.get("take_profit_policy"),
            "trailing_stop_policy": exit_plan.get("trailing_stop_policy"),
            "max_time_policy": exit_plan.get("max_time_policy"),
            "slippage_if_available": "PAPER_FIXTURE_0.1_PIPS",
            "secret_values_recorded": False,
            "private_identifiers_recorded": False,
            "raw_broker_payload_recorded": False,
        }
        return {
            "mode": PAPER_SIMULATION_LABEL,
            "paper_close_reconcile": True,
            "paper_trade_status": "PAPER_CLOSED_RECONCILED",
            "exit_price": round(exit_price, 5),
            "realized_paper_pl": realized_pl,
            "exit_reason": exit_reason,
            "trading_history_row": row,
            "block_reason": "NONE",
            "live_execution_allowed": False,
            "close_trade_allowed": False,
            "broker_write_calls_allowed": False,
        }


class TradingHistoryWriteback:
    """Prepare sanitized paper trading history writeback evidence."""

    def build(
        self,
        reconciliation: Mapping[str, Any],
        *,
        evidence_path: str = SAFE_EVIDENCE_PATH,
    ) -> dict[str, Any]:
        row = dict(reconciliation.get("trading_history_row") or {})
        row_written = bool(row) and reconciliation.get("paper_close_reconcile") is True
        return {
            "mode": PAPER_ONLY_LABEL,
            "trading_history_row_written": row_written,
            "evidence_path": evidence_path if row_written else "UNAVAILABLE",
            "history_rows": [row] if row_written else [],
            "block_reason": "NONE" if row_written else "paper_history_row_unavailable",
            "live_execution_allowed": False,
        }


def normalize_pair(value: Any) -> str:
    return str(value or DEFAULT_SELECTED_PAIR).strip().upper().replace("/", "_").replace("-", "_")


def paper_entry_signature(pair: str, side: str, strategy_name: Any) -> str:
    return f"{normalize_pair(pair)}|{str(side).upper()}|{strategy_name or DEFAULT_STRATEGY_NAME}"


def estimate_trade_risk(signal: Mapping[str, Any], units: int) -> float:
    pair = normalize_pair(signal.get("selected_pair"))
    prices = FIXTURE_PRICE_BY_PAIR.get(pair, {})
    entry = float(signal.get("entry_price") or prices.get("entry") or 0.0)
    stop_loss = float(prices.get("stop_loss") or 0.0)
    if entry <= 0 or stop_loss <= 0 or units <= 0:
        return 0.0
    return abs(entry - stop_loss) * units


def calculate_paper_pl(side: str, units: int, entry_price: float, exit_price: float) -> float:
    if side == "BUY":
        return round((exit_price - entry_price) * units, 2)
    if side == "SELL":
        return round((entry_price - exit_price) * units, 2)
    return 0.0


def _deterministic_signal_side(pair: str) -> str:
    normalized = normalize_pair(pair)
    if normalized == "EUR_USD":
        return "BUY"
    if normalized == "GBP_USD":
        return "SELL"
    return "NONE"


def _source_context(
    read_model: Mapping[str, Any] | None,
    explicit_paper_fixture_mode: bool,
) -> dict[str, Any]:
    if read_model:
        stale_status = str(read_model.get("stale_status") or "UNKNOWN").upper()
        block_reason = str(read_model.get("block_reason") or "No block reason supplied.")
        return {
            "source_type": read_model.get("source_type", "read-model"),
            "source_label": read_model.get("source_label", "SANITIZED_READ_MODEL"),
            "freshness_utc": read_model.get("freshness_utc", DEFAULT_ENTRY_TIME_UTC),
            "stale_status": stale_status,
            "read_only": True,
            "live_trading_allowed_from_this_data": False,
            "block_reason": block_reason,
        }

    return {
        "source_type": "paper",
        "source_label": "PAPER_SIMULATION_FIXTURE",
        "freshness_utc": DEFAULT_ENTRY_TIME_UTC,
        "stale_status": "VALID" if explicit_paper_fixture_mode else "BLOCKED",
        "read_only": True,
        "live_trading_allowed_from_this_data": False,
        "block_reason": "Explicit paper fixture mode; not live-tradable data.",
    }
