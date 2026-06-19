import json

from automation.forex_engine.paper_execution_simulator import (
    PaperExecutionSimulator,
    PaperExitPlanner,
    PaperReconciler,
    PaperRiskGate,
    PaperSignalEngine,
    TradingHistoryWriteback,
)


def test_signal_engine_returns_deterministic_buy_sell_none():
    buy_signal = PaperSignalEngine(selected_pair="EUR_USD").evaluate()
    sell_signal = PaperSignalEngine(selected_pair="GBP_USD").evaluate()
    none_signal = PaperSignalEngine(selected_pair="AUD_USD").evaluate()

    assert buy_signal["signal_side"] == "BUY"
    assert sell_signal["signal_side"] == "SELL"
    assert none_signal["signal_side"] == "NONE"
    assert buy_signal["label"] == "PAPER_SIGNAL_ONLY"
    assert buy_signal["live_execution_allowed"] is False


def test_risk_gate_blocks_oversize_duplicate_and_revenge_loop():
    signal = PaperSignalEngine(selected_pair="EUR_USD").evaluate()
    duplicate_signature = "EUR_USD|BUY|paper_fixture_expectancy_probe_v1"

    result = PaperRiskGate().evaluate(
        signal,
        requested_units=5000,
        recent_entry_signatures=[duplicate_signature],
        revenge_loop_detected=True,
    )

    assert result["risk_approval"] is False
    assert "max_paper_units_exceeded" in result["block_reason_list"]
    assert "no_duplicate_entry_rule_blocks_signal" in result["block_reason_list"]
    assert "no_revenge_loop_rule_blocks_signal" in result["block_reason_list"]
    assert result["broker_write_calls_allowed"] is False


def test_paper_entry_cannot_occur_without_risk_approval():
    signal = PaperSignalEngine(selected_pair="EUR_USD").evaluate()
    risk = PaperRiskGate().evaluate(signal, requested_units=5000)
    exit_plan = PaperExitPlanner().plan(signal)
    entry = PaperExecutionSimulator().create_entry(signal, risk, exit_plan)

    assert risk["risk_approval"] is False
    assert entry["paper_entry_created"] is False
    assert "risk_gate_must_approve_before_entry" in entry["block_reason_list"]
    assert entry["live_execution_allowed"] is False


def test_exit_plan_required_before_entry_completion():
    signal = PaperSignalEngine(selected_pair="EUR_USD").evaluate()
    risk = PaperRiskGate().evaluate(signal)
    missing_exit_plan = {"exit_plan_ready": False, "exit_plan_status": "BLOCKED"}
    entry = PaperExecutionSimulator().create_entry(signal, risk, missing_exit_plan)

    assert risk["risk_approval"] is True
    assert entry["paper_entry_created"] is False
    assert "exit_plan_required_before_entry_completion" in entry["block_reason_list"]


def test_reconciler_and_writeback_create_sanitized_history_row():
    signal = PaperSignalEngine(selected_pair="EUR_USD").evaluate()
    risk = PaperRiskGate().evaluate(signal)
    exit_plan = PaperExitPlanner().plan(signal)
    entry = PaperExecutionSimulator().create_entry(signal, risk, exit_plan)
    reconciliation = PaperReconciler().close_and_reconcile(entry, exit_plan)
    history = TradingHistoryWriteback().build(reconciliation)
    payload = json.dumps(history, sort_keys=True)

    assert reconciliation["paper_close_reconcile"] is True
    assert reconciliation["realized_paper_pl"] == 1.2
    assert history["trading_history_row_written"] is True
    assert history["history_rows"][0]["evidence_status"] == "PAPER_HISTORY_ROW_READY"
    assert "OANDA_API_TOKEN" not in payload
    assert "OANDA_ACCOUNT_ID" not in payload
    assert "transactionID" not in payload
    assert "orderID" not in payload
    assert history["live_execution_allowed"] is False
