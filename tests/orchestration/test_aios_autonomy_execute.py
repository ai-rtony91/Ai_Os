from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_autonomy_execute.py"


def load_executor_module():
    spec = importlib.util.spec_from_file_location("aios_autonomy_execute", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_generated_bot(path: Path):
    spec = importlib.util.spec_from_file_location("forex_paper_bot", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def passing_validator(_repo_root: Path) -> dict[str, object]:
    return {
        "name": "fake_validator",
        "command": "fake",
        "returncode": 0,
        "passed": True,
        "stdout": "",
        "stderr": "",
    }


def test_autonomy_executor_imports():
    module = load_executor_module()
    assert module.SCHEMA == "AIOS_AUTONOMY_EXECUTE.v1"


def test_unsupported_goal_blocked():
    module = load_executor_module()
    report = module.execute_goal(REPO_ROOT, "unsupported-goal", apply=True, max_repairs=1)
    assert report["result"] == "blocked"
    assert report["blocked_reason"] == "unsupported_goal"
    assert report["files_written"] == []


def test_forex_paper_bot_goal_writes_files_in_temp_workspace(tmp_path):
    module = load_executor_module()
    report = module.execute_goal(
        tmp_path,
        "forex-paper-bot",
        apply=True,
        max_repairs=1,
        validator_runner=passing_validator,
    )
    assert report["result"] == "passed"
    assert sorted(report["files_written"]) == sorted(
        [
            "apps/trading_lab/trading_lab/forex_paper_bot.py",
            "tests/trading_lab/test_forex_paper_bot.py",
            "docs/orchestration/AIOS_FOREX_PAPER_BOT.md",
        ]
    )
    for relative_path in report["files_written"]:
        assert (tmp_path / relative_path).exists()


def test_generated_forex_bot_imports(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    assert bot.SUPPORTED_PAIRS == {"EURUSD", "GBPUSD", "USDJPY"}


def test_valid_eurusd_paper_signal_allowed(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("EURUSD", "buy", 1.1, 1.09, 10000, 1.0)
    assert decision["allowed"] is True
    assert decision["decision_type"] == "paper_decision_only"
    assert decision["mock_position_size"]["risk_amount"] == 100.0
    assert decision["execution_allowed"] is False
    assert decision["broker_execution"] is False
    assert decision["real_orders"] is False


def test_valid_gbpusd_sell_paper_signal_allowed(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("GBPUSD", "sell", 1.25, 1.26, 10000, 1.0)
    assert decision["allowed"] is True
    assert decision["direction"] == "sell"
    assert decision["execution_allowed"] is False


def test_live_execution_blocked(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("EURUSD", "buy", 1.1, 1.09, 10000, 1.0, live_execution=True)
    assert decision["allowed"] is False
    assert decision["blocked_reason"] == "live_execution_blocked"


def test_broker_order_blocked(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("EURUSD", "buy", 1.1, 1.09, 10000, 1.0, broker_order=True)
    assert decision["allowed"] is False
    assert decision["blocked_reason"] == "broker_order_blocked"


def test_credentials_blocked(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("EURUSD", "buy", 1.1, 1.09, 10000, 1.0, credentials={"token": "x"})
    assert decision["allowed"] is False
    assert decision["blocked_reason"] == "credentials_blocked"


def test_real_webhook_blocked(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision(
        "EURUSD",
        "buy",
        1.1,
        1.09,
        10000,
        1.0,
        webhook_url="https://example.invalid/hook",
    )
    assert decision["allowed"] is False
    assert decision["blocked_reason"] == "real_webhook_blocked"


def test_invalid_pair_blocked(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("AUDUSD", "buy", 1.1, 1.09, 10000, 1.0)
    assert decision["allowed"] is False
    assert decision["blocked_reason"] == "unsupported_pair"


def test_invalid_direction_blocked(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("EURUSD", "hold", 1.1, 1.09, 10000, 1.0)
    assert decision["allowed"] is False
    assert decision["blocked_reason"] == "unsupported_direction"


def test_missing_stop_loss_blocked(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("EURUSD", "buy", 1.1, None, 10000, 1.0)
    assert decision["allowed"] is False
    assert decision["blocked_reason"] == "stop_loss_required"


def test_high_risk_blocked(tmp_path):
    module = load_executor_module()
    module.execute_goal(tmp_path, "forex-paper-bot", apply=True, validator_runner=passing_validator)
    bot = load_generated_bot(tmp_path / "apps/trading_lab/trading_lab/forex_paper_bot.py")
    decision = bot.paper_decision("EURUSD", "buy", 1.1, 1.09, 10000, 5.0)
    assert decision["allowed"] is False
    assert decision["blocked_reason"] == "max_risk_percent_exceeds_paper_limit"


def test_safety_flags_deny_all_blocked_actions():
    module = load_executor_module()
    flags = module.safety_flags()
    assert flags
    assert all(value is False for value in flags.values())
    for key in [
        "git_add",
        "git_commit",
        "git_push",
        "merge",
        "delete_reset",
        "queue_mutation",
        "approval_mutation",
        "worker_launch",
        "runtime_launch",
        "scheduler",
        "daemon",
        "secrets",
        "broker_live_trading",
        "real_orders",
    ]:
        assert flags[key] is False


def test_repair_count_respects_max_repairs(tmp_path):
    module = load_executor_module()

    def failing_validator(_repo_root: Path) -> dict[str, object]:
        return {
            "name": "fake_validator",
            "command": "fake",
            "returncode": 1,
            "passed": False,
            "stdout": "",
            "stderr": "failed",
        }

    report = module.execute_goal(
        tmp_path,
        "forex-paper-bot",
        apply=True,
        max_repairs=1,
        validator_runner=failing_validator,
    )
    assert report["result"] == "failed"
    assert report["repair_attempts"] == 1
    assert len(report["validators_run"]) == 2


def test_cli_report_is_json_compatible(tmp_path, capsys):
    module = load_executor_module()
    exit_code = module.main(["--goal", "forex-paper-bot", "--repo-root", str(tmp_path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    report = json.loads(captured.out)
    assert report["schema"] == "AIOS_AUTONOMY_EXECUTE.v1"
    assert report["result"] == "preview_only"
    assert report["files_written"] == []
