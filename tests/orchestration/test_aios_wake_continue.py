from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_wake_continue.py"
POLICY_SOURCE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_decision_policy.py"


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


def seed_report(repo_root: Path) -> None:
    report_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_report.py"
    test_path = repo_root / "tests" / "trading_lab" / "test_forex_report.py"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# report placeholder\n", encoding="utf-8")
    test_path.write_text("# report test placeholder\n", encoding="utf-8")


def seed_decision_policy(repo_root: Path) -> None:
    policy_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_decision_policy.py"
    test_path = repo_root / "tests" / "trading_lab" / "test_forex_decision_policy.py"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(POLICY_SOURCE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    test_path.write_text("# decision policy test placeholder\n", encoding="utf-8")


def seed_risk_controls(repo_root: Path) -> None:
    risk_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_risk_controls.py"
    test_path = repo_root / "tests" / "trading_lab" / "test_forex_risk_controls.py"
    risk_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    risk_path.write_text("# risk controls placeholder\n", encoding="utf-8")
    test_path.write_text("# risk controls test placeholder\n", encoding="utf-8")


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


def test_detects_data_import_present_selects_report_action(tmp_path):
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
        apply=False,
        max_cycles=3,
        max_repairs=1,
        state_path=state_path,
    )
    assert report["result"] == "preview_only"
    assert report["selected_action"] == "build_forex_report"


def test_detects_report_present_selects_decision_policy_action(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    seed_data_import(tmp_path)
    seed_report(tmp_path)
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
    assert report["selected_action"] == "build_forex_decision_policy"


def test_apply_validate_all_action_returns_done_and_writes_state(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    seed_data_import(tmp_path)
    seed_report(tmp_path)
    seed_decision_policy(tmp_path)
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
    assert report["goal_decision"]["schema"] == "AIOS_FOREX_GOAL_DECISION.v1"
    assert report["goal_decision"]["decision_bridge_passed"] is True
    assert report["goal_decision"]["decision"] == "continue_build"
    assert report["goal_decision"]["reason_code"] == "acceptable_report"
    assert report["goal_decision"]["next_build_recommendation"].startswith("Continue")
    assert report["next_build_plan"]["schema"] == "AIOS_NEXT_BUILD_PLAN.v1"
    assert report["next_build_plan"]["route"] == "build_next_paper_component"
    assert report["next_build_plan"]["next_component"] == "forex_risk_controls"
    assert report["bounded_executor_handoff"]["schema"] == "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1"
    assert report["bounded_executor_handoff"]["handoff_status"] == "ready"
    assert report["bounded_executor_handoff"]["allowed_action"] == "build_forex_risk_controls"
    assert report["cli_result_ingest"]["schema"] == "AIOS_CLI_RESULT_INGEST.v1"
    assert report["local_runner_bridge"]["schema"] == "AIOS_LOCAL_RUNNER_BRIDGE.v1"
    assert report["local_runner_bridge"]["runner_status"] == "preview_ready"
    assert report["bounded_executor_ready"]["schema"] == "AIOS_BOUNDED_EXECUTOR_READY.v1"
    assert report["bounded_executor_ready"]["status"] == "ready_for_human_review"
    assert report["resume_state"]["schema"] == "AIOS_RESUME_STATE.v1"
    assert report["resume_state"]["resume_ready"] is True
    assert report["operator_relay"]["schema"] == "AIOS_OPERATOR_RELAY.v1"
    assert report["operator_relay"]["codex_prompt_ready"] is True
    assert report["control_plane_status"]["schema"] == "AIOS_CONTROL_PLANE_STATUS.v1"
    assert report["control_plane_status"]["dashboard_ready"] is True
    assert report["next_safe_action"] == report["control_plane_status"]["next_action"]
    assert len(report["validators_run"]) == 1
    assert state["schema"] == "AIOS_WAKE_CONTINUE.v1"
    assert state["goal_decision"]["decision"] == "continue_build"
    assert state["next_build_plan"]["next_component"] == "forex_risk_controls"
    assert state["bounded_executor_handoff"]["handoff_status"] == "ready"
    assert report["resume_state_paths"] is None
    assert not (tmp_path / "Reports" / "aios_resume").exists()
    assert report["control_plane_status_path"] is None
    assert not (tmp_path / "Reports" / "aios_control_plane").exists()


def test_write_resume_state_persists_after_done_when_requested(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    seed_data_import(tmp_path)
    seed_report(tmp_path)
    seed_decision_policy(tmp_path)
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=tmp_path / "state.json",
        command_runner=passing_runner,
        write_resume_state_requested=True,
        resume_state_dir=tmp_path / "Reports" / "aios_resume",
        write_control_plane_status_requested=True,
        control_plane_dir=tmp_path / "Reports" / "aios_control_plane",
    )
    assert report["result"] == "DONE_FOR_CURRENT_GOAL"
    assert report["resume_state"]["schema"] == "AIOS_RESUME_STATE.v1"
    assert report["resume_state"]["resume_ready"] is True
    assert report["resume_state_paths"]["timestamped"].startswith("Reports/aios_resume/AIOS_RESUME_STATE_")
    assert report["resume_state_paths"]["latest"] == "Reports/aios_resume/AIOS_RESUME_STATE_latest.json"
    assert (tmp_path / report["resume_state_paths"]["timestamped"]).exists()
    assert (tmp_path / report["resume_state_paths"]["latest"]).exists()
    assert report["control_plane_status"]["dashboard_ready"] is True
    assert report["control_plane_status_path"] == "Reports/aios_control_plane/AIOS_CONTROL_PLANE_STATUS_latest.json"
    assert (tmp_path / report["control_plane_status_path"]).exists()
    assert report["next_safe_action"] == report["control_plane_status"]["next_action"]


def test_validate_all_with_risk_controls_returns_review_required(tmp_path):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    seed_data_import(tmp_path)
    seed_report(tmp_path)
    seed_decision_policy(tmp_path)
    seed_risk_controls(tmp_path)
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=tmp_path / "state.json",
        command_runner=passing_runner,
    )
    assert report["result"] == "REVIEW_REQUIRED"
    assert report["selected_action"] == "validate_all_forex_with_risk_controls"
    assert report["next_build_plan"]["next_component"] == "none"
    assert report["next_build_plan"]["reason_code"] == "forex_risk_controls_validated"
    assert "after risk controls" in report["next_safe_action"]


def test_validate_all_stop_route_returns_review_required(tmp_path, monkeypatch):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    seed_data_import(tmp_path)
    seed_report(tmp_path)
    seed_decision_policy(tmp_path)

    def stop_decision(_repo_root: Path, goal: str) -> dict[str, object]:
        return {
            "schema": "AIOS_FOREX_GOAL_DECISION.v1",
            "goal": goal,
            "decision_bridge_passed": True,
            "decision": "stop_for_human_review",
            "reason_code": "risk_flags_present",
            "decision_reasons": ["risk_flags_present"],
        }

    monkeypatch.setattr(module, "build_goal_decision", stop_decision)
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=tmp_path / "state.json",
        command_runner=passing_runner,
    )
    assert report["result"] == "REVIEW_REQUIRED"
    assert report["next_build_plan"]["route"] == "stop"
    assert report["next_build_plan"]["next_component"] == "none"
    assert report["bounded_executor_handoff"]["handoff_status"] == "stopped"
    assert report["next_safe_action"] == report["bounded_executor_handoff"]["next_safe_action"]


def test_validate_all_unsupported_handoff_returns_blocked(tmp_path, monkeypatch):
    module = load_module()
    seed_executor(tmp_path)
    seed_scaffold(tmp_path)
    seed_backtest(tmp_path)
    seed_ledger(tmp_path)
    seed_strategy(tmp_path)
    seed_data_import(tmp_path)
    seed_report(tmp_path)
    seed_decision_policy(tmp_path)

    def unsupported_plan(_goal_decision: dict[str, object]) -> dict[str, object]:
        return {
            "schema": "AIOS_NEXT_BUILD_PLAN.v1",
            "goal": "forex-paper-bot",
            "input_decision": "continue_build",
            "route": "build_next_paper_component",
            "next_component": "unsupported_component",
            "next_packet_id": "PKT-AIOS-UNSUPPORTED",
            "reason_code": "acceptable_report",
            "plan_reasons": ["acceptable_report"],
            "next_safe_action": "Unsupported preview.",
        }

    monkeypatch.setattr(module, "build_next_build_plan", unsupported_plan)
    report = module.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=tmp_path / "state.json",
        command_runner=passing_runner,
    )
    assert report["result"] == "BLOCKED"
    assert report["bounded_executor_handoff"]["handoff_status"] == "blocked"
    assert report["bounded_executor_handoff"]["reason_code"] == "unsupported_component"
    assert report["next_safe_action"] == report["bounded_executor_handoff"]["next_safe_action"]


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
    seed_report(tmp_path)
    seed_decision_policy(tmp_path)
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
