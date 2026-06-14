from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_wake_continue.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_wake_continue", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def seed_executor(repo_root: Path) -> None:
    path = repo_root / "automation" / "orchestration" / "aios_autonomy_execute.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# executor placeholder\n", encoding="utf-8")


def seed_scaffold(repo_root: Path) -> None:
    bot_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_paper_bot.py"
    test_path = repo_root / "tests" / "trading_lab" / "test_forex_paper_bot.py"
    bot_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    bot_path.write_text("# bot placeholder\n", encoding="utf-8")
    test_path.write_text("# test placeholder\n", encoding="utf-8")


def seed_backtest(repo_root: Path) -> None:
    backtest_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_backtest.py"
    test_path = repo_root / "tests" / "trading_lab" / "test_forex_backtest.py"
    backtest_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    backtest_path.write_text("# backtest placeholder\n", encoding="utf-8")
    test_path.write_text("# backtest test placeholder\n", encoding="utf-8")


def seed_ledger(repo_root: Path) -> None:
    ledger_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_paper_ledger.py"
    test_path = repo_root / "tests" / "trading_lab" / "test_forex_paper_ledger.py"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text("# ledger placeholder\n", encoding="utf-8")
    test_path.write_text("# ledger test placeholder\n", encoding="utf-8")


def seed_strategy(repo_root: Path) -> None:
    strategy_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_strategy_rules.py"
    test_path = repo_root / "tests" / "trading_lab" / "test_forex_strategy_rules.py"
    strategy_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    strategy_path.write_text("# strategy placeholder\n", encoding="utf-8")
    test_path.write_text("# strategy test placeholder\n", encoding="utf-8")


def seed_data_import(repo_root: Path) -> None:
    data_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_data_import.py"
    test_path = repo_root / "tests" / "trading_lab" / "test_forex_data_import.py"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text("# data import placeholder\n", encoding="utf-8")
    test_path.write_text("# data import test placeholder\n", encoding="utf-8")


def passing_runner(command: list[str], _repo_root: Path) -> dict[str, object]:
    return {
        "command": " ".join(command),
        "returncode": 0,
        "passed": True,
        "stdout": "",
        "stderr": "",
    }


def test_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_WAKE_CONTINUE.v1"


def test_unsupported_goal_blocked(tmp_path):
    module = load_module()
    state_path = tmp_path / "state.json"
    report = module.run_wake_continue(
        tmp_path,
        goal="unsupported",
        apply=True,
        max_cycles=1,
        max_repairs=1,
        state_path=state_path,
        command_runner=passing_runner,
    )
    assert report["result"] == "blocked"
    assert report["blocked_reason"] == "unsupported_goal"
    assert state_path.exists()


def test_detects_scaffold_missing_selects_build_action(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    state_path = tmp_path / "state.json"
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=False,
        max_cycles=3,
        max_repairs=1,
        state_path=state_path,
    )
    assert report["result"] == "preview_only"
    assert report["selected_action"] == "build_forex_scaffold"


def test_detects_scaffold_present_selects_backtest_action(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    state_path = tmp_path / "state.json"
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=False,
        max_cycles=3,
        max_repairs=1,
        state_path=state_path,
    )
    assert report["result"] == "preview_only"
    assert report["selected_action"] == "build_forex_backtest"


def test_detects_scaffold_and_backtest_present_selects_ledger_action(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    state_path = tmp_path / "state.json"
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=False,
        max_cycles=3,
        max_repairs=1,
        state_path=state_path,
    )
    assert report["result"] == "preview_only"
    assert report["selected_action"] == "build_forex_ledger"


def test_detects_scaffold_backtest_and_ledger_present_selects_strategy_action(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    state_path = tmp_path / "state.json"
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=False,
        max_cycles=3,
        max_repairs=1,
        state_path=state_path,
    )
    assert report["result"] == "preview_only"
    assert report["selected_action"] == "build_forex_strategy"


def test_detects_prior_forex_components_present_selects_data_import_action(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    state_path = tmp_path / "state.json"
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=False,
        max_cycles=3,
        max_repairs=1,
        state_path=state_path,
    )
    assert report["result"] == "preview_only"
    assert report["selected_action"] == "build_forex_data_import"


def test_apply_validate_all_action_returns_done_and_writes_state(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    seed_data_import(tmp_path)
    state_path = tmp_path / "state.json"
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=state_path,
        command_runner=passing_runner,
    )
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert report["result"] == "DONE_FOR_CURRENT_GOAL"
    assert report["selected_action"] == "validate_all_forex"
    assert len(report["validators_run"]) == 1
    assert state["schema"] == "AIOS_WAKE_CONTINUE.v1"


def test_max_cycles_respected(tmp_path):
    module = load_module()
    seed_executor(tmp_path)

    def build_without_materializing(command: list[str], _repo_root: Path) -> dict[str, object]:
        return {
            "command": " ".join(command),
            "returncode": 0,
            "passed": True,
            "stdout": "",
            "stderr": "",
        }

    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=1,
        max_repairs=0,
        state_path=tmp_path / "state.json",
        command_runner=build_without_materializing,
    )
    assert report["result"] == "max_cycles_reached"
    assert len(report["commands_run"]) == 1


def test_safety_blocks_all_forbidden_actions():
    module = load_module()
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
        "worker_dispatch",
        "runtime_launch",
        "scheduler",
        "daemon",
        "secrets",
        "broker",
        "live_trading",
        "real_orders",
    ]:
        assert flags[key] is False


def test_source_has_no_forbidden_command_or_ui_paths():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    assert "apps/dashboard" not in source
    for command in ["git add", "git commit", "git push", "git merge"]:
        assert command not in source


def test_cli_main_writes_state_in_temp_path(tmp_path, capsys):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    seed_data_import(tmp_path)
    state_path = tmp_path / "state.json"
    exit_code = module.main(
        [
            "--goal",
            "forex-paper-bot",
            "--repo-root",
            str(tmp_path),
            "--state-path",
            str(state_path),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    report = json.loads(captured.out)
    assert report["result"] == "preview_only"
    assert report["selected_action"] == "validate_all_forex"
    assert state_path.exists()
