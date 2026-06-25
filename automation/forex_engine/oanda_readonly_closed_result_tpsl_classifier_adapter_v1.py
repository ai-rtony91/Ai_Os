from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any

from automation.forex_engine.oanda_closed_trade_tpsl_result_capture_v1 import (
    BLOCKED_INVALID_EVIDENCE,
    BLOCKED_UNSAFE_EVIDENCE,
    CLOSED_BREAKEVEN_OTHER,
    CLOSED_BY_OTHER_OR_MANUAL,
    CLOSED_BY_STOP_LOSS,
    CLOSED_BY_TAKE_PROFIT,
    CLOSED_REALIZED_LOSS_OTHER,
    CLOSED_REALIZED_PROFIT_OTHER,
    STILL_OPEN_NO_REALIZED_RESULT,
    TRADE_NOT_FOUND,
    evaluate_oanda_closed_trade_tpsl_result_capture_v1,
)


PACKET_ID = (
    "AIOS-FOREX-OANDA-READONLY-CLOSED-RESULT-TPSL-CLASSIFIER-ADAPTER-V1"
)
ADAPTER_VERSION = "v1"

ADAPTED_STILL_OPEN_NO_REALIZED_RESULT = "ADAPTED_STILL_OPEN_NO_REALIZED_RESULT"
ADAPTED_CLOSED_BY_TAKE_PROFIT = "ADAPTED_CLOSED_BY_TAKE_PROFIT"
ADAPTED_CLOSED_BY_STOP_LOSS = "ADAPTED_CLOSED_BY_STOP_LOSS"
ADAPTED_CLOSED_BY_OTHER_OR_MANUAL = "ADAPTED_CLOSED_BY_OTHER_OR_MANUAL"
ADAPTED_CLOSED_REALIZED_PROFIT_OTHER = "ADAPTED_CLOSED_REALIZED_PROFIT_OTHER"
ADAPTED_CLOSED_REALIZED_LOSS_OTHER = "ADAPTED_CLOSED_REALIZED_LOSS_OTHER"
ADAPTED_CLOSED_BREAKEVEN_OTHER = "ADAPTED_CLOSED_BREAKEVEN_OTHER"
ADAPTED_TRADE_NOT_FOUND = "ADAPTED_TRADE_NOT_FOUND"
ADAPTED_BLOCKED_UNSAFE_EVIDENCE = "ADAPTED_BLOCKED_UNSAFE_EVIDENCE"
ADAPTED_BLOCKED_INVALID_EVIDENCE = "ADAPTED_BLOCKED_INVALID_EVIDENCE"

DEFAULT_TRADE_ANCHOR: dict[str, str] = {
    "trade_id": "328",
    "instrument": "EUR_USD",
    "entry_open_price": "1.13689",
    "take_profit_order_id": "329",
    "stop_loss_order_id": "330",
    "expected_units": "1",
}

CLASSIFIER_STATUS_TO_ADAPTER_STATUS = {
    STILL_OPEN_NO_REALIZED_RESULT: ADAPTED_STILL_OPEN_NO_REALIZED_RESULT,
    CLOSED_BY_TAKE_PROFIT: ADAPTED_CLOSED_BY_TAKE_PROFIT,
    CLOSED_BY_STOP_LOSS: ADAPTED_CLOSED_BY_STOP_LOSS,
    CLOSED_BY_OTHER_OR_MANUAL: ADAPTED_CLOSED_BY_OTHER_OR_MANUAL,
    CLOSED_REALIZED_PROFIT_OTHER: ADAPTED_CLOSED_REALIZED_PROFIT_OTHER,
    CLOSED_REALIZED_LOSS_OTHER: ADAPTED_CLOSED_REALIZED_LOSS_OTHER,
    CLOSED_BREAKEVEN_OTHER: ADAPTED_CLOSED_BREAKEVEN_OTHER,
    TRADE_NOT_FOUND: ADAPTED_TRADE_NOT_FOUND,
    BLOCKED_UNSAFE_EVIDENCE: ADAPTED_BLOCKED_UNSAFE_EVIDENCE,
    BLOCKED_INVALID_EVIDENCE: ADAPTED_BLOCKED_INVALID_EVIDENCE,
}

EXECUTION_AUTHORITY_FIELDS = (
    "network_allowed",
    "network_call_allowed",
    "broker_call_allowed",
    "broker_network_call_allowed",
    "broker_api_call_allowed",
    "broker_write_allowed",
    "credential_access_allowed",
    "credential_read_allowed",
    "account_id_read_allowed",
    "vault_read_allowed",
    "windows_vault_read_allowed",
    "dotenv_read_allowed",
    "env_read_allowed",
    "order_placement_allowed",
    "order_close_allowed",
    "order_mutation_allowed",
    "trade_mutation_allowed",
    "position_mutation_allowed",
    "live_endpoint_allowed",
    "live_trading_allowed",
    "live_order_allowed",
    "raw_broker_payload_persistence_allowed",
    "file_persistence_allowed",
    "write_allowed",
    "bucket_update_allowed",
    "bucket_mutation_allowed",
    "result_bucket_update_allowed",
    "result_bucket_mutation_allowed",
    "next_order_authorized",
    "next_trade_authorized",
    "next_allocation_authorized",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "live_funding_allowed",
)

SAFETY_PROOF_FIELDS = (
    "network_call_performed",
    "broker_network_call_performed",
    "broker_api_call_performed",
    "broker_call_performed",
    "broker_write_performed",
    "credential_read_performed",
    "account_id_read_performed",
    "vault_read_performed",
    "windows_vault_read_performed",
    "dotenv_read",
    "env_read",
    "order_placement_performed",
    "order_close_performed",
    "order_mutation_performed",
    "trade_mutation_performed",
    "position_mutation_performed",
    "orders_endpoint_called",
    "live_endpoint_used",
    "raw_broker_payload_persisted",
    "file_persistence_performed",
    "write_performed",
    "bucket_update_performed",
    "bucket_mutation_performed",
    "result_bucket_update_performed",
    "result_bucket_mutation_performed",
    "next_order_authorized",
    "next_trade_authorized",
    "next_allocation_authorized",
    "scheduler_started",
    "daemon_started",
    "webhook_called",
    "live_funding_performed",
)

UNSAFE_TRUE_FIELDS = EXECUTION_AUTHORITY_FIELDS + SAFETY_PROOF_FIELDS

SENSITIVE_VALUE_KEYS = {
    "access_token",
    "token",
    "authorization",
    "password",
    "secret",
    "secret_value",
    "credential_value",
    "api_key",
    "apikey",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
}

SENSITIVE_KEY_TERMS = (
    "access_token",
    "authorization",
    "password",
    "secret",
    "credential_value",
    "api_key",
    "apikey",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
)

SENSITIVE_KEY_EXEMPTIONS = {
    "credential_name",
    "credential_names",
    "approved_credential_names_only",
}

RAW_PAYLOAD_KEY_TERMS = ("raw_payload", "rawpayload", "raw_broker_payload")
REQUEST_HEADER_KEY_TERMS = ("headers", "request_headers", "requestheaders")
ENDPOINT_URL_KEY_TERMS = ("url", "endpoint_url", "endpointurl")
LIVE_OANDA_HOST = "api-fxtrade.oanda.com"

TRADE_ID_KEYS = ("trade_id", "tradeID", "tradeId", "id")
UNIT_KEYS = ("currentUnits", "current_units", "units")
REALIZED_PL_KEYS = ("realizedPL", "realized_pl", "pl", "profitLoss")
UNREALIZED_PL_KEYS = ("unrealizedPL", "unrealized_pl", "trueUnrealizedPL")


def evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
    read_only_capture_output: dict[str, Any] | Mapping[str, Any] | None,
    trade_anchor: dict[str, Any] | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    anchor = _normalize_anchor(trade_anchor)
    if read_only_capture_output is None or not isinstance(
        read_only_capture_output,
        Mapping,
    ):
        return _adapter_decision(
            adapter_status=ADAPTED_BLOCKED_INVALID_EVIDENCE,
            blockers=["read_only_capture_output_must_be_mapping"],
            warnings=["adapter_rejected_input_before_classifier"],
            trade_anchor=anchor,
            extracted_evidence_summary=_empty_evidence_summary(
                rejected_before_classifier=True,
            ),
            classifier_decision=None,
            classifier_status=None,
            classifier_evidence={},
        )

    unsafe_blockers = _unsafe_input_blockers(
        read_only_capture_output,
        "read_only_capture_output",
    )
    if unsafe_blockers:
        return _adapter_decision(
            adapter_status=ADAPTED_BLOCKED_UNSAFE_EVIDENCE,
            blockers=unsafe_blockers,
            warnings=[
                "unsafe_authority_or_sensitive_runtime_field_present",
                "adapter_blocked_before_classifier",
            ],
            trade_anchor=anchor,
            extracted_evidence_summary=_empty_evidence_summary(
                rejected_before_classifier=True,
            ),
            classifier_decision=None,
            classifier_status=None,
            classifier_evidence={},
        )

    extracted = _extract_classifier_evidence(read_only_capture_output, anchor)
    classifier_evidence = extracted["classifier_evidence"]
    classifier_decision = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        classifier_evidence,
        anchor,
    )
    classifier_status = _text(classifier_decision.get("status"))
    adapter_status = CLASSIFIER_STATUS_TO_ADAPTER_STATUS.get(
        classifier_status,
        ADAPTED_BLOCKED_INVALID_EVIDENCE,
    )
    blockers = [
        f"classifier_status_{classifier_status}"
    ] if adapter_status == ADAPTED_BLOCKED_INVALID_EVIDENCE and classifier_status not in {
        BLOCKED_INVALID_EVIDENCE,
        BLOCKED_UNSAFE_EVIDENCE,
    } else _string_items(classifier_decision.get("blockers"))
    warnings = _warnings(adapter_status)
    warnings.extend(_string_items(classifier_decision.get("warnings")))
    warnings.extend(extracted["warnings"])

    return _adapter_decision(
        adapter_status=adapter_status,
        blockers=_unique(blockers),
        warnings=_unique(warnings),
        trade_anchor=anchor,
        extracted_evidence_summary=extracted["extracted_evidence_summary"],
        classifier_decision=classifier_decision,
        classifier_status=classifier_status,
        classifier_evidence=classifier_evidence,
    )


def default_trade_anchor_v1() -> dict[str, str]:
    return dict(DEFAULT_TRADE_ANCHOR)


def oanda_readonly_closed_result_tpsl_classifier_adapter_template_v1() -> dict[str, Any]:
    return {
        "trade_anchor": default_trade_anchor_v1(),
        "read_only_capture_output": {
            "decision": {
                "pl_evidence": {
                    "open_trade_evidence": [
                        {
                            "trade_id": "328",
                            "instrument": "EUR_USD",
                            "currentUnits": "1",
                            "unrealizedPL": "sanitized_number",
                            "takeProfitOrder": {"id": "329"},
                            "stopLossOrder": {"id": "330"},
                        }
                    ],
                    "realized_pl_values": [],
                    "realized_pl_total": "0",
                    "account_summary_snapshot": {
                        "snapshot_present": True,
                    },
                }
            },
            "transaction_match": {
                "transactions": [],
            },
            "execution_authority": _execution_authority(),
            "safety_proof": _safety_proof(),
        },
        "template_only": True,
        "adapter_only_not_broker_caller": True,
        "adapter_only_not_order_closer": True,
        "adapter_only_not_bucket_updater": True,
        "adapter_only_not_scheduler_or_daemon": True,
        "no_next_order_authorized": True,
        "runtime_input_rule": {
            "command_line_secret_argument_supported": False,
            "command_line_account_identifier_supported": False,
            "env_file_supported": False,
            "repo_secret_supported": False,
            "oanda_capture_execution_supported": False,
            "owner_run_required": False,
        },
    }


def oanda_readonly_closed_result_tpsl_classifier_adapter_default_samples_v1() -> (
    dict[str, dict[str, Any]]
):
    return {
        "capture-still-open": _safe_capture(
            {
                "decision": {
                    "status": "READ_ONLY_FILLED_TRADE_PL_CAPTURE_ATTEMPTED",
                    "pl_evidence": {
                        "open_trade_evidence": [
                            {
                                "trade_id": "328",
                                "instrument": "EUR_USD",
                                "currentUnits": "1",
                                "unrealizedPL": "0.0008",
                                "takeProfitOrder": {"id": "329"},
                                "stopLossOrder": {"id": "330"},
                            }
                        ],
                        "realized_pl_values": [],
                        "realized_pl_total": "0",
                        "account_summary_snapshot": {"snapshot_present": True},
                    },
                },
            }
        ),
        "capture-closed-by-tp": _safe_capture(
            {
                "closed_trade_snapshot": {
                    "closed_trades": [
                        {
                            "id": "328",
                            "instrument": "EUR_USD",
                            "state": "CLOSED",
                            "currentUnits": "0",
                            "closeTime": "SANITIZED_TIMESTAMP",
                            "realizedPL": "0.0012",
                            "takeProfitOrder": {"id": "329"},
                        }
                    ]
                },
                "transaction_match": {
                    "transactions": [
                        {
                            "id": "329",
                            "type": "ORDER_FILL",
                            "orderID": "329",
                            "reason": "TAKE_PROFIT_ORDER",
                            "tradesClosed": [
                                {"tradeID": "328", "realizedPL": "0.0012"}
                            ],
                        }
                    ]
                },
            }
        ),
        "capture-closed-by-sl": _safe_capture(
            {
                "trade_evidence": {
                    "tradeID": "328",
                    "instrument": "EUR_USD",
                    "state": "CLOSED",
                    "currentUnits": "0",
                    "closeTime": "SANITIZED_TIMESTAMP",
                    "realizedPL": "-0.0010",
                    "stopLossOrder": {"id": "330"},
                },
                "transactions": [
                    {
                        "id": "330",
                        "type": "ORDER_FILL",
                        "orderID": "330",
                        "reason": "STOP_LOSS_ORDER",
                        "tradesClosed": [
                            {"tradeID": "328", "realizedPL": "-0.0010"}
                        ],
                    }
                ],
            }
        ),
        "capture-closed-other-profit": _safe_capture(
            {
                "closed_trade_snapshot": {
                    "closed_trades": [
                        {
                            "tradeID": "328",
                            "instrument": "EUR_USD",
                            "state": "CLOSED",
                            "currentUnits": "0",
                            "closeTime": "SANITIZED_TIMESTAMP",
                            "realizedPL": "0.0006",
                        }
                    ]
                },
                "transactions": [
                    {
                        "id": "410",
                        "type": "ORDER_FILL",
                        "reason": "CLIENT_ORDER",
                        "tradesClosed": [
                            {"tradeID": "328", "realizedPL": "0.0006"}
                        ],
                    }
                ],
            }
        ),
        "capture-closed-other-loss": _safe_capture(
            {
                "trade_evidence": {
                    "tradeID": "328",
                    "instrument": "EUR_USD",
                    "state": "CLOSED",
                    "currentUnits": "0",
                    "closeTime": "SANITIZED_TIMESTAMP",
                },
                "pl_evidence": {
                    "realized_pl_values": ["-0.0006"],
                    "open_trade_evidence": [],
                },
            }
        ),
        "capture-trade-not-found": _safe_capture(
            {
                "open_trade_snapshot": {"open_trades": []},
                "closed_trade_snapshot": {"closed_trades": []},
                "transaction_match": {"transactions": []},
                "pl_evidence": {
                    "open_trade_evidence": [],
                    "realized_pl_values": [],
                    "realized_pl_total": None,
                },
            }
        ),
        "capture-unsafe": {
            "execution_authority": {
                **_execution_authority(),
                "order_placement_allowed": True,
            },
            "pl_evidence": {
                "open_trade_evidence": [],
                "realized_pl_values": [],
            },
            "safety_proof": _safety_proof(),
        },
    }


def _extract_classifier_evidence(
    capture: Mapping[str, Any],
    anchor: Mapping[str, str],
) -> dict[str, Any]:
    open_trades: list[dict[str, Any]] = []
    closed_trades: list[dict[str, Any]] = []
    trade_evidence: list[dict[str, Any]] = []
    transactions: list[dict[str, Any]] = []
    source_paths: list[str] = []
    account_summary_paths: list[str] = []
    warnings: list[str] = []
    pl_values: list[str] = []
    pl_total: str | None = None

    for prefix, container in _containers(capture):
        open_trades.extend(
            _trade_collection(container.get("open_trade_evidence"), anchor),
        )
        _append_source_path(
            source_paths,
            prefix,
            "open_trade_evidence",
            container.get("open_trade_evidence"),
        )
        closed_trades.extend(
            _trade_collection(container.get("closed_trade_evidence"), anchor),
        )
        _append_source_path(
            source_paths,
            prefix,
            "closed_trade_evidence",
            container.get("closed_trade_evidence"),
        )
        trade_items = _trade_collection(container.get("trade_evidence"), anchor)
        if trade_items:
            trade_evidence.extend(trade_items)
            source_paths.append(f"{prefix}.trade_evidence")

        if _looks_trade_like(container):
            trade_evidence.append(_sanitize_trade(container, anchor))
            source_paths.append(prefix)

        tx_items = _transaction_collection(container.get("transactions"), anchor)
        if tx_items:
            transactions.extend(tx_items)
            source_paths.append(f"{prefix}.transactions")

        tx_match = _mapping(container.get("transaction_match"))
        if tx_match:
            matched_transactions = _transaction_collection(
                tx_match.get("transactions"),
                anchor,
            )
            if matched_transactions:
                transactions.extend(matched_transactions)
                source_paths.append(f"{prefix}.transaction_match.transactions")
            elif _looks_transaction_like(tx_match):
                transactions.append(_sanitize_transaction(tx_match, anchor))
                source_paths.append(f"{prefix}.transaction_match")

        open_snapshot = _mapping(container.get("open_trade_snapshot"))
        if open_snapshot:
            open_trades.extend(
                _trade_collection(
                    _first_present(
                        open_snapshot,
                        "open_trades",
                        "openTrades",
                        "trades",
                    ),
                    anchor,
                )
            )
            source_paths.append(f"{prefix}.open_trade_snapshot")

        closed_snapshot = _mapping(container.get("closed_trade_snapshot"))
        if closed_snapshot:
            closed_trades.extend(
                _trade_collection(
                    _first_present(
                        closed_snapshot,
                        "closed_trades",
                        "closedTrades",
                        "trades",
                    ),
                    anchor,
                )
            )
            source_paths.append(f"{prefix}.closed_trade_snapshot")

        account_snapshot = container.get("account_summary_snapshot")
        if isinstance(account_snapshot, Mapping):
            account_summary_paths.append(f"{prefix}.account_summary_snapshot")

        if "realized_pl_values" in container:
            pl_values.extend(_decimal_text_items(container.get("realized_pl_values")))
            source_paths.append(f"{prefix}.realized_pl_values")
        if "realized_pl_total" in container and container.get(
            "realized_pl_total",
        ) is not None:
            pl_total = _decimal_text_or_none(container.get("realized_pl_total"))
            source_paths.append(f"{prefix}.realized_pl_total")

    open_trades = _dedupe_mappings(open_trades)
    closed_trades = _dedupe_mappings(closed_trades)
    trade_evidence = _dedupe_mappings(trade_evidence)
    transactions = _dedupe_mappings(transactions)
    if not closed_trades and not trade_evidence:
        closed_trades = _dedupe_mappings(
            _closed_trades_from_transactions(transactions, anchor),
        )

    pl_evidence: dict[str, Any] = {
        "open_trade_evidence": open_trades,
        "realized_pl_values": pl_values,
        "realized_pl_total": pl_total,
    }
    if account_summary_paths:
        pl_evidence["account_summary_snapshot"] = {"snapshot_present": True}

    classifier_evidence: dict[str, Any] = {
        "open_trade_evidence": open_trades,
        "closed_trade_evidence": closed_trades,
        "trade_evidence": trade_evidence,
        "transactions": transactions,
        "pl_evidence": pl_evidence,
        "execution_authority": _execution_authority(),
        "safety_proof": _safety_proof(),
    }

    dropped_paths = _dropped_input_field_paths(capture)
    if dropped_paths:
        warnings.append("non_classifier_fields_dropped_before_classification")

    return {
        "classifier_evidence": classifier_evidence,
        "extracted_evidence_summary": {
            "sanitized_input_only": True,
            "classifier_evidence_built": True,
            "rejected_before_classifier": False,
            "source_paths": _unique(source_paths),
            "open_trade_evidence_count": len(open_trades),
            "closed_trade_evidence_count": len(closed_trades),
            "trade_evidence_count": len(trade_evidence),
            "transaction_evidence_count": len(transactions),
            "realized_pl_value_count": len(pl_values),
            "realized_pl_total_present": pl_total is not None,
            "account_summary_snapshot_present": bool(account_summary_paths),
            "account_summary_snapshot_paths": _unique(account_summary_paths),
            "dropped_input_field_count": len(dropped_paths),
            "dropped_input_field_paths": dropped_paths[:20],
            "raw_broker_payload_persisted": False,
            "broker_or_network_call_performed_here": False,
            "adapter_only_not_broker_caller": True,
        },
        "warnings": warnings,
    }


def _adapter_decision(
    *,
    adapter_status: str,
    blockers: Sequence[str],
    warnings: Sequence[str],
    trade_anchor: Mapping[str, str],
    extracted_evidence_summary: Mapping[str, Any],
    classifier_decision: Mapping[str, Any] | None,
    classifier_status: str | None,
    classifier_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    classifier_mapping = _mapping(classifier_decision)
    profit_claimed = bool(
        classifier_mapping.get("is_closed") is True
        and classifier_mapping.get("profit_claimed") is True
    )
    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "adapter_version": ADAPTER_VERSION,
        "status": adapter_status,
        "adapter_status": adapter_status,
        "blockers": list(blockers),
        "warnings": _unique(_warnings(adapter_status) + list(warnings)),
        "trade_anchor": dict(trade_anchor),
        "extracted_evidence_summary": dict(extracted_evidence_summary),
        "classifier_evidence": dict(classifier_evidence),
        "classifier_decision": dict(classifier_mapping)
        if classifier_mapping
        else None,
        "classifier_status": classifier_status,
        "profit_claimed": profit_claimed,
        "no_new_order_authorized": True,
        "no_next_trade_authorized": True,
        "no_bucket_update_performed": True,
        "safety_proof": _safety_proof(),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(adapter_status),
    }
    result.update(_safety_proof())
    return result


def _containers(capture: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    containers: list[tuple[str, Mapping[str, Any]]] = [("root", capture)]
    decision = _mapping(capture.get("decision"))
    if decision:
        containers.append(("decision", decision))
        decision_pl = _mapping(decision.get("pl_evidence"))
        if decision_pl:
            containers.append(("decision.pl_evidence", decision_pl))
    pl_evidence = _mapping(capture.get("pl_evidence"))
    if pl_evidence:
        containers.append(("pl_evidence", pl_evidence))
    return containers


def _trade_collection(value: Any, anchor: Mapping[str, str]) -> list[dict[str, Any]]:
    if isinstance(value, Mapping):
        items = [value]
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        items = [item for item in value if isinstance(item, Mapping)]
    else:
        items = []
    return [
        sanitized
        for item in items
        if (sanitized := _sanitize_trade(item, anchor))
    ]


def _sanitize_trade(
    item: Mapping[str, Any],
    anchor: Mapping[str, str],
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    _copy_first_present(output, item, "trade_id", "trade_id", "tradeID", "tradeId")
    _copy_first_present(output, item, "tradeID", "tradeID", "tradeId")
    _copy_first_present(output, item, "id", "id")
    _copy_first_present(output, item, "instrument", "instrument")
    _copy_first_present(output, item, "currentUnits", "currentUnits", "current_units")
    _copy_first_present(output, item, "units", "units")
    _copy_first_present(output, item, "state", "state")
    _copy_first_present(output, item, "closeTime", "closeTime", "close_time")
    _copy_first_present(output, item, "realizedPL", "realizedPL", "realized_pl")
    _copy_first_present(output, item, "realized_pl", "realized_pl")
    _copy_first_present(output, item, "unrealizedPL", "unrealizedPL", "unrealized_pl")
    _copy_first_present(output, item, "unrealized_pl", "unrealized_pl")

    status_text = _text(item.get("status")).upper()
    if item.get("is_closed") is True or status_text.startswith("CLOSED"):
        output.setdefault("state", "CLOSED")
        output.setdefault("currentUnits", "0")
    if item.get("is_open") is True:
        output.setdefault("currentUnits", anchor["expected_units"])

    tp_id = _nested_order_id(item.get("takeProfitOrder"))
    tp_id = tp_id or _text(item.get("matched_take_profit_order_id"))
    if tp_id:
        output["takeProfitOrder"] = {"id": tp_id}
    sl_id = _nested_order_id(item.get("stopLossOrder"))
    sl_id = sl_id or _text(item.get("matched_stop_loss_order_id"))
    if sl_id:
        output["stopLossOrder"] = {"id": sl_id}
    return output


def _transaction_collection(
    value: Any,
    anchor: Mapping[str, str],
) -> list[dict[str, Any]]:
    if isinstance(value, Mapping):
        items = [value]
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        items = [item for item in value if isinstance(item, Mapping)]
    else:
        items = []
    return [
        sanitized
        for item in items
        if (sanitized := _sanitize_transaction(item, anchor))
    ]


def _sanitize_transaction(
    item: Mapping[str, Any],
    anchor: Mapping[str, str],
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    _copy_first_present(output, item, "id", "id")
    _copy_first_present(output, item, "orderID", "orderID", "order_id")
    _copy_first_present(output, item, "order_id", "order_id")
    _copy_first_present(output, item, "reason", "reason")
    _copy_first_present(output, item, "type", "type")
    _copy_first_present(output, item, "realizedPL", "realizedPL", "realized_pl", "pl")
    _copy_first_present(output, item, "realized_pl", "realized_pl")
    trades_closed = _trade_collection(
        _first_present(item, "tradesClosed", "tradeClosed"),
        anchor,
    )
    if trades_closed:
        output["tradesClosed"] = trades_closed
    return output


def _closed_trades_from_transactions(
    transactions: Sequence[Mapping[str, Any]],
    anchor: Mapping[str, str],
) -> list[dict[str, Any]]:
    closed_trades: list[dict[str, Any]] = []
    for tx in transactions:
        if _first_present(tx, *REALIZED_PL_KEYS) is not None:
            continue
        order_id = _text(_first_present(tx, "orderID", "order_id", "id"))
        reason = _text(tx.get("reason")).upper()
        for closed in _trade_collection(tx.get("tradesClosed"), anchor):
            if not _node_matches_trade_id(closed, anchor["trade_id"]):
                continue
            closed.setdefault("state", "CLOSED")
            closed.setdefault("currentUnits", "0")
            if order_id == anchor["take_profit_order_id"] or "TAKE_PROFIT" in reason:
                closed.setdefault("takeProfitOrder", {"id": anchor["take_profit_order_id"]})
            if order_id == anchor["stop_loss_order_id"] or "STOP_LOSS" in reason:
                closed.setdefault("stopLossOrder", {"id": anchor["stop_loss_order_id"]})
            closed_trades.append(closed)
    return closed_trades


def _unsafe_input_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for raw_key, value in node.items():
                key = _normalized_key(raw_key)
                if key in UNSAFE_TRUE_FIELDS and _truthy_unsafe(value):
                    blockers.append(f"unsafe_{label}_{key}_true")
                if _raw_payload_key(key) and _present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _request_header_key(key) and _present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _endpoint_url_key(key) and LIVE_OANDA_HOST in _text(value):
                    blockers.append(f"unsafe_{label}_live_endpoint_url_present")
                if _sensitive_key(key) and _sensitive_value_present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                visit(value)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _dropped_input_field_paths(payload: Mapping[str, Any]) -> list[str]:
    paths: list[str] = []

    def visit(node: Any, prefix: str) -> None:
        if isinstance(node, Mapping):
            for raw_key, value in node.items():
                key = _normalized_key(raw_key)
                path = f"{prefix}.{raw_key}" if prefix else str(raw_key)
                if (
                    _endpoint_url_key(key)
                    or key
                    in {
                        "read_only_endpoint_plan",
                        "read_only_capture_results",
                        "sanitized_vault_load_result",
                        "response",
                        "body",
                        "json",
                        "payload",
                    }
                    or _raw_payload_key(key)
                    or _request_header_key(key)
                ):
                    paths.append(path)
                visit(value, path)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for index, child in enumerate(node):
                visit(child, f"{prefix}[{index}]")

    visit(payload, "")
    return _unique(paths)


def _warnings(adapter_status: str) -> list[str]:
    warnings = [
        "adapter_only_not_broker_caller",
        "adapter_only_not_order_closer",
        "adapter_only_not_order_mutator",
        "adapter_only_not_bucket_updater",
        "adapter_only_not_scheduler_or_daemon",
        "sanitized_capture_input_only",
        "no_oanda_call_performed_by_adapter",
        "no_vault_env_or_credential_read_by_adapter",
        "no_raw_payload_persistence",
        "no_new_order_authorized",
        "open_unrealized_pl_is_not_profit_claim",
    ]
    if adapter_status == ADAPTED_BLOCKED_UNSAFE_EVIDENCE:
        warnings.append("adapter_blocked_before_classifier")
    if adapter_status.startswith("ADAPTED_CLOSED"):
        warnings.append("closed_result_requires_owner_review_before_bucket_or_next_order")
    return warnings


def _next_safe_action(adapter_status: str) -> str:
    if adapter_status == ADAPTED_STILL_OPEN_NO_REALIZED_RESULT:
        return "continue_read_only_monitoring_no_order_no_bucket_update"
    if adapter_status in {
        ADAPTED_CLOSED_BY_TAKE_PROFIT,
        ADAPTED_CLOSED_BY_STOP_LOSS,
        ADAPTED_CLOSED_BY_OTHER_OR_MANUAL,
        ADAPTED_CLOSED_REALIZED_PROFIT_OTHER,
        ADAPTED_CLOSED_REALIZED_LOSS_OTHER,
        ADAPTED_CLOSED_BREAKEVEN_OTHER,
    }:
        return "owner_review_classifier_result_before_bucket_update_or_next_order"
    if adapter_status == ADAPTED_TRADE_NOT_FOUND:
        return "provide_sanitized_closed_trade_or_transaction_evidence_for_trade_328"
    if adapter_status == ADAPTED_BLOCKED_UNSAFE_EVIDENCE:
        return "remove_unsafe_authority_or_sensitive_runtime_fields_before_adapter"
    return "repair_sanitized_capture_shape_before_adapter"


def _normalize_anchor(anchor: Mapping[str, Any] | None) -> dict[str, str]:
    source = _mapping(anchor)
    normalized = dict(DEFAULT_TRADE_ANCHOR)
    for key in DEFAULT_TRADE_ANCHOR:
        value = _text(source.get(key))
        if value:
            normalized[key] = value
    return normalized


def _empty_evidence_summary(*, rejected_before_classifier: bool) -> dict[str, Any]:
    return {
        "sanitized_input_only": not rejected_before_classifier,
        "classifier_evidence_built": False,
        "rejected_before_classifier": rejected_before_classifier,
        "source_paths": [],
        "open_trade_evidence_count": 0,
        "closed_trade_evidence_count": 0,
        "trade_evidence_count": 0,
        "transaction_evidence_count": 0,
        "realized_pl_value_count": 0,
        "realized_pl_total_present": False,
        "account_summary_snapshot_present": False,
        "account_summary_snapshot_paths": [],
        "dropped_input_field_count": 0,
        "dropped_input_field_paths": [],
        "raw_broker_payload_persisted": False,
        "broker_or_network_call_performed_here": False,
        "adapter_only_not_broker_caller": True,
    }


def _safe_capture(payload: Mapping[str, Any]) -> dict[str, Any]:
    capture = dict(payload)
    capture["execution_authority"] = _execution_authority()
    capture["safety_proof"] = _safety_proof()
    capture.update(_safety_proof())
    return capture


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _safety_proof() -> dict[str, bool]:
    return {field: False for field in SAFETY_PROOF_FIELDS}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_present(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _copy_first_present(
    output: dict[str, Any],
    source: Mapping[str, Any],
    target_key: str,
    *source_keys: str,
) -> None:
    value = _first_present(source, *source_keys)
    if value is not None and _safe_scalar(value):
        output[target_key] = str(value)


def _safe_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, float, Decimal)) and not isinstance(value, bool)


def _nested_order_id(value: Any) -> str:
    if isinstance(value, Mapping):
        return _text(value.get("id") or value.get("orderID") or value.get("order_id"))
    return _text(value)


def _append_source_path(
    paths: list[str],
    prefix: str,
    key: str,
    value: Any,
) -> None:
    if isinstance(value, Mapping):
        paths.append(f"{prefix}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and value:
        paths.append(f"{prefix}.{key}")


def _looks_trade_like(value: Mapping[str, Any]) -> bool:
    return any(key in value for key in TRADE_ID_KEYS + UNIT_KEYS + REALIZED_PL_KEYS) or any(
        key in value
        for key in (
            "is_open",
            "is_closed",
            "status",
            "closeTime",
            "close_time",
            "takeProfitOrder",
            "stopLossOrder",
            "matched_take_profit_order_id",
            "matched_stop_loss_order_id",
        )
    )


def _looks_transaction_like(value: Mapping[str, Any]) -> bool:
    return any(
        key in value
        for key in (
            "id",
            "orderID",
            "order_id",
            "reason",
            "type",
            "tradesClosed",
            "tradeClosed",
        )
    )


def _node_matches_trade_id(node: Any, trade_id: str) -> bool:
    if isinstance(node, Mapping):
        for key, value in node.items():
            if str(key) in TRADE_ID_KEYS and _text(value) == trade_id:
                return True
            if _node_matches_trade_id(value, trade_id):
                return True
    elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        return any(_node_matches_trade_id(child, trade_id) for child in node)
    return False


def _decimal_text_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    output: list[str] = []
    for item in value:
        text = _decimal_text_or_none(item)
        if text is not None:
            output.append(text)
    return output


def _decimal_text_or_none(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not decimal_value.is_finite():
        return None
    return format(decimal_value, "f")


def _dedupe_mappings(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for item in items:
        signature = repr(sorted(_flatten_for_signature(item)))
        if signature in seen:
            continue
        seen.add(signature)
        output.append(dict(item))
    return output


def _flatten_for_signature(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    if isinstance(value, Mapping):
        pairs: list[tuple[str, str]] = []
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            pairs.extend(_flatten_for_signature(child, child_prefix))
        return pairs
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        pairs = []
        for index, child in enumerate(value):
            pairs.extend(_flatten_for_signature(child, f"{prefix}[{index}]"))
        return pairs
    return [(prefix, _text(value))]


def _raw_payload_key(key: str) -> bool:
    return any(term in key for term in RAW_PAYLOAD_KEY_TERMS)


def _request_header_key(key: str) -> bool:
    return key in REQUEST_HEADER_KEY_TERMS


def _endpoint_url_key(key: str) -> bool:
    return key in ENDPOINT_URL_KEY_TERMS or key.endswith("_url")


def _sensitive_key(key: str) -> bool:
    if key in SENSITIVE_KEY_EXEMPTIONS:
        return False
    return key in SENSITIVE_VALUE_KEYS or any(term in key for term in SENSITIVE_KEY_TERMS)


def _sensitive_value_present(value: Any) -> bool:
    if value in (None, False):
        return False
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        upper = text.upper()
        return "REDACTED" not in upper and "SANITIZED" not in upper
    return True


def _truthy_unsafe(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "1",
            "allowed",
            "performed",
            "enabled",
            "started",
            "called",
            "authorized",
        }
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 1
    return False


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _string_items(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return []


def _normalized_key(value: Any) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output
