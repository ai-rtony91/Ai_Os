from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from automation.forex_engine.oanda_demo_open_trade_monitor_v1 import (
    BROKER_EVIDENCE_BLOCKED as MONITOR_BROKER_EVIDENCE_BLOCKED,
    INVALID_EVIDENCE as MONITOR_INVALID_EVIDENCE,
    NOT_FOUND as MONITOR_NOT_FOUND,
    OWNER_RUN_TRADE_320_ANCHOR_EVIDENCE,
    STATUS_BUCKETS as MONITOR_STATUS_BUCKETS,
    classify_oanda_demo_trade_state,
)
from automation.forex_engine.oanda_demo_pl_result_bucket_repeat_proof_v1 import (
    BROKER_EVIDENCE_BLOCKED,
    INVALID_EVIDENCE,
    classify_pl_result_and_repeat_proof_lane,
)


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-TRADE-320-READ-ONLY-PL-REFRESH-V1"
PACKET_NAME = "AIOS FOREX OANDA DEMO TRADE 320 READ ONLY PL REFRESH V1"
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_TRADE_320_READ_ONLY_PL_REFRESH_V1_REPORT.md"
)

TRADE_ID = "320"
INSTRUMENT = "EUR_USD"
OFFLINE_FIXTURE_SOURCE = "offline_fixture_owner_trade_320_anchor"
OFFLINE_FIXTURE_READ_MODE = "OFFLINE_FIXTURE_ONLY"
OWNER_RUN_READ_ONLY_BROKER_MODE = "OWNER_RUN_READ_ONLY_BROKER_REQUESTED"


def refresh_trade_320_pl_result(evidence: dict | None = None) -> dict[str, Any]:
    source_evidence = _default_evidence() if evidence is None else evidence
    broker_read_mode = _broker_read_mode(source_evidence, evidence is None)

    monitor_result = _monitor_result(source_evidence)
    pl_result = classify_pl_result_and_repeat_proof_lane(monitor_result)

    result_bucket = pl_result.get("result_bucket")
    blockers = _unique(
        list(_sequence(monitor_result.get("blockers")))
        + list(_sequence(pl_result.get("blockers")))
    )
    broker_evidence_status = _broker_evidence_status(
        monitor_result,
        pl_result,
        broker_read_mode,
    )

    return {
        "packet_id": PACKET_ID,
        "packet_name": PACKET_NAME,
        "campaign_packet": 3,
        "trade_id": _display(pl_result.get("trade_id"), TRADE_ID),
        "instrument": _display(pl_result.get("instrument"), INSTRUMENT),
        "source": _source(monitor_result, source_evidence, evidence is None),
        "broker_read_mode": broker_read_mode,
        "monitor_bucket": monitor_result.get("status_bucket"),
        "result_bucket": result_bucket,
        "repeat_proof_lane_status": pl_result.get("repeat_proof_lane_status"),
        "repeat_proof_eligible": bool(pl_result.get("repeat_proof_eligible") is True),
        "profit_evidence": bool(pl_result.get("is_profit_evidence") is True),
        "realized_pl": pl_result.get("realized_pl"),
        "unrealized_pl": pl_result.get("unrealized_pl"),
        "is_open": bool(pl_result.get("is_open") is True),
        "is_closed": bool(pl_result.get("is_closed") is True),
        "broker_evidence_status": broker_evidence_status,
        "next_action": pl_result.get("next_action"),
        "next_packet_name": pl_result.get("next_packet_name"),
        "blockers": blockers,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
    }


def render_trade_320_read_only_pl_refresh_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = result.get("blockers")
    blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO TRADE 320 READ ONLY PL REFRESH V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- repo_branch: {branch}",
            "- pr_1072_anchor: Add OANDA demo open trade monitor",
            "- pr_1074_anchor: Add OANDA demo PL result bucket repeat proof lane",
            (
                "- trade_320_anchor: EUR_USD long 1 entry 1.13596 "
                "TP 321 SL 322"
            ),
            f"- broker_read_mode_used: {result.get('broker_read_mode')}",
            f"- monitor_bucket: {result.get('monitor_bucket')}",
            f"- pl_result_bucket: {result.get('result_bucket')}",
            (
                "- repeat_proof_lane_status: "
                f"{result.get('repeat_proof_lane_status')}"
            ),
            f"- repeat_proof_eligible: {_yes_no(result.get('repeat_proof_eligible'))}",
            f"- profit_evidence: {_yes_no(result.get('profit_evidence'))}",
            f"- realized_pl: {_display(result.get('realized_pl'), 'UNKNOWN')}",
            f"- unrealized_pl: {_display(result.get('unrealized_pl'), 'UNKNOWN')}",
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
            f"- trade_id: {_display(result.get('trade_id'), TRADE_ID)}",
            f"- instrument: {_display(result.get('instrument'), INSTRUMENT)}",
            f"- source: {_display(result.get('source'), 'UNKNOWN')}",
            (
                "- broker_evidence_status: "
                f"{_display(result.get('broker_evidence_status'), 'UNKNOWN')}"
            ),
            f"- is_open: {_true_false(result.get('is_open'))}",
            f"- is_closed: {_true_false(result.get('is_closed'))}",
            (
                "- no_new_order_placed: "
                f"{_true_false(result.get('no_new_order_placed'))}"
            ),
            (
                "- no_live_trade_placed: "
                f"{_true_false(result.get('no_live_trade_placed'))}"
            ),
            (
                "- no_broker_state_modified: "
                f"{_true_false(result.get('no_broker_state_modified'))}"
            ),
            (
                "- no_secrets_written: "
                f"{_true_false(result.get('no_secrets_written'))}"
            ),
            "",
        ]
    )


def write_trade_320_read_only_pl_refresh_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_trade_320_read_only_pl_refresh_report(result, branch=branch),
        encoding="utf-8",
    )
    return path


def _default_evidence() -> dict[str, Any]:
    evidence = dict(OWNER_RUN_TRADE_320_ANCHOR_EVIDENCE)
    evidence["evidence_source"] = OFFLINE_FIXTURE_SOURCE
    return evidence


def _monitor_result(evidence: Any) -> dict[str, Any]:
    if _is_packet_01_monitor_result(evidence):
        return dict(evidence)
    return classify_oanda_demo_trade_state(evidence, expected_trade_id=TRADE_ID)


def _is_packet_01_monitor_result(evidence: Any) -> bool:
    if not isinstance(evidence, Mapping):
        return False
    status_bucket = evidence.get("status_bucket")
    if status_bucket not in MONITOR_STATUS_BUCKETS:
        return False
    return (
        evidence.get("packet_id") is not None
        or "is_open" in evidence
        or "is_closed" in evidence
        or status_bucket
        in {
            MONITOR_BROKER_EVIDENCE_BLOCKED,
            MONITOR_INVALID_EVIDENCE,
            MONITOR_NOT_FOUND,
        }
    )


def _broker_read_mode(evidence: Any, is_default: bool) -> str:
    if is_default:
        return OFFLINE_FIXTURE_READ_MODE
    if isinstance(evidence, Mapping):
        requested = evidence.get("broker_read_mode")
        if requested:
            return str(requested)
        source = str(evidence.get("evidence_source", "")).lower()
        if "owner_run" in source or "broker" in source:
            return OWNER_RUN_READ_ONLY_BROKER_MODE
    return OFFLINE_FIXTURE_READ_MODE


def _broker_evidence_status(
    monitor_result: Mapping[str, Any],
    pl_result: Mapping[str, Any],
    broker_read_mode: str,
) -> str:
    if monitor_result.get("status_bucket") == MONITOR_BROKER_EVIDENCE_BLOCKED:
        return BROKER_EVIDENCE_BLOCKED
    if pl_result.get("result_bucket") == BROKER_EVIDENCE_BLOCKED:
        return BROKER_EVIDENCE_BLOCKED
    if pl_result.get("result_bucket") == INVALID_EVIDENCE:
        return INVALID_EVIDENCE
    if broker_read_mode == OWNER_RUN_READ_ONLY_BROKER_MODE:
        return "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED"
    return "OFFLINE_FIXTURE_CLASSIFIED"


def _source(
    monitor_result: Mapping[str, Any],
    evidence: Any,
    is_default: bool,
) -> str:
    if is_default:
        return OFFLINE_FIXTURE_SOURCE
    if isinstance(evidence, Mapping):
        explicit = evidence.get("source") or evidence.get("evidence_source")
        if explicit:
            return str(explicit)
    return _display(monitor_result.get("evidence_source"), "provided_evidence")


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    if value:
        return [value]
    return []


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            unique.append(text)
    return unique


def _display(value: Any, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
