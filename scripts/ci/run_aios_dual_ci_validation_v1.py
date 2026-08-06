#!/usr/bin/env python3
"""Provider-neutral, exact-SHA deterministic validation for AI_OS CI."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence

SCHEMA = "AIOS_DUAL_CI_RECEIPT_V1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ROOT = Path(__file__).resolve().parents[2]

COMMANDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("compile.phase_bridge", ("automation/bridge/aios_phase_bridge.py",)),
    ("compile.governance_validator", ("automation/validators/aios_governance_validator.py",)),
    ("compile.assignment_executor", ("automation/orchestration/dispatcher/assignment_executor.py",)),
    ("compile.assignment_validator", ("automation/validators/aios_worker_dispatcher_assignment_executor_validator.py",)),
    ("compile.self_build_inspector", ("automation/self_build/aios_self_build_inspector.py",)),
    ("sample.governance_validator", ("automation/validators/aios_governance_validator.py", "--sample-check")),
    ("sample.assignment_validator", ("automation/validators/aios_worker_dispatcher_assignment_executor_validator.py", "--sample-check")),
    ("static.required_governance_files", ()),
    ("static.placeholder_identity", ()),
    ("static.secret_assignments", ()),
)
COMMAND_IDS = tuple(item[0] for item in COMMANDS)

REQUIRED_FILES = (
    "SECURITY.md", "COMPLIANCE_BASELINE.md", "LICENSE", ".github/dependabot.yml",
    "docs/security/threat-model.md", "docs/security/approval-model.md",
    "docs/security/audit-logging.md", "docs/security/secret-prevention.md",
    "docs/security/repo-hygiene.md",
)


def _run_process(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, check=False)


def checked_out_sha(run: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] = _run_process) -> str:
    result = run(("git", "rev-parse", "HEAD"))
    return result.stdout.strip().lower() if result.returncode == 0 else ""


def runner_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _source_files() -> list[Path]:
    suffixes = {".py", ".ps1", ".json", ".yml", ".yaml"}
    excluded = {".git", "tests", "docs", ".github"}
    return [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in suffixes
            and not excluded.intersection(p.relative_to(ROOT).parts)]


def _execute(command_id: str, args: tuple[str, ...], run: Callable[[Sequence[str]], subprocess.CompletedProcess[str]]) -> tuple[bool, str]:
    if command_id.startswith("compile."):
        path = ROOT / args[0]
        if not path.is_file():
            return False, "required source is missing"
        try:
            compile(path.read_bytes(), str(path.relative_to(ROOT)), "exec")
            return True, "compiled"
        except (OSError, SyntaxError) as exc:
            return False, f"compile failed: {exc}"
    if command_id.startswith("sample."):
        if not (ROOT / args[0]).is_file():
            return False, "required command is missing"
        result = run((sys.executable, *args))
        return result.returncode == 0, (result.stderr or result.stdout).strip()[-500:]
    if command_id == "static.required_governance_files":
        missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
        return not missing, "missing: " + ", ".join(missing) if missing else "all required files present"
    texts = []
    try:
        texts = [(path, path.read_text(encoding="utf-8", errors="replace")) for path in _source_files()]
    except OSError as exc:
        return False, f"static scan failed: {exc}"
    if command_id == "static.placeholder_identity":
        placeholder_pattern = re.compile("youremail" + r"@example\.com|your-github-" + "email", re.I)
        hits = [str(p.relative_to(ROOT)) for p, value in texts if placeholder_pattern.search(value)]
        return not hits, "matches: " + ", ".join(hits) if hits else "no placeholder identities"
    if command_id == "static.secret_assignments":
        pattern = re.compile(r"\b(api_key|apikey|secret|token|password|broker)\b[ \t]*[:=][ \t]*['\"](?!BLOCKED|NONE|MISSING|EXAMPLE|placeholder|changeme|your_|demo_)[^'\"]+['\"]", re.I)
        hits = [str(p.relative_to(ROOT)) for p, value in texts if any(pattern.search(line) for line in value.splitlines())]
        return not hits, "matches: " + ", ".join(hits) if hits else "no obvious secret assignments"
    return False, "unknown command ID"


def validate(expected_sha: str, run: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] = _run_process) -> dict[str, object]:
    expected = expected_sha.lower()
    actual = checked_out_sha(run)
    receipt: dict[str, object] = {
        "schema": SCHEMA, "state": "SHA_MISMATCH_BLOCKED", "expected_sha": expected,
        "checked_out_sha": actual, "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "runner_sha256": runner_sha256(), "command_ids": list(COMMAND_IDS), "commands": [],
        "merge_authorized": False,
    }
    if not SHA_RE.fullmatch(expected) or actual != expected:
        return receipt
    results = []
    failed = False
    for command_id, args in COMMANDS:
        passed, detail = _execute(command_id, args, run)
        results.append({"id": command_id, "result": "PASS" if passed else "FAIL", "detail": detail})
        failed |= not passed
    receipt["commands"] = results
    receipt["state"] = "VALIDATION_FAILED" if failed else "VALIDATION_PASS"
    return receipt


def equivalent_validation_pass(first: dict[str, object], second: dict[str, object]) -> bool:
    keys = ("expected_sha", "checked_out_sha", "runner_sha256", "python_version", "command_ids")
    return all(first.get(k) == second.get(k) for k in keys) and all(
        item.get("state") == "VALIDATION_PASS"
        and item.get("expected_sha") == item.get("checked_out_sha")
        and all(command.get("result") == "PASS" for command in item.get("commands", []))
        for item in (first, second)
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--receipt-path", type=Path)
    args = parser.parse_args(argv)
    receipt = validate(args.expected_sha)
    rendered = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.receipt_path:
        args.receipt_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if receipt["state"] == "VALIDATION_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
