"""Approved validator planning and orchestration for Operator Relief autonomy spine v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .full_auto_policy import FullAutoTask
from .validator_router import run_validator, select_validator


@dataclass(frozen=True)
class ValidatorPlanItem:
    path: str
    validator: str
    supported: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidatorOrchestrationResult:
    status: str
    plan: list[ValidatorPlanItem]
    results: list[dict[str, Any]]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "plan": [item.to_dict() for item in self.plan],
            "results": self.results,
            "executable": False,
        }


def build_validator_plan(task: FullAutoTask) -> ValidatorOrchestrationResult:
    plan = [
        ValidatorPlanItem(
            path=target,
            validator=select_validator(target),
            supported=select_validator(target) != "unsupported_extension",
        )
        for target in task.validator_targets
    ]
    status = "PLANNED" if all(item.supported for item in plan) else "UNSUPPORTED_VALIDATOR"
    return ValidatorOrchestrationResult(status=status, plan=plan, results=[])


def run_validator_plan(task: FullAutoTask, repo_root: Path | None = None) -> ValidatorOrchestrationResult:
    planned = build_validator_plan(task)
    if planned.status != "PLANNED":
        return planned

    root = repo_root or Path.cwd()
    results = [run_validator(root / item.path).to_dict() for item in planned.plan]
    status = "PASSED" if all(result["success"] for result in results) else "FAILED"
    return ValidatorOrchestrationResult(status=status, plan=planned.plan, results=results)
