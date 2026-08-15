import json
import subprocess
from pathlib import Path

from automation.forex_engine.forex_p1_paper_autostart_v1 import (
    RUNNER_RELATIVE_PATH,
    STATE_RELATIVE_PATH,
    launch,
    preflight,
)


def _repo(tmp_path: Path, accepted: int = 0) -> Path:
    runner = tmp_path / RUNNER_RELATIVE_PATH
    runner.parent.mkdir(parents=True)
    runner.write_text("# canonical runner\n", encoding="utf-8")
    state = tmp_path / STATE_RELATIVE_PATH
    state.parent.mkdir(parents=True)
    state.write_text(
        json.dumps({"accepted_qualifying_trades": accepted}), encoding="utf-8"
    )
    return tmp_path


def _env() -> dict[str, str]:
    return {"OANDA_API_TOKEN": "secret", "OANDA_ACCOUNT_ID": "practice"}


def test_preflight_ready_is_paper_only(tmp_path: Path) -> None:
    result = preflight(
        _repo(tmp_path, 2), environment=_env(), branch_reader=lambda _: "main"
    )

    assert result.status == "READY"
    assert result.accepted_trades == 2
    assert result.paper_only is True
    assert result.live_execution_allowed is False


def test_preflight_blocks_missing_credentials(tmp_path: Path) -> None:
    result = preflight(
        _repo(tmp_path), environment={}, branch_reader=lambda _: "main"
    )

    assert result.reason == "RUNTIME_CREDENTIALS_MISSING"


def test_preflight_blocks_safety_stop(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    stop = root / ".aios/runtime/forex/kill_switch.active"
    stop.parent.mkdir(parents=True)
    stop.touch()

    result = preflight(root, environment=_env(), branch_reader=lambda _: "main")

    assert result.reason.startswith("SAFETY_STOP_ACTIVE:")


def test_preflight_does_nothing_after_target(tmp_path: Path) -> None:
    result = preflight(
        _repo(tmp_path, 30), environment=_env(), branch_reader=lambda _: "main"
    )

    assert result.status == "NO_ACTION"
    assert result.reason == "TARGET_ALREADY_REACHED"


def test_launch_uses_only_canonical_supertrend_paper_flags(tmp_path: Path) -> None:
    root = _repo(tmp_path, 1)
    observed = {}

    def fake_run(command, **kwargs):
        observed["command"] = list(command)
        return subprocess.CompletedProcess(command, 0)

    assert launch(
        root,
        environment=_env(),
        branch_reader=lambda _: "main",
        run=fake_run,
    ) == 0
    assert "--signal-source" in observed["command"]
    assert "supertrend" in observed["command"]
    assert "--supertrend-paper-demo-only" in observed["command"]
    assert "--owner-local-runtime" in observed["command"]
    assert not (root / ".aios/runtime/forex_p1_paper_autostart_v1/launch.lock").exists()


def test_preflight_only_never_starts_runner(tmp_path: Path) -> None:
    root = _repo(tmp_path)

    def forbidden_run(*args, **kwargs):
        raise AssertionError("runner must not start")

    assert launch(
        root,
        environment=_env(),
        preflight_only=True,
        branch_reader=lambda _: "main",
        run=forbidden_run,
    ) == 0
