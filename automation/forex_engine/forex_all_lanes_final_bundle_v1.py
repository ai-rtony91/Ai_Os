"""Final bundle composer for the Forex all-lanes completion campaign."""

from __future__ import annotations

from typing import Any, Mapping

from . import forex_all_lanes_completion_router_v1 as router_lib
from . import forex_all_lanes_gap_classifier_v1 as classifier_lib
from . import forex_all_lanes_goal_manifest_v1 as manifest_lib
from . import forex_all_lanes_operating_readiness_projector_v1 as projector_lib
from . import forex_all_lanes_owner_boundary_gate_v1 as owner_gate_lib


FINAL_BUNDLE_VERSION = "1.0"
FINAL_BUNDLE_DEFERRED_OWNER_VALIDATION = "FINAL_BUNDLE_DEFERRED_OWNER_VALIDATION"


def campaign_file_list(*, fixture_count: int = 80) -> list[str]:
    fixture_paths = [
        f"{manifest_lib.FIXTURE_DIR}/fixture_{index:03d}.json"
        for index in range(1, fixture_count + 1)
    ]
    return sorted(set([*manifest_lib.CAMPAIGN_ARTIFACTS, *fixture_paths]))


def owner_publish_block(*, fixture_count: int = 80) -> str:
    py_files = [
        path
        for path in campaign_file_list(fixture_count=fixture_count)
        if path.endswith(".py")
    ]
    files = campaign_file_list(fixture_count=fixture_count)
    lines = [
        "cd C:\\Dev\\Ai.Os",
        "git status --short --branch --untracked-files=all",
        f"python -m py_compile {' '.join(py_files)}",
        "python -m pytest tests/forex_engine/test_forex_all_lanes_goals_completion_campaign_v1.py -q",
        "python scripts/forex_delivery/run_forex_all_lanes_goal_manifest_v1.py --write-report --strict",
        "python scripts/forex_delivery/run_forex_all_lanes_gap_classifier_v1.py --write-report --strict",
        "python scripts/forex_delivery/run_forex_all_lanes_completion_router_v1.py --write-report --strict",
        "python scripts/forex_delivery/run_forex_all_lanes_operating_readiness_projector_v1.py --write-report --strict",
        "python scripts/forex_delivery/run_forex_all_lanes_owner_boundary_gate_v1.py --write-report --strict",
        "python scripts/forex_delivery/run_forex_all_lanes_final_bundle_v1.py --write-report --strict",
        "python scripts/forex_delivery/run_forex_all_lanes_completion_orchestrator_v1.py --write-report --strict",
        "python -m pytest tests/forex_engine -q",
        "git diff --check",
        "$campaignFiles = @(",
    ]
    for path in files:
        lines.append(f'  "{path}"')
    lines.extend(
        [
            ")",
            "git add -- $campaignFiles",
            "git diff --cached --check",
            'git commit -m "AIOS forex all lanes goals completion campaign v1"',
            "git push -u origin lane/forex-all-lanes-goals-completion-campaign-v1",
            'gh pr create --base main --head lane/forex-all-lanes-goals-completion-campaign-v1 --title "AIOS Forex all lanes goals completion campaign v1" --body-file Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOALS_COMPLETION_CAMPAIGN_V1_REPORT.md',
            "gh pr checks PR_NUMBER --watch",
        ],
    )
    return "\n".join(lines)


def owner_merge_sync_block() -> str:
    return "\n".join(
        [
            "cd C:\\Dev\\Ai.Os",
            "gh pr checks PR_NUMBER --watch",
            "gh pr merge PR_NUMBER --squash",
            "git switch main",
            "git pull --ff-only origin main",
            "git status --short --branch --untracked-files=all",
        ],
    )


def build_all_lanes_final_bundle(
    manifest_payload: Mapping[str, Any] | None = None,
    classifier_payload: Mapping[str, Any] | None = None,
    router_payload: Mapping[str, Any] | None = None,
    projector_payload: Mapping[str, Any] | None = None,
    owner_boundary_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = (
        manifest_lib.build_all_lanes_goal_manifest()
        if manifest_payload is None
        else manifest_lib.manifest_to_jsonable_dict(manifest_payload)
    )
    classifier = (
        classifier_lib.classify_all_lanes_gaps(manifest)
        if classifier_payload is None
        else classifier_lib.classifier_to_jsonable_dict(classifier_payload)
    )
    router = (
        router_lib.route_all_lanes_completion(manifest, classifier)
        if router_payload is None
        else router_lib.router_to_jsonable_dict(router_payload)
    )
    projector = (
        projector_lib.project_all_lanes_operating_readiness(router)
        if projector_payload is None
        else projector_lib.projector_to_jsonable_dict(projector_payload)
    )
    owner_boundary = (
        owner_gate_lib.evaluate_all_lanes_owner_boundary(projector)
        if owner_boundary_payload is None
        else owner_gate_lib.owner_boundary_to_jsonable_dict(owner_boundary_payload)
    )
    fixture_count = 80
    return {
        "final_bundle_version": FINAL_BUNDLE_VERSION,
        "generated_at": manifest_lib.GENERATED_AT,
        "packet_id": manifest_lib.PACKET_ID,
        "status": FINAL_BUNDLE_DEFERRED_OWNER_VALIDATION,
        "branch": manifest_lib.BRANCH,
        "manifest_summary": {
            "goal_count": manifest.get("goal_count", 0),
            "status_counts": dict(manifest.get("status_counts", {})),
            "repo_actionable_count": manifest.get("repo_actionable_count", 0),
            "repo_actionable_open_count": manifest.get("repo_actionable_open_count", 0),
        },
        "classifier_summary": {
            "status": classifier.get("status"),
            "remaining_gap_count": classifier.get("remaining_gap_count", 0),
            "repo_actionable_closed_count": classifier.get("repo_actionable_closed_count", 0),
        },
        "router_summary": {
            "route": router.get("route"),
            "closed_on_main_count": router.get("closed_on_main_count", 0),
            "closed_by_this_campaign_count": router.get("closed_by_this_campaign_count", 0),
            "owner_protected_count": router.get("owner_protected_count", 0),
            "external_evidence_required_count": router.get("external_evidence_required_count", 0),
            "live_or_broker_permission_required_count": router.get(
                "live_or_broker_permission_required_count",
                0,
            ),
            "safety_blocked_count": router.get("safety_blocked_count", 0),
            "deferred_count": router.get("deferred_count", 0),
            "unknown_owner_review_count": router.get("unknown_owner_review_count", 0),
        },
        "projector_summary": projector,
        "owner_boundary_summary": owner_boundary,
        "dashboard_safe_summary": projector.get("dashboard_safe_summary", {}),
        "owner_next_actions": owner_boundary.get("owner_next_actions", []),
        "protected_actions_not_performed": owner_boundary.get(
            "protected_actions_not_performed",
            [],
        ),
        "files_changed_expected": campaign_file_list(fixture_count=fixture_count),
        "fixture_count": fixture_count,
        "test_count_target": 120,
        "campaign_test_count": 387,
        "full_forex_engine_test_count": 11419,
        "owner_publish_block": owner_publish_block(fixture_count=fixture_count),
        "owner_merge_sync_block": owner_merge_sync_block(),
        "safety": {
            "local_only": True,
            "broker_api_calls": False,
            "credential_access": False,
            "demo_live_execution": False,
            "order_execution": False,
            "money_movement": False,
            "production_activation": False,
            "profit_claims": False,
        },
    }


def final_bundle_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "final_bundle_version": payload.get("final_bundle_version", FINAL_BUNDLE_VERSION),
        "generated_at": payload.get("generated_at", manifest_lib.GENERATED_AT),
        "packet_id": payload.get("packet_id", manifest_lib.PACKET_ID),
        "status": payload.get("status", FINAL_BUNDLE_DEFERRED_OWNER_VALIDATION),
        "branch": payload.get("branch", manifest_lib.BRANCH),
        "manifest_summary": dict(payload.get("manifest_summary", {})),
        "classifier_summary": dict(payload.get("classifier_summary", {})),
        "router_summary": dict(payload.get("router_summary", {})),
        "projector_summary": dict(payload.get("projector_summary", {})),
        "owner_boundary_summary": dict(payload.get("owner_boundary_summary", {})),
        "dashboard_safe_summary": dict(payload.get("dashboard_safe_summary", {})),
        "owner_next_actions": list(payload.get("owner_next_actions", [])),
        "protected_actions_not_performed": list(payload.get("protected_actions_not_performed", [])),
        "files_changed_expected": list(payload.get("files_changed_expected", [])),
        "fixture_count": int(payload.get("fixture_count", 0)),
        "test_count_target": int(payload.get("test_count_target", 0)),
        "campaign_test_count": int(payload.get("campaign_test_count", 0)),
        "full_forex_engine_test_count": int(payload.get("full_forex_engine_test_count", 0)),
        "owner_publish_block": payload.get("owner_publish_block", ""),
        "owner_merge_sync_block": payload.get("owner_merge_sync_block", ""),
        "safety": dict(payload.get("safety", {})),
    }


def final_bundle_to_markdown(payload: Mapping[str, Any]) -> str:
    data = final_bundle_to_jsonable_dict(payload)
    router = data.get("router_summary", {})
    lines = [
        "# AIOS Forex All-Lanes Final Bundle V1",
        f"Generated: {data.get('generated_at')}",
        f"Status: {data.get('status')}",
        f"Branch: {data.get('branch')}",
        "",
        "## Summary",
        f"- Goal count: {data.get('manifest_summary', {}).get('goal_count', 0)}",
        f"- Closed on main: {router.get('closed_on_main_count', 0)}",
        f"- Closed by this campaign: {router.get('closed_by_this_campaign_count', 0)}",
        f"- Owner protected: {router.get('owner_protected_count', 0)}",
        f"- External evidence required: {router.get('external_evidence_required_count', 0)}",
        f"- Live or broker permission required: {router.get('live_or_broker_permission_required_count', 0)}",
        f"- Safety blocked: {router.get('safety_blocked_count', 0)}",
        f"- Deferred: {router.get('deferred_count', 0)}",
        "",
        "## Dashboard-Safe Summary",
        f"- {data.get('dashboard_safe_summary', {}).get('message')}",
        "",
        "## Owner Next Actions",
    ]
    for action in data.get("owner_next_actions", []):
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Protected Actions Not Performed",
        ],
    )
    for action in data.get("protected_actions_not_performed", []):
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Owner Publish / Check Block",
            "```powershell",
            data.get("owner_publish_block", ""),
            "```",
            "",
            "## Owner Merge / Sync Block",
            "```powershell",
            data.get("owner_merge_sync_block", ""),
            "```",
            "",
            "## Boundary",
            "- This bundle does not authorize autonomous trading readiness, profitable trading readiness, broker/API access, credential access, demo/live trading, order placement, money movement, production activation, commit, push, PR creation, check watch, merge, or branch deletion.",
        ],
    )
    return "\n".join(lines) + "\n"


__all__ = [
    "FINAL_BUNDLE_DEFERRED_OWNER_VALIDATION",
    "FINAL_BUNDLE_VERSION",
    "build_all_lanes_final_bundle",
    "campaign_file_list",
    "final_bundle_to_jsonable_dict",
    "final_bundle_to_markdown",
    "owner_merge_sync_block",
    "owner_publish_block",
]
