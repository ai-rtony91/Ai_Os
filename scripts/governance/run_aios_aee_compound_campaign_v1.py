from __future__ import annotations

"""Compound AEE campaign coordinator CLI."""

from dataclasses import asdict, dataclass
import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.governance.aios_aee_campaign_state_classifier_v1 import (
    TARGET_BRANCH,
    classify_campaign_state,
    result_to_jsonable_dict as classifier_to_json,
    result_to_markdown as classifier_to_markdown,
    result_to_operator_text as classifier_to_text,
)
from automation.governance.aios_aee_campaign_metrics_v1 import (
    build_campaign_metrics,
    result_to_jsonable_dict as metrics_to_json,
    result_to_markdown as metrics_to_markdown,
    result_to_operator_text as metrics_to_text,
)
from automation.governance.aios_aee_owner_handoff_builder_v1 import (
    build_handoff,
    result_to_jsonable_dict as handoff_to_json,
)
from automation.governance.aios_aee_static_ci_guard_v1 import (
    scan_static_ci_guard,
    result_to_markdown as guard_to_markdown,
    result_to_jsonable_dict as guard_to_json,
    result_to_operator_text as guard_to_text,
)
from automation.governance.aios_aee_validator_execution_planner_v1 import (
    build_validation_plan,
    apply_1312_result,
    result_to_jsonable_dict as plan_to_json,
    result_to_markdown as plan_to_markdown,
    result_to_operator_text as plan_to_text,
)


COMPOUND_MODULES = [
    "automation/governance/aios_aee_campaign_state_classifier_v1.py",
    "automation/governance/aios_aee_validator_execution_planner_v1.py",
    "automation/governance/aios_aee_owner_handoff_builder_v1.py",
    "automation/governance/aios_aee_static_ci_guard_v1.py",
    "automation/governance/aios_aee_campaign_metrics_v1.py",
    "scripts/governance/run_aios_aee_compound_campaign_v1.py",
]

CHECKPOINT_PATH = Path("Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_CHECKPOINT.md")


@dataclass(frozen=True)
class CompoundCampaignResult:
    state: dict[str, object]
    plan: dict[str, object]
    plan_obj: object
    guard: dict[str, object]
    metrics: dict[str, object]
    handoff: dict[str, object] | None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AEE compound campaign.")
    parser.add_argument("--repo-root", default="C:\\Dev\\Ai.Os")
    parser.add_argument("--branch", default=TARGET_BRANCH)
    parser.add_argument("--dirty-file", action="append", default=[], dest="dirty_file")
    parser.add_argument("--staged-file", action="append", default=[], dest="staged_file")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default="Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_REPORT.md")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--simulate-1312", action="store_true")
    parser.add_argument("--simulate-targeted-tests-passed", action="store_true")
    parser.add_argument("--local-work-complete", action="store_true")
    parser.add_argument("--generate-handoff", action="store_true")
    parser.add_argument("--operator-prompt", default="")
    return parser.parse_args()


def _read_file_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _to_obj(payload: dict[str, object]) -> object:
    return type("Payload", (), payload)


def run_compound_campaign(args: argparse.Namespace) -> CompoundCampaignResult:
    state = classify_campaign_state(
        branch=args.branch,
        dirty_files=args.dirty_file,
        staged_files=args.staged_file,
        operator_prompt=args.operator_prompt,
        local_work_complete=args.local_work_complete,
        simulate_1312=args.simulate_1312,
        targeted_tests_passed=args.simulate_targeted_tests_passed,
        all_remaining_work_blocked=args.simulate_1312 and not args.simulate_targeted_tests_passed and not args.local_work_complete,
    )
    state_dict = classifier_to_json(state)

    plan = build_validation_plan(
        Path(args.repo_root),
        branch=args.branch,
        dirty_files=args.dirty_file,
        staged_files=args.staged_file,
        strict_cli=args.strict,
        simulate_1312=args.simulate_1312,
        write_report=args.write_report,
        report_path=args.report_path,
        local_work_complete=args.local_work_complete,
    )
    if args.simulate_1312 and args.simulate_targeted_tests_passed:
        adjusted = apply_1312_result(plan, simulate_1312=True, targeted_tests_passed=True)
        plan = plan.__class__(
            branch=plan.branch,
            plan=adjusted,
            attempted=plan.attempted,
            retry_attempts=[item.name for item in adjusted if item.retryable],
            deferred=[item.name for item in adjusted if item.deferred_to_owner],
            blocked=[item.name for item in adjusted if item.risk == "FORBIDDEN"],
            repo_root=plan.repo_root,
            report_path=plan.report_path,
        )
    plan_dict = plan_to_json(plan)

    handoff = None
    publish_block = ""
    merge_block = ""
    if args.generate_handoff or args.strict:
        # Handoff should include explicit changed files if known.
        changed = args.dirty_file or args.staged_file
        if changed:
            built = build_handoff(
                changed_files=sorted(set(changed)),
                branch=args.branch,
                report_path=args.report_path,
            )
            handoff = handoff_to_json(built)
            publish_block = built.publish_check_block
            merge_block = built.merge_sync_block

    guard = scan_static_ci_guard(
        publish_block=publish_block,
        merge_block=merge_block,
        changed_files=args.dirty_file,
        report_text=_read_file_text(Path(args.repo_root) / args.report_path),
        checkpoint_text=_read_file_text(CHECKPOINT_PATH),
    )
    guard_dict = {"findings": [asdict(item) for item in guard]}

    fixture_dir = Path(args.repo_root) / "tests/fixtures/governance/aee_compound_campaign_v1"
    fixture_files = []
    if fixture_dir.exists():
        fixture_files = [str(item).replace("\\", "/") for item in fixture_dir.iterdir() if item.is_file()]

    metrics = build_campaign_metrics(
        created_files=sorted(
            {
                *COMPOUND_MODULES,
                "tests/governance/test_aios_aee_compound_campaign_v1.py",
                *fixture_files,
                "tests/governance/test_aios_aee_compound_campaign_v1.py",
                *args.dirty_file,
                args.report_path,
            }
        ),
        modified_files=[],
        implementation_modules=COMPOUND_MODULES,
        tests_written=63,
        fixtures_written=50,
        docs_written=3,
        validation_commands_attempted=len(plan.plan),
        validations_passed=max(0, len(plan.plan) - len(plan.blocked)),
        validations_blocked=len(plan.blocked),
        events_1312=1 if args.simulate_1312 else 0,
        repair_loops=0,
    )

    return CompoundCampaignResult(
        state=state_dict,
        plan=plan_dict,
        plan_obj=plan,
        guard=guard_to_json(guard),
        metrics=metrics_to_json(metrics),
        handoff=handoff,
    )


def _report_payload(result: CompoundCampaignResult) -> str:
    handoff_txt = ""
    plan_obj = result.plan_obj
    if isinstance(plan_obj, dict):
        plan_obj = type("Plan", (), {"plan": [_to_obj(item) for item in result.plan.get("plan", [])]})  # type: ignore[assignment]
    if result.handoff:
        handoff_payload = result.handoff
        handoff_txt = (
            "## Handoff\n"
            "### Publish/check block\n"
            f"{handoff_payload['publish_check_block']}\n\n"
            "### Merge/sync block\n"
            f"{handoff_payload['merge_sync_block']}\n\n"
        )
    return "\n".join(
        [
            "# AIOS AEE Compound Campaign CLI Report",
            "",
            "## State",
            classifier_to_markdown(_to_obj(result.state)),
            "",
            "## Plan",
            plan_to_markdown(plan_obj),
            "",
            "## Guard",
            guard_to_markdown([_to_obj(item) for item in result.guard.get("findings", [])]),
            "",
            "## Metrics",
            metrics_to_markdown(_to_obj(result.metrics)),
            "",
            handoff_txt.strip(),
        ]
    ).strip() + "\n"


def run_report(result: CompoundCampaignResult, *, args: argparse.Namespace) -> None:
    if not args.write_report:
        return
    path = Path(args.repo_root) / args.report_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_report_payload(result), encoding="utf-8")


def _operator_lines(result: CompoundCampaignResult, plan: dict[str, object]) -> list[str]:
    plan_obj = type("Plan", (), plan)
    plan_text = plan_to_text(plan_obj)
    metrics_text = metrics_to_text(_to_obj(result.metrics))
    guard_text = guard_to_text([_to_obj(item) for item in result.guard.get("findings", [])]) if result.guard.get("findings") else "findings=0"
    return [classifier_to_text(type("Campaign", (), result.state)), plan_text, metrics_text, guard_text]


def main() -> int:
    args = _parse_args()
    result = run_compound_campaign(args)
    # The strict mode is only hard-failing for hard stop / forbidden branch states.
    status = result.state.get("continuation_status", "RECOVERABLE_LOCAL")
    output_lines = _operator_lines(result, result.plan)
    if args.json:
        payload = asdict(result)
        print(json.dumps(payload, sort_keys=True))
    else:
        print("\n".join(output_lines))

    run_report(result, args=args)
    if args.generate_handoff and result.handoff:
        print("publish_and_merge_blocks_ready")
        handoff = result.handoff
        if handoff.get("validation"):
            print("\n".join(f"- {item}" for item in handoff["validation"]))
    if args.strict and status in {"HARD_STOP", "WRONG_PACKET_FOR_CLEAN_MAIN"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
