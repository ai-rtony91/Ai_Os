from __future__ import annotations

"""Execution planner for AEE compound campaign validation flows."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List

from .aios_aee_campaign_state_classifier_v1 import TARGET_BRANCH

COMMAND_SAFETY_MATRIX = {
    "SAFE_LOCAL": "safe local execution by Codex",
    "RETRY_ONCE_IF_1312": "retry once on CreateProcessAsUserW 1312",
    "DEFERRED_OWNER_IF_1312": "defer to owner PowerShell after 1312",
    "PROTECTED_OWNER_ONLY": "owner-only protected command",
    "FORBIDDEN": "command not allowed",
}

KNOWN_COMMANDS = {
    "status_check": "git status --short --branch",
    "safe_python_compile": "python -m py_compile automation/governance/aios_aee_campaign_state_classifier_v1.py automation/governance/aios_aee_validator_execution_planner_v1.py automation/governance/aios_aee_owner_handoff_builder_v1.py automation/governance/aios_aee_static_ci_guard_v1.py automation/governance/aios_aee_campaign_metrics_v1.py scripts/governance/run_aios_aee_compound_campaign_v1.py",
    "targeted_pytest": "python -m pytest tests/governance/test_aios_aee_compound_campaign_v1.py -q",
    "strict_cli": "python scripts/governance/run_aios_aee_compound_campaign_v1.py --strict --branch {branch} --dirty-file automation/governance/aios_aee_campaign_state_classifier_v1.py --dirty-file automation/governance/aios_aee_governance_validator_v1.py",
    "report_write": "python scripts/governance/run_aios_aee_compound_campaign_v1.py --write-report --report-path {report_path} --strict --branch {branch}",
    "git_diff_check": "git diff --check",
    "owner_deferred_validation": "python scripts/governance/run_aios_aee_compound_campaign_v1.py --strict --simulate-1312 --simulate-targeted-tests-passed --branch {branch}",
}


@dataclass(frozen=True)
class ValidationPlanStep:
    name: str
    command: str
    command_family: str
    risk: str
    retryable: bool
    deferred_to_owner: bool
    reason: str


@dataclass(frozen=True)
class ValidationPlanResult:
    branch: str
    plan: list[ValidationPlanStep]
    attempted: list[str]
    retry_attempts: list[str]
    deferred: list[str]
    blocked: list[str]
    repo_root: str
    report_path: str


def classify_command(command: str) -> str:
    command_lower = command.lower()
    if any(token in command_lower for token in ("git add .", "git add -A", "git add -a")):
        return "FORBIDDEN"
    if any(token in command_lower for token in ("git commit", "git push", "gh pr create", "gh pr merge", "git switch", "git pull --ff-only")):
        return "PROTECTED_OWNER_ONLY"
    if "python -m py_compile" in command_lower:
        return "SAFE_LOCAL"
    if "python -m pytest" in command_lower:
        return "SAFE_LOCAL"
    if "git status --short --branch" in command_lower or "git diff --check" in command_lower:
        return "SAFE_LOCAL"
    if "strict" in command_lower and "run_aios_aee_compound_campaign_v1.py" in command_lower:
        return "SAFE_LOCAL"
    if "simulate-1312" in command_lower:
        return "DEFERRED_OWNER_IF_1312"
    return "FORBIDDEN"


def _normalise(items: Iterable[str] | None) -> list[str]:
    return [str(item).strip() for item in (items or []) if str(item).strip()]


def _build_step(name: str, command: str, command_family: str, *, deferred: bool = False) -> ValidationPlanStep:
    risk = classify_command(command)
    if risk == "FORBIDDEN" and command_family == "owner_deferred_validation":
        risk = "DEFERRED_OWNER_IF_1312"
    return ValidationPlanStep(
        name=name,
        command=command,
        command_family=command_family,
        risk=risk,
        retryable=risk in {"RETRY_ONCE_IF_1312", "SAFE_LOCAL"},
        deferred_to_owner=deferred,
        reason=COMMAND_SAFETY_MATRIX.get(risk, "unknown"),
    )


def build_validation_plan(
    repo_root: str | Path,
    *,
    branch: str = TARGET_BRANCH,
    dirty_files: Iterable[str] | None = None,  # noqa: ARG001
    staged_files: Iterable[str] | None = None,  # noqa: ARG001
    strict_cli: bool = False,
    include_owner_deferred_block: bool = True,
    simulate_1312: bool = False,
    report_path: str = "Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_REPORT.md",
    local_work_complete: bool = False,  # noqa: ARG001
    write_report: bool = False,
) -> ValidationPlanResult:
    _ = _normalise(dirty_files)
    _ = _normalise(staged_files)

    status_check = _build_step("status_check", KNOWN_COMMANDS["status_check"], "status_check")
    compile_step = _build_step("safe_python_compile", KNOWN_COMMANDS["safe_python_compile"], "safe_python_compile")
    test_step = _build_step("targeted_pytest", KNOWN_COMMANDS["targeted_pytest"], "targeted_pytest")
    strict_command = KNOWN_COMMANDS["strict_cli"].format(branch=branch)
    strict_step = _build_step("strict_cli", strict_command, "strict_cli")
    diff_step = _build_step("git_diff_check", KNOWN_COMMANDS["git_diff_check"], "git_diff_check")

    plan: list[ValidationPlanStep] = [status_check, compile_step, test_step, strict_step, diff_step]
    if write_report:
        report_command = KNOWN_COMMANDS["report_write"].format(branch=branch, report_path=report_path)
        plan.append(_build_step("report_write", report_command, "report_write"))
    if include_owner_deferred_block:
        owner_command = KNOWN_COMMANDS["owner_deferred_validation"].format(branch=branch)
        plan.append(_build_step("owner_deferred_validation", owner_command, "owner_deferred_validation", deferred=True))

    if strict_cli and not write_report:
        attempted = ["status_check", "safe_python_compile", "targeted_pytest", "strict_cli", "git_diff_check"]
    elif strict_cli:
        attempted = ["status_check", "safe_python_compile", "targeted_pytest", "strict_cli", "git_diff_check", "report_write"]
    else:
        attempted = [step.name for step in plan]

    if simulate_1312:
        plan = apply_1312_result(plan, simulate_1312=True, targeted_tests_passed=False)

    blocked = [step.name for step in plan if step.risk == "FORBIDDEN"]
    return ValidationPlanResult(
        branch=branch,
        plan=plan,
        attempted=attempted,
        retry_attempts=[
            step.name
            for step in plan
            if step.retryable and step.risk != "FORBIDDEN"
        ],
        deferred=[step.name for step in plan if step.deferred_to_owner],
        blocked=blocked,
        repo_root=str(Path(repo_root)),
        report_path=report_path,
    )


def apply_1312_result(
    plan: list[ValidationPlanStep] | ValidationPlanResult,
    *,
    command_name: str | None = None,
    simulate_1312: bool = True,
    targeted_tests_passed: bool = False,
    all_remaining_work_blocked: bool = False,
) -> list[ValidationPlanStep]:
    source = plan.plan if isinstance(plan, ValidationPlanResult) else plan
    updated: list[ValidationPlanStep] = []

    for step in source:
        if command_name and step.command != command_name:
            updated.append(step)
            continue

        if step.command_family == "strict_cli":
            if all_remaining_work_blocked:
                updated.append(
                    ValidationPlanStep(
                        name=step.name,
                        command=step.command,
                        command_family=step.command_family,
                        risk="DEFERRED_OWNER_IF_1312",
                        retryable=False,
                        deferred_to_owner=True,
                        reason=COMMAND_SAFETY_MATRIX["DEFERRED_OWNER_IF_1312"],
                    )
                )
                continue
            if targeted_tests_passed:
                updated.append(
                    ValidationPlanStep(
                        name=step.name,
                        command=step.command,
                        command_family=step.command_family,
                        risk="DEFERRED_OWNER_IF_1312",
                        retryable=False,
                        deferred_to_owner=True,
                        reason=COMMAND_SAFETY_MATRIX["DEFERRED_OWNER_IF_1312"],
                    )
                )
                continue
            updated.append(
                ValidationPlanStep(
                    name=step.name,
                    command=step.command,
                    command_family=step.command_family,
                    risk="RETRY_ONCE_IF_1312",
                    retryable=True,
                    deferred_to_owner=False,
                    reason=COMMAND_SAFETY_MATRIX["RETRY_ONCE_IF_1312"],
                )
            )
            continue

        if step.command_family in {"safe_python_compile", "targeted_pytest", "status_check", "git_diff_check", "report_write"}:
            updated.append(
                ValidationPlanStep(
                    name=step.name,
                    command=step.command,
                    command_family=step.command_family,
                    risk="RETRY_ONCE_IF_1312",
                    retryable=True,
                    deferred_to_owner=False,
                    reason=COMMAND_SAFETY_MATRIX["RETRY_ONCE_IF_1312"],
                )
            )
            continue

        updated.append(step)

    return updated


def plan_owner_deferred_commands(
    *,
    branch: str = TARGET_BRANCH,
    status_path: str = "Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_REPORT.md",
    report_path: str = "Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_REPORT.md",
) -> list[str]:
    del status_path
    return [
        "git status --short --branch",
        "git diff --check",
        f"gh pr checks --watch",
        "git commit -m \"feat(aios): add compound AEE longrun governance infrastructure\"",
        f"git push -u origin {branch}",
        f"gh pr create --base main --head {branch} --title \"feat(aios): add compound AEE longrun governance infrastructure\" --body-file {report_path}",
        "gh pr merge --squash",
        "git switch main",
        "git pull --ff-only origin main",
    ]


def result_to_markdown(result: ValidationPlanResult) -> str:
    rows = [
        "# AIOS AEE Compound Campaign Validation Planner",
        "",
        f"- branch: {result.branch}",
        f"- repo_root: {result.repo_root}",
        f"- report_path: {result.report_path}",
        f"- attempted: {', '.join(result.attempted)}",
        "",
        "|name|command_family|command|risk|retryable|deferred|",
        "|---|---|---|---|---|---|",
    ]
    for item in result.plan:
        safe_command = item.command.replace("|", "\\|")
        rows.append(
            f"|{item.name}|{item.command_family}|{safe_command}|{item.risk}|{str(item.retryable).lower()}|{str(item.deferred_to_owner).lower()}|"
        )
    if result.deferred:
        rows.append("")
        rows.append("deferred: " + ", ".join(result.deferred))
    return "\n".join(rows) + "\n"


def result_to_jsonable_dict(result: ValidationPlanResult) -> dict[str, object]:
    payload = asdict(result)
    payload["plan"] = [asdict(item) for item in result.plan]
    return payload


def result_to_operator_text(result: ValidationPlanResult) -> str:
    return (
        f"branch={result.branch} commands={len(result.plan)} "
        f"blocked={len(result.blocked)} deferred={len(result.deferred)}"
    )
