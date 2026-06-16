from __future__ import annotations

from pathlib import Path

from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import out_of_sample_validator


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "out_of_sample_validator.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def test_oos_splits_include_train_heldout_and_leave_one_groups() -> None:
    splits = out_of_sample_validator.build_oos_splits()

    assert splits["mode"] == "PAPER_ONLY"
    assert splits["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert splits["train_like_fixtures"]
    assert splits["heldout_fixtures"]
    assert splits["leave_one_regime_out"]
    assert splits["leave_one_symbol_out"]
    assert splits["leave_one_timeframe_out"]
    assert splits["network_allowed"] is False
    assert splits["broker_allowed"] is False
    assert splits["live_ready"] is False


def test_out_of_sample_validation_reports_heldout_and_leave_one_results() -> None:
    result = out_of_sample_validator.run_out_of_sample_validation()

    assert result["mode"] == "PAPER_ONLY"
    assert result["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert result["fixture_count"] >= 14
    assert result["heldout_count"] > 0
    assert result["train_like_count"] > 0
    assert result["heldout_pnl"] >= 0.0
    assert result["heldout_return_pct"] >= 0.0
    assert result["heldout_consistency_pct"] >= 0.0
    assert result["leave_one_regime_results"]
    assert result["leave_one_symbol_results"]
    assert result["leave_one_timeframe_results"]
    assert result["weakest_holdout"]
    assert result["strongest_holdout"]
    assert result["classification"] in ALLOWED_CLASSIFICATIONS
    assert result["classification"] != "LIVE_READY"
    assert result["live_ready"] is False
    assert result["protected_gate_required"] is True


def test_out_of_sample_summary_is_compact_and_never_live_ready() -> None:
    result = out_of_sample_validator.run_out_of_sample_validation()
    summary = out_of_sample_validator.summarize_oos_validation(result)

    assert summary["fixture_count"] == len(local_fixture_catalog.REQUIRED_FIXTURE_IDS)
    assert summary["fixture_count"] >= 14
    assert summary["heldout_count"] == result["heldout_count"]
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] != "LIVE_READY"
    assert summary["live_ready"] is False
    assert summary["protected_gate_required"] is True
    assert summary["next_safe_action"]


def test_oos_boundary_summary_blocks_broker_network_orders_and_live() -> None:
    boundary = out_of_sample_validator.oos_boundary_summary()

    assert boundary["local_simulation_only"] is True
    assert boundary["deterministic_fixtures_only"] is True
    assert boundary["broker_allowed"] is False
    assert boundary["broker_paper_orders"] is False
    assert boundary["network_allowed"] is False
    assert boundary["csv_ingestion"] is False
    assert boundary["api_ingestion"] is False
    assert boundary["credentials_allowed"] is False
    assert boundary["live_trading"] is False
    assert boundary["live_ready"] is False
    assert boundary["orders_allowed"] is False
    assert boundary["scheduler_allowed"] is False
    assert boundary["daemon_allowed"] is False


def test_oos_module_has_no_forbidden_imports_or_execution_calls() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    import_lines = "\n".join(
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    for forbidden_import in ("requests", "socket", "urllib", "subprocess", "os", "schedule", "daemon"):
        assert forbidden_import not in import_lines
    for forbidden_call in (
        "os.environ",
        "getenv",
        "broker_sdk",
        "import broker",
        "from broker",
        "oanda",
        "schedule.every",
        "daemon.daemoncontext",
        "open(",
        "write_text(",
        "write_bytes(",
        "start-process",
    ):
        assert forbidden_call not in source
