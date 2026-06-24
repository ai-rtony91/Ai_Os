from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_open_trade_monitor_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED,
    CLOSED_BREAKEVEN,
    CLOSED_OTHER_LOSS,
    CLOSED_OTHER_PROFIT,
    CLOSED_STOP_LOSS_LOSS,
    CLOSED_TAKE_PROFIT_PROFIT,
    INVALID_EVIDENCE,
    NOT_FOUND,
    OPEN_UNREALIZED_FLAT,
    OPEN_UNREALIZED_NEGATIVE,
    OPEN_UNREALIZED_POSITIVE,
    classify_oanda_demo_trade_state,
    write_oanda_demo_open_trade_monitor_report,
)
from scripts.run_oanda_demo_open_trade_monitor_v1 import main as script_main  # noqa: E402


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


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_open_trade_unrealized_positive_is_profit_evidence():
    result = classify_oanda_demo_trade_state(open_trade("0.0004"))

    assert result["status_bucket"] == OPEN_UNREALIZED_POSITIVE
    assert result["is_profit_evidence"] is True
    assert result["is_open"] is True
    assert result["order_placement_performed"] is False


def test_open_trade_unrealized_negative_is_not_profit_evidence():
    result = classify_oanda_demo_trade_state(open_trade("-0.0004"))

    assert result["status_bucket"] == OPEN_UNREALIZED_NEGATIVE
    assert result["is_profit_evidence"] is False
    assert result["is_open"] is True


def test_open_trade_unrealized_flat():
    result = classify_oanda_demo_trade_state(open_trade("0.0000"))

    assert result["status_bucket"] == OPEN_UNREALIZED_FLAT
    assert result["is_profit_evidence"] is False


def test_closed_tp_positive_is_profit_evidence():
    result = classify_oanda_demo_trade_state(
        closed_trade("0.0010", close_reason="TAKE_PROFIT_ORDER")
    )

    assert result["status_bucket"] == CLOSED_TAKE_PROFIT_PROFIT
    assert result["is_profit_evidence"] is True
    assert result["is_closed"] is True


def test_closed_sl_loss():
    result = classify_oanda_demo_trade_state(
        closed_trade("-0.0010", close_reason="STOP_LOSS_ORDER")
    )

    assert result["status_bucket"] == CLOSED_STOP_LOSS_LOSS
    assert result["is_profit_evidence"] is False


def test_closed_breakeven():
    result = classify_oanda_demo_trade_state(closed_trade("0.0000"))

    assert result["status_bucket"] == CLOSED_BREAKEVEN
    assert result["is_profit_evidence"] is False


def test_closed_positive_without_tp_proof():
    result = classify_oanda_demo_trade_state(
        closed_trade("0.0010", close_reason="manual_close")
    )

    assert result["status_bucket"] == CLOSED_OTHER_PROFIT
    assert result["is_profit_evidence"] is True


def test_closed_loss_without_sl_proof():
    result = classify_oanda_demo_trade_state(
        closed_trade("-0.0010", close_reason="manual_close")
    )

    assert result["status_bucket"] == CLOSED_OTHER_LOSS


def test_expected_trade_absent_from_valid_evidence():
    evidence = {
        "evidence_source": "unit_test",
        "open_trades": {"trades": [{"id": "999", "state": "OPEN"}]},
        "closed_trades": [],
        "open_trade_count": 1,
    }

    result = classify_oanda_demo_trade_state(evidence)

    assert result["status_bucket"] == NOT_FOUND
    assert result["blockers"] == []


def test_broker_auth_vault_blocked_evidence():
    evidence = {
        "evidence_source": "unit_test",
        "status": "BLOCKED_BY_MISSING_TOKEN",
        "blockers": ["vault_demo_access_token_missing"],
    }

    result = classify_oanda_demo_trade_state(evidence)

    assert result["status_bucket"] == BROKER_EVIDENCE_BLOCKED
    assert result["is_broker_blocked"] is True


def test_malformed_pl_is_invalid_evidence():
    result = classify_oanda_demo_trade_state(open_trade("not-a-number"))

    assert result["status_bucket"] == INVALID_EVIDENCE
    assert "unrealized_pl_must_be_numeric" in result["blockers"]


def test_report_writer_states_no_new_order_no_live_trade_no_secrets(tmp_path):
    result = classify_oanda_demo_trade_state(open_trade("-0.0004"))
    report_path = tmp_path / "monitor_report.md"

    write_oanda_demo_open_trade_monitor_report(
        result,
        report_path,
        branch="feature/forex-oanda-demo-open-trade-monitor-v1",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "no new order was placed" in text
    assert "no live trade was placed" in text
    assert "no secrets were written" in text
    assert OPEN_UNREALIZED_NEGATIVE in text


def test_cli_reads_evidence_file_writes_report_and_prints_json(tmp_path):
    evidence_path = tmp_path / "evidence.json"
    report_path = tmp_path / "report.md"
    evidence_path.write_text(json.dumps(open_trade("-0.0004")), encoding="utf-8")

    code, payload = run_script(
        [
            "--evidence-file",
            str(evidence_path),
            "--expected-trade-id",
            "320",
            "--write-report",
            "--report-path",
            str(report_path),
            "--json",
        ]
    )

    assert code == 0
    assert payload["script_status"] == OPEN_UNREALIZED_NEGATIVE
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False
    assert report_path.exists()
