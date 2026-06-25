from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


PACKET_ID = "AIOS-FOREX-OANDA-CLOSED-TRADE-TPSL-RESULT-CAPTURE-V1"
CAPTURE_VERSION = "v1"

STILL_OPEN_NO_REALIZED_RESULT = "STILL_OPEN_NO_REALIZED_RESULT"
CLOSED_BY_TAKE_PROFIT = "CLOSED_BY_TAKE_PROFIT"
CLOSED_BY_STOP_LOSS = "CLOSED_BY_STOP_LOSS"
CLOSED_BY_OTHER_OR_MANUAL = "CLOSED_BY_OTHER_OR_MANUAL"
CLOSED_REALIZED_PROFIT_OTHER = "CLOSED_REALIZED_PROFIT_OTHER"
CLOSED_REALIZED_LOSS_OTHER = "CLOSED_REALIZED_LOSS_OTHER"
CLOSED_BREAKEVEN_OTHER = "CLOSED_BREAKEVEN_OTHER"
TRADE_NOT_FOUND = "TRADE_NOT_FOUND"
BLOCKED_UNSAFE_EVIDENCE = "BLOCKED_UNSAFE_EVIDENCE"
BLOCKED_INVALID_EVIDENCE = "BLOCKED_INVALID_EVIDENCE"

DEFAULT_TRADE_ANCHOR: dict[str, str] = {
    "trade_id": "328",
    "instrument": "EUR_USD",
    "entry_open_price": "1.13689",
    "take_profit_order_id": "329",
    "stop_loss_order_id": "330",
    "expected_units": "1",
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
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
}

OPEN_TRADE_KEYS = ("open_trade_evidence",)
CLOSED_TRADE_KEYS = ("closed_trade_evidence",)
TRADE_EVIDENCE_KEYS = ("trade_evidence",)
TRANSACTION_KEYS = ("transactions",)
REALIZED_PL_KEYS = ("realized_pl", "realizedPL", "pl", "profitLoss")
UNREALIZED_PL_KEYS = ("unrealized_pl", "unrealizedPL", "trueUnrealizedPL")
UNIT_KEYS = ("currentUnits", "current_units", "units")
TRADE_ID_KEYS = ("trade_id", "tradeID", "tradeId", "id")


def evaluate_oanda_closed_trade_tpsl_result_capture_v1(
    read_only_trade_result_evidence: dict[str, Any] | Mapping[str, Any] | None,
    trade_anchor: dict[str, Any] | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    anchor = _normalize_anchor(trade_anchor)
    evidence = _mapping(read_only_trade_result_evidence)

    if read_only_trade_result_evidence is not None and not isinstance(
        read_only_trade_result_evidence,
        Mapping,
    ):
        return _decision(
            anchor=anchor,
            status=BLOCKED_INVALID_EVIDENCE,
            blockers=["read_only_trade_result_evidence_must_be_mapping"],
            warnings=[],
            is_open=False,
            is_closed=False,
            close_reason="input_not_mapping",
            realized_pl=None,
            unrealized_pl=None,
            source_summary=_empty_source_summary(),
        )

    unsafe_blockers = _unsafe_input_blockers(evidence, "read_only_trade_result_evidence")
    unsafe_blockers.extend(_unsafe_input_blockers(anchor, "trade_anchor"))
    if unsafe_blockers:
        return _decision(
            anchor=anchor,
            status=BLOCKED_UNSAFE_EVIDENCE,
            blockers=_unique(unsafe_blockers),
            warnings=["unsafe_authority_or_sensitive_runtime_field_present"],
            is_open=False,
            is_closed=False,
            close_reason="unsafe_evidence_rejected_before_classification",
            realized_pl=None,
            unrealized_pl=None,
            source_summary=_source_summary(
                _extract_sources(evidence),
                realized_pl_source=None,
                realized_values=[],
            ),
        )

    sources = _extract_sources(evidence)
    open_matches = _matching_open_trades(sources["open_trade_evidence"], anchor)
    open_match = open_matches[0] if open_matches else None
    closed_candidates = _matching_closed_candidates(sources, anchor)
    realized_pl, realized_source, realized_values = _realized_pl(
        evidence,
        sources,
        anchor,
    )
    unrealized_pl = _unrealized_pl(open_match, evidence)
    tp_match = _order_match(sources, anchor, order_kind="take_profit")
    sl_match = _order_match(sources, anchor, order_kind="stop_loss")
    source_summary = _source_summary(
        sources,
        realized_pl_source=realized_source,
        realized_values=realized_values,
    )
    source_summary["open_trade_match_count"] = len(open_matches)
    source_summary["closed_trade_match_count"] = len(closed_candidates)
    source_summary["take_profit_evidence_paths"] = tp_match["paths"]
    source_summary["stop_loss_evidence_paths"] = sl_match["paths"]

    if open_match is not None:
        return _decision(
            anchor=anchor,
            status=STILL_OPEN_NO_REALIZED_RESULT,
            blockers=[],
            warnings=["open_unrealized_pl_is_not_profit_claim"],
            is_open=True,
            is_closed=False,
            close_reason="trade_328_present_in_open_trade_evidence_with_nonzero_units",
            matched_take_profit_order_id=None,
            matched_stop_loss_order_id=None,
            realized_pl=None,
            unrealized_pl=unrealized_pl,
            source_summary=source_summary,
        )

    is_closed = _is_closed_trade(sources, anchor, closed_candidates, realized_pl)
    if not is_closed and not _has_any_trade_or_transaction_evidence(sources):
        return _decision(
            anchor=anchor,
            status=TRADE_NOT_FOUND,
            blockers=["trade_328_not_found_in_sanitized_evidence"],
            warnings=[],
            is_open=False,
            is_closed=False,
            close_reason="no_matching_open_closed_or_transaction_evidence",
            realized_pl=None,
            unrealized_pl=unrealized_pl,
            source_summary=source_summary,
        )
    if not is_closed:
        return _decision(
            anchor=anchor,
            status=TRADE_NOT_FOUND,
            blockers=["trade_328_not_found_as_open_or_closed"],
            warnings=[],
            is_open=False,
            is_closed=False,
            close_reason="matching_trade_not_resolved_from_sanitized_evidence",
            realized_pl=realized_pl,
            unrealized_pl=unrealized_pl,
            source_summary=source_summary,
        )

    if tp_match["matched"] and sl_match["matched"]:
        explicit_tp = tp_match["explicit"]
        explicit_sl = sl_match["explicit"]
        if explicit_tp and not explicit_sl:
            sl_match = _empty_order_match()
        elif explicit_sl and not explicit_tp:
            tp_match = _empty_order_match()
        else:
            return _decision(
                anchor=anchor,
                status=BLOCKED_INVALID_EVIDENCE,
                blockers=["conflicting_take_profit_and_stop_loss_order_match"],
                warnings=["closed_trade_has_conflicting_tpsl_evidence"],
                is_open=False,
                is_closed=True,
                close_reason="both_take_profit_329_and_stop_loss_330_matched",
                matched_take_profit_order_id=anchor["take_profit_order_id"],
                matched_stop_loss_order_id=anchor["stop_loss_order_id"],
                realized_pl=realized_pl,
                unrealized_pl=unrealized_pl,
                source_summary=source_summary,
            )

    if tp_match["matched"]:
        return _decision(
            anchor=anchor,
            status=CLOSED_BY_TAKE_PROFIT,
            blockers=[],
            warnings=[],
            is_open=False,
            is_closed=True,
            close_reason="take_profit_order_329_matched_in_closed_evidence",
            matched_take_profit_order_id=anchor["take_profit_order_id"],
            matched_stop_loss_order_id=None,
            realized_pl=realized_pl,
            unrealized_pl=unrealized_pl,
            source_summary=source_summary,
        )

    if sl_match["matched"]:
        return _decision(
            anchor=anchor,
            status=CLOSED_BY_STOP_LOSS,
            blockers=[],
            warnings=[],
            is_open=False,
            is_closed=True,
            close_reason="stop_loss_order_330_matched_in_closed_evidence",
            matched_take_profit_order_id=None,
            matched_stop_loss_order_id=anchor["stop_loss_order_id"],
            realized_pl=realized_pl,
            unrealized_pl=unrealized_pl,
            source_summary=source_summary,
        )

    if realized_pl is None:
        return _decision(
            anchor=anchor,
            status=CLOSED_BY_OTHER_OR_MANUAL,
            blockers=[],
            warnings=["closed_trade_realized_pl_not_present"],
            is_open=False,
            is_closed=True,
            close_reason="closed_without_tpsl_match_or_realized_pl",
            realized_pl=None,
            unrealized_pl=unrealized_pl,
            source_summary=source_summary,
        )

    if realized_pl > 0:
        status = CLOSED_REALIZED_PROFIT_OTHER
        reason = "closed_other_or_manual_positive_realized_pl"
    elif realized_pl < 0:
        status = CLOSED_REALIZED_LOSS_OTHER
        reason = "closed_other_or_manual_negative_realized_pl"
    else:
        status = CLOSED_BREAKEVEN_OTHER
        reason = "closed_other_or_manual_zero_realized_pl"

    return _decision(
        anchor=anchor,
        status=status,
        blockers=[],
        warnings=[],
        is_open=False,
        is_closed=True,
        close_reason=reason,
        realized_pl=realized_pl,
        unrealized_pl=unrealized_pl,
        source_summary=source_summary,
    )


def default_trade_anchor_v1() -> dict[str, str]:
    return dict(DEFAULT_TRADE_ANCHOR)


def oanda_closed_trade_tpsl_result_capture_template_v1() -> dict[str, Any]:
    return {
        "trade_anchor": default_trade_anchor_v1(),
        "read_only_trade_result_evidence": {
            "open_trade_evidence": [],
            "closed_trade_evidence": [],
            "trade_evidence": {},
            "transactions": [],
            "pl_evidence": {
                "open_trade_evidence": [],
                "realized_pl_values": [],
                "realized_pl_total": None,
            },
            "execution_authority": _execution_authority(),
            "safety_proof": _safety_proof(),
        },
        "template_only": True,
        "broker_network_call_performed": False,
        "credential_read_performed": False,
        "order_placement_performed": False,
        "order_close_performed": False,
        "bucket_update_performed": False,
    }


def oanda_closed_trade_tpsl_result_capture_default_samples_v1() -> dict[str, dict[str, Any]]:
    return {
        "still_open_trade_328": _safe_evidence(
            {
                "open_trade_evidence": [
                    {
                        "id": "328",
                        "instrument": "EUR_USD",
                        "currentUnits": "1",
                        "unrealizedPL": "0.0004",
                        "takeProfitOrder": {"id": "329"},
                        "stopLossOrder": {"id": "330"},
                    }
                ],
                "pl_evidence": {
                    "open_trade_evidence": [
                        {
                            "trade_id": "328",
                            "instrument": "EUR_USD",
                            "currentUnits": "1",
                            "unrealizedPL": "0.0004",
                        }
                    ],
                    "realized_pl_values": [],
                    "realized_pl_total": "0",
                },
            }
        ),
        "closed_by_tp_trade_328": _safe_evidence(
            {
                "open_trade_evidence": [],
                "closed_trade_evidence": [
                    {
                        "id": "328",
                        "instrument": "EUR_USD",
                        "state": "CLOSED",
                        "currentUnits": "0",
                        "realizedPL": "0.0012",
                        "takeProfitOrder": {"id": "329"},
                    }
                ],
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
                ],
            }
        ),
        "closed_by_sl_trade_328": _safe_evidence(
            {
                "open_trade_evidence": [],
                "closed_trade_evidence": [
                    {
                        "id": "328",
                        "instrument": "EUR_USD",
                        "state": "CLOSED",
                        "currentUnits": "0",
                        "realizedPL": "-0.0010",
                        "stopLossOrder": {"id": "330"},
                    }
                ],
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
        "closed_other_profit_trade_328": _safe_evidence(
            {
                "open_trade_evidence": [],
                "closed_trade_evidence": [
                    {
                        "tradeID": "328",
                        "instrument": "EUR_USD",
                        "state": "CLOSED",
                        "currentUnits": "0",
                        "closeTime": "SANITIZED_TIMESTAMP",
                        "realizedPL": "0.0006",
                    }
                ],
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
        "closed_other_loss_trade_328": _safe_evidence(
            {
                "open_trade_evidence": [],
                "closed_trade_evidence": [
                    {
                        "tradeID": "328",
                        "instrument": "EUR_USD",
                        "state": "CLOSED",
                        "currentUnits": "0",
                        "closeTime": "SANITIZED_TIMESTAMP",
                        "realizedPL": "-0.0006",
                    }
                ],
            }
        ),
        "breakeven_trade_328": _safe_evidence(
            {
                "open_trade_evidence": [],
                "closed_trade_evidence": [
                    {
                        "tradeID": "328",
                        "instrument": "EUR_USD",
                        "state": "CLOSED",
                        "currentUnits": "0",
                        "closeTime": "SANITIZED_TIMESTAMP",
                        "realizedPL": "0.0000",
                    }
                ],
            }
        ),
        "trade_not_found": _safe_evidence(
            {
                "open_trade_evidence": [],
                "closed_trade_evidence": [],
                "transactions": [],
                "pl_evidence": {
                    "open_trade_evidence": [],
                    "realized_pl_values": [],
                    "realized_pl_total": None,
                },
            }
        ),
    }


def _decision(
    *,
    anchor: Mapping[str, str],
    status: str,
    blockers: Sequence[str],
    warnings: Sequence[str],
    is_open: bool,
    is_closed: bool,
    close_reason: str,
    realized_pl: Decimal | None,
    unrealized_pl: Decimal | None,
    source_summary: Mapping[str, Any],
    matched_take_profit_order_id: str | None = None,
    matched_stop_loss_order_id: str | None = None,
) -> dict[str, Any]:
    profit_claimed = bool(
        is_closed
        and not blockers
        and status
        not in {
            BLOCKED_INVALID_EVIDENCE,
            BLOCKED_UNSAFE_EVIDENCE,
            TRADE_NOT_FOUND,
        }
        and realized_pl is not None
        and realized_pl > 0
    )
    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "capture_version": CAPTURE_VERSION,
        "status": status,
        "blockers": list(blockers),
        "warnings": list(warnings),
        "trade_id": anchor["trade_id"],
        "instrument": anchor["instrument"],
        "is_open": is_open,
        "is_closed": is_closed,
        "close_classification": status,
        "close_reason": close_reason,
        "matched_take_profit_order_id": matched_take_profit_order_id,
        "matched_stop_loss_order_id": matched_stop_loss_order_id,
        "realized_pl": _decimal_text(realized_pl) if realized_pl is not None else None,
        "unrealized_pl": _decimal_text(unrealized_pl)
        if unrealized_pl is not None
        else None,
        "profit_claimed": profit_claimed,
        "no_new_order_authorized": True,
        "no_bucket_update_performed": True,
        "source_evidence_summary": dict(source_summary),
        "safety_proof": _safety_proof(),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }
    result.update(_safety_proof())
    return result


def _normalize_anchor(anchor: Mapping[str, Any] | None) -> dict[str, str]:
    source = _mapping(anchor)
    normalized = dict(DEFAULT_TRADE_ANCHOR)
    for key in DEFAULT_TRADE_ANCHOR:
        value = _text(source.get(key))
        if value:
            normalized[key] = value
    return normalized


def _extract_sources(evidence: Mapping[str, Any]) -> dict[str, Any]:
    sources = {
        "open_trade_evidence": [],
        "closed_trade_evidence": [],
        "trade_evidence": [],
        "transactions": [],
        "source_paths": [],
    }

    containers: list[tuple[str, Mapping[str, Any]]] = [("root", evidence)]
    pl_evidence = _mapping(evidence.get("pl_evidence"))
    if pl_evidence:
        containers.append(("pl_evidence", pl_evidence))
    decision = _mapping(evidence.get("decision"))
    if decision:
        containers.append(("decision", decision))
        decision_pl_evidence = _mapping(decision.get("pl_evidence"))
        if decision_pl_evidence:
            containers.append(("decision.pl_evidence", decision_pl_evidence))

    for prefix, container in containers:
        _append_collection(
            sources,
            "open_trade_evidence",
            prefix,
            container,
            OPEN_TRADE_KEYS,
        )
        _append_collection(
            sources,
            "closed_trade_evidence",
            prefix,
            container,
            CLOSED_TRADE_KEYS,
        )
        _append_collection(
            sources,
            "trade_evidence",
            prefix,
            container,
            TRADE_EVIDENCE_KEYS,
        )
        _append_collection(
            sources,
            "transactions",
            prefix,
            container,
            TRANSACTION_KEYS,
        )
        transaction_match = container.get("transaction_match")
        if transaction_match is not None:
            _append_value(
                sources,
                "transactions",
                f"{prefix}.transaction_match",
                transaction_match,
            )

    return sources


def _append_collection(
    sources: dict[str, Any],
    target: str,
    prefix: str,
    container: Mapping[str, Any],
    keys: Sequence[str],
) -> None:
    for key in keys:
        if key in container:
            _append_value(sources, target, f"{prefix}.{key}", container.get(key))


def _append_value(
    sources: dict[str, Any],
    target: str,
    path: str,
    value: Any,
) -> None:
    items: list[Any]
    if isinstance(value, Mapping):
        items = [value]
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        items = [item for item in value if isinstance(item, Mapping)]
    else:
        items = []
    if items:
        sources[target].extend(items)
        sources["source_paths"].append(path)


def _matching_open_trades(
    open_trade_evidence: Sequence[Any],
    anchor: Mapping[str, str],
) -> list[Mapping[str, Any]]:
    matches: list[Mapping[str, Any]] = []
    for item in open_trade_evidence:
        if not isinstance(item, Mapping):
            continue
        if not _trade_id_matches(item, anchor["trade_id"]):
            continue
        if not _instrument_matches(item, anchor["instrument"]):
            continue
        units = _first_decimal(item, UNIT_KEYS)
        if units is not None and units != 0:
            matches.append(item)
    return matches


def _matching_closed_candidates(
    sources: Mapping[str, Any],
    anchor: Mapping[str, str],
) -> list[Mapping[str, Any]]:
    matches: list[Mapping[str, Any]] = []
    for group in (
        sources.get("closed_trade_evidence", []),
        sources.get("trade_evidence", []),
        sources.get("transactions", []),
    ):
        for item in group if isinstance(group, Sequence) else []:
            if isinstance(item, Mapping) and _node_matches_trade_id(
                item,
                anchor["trade_id"],
            ):
                matches.append(item)
    return matches


def _is_closed_trade(
    sources: Mapping[str, Any],
    anchor: Mapping[str, str],
    closed_candidates: Sequence[Mapping[str, Any]],
    realized_pl: Decimal | None,
) -> bool:
    for item in closed_candidates:
        if _explicit_closed(item):
            return True
    if realized_pl is not None and (
        closed_candidates
        or _empty_or_absent_open_trade_evidence_for_trade(sources, anchor)
    ):
        return True
    return False


def _explicit_closed(item: Mapping[str, Any]) -> bool:
    if _bool_or_none(item.get("is_closed")) is True:
        return True
    if _text(item.get("state")).upper() == "CLOSED":
        return True
    units = _first_decimal(item, UNIT_KEYS)
    if units is not None and units == 0:
        return True
    if _text(item.get("closeTime")) or _text(item.get("close_time")):
        return True
    if _contains_key(item, "tradeClosed") or _contains_key(item, "tradesClosed"):
        return True
    return False


def _empty_or_absent_open_trade_evidence_for_trade(
    sources: Mapping[str, Any],
    anchor: Mapping[str, str],
) -> bool:
    open_items = sources.get("open_trade_evidence", [])
    if not isinstance(open_items, Sequence) or isinstance(open_items, (str, bytes)):
        return True
    return not _matching_open_trades(open_items, anchor)


def _realized_pl(
    evidence: Mapping[str, Any],
    sources: Mapping[str, Any],
    anchor: Mapping[str, str],
) -> tuple[Decimal | None, str | None, list[str]]:
    explicit = _first_decimal(evidence, ("realized_pl", "realizedPL"))
    if explicit is not None:
        return explicit, "root.realized_pl", [_decimal_text(explicit)]

    decision = _mapping(evidence.get("decision"))
    decision_explicit = _first_decimal(decision, ("realized_pl", "realizedPL"))
    if decision_explicit is not None:
        return decision_explicit, "decision.realized_pl", [_decimal_text(decision_explicit)]

    for label, container in (
        ("pl_evidence", _mapping(evidence.get("pl_evidence"))),
        ("decision.pl_evidence", _mapping(decision.get("pl_evidence"))),
    ):
        total = _decimal_or_none(container.get("realized_pl_total"))
        if total is not None:
            return total, f"{label}.realized_pl_total", [_decimal_text(total)]
        values = _decimal_sequence(container.get("realized_pl_values"))
        if values:
            return sum(values, Decimal("0")), f"{label}.realized_pl_values", [
                _decimal_text(value) for value in values
            ]

    matched_values: list[Decimal] = []
    for item in _matching_closed_candidates(sources, anchor):
        value = _first_decimal(item, REALIZED_PL_KEYS)
        if value is not None:
            matched_values.append(value)
    if matched_values:
        return sum(matched_values, Decimal("0")), "matched_closed_or_transaction_evidence", [
            _decimal_text(value) for value in matched_values
        ]
    return None, None, []


def _unrealized_pl(
    open_match: Mapping[str, Any] | None,
    evidence: Mapping[str, Any],
) -> Decimal | None:
    if open_match is not None:
        value = _first_decimal(open_match, UNREALIZED_PL_KEYS)
        if value is not None:
            return value
    return _first_decimal(evidence, UNREALIZED_PL_KEYS)


def _order_match(
    sources: Mapping[str, Any],
    anchor: Mapping[str, str],
    *,
    order_kind: str,
) -> dict[str, Any]:
    order_id = (
        anchor["take_profit_order_id"]
        if order_kind == "take_profit"
        else anchor["stop_loss_order_id"]
    )
    reason_terms = (
        ("TAKE_PROFIT", "TAKEPROFIT")
        if order_kind == "take_profit"
        else ("STOP_LOSS", "STOPLOSS")
    )
    label_terms = (
        ("takeProfitOrder", "take_profit_order", "takeprofit")
        if order_kind == "take_profit"
        else ("stopLossOrder", "stop_loss_order", "stoploss")
    )
    paths: list[str] = []
    explicit = False
    for group_name in ("closed_trade_evidence", "trade_evidence", "transactions"):
        group = sources.get(group_name, [])
        if not isinstance(group, Sequence) or isinstance(group, (str, bytes)):
            continue
        for index, item in enumerate(group):
            if not isinstance(item, Mapping):
                continue
            if _node_matches_order_id(item, order_id, label_terms=label_terms):
                paths.append(f"{group_name}[{index}]")
            if _node_has_order_reason(item, reason_terms):
                explicit = True
                paths.append(f"{group_name}[{index}].reason")
            if _node_has_direct_order_id(item, order_id):
                explicit = True
                paths.append(f"{group_name}[{index}].order_id")
    return {
        "matched": bool(paths),
        "explicit": explicit,
        "paths": _unique(paths),
    }


def _empty_order_match() -> dict[str, Any]:
    return {"matched": False, "explicit": False, "paths": []}


def _node_matches_order_id(
    node: Any,
    order_id: str,
    *,
    label_terms: Sequence[str],
) -> bool:
    if isinstance(node, Mapping):
        for key, value in node.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if any(term.lower() in key_lower for term in label_terms):
                if _node_contains_text(value, order_id):
                    return True
            if key_text in {"id", "orderID", "order_id", "clientOrderID"}:
                if _text(value) == order_id:
                    return True
            if _node_matches_order_id(value, order_id, label_terms=label_terms):
                return True
    elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        return any(
            _node_matches_order_id(child, order_id, label_terms=label_terms)
            for child in node
        )
    return False


def _node_has_direct_order_id(node: Any, order_id: str) -> bool:
    if isinstance(node, Mapping):
        for key, value in node.items():
            if str(key) in {"orderID", "order_id", "clientOrderID"}:
                if _text(value) == order_id:
                    return True
            if _node_has_direct_order_id(value, order_id):
                return True
    elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        return any(_node_has_direct_order_id(child, order_id) for child in node)
    return False


def _node_has_order_reason(node: Any, terms: Sequence[str]) -> bool:
    if isinstance(node, Mapping):
        for key, value in node.items():
            if str(key).lower() in {"reason", "type", "orderreason"}:
                text = _text(value).upper()
                if any(term in text for term in terms):
                    return True
            if _node_has_order_reason(value, terms):
                return True
    elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        return any(_node_has_order_reason(child, terms) for child in node)
    return False


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


def _trade_id_matches(item: Mapping[str, Any], trade_id: str) -> bool:
    return any(_text(item.get(key)) == trade_id for key in TRADE_ID_KEYS)


def _instrument_matches(item: Mapping[str, Any], instrument: str) -> bool:
    observed = _text(item.get("instrument"))
    return not observed or observed == instrument


def _has_any_trade_or_transaction_evidence(sources: Mapping[str, Any]) -> bool:
    return bool(
        sources.get("open_trade_evidence")
        or sources.get("closed_trade_evidence")
        or sources.get("trade_evidence")
        or sources.get("transactions")
    )


def _source_summary(
    sources: Mapping[str, Any],
    *,
    realized_pl_source: str | None,
    realized_values: Sequence[str],
) -> dict[str, Any]:
    return {
        "sanitized_input_only": True,
        "open_trade_evidence_count": _count(sources.get("open_trade_evidence")),
        "closed_trade_evidence_count": _count(sources.get("closed_trade_evidence")),
        "trade_evidence_count": _count(sources.get("trade_evidence")),
        "transaction_evidence_count": _count(sources.get("transactions")),
        "source_paths": list(sources.get("source_paths", [])),
        "realized_pl_source": realized_pl_source,
        "realized_pl_value_count": len(realized_values),
        "realized_pl_values": list(realized_values),
        "raw_broker_payload_persisted": False,
        "broker_or_network_call_performed_here": False,
    }


def _empty_source_summary() -> dict[str, Any]:
    return _source_summary(
        {
            "open_trade_evidence": [],
            "closed_trade_evidence": [],
            "trade_evidence": [],
            "transactions": [],
            "source_paths": [],
        },
        realized_pl_source=None,
        realized_values=[],
    )


def _unsafe_input_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            authority = _mapping(node.get("execution_authority"))
            safety = _mapping(node.get("safety_proof"))
            for raw_key, value in node.items():
                key = str(raw_key)
                if key in UNSAFE_TRUE_FIELDS and _truthy_unsafe(value):
                    blockers.append(f"unsafe_{label}_{key}_true")
                if key in SENSITIVE_VALUE_KEYS and _sensitive_value_present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                visit(value)
            for key in UNSAFE_TRUE_FIELDS:
                if _truthy_unsafe(authority.get(key)):
                    blockers.append(f"unsafe_{label}_execution_authority_{key}_true")
                if _truthy_unsafe(safety.get(key)):
                    blockers.append(f"unsafe_{label}_safety_proof_{key}_true")
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _safe_evidence(payload: Mapping[str, Any]) -> dict[str, Any]:
    evidence = dict(payload)
    evidence["execution_authority"] = _execution_authority()
    evidence["safety_proof"] = _safety_proof()
    return evidence


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _safety_proof() -> dict[str, bool]:
    return {field: False for field in SAFETY_PROOF_FIELDS}


def _next_safe_action(status: str) -> str:
    if status == STILL_OPEN_NO_REALIZED_RESULT:
        return "continue_read_only_monitoring_no_order_no_bucket_update"
    if status in {
        CLOSED_BY_TAKE_PROFIT,
        CLOSED_BY_STOP_LOSS,
        CLOSED_BY_OTHER_OR_MANUAL,
        CLOSED_REALIZED_PROFIT_OTHER,
        CLOSED_REALIZED_LOSS_OTHER,
        CLOSED_BREAKEVEN_OTHER,
    }:
        return "owner_review_closed_trade_result_before_any_bucket_update_or_next_packet"
    if status == TRADE_NOT_FOUND:
        return "provide_sanitized_closed_trade_or_transaction_evidence_for_trade_328"
    if status == BLOCKED_UNSAFE_EVIDENCE:
        return "remove_unsafe_authority_or_performed_flags_before_reclassification"
    return "repair_sanitized_evidence_shape_before_reclassification"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _count(value: Any) -> int:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return len(value)
    return 0


def _contains_key(node: Any, key: str) -> bool:
    if isinstance(node, Mapping):
        return key in node or any(_contains_key(value, key) for value in node.values())
    if isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        return any(_contains_key(child, key) for child in node)
    return False


def _node_contains_text(node: Any, text: str) -> bool:
    if isinstance(node, Mapping):
        return any(_node_contains_text(value, text) for value in node.values())
    if isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        return any(_node_contains_text(child, text) for child in node)
    return _text(node) == text


def _first_decimal(mapping: Mapping[str, Any], keys: Sequence[str]) -> Decimal | None:
    for key in keys:
        if key in mapping:
            value = _decimal_or_none(mapping.get(key))
            if value is not None:
                return value
    return None


def _decimal_sequence(value: Any) -> list[Decimal]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    output: list[Decimal] = []
    for item in value:
        decimal_value = _decimal_or_none(item)
        if decimal_value is not None:
            output.append(decimal_value)
    return output


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not decimal_value.is_finite():
        return None
    return decimal_value


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")


def _bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return None


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
        }
    return False


def _sensitive_value_present(value: Any) -> bool:
    if value in (None, False):
        return False
    if isinstance(value, str):
        text = value.strip()
        return bool(text and "REDACTED" not in text.upper())
    return True


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
