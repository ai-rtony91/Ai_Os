from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_productive_bounded_executor.py"
WAKE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_wake_continue.py"
AUTONOMY_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_autonomy_execute.py"
POLICY_SOURCE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_decision_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_productive_bounded_executor", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_wake_module():
    spec = importlib.util.spec_from_file_location("aios_wake_continue", WAKE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_autonomy_module():
    spec = importlib.util.spec_from_file_location("aios_autonomy_execute", AUTONOMY_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def passing_validator(_repo_root: Path) -> dict[str, object]:
    return {
        "name": "fake_validator",
        "command": "python -m pytest -p no:cacheprovider tests/trading_lab/test_forex_risk_controls.py",
        "returncode": 0,
        "passed": True,
        "stdout": "",
        "stderr": "",
    }


def passing_simulator_validator(_repo_root: Path) -> dict[str, object]:
    return {
        "name": "fake_simulator_validator",
        "command": "python -m pytest -p no:cacheprovider tests/trading_lab/test_forex_paper_execution_simulator.py",
        "returncode": 0,
        "passed": True,
        "stdout": "",
        "stderr": "",
    }


def passing_integration_validator(_repo_root: Path) -> dict[str, object]:
    return {
        "name": "fake_integration_validator",
        "command": "python -m pytest -p no:cacheprovider tests/trading_lab/test_forex_execution_ledger_integration.py",
        "returncode": 0,
        "passed": True,
        "stdout": "",
        "stderr": "",
    }


def passing_portfolio_validator(_repo_root: Path) -> dict[str, object]:
    return {
        "name": "fake_portfolio_validator",
        "command": "python -m pytest -p no:cacheprovider tests/trading_lab/test_forex_portfolio_state.py",
        "returncode": 0,
        "passed": True,
        "stdout": "",
        "stderr": "",
    }


def failing_validator(_repo_root: Path) -> dict[str, object]:
    return {
        "name": "fake_validator",
        "command": "python -m pytest -p no:cacheprovider tests/trading_lab/test_forex_risk_controls.py",
        "returncode": 1,
        "passed": False,
        "stdout": "",
        "stderr": "formatting failure",
    }


def passing_command_runner(command: list[str], _repo_root: Path) -> dict[str, object]:
    return {
        "command": " ".join(command),
        "returncode": 0,
        "passed": True,
        "stdout": "",
        "stderr": "",
    }


def handoff() -> dict[str, object]:
    return {
        "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
        "goal": "forex-paper-bot",
        "handoff_status": "ready",
        "allowed_action": "build_forex_risk_controls",
        "allowed_paths": [
            "apps/trading_lab/trading_lab/forex_risk_controls.py",
            "tests/trading_lab/test_forex_risk_controls.py",
            "docs/orchestration/AIOS_FOREX_RISK_CONTROLS.md",
            "automation/orchestration/aios_autonomy_execute.py",
            "tests/orchestration/test_aios_autonomy_execute.py",
            "automation/orchestration/aios_wake_continue.py",
            "tests/orchestration/test_aios_wake_continue.py",
        ],
    }


def simulator_handoff() -> dict[str, object]:
    return {
        "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
        "goal": "forex-paper-bot",
        "handoff_status": "ready",
        "allowed_action": "build_forex_paper_execution_simulator",
        "allowed_paths": [
            "apps/trading_lab/trading_lab/forex_paper_execution_simulator.py",
            "tests/trading_lab/test_forex_paper_execution_simulator.py",
            "docs/orchestration/AIOS_FOREX_PAPER_EXECUTION_SIMULATOR.md",
            "automation/orchestration/aios_productive_bounded_executor.py",
            "tests/orchestration/test_aios_productive_bounded_executor.py",
            "automation/orchestration/aios_wake_continue.py",
            "tests/orchestration/test_aios_wake_continue.py",
        ],
    }


def integration_handoff() -> dict[str, object]:
    return {
        "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
        "goal": "forex-paper-bot",
        "handoff_status": "ready",
        "allowed_action": "build_forex_execution_ledger_integration",
        "allowed_paths": [
            "apps/trading_lab/trading_lab/forex_execution_ledger_integration.py",
            "tests/trading_lab/test_forex_execution_ledger_integration.py",
            "docs/orchestration/AIOS_FOREX_EXECUTION_LEDGER_INTEGRATION.md",
            "automation/orchestration/aios_productive_bounded_executor.py",
            "tests/orchestration/test_aios_productive_bounded_executor.py",
            "automation/orchestration/aios_wake_continue.py",
            "tests/orchestration/test_aios_wake_continue.py",
        ],
    }


def portfolio_handoff() -> dict[str, object]:
    return {
        "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
        "goal": "forex-paper-bot",
        "handoff_status": "ready",
        "allowed_action": "build_forex_portfolio_state",
        "allowed_paths": [
            "apps/trading_lab/trading_lab/forex_portfolio_state.py",
            "tests/trading_lab/test_forex_portfolio_state.py",
            "docs/orchestration/AIOS_FOREX_PORTFOLIO_STATE.md",
            "automation/orchestration/aios_productive_bounded_executor.py",
            "tests/orchestration/test_aios_productive_bounded_executor.py",
            "automation/orchestration/aios_wake_continue.py",
            "tests/orchestration/test_aios_wake_continue.py",
        ],
    }


def seed_executor(repo_root: Path) -> None:
    path = repo_root / "automation" / "orchestration" / "aios_autonomy_execute.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# executor placeholder\n", encoding="utf-8")


def seed_existing_forex_components(repo_root: Path) -> None:
    component_paths = [
        "apps/trading_lab/trading_lab/forex_paper_bot.py",
        "tests/trading_lab/test_forex_paper_bot.py",
        "apps/trading_lab/trading_lab/forex_backtest.py",
        "tests/trading_lab/test_forex_backtest.py",
        "apps/trading_lab/trading_lab/forex_paper_ledger.py",
        "tests/trading_lab/test_forex_paper_ledger.py",
        "apps/trading_lab/trading_lab/forex_strategy_rules.py",
        "tests/trading_lab/test_forex_strategy_rules.py",
        "apps/trading_lab/trading_lab/forex_data_import.py",
        "tests/trading_lab/test_forex_data_import.py",
        "apps/trading_lab/trading_lab/forex_report.py",
        "tests/trading_lab/test_forex_report.py",
        "tests/trading_lab/test_forex_decision_policy.py",
    ]
    for relative_path in component_paths:
        target = repo_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# placeholder\n", encoding="utf-8")
    policy_path = repo_root / "apps" / "trading_lab" / "trading_lab" / "forex_decision_policy.py"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(POLICY_SOURCE_PATH.read_text(encoding="utf-8"), encoding="utf-8")


def test_productive_bounded_executor_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_PRODUCTIVE_BOUNDED_EXECUTOR.v1"
    assert callable(module.execute_productive_bounded_action)


def test_dry_run_writes_no_files(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_risk_controls",
    )
    assert report["result"] == "preview_only"
    assert report["mode"] == "DRY_RUN"
    assert report["files_written"] == []
    assert not (tmp_path / "apps" / "trading_lab" / "trading_lab" / "forex_risk_controls.py").exists()


def test_dry_run_for_execution_simulator_writes_no_files(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_paper_execution_simulator",
    )
    assert report["result"] == "preview_only"
    assert report["mode"] == "DRY_RUN"
    assert report["files_written"] == []
    assert not (tmp_path / "apps" / "trading_lab" / "trading_lab" / "forex_paper_execution_simulator.py").exists()


def test_dry_run_for_execution_ledger_integration_writes_no_files(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_execution_ledger_integration",
    )
    assert report["result"] == "preview_only"
    assert report["mode"] == "DRY_RUN"
    assert report["files_written"] == []
    assert not (tmp_path / "apps" / "trading_lab" / "trading_lab" / "forex_execution_ledger_integration.py").exists()


def test_dry_run_for_portfolio_state_writes_no_files(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_portfolio_state",
    )
    assert report["result"] == "preview_only"
    assert report["mode"] == "DRY_RUN"
    assert report["files_written"] == []
    assert not (tmp_path / "apps" / "trading_lab" / "trading_lab" / "forex_portfolio_state.py").exists()


def test_apply_writes_only_allowlisted_risk_control_files(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_risk_controls",
        apply=True,
        max_repairs=1,
        validator_runner=passing_validator,
    )
    assert report["result"] == "passed"
    assert sorted(report["files_written"]) == sorted(module.WRITE_ALLOWED_PATHS)
    for relative_path in module.WRITE_ALLOWED_PATHS:
        assert (tmp_path / relative_path).exists()
    assert not (tmp_path / "automation" / "orchestration" / "aios_wake_continue.py").exists()


def test_apply_writes_only_allowlisted_execution_simulator_files(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_paper_execution_simulator",
        apply=True,
        max_repairs=1,
        validator_runner=passing_simulator_validator,
    )
    assert report["result"] == "passed"
    assert sorted(report["files_written"]) == sorted(module.SIMULATOR_WRITE_ALLOWED_PATHS)
    for relative_path in module.SIMULATOR_WRITE_ALLOWED_PATHS:
        assert (tmp_path / relative_path).exists()
    assert not (tmp_path / "automation" / "orchestration" / "aios_productive_bounded_executor.py").exists()


def test_apply_writes_only_allowlisted_execution_ledger_integration_files(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_execution_ledger_integration",
        apply=True,
        max_repairs=1,
        validator_runner=passing_integration_validator,
    )
    assert report["result"] == "passed"
    assert sorted(report["files_written"]) == sorted(module.INTEGRATION_WRITE_ALLOWED_PATHS)
    for relative_path in module.INTEGRATION_WRITE_ALLOWED_PATHS:
        assert (tmp_path / relative_path).exists()
    assert not (tmp_path / "automation" / "orchestration" / "aios_productive_bounded_executor.py").exists()


def test_apply_writes_only_allowlisted_portfolio_state_files(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_portfolio_state",
        apply=True,
        max_repairs=1,
        validator_runner=passing_portfolio_validator,
    )
    assert report["result"] == "passed"
    assert sorted(report["files_written"]) == sorted(module.PORTFOLIO_WRITE_ALLOWED_PATHS)
    for relative_path in module.PORTFOLIO_WRITE_ALLOWED_PATHS:
        assert (tmp_path / relative_path).exists()
    assert not (tmp_path / "automation" / "orchestration" / "aios_productive_bounded_executor.py").exists()


def test_accepts_bounded_handoff_fixture(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        handoff=handoff(),
        apply=True,
        validator_runner=passing_validator,
    )
    assert report["result"] == "passed"
    assert report["action"] == "build_forex_risk_controls"
    assert "automation/orchestration/aios_wake_continue.py" in report["allowed_paths"]


def test_accepts_execution_simulator_bounded_handoff_fixture(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        handoff=simulator_handoff(),
        apply=True,
        validator_runner=passing_simulator_validator,
    )
    assert report["result"] == "passed"
    assert report["action"] == "build_forex_paper_execution_simulator"
    assert "automation/orchestration/aios_productive_bounded_executor.py" in report["allowed_paths"]


def test_accepts_execution_ledger_integration_bounded_handoff_fixture(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        handoff=integration_handoff(),
        apply=True,
        validator_runner=passing_integration_validator,
    )
    assert report["result"] == "passed"
    assert report["action"] == "build_forex_execution_ledger_integration"
    assert "automation/orchestration/aios_productive_bounded_executor.py" in report["allowed_paths"]


def test_accepts_portfolio_state_bounded_handoff_fixture(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        handoff=portfolio_handoff(),
        apply=True,
        validator_runner=passing_portfolio_validator,
    )
    assert report["result"] == "passed"
    assert report["action"] == "build_forex_portfolio_state"
    assert "automation/orchestration/aios_productive_bounded_executor.py" in report["allowed_paths"]


def test_rejects_unsupported_action(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="unsupported",
        apply=True,
        validator_runner=passing_validator,
    )
    assert report["result"] == "blocked"
    assert report["blocked_reason"] == "unsupported_action"
    assert report["files_written"] == []


def test_rejects_unbounded_path_in_handoff(tmp_path):
    module = load_module()
    unsafe = handoff()
    unsafe["allowed_paths"] = ["../outside.py"]
    report = module.execute_productive_bounded_action(
        tmp_path,
        handoff=unsafe,
        apply=True,
        validator_runner=passing_validator,
    )
    assert report["result"] == "blocked"
    assert report["blocked_reason"] == "unbounded_path"


def test_reports_validator_pass(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_risk_controls",
        apply=True,
        validator_runner=passing_validator,
    )
    assert report["validators_run"][0]["passed"] is True
    assert report["validators_run"][0]["name"] == "fake_validator"


def test_reports_execution_simulator_validator_pass(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_paper_execution_simulator",
        apply=True,
        validator_runner=passing_simulator_validator,
    )
    assert report["validators_run"][0]["passed"] is True
    assert report["validators_run"][0]["name"] == "fake_simulator_validator"


def test_reports_execution_ledger_integration_validator_pass(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_execution_ledger_integration",
        apply=True,
        validator_runner=passing_integration_validator,
    )
    assert report["validators_run"][0]["passed"] is True
    assert report["validators_run"][0]["name"] == "fake_integration_validator"


def test_reports_portfolio_state_validator_pass(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_portfolio_state",
        apply=True,
        validator_runner=passing_portfolio_validator,
    )
    assert report["validators_run"][0]["passed"] is True
    assert report["validators_run"][0]["name"] == "fake_portfolio_validator"


def test_reports_no_protected_actions_or_runtime_activation(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_risk_controls",
        apply=True,
        validator_runner=passing_validator,
    )
    assert report["approval_required"]["commit"] is True
    assert report["approval_required"]["push"] is True
    assert report["approval_required"]["merge"] is True
    for key in ["git_add", "git_commit", "git_push", "merge", "scheduler", "daemon", "worker_dispatch"]:
        assert report["safety"][key] is False


def test_one_repair_max(tmp_path):
    module = load_module()
    report = module.execute_productive_bounded_action(
        tmp_path,
        goal="forex-paper-bot",
        action="build_forex_risk_controls",
        apply=True,
        max_repairs=1,
        validator_runner=failing_validator,
    )
    assert report["result"] == "failed"
    assert report["repair_attempts"] == 1
    assert len(report["validators_run"]) == 2


def test_wake_continue_recognizes_risk_controls_after_created(tmp_path):
    product = load_module()
    wake = load_wake_module()
    seed_executor(tmp_path)
    seed_existing_forex_components(tmp_path)
    product.write_risk_controls_files(tmp_path)
    report = wake.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=tmp_path / "state.json",
        command_runner=passing_command_runner,
    )
    assert report["selected_action"] == "validate_all_forex_with_risk_controls"
    assert report["result"] == "DONE_FOR_CURRENT_GOAL"
    assert report["post_risk_decision"]["selected_next_component"] == "forex_paper_execution_simulator"
    assert report["next_build_plan"]["next_component"] == "forex_paper_execution_simulator"
    assert report["bounded_executor_handoff"]["allowed_action"] == "build_forex_paper_execution_simulator"


def test_wake_continue_recognizes_execution_simulator_after_created(tmp_path):
    product = load_module()
    wake = load_wake_module()
    seed_executor(tmp_path)
    seed_existing_forex_components(tmp_path)
    product.write_risk_controls_files(tmp_path)
    product.write_execution_simulator_files(tmp_path)
    report = wake.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=tmp_path / "state.json",
        command_runner=passing_command_runner,
    )
    assert report["selected_action"] == "validate_all_forex_with_risk_controls_and_execution_simulator"
    assert report["result"] == "DONE_FOR_CURRENT_GOAL"
    assert report["next_build_plan"]["next_component"] == "forex_execution_ledger_integration"
    assert report["bounded_executor_handoff"]["allowed_action"] == "build_forex_execution_ledger_integration"


def test_wake_continue_recognizes_execution_ledger_integration_after_created(tmp_path):
    product = load_module()
    wake = load_wake_module()
    seed_executor(tmp_path)
    seed_existing_forex_components(tmp_path)
    product.write_risk_controls_files(tmp_path)
    product.write_execution_simulator_files(tmp_path)
    product.write_execution_ledger_integration_files(tmp_path)
    report = wake.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=tmp_path / "state.json",
        command_runner=passing_command_runner,
    )
    assert report["selected_action"] == "validate_all_forex_with_execution_ledger_integration"
    assert report["result"] == "DONE_FOR_CURRENT_GOAL"
    assert "tests/trading_lab/test_forex_execution_ledger_integration.py" in report["validators_run"][0]["command"]
    assert report["next_build_plan"]["next_component"] == "forex_portfolio_state"
    assert report["bounded_executor_handoff"]["handoff_status"] == "ready"
    assert report["bounded_executor_handoff"]["allowed_action"] == "build_forex_portfolio_state"


def test_wake_continue_recognizes_portfolio_state_after_created(tmp_path):
    product = load_module()
    wake = load_wake_module()
    seed_executor(tmp_path)
    seed_existing_forex_components(tmp_path)
    product.write_risk_controls_files(tmp_path)
    product.write_execution_simulator_files(tmp_path)
    product.write_execution_ledger_integration_files(tmp_path)
    product.write_portfolio_state_files(tmp_path)
    report = wake.run_wake_continue(
        tmp_path,
        goal="forex-paper-bot",
        apply=True,
        max_cycles=3,
        max_repairs=1,
        state_path=tmp_path / "state.json",
        command_runner=passing_command_runner,
    )
    assert report["selected_action"] == "validate_all_forex_with_portfolio_state"
    assert report["result"] == "REVIEW_REQUIRED"
    assert "tests/trading_lab/test_forex_portfolio_state.py" in report["validators_run"][0]["command"]
    assert report["bounded_executor_handoff"]["handoff_status"] == "stopped"


def test_autonomy_execute_validation_includes_risk_controls_after_created(tmp_path):
    product = load_module()
    autonomy = load_autonomy_module()
    autonomy.write_forex_scaffold(tmp_path)
    autonomy.write_forex_backtest(tmp_path)
    autonomy.write_forex_ledger(tmp_path)
    autonomy.write_forex_strategy(tmp_path)
    autonomy.write_forex_data_import(tmp_path)
    autonomy.write_forex_report(tmp_path)
    autonomy.write_forex_decision_policy(tmp_path)
    assert autonomy.select_forex_continue_action(tmp_path) == "build_risk_controls"
    product.write_risk_controls_files(tmp_path)
    assert autonomy.select_forex_continue_action(tmp_path) == "done"


def test_cli_report_is_json_compatible(tmp_path, capsys):
    module = load_module()
    exit_code = module.main(
        [
            "--goal",
            "forex-paper-bot",
            "--action",
            "build_forex_risk_controls",
            "--repo-root",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    report = json.loads(captured.out)
    assert report["schema"] == "AIOS_PRODUCTIVE_BOUNDED_EXECUTOR.v1"
    assert report["result"] == "preview_only"
    assert report["files_written"] == []


def test_no_scanner_sensitive_or_forbidden_source_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [
        "git add",
        "git commit",
        "git push",
        "git merge",
        "requests",
        "socket",
        "urllib",
        "http.client",
        "openai",
        "anthropic",
    ]:
        assert forbidden not in source
