"""Top-level orchestration for paper-trading completion sweep."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from automation.trading.runner.paper_replay_runner import PaperSignalReplayResult, run_paper_replay, build_replay_result
from automation.trading.safety.paper_only_validator import validate_paper_payload


class PaperSafetyValidationError(ValueError):
    """Raised when replay input/output breaks paper safety constraints."""


class PaperSafetyValidator:
    """Validate paper-only packets used by the completion sweep."""

    def validate_payload(self, payload: dict[str, Any]) -> list[str]:
        return validate_paper_payload(payload)


def run_paper_completion_sweep(
    *,
    repo_root: Path | str | None = None,
    fixture_path: Path | str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Execute the paper completion sweep with deterministic paper fixtures.

    When dry_run is True, outputs are not written.
    """
    target_repo_root = Path(repo_root or Path(__file__).resolve().parents[2])
    fixture = Path(fixture_path or target_repo_root / "automation/trading/fixtures/paper_signal_fixture.json")
    if not fixture.exists():
        raise FileNotFoundError(f"Paper fixture missing: {fixture}")

    results = run_paper_replay(fixture_path=fixture, repo_root=target_repo_root, dry_run=dry_run)
    validator = PaperSafetyValidator()
    if not results["paper_only"]:
        raise PaperSafetyValidationError("Sweep output is not paper-only.")
    blocked = []
    for entry in results["ledger"]:
        blocked.extend([item for item in validator.validate_payload(entry) if item not in blocked])
    if blocked:
        raise PaperSafetyValidationError(f"Paper safety blockers: {blocked}")
    return {
        "status": "PASS" if results["execution_quality"]["execution_quality_score"] > 0 else "FAIL",
        "run": results,
        "ledger_runs": build_replay_result(results),
    }


@dataclass(frozen=True)
class OperatorPaperStatusReport:
    run_id: str
    status: str
    blocked_reasons: list[str]
    quality_score: float

