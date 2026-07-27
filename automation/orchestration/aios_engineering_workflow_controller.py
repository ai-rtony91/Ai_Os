"""Single-pass engineering workflow controller built from canonical components.

The controller consolidates inspection, candidate normalization, queue planning,
validator evidence, PR/CI interpretation, and next-action reporting.  It is
read-only and never performs protected actions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from automation.orchestration.aios_candidate_packet_evidence_adapter import (
    build_candidate_packet_evidence,
)
from automation.orchestration.aios_github_pr_state import build_github_pr_state
from automation.orchestration.aios_packet_queue_planner import build_packet_queue_planner
from automation.orchestration.aios_repo_state_evidence import collect_repo_state
from automation.forex_engine.first_withdrawable_dollar_v1 import evaluate_first_withdrawable_dollar


SCHEMA = "AIOS_ENGINEERING_WORKFLOW_CONTROLLER.v1"


def _validator_summary(selected: dict[str, Any] | None, results: dict[str, Any] | None) -> dict[str, Any]:
    expected = list((selected or {}).get("validators", []))
    supplied = results if isinstance(results, dict) else {}
    missing = [command for command in expected if command not in supplied]
    failed = [command for command in expected if str(supplied.get(command, "")).upper() != "PASS" and command not in missing]
    status = "PASS" if expected and not missing and not failed else "BLOCKED"
    return {
        "status": status,
        "expected": expected,
        "results": {command: supplied[command] for command in expected if command in supplied},
        "missing": missing,
        "failed": failed,
    }


def _next_action(repo: dict[str, Any], queue: dict[str, Any], validators: dict[str, Any], pr: dict[str, Any]) -> str:
    if not repo.get("safe_for_apply"):
        return "REPAIR_REPOSITORY_STATE"
    if queue.get("queue_status") != "selected":
        return "REPAIR_OR_SUPPLY_PACKET_CANDIDATES"
    if validators["status"] != "PASS":
        return "RUN_OR_REPAIR_SELECTED_PACKET_VALIDATORS"
    if pr.get("pr_number") is None:
        return "PREPARE_ONE_PULL_REQUEST"
    if not pr.get("merge_allowed"):
        return "WAIT_OR_REPAIR_CI"
    return "READY_FOR_OWNER_MERGE_REVIEW"


def build_engineering_workflow_report(
    candidate_evidence: Any,
    *,
    pr_evidence: Any = "no checks reported",
    validator_results: dict[str, Any] | None = None,
    anchor_evidence: dict[str, Any] | None = None,
    repo_root: str | Path | None = None,
    repo_state_collector: Callable[..., dict[str, Any]] = collect_repo_state,
) -> dict[str, Any]:
    """Build one deterministic owner report without mutating repository state."""

    repo = repo_state_collector(repo_root)
    normalized = build_candidate_packet_evidence(candidate_evidence)
    queue = build_packet_queue_planner(normalized)
    selected = queue.get("selected_packet")
    validators = _validator_summary(selected, validator_results)
    pr = build_github_pr_state(pr_evidence)
    next_action = _next_action(repo, queue, validators, pr)
    anchor = evaluate_first_withdrawable_dollar(anchor_evidence)

    return {
        "schema": SCHEMA,
        "mode": "READ_ONLY",
        "workflow_status": "READY" if next_action == "READY_FOR_OWNER_MERGE_REVIEW" else "ACTION_REQUIRED",
        "repo_state": repo,
        "candidate_evidence": normalized,
        "queue_plan": queue,
        "selected_packet": selected,
        "validator_evidence": validators,
        "pr_ci_state": pr,
        "next_task": next_action,
        "primary_anchor": anchor,
        "next_verified_anchor_blocker": anchor["next_verified_blocker"],
        "owner_intervention_required": next_action in {
            "PREPARE_ONE_PULL_REQUEST",
            "READY_FOR_OWNER_MERGE_REVIEW",
        },
        "protected_actions": {
            "apply": False,
            "queue_mutation": False,
            "approval_mutation": False,
            "commit": False,
            "push": False,
            "pr_create": False,
            "merge": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compose the canonical AIOS engineering workflow report.")
    parser.add_argument("--candidates", required=True, help="Candidate evidence JSON.")
    parser.add_argument("--pr-evidence", default='"no checks reported"', help="PR/CI evidence JSON.")
    parser.add_argument("--validator-results", default="{}", help="Validator result map JSON.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--anchor-evidence", default="{}")
    args = parser.parse_args(argv)
    report = build_engineering_workflow_report(
        json.loads(args.candidates),
        pr_evidence=json.loads(args.pr_evidence),
        validator_results=json.loads(args.validator_results),
        repo_root=args.repo_root,
        anchor_evidence=json.loads(args.anchor_evidence),
    )
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
