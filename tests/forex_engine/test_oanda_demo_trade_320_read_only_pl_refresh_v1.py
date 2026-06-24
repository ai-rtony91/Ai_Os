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
    OPEN_UNREALIZED_PROFIT_EVIDENCE,
    TRADE_NOT_FOUND,
)
from automation.forex_engine.oanda_demo_trade_320_read_only_pl_refresh_v1 import (  # noqa: E402
    refresh_trade_320_pl_result,
    write_trade_320_read_only_pl_refresh_report,
)
from scripts.forex_delivery.run_oanda_demo_trade_320_read_only_pl_refresh_v1 import (  # noqa: E402
    main as script_main,
)


def open_trade(unrealized_pl: str) -> dict:
    return {
        "evidence_source": "unit_test",
        "open_trades": {
            "trades": [
                {
                    "id": "320",
                    "state": "OPEN",
                    "instrument": "EUR_USD",
                    "currentUnits": "1",
                    "price": "1.13596",
                    "realizedPL": "0.0000",
                    "unrealizedPL": unrealized_pl,
                    "takeProfitOrderID": "321",
                    "stopLossOrderID": "322",
                }
            ]
        },
        "account": {"openTradeCount": "1", "openPositionCount": "1"},
    }


def closed_trade(realized_pl: str, **overrides) -> dict:
    trade = {
        "trade_id": "320",
        "state": "CLOSED",
        "instrument": "EUR_USD",
        "side": "long",
        "units": "1",
        "entry": "1.13596",
        "realized_pl": realized_pl,
        "take_profit_order_id": "321",
        "stop_loss_order_id": "322",
    }
    trade.update(overrides)
    return {"evidence_source": "unit_test", "closed_trades": [trade]}


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_default_fixture_returns_no_profit_open_negative() -> None:
    result = refresh_trade_320_pl_result()

    assert result["monitor_bucket"] == "OPEN_UNREALIZED_NEGATIVE"
    assert result["result_bucket"] == NO_PROFIT_EVIDENCE_OPEN_NEGATIVE
    assert result["repeat_proof_lane_status"] == "NOT_STARTED_NO_PROFIT_EVIDENCE"
    assert result["repeat_proof_eligible"] is False
    assert result["profit_evidence"] is False
    assert result["next_action"] == "KEEP_MONITORING_EXISTING_TRADE_NO_NEW_ORDER"


def test_open_unrealized_positive_maps_to_watch_only_profit_evidence() -> None:
    result = refresh_trade_320_pl_result(open_trade("0.0004"))

    assert result["monitor_bucket"] == "OPEN_UNREALIZED_POSITIVE"
    assert result["result_bucket"] == OPEN_UNREALIZED_PROFIT_EVIDENCE
    assert result["profit_evidence"] is True
    assert result["repeat_proof_eligible"] is False


def test_closed_tp_positive_maps_to_repeat_eligible() -> None:
    result = refresh_trade_320_pl_result(
        closed_trade("0.0010", close_reason="TAKE_PROFIT_ORDER")
    )

    assert result["monitor_bucket"] == "CLOSED_TAKE_PROFIT_PROFIT"
    assert result["result_bucket"] == CLOSED_REALIZED_TAKE_PROFIT_EVIDENCE
    assert result["repeat_proof_eligible"] is True


def test_closed_other_profit_maps_to_repeat_eligible() -> None:
    result = refresh_trade_320_pl_result(
        closed_trade("0.0010", close_reason="manual_close")
    )

    assert result["monitor_bucket"] == "CLOSED_OTHER_PROFIT"
    assert result["result_bucket"] == CLOSED_REALIZED_OTHER_PROFIT_EVIDENCE
    assert result["repeat_proof_eligible"] is True


def test_closed_loss_maps_to_not_repeat_eligible() -> None:
    result = refresh_trade_320_pl_result(
        closed_trade("-0.0010", close_reason="STOP_LOSS_ORDER")
    )

    assert result["result_bucket"] == CLOSED_REALIZED_LOSS_EVIDENCE
    assert result["repeat_proof_lane_status"] == "BLOCKED_BY_LOSS"
    assert result["repeat_proof_eligible"] is False


def test_breakeven_maps_to_no_profit() -> None:
    result = refresh_trade_320_pl_result(closed_trade("0.0000"))

    assert result["monitor_bucket"] == "CLOSED_BREAKEVEN"
    assert result["result_bucket"] == CLOSED_BREAKEVEN_NO_PROFIT
    assert result["profit_evidence"] is False


def test_broker_evidence_blocked_maps_to_broker_blocked() -> None:
    result = refresh_trade_320_pl_result(
        {
            "evidence_source": "unit_test",
            "status": "BLOCKED_BY_MISSING_TOKEN",
            "blockers": ["vault_demo_access_token_missing"],
        }
    )

    assert result["monitor_bucket"] == "BROKER_EVIDENCE_BLOCKED"
    assert result["result_bucket"] == BROKER_EVIDENCE_BLOCKED
    assert result["broker_evidence_status"] == BROKER_EVIDENCE_BLOCKED
    assert result["repeat_proof_eligible"] is False


def test_trade_not_found_maps_to_trade_not_found() -> None:
    result = refresh_trade_320_pl_result(
        {
            "evidence_source": "unit_test",
            "broker_evidence_valid": True,
            "open_trades": {"trades": []},
            "closed_trades": [],
            "open_trade_count": 0,
        }
    )

    assert result["monitor_bucket"] == "NOT_FOUND"
    assert result["result_bucket"] == TRADE_NOT_FOUND


def test_invalid_evidence_maps_to_invalid_evidence() -> None:
    result = refresh_trade_320_pl_result({"open_trades": "invalid"})

    assert result["monitor_bucket"] == "INVALID_EVIDENCE"
    assert result["result_bucket"] == INVALID_EVIDENCE
    assert result["repeat_proof_eligible"] is False


def test_contradictory_evidence_cannot_be_repeat_eligible() -> None:
    open_payload = open_trade("0.0004")
    closed_payload = closed_trade("0.0010", close_reason="TAKE_PROFIT_ORDER")
    evidence = {
        "evidence_source": "unit_test",
        "open_trades": open_payload["open_trades"],
        "closed_trades": closed_payload["closed_trades"],
    }

    result = refresh_trade_320_pl_result(evidence)

    assert result["result_bucket"] == INVALID_EVIDENCE
    assert result["repeat_proof_eligible"] is False
    assert "expected_trade_appears_open_and_closed" in result["blockers"]


def test_cli_default_fixture_emits_json_without_broker_calls() -> None:
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["script_status"] == NO_PROFIT_EVIDENCE_OPEN_NEGATIVE
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False


def test_report_writer_includes_safety_statements(tmp_path: Path) -> None:
    result = refresh_trade_320_pl_result()
    report_path = tmp_path / "refresh_report.md"

    write_trade_320_read_only_pl_refresh_report(result, report_path)

    text = report_path.read_text(encoding="utf-8")
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text
