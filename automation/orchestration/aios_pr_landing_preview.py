from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_PR_LANDING_PREVIEW.v1"

PASS_STATUSES = {
    "pass",
    "passed",
    "passing",
    "success",
    "successful",
    "green",
    "completed_success",
}
PENDING_STATUSES = {
    "pending",
    "queued",
    "in_progress",
    "running",
    "waiting",
    "missing",
    "unknown",
    "not_run",
}
FAIL_STATUSES = {
    "fail",
    "failed",
    "failure",
    "error",
    "cancelled",
    "canceled",
    "timed_out",
    "red",
}
MERGEABLE_STATUSES = {"true", "yes", "mergeable", "clean", "ready"}
NON_MERGEABLE_STATUSES = {"false", "no", "blocked", "dirty", "conflicting", "unknown"}

UNSAFE_PATH_PREFIXES = (
    ".github/workflows/",
    "automation/orchestration/approval_inbox/",
    "automation/orchestration/work_packets/active/",
    "automation/orchestration/work_packets/blocked/",
    "automation/orchestration/workers/inbox/",
    "apps/trading_lab/trading_lab/execution/",
    "aios/modules/trader/",
    "services/runtime/",
    "services/dispatcher/",
    "services/policy/",
    "services/telemetry/",
    "telemetry/",
    "reports/",
    "control/review_bridge/",
)
UNSAFE_PATH_TERMS = (
    ".env",
    "secret",
    "credential",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "broker",
    "oanda",
    "live_trading",
    "live-order",
    "live_order",
    "real-order",
    "real_order",
    "webhook",
)
UNSAFE_SUMMARY_TERMS = (
    "unsafe",
    "failed",
    "failure",
    "secret",
    "credential",
    "broker",
    "oanda",
    "live trading",
    "live_trading",
    "real order",
    "real_order",
    "webhook",
    "approval mutation",
    "queue mutation",
)
SAFE_SUMMARY_TERMS = ("safe", "pass", "passed", "success", "preview-only", "no protected")


def _safety() -> dict[str, bool]:
    return {
        "preview_only": True,
        "command_execution": False,
        "gh_execution": False,
        "git_execution": False,
        "network_access": False,
        "github_mutation": False,
        "approval_mutation": False,
        "queue_mutation": False,
        "merge": False,
        "push": False,
        "branch_deletion": False,
        "reset": False,
        "local_main_sync": False,
        "reports_written": False,
        "files_written": False,
        "required_human_approval": True,
    }


def _forbidden_actions() -> list[str]:
    return [
        "gh pr merge",
        "git merge",
        "git push",
        "git reset",
        "git branch -d",
        "git branch -D",
        "delete_head_branch",
        "mutate_approval_state",
        "mutate_queue_state",
        "bypass_checks",
        "bypass_branch_protection",
    ]


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "y", "1"}:
            return True
        if normalized in {"false", "no", "n", "0"}:
            return False
    return None


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _text(value).lower().replace("-", "_").replace(" ", "_")


def _changed_files(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        separators = value.replace("\r", "\n").replace(",", "\n").splitlines()
        return [item.strip() for item in separators if item.strip()]
    return []


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def _checks_status(value: Any, validation_summary: Any) -> str:
    normalized = _normalized(value)
    validation = _text(validation_summary).lower()
    if normalized in FAIL_STATUSES or _contains_any(validation, ("check failed", "checks failed", "ci failed")):
        return "failed"
    if normalized in PENDING_STATUSES or _contains_any(validation, ("check pending", "checks pending", "ci pending")):
        return "pending"
    if normalized in PASS_STATUSES:
        return "passed"
    if _contains_any(validation, ("validation failed", "pytest failed", "test failed")):
        return "failed"
    if _contains_any(validation, ("validation pending", "pytest pending", "test pending", "not run")):
        return "pending"
    if _contains_any(validation, ("validation passed", "pytest passed", "tests passed", "success")):
        return "passed"
    return "missing"


def _validation_status(value: Any) -> str:
    summary = _text(value).lower()
    if not summary:
        return "missing"
    if _contains_any(summary, ("failed", "failure", "error", "blocked")):
        return "failed"
    if _contains_any(summary, ("pending", "not run", "missing", "queued", "running")):
        return "pending"
    if _contains_any(summary, ("passed", "pass", "success", "green")):
        return "passed"
    return "unknown"


def _mergeable_status(value: Any) -> str:
    bool_value = _as_bool(value)
    if bool_value is True:
        return "mergeable"
    if bool_value is False:
        return "blocked"
    normalized = _normalized(value)
    if normalized in MERGEABLE_STATUSES:
        return "mergeable"
    if normalized in NON_MERGEABLE_STATUSES:
        return "blocked"
    return "unknown"


def _scope_status(files: list[str]) -> tuple[str, list[str]]:
    if not files:
        return "blocked", ["changed_files_missing"]
    unsafe: list[str] = []
    for path in files:
        normalized = path.replace("\\", "/").strip().lower()
        if normalized.startswith(UNSAFE_PATH_PREFIXES) or any(term in normalized for term in UNSAFE_PATH_TERMS):
            unsafe.append(path)
    if unsafe:
        return "blocked", [f"unsafe_changed_file_scope:{path}" for path in unsafe]
    return "safe", []


def _safety_status(summary: Any) -> str:
    text = _text(summary).lower()
    if not text:
        return "blocked"
    if _contains_any(text, UNSAFE_SUMMARY_TERMS):
        return "blocked"
    if _contains_any(text, SAFE_SUMMARY_TERMS):
        return "safe"
    return "blocked"


def _local_status(value: Any) -> str:
    text = _text(value).lower()
    if not text:
        return "blocked"
    if _contains_any(text, ("conflict", "diverged", "behind", "ahead", "dirty", "uncommitted")):
        return "blocked"
    if _contains_any(text, ("clean", "synced", "main...origin/main", "up to date", "up-to-date")):
        return "safe"
    return "blocked"


def _proposed_commands(pr_number: int | None, landing_status: str) -> list[str]:
    if pr_number is None:
        return ["gh pr list --state open --base main"]

    commands = [
        f"gh pr view {pr_number} --json number,state,isDraft,mergeable,baseRefName,headRefName,additions,deletions,changedFiles,statusCheckRollup",
        f"gh pr checks {pr_number} --watch",
        f"powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/pr_gates/Merge-AiOsPullRequest.DRY_RUN.ps1 -PrNumber {pr_number} -Json",
    ]
    if landing_status == "ready":
        commands.append("STOP: request Anthony approval before merge, push, branch deletion, reset, or local main sync")
    return commands


def _next_safe_action(landing_status: str, pr_number: int | None) -> str:
    if landing_status == "ready":
        return f"PR #{pr_number} is ready as evidence only. Stop and request explicit Anthony merge approval before any protected landing action."
    if landing_status == "rejected":
        return "Stop and repair rejected PR evidence before requesting merge approval."
    if landing_status == "blocked":
        return "Resolve blocked readiness evidence, then regenerate the PR landing preview."
    return "Collect local PR evidence first; no PR landing plan is available without a PR number and open PR state."


def build_pr_landing_preview(pr_evidence: Any) -> dict[str, Any]:
    evidence = _as_dict(pr_evidence)
    pr_number = _as_int(evidence.get("pr_number"))
    pr_state = _text(evidence.get("pr_state"))
    draft = _as_bool(evidence.get("draft")) is True
    mergeable_status = _mergeable_status(evidence.get("mergeable"))
    checks_status = _checks_status(evidence.get("checks_status"), evidence.get("validation_summary"))
    validation_status = _validation_status(evidence.get("validation_summary"))
    changed_files = _changed_files(evidence.get("changed_files"))
    scope_status, scope_reasons = _scope_status(changed_files)
    safety_status = _safety_status(evidence.get("safety_summary"))
    local_status = _local_status(evidence.get("local_branch_status"))
    base_branch = _text(evidence.get("base_branch"))
    head_branch = _text(evidence.get("head_branch"))

    blocked_reasons: list[str] = []
    rejected_reasons: list[str] = []

    if pr_number is None or not pr_state:
        landing_status = "no_pr"
        blocked_reasons.append("missing_pr_evidence")
    else:
        normalized_state = _normalized(pr_state)
        if normalized_state not in {"open", "opened"}:
            rejected_reasons.append(f"pr_not_open:{pr_state}")
        if draft:
            blocked_reasons.append("draft_pr")
        if mergeable_status != "mergeable":
            blocked_reasons.append(f"pr_not_mergeable:{mergeable_status}")
        if checks_status == "failed":
            rejected_reasons.append("checks_failed")
        elif checks_status != "passed":
            blocked_reasons.append(f"checks_not_passed:{checks_status}")
        if validation_status == "failed":
            rejected_reasons.append("validation_failed")
        elif validation_status != "passed":
            blocked_reasons.append(f"validation_not_passed:{validation_status}")
        if base_branch != "main":
            blocked_reasons.append(f"base_branch_not_main:{base_branch or 'missing'}")
        if not head_branch:
            blocked_reasons.append("head_branch_missing")
        if scope_status != "safe":
            blocked_reasons.extend(scope_reasons)
        if safety_status != "safe":
            blocked_reasons.append("safety_summary_not_safe")
        if local_status != "safe":
            blocked_reasons.append("local_branch_status_not_safe")

        if rejected_reasons:
            landing_status = "rejected"
        elif blocked_reasons:
            landing_status = "blocked"
        else:
            landing_status = "ready"

    all_reasons = list(dict.fromkeys(rejected_reasons + blocked_reasons))
    return {
        "schema": SCHEMA,
        "landing_status": landing_status,
        "pr_number": pr_number,
        "merge_allowed_by_policy": False,
        "required_human_approval": True,
        "checks_required": True,
        "checks_passed": checks_status == "passed",
        "scope_status": scope_status,
        "safety_status": safety_status,
        "blocked_reasons": all_reasons,
        "proposed_landing_commands": _proposed_commands(pr_number, landing_status),
        "forbidden_actions": _forbidden_actions(),
        "commands_executed": [],
        "branches_deleted": False,
        "merges_performed": False,
        "pushes_performed": False,
        "resets_performed": False,
        "safety": _safety(),
        "next_safe_action": _next_safe_action(landing_status, pr_number),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a preview-only AIOS PR landing plan from local evidence.")
    parser.add_argument("--evidence", default="{}", help="JSON PR evidence payload.")
    return parser


def _load_evidence(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    preview = build_pr_landing_preview(_load_evidence(args.evidence))
    print(json.dumps(preview, indent=2, sort_keys=False))
    return 0 if preview["landing_status"] in {"ready", "blocked", "no_pr"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
