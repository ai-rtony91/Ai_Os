from __future__ import annotations

import json
from pathlib import Path

from automation.orchestration.relay.aios_codex_prompt_consumer_v1 import PROTECTED_FLAGS
from automation.orchestration.relay.aios_self_consuming_codex_cycle_v1 import build_next_pr_lifecycle_packet, run_self_consuming_cycle
from tests.orchestration.test_aios_codex_prompt_consumer_v1 import prompt_text


FLAGS = {name: False for name in PROTECTED_FLAGS}


def prompt(tmp_path: Path, suffix: str = "") -> Path:
    path = tmp_path / f"prompt{suffix}.md"
    path.write_text(prompt_text((f"safe/{suffix or 'one'}.py",)), encoding="utf-8")
    return path


def fake_complete(relay: Path):
    def worker() -> None:
        task = next((relay / "inbox").glob("*.task.json"))
        (relay / "done").mkdir(parents=True, exist_ok=True)
        task.replace(relay / "done" / task.name)
    return worker


def test_successful_completion_attempts_next_cycle_then_stops_unchanged(tmp_path: Path) -> None:
    source = prompt(tmp_path)
    calls = 0
    def generate() -> str:
        nonlocal calls
        calls += 1
        return str(source)
    result = run_self_consuming_cycle(generate=generate, relay_root=tmp_path / "relay", flags=FLAGS, invoke_worker=fake_complete(tmp_path / "relay"))
    assert result.status == "UNCHANGED_PROMPT"
    assert calls == 2


def test_stop_flag_stops_without_generation(tmp_path: Path) -> None:
    relay = tmp_path / "relay"
    relay.mkdir()
    (relay / "STOP.flag").touch()
    result = run_self_consuming_cycle(generate=lambda: (_ for _ in ()).throw(AssertionError()), relay_root=relay)
    assert result.status == "STOP_FLAG"


def test_error_and_approval_stop_cycle(tmp_path: Path) -> None:
    source = prompt(tmp_path)
    relay = tmp_path / "relay"
    def error_worker() -> None:
        task = next((relay / "inbox").glob("*.task.json"))
        (relay / "error").mkdir(parents=True)
        task.replace(relay / "error" / task.name)
    assert run_self_consuming_cycle(generate=lambda: str(source), relay_root=relay, invoke_worker=error_worker).status == "ERROR"
    approved = dict(FLAGS)
    approved["commit"] = True
    assert run_self_consuming_cycle(generate=lambda: str(source), relay_root=tmp_path / "relay2", flags=approved).status == "APPROVAL_REQUIRED"


def test_max_cycles_and_elapsed_are_enforced(tmp_path: Path) -> None:
    relay = tmp_path / "relay"
    count = 0
    def generate() -> str:
        nonlocal count
        count += 1
        return str(prompt(tmp_path, str(count)))
    assert run_self_consuming_cycle(generate=generate, relay_root=relay, invoke_worker=fake_complete(relay), max_cycles=2).status == "MAX_CYCLES"
    ticks = iter((0.0, 61.0))
    assert run_self_consuming_cycle(generate=generate, relay_root=tmp_path / "relay3", monotonic=lambda: next(ticks), max_elapsed_minutes=1).status == "MAX_ELAPSED"


def test_dry_run_never_invokes_worker_or_writes_task(tmp_path: Path) -> None:
    relay = tmp_path / "relay"
    result = run_self_consuming_cycle(generate=lambda: str(prompt(tmp_path)), relay_root=relay, dry_run=True, invoke_worker=lambda: (_ for _ in ()).throw(AssertionError()))
    assert result.status == "DRY_RUN"
    assert not list(relay.rglob("*.task.json"))


def test_task_contract_contains_allowed_paths_for_worker_validation(tmp_path: Path) -> None:
    source = prompt(tmp_path)
    relay = tmp_path / "relay"
    seen = {}
    def worker() -> None:
        task_path = next((relay / "inbox").glob("*.task.json"))
        seen.update(json.loads(task_path.read_text(encoding="utf-8")))
        (relay / "done").mkdir(parents=True)
        task_path.replace(relay / "done" / task_path.name)
    run_self_consuming_cycle(generate=lambda: str(source), relay_root=relay, invoke_worker=worker, max_cycles=1)
    assert seen["allowed_paths"] == ["safe/one.py"]


def test_next_pr_lifecycle_packet_is_complete_but_dry_run() -> None:
    packet = build_next_pr_lifecycle_packet()
    assert packet.startswith("CODEX-ONLY PROMPT\n")
    assert "AI_OS EXECUTION TOKEN" in packet
    assert "MODE: DRY_RUN" in packet
    assert "Commit, push, PR mutation, merge, and branch deletion require separate approval." in packet
