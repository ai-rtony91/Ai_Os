"""Fail-closed launcher for one unattended Supertrend PAPER campaign run."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

VERSION = "forex_p1_paper_autostart_v1"
TARGET_TRADES = 30
STATE_RELATIVE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_SUPERTREND_30_TRADE_CAMPAIGN_STATE.json"
)
RUNNER_RELATIVE_PATH = Path(
    "scripts/forex_delivery/run_forex_p1_supervised_paper_campaign_v1.py"
)
RUNTIME_DIR_RELATIVE_PATH = Path(".aios/runtime/forex_p1_paper_autostart_v1")
STOP_FILES = (
    Path(".aios/runtime/forex/kill_switch.active"),
    Path(".aios/runtime/forex/risk_halt.active"),
    Path(".aios/runtime/forex/cancel_campaign.active"),
)


@dataclass(frozen=True)
class PreflightResult:
    status: str
    reason: str
    accepted_trades: int
    target_trades: int = TARGET_TRADES
    paper_only: bool = True
    live_execution_allowed: bool = False


def _read_state(path: Path) -> Mapping[str, object]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("CAMPAIGN_STATE_INVALID")
    return payload


def _accepted_trades(state: Mapping[str, object]) -> int:
    value = state.get("accepted_qualifying_trades", 0)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("CAMPAIGN_ACCEPTED_COUNT_INVALID")
    return value


def _branch(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError("GIT_BRANCH_UNAVAILABLE")
    return result.stdout.strip()


def preflight(
    repo_root: Path,
    *,
    environment: Mapping[str, str] | None = None,
    branch_reader: Callable[[Path], str] = _branch,
) -> PreflightResult:
    """Verify that exactly one bounded Practice/PAPER run may start."""
    env = os.environ if environment is None else environment
    root = repo_root.resolve()
    runner = root / RUNNER_RELATIVE_PATH
    if not runner.is_file():
        return PreflightResult("BLOCKED", "CANONICAL_RUNNER_MISSING", 0)
    if branch_reader(root) != "main":
        return PreflightResult("BLOCKED", "MAIN_BRANCH_REQUIRED", 0)
    if not env.get("OANDA_API_TOKEN") or not env.get("OANDA_ACCOUNT_ID"):
        return PreflightResult("BLOCKED", "RUNTIME_CREDENTIALS_MISSING", 0)
    active_stop = next((str(path) for path in STOP_FILES if (root / path).exists()), None)
    if active_stop:
        return PreflightResult("BLOCKED", f"SAFETY_STOP_ACTIVE:{active_stop}", 0)
    try:
        state = _read_state(root / STATE_RELATIVE_PATH)
        accepted = _accepted_trades(state)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return PreflightResult("BLOCKED", str(exc), 0)
    if accepted >= TARGET_TRADES:
        return PreflightResult("NO_ACTION", "TARGET_ALREADY_REACHED", accepted)
    return PreflightResult("READY", "PAPER_CAMPAIGN_READY", accepted)


def _write_jsonl(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True, allow_nan=False) + "\n")


def _acquire_lock(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError("AUTOSTART_ALREADY_ACTIVE") from exc
    os.write(descriptor, f"{os.getpid()}\n".encode("ascii"))
    return descriptor


def _release_lock(path: Path, descriptor: int) -> None:
    os.close(descriptor)
    path.unlink(missing_ok=True)


def launch(
    repo_root: Path,
    *,
    cycles: int = 288,
    reviewer: str = "Human Owner Anthony",
    preflight_only: bool = False,
    environment: Mapping[str, str] | None = None,
    branch_reader: Callable[[Path], str] = _branch,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> int:
    if cycles < 1 or cycles > 288:
        raise ValueError("CYCLES_OUT_OF_RANGE")
    root = repo_root.resolve()
    runtime_dir = root / RUNTIME_DIR_RELATIVE_PATH
    log_path = runtime_dir / "events.jsonl"
    result = preflight(
        root,
        environment=environment,
        branch_reader=branch_reader,
    )
    event = {
        "schema": "AIOS_FOREX_P1_PAPER_AUTOSTART_EVENT.v1",
        "version": VERSION,
        "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        **asdict(result),
    }
    _write_jsonl(log_path, event)
    print(json.dumps(event, sort_keys=True))
    if result.status == "NO_ACTION":
        return 0
    if result.status != "READY":
        return 2
    if preflight_only:
        return 0

    lock_path = runtime_dir / "launch.lock"
    descriptor = _acquire_lock(lock_path)
    try:
        command: Sequence[str] = (
            sys.executable,
            str(root / RUNNER_RELATIVE_PATH),
            "--owner-local-runtime",
            "--signal-source",
            "supertrend",
            "--supertrend-paper-demo-only",
            "--cycles",
            str(cycles),
            "--reviewer",
            reviewer,
        )
        completed = run(
            command,
            cwd=root,
            env=dict(os.environ if environment is None else environment),
            check=False,
            text=True,
        )
        _write_jsonl(
            log_path,
            {
                "schema": "AIOS_FOREX_P1_PAPER_AUTOSTART_EVENT.v1",
                "version": VERSION,
                "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "status": "RUN_COMPLETE" if completed.returncode == 0 else "RUN_STOPPED",
                "return_code": completed.returncode,
                "paper_only": True,
                "live_execution_allowed": False,
            },
        )
        return completed.returncode
    finally:
        _release_lock(lock_path, descriptor)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repo-root", type=Path, required=True)
    result.add_argument("--cycles", type=int, default=288)
    result.add_argument("--reviewer", default="Human Owner Anthony")
    result.add_argument("--preflight-only", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return launch(
            args.repo_root,
            cycles=args.cycles,
            reviewer=args.reviewer,
            preflight_only=args.preflight_only,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
