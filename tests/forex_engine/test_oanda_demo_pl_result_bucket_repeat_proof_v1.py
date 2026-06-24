from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_pl_result_bucket_repeat_proof_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED,
    CLOSED_BREAKEVEN_NO_PROFIT,
    CLOSED_REALIZED_LOSS_EVIDENCE,
    CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE,
    CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE,
    INVALID_EVIDENCE,
    NO_PROFIT_EVIDENCE_OPEN_NEGATIVE,
    OPEN_UNREALIZED_FLAT_NO_PROFIT,
    OPEN_UNREALIZED_PROFIT_EVIDENCE,
    TRADE_NOT_FOUND,
    classify_pl_result_and_repeat_proof_lane,
    write_pl_result_bucket_repeat_proof_report,
)
from scripts.forex_delivery.run_oanda_demo_pl_result_bucket_repeat_proof_v1 import (  # noqa: E402
    main as script_main,
)


def monitor_bucket(
    status_bucket: str,
    *,
    realized_pl: str = "0.0000",
    unrealized_pl: str | None = "-0.0004",
    is_open: bool = True,
    is_closed: bool = False,
) -> dict:
    return {
        "status_bucket": status_bucket,
        "trade_id": "320",
        "instrument": "EUR_USD",
        "realized_pl": realized_pl,
        "unrealized_pl": unrealized_pl,
        "is_open": is_open,
        "is_closed": is_closed,
        "blockers": [],
    }


def closed_bucket(status_bucket: str, realized_pl: str) -> dict:
    return monitor_bucket(
        status_bucket,
        realized_pl=realized_pl,
        unrealized_pl=None,
        is_open=False,
        is_closed=True,
    )


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_open_unrealized_negative_maps_to_no_profit_open_negative() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        monitor_bucket("OPEN_UNREALIZED_NEGATIVE", unrealized_pl="-0.0004")
    )

    assert result["result_bucket"] == NO_PROFIT_EVIDENCE_OPEN_NEGATIVE
    assert result["repeat_proof_lane_status"] == "NOT_STARTED_NO_PROFIT_EVIDENCE"
    assert result["repeat_proof_eligible"] is False
    assert result["is_profit_evidence"] is False


def test_open_unrealized_positive_is_watch_only_not_repeat_eligible() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        monitor_bucket("OPEN_UNREALIZED_POSITIVE", unrealized_pl="0.0004")
    )

    assert result["result_bucket"] == OPEN_UNREALIZED_PROFIT_EVIDENCE
    assert result["repeat_proof_lane_status"] == "WATCH_OPEN_UNREALIZED_PROFIT"
    assert result["is_unrealized_profit_evidence"] is True
    assert result["repeat_proof_eligible"] is False


def test_open_unrealized_flat_maps_to_flat_no_profit() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        monitor_bucket("OPEN_UNREALIZED_FLAT", unrealized_pl="0.0000")
    )

    assert result["result_bucket"] == OPEN_UNREALIZED_FLAT_NO_PROFIT
    assert result["is_profit_evidence"] is False
    assert result["repeat_proof_eligible"] is False


def test_closed_take_profit_profit_is_repeat_eligible() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        closed_bucket("CLOSED_TAKE_PROFIT_PROFIT", "0.0010")
    )

    assert result["result_bucket"] == CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE
    assert result["repeat_proof_lane_status"] == "READY_AFTER_REALIZED_PROFIT"
    assert result["repeat_proof_eligible"] is True


def test_closed_other_profit_is_repeat_eligible() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        closed_bucket("CLOSED_OTHER_PROFIT", "0.0010")
    )

    assert result["result_bucket"] == CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE
    assert result["repeat_proof_lane_status"] == "READY_AFTER_REALIZED_PROFIT"
    assert result["repeat_proof_eligible"] is True


def test_closed_stop_loss_loss_blocks_repeat_proof() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        closed_bucket("CLOSED_STOP_LOSS_LOSS", "-0.0010")
    )

    assert result["result_bucket"] == CLOSED_REALIZED_LOSS_EVIDENCE
    assert result["repeat_proof_lane_status"] == "BLOCKED_BY_LOSS"
    assert result["is_loss_evidence"] is True


def test_closed_other_loss_blocks_repeat_proof() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        closed_bucket("CLOSED_OTHER_LOSS", "-0.0010")
    )

    assert result["result_bucket"] == CLOSED_REALIZED_LOSS_EVIDENCE
    assert result["repeat_proof_lane_status"] == "BLOCKED_BY_LOSS"


def test_closed_breakeven_blocks_repeat_proof() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        closed_bucket("CLOSED_BREAKEVEN", "0.0000")
    )

    assert result["result_bucket"] == CLOSED_BREAKEVEN_NO_PROFIT
    assert result["repeat_proof_lane_status"] == "BLOCKED_BY_BREAKEVEN"
    assert result["is_breakeven_evidence"] is True


def test_broker_evidence_blocked_maps_to_broker_block() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        {
            "status_bucket": "BROKER_EVIDENCE_BLOCKED",
            "trade_id": "320",
            "blockers": ["vault_demo_access_token_missing"],
        }
    )

    assert result["result_bucket"] == BROKER_EVIDENCE_BLOCKED
    assert result["repeat_proof_lane_status"] == "BLOCKED_BY_BROKER_EVIDENCE"
    assert result["repeat_proof_eligible"] is False


def test_trade_not_found_blocks_repeat_proof() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        {"status_bucket": "NOT_FOUND", "trade_id": "320"}
    )

    assert result["result_bucket"] == TRADE_NOT_FOUND
    assert result["repeat_proof_lane_status"] == "BLOCKED_TRADE_NOT_FOUND"


def test_invalid_evidence_blocks_repeat_proof() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        {"status_bucket": "INVALID_EVIDENCE", "blockers": ["schema_missing"]}
    )

    assert result["result_bucket"] == INVALID_EVIDENCE
    assert result["repeat_proof_lane_status"] == "BLOCKED_BY_INVALID_EVIDENCE"
    assert result["repeat_proof_eligible"] is False


def test_contradictory_evidence_cannot_be_repeat_eligible() -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        monitor_bucket(
            "CLOSED_TAKE_PROFIT_PROFIT",
            realized_pl="0.0010",
            unrealized_pl=None,
            is_open=True,
            is_closed=False,
        )
    )

    assert result["result_bucket"] == INVALID_EVIDENCE
    assert result["repeat_proof_eligible"] is False
    assert "source_closed_bucket_conflicts_with_is_open_true" in result["blockers"]


def test_report_writer_includes_required_safety_statements(tmp_path: Path) -> None:
    result = classify_pl_result_and_repeat_proof_lane(
        monitor_bucket("OPEN_UNREALIZED_NEGATIVE", unrealized_pl="-0.0004")
    )
    report_path = tmp_path / "report.md"

    write_pl_result_bucket_repeat_proof_report(result, report_path)

    text = report_path.read_text(encoding="utf-8")
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text


def test_cli_default_fixture_returns_no_profit_open_negative() -> None:
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["script_status"] == NO_PROFIT_EVIDENCE_OPEN_NEGATIVE
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False
