from pathlib import Path

import pytest

from automation.forex_engine import broker_paper_dryrun_intent_ledger
from automation.forex_engine import broker_paper_dryrun_risk_governor


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_paper_dryrun_risk_governor.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_broker_paper_dryrun_risk_governor_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "DRYRUN_RISK_GOVERNOR_READY"}


def _intent(**overrides):
    payload = {
        "symbol": "EURUSD_FAKE",
        "side": "buy",
        "quantity_units": 500,
        "order_type": "market_stub",
        "stop_loss_pips": 8.0,
        "take_profit_pips": 12.0,
        "max_loss_usd": 1.0,
        "dry_run": True,
        "approved_by_operator": True,
    }
    payload.update(overrides)
    return payload


def _record(**overrides):
    return broker_paper_dryrun_intent_ledger.create_dryrun_intent_record(_intent(**overrides))


def test_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_policy_includes_blocked_capability_flags_and_conservative_caps() -> None:
    policy = broker_paper_dryrun_risk_governor.build_broker_paper_dryrun_risk_policy()

    assert policy["mode"] == "PAPER_ONLY_DRYRUN_RISK_GOVERNOR"
    for field in (
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "env_secret_read_allowed",
        "webhook_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
        "file_writes_allowed",
        "reports_writes_allowed",
    ):
        assert policy[field] is False
    assert policy["manual_approval_required"] is True
    assert policy["presecurity_gate_required"] is True
    assert policy["stub_contract_required"] is True
    assert policy["dryrun_ledger_required"] is True
    assert policy["kill_switch_required"] is True
    assert policy["kill_switch_armed"] is True
    assert policy["max_loss_guard_required"] is True
    assert policy["daily_stop_required"] is True
    assert policy["audit_log_required"] is True
    assert policy["max_loss_usd_per_intent"] == 2.00
    assert policy["max_daily_loss_usd"] == 5.00
    assert policy["max_intents_per_day"] == 3
    assert policy["max_quantity_units"] == 1000
    assert {"EURUSD", "GBPUSD", "USDJPY"}.issubset(set(policy["approved_symbol_allowlist"]))
    assert "BTCUSD" in policy["rejected_symbol_blocklist"]


def test_accepted_fake_dryrun_record_is_accepted_by_risk_governor_only() -> None:
    decision = broker_paper_dryrun_risk_governor.evaluate_dryrun_intent_risk(_record())

    assert decision["accepted_by_risk_governor"] is True
    assert decision["risk_decision"] == "ACCEPTED_DRYRUN_ONLY"
    assert decision["classification"] == "DRYRUN_RISK_GOVERNOR_READY"
    assert decision["would_place_order"] is False
    assert decision["order_placed"] is False
    assert decision["broker_request_sent"] is False
    assert decision["network_used"] is False
    assert decision["credentials_used"] is False
    assert decision["live_ready"] is False
    assert decision["broker_paper_orders_allowed"] is False


def test_over_loss_fake_record_is_rejected() -> None:
    decision = broker_paper_dryrun_risk_governor.evaluate_dryrun_intent_risk(
        _record(max_loss_usd=3.0)
    )

    assert decision["accepted_by_risk_governor"] is False
    assert decision["risk_decision"] == "REJECTED"
    assert "max_loss_usd_exceeds_per_intent_cap" in decision["rejection_reasons"]


def test_missing_stop_loss_fake_record_is_rejected() -> None:
    record = _record()
    record["stop_loss_pips"] = None

    decision = broker_paper_dryrun_risk_governor.evaluate_dryrun_intent_risk(record)

    assert decision["accepted_by_risk_governor"] is False
    assert "stop_loss_pips_required" in decision["rejection_reasons"]


def test_symbol_outside_allowlist_is_rejected() -> None:
    decision = broker_paper_dryrun_risk_governor.evaluate_dryrun_intent_risk(
        _record(symbol="BTCUSD")
    )

    assert decision["accepted_by_risk_governor"] is False
    assert "symbol_blocklisted" in decision["rejection_reasons"]
    assert "symbol_not_in_risk_allowlist" in decision["rejection_reasons"]


@pytest.mark.parametrize(
    "field",
    (
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
        "broker_paper_orders_allowed",
    ),
)
def test_any_execution_flag_true_causes_rejection(field: str) -> None:
    record = _record()
    record[field] = True

    decision = broker_paper_dryrun_risk_governor.evaluate_dryrun_intent_risk(record)

    assert decision["accepted_by_risk_governor"] is False
    assert f"{field}_must_be_false" in decision["rejection_reasons"]
    assert decision[field] is False


def test_ledger_summary_counts_accepted_and_rejected_records() -> None:
    result = broker_paper_dryrun_risk_governor.evaluate_dryrun_ledger_risk()
    summary = broker_paper_dryrun_risk_governor.summarize_dryrun_risk_governor(result)

    assert summary["records_count"] == 2
    assert summary["risk_accepted"] == 1
    assert summary["risk_rejected"] == 1
    assert summary["classification"] == "DRYRUN_RISK_GOVERNOR_READY"
    assert summary["broker_paper_dryrun_risk_governor_ready"] is True


def test_aggregate_daily_loss_over_cap_is_rejected() -> None:
    ledger = broker_paper_dryrun_intent_ledger.replay_dryrun_intent_batch(
        [
            _intent(max_loss_usd=2.0, side="buy"),
            _intent(max_loss_usd=2.0, side="sell"),
            _intent(max_loss_usd=2.0, order_type="limit_stub"),
        ]
    )

    result = broker_paper_dryrun_risk_governor.evaluate_dryrun_ledger_risk(ledger)

    assert result["risk_accepted"] == 3
    assert result["aggregate_max_loss_usd"] == 6.0
    assert "aggregate_max_loss_exceeds_daily_cap" in result["blockers"]
    assert result["classification"] == "WATCHLIST"


def test_classification_is_limited_to_allowed_values_and_never_live_or_order_ready() -> None:
    result = broker_paper_dryrun_risk_governor.evaluate_dryrun_ledger_risk()
    summary = broker_paper_dryrun_risk_governor.summarize_dryrun_risk_governor(result)

    assert result["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    for forbidden in ("LIVE_READY", "BROKER_READY", "ORDER_READY"):
        assert broker_paper_dryrun_risk_governor.classify_dryrun_risk_governor(
            {"classification": forbidden}
        ) == "FAIL"


def test_boundary_summary_preserves_local_only_contract() -> None:
    summary = broker_paper_dryrun_risk_governor.broker_paper_dryrun_risk_governor_boundary_summary()

    assert summary["risk_governor_only"] is True
    assert summary["ledger_storage"] == "IN_MEMORY_ONLY"
    assert summary["broker_sdk_allowed"] is False
    assert summary["network_api_allowed"] is False
    assert summary["credentials_allowed"] is False
    assert summary["env_secret_read_allowed"] is False
    assert summary["webhook_allowed"] is False
    assert summary["scheduler_allowed"] is False
    assert summary["daemon_allowed"] is False
    assert summary["broker_paper_orders_allowed"] is False
    assert summary["live_orders_allowed"] is False
    assert summary["file_writes_allowed"] is False
    assert summary["reports_writes_allowed"] is False
    assert summary["kill_switch_armed"] is True
    assert (
        summary["next_safe_packet_after_dryrun_risk_governor"]
        == "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1"
    )


def test_demo_imports_and_prints_required_lines(capsys) -> None:
    from automation.forex_engine import run_broker_paper_dryrun_risk_governor_demo

    assert run_broker_paper_dryrun_risk_governor_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Broker-Paper Dry-Run Risk Governor Demo" in output
    assert "Mode: PAPER_ONLY_DRYRUN_RISK_GOVERNOR" in output
    assert "Broker SDK allowed: false" in output
    assert "Network/API allowed: false" in output
    assert "Credentials allowed: false" in output
    assert "Broker-paper orders allowed: false" in output
    assert "Live orders allowed: false" in output
    assert "Would place order: false" in output
    assert "Order placed: false" in output
    assert "Safety: dry-run risk governor only; no broker/API/network/orders/secrets/live execution." in output


def test_modules_have_no_forbidden_imports_or_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "dotenv"):
            assert forbidden_import not in import_lines
        for line in import_lines.splitlines():
            assert not line.startswith("import broker")
            assert not line.startswith("from broker")
            assert not line.startswith("import oanda")
            assert not line.startswith("from oanda")
            assert not line.startswith("import mt5")
            assert not line.startswith("from mt5")
            assert not line.startswith("import ibkr")
            assert not line.startswith("from ibkr")
        for forbidden_call in (
            "os.environ",
            "getenv",
            "open(",
            "path.write_text",
            "path.write_bytes",
            "subprocess",
            "schedule.every",
            "daemon.daemoncontext",
        ):
            assert forbidden_call not in source
