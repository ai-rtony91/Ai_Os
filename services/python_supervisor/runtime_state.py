"""AI_OS Night Supervisor runtime state synthesis.

Schema/contract reference: schemas/aios/orchestration/overnight_supervisor.schema.json
Mode: DRY_RUN
blocked_capabilities: runtime_launch, supervisor_loop, worker_launch, packet_movement,
approval_mutation, telemetry_append, file_write, git_stage_commit_push
next_safe_action: Review DRY_RUN runtime bundle evidence before approving any protected action.
commit_performed: NO / push_performed: NO
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _get_path(payload: Any, path: tuple[str, ...], default: Any = None) -> Any:
    current = payload
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def _load_json_file(path: Path) -> dict[str, Any]:
    last_error = ""
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return json.loads(path.read_text(encoding=encoding))
        except Exception as exc:  # noqa: BLE001 - try common local JSON encodings
            last_error = str(exc)
    try:
        return json.loads(path.read_bytes().decode())
    except Exception:  # noqa: BLE001 - fail-closed evidence wrapper
        return {
            "schema": "AIOS_RUNTIME_STATE_BUNDLE_READ_ERROR.v1",
            "status": "BUNDLE_UNAVAILABLE",
            "error": last_error,
            "source_path": str(path),
        }


def _run_runtime_bundle(repo_root: Path) -> dict[str, Any]:
    """Call the approved DRY_RUN runtime bundle once and capture JSON evidence."""

    script_path = repo_root / "automation" / "orchestration" / "runtime" / "Get-AiOsRuntimeStateBundle.DRY_RUN.ps1"
    if not script_path.exists():
        return {
            "schema": "AIOS_RUNTIME_STATE_BUNDLE_MISSING.v1",
            "status": "BUNDLE_UNAVAILABLE",
            "error": "Runtime state bundle script is missing.",
            "source_path": str(script_path),
        }

    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
                "-QuietJson",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001 - fail-closed evidence wrapper
        return {
            "schema": "AIOS_RUNTIME_STATE_BUNDLE_EXECUTION_ERROR.v1",
            "status": "BUNDLE_UNAVAILABLE",
            "error": str(exc),
            "source_path": str(script_path),
        }

    if completed.returncode != 0:
        return {
            "schema": "AIOS_RUNTIME_STATE_BUNDLE_FAILED.v1",
            "status": "BUNDLE_UNAVAILABLE",
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "source_path": str(script_path),
        }

    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {
            "schema": "AIOS_RUNTIME_STATE_BUNDLE_PARSE_ERROR.v1",
            "status": "BUNDLE_UNAVAILABLE",
            "error": str(exc),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "source_path": str(script_path),
        }


@dataclass
class RuntimeState:
    mode: str = "DRY_RUN"
    repo_root: str = ""
    branch: str = "UNKNOWN"
    bundle_integrity: str = "UNKNOWN"
    validator_confidence: str = "UNKNOWN"
    safe_auto_allowed: bool = False
    lock_conflicts: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    execution_enabled: bool = False
    queue_mutation_enabled: bool = False
    approval_mutation_enabled: bool = False
    cycle_count: int = 0
    last_cycle_at: str = ""
    generated_at: str = field(default_factory=_utc_now)
    runtime_notes: list[str] = field(default_factory=list)
    raw_bundle: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _extract_branch(bundle: dict[str, Any]) -> str:
    branch_line = ""
    git_items = _get_path(bundle, ("git_state", "items"), [])
    if git_items:
        first = git_items[0]
        if isinstance(first, dict):
            branch_line = str(first.get("branch", ""))
    if branch_line.startswith("## "):
        branch = branch_line[3:].split("...", maxsplit=1)[0].strip()
        return branch or "UNKNOWN"
    return str(bundle.get("branch") or _get_path(bundle, ("git", "branch"), "UNKNOWN"))


def _extract_changed_paths(bundle: dict[str, Any]) -> list[str]:
    git_items = _get_path(bundle, ("git_state", "items"), [])
    paths: list[str] = []
    for item in _as_list(git_items):
        if isinstance(item, dict):
            paths.extend(str(path) for path in _as_list(item.get("candidate_files")) if str(path).strip())
            paths.extend(str(path) for path in _as_list(item.get("changed_paths")) if str(path).strip())
    paths.extend(str(path) for path in _as_list(bundle.get("changed_paths")) if str(path).strip())
    return sorted(set(paths))


def _extract_lock_conflicts(bundle: dict[str, Any]) -> list[str]:
    signals = [str(signal) for signal in _as_list(bundle.get("blocking_signals"))]
    return sorted({signal for signal in signals if "lock_conflict" in signal.lower()})


def build_runtime_state(
    repo_root: str | Path = ".",
    *,
    runtime_bundle: dict[str, Any] | None = None,
    runtime_bundle_path: str | Path | None = None,
    session_state: dict[str, Any] | None = None,
) -> RuntimeState:
    """Build read-only DRY_RUN runtime state evidence for the Night Supervisor."""

    resolved_root = Path(repo_root).resolve()
    if runtime_bundle is None:
        runtime_bundle = _load_json_file(Path(runtime_bundle_path)) if runtime_bundle_path else _run_runtime_bundle(resolved_root)

    cycle_count = 1
    if session_state is not None:
        cycle_count = int(session_state.get("cycle_count", 0)) + 1
        session_state["cycle_count"] = cycle_count
        session_state["last_cycle_at"] = _utc_now()

    integrity = _get_path(runtime_bundle, ("bundle_integrity", "status"), runtime_bundle.get("status", "UNKNOWN"))
    confidence = runtime_bundle.get("validator_confidence", {})
    if isinstance(confidence, dict):
        validator_confidence = str(
            confidence.get("overall_result")
            or confidence.get("status")
            or _get_path(runtime_bundle, ("confidence_state", "overall_confidence"), "UNKNOWN")
        )
    else:
        validator_confidence = str(confidence or "UNKNOWN")

    notes = [
        "Runtime state is DRY_RUN evidence only.",
        "Runtime bundle subprocess is limited to Get-AiOsRuntimeStateBundle.DRY_RUN.ps1 -QuietJson.",
    ]
    if runtime_bundle.get("status") == "BUNDLE_UNAVAILABLE":
        notes.append("Runtime bundle unavailable; fail-closed UNKNOWN state emitted.")

    return RuntimeState(
        repo_root=str(resolved_root),
        branch=_extract_branch(runtime_bundle),
        bundle_integrity=str(integrity or "UNKNOWN"),
        validator_confidence=validator_confidence,
        safe_auto_allowed=False,
        lock_conflicts=_extract_lock_conflicts(runtime_bundle),
        changed_paths=_extract_changed_paths(runtime_bundle),
        cycle_count=cycle_count,
        last_cycle_at=str(session_state.get("last_cycle_at", "")) if session_state else "",
        runtime_notes=notes,
        raw_bundle=runtime_bundle,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit AI_OS DRY_RUN runtime state synthesis.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--runtime-bundle-path", default=None, help="Optional pre-generated runtime bundle JSON path.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    state = build_runtime_state(args.repo_root, runtime_bundle_path=args.runtime_bundle_path)
    print(json.dumps(state.to_dict(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
