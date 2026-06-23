"""Read-only live data bridge for forex delivery readiness.

The bridge may use fixture fallback by default or perform OANDA GET-only reads
when explicitly enabled by runtime environment. It never places, modifies,
cancels, or closes orders and it never returns secrets, account IDs, order IDs,
transaction IDs, or raw broker payloads.
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable

from automation.forex_engine.oanda_read_only_client import (
    OandaReadOnlyClient,
    OandaReadOnlyClientError,
)
from automation.forex_engine.read_only_live_data_sanitizer import (
    SANITIZED_EVIDENCE_PATH,
    assert_no_forbidden_output,
    sanitize_account_summary,
    sanitize_pending_orders,
    sanitize_positions,
    sanitize_pricing,
    sanitize_trading_history,
    build_money_strip_payload,
    source_fields,
    utc_now_iso,
)


DEFAULT_SELECTED_PAIR = "EUR_USD"
SUPPORTED_BROKER = "oanda"


ClientFactory = Callable[..., Any]


class ReadOnlyLiveDataBridge:
    def __init__(
        self,
        *,
        env: dict[str, str] | None = None,
        client_factory: ClientFactory | None = None,
        selected_pair: str = DEFAULT_SELECTED_PAIR,
        now_utc: str | None = None,
    ) -> None:
        self.env = dict(os.environ if env is None else env)
        self.client_factory = client_factory or OandaReadOnlyClient
        self.selected_pair = _normalize_pair(selected_pair)
        self.now_utc = now_utc or utc_now_iso()

    def run(self) -> dict[str, Any]:
        enable = self.env.get("AIOS_FOREX_READONLY_LIVE_ENABLE") == "1"
        broker = str(self.env.get("AIOS_FOREX_BROKER") or "").strip().lower()
        token_present = bool(self.env.get("OANDA_API_TOKEN"))
        account_present = bool(self.env.get("OANDA_ACCOUNT_ID"))
        environment = _normalize_environment(self.env.get("OANDA_ENVIRONMENT"))

        if not enable:
            return self._fixture_model(
                "AIOS_FOREX_READONLY_LIVE_ENABLE is not 1; using fixture/readiness fallback."
            )
        if broker != SUPPORTED_BROKER:
            return self._blocked_model(
                source_type="broker-live-read-only",
                source_label="READ_ONLY_BROKER_BLOCKED",
                broker_mode=environment,
                block_reason="AIOS_FOREX_BROKER must be oanda for the first read-only bridge.",
                token_present=token_present,
                account_present=account_present,
            )
        if not token_present or not account_present:
            missing = []
            if not token_present:
                missing.append("OANDA_API_TOKEN")
            if not account_present:
                missing.append("OANDA_ACCOUNT_ID")
            return self._blocked_model(
                source_type="broker-live-read-only",
                source_label="OANDA_READ_ONLY_BLOCKED",
                broker_mode=environment,
                block_reason=(
                    "Missing runtime credential presence for "
                    + ", ".join(missing)
                    + ". Values are not printed or stored."
                ),
                token_present=token_present,
                account_present=account_present,
            )

        token = self.env.get("OANDA_API_TOKEN") or ""
        account_id = self.env.get("OANDA_ACCOUNT_ID") or ""
        try:
            client = self.client_factory(
                api_token=token,
                account_id=account_id,
                environment=environment,
            )
            snapshot = client.fetch_read_only_snapshot(instruments=(self.selected_pair,))
            model = self._model_from_oanda_snapshot(
                snapshot,
                broker_mode=environment,
                token_present=token_present,
                account_present=account_present,
            )
        except OandaReadOnlyClientError as exc:
            model = self._blocked_model(
                source_type="broker-live-read-only",
                source_label="OANDA_READ_ONLY_BLOCKED",
                broker_mode=environment,
                block_reason=exc.public_reason,
                token_present=token_present,
                account_present=account_present,
            )
        except Exception as exc:
            model = self._blocked_model(
                source_type="broker-live-read-only",
                source_label="OANDA_READ_ONLY_BLOCKED",
                broker_mode=environment,
                block_reason=f"READ_ONLY_BRIDGE_ERROR_SANITIZED:{type(exc).__name__}",
                token_present=token_present,
                account_present=account_present,
            )

        assert_no_forbidden_output(model, forbidden_values=(token, account_id))
        return model

    def _fixture_model(self, block_reason: str) -> dict[str, Any]:
        return self._blocked_model(
            source_type="fixture",
            source_label="FIXTURE_NOT_LIVE",
            broker_mode="not_enabled",
            block_reason=block_reason,
            token_present=False,
            account_present=False,
        )

    def _blocked_model(
        self,
        *,
        source_type: str,
        source_label: str,
        broker_mode: str,
        block_reason: str,
        token_present: bool,
        account_present: bool,
    ) -> dict[str, Any]:
        context = source_fields(
            source_type=source_type,
            source_label=source_label,
            freshness_utc=self.now_utc,
            stale_status="BLOCKED",
            block_reason=block_reason,
        )
        broker_state = {
            **context,
            "broker_mode": broker_mode,
            "account_reachable": False,
            "open_positions_reconciled": False,
            "pending_orders_reconciled": False,
            "daily_pl_available": False,
            "margin_risk_available": False,
            "block_reason": block_reason,
        }
        positions = {
            **context,
            "positions_reconciled": False,
            "open_position_count": 0,
            "open_trade_count": 0,
            "positions": [],
            "open_trades": [],
            "block_reason": block_reason,
        }
        risk_pl = {
            **context,
            "daily_pl_available": False,
            "realized_pl": "UNAVAILABLE",
            "unrealized_pl": "UNAVAILABLE",
            "margin_available": "UNAVAILABLE",
            "margin_risk_available": False,
            "block_reason": block_reason,
        }
        history = {
            **context,
            "trading_history_available": False,
            "closed_trade_count": 0,
            "rows": [],
            "block_reason": "No sanitized real closed-trade history is available.",
        }
        market = {
            **context,
            "selected_pair": self.selected_pair,
            "price_snapshot_available": False,
            "block_reason": block_reason,
        }
        return self._aggregate_model(
            context=context,
            market=market,
            broker_state=broker_state,
            positions=positions,
            risk_pl=risk_pl,
            exit_readiness=self._exit_readiness(context, positions),
            trading_history=history,
            money_strip=build_money_strip_payload(
                source_context=context,
                broker_mode=broker_mode,
                broker_state=broker_state,
                positions=positions,
                risk_pl=risk_pl,
                market=market,
            ),
            token_present=token_present,
            account_present=account_present,
        )

    def _model_from_oanda_snapshot(
        self,
        snapshot: dict[str, Any],
        *,
        broker_mode: str,
        token_present: bool,
        account_present: bool,
    ) -> dict[str, Any]:
        block_reason = (
            "Read-only broker data is available for display; live execution remains blocked "
            "pending paper validation and Human Owner arming."
        )
        context = source_fields(
            source_type="broker-live-read-only",
            source_label="OANDA_READ_ONLY_SANITIZED",
            freshness_utc=self.now_utc,
            stale_status="VALID",
            block_reason=block_reason,
        )
        account_payload = snapshot.get("account_summary") or snapshot.get("account_details")
        broker_state = sanitize_account_summary(
            account_payload,
            broker_mode=broker_mode,
            freshness_utc=self.now_utc,
            source_context=context,
        )
        positions = sanitize_positions(
            snapshot.get("open_positions"),
            snapshot.get("open_trades"),
            source_context=context,
        )
        pending_orders = sanitize_pending_orders(
            snapshot.get("pending_orders"),
            source_context=context,
        )
        broker_state["pending_order_count"] = pending_orders["pending_order_count"]
        broker_state["pending_orders_reconciled"] = pending_orders["pending_orders_reconciled"]
        market = sanitize_pricing(
            snapshot.get("pricing"),
            selected_pair=self.selected_pair,
            source_context=context,
        )
        history = sanitize_trading_history(
            snapshot.get("transactions"),
            source_context=context,
        )
        risk_pl = {
            **context,
            "daily_pl_available": broker_state["daily_pl_available"],
            "realized_pl": broker_state["realized_pl"],
            "unrealized_pl": broker_state["unrealized_pl"],
            "margin_available": broker_state["margin_available"],
            "margin_risk_available": broker_state["margin_risk_available"],
            "block_reason": broker_state["block_reason"],
        }
        return self._aggregate_model(
            context=context,
            market=market,
            broker_state=broker_state,
            positions=positions,
            risk_pl=risk_pl,
            money_strip=build_money_strip_payload(
                source_context=context,
                broker_mode=broker_mode,
                broker_state=broker_state,
                positions=positions,
                risk_pl=risk_pl,
                market=market,
            ),
            exit_readiness=self._exit_readiness(context, positions),
            trading_history=history,
            token_present=token_present,
            account_present=account_present,
        )

    def _exit_readiness(
        self,
        context: dict[str, Any],
        positions: dict[str, Any],
    ) -> dict[str, Any]:
        has_open_position = int(positions.get("open_position_count") or 0) > 0
        if has_open_position:
            block_reason = (
                "Open position protection cannot be proven by this read-only bridge; "
                "auto-exit remains blocked."
            )
        else:
            block_reason = "No open position requiring live exit protection was reconciled."
        return {
            **context,
            "auto_exit_ready": False,
            "stop_loss_present": False,
            "take_profit_policy_present": False,
            "trailing_stop_policy_present": False,
            "max_time_policy_present": False,
            "manual_close_fallback": "BROKER_UI_MANUAL_FALLBACK_REQUIRED",
            "block_reason": block_reason,
        }

    def _aggregate_model(
        self,
        *,
        context: dict[str, Any],
        market: dict[str, Any],
        broker_state: dict[str, Any],
        positions: dict[str, Any],
        risk_pl: dict[str, Any],
        money_strip: dict[str, Any],
        exit_readiness: dict[str, Any],
        trading_history: dict[str, Any],
        token_present: bool,
        account_present: bool,
    ) -> dict[str, Any]:
        execution_readiness = self._execution_readiness(
            context=context,
            broker_state=broker_state,
            positions=positions,
            risk_pl=risk_pl,
            exit_readiness=exit_readiness,
            trading_history=trading_history,
        )
        model = {
            "schema": "AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE.v1",
            **context,
            "mode": "READ_ONLY",
            "selected_pair": self.selected_pair,
            "secret_status": {
                "OANDA_API_TOKEN_STATUS": "PRESENT" if token_present else "MISSING",
                "OANDA_ACCOUNT_ID_STATUS": "PRESENT" if account_present else "MISSING",
                "SECRET_VALUES_PRINTED": False,
                "ACCOUNT_ID_RECORDED": False,
                "RAW_BROKER_PAYLOAD_RECORDED": False,
            },
            "market": market,
            "broker_state": broker_state,
            "positions": positions,
            "risk_pl": risk_pl,
            "money_strip": money_strip,
            "exit_readiness": exit_readiness,
            "trading_history": trading_history,
            "execution_readiness": execution_readiness,
            "capabilities": {
                "read_only": True,
                "get_requests_only": True,
                "post_put_patch_delete_allowed": False,
                "broker_write_calls_allowed": False,
                "order_placement_allowed": False,
                "close_trade_allowed": False,
                "live_execution_allowed": False,
            },
        }
        assert_no_forbidden_output(model)
        return model

    def _execution_readiness(
        self,
        *,
        context: dict[str, Any],
        broker_state: dict[str, Any],
        positions: dict[str, Any],
        risk_pl: dict[str, Any],
        exit_readiness: dict[str, Any],
        trading_history: dict[str, Any],
    ) -> dict[str, Any]:
        blockers = []
        if context["source_type"] == "fixture":
            blockers.append("real_market_data_source_not_enabled")
        if broker_state.get("account_reachable") is not True:
            blockers.append("broker_account_state_not_reconciled")
        if positions.get("positions_reconciled") is not True:
            blockers.append("positions_not_reconciled")
        if risk_pl.get("daily_pl_available") is not True:
            blockers.append("daily_pl_not_available")
        if exit_readiness.get("auto_exit_ready") is not True:
            blockers.append("auto_exit_not_ready")
        if trading_history.get("trading_history_available") is not True:
            blockers.append("trading_history_writeback_not_available")
        blockers.extend(
            [
                "signal_logic_not_connected",
                "risk_governor_not_approved",
                "human_owner_live_execution_not_armed",
            ]
        )
        return {
            **context,
            "LIVE_READY": False,
            "live_execution_allowed": False,
            "blocked_reasons": _unique(blockers),
            "next_safe_action": (
                "Run the read-only live data bridge, review sanitized readiness, then proceed "
                "to AIOS-FOREX-PAPER-SIGNAL-EXECUTION-LOOP-V1 before any live arming gate."
            ),
        }


def build_read_only_live_data_bridge_read_model(
    *,
    env: dict[str, str] | None = None,
    client_factory: ClientFactory | None = None,
    selected_pair: str = DEFAULT_SELECTED_PAIR,
    now_utc: str | None = None,
) -> dict[str, Any]:
    return ReadOnlyLiveDataBridge(
        env=env,
        client_factory=client_factory,
        selected_pair=selected_pair,
        now_utc=now_utc,
    ).run()


def build_sanitized_report(model: dict[str, Any]) -> str:
    assert_no_forbidden_output(model)
    summary = {
        "source_type": model.get("source_type"),
        "source_label": model.get("source_label"),
        "freshness_utc": model.get("freshness_utc"),
        "stale_status": model.get("stale_status"),
        "broker_reachable": model.get("broker_state", {}).get("account_reachable"),
        "positions_reconciled": model.get("positions", {}).get("positions_reconciled"),
        "pl_available": model.get("risk_pl", {}).get("daily_pl_available"),
        "trading_history_available": model.get("trading_history", {}).get(
            "trading_history_available"
        ),
        "live_execution_allowed": False,
        "next_safe_action": model.get("execution_readiness", {}).get("next_safe_action"),
    }
    return (
        "# AIOS Forex Read-Only Live Data Bridge Dry Run V1\n\n"
        "Status: READ_ONLY_SANITIZED\n\n"
        "No live trade, BUY, SELL, close, order placement, broker write call, secret, "
        "account ID, order ID, transaction ID, or raw broker payload is recorded here.\n\n"
        "## Summary\n\n"
        f"```json\n{json.dumps(summary, indent=2, sort_keys=True)}\n```\n\n"
        "## Sanitized Read Model\n\n"
        f"```json\n{json.dumps(model, indent=2, sort_keys=True)}\n```\n"
    )


def _normalize_environment(value: Any) -> str:
    normalized = str(value or "practice").strip().lower()
    if normalized == "live":
        return "live"
    return "practice"


def _normalize_pair(value: Any) -> str:
    return str(value or DEFAULT_SELECTED_PAIR).strip().upper().replace("/", "_").replace("-", "_")


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
