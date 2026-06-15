from __future__ import annotations

import argparse
import json
import re
from typing import Any


SCHEMA = "AIOS_GITHUB_PR_STATE.v1"
REQUIRED_VALIDATE_CHECK = "validate"


def _as_text(value: str | dict[str, Any]) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=False)


def _extract_pr_number(value: str | dict[str, Any], text: str) -> int | None:
    if isinstance(value, dict):
        number = value.get("number", value.get("pr_number"))
        if isinstance(number, int):
            return number
        if isinstance(number, str) and number.isdigit():
            return int(number)
    match = re.search(r"#(\d+)|pr[_ ]?number[:\s]+(\d+)|pull request[:\s]+(\d+)", text, flags=re.IGNORECASE)
    if not match:
        return None
    return int(next(group for group in match.groups() if group))


def _extract_branch(value: str | dict[str, Any], text: str) -> str | None:
    if isinstance(value, dict):
        for key in ("branch", "headRefName"):
            branch = value.get(key)
            if isinstance(branch, str) and branch:
                return branch
        head = value.get("head")
        if isinstance(head, dict):
            branch = head.get("ref")
            if isinstance(branch, str) and branch:
                return branch
    match = re.search(r"branch[:\s]+([A-Za-z0-9._/\-]+)", text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _check_nodes(value: dict[str, Any]) -> list[dict[str, Any]]:
    checks = value.get("checks")
    if isinstance(checks, list):
        return [item for item in checks if isinstance(item, dict)]

    nodes = value.get("statusCheckRollup")
    if isinstance(nodes, dict):
        contexts = nodes.get("contexts")
        if isinstance(contexts, dict) and isinstance(contexts.get("nodes"), list):
            return [item for item in contexts["nodes"] if isinstance(item, dict)]
        if isinstance(nodes.get("nodes"), list):
            return [item for item in nodes["nodes"] if isinstance(item, dict)]
    return []


def _classify_check(name: str, conclusion: str, status: str) -> str:
    text = f"{conclusion} {status}".lower()
    if any(token in text for token in ("failure", "failed", "fail", "cancelled", "timed_out")):
        return "failed"
    if any(token in text for token in ("success", "passed", "pass")):
        return "passed"
    return "pending"


def _checks_from_dict(value: dict[str, Any]) -> tuple[list[str], list[str]]:
    passed: list[str] = []
    failed: list[str] = []
    for node in _check_nodes(value):
        name = str(node.get("name", node.get("workflowName", node.get("context", ""))))
        if not name:
            continue
        classification = _classify_check(
            name,
            str(node.get("conclusion", node.get("state", ""))),
            str(node.get("status", "")),
        )
        if classification == "passed":
            passed.append(name)
        elif classification == "failed":
            failed.append(name)
    return passed, failed


def _checks_from_text(text: str) -> tuple[list[str], list[str]]:
    passed: list[str] = []
    failed: list[str] = []
    for line in text.splitlines():
        lower = line.lower()
        if REQUIRED_VALIDATE_CHECK not in lower:
            continue
        if re.search(r"pass|success|✓|completed", lower):
            passed.append(REQUIRED_VALIDATE_CHECK)
        elif re.search(r"fail|failure|x|✗", lower):
            failed.append(REQUIRED_VALIDATE_CHECK)
    return passed, failed


def build_github_pr_state(pr_fixture: str | dict[str, Any]) -> dict[str, Any]:
    text = _as_text(pr_fixture)
    lower = text.lower()
    if isinstance(pr_fixture, dict):
        checks_passed, checks_failed = _checks_from_dict(pr_fixture)
    else:
        checks_passed, checks_failed = _checks_from_text(text)

    no_checks_reported = "no checks reported" in lower or "no checks" in lower
    checks_attached = bool(checks_passed or checks_failed) and not no_checks_reported
    required_validate_present = REQUIRED_VALIDATE_CHECK in {item.lower() for item in checks_passed + checks_failed}

    if no_checks_reported or not checks_attached:
        merge_allowed = False
        merge_block_reason = "no_checks_reported"
    elif REQUIRED_VALIDATE_CHECK in {item.lower() for item in checks_failed}:
        merge_allowed = False
        merge_block_reason = "validate_check_failed"
    elif not required_validate_present:
        merge_allowed = False
        merge_block_reason = "required_validate_missing"
    else:
        merge_allowed = True
        merge_block_reason = "none"

    next_safe_action = (
        "Merge may be considered only after Anthony approval."
        if merge_allowed
        else "Wait for the required validate check before any merge decision."
    )
    if merge_block_reason == "validate_check_failed":
        next_safe_action = "Repair the validate failure before any merge decision."

    return {
        "schema": SCHEMA,
        "pr_number": _extract_pr_number(pr_fixture, text),
        "branch": _extract_branch(pr_fixture, text),
        "checks_attached": checks_attached,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "required_validate_present": required_validate_present,
        "merge_allowed": merge_allowed,
        "merge_block_reason": merge_block_reason,
        "next_safe_action": next_safe_action,
        "command_preview": [
            "gh pr checks <number> --json name,conclusion,status",
            "gh pr view <number> --json number,headRefName,statusCheckRollup",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a GitHub PR/check state parser contract.")
    parser.add_argument("--text", default="no checks reported", help="Optional gh-style text fixture.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state = build_github_pr_state(args.text)
    print(json.dumps(state, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
