from __future__ import annotations

import argparse
import json
import re
from typing import Any


SCHEMA = "AIOS_CLI_RESULT_INGEST.v1"
SANDBOX_1312 = "CreateProcessAsUserW failed: 1312"


def safety_summary() -> dict[str, bool]:
    return {
        "command_execution": False,
        "network_access": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "scheduler": False,
        "daemon": False,
        "broker": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "credentials": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def _as_text(report: str | dict[str, Any]) -> str:
    if isinstance(report, str):
        return report
    return json.dumps(report, sort_keys=False)


def _as_mapping(report: str | dict[str, Any]) -> dict[str, Any]:
    return report if isinstance(report, dict) else {}


def _count_from_text(pattern: str, text: str) -> int:
    matches = [int(match) for match in re.findall(pattern, text, flags=re.IGNORECASE)]
    return sum(matches)


def _extract_files_changed(text: str, mapping: dict[str, Any]) -> list[str]:
    files = mapping.get("files_changed")
    if isinstance(files, list):
        return [str(item) for item in files]

    changed: list[str] = []
    capture = False
    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("files changed"):
            capture = True
            suffix = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
            if suffix and suffix.lower() not in {"none", "n/a"}:
                changed.extend(part.strip() for part in suffix.split(",") if part.strip())
            continue
        if capture and stripped.startswith(("-", "*")):
            changed.append(stripped[1:].strip())
            continue
        if capture and stripped.endswith(".py"):
            changed.append(stripped)
            continue
        if capture and stripped and ":" in stripped:
            break
    return changed


def _extract_status(text: str, mapping: dict[str, Any], sandbox_blocked: bool, tests_failed_count: int) -> str:
    status = mapping.get("status", mapping.get("result"))
    if isinstance(status, str) and status:
        return status
    if sandbox_blocked:
        return "SANDBOX_BLOCKED"
    status_match = re.search(r"STATUS:\s*([A-Z0-9_ ,\-]+)", text, flags=re.IGNORECASE)
    if status_match:
        return status_match.group(1).strip()
    if tests_failed_count > 0:
        return "FAILED"
    if re.search(r"\b\d+\s+passed\b", text, flags=re.IGNORECASE):
        return "PASSED"
    return "UNKNOWN"


def _extract_next_safe_action(text: str, mapping: dict[str, Any], sandbox_blocked: bool) -> str:
    value = mapping.get("next_safe_action")
    if isinstance(value, str) and value:
        return value
    for label in ("SAFE NEXT COMMAND", "SAFE NEXT ACTION", "next_safe_action"):
        match = re.search(rf"{label}:\s*(.+)", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    if sandbox_blocked:
        return "Rerun from an environment where the Codex sandbox launcher can start commands."
    return "Review the CLI result before continuing."


def _extract_protected_status(text: str, mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if isinstance(value, str) and value:
        return value
    label = key.replace("_", " ")
    match = re.search(rf"{label}:\s*(.+)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if key == "commit_status" and re.search(r"\bno commit\b", text, flags=re.IGNORECASE):
        return "NO_COMMIT"
    if key == "push_status" and re.search(r"\bno push\b", text, flags=re.IGNORECASE):
        return "NO_PUSH"
    return "NOT_REQUESTED"


def build_cli_result_ingest(report: str | dict[str, Any]) -> dict[str, Any]:
    text = _as_text(report)
    mapping = _as_mapping(report)

    sandbox_blocked = SANDBOX_1312.lower() in text.lower()
    direct_command_blocked = bool(
        re.search(r"direct command .*blocked|command execution .*blocked", text, flags=re.IGNORECASE)
    )

    tests_passed_count = int(mapping.get("tests_passed_count", 0) or 0)
    tests_failed_count = int(mapping.get("tests_failed_count", 0) or 0)
    tests_passed_count += _count_from_text(r"\b(\d+)\s+passed\b", text)
    tests_failed_count += _count_from_text(r"\b(\d+)\s+failed\b", text)

    validation_passed = mapping.get("validation_passed")
    if not isinstance(validation_passed, bool):
        validation_passed = tests_failed_count == 0 and (
            tests_passed_count > 0 or bool(mapping.get("passed") is True)
        )
    if sandbox_blocked:
        validation_passed = False

    blockers = mapping.get("blockers")
    if not isinstance(blockers, list):
        blockers = []
    blockers = [str(item) for item in blockers]
    if sandbox_blocked and "sandbox_launcher_unavailable_1312" not in blockers:
        blockers.append("sandbox_launcher_unavailable_1312")
    if direct_command_blocked and "direct_command_blocked" not in blockers:
        blockers.append("direct_command_blocked")
    if tests_failed_count > 0 and "tests_failed" not in blockers:
        blockers.append("tests_failed")

    status = _extract_status(text, mapping, sandbox_blocked, tests_failed_count)

    return {
        "schema": SCHEMA,
        "status": status,
        "files_changed": _extract_files_changed(text, mapping),
        "validation_passed": validation_passed,
        "tests_passed_count": tests_passed_count,
        "tests_failed_count": tests_failed_count,
        "sandbox_blocked": sandbox_blocked,
        "direct_command_blocked": direct_command_blocked,
        "blockers": blockers,
        "next_safe_action": _extract_next_safe_action(text, mapping, sandbox_blocked),
        "commit_status": _extract_protected_status(text, mapping, "commit_status"),
        "push_status": _extract_protected_status(text, mapping, "push_status"),
        "safety_summary": safety_summary(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a sanitized AIOS CLI result ingest contract.")
    parser.add_argument("--text", default="", help="Optional report text to ingest.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = build_cli_result_ingest(args.text)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
