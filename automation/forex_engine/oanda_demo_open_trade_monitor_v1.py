from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-OPEN-TRADE-MONITOR-V1"
PACKET_NAME = "AIOS FOREX OANDA DEMO OPEN TRADE MONITOR V1"
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_OPEN_TRADE_MONITOR_V1_REPORT.md"
)
NEXT_RECOMMENDED_PACKET = (
    "AIOS FOREX OANDA DEMO P/L RESULT BUCKET AND REPEAT PROOF LANE V1"
)

OPEN_UNREALIZED_POSITIVE = "OPEN_UNREALIZED_POSITIVE"
OPEN_UNREALIZED_NEGATIVE = "OPEN_UNREALIZED_NEGATIVE"
OPEN_UNREALIZED_FLAT = "OPEN_UNREALIZED_FLAT"
CLOSED_TAKE_PROFIT_PROFIT = "CLOSED_TAKE_PROFIT_PROFIT"
CLOSED_STOP_LOSS_LOSS = "CLOSED_STOP_LOSS_LOSS"
CLOSED_BREAKEVEN = "CLOSED_BREAKEVEN"
CLOSED_OTHER_PROFIT = "CLOSED_OTHER_PROFIT"
CLOSED_OTHER_LOSS = "CLOSED_OTHER_LOSS"
NOT_FOUND = "NOT_FOUND"
BROKER_EVIDENCE_BLOCKED = "BROKER_EVIDENCE_BLOCKED"
INVALID_EVIDENCE = "INVALID_EVIDENCE"

STATUS_BUCKETS = (
    OPEN_UNREALIZED_POSITIVE,
    OPEN_UNREALIZED_NEGATIVE,
    OPEN_UNREALIZED_FLAT,
    CLOSED_TAKE_PROFIT_PROFIT,
    CLOSED_STOP_LOSS_LOSS,
    CLOSED_BREAKEVEN,
    CLOSED_OTHER_PROFIT,
    CLOSED_OTHER_LOSS,
    NOT_FOUND,
    BROKER_EVIDENCE_BLOCKED,
    INVALID_EVIDENCE,
)

OWNER_RUN_TRADE_320_ANCHOR_EVIDENCE: dict[str, Any] = {
    "evidence_source": "owner_packet_anchor_oanda_demo_trade_320",
    "trade_id": "320",
    "instrument": "EUR_USD",
    "state": "OPEN",
    "side": "long",
    "units": "1",
    "entry": "1.13596",
    "take_profit_order_id": "321",
    "stop_loss_order_id": "322",
    "realized_pl": "0.0000",
    "unrealized_pl": "-0.0004",
    "open_trade_count": 1,
    "open_position_count": 1,
    "order_placement_performed": False,
    "order_close_performed": False,
    "mutation_performed": False,
    "live_endpoint_used": False,
}

NUMERIC_FIELDS = {
    "entry_price",
    "current_price",
    "realized_pl",
    "unrealized_pl",
    "units",
}

BROKER_BLOCKED_TERMS = (
    "auth",
    "authorization",
    "blocked",
    "broker",
    "cloudflare",
    "credential",
    "forbidden",
    "login",
    "token",
    "unauthorized",
    "vault",
)


def classify_oanda_demo_trade_state(
    evidence: dict,
    expected_trade_id: str | int = "320",
) -> dict[str, Any]:
    expected_id = _text(expected_trade_id, "320")
    result = _base_result(expected_id, evidence if isinstance(evidence, Mapping) else {})

    if not isinstance(evidence, Mapping):
        return _invalid(result, ["evidence_must_be_mapping"])

    collection_blockers = _collection_shape_blockers(evidence)
    if collection_blockers:
        return _invalid(result, collection_blockers)

    broker_blockers = _broker_blockers(evidence)
    if broker_blockers:
        result.update(
            {
                "status_bucket": BROKER_EVIDENCE_BLOCKED,
                "blockers": broker_blockers,
                "is_broker_blocked": True,
                "notes": ["broker_or_auth_evidence_collection_blocked"],
                "next_recommended_packet": (
                    "AIOS FOREX OANDA DEMO BROKER EVIDENCE BLOCKER RECOVERY V1"
                ),
            }
        )
        return result

    open_trade = _find_trade(evidence, expected_id, mode="open")
    closed_trade = _find_trade(evidence, expected_id, mode="closed")
    if open_trade is not None and closed_trade is not None:
        return _invalid(result, ["expected_trade_appears_open_and_closed"])

    if open_trade is not None:
        return _classify_open_trade(result, open_trade)

    if closed_trade is not None:
        return _classify_closed_trade(result, closed_trade)

    if _has_valid_trade_evidence_boundary(evidence):
        result.update(
            {
                "status_bucket": NOT_FOUND,
                "blockers": [],
                "notes": ["expected_trade_absent_from_valid_open_and_closed_evidence"],
            }
        )
        return result

    return _invalid(result, ["missing_valid_open_or_closed_trade_evidence"])


def render_oanda_demo_open_trade_monitor_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = result.get("blockers")
    blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO OPEN TRADE MONITOR V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- repo_branch: {branch}",
            "- prior_proof_chain_anchor: PR #1071 finalized OANDA demo proof chain",
            (
                "- known_owner_run_trade_anchor: trade 320 EUR/USD long 1 entry "
                "1.13596 TP 321 SL 322"
            ),
            f"- current_bucket_result: {result.get('status_bucket')}",
            f"- profit_evidence: {_bool_word(result.get('is_profit_evidence'))}",
            f"- trade_open: {_bool_word(result.get('is_open'))}",
            f"- trade_closed: {_bool_word(result.get('is_closed'))}",
            f"- realized_pl: {_display(result.get('realized_pl'))}",
            f"- unrealized_pl: {_display(result.get('unrealized_pl'))}",
            f"- total_pl: {_display(result.get('total_pl'))}",
            f"- blockers: {blocker_text}",
            f"- next_packet_recommendation: {result.get('next_recommended_packet')}",
            "",
            "## Safety Statements",
            "",
            "- no new order was placed",
            "- no live trade was placed",
            "- no secrets were written",
            "- no broker state was modified by this monitor",
            "- no close, replace, TP, SL, unit, leverage, or account change was performed",
            "",
            "## Machine Result",
            "",
            f"- status_bucket: {result.get('status_bucket')}",
            f"- trade_id: {_display(result.get('trade_id'))}",
            f"- instrument: {_display(result.get('instrument'))}",
            f"- side: {_display(result.get('side'))}",
            f"- units: {_display(result.get('units'))}",
            f"- entry_price: {_display(result.get('entry_price'))}",
            f"- current_price: {_display(result.get('current_price'))}",
            f"- take_profit_order_id: {_display(result.get('take_profit_order_id'))}",
            f"- stop_loss_order_id: {_display(result.get('stop_loss_order_id'))}",
            f"- open_trade_count: {_display(result.get('open_trade_count'))}",
            f"- open_position_count: {_display(result.get('open_position_count'))}",
            f"- evidence_timestamp_utc: {_display(result.get('evidence_timestamp_utc'))}",
            f"- evidence_source: {_display(result.get('evidence_source'))}",
            "",
        ]
    )


def write_oanda_demo_open_trade_monitor_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_oanda_demo_open_trade_monitor_report(result, branch=branch),
        encoding="utf-8",
    )
    return path


def _classify_open_trade(
    result: dict[str, Any],
    trade: Mapping[str, Any],
) -> dict[str, Any]:
    hydrated, blockers = _hydrate_trade_fields(result, trade, is_open=True)
    if blockers:
        return _invalid(hydrated, blockers)

    unrealized = _decimal_or_none(hydrated.get("unrealized_pl"))
    realized = _decimal_or_none(hydrated.get("realized_pl"))
    units = _decimal_or_none(hydrated.get("units"))
    if unrealized is None:
        return _invalid(hydrated, ["open_trade_unrealized_pl_must_be_numeric"])
    if realized is None:
        return _invalid(hydrated, ["open_trade_realized_pl_must_be_numeric"])
    if units is None or units == 0:
        return _invalid(hydrated, ["open_trade_units_must_be_nonzero_numeric"])

    bucket = OPEN_UNREALIZED_FLAT
    if unrealized > 0:
        bucket = OPEN_UNREALIZED_POSITIVE
    elif unrealized < 0:
        bucket = OPEN_UNREALIZED_NEGATIVE

    total = realized + unrealized
    hydrated.update(
        {
            "status_bucket": bucket,
            "total_pl": _decimal_text(total),
            "is_profit_evidence": unrealized > 0,
            "is_open": True,
            "is_closed": False,
            "is_broker_blocked": False,
            "notes": ["open_trade_classified_from_unrealized_pl"],
            "next_recommended_packet": NEXT_RECOMMENDED_PACKET,
        }
    )
    return hydrated


def _classify_closed_trade(
    result: dict[str, Any],
    trade: Mapping[str, Any],
) -> dict[str, Any]:
    hydrated, blockers = _hydrate_trade_fields(result, trade, is_open=False)
    if blockers:
        return _invalid(hydrated, blockers)

    realized = _decimal_or_none(hydrated.get("realized_pl"))
    if realized is None:
        return _invalid(hydrated, ["closed_trade_realized_pl_must_be_numeric"])

    if realized == 0:
        bucket = CLOSED_BREAKEVEN
    elif realized > 0 and _closure_links_to_take_profit(trade, hydrated):
        bucket = CLOSED_TAKE_PROFIT_PROFIT
    elif realized < 0 and _closure_links_to_stop_loss(trade, hydrated):
        bucket = CLOSED_STOP_LOSS_LOSS
    elif realized > 0:
        bucket = CLOSED_OTHER_PROFIT
    else:
        bucket = CLOSED_OTHER_LOSS

    hydrated.update(
        {
            "status_bucket": bucket,
            "unrealized_pl": hydrated.get("unrealized_pl"),
            "total_pl": _decimal_text(realized),
            "is_profit_evidence": realized > 0,
            "is_open": False,
            "is_closed": True,
            "is_broker_blocked": False,
            "notes": ["closed_trade_classified_from_realized_pl"],
            "next_recommended_packet": NEXT_RECOMMENDED_PACKET,
        }
    )
    return hydrated


def _hydrate_trade_fields(
    result: dict[str, Any],
    trade: Mapping[str, Any],
    *,
    is_open: bool,
) -> tuple[dict[str, Any], list[str]]:
    blockers: list[str] = []
    units = _decimal_field(trade, ("units", "currentUnits", "current_units"), "units", blockers)
    realized = _decimal_field(
        trade,
        ("realized_pl", "realizedPL", "pl", "profitLoss"),
        "realized_pl",
        blockers,
        required=not is_open,
    )
    unrealized = _decimal_field(
        trade,
        ("unrealized_pl", "unrealizedPL", "trueUnrealizedPL"),
        "unrealized_pl",
        blockers,
        required=is_open,
    )
    entry = _decimal_field(
        trade,
        ("entry_price", "entry", "price", "open_price"),
        "entry_price",
        blockers,
        required=is_open,
    )
    current = _decimal_field(
        trade,
        ("current_price", "currentPrice", "current_price_snapshot"),
        "current_price",
        blockers,
        required=False,
    )

    result.update(
        {
            "trade_id": _first_text(trade, ("trade_id", "tradeID", "id"), result["trade_id"]),
            "instrument": _first_text(trade, ("instrument", "pair"), None),
            "side": _side_from_trade(trade, units),
            "units": _decimal_text(units) if units is not None else None,
            "entry_price": _decimal_text(entry) if entry is not None else None,
            "current_price": _decimal_text(current) if current is not None else None,
            "realized_pl": _decimal_text(realized) if realized is not None else None,
            "unrealized_pl": _decimal_text(unrealized) if unrealized is not None else None,
            "take_profit_order_id": _first_text(
                trade,
                ("take_profit_order_id", "takeProfitOrderID", "takeProfitOrderId"),
                None,
            ),
            "stop_loss_order_id": _first_text(
                trade,
                ("stop_loss_order_id", "stopLossOrderID", "stopLossOrderId"),
                None,
            ),
        }
    )

    if not result["instrument"]:
        blockers.append("trade_instrument_required")
    if is_open and result["entry_price"] is None:
        blockers.append("open_trade_entry_price_required")
    return result, _unique(blockers)


def _find_trade(
    evidence: Mapping[str, Any],
    expected_trade_id: str,
    *,
    mode: str,
) -> Mapping[str, Any] | None:
    matches: list[Mapping[str, Any]] = []
    for node, path in _iter_mappings(evidence):
        if _candidate_trade_id(node) != expected_trade_id:
            continue
        if mode == "open" and _is_open_candidate(node, path):
            matches.append(node)
        if mode == "closed" and _is_closed_candidate(node, path):
            matches.append(node)
    return matches[0] if matches else None


def _iter_mappings(
    value: Any,
    path: tuple[str, ...] = (),
) -> list[tuple[Mapping[str, Any], tuple[str, ...]]]:
    found: list[tuple[Mapping[str, Any], tuple[str, ...]]] = []
    if isinstance(value, Mapping):
        found.append((value, path))
        for key, child in value.items():
            child_path = path + (str(key),)
            found.extend(_iter_mappings(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_iter_mappings(child, path + (str(index),)))
    return found


def _candidate_trade_id(node: Mapping[str, Any]) -> str | None:
    for key in (
        "trade_id",
        "tradeID",
        "tradeId",
        "id",
        "orderFillTransaction_id",
        "order_fill_transaction_id",
    ):
        value = node.get(key)
        if value is not None:
            return _text(value)
    return None


def _is_open_candidate(node: Mapping[str, Any], path: tuple[str, ...]) -> bool:
    state = _first_text(node, ("state", "status", "trade_state"), "").upper()
    path_text = "/".join(path).lower()
    if state in {"OPEN", "FILLED_OPEN"}:
        return True
    if "open" in path_text and ("trade" in path_text or "trades" in path_text):
        return True
    units = _decimal_or_none(
        _first_present(node, ("currentUnits", "current_units", "units"))
    )
    has_unrealized = _first_present(
        node,
        ("unrealized_pl", "unrealizedPL", "trueUnrealizedPL"),
    ) is not None
    return units is not None and units != 0 and has_unrealized and state != "CLOSED"


def _is_closed_candidate(node: Mapping[str, Any], path: tuple[str, ...]) -> bool:
    state = _first_text(node, ("state", "status", "trade_state"), "").upper()
    path_text = "/".join(path).lower()
    if state in {"CLOSED", "FILLED_CLOSED"}:
        return True
    if "closed" in path_text and ("trade" in path_text or "trades" in path_text):
        return True
    if _first_present(
        node,
        (
            "close_reason",
            "closure_reason",
            "closingTransactionID",
            "tradeClosed",
            "tradesClosed",
        ),
    ) is not None:
        return True
    return False


def _collection_shape_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    collection_keys = {
        "open_trade",
        "open_trades",
        "openTrades",
        "closed_trade",
        "closed_trades",
        "closedTrades",
        "transactions",
        "trades",
    }
    for key, value in evidence.items():
        if key not in collection_keys:
            continue
        if isinstance(value, (Mapping, list)):
            continue
        blockers.append(f"{key}_collection_must_be_mapping_or_list")
    return blockers


def _broker_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if evidence.get("status_bucket") == BROKER_EVIDENCE_BLOCKED:
        blockers.append("evidence_status_bucket_broker_blocked")
    if evidence.get("is_broker_blocked") is True or evidence.get("broker_evidence_blocked") is True:
        blockers.append("broker_evidence_blocked_true")

    status_text = " ".join(
        _text(evidence.get(key))
        for key in ("status", "evidence_status", "script_status", "error", "error_type")
        if evidence.get(key) is not None
    ).lower()
    if "blocked" in status_text and _contains_broker_blocked_term(status_text):
        blockers.append("evidence_status_indicates_broker_blocked")

    raw_blockers = evidence.get("blockers", [])
    if isinstance(raw_blockers, str):
        raw_blockers = [raw_blockers]
    if isinstance(raw_blockers, list):
        for blocker in raw_blockers:
            blocker_text = _text(blocker).lower()
            if _contains_broker_blocked_term(blocker_text):
                blockers.append(f"broker_blocker_{_safe_blocker_name(blocker_text)}")

    for key, value in evidence.items():
        key_text = str(key).lower()
        if key_text.endswith("status_code") or key_text in {"status_code", "status"}:
            if _text(value) in {"401", "403"}:
                blockers.append(f"{key_text}_auth_or_forbidden")

    return _unique(blockers)


def _contains_broker_blocked_term(value: str) -> bool:
    return any(term in value for term in BROKER_BLOCKED_TERMS)


def _has_valid_trade_evidence_boundary(evidence: Mapping[str, Any]) -> bool:
    if evidence.get("broker_evidence_valid") is True or evidence.get("evidence_valid") is True:
        return True
    if _first_present(
        evidence,
        (
            "open_trade_count",
            "openTradeCount",
            "account_openTradeCount",
            "open_position_count",
            "openPositionCount",
            "account_openPositionCount",
        ),
    ) is not None:
        return True
    for key in (
        "open_trade",
        "open_trades",
        "openTrades",
        "closed_trade",
        "closed_trades",
        "closedTrades",
        "transactions",
        "trades",
    ):
        if key in evidence:
            return True
    for _, path in _iter_mappings(evidence):
        path_text = "/".join(path).lower()
        if "opentrades" in path_text or "closedtrades" in path_text:
            return True
    return False


def _base_result(expected_trade_id: str, evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "status_bucket": INVALID_EVIDENCE,
        "trade_id": expected_trade_id,
        "instrument": None,
        "side": None,
        "units": None,
        "entry_price": None,
        "current_price": None,
        "realized_pl": None,
        "unrealized_pl": None,
        "total_pl": None,
        "take_profit_order_id": None,
        "stop_loss_order_id": None,
        "open_trade_count": _count_from_evidence(
            evidence,
            ("open_trade_count", "openTradeCount", "account_openTradeCount"),
        ),
        "open_position_count": _count_from_evidence(
            evidence,
            ("open_position_count", "openPositionCount", "account_openPositionCount"),
        ),
        "evidence_timestamp_utc": _first_text(
            evidence,
            ("evidence_timestamp_utc", "timestamp_utc", "time", "lastTransactionTime"),
            None,
        ),
        "evidence_source": _first_text(
            evidence,
            ("evidence_source", "source", "packet_id", "script_status"),
            "provided_evidence",
        ),
        "blockers": [],
        "is_profit_evidence": False,
        "is_closed": False,
        "is_open": False,
        "is_broker_blocked": False,
        "notes": [],
        "next_recommended_packet": NEXT_RECOMMENDED_PACKET,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "live_endpoint_used": False,
        "secrets_written": False,
    }


def _count_from_evidence(
    evidence: Mapping[str, Any],
    keys: Sequence[str],
) -> int | None:
    direct = _first_present(evidence, keys)
    if direct is not None:
        return _int_or_none(direct)
    for node, _ in _iter_mappings(evidence):
        nested = _first_present(node, keys)
        if nested is not None:
            return _int_or_none(nested)
    return None


def _invalid(result: dict[str, Any], blockers: Sequence[str]) -> dict[str, Any]:
    result.update(
        {
            "status_bucket": INVALID_EVIDENCE,
            "blockers": _unique([str(blocker) for blocker in blockers]),
            "is_profit_evidence": False,
            "is_open": False,
            "is_closed": False,
            "is_broker_blocked": False,
            "notes": ["evidence_invalid_or_incomplete"],
        }
    )
    return result


def _closure_links_to_take_profit(
    trade: Mapping[str, Any],
    hydrated: Mapping[str, Any],
) -> bool:
    reason = _closure_text(trade)
    tp_id = _text(hydrated.get("take_profit_order_id"))
    order_id = _first_text(
        trade,
        ("closure_order_id", "order_id", "orderID", "orderId", "takeProfitOrderID"),
        "",
    )
    return "take_profit" in reason or "take-profit" in reason or (
        bool(tp_id) and order_id == tp_id
    )


def _closure_links_to_stop_loss(
    trade: Mapping[str, Any],
    hydrated: Mapping[str, Any],
) -> bool:
    reason = _closure_text(trade)
    sl_id = _text(hydrated.get("stop_loss_order_id"))
    order_id = _first_text(
        trade,
        ("closure_order_id", "order_id", "orderID", "orderId", "stopLossOrderID"),
        "",
    )
    return "stop_loss" in reason or "stop-loss" in reason or (
        bool(sl_id) and order_id == sl_id
    )


def _closure_text(trade: Mapping[str, Any]) -> str:
    values = [
        _first_text(
            trade,
            (
                "close_reason",
                "closure_reason",
                "reason",
                "type",
                "order_type",
                "trigger_reason",
            ),
            "",
        )
    ]
    return " ".join(values).replace(" ", "_").lower()


def _decimal_field(
    source: Mapping[str, Any],
    keys: Sequence[str],
    field_name: str,
    blockers: list[str],
    *,
    required: bool = True,
) -> Decimal | None:
    value = _first_present(source, keys)
    if value is None:
        if required:
            blockers.append(f"{field_name}_required")
        return None
    decimal_value = _decimal_or_none(value)
    if decimal_value is None:
        blockers.append(f"{field_name}_must_be_numeric")
    return decimal_value


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value, "f")


def _side_from_trade(trade: Mapping[str, Any], units: Decimal | None) -> str | None:
    explicit = _first_text(trade, ("side", "direction"), None)
    if explicit:
        return explicit.lower()
    if units is None:
        return None
    if units > 0:
        return "long"
    if units < 0:
        return "short"
    return "flat"


def _first_text(
    source: Mapping[str, Any],
    keys: Sequence[str],
    default: str | None = "",
) -> str | None:
    value = _first_present(source, keys)
    if value is None:
        return default
    return _text(value, default or "")


def _first_present(source: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in source and source[key] is not None:
            return source[key]
    return None


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _safe_blocker_name(value: str) -> str:
    cleaned = "".join(char if char.isalnum() else "_" for char in value.lower())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:80] or "broker_blocked"


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique


def _bool_word(value: Any) -> str:
    return "true" if value is True else "false"


def _display(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    if value == "":
        return "UNKNOWN"
    return str(value)
