from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-PL-RESULT-BUCKET-REPEAT-PROOF-LANE-V1"
PACKET_NAME = "AIOS FOREX OANDA DEMO P/L RESULT BUCKET AND REPEAT PROOF LANE V1"
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_PL_RESULT_BUCKET_REPEAT_PROOF_LANE_V1_REPORT.md"
)

NO_PROFIT_EVIDENCE_OPEN_NEGATIVE = "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE"
OPEN_UNREALIZED_PROFIT_EVIDENCE = "OPEN_UNREALIZED_PROFIT_EVIDENCE"
OPEN_UNREALIZED_FLAT_NO_PROFIT = "OPEN_UNREALIZED_FLAT_NO_PROFIT"
CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE = "CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE"
CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE = "CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE"
CLOSED_REALIZED_LOSS_EVIDENCE = "CLOSED_REALIZED_LOSS_EVIDENCE"
CLOSED_BREAKEVEN_NO_PROFIT = "CLOSED_BREAKEVEN_NO_PROFIT"
BROKER_EVIDENCE_BLOCKED = "BROKER_EVIDENCE_BLOCKED"
TRADE_NOT_FOUND = "TRADE_NOT_FOUND"
INVALID_EVIDENCE = "INVALID_EVIDENCE"

RESULT_BUCKETS = (
    NO_PROFIT_EVIDENCE_OPEN_NEGATIVE,
    OPEN_UNREALIZED_PROFIT_EVIDENCE,
    OPEN_UNREALIZED_FLAT_NO_PROFIT,
    CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE,
    CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE,
    CLOSED_REALIZED_LOSS_EVIDENCE,
    CLOSED_BREAKEVEN_NO_PROFIT,
    BROKER_EVIDENCE_BLOCKED,
    TRADE_NOT_FOUND,
    INVALID_EVIDENCE,
)

NOT_STARTED_NO_PROFIT_EVIDENCE = "NOT_STARTED_NO_PROFIT_EVIDENCE"
READY_AFTER_REALIZED_PROFIT = "READY_AFTER_REALIZED_PROFIT"
WATCH_OPEN_UNREALIZED_PROFIT = "WATCH_OPEN_UNREALIZED_PROFIT"
BLOCKED_BY_LOSS = "BLOCKED_BY_LOSS"
BLOCKED_BY_BREAKEVEN = "BLOCKED_BY_BREAKEVEN"
BLOCKED_BY_BROKER_EVIDENCE = "BLOCKED_BY_BROKER_EVIDENCE"
BLOCKED_BY_INVALID_EVIDENCE = "BLOCKED_BY_INVALID_EVIDENCE"
BLOCKED_TRADE_NOT_FOUND = "BLOCKED_TRADE_NOT_FOUND"

REPEAT_PROOF_LANE_STATUSES = (
    NOT_STARTED_NO_PROFIT_EVIDENCE,
    READY_AFTER_REALIZED_PROFIT,
    WATCH_OPEN_UNREALIZED_PROFIT,
    BLOCKED_BY_LOSS,
    BLOCKED_BY_BREAKEVEN,
    BLOCKED_BY_BROKER_EVIDENCE,
    BLOCKED_BY_INVALID_EVIDENCE,
    BLOCKED_TRADE_NOT_FOUND,
)

KEEP_MONITORING_EXISTING_TRADE_NO_NEW_ORDER = (
    "KEEP_MONITORING_EXISTING_TRADE_NO_NEW_ORDER"
)
KEEP_MONITORING_FOR_REALIZED_CLOSE_NO_NEW_ORDER = (
    "KEEP_MONITORING_FOR_REALIZED_CLOSE_NO_NEW_ORDER"
)
START_REPEAT_PROOF_LANE_WITH_OWNER_APPROVAL = (
    "START_REPEAT_PROOF_LANE_WITH_OWNER_APPROVAL"
)
RECORD_LOSS_AND_REQUIRE_REVIEW_BEFORE_NEXT_DEMO_ORDER = (
    "RECORD_LOSS_AND_REQUIRE_REVIEW_BEFORE_NEXT_DEMO_ORDER"
)
RECORD_BREAKEVEN_AND_REQUIRE_REVIEW = "RECORD_BREAKEVEN_AND_REQUIRE_REVIEW"
RESTORE_READ_ONLY_EVIDENCE_ACCESS = "RESTORE_READ_ONLY_EVIDENCE_ACCESS"
RECONCILE_TRADE_HISTORY_BEFORE_NEXT_PACKET = (
    "RECONCILE_TRADE_HISTORY_BEFORE_NEXT_PACKET"
)
FIX_EVIDENCE_SCHEMA_OR_INPUT = "FIX_EVIDENCE_SCHEMA_OR_INPUT"

NEXT_PACKET_BY_RESULT_BUCKET = {
    NO_PROFIT_EVIDENCE_OPEN_NEGATIVE: (
        "AIOS FOREX OANDA DEMO OPEN TRADE MONITOR V2"
    ),
    OPEN_UNREALIZED_PROFIT_EVIDENCE: (
        "AIOS FOREX OANDA DEMO REALIZED CLOSE MONITOR V1"
    ),
    OPEN_UNREALIZED_FLAT_NO_PROFIT: (
        "AIOS FOREX OANDA DEMO OPEN TRADE MONITOR V2"
    ),
    CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE: (
        "AIOS FOREX OANDA DEMO REPEAT PROOF LANE OWNER APPROVAL V1"
    ),
    CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE: (
        "AIOS FOREX OANDA DEMO REPEAT PROOF LANE OWNER APPROVAL V1"
    ),
    CLOSED_REALIZED_LOSS_EVIDENCE: (
        "AIOS FOREX OANDA DEMO LOSS REVIEW BEFORE NEXT ORDER V1"
    ),
    CLOSED_BREAKEVEN_NO_PROFIT: "AIOS FOREX OANDA DEMO BREAKEVEN REVIEW V1",
    BROKER_EVIDENCE_BLOCKED: (
        "AIOS FOREX OANDA DEMO READ ONLY EVIDENCE ACCESS RECOVERY V1"
    ),
    TRADE_NOT_FOUND: "AIOS FOREX OANDA DEMO TRADE HISTORY RECONCILIATION V1",
    INVALID_EVIDENCE: "AIOS FOREX OANDA DEMO EVIDENCE SCHEMA REPAIR V1",
}

SOURCE_TO_RESULT_BUCKET = {
    "OPEN_UNREALIZED_NEGATIVE": NO_PROFIT_EVIDENCE_OPEN_NEGATIVE,
    "OPEN_UNREALIZED_POSITIVE": OPEN_UNREALIZED_PROFIT_EVIDENCE,
    "OPEN_UNREALIZED_FLAT": OPEN_UNREALIZED_FLAT_NO_PROFIT,
    "CLOSED_TAKE_PROFIT_PROFIT": CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE,
    "CLOSED_OTHER_PROFIT": CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE,
    "CLOSED_STOP_LOSS_LOSS": CLOSED_REALIZED_LOSS_EVIDENCE,
    "CLOSED_OTHER_LOSS": CLOSED_REALIZED_LOSS_EVIDENCE,
    "CLOSED_BREAKEVEN": CLOSED_BREAKEVEN_NO_PROFIT,
    "BROKER_EVIDENCE_BLOCKED": BROKER_EVIDENCE_BLOCKED,
    "NOT_FOUND": TRADE_NOT_FOUND,
    "INVALID_EVIDENCE": INVALID_EVIDENCE,
}

FILLED_CAPTURE_TO_RESULT_BUCKET = {
    "FILLED_TRADE_PL_POSITIVE": CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE,
    "FILLED_TRADE_PL_NEGATIVE": CLOSED_REALIZED_LOSS_EVIDENCE,
    "FILLED_TRADE_PL_ZERO": CLOSED_BREAKEVEN_NO_PROFIT,
    "FILLED_TRADE_PL_NOT_FOUND": TRADE_NOT_FOUND,
    "BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE": BROKER_EVIDENCE_BLOCKED,
}

RESULT_TO_REPEAT_PROOF_STATUS = {
    NO_PROFIT_EVIDENCE_OPEN_NEGATIVE: NOT_STARTED_NO_PROFIT_EVIDENCE,
    OPEN_UNREALIZED_PROFIT_EVIDENCE: WATCH_OPEN_UNREALIZED_PROFIT,
    OPEN_UNREALIZED_FLAT_NO_PROFIT: NOT_STARTED_NO_PROFIT_EVIDENCE,
    CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE: READY_AFTER_REALIZED_PROFIT,
    CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE: READY_AFTER_REALIZED_PROFIT,
    CLOSED_REALIZED_LOSS_EVIDENCE: BLOCKED_BY_LOSS,
    CLOSED_BREAKEVEN_NO_PROFIT: BLOCKED_BY_BREAKEVEN,
    BROKER_EVIDENCE_BLOCKED: BLOCKED_BY_BROKER_EVIDENCE,
    TRADE_NOT_FOUND: BLOCKED_TRADE_NOT_FOUND,
    INVALID_EVIDENCE: BLOCKED_BY_INVALID_EVIDENCE,
}

RESULT_TO_NEXT_ACTION = {
    NO_PROFIT_EVIDENCE_OPEN_NEGATIVE: (
        KEEP_MONITORING_EXISTING_TRADE_NO_NEW_ORDER
    ),
    OPEN_UNREALIZED_PROFIT_EVIDENCE: (
        KEEP_MONITORING_FOR_REALIZED_CLOSE_NO_NEW_ORDER
    ),
    OPEN_UNREALIZED_FLAT_NO_PROFIT: KEEP_MONITORING_EXISTING_TRADE_NO_NEW_ORDER,
    CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE: (
        START_REPEAT_PROOF_LANE_WITH_OWNER_APPROVAL
    ),
    CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE: (
        START_REPEAT_PROOF_LANE_WITH_OWNER_APPROVAL
    ),
    CLOSED_REALIZED_LOSS_EVIDENCE: (
        RECORD_LOSS_AND_REQUIRE_REVIEW_BEFORE_NEXT_DEMO_ORDER
    ),
    CLOSED_BREAKEVEN_NO_PROFIT: RECORD_BREAKEVEN_AND_REQUIRE_REVIEW,
    BROKER_EVIDENCE_BLOCKED: RESTORE_READ_ONLY_EVIDENCE_ACCESS,
    TRADE_NOT_FOUND: RECONCILE_TRADE_HISTORY_BEFORE_NEXT_PACKET,
    INVALID_EVIDENCE: FIX_EVIDENCE_SCHEMA_OR_INPUT,
}

OPEN_RESULT_BUCKETS = {
    NO_PROFIT_EVIDENCE_OPEN_NEGATIVE,
    OPEN_UNREALIZED_PROFIT_EVIDENCE,
    OPEN_UNREALIZED_FLAT_NO_PROFIT,
}

CLOSED_RESULT_BUCKETS = {
    CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE,
    CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE,
    CLOSED_REALIZED_LOSS_EVIDENCE,
    CLOSED_BREAKEVEN_NO_PROFIT,
}

OWNER_PACKET_01_OPEN_NEGATIVE_EVIDENCE: dict[str, Any] = {
    "status_bucket": "OPEN_UNREALIZED_NEGATIVE",
    "evidence_source": "owner_packet_anchor_oanda_demo_trade_320",
    "trade_id": "320",
    "instrument": "EUR_USD",
    "side": "long",
    "units": "1",
    "entry": "1.13596",
    "take_profit_order_id": "321",
    "stop_loss_order_id": "322",
    "realized_pl": "0.0000",
    "unrealized_pl": "-0.0004",
    "open_trade_count": 1,
    "open_position_count": 1,
    "is_open": True,
    "is_closed": False,
    "is_profit_evidence": False,
    "order_placement_performed": False,
    "order_close_performed": False,
    "order_mutation_performed": False,
    "live_endpoint_used": False,
    "secrets_written": False,
}


def classify_pl_result_and_repeat_proof_lane(evidence: dict) -> dict[str, Any]:
    normalized = _normalize_evidence(evidence)
    source_bucket = normalized["source_trade_bucket"]
    result_bucket, mapping_blockers = _result_bucket_from_source(
        source_bucket,
        normalized,
    )
    blockers = _unique(normalized["input_blockers"] + mapping_blockers)

    if result_bucket not in {
        BROKER_EVIDENCE_BLOCKED,
        TRADE_NOT_FOUND,
        INVALID_EVIDENCE,
    }:
        blockers = _unique(blockers + _pl_consistency_blockers(result_bucket, normalized))

    if result_bucket == BROKER_EVIDENCE_BLOCKED and not blockers:
        blockers.append("broker_evidence_blocked")
    if result_bucket == TRADE_NOT_FOUND and not blockers:
        blockers.append("trade_not_found")
    if result_bucket == INVALID_EVIDENCE and not blockers:
        blockers.append("invalid_evidence")

    if mapping_blockers or _has_invalidating_blockers(blockers):
        result_bucket = INVALID_EVIDENCE

    is_open = _resolved_open_state(result_bucket, normalized)
    is_closed = _resolved_closed_state(result_bucket, normalized)
    realized = _decimal_or_none(normalized["realized_pl"])
    unrealized = _decimal_or_none(normalized["unrealized_pl"])

    is_realized_profit_evidence = (
        result_bucket
        in {
            CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE,
            CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE,
        }
        and realized is not None
        and realized > 0
    )
    is_unrealized_profit_evidence = (
        result_bucket == OPEN_UNREALIZED_PROFIT_EVIDENCE
        and unrealized is not None
        and unrealized > 0
    )
    is_loss_evidence = result_bucket == CLOSED_REALIZED_LOSS_EVIDENCE
    is_breakeven_evidence = result_bucket == CLOSED_BREAKEVEN_NO_PROFIT

    repeat_proof_eligible = (
        result_bucket
        in {
            CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE,
            CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE,
        }
        and realized is not None
        and realized > 0
        and is_closed is True
        and not blockers
    )

    repeat_status = RESULT_TO_REPEAT_PROOF_STATUS[result_bucket]
    next_action = RESULT_TO_NEXT_ACTION[result_bucket]
    return {
        "packet_id": PACKET_ID,
        "campaign_packet": 2,
        "result_bucket": result_bucket,
        "source_trade_bucket": source_bucket,
        "trade_id": normalized["trade_id"],
        "instrument": normalized["instrument"],
        "realized_pl": _decimal_text(realized)
        if realized is not None
        else normalized["realized_pl"],
        "unrealized_pl": _decimal_text(unrealized)
        if unrealized is not None
        else normalized["unrealized_pl"],
        "is_open": is_open,
        "is_closed": is_closed,
        "is_profit_evidence": bool(
            is_realized_profit_evidence or is_unrealized_profit_evidence
        ),
        "is_realized_profit_evidence": is_realized_profit_evidence,
        "is_unrealized_profit_evidence": is_unrealized_profit_evidence,
        "is_loss_evidence": is_loss_evidence,
        "is_breakeven_evidence": is_breakeven_evidence,
        "repeat_proof_lane_status": repeat_status,
        "repeat_proof_eligible": repeat_proof_eligible,
        "blockers": blockers,
        "next_action": next_action,
        "next_packet_name": NEXT_PACKET_BY_RESULT_BUCKET[result_bucket],
        "no_new_order_required": True,
        "no_broker_state_change_required": True,
        "notes": _notes(result_bucket, repeat_proof_eligible, blockers),
    }


def render_pl_result_bucket_repeat_proof_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = result.get("blockers")
    blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO P/L RESULT BUCKET AND REPEAT PROOF LANE V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- repo_branch: {branch}",
            "- pr_1072_anchor: Add OANDA demo open trade monitor",
            "- pr_1073_anchor: Preserve OANDA demo proof chain leftovers",
            (
                "- current_trade_anchor: trade 320 EUR_USD long 1 entry 1.13596 "
                "TP 321 SL 322"
            ),
            f"- source_monitor_bucket: {result.get('source_trade_bucket')}",
            f"- pl_result_bucket: {result.get('result_bucket')}",
            f"- repeat_proof_lane_status: {result.get('repeat_proof_lane_status')}",
            f"- repeat_proof_eligible: {_yes_no(result.get('repeat_proof_eligible'))}",
            f"- profit_evidence: {_yes_no(result.get('is_profit_evidence'))}",
            f"- realized_pl: {_display(result.get('realized_pl'))}",
            f"- unrealized_pl: {_display(result.get('unrealized_pl'))}",
            f"- next_action: {result.get('next_action')}",
            f"- next_packet_name: {result.get('next_packet_name')}",
            f"- blockers: {blocker_text}",
            "",
            "## Safety Statements",
            "",
            "- no new order placed",
            "- no live trade placed",
            "- no broker state modified",
            "- no secrets written",
            "",
            "## Machine Result",
            "",
            f"- campaign_packet: {result.get('campaign_packet')}",
            f"- trade_id: {_display(result.get('trade_id'))}",
            f"- instrument: {_display(result.get('instrument'))}",
            f"- is_open: {_true_false(result.get('is_open'))}",
            f"- is_closed: {_true_false(result.get('is_closed'))}",
            (
                "- no_new_order_required: "
                f"{_true_false(result.get('no_new_order_required'))}"
            ),
            (
                "- no_broker_state_change_required: "
                f"{_true_false(result.get('no_broker_state_change_required'))}"
            ),
            "",
        ]
    )


def write_pl_result_bucket_repeat_proof_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_pl_result_bucket_repeat_proof_report(result, branch=branch),
        encoding="utf-8",
    )
    return path


def _normalize_evidence(evidence: Any) -> dict[str, Any]:
    if not isinstance(evidence, Mapping):
        return {
            "source_trade_bucket": INVALID_EVIDENCE,
            "trade_id": None,
            "instrument": None,
            "realized_pl": None,
            "unrealized_pl": None,
            "is_open": None,
            "is_closed": None,
            "input_blockers": ["evidence_must_be_mapping"],
        }

    payload = _primary_payload(evidence)
    source_bucket = _source_bucket(evidence, payload)
    trade_id = _first_value(
        payload,
        evidence,
        keys=("trade_id", "tradeID", "id", "orderFillTransaction_id"),
    )
    instrument = _first_value(
        payload,
        evidence,
        keys=("instrument", "pair"),
    )
    owner_filled_trade = _mapping(payload.get("owner_filled_trade_evidence"))
    if trade_id is None:
        trade_id = _first_value(
            owner_filled_trade,
            keys=("orderFillTransaction_id", "order_fill_transaction_id"),
        )
    if instrument is None:
        instrument = _first_value(owner_filled_trade, keys=("instrument",))

    pl_evidence = _mapping(payload.get("pl_evidence"))
    realized_pl = _first_value(
        payload,
        evidence,
        keys=("realized_pl", "realizedPL", "pl", "profitLoss"),
    )
    if realized_pl is None:
        realized_pl = _first_value(pl_evidence, keys=("realized_pl_total",))

    unrealized_pl = _first_value(
        payload,
        evidence,
        keys=("unrealized_pl", "unrealizedPL", "trueUnrealizedPL"),
    )
    if unrealized_pl is None:
        unrealized_pl = _first_unrealized_from_pl_evidence(pl_evidence)

    is_open = _bool_or_none(_first_value(payload, evidence, keys=("is_open",)))
    is_closed = _bool_or_none(_first_value(payload, evidence, keys=("is_closed",)))
    return {
        "source_trade_bucket": source_bucket,
        "trade_id": _text(trade_id) if trade_id is not None else None,
        "instrument": _text(instrument) if instrument is not None else None,
        "realized_pl": _text(realized_pl) if realized_pl is not None else None,
        "unrealized_pl": _text(unrealized_pl) if unrealized_pl is not None else None,
        "is_open": is_open,
        "is_closed": is_closed,
        "input_blockers": _input_blockers(evidence, payload),
    }


def _primary_payload(evidence: Mapping[str, Any]) -> Mapping[str, Any]:
    result = evidence.get("result")
    if isinstance(result, Mapping) and (
        "status_bucket" in result or "trade_id" in result
    ):
        return result
    decision = evidence.get("decision")
    if isinstance(decision, Mapping) and (
        "pl_capture_classification" in decision or "pl_evidence" in decision
    ):
        return decision
    return evidence


def _source_bucket(
    evidence: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> str:
    for candidate in (
        payload.get("status_bucket"),
        evidence.get("status_bucket"),
        payload.get("result_bucket"),
        evidence.get("result_bucket"),
        payload.get("script_status"),
        evidence.get("script_status"),
    ):
        text = _text(candidate)
        if text in SOURCE_TO_RESULT_BUCKET or text in RESULT_BUCKETS:
            return text
    for candidate in (
        payload.get("pl_capture_classification"),
        evidence.get("pl_capture_classification"),
    ):
        text = _text(candidate)
        if text:
            return text
    decision = evidence.get("decision")
    if isinstance(decision, Mapping):
        text = _text(decision.get("pl_capture_classification"))
        if text:
            return text
    return INVALID_EVIDENCE


def _result_bucket_from_source(
    source_bucket: str,
    normalized: Mapping[str, Any],
) -> tuple[str, list[str]]:
    if source_bucket in SOURCE_TO_RESULT_BUCKET:
        return SOURCE_TO_RESULT_BUCKET[source_bucket], []
    if source_bucket in RESULT_BUCKETS:
        return source_bucket, []
    if source_bucket in FILLED_CAPTURE_TO_RESULT_BUCKET:
        return FILLED_CAPTURE_TO_RESULT_BUCKET[source_bucket], []
    if source_bucket == "FILLED_TRADE_PL_OPEN_UNREALIZED":
        unrealized = _decimal_or_none(normalized.get("unrealized_pl"))
        if unrealized is None:
            return INVALID_EVIDENCE, ["open_unrealized_capture_missing_unrealized_pl"]
        if unrealized > 0:
            return OPEN_UNREALIZED_PROFIT_EVIDENCE, []
        if unrealized < 0:
            return NO_PROFIT_EVIDENCE_OPEN_NEGATIVE, []
        return OPEN_UNREALIZED_FLAT_NO_PROFIT, []
    return INVALID_EVIDENCE, ["source_trade_bucket_not_supported"]


def _pl_consistency_blockers(
    result_bucket: str,
    normalized: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    realized = _decimal_or_none(normalized.get("realized_pl"))
    unrealized = _decimal_or_none(normalized.get("unrealized_pl"))
    is_open = normalized.get("is_open")
    is_closed = normalized.get("is_closed")

    if result_bucket in OPEN_RESULT_BUCKETS:
        if is_open is False:
            blockers.append("source_open_bucket_conflicts_with_is_open_false")
        if is_closed is True:
            blockers.append("source_open_bucket_conflicts_with_is_closed_true")
        if unrealized is None:
            blockers.append("open_bucket_unrealized_pl_must_be_numeric")
    if result_bucket in CLOSED_RESULT_BUCKETS:
        if is_open is True:
            blockers.append("source_closed_bucket_conflicts_with_is_open_true")
        if is_closed is False:
            blockers.append("source_closed_bucket_conflicts_with_is_closed_false")
        if realized is None:
            blockers.append("closed_bucket_realized_pl_must_be_numeric")

    if result_bucket == NO_PROFIT_EVIDENCE_OPEN_NEGATIVE and unrealized is not None:
        if unrealized >= 0:
            blockers.append("open_negative_bucket_requires_negative_unrealized_pl")
    if result_bucket == OPEN_UNREALIZED_PROFIT_EVIDENCE and unrealized is not None:
        if unrealized <= 0:
            blockers.append("open_profit_bucket_requires_positive_unrealized_pl")
    if result_bucket == OPEN_UNREALIZED_FLAT_NO_PROFIT and unrealized is not None:
        if unrealized != 0:
            blockers.append("open_flat_bucket_requires_zero_unrealized_pl")
    if result_bucket in {
        CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE,
        CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE,
    } and realized is not None:
        if realized <= 0:
            blockers.append("closed_profit_bucket_requires_positive_realized_pl")
    if result_bucket == CLOSED_REALIZED_LOSS_EVIDENCE and realized is not None:
        if realized >= 0:
            blockers.append("closed_loss_bucket_requires_negative_realized_pl")
    if result_bucket == CLOSED_BREAKEVEN_NO_PROFIT and realized is not None:
        if realized != 0:
            blockers.append("closed_breakeven_bucket_requires_zero_realized_pl")
    return blockers


def _has_invalidating_blockers(blockers: Sequence[str]) -> bool:
    invalid_terms = (
        "conflicts",
        "must_be_numeric",
        "requires_",
        "not_supported",
        "missing_unrealized_pl",
        "evidence_must_be_mapping",
    )
    return any(any(term in blocker for term in invalid_terms) for blocker in blockers)


def _resolved_open_state(result_bucket: str, normalized: Mapping[str, Any]) -> bool:
    if result_bucket in OPEN_RESULT_BUCKETS:
        return True
    if result_bucket in CLOSED_RESULT_BUCKETS:
        return False
    return bool(normalized.get("is_open") is True)


def _resolved_closed_state(result_bucket: str, normalized: Mapping[str, Any]) -> bool:
    if result_bucket in CLOSED_RESULT_BUCKETS:
        return True
    if result_bucket in OPEN_RESULT_BUCKETS:
        return False
    return bool(normalized.get("is_closed") is True)


def _notes(
    result_bucket: str,
    repeat_proof_eligible: bool,
    blockers: Sequence[str],
) -> list[str]:
    notes = [
        "no_new_order_required",
        "no_broker_state_change_required",
        "no_live_trade_authorized",
        "no_secret_write_required",
    ]
    if repeat_proof_eligible:
        notes.append("realized_profit_trade_closed_repeat_proof_ready")
    elif result_bucket == OPEN_UNREALIZED_PROFIT_EVIDENCE:
        notes.append("open_unrealized_profit_is_watch_only_not_repeat_proof")
    elif result_bucket == NO_PROFIT_EVIDENCE_OPEN_NEGATIVE:
        notes.append("open_negative_trade_is_not_profit_evidence")
    elif result_bucket == OPEN_UNREALIZED_FLAT_NO_PROFIT:
        notes.append("open_flat_trade_is_not_profit_evidence")
    elif blockers:
        notes.append("repeat_proof_lane_blocked")
    return notes


def _input_blockers(
    evidence: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    for raw in (payload.get("blockers"), evidence.get("blockers")):
        if isinstance(raw, str):
            blockers.append(raw)
        elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
            blockers.extend(str(item) for item in raw)
    return _unique(blockers)


def _first_unrealized_from_pl_evidence(pl_evidence: Mapping[str, Any]) -> Any:
    for collection_key in ("open_trade_evidence", "open_position_evidence"):
        collection = pl_evidence.get(collection_key)
        if not isinstance(collection, Sequence) or isinstance(collection, (str, bytes)):
            continue
        for item in collection:
            if isinstance(item, Mapping):
                value = _first_value(item, keys=("unrealized_pl", "unrealizedPL"))
                if value is not None:
                    return value
    snapshot = _mapping(pl_evidence.get("account_summary_snapshot"))
    return _first_value(snapshot, keys=("unrealized_pl", "unrealizedPL"))


def _first_value(*mappings: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for mapping in mappings:
        if not isinstance(mapping, Mapping):
            continue
        for key in keys:
            if key in mapping and mapping.get(key) is not None:
                return mapping.get(key)
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


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


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")


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


def _display(value: Any) -> str:
    text = _text(value)
    return text if text else "UNKNOWN"


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
