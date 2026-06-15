from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_SAFE_PR_AUTOLAND_POLICY.v1"

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

REQUIRED_CONDITIONS = [
    "pr_open",
    "not_draft",
    "mergeable",
    "checks_success",
    "base_branch_main",
    "head_branch_not_main",
    "expected_head_sha_matches",
    "changed_files_allowed",
    "no_protected_files",
    "no_credential_or_secret_paths",
    "no_broker_live_trading_order_or_webhook_paths",
    "no_approval_mutation_paths",
    "no_queue_mutation_paths",
    "no_scheduler_or_daemon_activation_paths",
    "safety_summary_low_risk",
    "validation_summary_not_failed",
]

ALLOWED_PATH_PREFIXES = (
    "automation/",
    "docs/",
    "tests/",
)
PROTECTED_PATH_EXACT = {
    "agents.md",
    "readme.md",
    "whitepaper.md",
    "architecture.md",
    "deployment.md",
    "source_log.md",
    "error_log.md",
    "hallucination_log.md",
    "risk_policy.md",
    "daily_report.md",
    "aar.md",
}
PROTECTED_PATH_PREFIXES = (
    ".github/",
    "docs/governance/",
    "docs/ai_os/governance/",
    "reports/",
    "control/review_bridge/",
)
SECRET_PATH_TERMS = (
    ".env",
    "/secret",
    "secrets/",
    "credential",
    "credentials/",
    "token",
    "api_key",
    "apikey",
    "private_key",
    ".pem",
    ".pfx",
)
BROKER_LIVE_PATH_TERMS = (
    "broker",
    "oanda",
    "live_trading",
    "live-trading",
    "live_order",
    "live-order",
    "real_order",
    "real-order",
    "/orders/",
    "/order_",
    "-order",
    "order_execution",
    "webhook",
)
APPROVAL_MUTATION_PATH_TERMS = (
    "approval_inbox",
    "approvals/",
    "/approval/",
    "approval_queue",
    "approval_mutation",
)
QUEUE_MUTATION_PATH_TERMS = (
    "work_packets/active/",
    "work_packets/blocked/",
    "workers/inbox/",
    "command_queue",
    "queue/",
    "queue_mutation",
)
SCHEDULER_DAEMON_PATH_TERMS = (
    "scheduler",
    "daemon",
    "scheduled_task",
    "startup_task",
)
HIGH_RISK_SUMMARY_TERMS = (
    "unsafe",
    "high-risk flag",
    "high risk flag",
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
    "scheduler",
    "daemon",
    "worker dispatch",
)
NEGATED_HIGH_RISK_SUMMARY_TERMS = (
    "no high-risk",
    "no high risk",
    "without high-risk",
    "without high risk",
)


def _safety(safe_to_autoland: bool) -> dict[str, bool]:
    return {
        "preview_only": True,
        "evidence_only": True,
        "safe_to_autoland": safe_to_autoland,
        "command_execution": False,
        "gh_execution": False,
        "git_execution": False,
        "network_access": False,
        "approval_mutation": False,
        "queue_mutation": False,
        "scheduler_activation": False,
        "daemon_activation": False,
        "worker_dispatch": False,
        "merge": False,
        "push": False,
        "branch_deletion": False,
        "reset": False,
        "files_written": False,
        "reports_written": False,
    }


def _forbidden_actions() -> list[str]:
    return [
        "execute_gh_from_planner",
        "execute_git_from_planner",
        "merge_without_safe_autoland_eligibility",
        "push_from_planner",
        "delete_branch_from_planner",
        "reset_from_planner",
        "mutate_approval_state",
        "mutate_queue_state",
        "start_scheduler",
        "start_daemon",
        "dispatch_worker",
        "access_network_from_planner",
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


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip().lower()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _checks_status(value: Any) -> str:
    normalized = _normalized(value)
    if normalized in FAIL_STATUSES:
        return "failed"
    if normalized in PENDING_STATUSES:
        return "pending"
    if normalized in PASS_STATUSES:
        return "success"
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


def _path_flags(files: list[str]) -> dict[str, list[str]]:
    flags = {
        "outside_allowed_scope": [],
        "protected": [],
        "secret": [],
        "broker_live_order_webhook": [],
        "approval_mutation": [],
        "queue_mutation": [],
        "scheduler_daemon": [],
    }
    for raw_path in files:
        path = _normalize_path(raw_path)
        if not path.startswith(ALLOWED_PATH_PREFIXES):
            flags["outside_allowed_scope"].append(raw_path)
        if path in PROTECTED_PATH_EXACT or path.startswith(PROTECTED_PATH_PREFIXES):
            flags["protected"].append(raw_path)
        if _contains_any(path, SECRET_PATH_TERMS):
            flags["secret"].append(raw_path)
        if _contains_any(path, BROKER_LIVE_PATH_TERMS):
            flags["broker_live_order_webhook"].append(raw_path)
        if _contains_any(path, APPROVAL_MUTATION_PATH_TERMS):
            flags["approval_mutation"].append(raw_path)
        if _contains_any(path, QUEUE_MUTATION_PATH_TERMS):
            flags["queue_mutation"].append(raw_path)
        if _contains_any(path, SCHEDULER_DAEMON_PATH_TERMS):
            flags["scheduler_daemon"].append(raw_path)
    return flags


def _safety_summary_has_high_risk(value: Any) -> bool:
    summary = _text(value).lower()
    if not summary:
        return True
    if _contains_any(summary, NEGATED_HIGH_RISK_SUMMARY_TERMS):
        scrubbed = summary
        for term in NEGATED_HIGH_RISK_SUMMARY_TERMS:
            scrubbed = scrubbed.replace(term, "")
        return _contains_any(scrubbed, HIGH_RISK_SUMMARY_TERMS)
    return _contains_any(summary, HIGH_RISK_SUMMARY_TERMS)


def _proposed_commands(pr_number: int | None, safe_to_autoland: bool) -> list[str]:
    if pr_number is None or not safe_to_autoland:
        return []
    return [
        f"gh pr checks {pr_number}",
        f"gh pr merge {pr_number} --squash --delete-branch",
        "git fetch origin",
        "git reset --hard origin/main",
        "git status --short --branch",
    ]


def _next_safe_action(autoland_status: str, pr_number: int | None) -> str:
    if autoland_status == "eligible":
        return (
            f"PR #{pr_number} is SAFE_AUTO_LAND_ELIGIBLE as evidence only. "
            "Protected landing commands still require the external approval-gated runner."
        )
    if autoland_status == "rejected":
        return "Stop auto-land. Repair or replace the rejected PR evidence before any landing action."
    if autoland_status == "blocked":
        return "Resolve blocked eligibility evidence, then regenerate the safe PR auto-land policy preview."
    return "Collect open PR evidence before producing any auto-land plan."


def _append_reason(target: list[str], reason: str) -> None:
    if reason not in target:
        target.append(reason)


def build_safe_pr_autoland_policy(pr_evidence: Any) -> dict[str, Any]:
    evidence = _as_dict(pr_evidence)
    pr_number = _as_int(evidence.get("pr_number"))
    pr_state = _text(evidence.get("pr_state"))
    draft_value = _as_bool(evidence.get("draft"))
    mergeable_status = _mergeable_status(evidence.get("mergeable"))
    checks_status = _checks_status(evidence.get("checks_status"))
    validation_status = _validation_status(evidence.get("validation_summary"))
    changed_files = _changed_files(evidence.get("changed_files"))
    base_branch = _text(evidence.get("base_branch"))
    head_branch = _text(evidence.get("head_branch"))
    base_branch_normalized = base_branch.lower()
    head_branch_normalized = head_branch.lower()
    head_sha = _text(evidence.get("head_sha"))
    expected_head_sha = _text(evidence.get("expected_head_sha"))
    path_flags = _path_flags(changed_files)

    passed_conditions: list[str] = []
    blocked_reasons: list[str] = []
    rejected_reasons: list[str] = []

    def record(condition: str, passed: bool, reason: str, rejected: bool = False) -> None:
        if passed:
            passed_conditions.append(condition)
        elif rejected:
            _append_reason(rejected_reasons, reason)
        else:
            _append_reason(blocked_reasons, reason)

    if pr_number is None or not pr_state:
        autoland_status = "no_pr"
        _append_reason(blocked_reasons, "missing_pr_evidence")
    else:
        normalized_state = _normalized(pr_state)
        record(
            "pr_open",
            normalized_state in {"open", "opened"},
            f"pr_not_open:{pr_state}",
            rejected=True,
        )
        record("not_draft", draft_value is False, "draft_pr" if draft_value is True else "draft_status_missing")
        record(
            "mergeable",
            mergeable_status == "mergeable",
            f"pr_not_mergeable:{mergeable_status}",
        )
        if checks_status == "failed":
            record("checks_success", False, "checks_failed", rejected=True)
        else:
            record("checks_success", checks_status == "success", f"checks_not_success:{checks_status}")
        record(
            "base_branch_main",
            base_branch_normalized == "main",
            f"base_branch_not_main:{base_branch or 'missing'}",
        )
        record(
            "head_branch_not_main",
            bool(head_branch) and head_branch_normalized != "main",
            f"head_branch_not_safe:{head_branch or 'missing'}",
            rejected=head_branch_normalized == "main",
        )

        if not head_sha or not expected_head_sha:
            record("expected_head_sha_matches", False, "head_sha_evidence_missing")
        else:
            record(
                "expected_head_sha_matches",
                head_sha == expected_head_sha,
                "expected_head_sha_mismatch",
                rejected=True,
            )

        changed_files_allowed = bool(changed_files) and not path_flags["outside_allowed_scope"]
        record(
            "changed_files_allowed",
            changed_files_allowed,
            "changed_files_missing" if not changed_files else "changed_files_outside_allowed_scope",
        )
        record(
            "no_protected_files",
            not path_flags["protected"],
            "protected_file_path:" + ",".join(path_flags["protected"]),
        )
        record(
            "no_credential_or_secret_paths",
            not path_flags["secret"],
            "credential_or_secret_path:" + ",".join(path_flags["secret"]),
            rejected=bool(path_flags["secret"]),
        )
        record(
            "no_broker_live_trading_order_or_webhook_paths",
            not path_flags["broker_live_order_webhook"],
            "broker_live_trading_order_or_webhook_path:"
            + ",".join(path_flags["broker_live_order_webhook"]),
            rejected=bool(path_flags["broker_live_order_webhook"]),
        )
        record(
            "no_approval_mutation_paths",
            not path_flags["approval_mutation"],
            "approval_mutation_path:" + ",".join(path_flags["approval_mutation"]),
        )
        record(
            "no_queue_mutation_paths",
            not path_flags["queue_mutation"],
            "queue_mutation_path:" + ",".join(path_flags["queue_mutation"]),
        )
        record(
            "no_scheduler_or_daemon_activation_paths",
            not path_flags["scheduler_daemon"],
            "scheduler_or_daemon_activation_path:" + ",".join(path_flags["scheduler_daemon"]),
        )
        safety_high_risk = _safety_summary_has_high_risk(evidence.get("safety_summary"))
        record("safety_summary_low_risk", not safety_high_risk, "safety_summary_high_risk")
        record(
            "validation_summary_not_failed",
            validation_status != "failed",
            "validation_summary_failed",
            rejected=True,
        )

        if rejected_reasons:
            autoland_status = "rejected"
        elif blocked_reasons:
            autoland_status = "blocked"
        else:
            autoland_status = "eligible"

    safe_to_autoland = autoland_status == "eligible"
    all_reasons = [*rejected_reasons, *blocked_reasons]

    human_wake_required = autoland_status == "rejected"
    sos_reason = ", ".join(rejected_reasons) if rejected_reasons else "none"

    return {
        "schema": SCHEMA,
        "autoland_status": autoland_status,
        "pr_number": pr_number,
        "safe_to_autoland": safe_to_autoland,
        "required_conditions": REQUIRED_CONDITIONS,
        "passed_conditions": passed_conditions,
        "blocked_reasons": all_reasons,
        "forbidden_actions": _forbidden_actions(),
        "proposed_commands": _proposed_commands(pr_number, safe_to_autoland),
        "expected_head_sha": expected_head_sha or None,
        "merge_method": "squash",
        "branch_delete_allowed": safe_to_autoland,
        "local_sync_allowed": safe_to_autoland,
        "human_wake_required": human_wake_required,
        "sos_reason": sos_reason,
        "commands_executed": [],
        "merges_performed": False,
        "pushes_performed": False,
        "branches_deleted": False,
        "resets_performed": False,
        "safety": _safety(safe_to_autoland),
        "next_safe_action": _next_safe_action(autoland_status, pr_number),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview the AIOS safe PR auto-land policy.")
    parser.add_argument("--pr-evidence", default="{}", help="JSON PR landing evidence.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = json.loads(args.pr_evidence)
    except json.JSONDecodeError:
        evidence = {"raw_pr_evidence": args.pr_evidence}
    result = build_safe_pr_autoland_policy(evidence)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
