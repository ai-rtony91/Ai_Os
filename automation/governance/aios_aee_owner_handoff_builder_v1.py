from __future__ import annotations

"""Owner handoff helpers for compound campaign publishing and merge."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
import re

from .aios_aee_campaign_state_classifier_v1 import ALLOWED_WRITE_PATHS, FORBIDDEN_PATH_PREFIXES

COMMIT_MESSAGE = "feat(aios): add compound AEE longrun governance infrastructure"
PR_TITLE = "feat(aios): add compound AEE longrun governance infrastructure"
PR_BODY_PREFIX = "# AIOS AEE Compound Spark Longrun Campaign V1"
REPORT_PATH_DEFAULT = "Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_REPORT.md"
DEFAULT_BRANCH = "lane/aios-aee-governance-validator-v1"

PLACEHOLDER_PATTERN = re.compile(
    r"@filename|\{[^}]+\}|TODO|TBD|path/to/",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class HandoffBuildResult:
    publish_check_block: str
    merge_sync_block: str
    validation: list[str]
    changed_files: list[str]
    branch: str
    report_path: str


def _normalise(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _under(candidate: str, prefix: str) -> bool:
    candidate_norm = _normalise(candidate).lower().rstrip("/")
    prefix_norm = _normalise(prefix).lower().rstrip("/")
    return candidate_norm == prefix_norm or candidate_norm.startswith(prefix_norm + "/")


def validate_explicit_file_list(
    file_list: Iterable[str] | None,
    *,
    allowed_prefixes: list[str] | None = None,
) -> list[str]:
    provided = [_normalise(path) for path in (file_list or []) if str(path).strip()]
    if not provided:
        return ["explicit file list is required"]

    allowed = allowed_prefixes or ALLOWED_WRITE_PATHS
    issues: list[str] = []
    for item in provided:
        if PLACEHOLDER_PATTERN.search(item):
            issues.append(f"placeholder token in explicit file list: {item}")
            continue
        if any(_under(item, prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
            issues.append(f"forbidden path in explicit file list: {item}")
            continue
        if not any(_under(item, prefix) for prefix in allowed):
            issues.append(f"explicit file outside allowed paths: {item}")
    return issues


def reject_placeholder_commands(block_text: str) -> list[str]:
    found = PLACEHOLDER_PATTERN.findall(block_text)
    if not found:
        return []
    return [f"placeholder token detected in command block: {token}" for token in set(found)]


def reject_broad_git_add(block_text: str) -> list[str]:
    lowered = block_text.lower()
    issues: list[str] = []
    if "git add ." in lowered.replace("  ", " "):
        issues.append("git add . is not allowed")
    if re.search(r"\bgit\s+add\s+-a\b", lowered) or re.search(r"\bgit\s+add\s+-A\b", lowered):
        issues.append("git add -A is not allowed")
    return issues


def reject_broad_git_add_in_commands(commands: Iterable[str]) -> list[str]:
    issues: list[str] = []
    for command in commands:
        issues.extend(reject_broad_git_add(command))
    return issues


def build_publish_check_block(
    changed_files: Iterable[str],
    *,
    branch: str = DEFAULT_BRANCH,
    repo_root: str = "C:\\Dev\\Ai.Os",
    report_path: str = REPORT_PATH_DEFAULT,
) -> str:
    files = [_normalise(path) for path in changed_files if str(path).strip()]
    issues = validate_explicit_file_list(files)
    if issues:
        raise ValueError("; ".join(issues))

    add_cmd = "git add -- " + " ".join(f'"{path}"' for path in sorted(set(files)))
    lines = [
        "# Block 1 publish/check only",
        f"cd {repo_root}",
        "git status --short --branch",
        "git diff --check",
        add_cmd,
        "git diff --cached --check",
        f'git commit -m "{COMMIT_MESSAGE}"',
        f"git push -u origin {branch}",
        f'gh pr create --base main --head {branch} --title "{PR_TITLE}" --body-file {report_path}',
        "gh pr checks --watch",
        "",
    ]
    del branch
    return "\n".join(lines) + "\n"


def build_merge_sync_block(
    *,
    merge_command: str = "gh pr merge --squash",
    branch: str = DEFAULT_BRANCH,
    repo_root: str = "C:\\Dev\\Ai.Os",
) -> str:
    del branch
    lines = [
        "# Block 2 merge/sync only",
        f"cd {repo_root}",
        merge_command,
        "git switch main",
        "git pull --ff-only origin main",
        "git status --short --branch",
        "",
    ]
    return "\n".join(lines) + "\n"


def validate_handoff_blocks(
    publish_check_block: str,
    merge_sync_block: str,
) -> list[str]:
    issues: list[str] = []
    issues.extend(reject_placeholder_commands(publish_check_block))
    issues.extend(reject_placeholder_commands(merge_sync_block))
    issues.extend(reject_broad_git_add_in_commands(publish_check_block.splitlines()))
    issues.extend(reject_broad_git_add_in_commands(merge_sync_block.splitlines()))

    pub_lines = [line.lower().strip() for line in publish_check_block.splitlines()]
    merge_lines = [line.lower().strip() for line in merge_sync_block.splitlines()]

    if "gh pr checks --watch" not in pub_lines:
        issues.append("check-watch must be in Block 1")
    if "gh pr merge --squash" in pub_lines:
        issues.append("merge command must not be in Block 1")
    if "git switch main" in pub_lines or "git pull --ff-only origin main" in pub_lines:
        issues.append("merge/sync command must not be in Block 1")
    if any(line.startswith("git add ") for line in merge_lines):
        issues.append("publish commands must not be in Block 2")
    if "git commit" in " ".join(merge_lines):
        issues.append("commit must not be in Block 2")
    if "gh pr checks --watch" in " ".join(merge_lines):
        issues.append("check-watch must not be in Block 2")
    if "git switch main" not in merge_lines or "git pull --ff-only origin main" not in merge_lines:
        issues.append("merge/sync commands missing from Block 2")
    if not any("gh pr merge" in line for line in merge_lines):
        issues.append("block 2 must include gh pr merge --squash")
    return issues


def build_handoff(
    *,
    changed_files: Iterable[str],
    report_path: str = REPORT_PATH_DEFAULT,
    branch: str = DEFAULT_BRANCH,
    repo_root: str = "C:\\Dev\\Ai.Os",
) -> HandoffBuildResult:
    publish = build_publish_check_block(
        changed_files=changed_files,
        branch=branch,
        repo_root=repo_root,
        report_path=report_path,
    )
    merge = build_merge_sync_block(branch=branch, repo_root=repo_root)
    issues = validate_handoff_blocks(publish, merge)
    return HandoffBuildResult(
        publish_check_block=publish,
        merge_sync_block=merge,
        validation=issues,
        changed_files=[_normalise(path) for path in changed_files],
        branch=branch,
        report_path=report_path,
    )


def result_to_markdown(result: HandoffBuildResult) -> str:
    lines = [
        "# AIOS AEE Compound Campaign Owner Handoff",
        "",
        f"branch: {result.branch}",
        f"report_path: {result.report_path}",
        "",
        "## Block 1 publish/check",
        result.publish_check_block.rstrip(),
        "",
        "## Block 2 merge/sync",
        result.merge_sync_block.rstrip(),
        "",
        "## Validation",
    ]
    if result.validation:
        lines.extend(f"- {issue}" for issue in result.validation)
    else:
        lines.append("- no issues")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: HandoffBuildResult) -> dict[str, object]:
    return asdict(result)
