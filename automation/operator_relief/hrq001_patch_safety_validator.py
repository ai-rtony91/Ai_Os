"""Validate the DRY_RUN-only HRQ-001 draft patch."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_hrq001_patch_safety_validator_v1"
PATCH_ROOT = Path("Reports/operator_relief/hrq001_apply_draft_patch")
DIFF_PATH = PATCH_ROOT / "hrq001_apply_draft_patch.diff"
PATCH_JSON_PATH = PATCH_ROOT / "hrq001_apply_draft_patch.json"
OUTPUT_PATH = PATCH_ROOT / "hrq001_patch_safety_validation.json"
CANONICAL_TARGET = "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md"
DUPLICATE_SOURCE = "docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md"
ALLOWED_REQUIRED_TEXT = (
    "Legacy worker branch examples for human review",
    "worker/work-intelligence/phase-21-branch-rules",
    "worker/operator-orchestration/phase-22-file-ownership",
    "worker/dashboard-ui/phase-15-centerpiece-review",
    "Worker reports should include planned files and validation commands.",
    "The integration lane checks those reports before any merge or APPLY review.",
)
DISALLOWED_SCOPE_TERMS = (
    "HRQ-002",
    "HRQ-003",
    "PARALLEL_CODEX_WORKFLOW",
    "APPLY_ROUTING_CHAIN",
    "docs/governance/",
    "docs/security/",
    "docs/AI_OS/governance/",
    "docs/AI_OS/security/",
)


@dataclass(frozen=True)
class HRQ001PatchSafetyValidationResult:
    report_type: str
    generated_at: str
    executable: bool
    source_diff: str
    source_patch_json: str
    patch_validation_status: str
    accepted_count: int
    rejected_count: int
    rejection_reasons: list[str]
    canonical_target: str
    duplicate_source: str
    apply_ready_paths: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _diff_headers(diff_text: str) -> list[str]:
    return [line.strip() for line in diff_text.splitlines() if line.startswith(("--- ", "+++ "))]


def _added_lines(diff_text: str) -> list[str]:
    lines: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++ "):
            lines.append(line[1:])
    return lines


def _removed_lines(diff_text: str) -> list[str]:
    lines: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("-") and not line.startswith("--- "):
            lines.append(line[1:])
    return lines


def _validate_patch(diff_text: str, patch_json: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not diff_text.strip():
        errors.append("draft patch diff is missing or empty")
    if not patch_json:
        errors.append("draft patch json is missing or empty")
    headers = _diff_headers(diff_text)
    expected_from = f"--- {CANONICAL_TARGET}"
    expected_to = f"+++ {CANONICAL_TARGET} (draft only)"
    if expected_from not in headers or expected_to not in headers:
        errors.append("patch must target only docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md")
    if DUPLICATE_SOURCE in diff_text:
        errors.append("patch must not modify duplicate source file")
    if "/dev/null" in diff_text or _removed_lines(diff_text):
        errors.append("patch must not delete files or remove lines")
    added_text = "\n".join(_added_lines(diff_text))
    for required in ALLOWED_REQUIRED_TEXT:
        if required not in added_text:
            errors.append(f"required HRQ-001 insertion text missing: {required}")
    for term in DISALLOWED_SCOPE_TERMS:
        if term in diff_text:
            errors.append(f"disallowed scope term found: {term}")
    if patch_json.get("canonical_target") != CANONICAL_TARGET:
        errors.append("patch json canonical_target mismatch")
    if patch_json.get("duplicate_source") != DUPLICATE_SOURCE:
        errors.append("patch json duplicate_source mismatch")
    if patch_json.get("executable") is True:
        errors.append("patch json executable=true is rejected")
    if patch_json.get("apply_ready_paths") not in ([], None):
        errors.append("apply_ready_paths must be empty")
    safety = patch_json.get("safety")
    if not isinstance(safety, dict):
        errors.append("patch safety metadata is missing")
    else:
        expected_false = (
            "workflow_docs_modified",
            "files_deleted",
            "canonicalization_performed",
            "executable_apply_packet_generated",
            "protected_docs_modified",
            "hrq002_touched",
            "hrq003_touched",
        )
        for field in expected_false:
            if safety.get(field) is not False:
                errors.append(f"safety.{field} must be false")
    sections = patch_json.get("sections_included")
    if not isinstance(sections, list) or [item.get("source_section") for item in sections if isinstance(item, dict)] != ["Branch Naming", "Report Rules"]:
        errors.append("sections_included must be exactly Branch Naming and Report Rules")
    if "rollback" not in str(patch_json.get("recommended_next_action", "")).lower() and "approve exact text" not in str(patch_json.get("recommended_next_action", "")).lower():
        errors.append("rollback or human approval instruction is missing")
    return errors


def build_validation(repo_root: Path) -> HRQ001PatchSafetyValidationResult:
    root = repo_root.resolve()
    diff_text = _load_text(root / DIFF_PATH)
    patch_json = _load_json(root / PATCH_JSON_PATH)
    rejection_reasons = _validate_patch(diff_text, patch_json)
    accepted = 0 if rejection_reasons else 1
    rejected = 1 if rejection_reasons else 0
    status = "ACCEPTED" if accepted else "REJECTED"
    return HRQ001PatchSafetyValidationResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_diff=_normalize_path(DIFF_PATH),
        source_patch_json=_normalize_path(PATCH_JSON_PATH),
        patch_validation_status=status,
        accepted_count=accepted,
        rejected_count=rejected,
        rejection_reasons=rejection_reasons,
        canonical_target=CANONICAL_TARGET,
        duplicate_source=DUPLICATE_SOURCE,
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "validation_only": True,
            "workflow_docs_modified": False,
            "files_deleted": False,
            "canonicalization_performed": False,
            "executable_apply_packet_generated": False,
            "protected_docs_modified": False,
            "hrq002_touched": False,
            "hrq003_touched": False,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action=(
            "Patch may proceed only to human review; this validator does not authorize APPLY."
            if accepted
            else "Fix rejected draft patch evidence before any human review or APPLY consideration."
        ),
    )


def _output_path(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_PATH).resolve()
    allowed_root = (root / PATCH_ROOT).resolve()
    if not (output.parent == allowed_root and allowed_root in output.parents):
        raise ValueError("HRQ-001 patch safety validation must be written under Reports/operator_relief/hrq001_apply_draft_patch/.")
    return output


def write_validation(result: HRQ001PatchSafetyValidationResult, repo_root: Path) -> Path:
    path = _output_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate DRY_RUN-only HRQ-001 draft patch.")
    parser.add_argument("--write-report", action="store_true", help="Write validation report.")
    args = parser.parse_args(argv)
    result = build_validation(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_report:
        payload["written_file"] = _normalize_path(write_validation(result, Path.cwd()))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
