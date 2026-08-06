#!/usr/bin/env python3
"""Deterministic, fail-closed validation shared by GitHub and Azure CI."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

SCHEMA = "AIOS_DUAL_CI_RECEIPT_V1"
PROVIDERS = {"GITHUB_ACTIONS", "AZURE_PIPELINES", "LOCAL_VALIDATION"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CORE_ROOTS = ("aios/", "agent/", "services/", "apps/", "scripts/", "automation/")
REQUIRED_COMMAND_IDS = (
    "static.required_governance_files",
    "static.workflow_shape",
    "syntax.powershell_tracked",
    "syntax.python_tracked_core",
    "static.placeholder_identity",
    "static.secret_assignments",
    "compile.phase_bridge",
    "compile.governance_validator",
    "compile.assignment_executor",
    "compile.assignment_validator",
    "compile.self_build_inspector",
    "sample.governance_validator",
    "sample.assignment_validator",
)
REQUIRED_FILES = (
    "SECURITY.md", "COMPLIANCE_BASELINE.md", "LICENSE", ".github/dependabot.yml",
    "docs/security/threat-model.md", "docs/security/approval-model.md",
    "docs/security/audit-logging.md", "docs/security/secret-prevention.md",
    "docs/security/repo-hygiene.md",
)
COMPILE_TARGETS = {
    "compile.phase_bridge": "automation/bridge/aios_phase_bridge.py",
    "compile.governance_validator": "automation/validators/aios_governance_validator.py",
    "compile.assignment_executor": "automation/orchestration/dispatcher/assignment_executor.py",
    "compile.assignment_validator": "automation/validators/aios_worker_dispatcher_assignment_executor_validator.py",
    "compile.self_build_inspector": "automation/self_build/aios_self_build_inspector.py",
}


class ValidationBlocked(RuntimeError):
    """A fail-closed validation boundary was reached."""


def _run(args: list[str], root: Path, *, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=root, check=False, capture_output=True, text=text)


def tracked_files(root: Path) -> list[str]:
    result = _run(["git", "ls-files", "-z"], root, text=False)
    if result.returncode:
        raise ValidationBlocked("TRACKED_INVENTORY_UNAVAILABLE_BLOCKED")
    return sorted(x.decode("utf-8") for x in result.stdout.split(b"\0") if x)


def checked_out_sha(root: Path) -> str:
    result = _run(["git", "rev-parse", "HEAD"], root)
    value = result.stdout.strip()
    if result.returncode or not SHA_RE.fullmatch(value):
        raise ValidationBlocked("SHA_SOURCE_UNAVAILABLE_BLOCKED")
    return value


def require_exact_sha(expected_sha: str, root: Path) -> str:
    if not SHA_RE.fullmatch(expected_sha):
        raise ValidationBlocked("SHA_SOURCE_UNAVAILABLE_BLOCKED")
    actual = checked_out_sha(root)
    if expected_sha != actual:
        raise ValidationBlocked("SHA_MISMATCH_BLOCKED")
    return actual


def resolve_azure_expected_sha(env: dict[str, str]) -> str:
    reason = env.get("BUILD_REASON", "")
    if reason == "PullRequest":
        value = env.get("SYSTEM_PULLREQUEST_SOURCECOMMITID", "").strip()
    else:
        value = env.get("BUILD_SOURCEVERSION", "").strip()
    if not SHA_RE.fullmatch(value):
        raise ValidationBlocked("SHA_SOURCE_UNAVAILABLE_BLOCKED")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency_lock_sha256(root: Path, files: list[str]) -> str:
    locks = [p for p in files if Path(p).name in {"requirements.txt", "requirements-dev.txt", "poetry.lock", "Pipfile.lock", "uv.lock"}]
    payload = b"".join(p.encode() + b"\0" + (root / p).read_bytes() + b"\0" for p in locks)
    return hashlib.sha256(payload).hexdigest()


def command_manifest_sha256() -> str:
    data = json.dumps(REQUIRED_COMMAND_IDS, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def _required_files(root: Path, _: list[str]) -> None:
    missing = [p for p in REQUIRED_FILES if not (root / p).is_file()]
    if missing:
        raise ValidationBlocked("MISSING_REQUIRED_GOVERNANCE_FILES: " + ", ".join(missing))


def _workflow_shape(root: Path, _: list[str]) -> None:
    expected = {
        ".github/workflows/ci.yml": ("name: CI", "validate:", "ubuntu-24.04"),
        ".github/workflows/aios-governance.yml": ("name: AIOS Governance", "governance:", "ubuntu-24.04"),
    }
    for filename, markers in expected.items():
        text = (root / filename).read_text(encoding="utf-8")
        if any(marker not in text for marker in markers):
            raise ValidationBlocked(f"WORKFLOW_SHAPE_INVALID: {filename}")


def _powershell(root: Path, files: list[str]) -> None:
    ps1 = [p for p in files if p.lower().endswith(".ps1")]
    probe = _run(["pwsh", "-NoLogo", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"], root)
    if probe.returncode:
        raise ValidationBlocked("POWERSHELL_UNAVAILABLE_BLOCKED")
    for name in ps1:
        command = "$e=$null;$t=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($args[0],[ref]$t,[ref]$e);if($e.Count){$e|% Message;exit 1}"
        result = _run(["pwsh", "-NoLogo", "-NoProfile", "-Command", command, name], root)
        if result.returncode:
            raise ValidationBlocked(f"POWERSHELL_SYNTAX_FAILED: {name}")


def _python_core(root: Path, files: list[str]) -> None:
    for name in [p for p in files if p.endswith(".py") and p.startswith(CORE_ROOTS)]:
        compile((root / name).read_bytes(), name, "exec", dont_inherit=True)


def _placeholder(root: Path, files: list[str]) -> None:
    extensions = {".py", ".ps1", ".json", ".yml", ".yaml"}
    pattern = re.compile(r"youremail@example\.com|your-github-email", re.I)
    for name in files:
        if Path(name).suffix.lower() in extensions and not name.startswith((".github/", "tests/")):
            if pattern.search((root / name).read_text(encoding="utf-8", errors="replace")):
                raise ValidationBlocked(f"PLACEHOLDER_IDENTITY_FOUND: {name}")


def _secrets(root: Path, files: list[str]) -> None:
    extensions = {".py", ".ps1", ".json", ".yml", ".yaml"}
    pattern = re.compile(r"\b(api_key|apikey|secret|token|password|broker)\b\s*[:=]\s*['\"](?!BLOCKED|NONE|MISSING|EXAMPLE|placeholder|changeme|your_|demo_)[^'\"]+['\"]", re.I)
    for name in files:
        if Path(name).suffix.lower() in extensions and not name.startswith((".github/", "docs/", "tests/")):
            if pattern.search((root / name).read_text(encoding="utf-8", errors="replace")):
                raise ValidationBlocked(f"SECRET_ASSIGNMENT_FOUND: {name}")


def _compile(root: Path, name: str) -> None:
    compile((root / name).read_bytes(), name, "exec", dont_inherit=True)


def _sample(root: Path, name: str) -> None:
    result = _run([sys.executable, "-B", name, "--sample-check"], root)
    if result.returncode:
        raise ValidationBlocked(f"SAMPLE_CHECK_FAILED: {name}")


def run_validation(root: Path, provider: str, expected_sha: str) -> dict:
    if provider not in PROVIDERS:
        raise ValidationBlocked("PROVIDER_INVALID_BLOCKED")
    actual = require_exact_sha(expected_sha, root)  # Nothing below may execute first.
    files = tracked_files(root)
    actions: dict[str, Callable[[], None]] = {
        "static.required_governance_files": lambda: _required_files(root, files),
        "static.workflow_shape": lambda: _workflow_shape(root, files),
        "syntax.powershell_tracked": lambda: _powershell(root, files),
        "syntax.python_tracked_core": lambda: _python_core(root, files),
        "static.placeholder_identity": lambda: _placeholder(root, files),
        "static.secret_assignments": lambda: _secrets(root, files),
        **{key: (lambda value=value: _compile(root, value)) for key, value in COMPILE_TARGETS.items()},
        "sample.governance_validator": lambda: _sample(root, COMPILE_TARGETS["compile.governance_validator"]),
        "sample.assignment_validator": lambda: _sample(root, COMPILE_TARGETS["compile.assignment_validator"]),
    }
    commands = []
    for command_id in REQUIRED_COMMAND_IDS:
        actions[command_id]()
        commands.append({"id": command_id, "state": "PASS"})
    return {
        "schema": SCHEMA, "provider": provider, "state": "VALIDATION_PASS",
        "expected_sha": expected_sha, "checked_out_sha": actual,
        "runner_sha256": sha256_file(Path(__file__)),
        "command_manifest_sha256": command_manifest_sha256(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "dependency_lock_sha256": dependency_lock_sha256(root, files),
        "command_ids": list(REQUIRED_COMMAND_IDS), "commands": commands,
        "merge_authorized": False,
    }


def validate_receipt(receipt: dict) -> None:
    required = {"schema", "provider", "state", "expected_sha", "checked_out_sha", "runner_sha256", "command_manifest_sha256", "python_version", "dependency_lock_sha256", "command_ids", "commands", "merge_authorized"}
    if set(receipt) != required or receipt["schema"] != SCHEMA or receipt["provider"] not in PROVIDERS:
        raise ValidationBlocked("RECEIPT_INVALID_BLOCKED")
    if receipt["merge_authorized"] is not False or receipt["state"] != "VALIDATION_PASS":
        raise ValidationBlocked("RECEIPT_INVALID_BLOCKED")
    if not SHA_RE.fullmatch(receipt["expected_sha"]) or receipt["checked_out_sha"] != receipt["expected_sha"]:
        raise ValidationBlocked("SHA_MISMATCH_BLOCKED")
    if not re.fullmatch(r"3\.12(?:\.\d+)?", receipt["python_version"]):
        raise ValidationBlocked("PYTHON_RUNTIME_MISMATCH_BLOCKED")
    if receipt["command_ids"] != list(REQUIRED_COMMAND_IDS) or not receipt["commands"]:
        raise ValidationBlocked("COMMAND_SET_INVALID_BLOCKED")
    if [c.get("id") for c in receipt["commands"]] != list(REQUIRED_COMMAND_IDS) or any(c.get("state") != "PASS" for c in receipt["commands"]):
        raise ValidationBlocked("COMMAND_SET_INVALID_BLOCKED")


def equivalent(github: dict, azure: dict) -> str:
    validate_receipt(github); validate_receipt(azure)
    if {github["provider"], azure["provider"]} != {"GITHUB_ACTIONS", "AZURE_PIPELINES"}:
        raise ValidationBlocked("PROVIDER_MISMATCH_BLOCKED")
    comparable = ("expected_sha", "runner_sha256", "command_manifest_sha256", "dependency_lock_sha256", "command_ids")
    if any(github[k] != azure[k] for k in comparable):
        raise ValidationBlocked("EQUIVALENCE_MISMATCH_BLOCKED")
    return "EQUIVALENT_VALIDATION_PASS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=sorted(PROVIDERS))
    parser.add_argument("--expected-sha")
    parser.add_argument("--receipt")
    parser.add_argument("--equivalence", nargs=2, metavar=("GITHUB", "AZURE"))
    args = parser.parse_args()
    try:
        if args.equivalence:
            receipts = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.equivalence]
            print(equivalent(*receipts)); return 0
        if not (args.provider and args.expected_sha and args.receipt):
            parser.error("validation requires --provider, --expected-sha, and --receipt")
        receipt = run_validation(Path.cwd(), args.provider, args.expected_sha)
        Path(args.receipt).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("VALIDATION_PASS"); return 0
    except (OSError, SyntaxError, ValidationBlocked) as exc:
        print(str(exc), file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
