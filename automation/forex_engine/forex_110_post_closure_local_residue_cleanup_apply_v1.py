"""Apply the post-closure local residue cleanup for Forex 110.

This module only removes explicitly allowed local/generated artifacts and does
not perform broker/live/demo/order/money/credential/file-system-unsafe actions.
"""

from __future__ import annotations

import subprocess
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

PACKET_ID = "PKT-FOREX-110-POST-CLOSURE-LOCAL-RESIDUE-CLEANUP-APPLY-V1"
STATE_NAME = "AIOS_FOREX_110_POST_CLOSURE_LOCAL_RESIDUE_CLEANUP_APPLY_V1_STATE.json"
REPORT_NAME = "AIOS_FOREX_110_POST_CLOSURE_LOCAL_RESIDUE_CLEANUP_APPLY_V1_REPORT.md"

PLAN_STATE_NAME = "AIOS_FOREX_110_POST_CLOSURE_LOCAL_RESIDUE_CLEANUP_PLAN_V1_STATE.json"
PLAN_REPORT_NAME = "AIOS_FOREX_110_POST_CLOSURE_LOCAL_RESIDUE_CLEANUP_PLAN_V1_REPORT.md"

DEFAULT_REPORT_ROOT = Path("Reports") / "forex_delivery"

SAFE_DELETE_CATEGORIES = [
    "apps/dashboard/node_modules/",
    "Python __pycache__ directories",
    "Python .pyc files inside __pycache__",
    "apps/dashboard/dist/",
    ".pytest_cache/",
]

SAFE_CATEGORY_ORDER = {
    "Python __pycache__ directories": 0,
    "Python .pyc files inside __pycache__": 1,
    "apps/dashboard/node_modules/": 2,
    "apps/dashboard/dist/": 3,
    ".pytest_cache/": 4,
}

ALLOWED_WRITE_FILES = {
    "automation/forex_engine/forex_110_post_closure_local_residue_cleanup_apply_v1.py",
    "scripts/forex_delivery/run_forex_110_post_closure_local_residue_cleanup_apply_v1.py",
    "tests/forex_engine/test_forex_110_post_closure_local_residue_cleanup_apply_v1.py",
    "Reports/forex_delivery/AIOS_FOREX_110_POST_CLOSURE_LOCAL_RESIDUE_CLEANUP_APPLY_V1_STATE.json",
    "Reports/forex_delivery/AIOS_FOREX_110_POST_CLOSURE_LOCAL_RESIDUE_CLEANUP_APPLY_V1_REPORT.md",
}

PROTECTED_DO_NOT_TOUCH = (
    "AGENTS.md",
    "README.md",
    "RISK_POLICY.md",
    "WHITEPAPER.md",
    ".env",
    ".env.*",
    "credentials",
    "secrets",
    "Bitwarden",
    "Vaultwarden",
    ".local_backlog/",
    ".local_hold/",
    "Reports/",
    "Reports/forex_delivery/",
    "Reports/forex_delivery/AIOS_FOREX_110_*",
    "Reports/forex_delivery/AIOS_FOREX_110_COMPLETION_INDEX_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FINAL_PROTECTED_BOUNDARY_HANDOFF_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_POST_110_NEXT_PROJECT_BLOCKER_BITWARDEN_V1.md",
    "archive/",
    "docs/",
    "automation/",
    "tests/",
    "services/",
)

ROOT_RUNTIME_JSON_FILES = (
    "approval.json",
    "completion_report.json",
    "validation_result.json",
    "task_log.json",
)

FOREX_110_PROOF_FILES = (
    "Reports/forex_delivery/AIOS_FOREX_110_COMPLETION_INDEX_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FINAL_PROTECTED_BOUNDARY_HANDOFF_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_POST_110_NEXT_PROJECT_BLOCKER_BITWARDEN_V1.md",
)


def run_forex_110_post_closure_local_residue_cleanup_apply_v1(
    report_root: str | Path = DEFAULT_REPORT_ROOT,
    *,
    repo_root: str | Path | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Execute the post-closure cleanup and return a JSON-serializable report."""

    root = _resolve_repo_root(Path(report_root), repo_root)
    report_root = Path(report_root)
    precheck = _precheck(root, report_root)
    git_before = _git_counts(root)
    manifest_before = _build_manifest(root)

    dry_run_manifest = {
        "safe_targets": manifest_before["safe_targets"],
        "target_count": manifest_before["target_count"],
        "category_counts": manifest_before["category_counts"],
        "forbidden_targets": manifest_before["forbidden_targets"],
    }

    deleted_targets: list[str] = []
    skipped_targets: list[dict[str, str]] = []
    deleted_count = 0
    deleted_bytes_estimate = 0

    if dry_run:
        cleanup_apply_status = "DRY_RUN_COMPLETE"
        skipped_targets.extend(_skip_targets(manifest_before["safe_targets"], "dry_run"))
        manifest_after = manifest_before
        after_counts = manifest_before
        non_ignored_untracked_count_after = len(git_before["non_ignored_untracked"])
        ignored_local_generated_count_after = len(git_before["ignored"])
    elif not precheck["ok"]:
        cleanup_apply_status = "APPLY_BLOCKED"
        blocked_reason = str(precheck.get("reason", "precheck_blocked"))
        skipped_targets.extend(_skip_targets(manifest_before["safe_targets"], blocked_reason))
        manifest_after = manifest_before
        non_ignored_untracked_count_after = len(git_before["non_ignored_untracked"])
        ignored_local_generated_count_after = len(git_before["ignored"])
    else:
        deleted_targets, skipped_targets, deleted_count, deleted_bytes_estimate = _apply_targets(root, manifest_before["safe_targets"])
        cleanup_apply_status = "APPLY_COMPLETED" if deleted_count else "APPLY_NO_TARGETS"
        git_after = _git_counts(root)
        non_ignored_untracked_count_after = len(git_after["non_ignored_untracked"])
        ignored_local_generated_count_after = len(git_after["ignored"])
        manifest_after = _build_manifest(root)

    result = {
        "packet_id": PACKET_ID,
        "cleanup_apply_status": cleanup_apply_status,
        "dry_run_manifest": dry_run_manifest,
        "deleted_targets": deleted_targets,
        "skipped_targets": skipped_targets,
        "forbidden_targets_detected": sorted(manifest_before["forbidden_targets"], key=lambda item: item["path"]),
        "deletion_performed": (not dry_run and precheck["ok"] and deleted_count > 0),
        "git_clean_performed": False,
        "gitignore_modified": False,
        "safe_delete_categories": SAFE_DELETE_CATEGORIES,
        "protected_do_not_touch": list(PROTECTED_DO_NOT_TOUCH),
        "before_counts": {
            "safe_target_count": manifest_before["target_count"],
            "target_count": manifest_before["target_count"],
            "category_counts": manifest_before["category_counts"],
            "forbidden_count": len(manifest_before["forbidden_targets"]),
        },
        "after_counts": {
            "safe_target_count": manifest_after["target_count"],
            "target_count": manifest_after["target_count"],
            "category_counts": manifest_after["category_counts"],
            "forbidden_count": len(manifest_after["forbidden_targets"]),
        },
        "deleted_count": deleted_count,
        "deleted_bytes_estimate": deleted_bytes_estimate,
        "non_ignored_untracked_count_before": len(git_before["non_ignored_untracked"]),
        "non_ignored_untracked_count_after": non_ignored_untracked_count_after,
        "ignored_local_generated_count_before": len(git_before["ignored"]),
        "ignored_local_generated_count_after": ignored_local_generated_count_after,
        "forex_110_closure_landed": _is_forex_110_closure_landed(root),
        "broker_api_used": False,
        "credentials_used": False,
        "env_read": False,
        "account_identifiers_used": False,
        "order_execution": False,
        "demo_authorized": False,
        "live_authorized": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "background_loop_started": False,
        "bitwarden_started": False,
        "next_safe_action": _next_safe_action(cleanup_apply_status),
        "ATTACK_TO_FINISH": _attack_to_finish(
            cleanup_apply_status=cleanup_apply_status,
            precheck_ok=precheck["ok"],
            branch=precheck.get("branch", "UNKNOWN"),
            precheck_reason=precheck.get("reason"),
        ),
    }
    return result


def _resolve_repo_root(report_root: Path, repo_root: str | Path | None) -> Path:
    if repo_root is not None:
        return Path(repo_root).resolve()

    resolved_report_root = report_root if report_root.is_absolute() else Path.cwd().resolve() / report_root
    if resolved_report_root.name == "forex_delivery" and resolved_report_root.parent.name == "Reports":
        return resolved_report_root.parent.parent
    return Path.cwd().resolve()


def _precheck(repo_root: Path, report_root: Path) -> dict[str, Any]:
    status = _git_status(repo_root)
    if status["branch"] != "main":
        return {
            "ok": False,
            "reason": f"branch_not_main:{status['branch']}",
            "branch": status["branch"],
            "status": status,
        }

    if status["tracked_dirty_lines"]:
        return {
            "ok": False,
            "reason": "tracked_files_dirty",
            "branch": status["branch"],
            "status": status,
        }

    non_ignored_untracked = _run_git_lines(repo_root, ["ls-files", "--others", "--exclude-standard"])
    allowed = {_normalize_rel(path) for path in ALLOWED_WRITE_FILES}
    for untracked in non_ignored_untracked:
        normalized = _normalize_rel(untracked)
        if normalized and normalized not in allowed:
            return {
                "ok": False,
                "reason": f"disallowed_untracked:{normalized}",
                "branch": status["branch"],
                "status": status,
                "disallowed_untracked": normalized,
            }

    plan_state = report_root / PLAN_STATE_NAME
    plan_report = report_root / PLAN_REPORT_NAME
    if not plan_state.is_file() or not plan_report.is_file():
        return {
            "ok": False,
            "reason": "plan_not_found",
            "branch": status["branch"],
            "status": status,
        }

    return {
        "ok": True,
        "reason": None,
        "branch": status["branch"],
        "status": status,
    }


def _build_manifest(repo_root: Path) -> dict[str, Any]:
    tracked_files = set(_run_git_lines(repo_root, ["ls-files"]))
    safe_targets: list[dict[str, Any]] = []
    forbidden_targets: list[dict[str, str]] = []
    seen: set[str] = set()
    pycache_directories: set[str] = set()

    candidates = _collect_candidates(repo_root)
    for item in sorted(candidates, key=lambda candidate: (_candidate_sort_key(candidate), str(candidate[2]))):
        kind, category, path = item
        if not path.exists():
            continue

        rel = _normalize_rel(path.relative_to(repo_root))
        if rel in seen:
            continue

        if not _is_within_root(path, repo_root):
            forbidden_targets.append({"path": rel, "kind": kind, "category": category, "reason": "path_safety_uncertain"})
            continue

        if _is_forbidden_path(rel):
            forbidden_targets.append({"path": rel, "kind": kind, "category": category, "reason": "forbidden_path"})
            continue

        if _is_tracked_or_contains_tracked(rel, tracked_files):
            forbidden_targets.append({"path": rel, "kind": kind, "category": category, "reason": "tracked_path"})
            continue

        if kind == "file" and Path(rel).parent.as_posix() in pycache_directories:
            # covered by directory entry when directory target is deleted
            continue

        safe_targets.append(
            {
                "category": category,
                "kind": kind,
                "path": rel,
                "bytes_estimate": _estimate_bytes(path),
            },
        )
        seen.add(rel)
        if category == "Python __pycache__ directories" and kind == "directory":
            pycache_directories.add(rel)

    safe_targets = [entry for entry in safe_targets if not (entry["category"] == "Python .pyc files inside __pycache__" and Path(entry["path"]).parent.as_posix() in pycache_directories)]
    category_counts = dict(Counter(item["category"] for item in safe_targets))
    return {
        "safe_targets": safe_targets,
        "target_count": len(safe_targets),
        "category_counts": category_counts,
        "forbidden_targets": forbidden_targets,
    }


def _collect_candidates(repo_root: Path) -> list[tuple[str, str, Path]]:
    candidates: list[tuple[str, str, Path]] = []
    node_modules = repo_root / "apps" / "dashboard" / "node_modules"
    if node_modules.is_dir():
        candidates.append(("directory", "apps/dashboard/node_modules/", node_modules))

    dist = repo_root / "apps" / "dashboard" / "dist"
    if dist.is_dir():
        candidates.append(("directory", "apps/dashboard/dist/", dist))

    pytest_cache = repo_root / ".pytest_cache"
    if pytest_cache.is_dir():
        candidates.append(("directory", ".pytest_cache/", pytest_cache))

    for path in repo_root.rglob("__pycache__"):
        if path.is_dir():
            candidates.append(("directory", "Python __pycache__ directories", path))

    for path in repo_root.rglob("*.pyc"):
        if path.is_file() and "__pycache__" in path.parts:
            candidates.append(("file", "Python .pyc files inside __pycache__", path))

    return candidates


def _is_forbidden_path(relative_path: str) -> bool:
    normalized = _normalize_rel(relative_path)
    if _is_prefixed(normalized, "Reports/") or _is_prefixed(normalized, ".local_backlog/"):
        return True
    if _is_prefixed(normalized, ".local_hold/") or _is_prefixed(normalized, "archive/"):
        return True
    if _is_prefixed(normalized, "docs/") or _is_prefixed(normalized, "automation/"):
        return True
    if _is_prefixed(normalized, "tests/") or _is_prefixed(normalized, "services/"):
        return True
    if normalized == ".env" or normalized.startswith(".env.") or normalized in {"credentials", "secrets"}:
        return True
    for root_runtime_file in ROOT_RUNTIME_JSON_FILES:
        if normalized == _normalize_rel(root_runtime_file):
            return True
    if normalized.startswith("Reports/forex_delivery/AIOS_FOREX_110_"):
        return True
    for proof in FOREX_110_PROOF_FILES:
        if normalized == _normalize_rel(proof):
            return True
    return False


def _is_tracked_or_contains_tracked(relative_path: str, tracked_files: set[str]) -> bool:
    normalized = _normalize_rel(relative_path)
    if normalized in tracked_files:
        return True
    prefix = normalized.rstrip("/") + "/"
    return any(
        tracked == normalized or tracked.startswith(prefix)
        for tracked in tracked_files
    )


def _apply_targets(
    repo_root: Path,
    safe_targets: list[dict[str, Any]],
) -> tuple[list[str], list[dict[str, str]], int, int]:
    deleted_targets: list[str] = []
    skipped_targets: list[dict[str, str]] = []
    deleted_count = 0
    deleted_bytes_estimate = 0
    deleted_dirs: set[str] = set()

    for item in sorted(safe_targets, key=lambda item: (
        SAFE_CATEGORY_ORDER.get(item["category"], 999),
        _normalize_rel(item["path"]),
    )):
        path = repo_root / item["path"]
        rel = _normalize_rel(item["path"])
        if not path.exists():
            skipped_targets.append({"path": rel, "reason": "missing_before_delete"})
            continue

        if item["kind"] == "file":
            parent_dir = _normalize_rel(path.parent)
            if parent_dir in deleted_dirs:
                skipped_targets.append({"path": rel, "reason": "covered_by_deleted_parent"})
                continue
            try:
                path.unlink()
            except OSError as exc:
                skipped_targets.append({"path": rel, "reason": f"delete_failed:{exc!s}"})
                continue
            deleted_targets.append(rel)
            deleted_count += 1
            deleted_bytes_estimate += int(item.get("bytes_estimate", 0))
            continue

        if item["kind"] == "directory":
            try:
                shutil.rmtree(path)
            except OSError as exc:
                skipped_targets.append({"path": rel, "reason": f"delete_failed:{exc!s}"})
                continue
            deleted_targets.append(rel)
            deleted_dirs.add(rel)
            deleted_count += 1
            deleted_bytes_estimate += int(item.get("bytes_estimate", 0))
            continue

        skipped_targets.append({"path": rel, "reason": f"unsupported_kind:{item['kind']}"})

    return deleted_targets, skipped_targets, deleted_count, deleted_bytes_estimate


def _skip_targets(safe_targets: list[dict[str, Any]], reason: str) -> list[dict[str, str]]:
    return [{"path": item["path"], "reason": reason} for item in safe_targets]


def _git_counts(repo_root: Path) -> dict[str, list[str]]:
    return {
        "non_ignored_untracked": _run_git_lines(repo_root, ["ls-files", "--others", "--exclude-standard"]),
        "ignored": _run_git_lines(repo_root, ["ls-files", "-i", "-o", "--exclude-standard"]),
    }


def _git_status(repo_root: Path) -> dict[str, list[str] | str]:
    lines = _run_git_lines(repo_root, ["status", "--short", "--branch"])
    branch = "UNKNOWN"
    if lines:
        status_line = lines[0].strip()
        if status_line.startswith("## "):
            branch = status_line[3:].split("...")[0]
    return {
        "branch": branch,
        "tracked_dirty_lines": [line for line in lines if line and not line.startswith("## ") and not line.startswith("??")],
        "dirty_lines": [line for line in lines if line and not line.startswith("## ")],
        "lines": lines,
    }


def _run_git_lines(repo_root: Path, args: list[str]) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _is_within_root(path: Path, repo_root: Path) -> bool:
    try:
        path.relative_to(repo_root)
        return True
    except ValueError:
        return False


def _is_prefixed(value: str, prefix: str) -> bool:
    normalized = _normalize_rel(value)
    normalized_prefix = _normalize_rel(prefix).rstrip("/")
    return normalized == normalized_prefix or normalized.startswith(normalized_prefix + "/")


def _normalize_rel(value: str | Path) -> str:
    text = value.as_posix() if isinstance(value, Path) else str(value)
    text = text.replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.strip("/")


def _estimate_bytes(path: Path) -> int:
    try:
        if path.is_file():
            return int(path.stat().st_size)

        total = 0
        for child in path.rglob("*"):
            if child.is_file():
                total += int(child.stat().st_size)
        return total
    except OSError:
        return 0


def _is_forex_110_closure_landed(repo_root: Path) -> bool:
    return all((repo_root / proof).exists() for proof in FOREX_110_PROOF_FILES)


def _candidate_sort_key(candidate: tuple[str, str, Path]) -> tuple[int, str]:
    _, category, _ = candidate
    return (SAFE_CATEGORY_ORDER.get(category, 999), category)


def _next_safe_action(cleanup_apply_status: str) -> str:
    if cleanup_apply_status == "APPLY_COMPLETED":
        return "Cleanup completed. Verify state/report and run git status before next packet."
    if cleanup_apply_status == "APPLY_NO_TARGETS":
        return "No deletions were safe. Re-run only if safe targets exist."
    if cleanup_apply_status == "APPLY_BLOCKED":
        return "Resolve precheck blockers and rerun with --apply."
    return "Review dry-run manifest and run --apply only after prechecks pass."


def _attack_to_finish(*, cleanup_apply_status: str, precheck_ok: bool, branch: str, precheck_reason: str | None) -> dict[str, str]:
    if cleanup_apply_status == "APPLY_COMPLETED":
        return {
            "blocker_id": "NO_BLOCKER",
            "blocker_status": "DONE",
            "exact_blocker": "NONE",
            "canonical_owner_file": f"{DEFAULT_REPORT_ROOT}/{REPORT_NAME}",
            "test_file": "tests/forex_engine/test_forex_110_post_closure_local_residue_cleanup_apply_v1.py",
            "runner_script": "scripts/forex_delivery/run_forex_110_post_closure_local_residue_cleanup_apply_v1.py",
            "missing_evidence_field": "NONE",
            "unlock_status_required": "NONE",
            "next_packet_name": "PKT-FOREX-110-POST-CLOSURE-LOCAL-RESIDUE-CLEANUP-APPLY-V1",
            "owner_action_required": "Review deleted-target evidence and proceed with closure reporting.",
            "stop_condition": "NONE",
            "no_bloat_guard": "Do not expand cleanup categories beyond this packet.",
        }

    if cleanup_apply_status == "DRY_RUN_COMPLETE":
        blocker_status = "READY_FOR_APPLY_REVIEW" if precheck_ok else "BLOCKED"
        exact = "NONE" if precheck_ok else str(precheck_reason or "precheck_failed")
        return {
            "blocker_id": "NO_BLOCKER" if precheck_ok else "PRECHECK_BLOCKER",
            "blocker_status": blocker_status,
            "exact_blocker": exact,
            "canonical_owner_file": f"{DEFAULT_REPORT_ROOT}/{REPORT_NAME}",
            "test_file": "tests/forex_engine/test_forex_110_post_closure_local_residue_cleanup_apply_v1.py",
            "runner_script": "scripts/forex_delivery/run_forex_110_post_closure_local_residue_cleanup_apply_v1.py",
            "missing_evidence_field": "NONE" if precheck_ok else "precheck_status",
            "unlock_status_required": "APPLY_REVIEW" if precheck_ok else "PRECHECK",
            "next_packet_name": "PKT-FOREX-110-POST-CLOSURE-LOCAL-RESIDUE-CLEANUP-APPLY-V1",
            "owner_action_required": "Review dry-run manifest and run apply when safe.",
            "stop_condition": "NONE" if precheck_ok else "precheck_failed",
            "no_bloat_guard": "Do not add categories without explicit lane update.",
        }

    return {
        "blocker_id": "PRECHECK_BLOCKER",
        "blocker_status": "BLOCKED",
        "exact_blocker": precheck_reason or "precheck_failed",
        "canonical_owner_file": f"{DEFAULT_REPORT_ROOT}/{PLAN_REPORT_NAME}",
        "test_file": "tests/forex_engine/test_forex_110_post_closure_local_residue_cleanup_apply_v1.py",
        "runner_script": "scripts/forex_delivery/run_forex_110_post_closure_local_residue_cleanup_apply_v1.py",
        "missing_evidence_field": "precheck_status",
        "unlock_status_required": "PRECHECK",
        "next_packet_name": "PKT-FOREX-110-POST-CLOSURE-LOCAL-RESIDUE-CLEANUP-APPLY-V1",
        "owner_action_required": "Resolve precheck blockers then rerun.",
        "stop_condition": "precheck_failed",
        "no_bloat_guard": "No scope expansion.",
    }


def build_report_markdown(result: dict[str, Any]) -> str:
    lines: list[str] = [
        f"# AIOS Forex 110 Post-Closure Local Residue Cleanup Apply V1 ({result['packet_id']})",
        "",
        f"Cleanup status: `{result['cleanup_apply_status']}`",
        f"Forex 110 closure landed: `{str(result['forex_110_closure_landed']).lower()}`",
        "",
        "## Counts",
        f"- Before safe target count: `{result['before_counts']['safe_target_count']}`",
        f"- After safe target count: `{result['after_counts']['safe_target_count']}`",
        f"- Non-ignored untracked before: `{result['non_ignored_untracked_count_before']}`",
        f"- Non-ignored untracked after: `{result['non_ignored_untracked_count_after']}`",
        f"- Ignored/local-generated before: `{result['ignored_local_generated_count_before']}`",
        f"- Ignored/local-generated after: `{result['ignored_local_generated_count_after']}`",
        f"- Deleted count: `{result['deleted_count']}`",
        f"- Deleted bytes estimate: `{result['deleted_bytes_estimate']}`",
        "",
        "## Safe delete categories",
    ]
    for category in SAFE_DELETE_CATEGORIES:
        lines.append(f"- {category}")

    lines.extend(["", "## Safe targets"])
    safe_targets = result["dry_run_manifest"]["safe_targets"]
    if safe_targets:
        for target in safe_targets:
            lines.append(f"- {target['category']} | {target['path']} ({target['kind']})")
    else:
        lines.append("- none")

    lines.extend(["", "## Deleted targets"])
    if result["deleted_targets"]:
        for target in result["deleted_targets"]:
            lines.append(f"- {target}")
    else:
        lines.append("- none")

    lines.extend(["", "## Skipped targets"])
    if result["skipped_targets"]:
        for target in result["skipped_targets"]:
            lines.append(f"- {target['path']}: {target['reason']}")
    else:
        lines.append("- none")

    lines.extend(["", "## Forbidden targets detected"])
    if result["forbidden_targets_detected"]:
        for item in result["forbidden_targets_detected"]:
            lines.append(f"- {item['path']}: {item['reason']}")
    else:
        lines.append("- none")

    lines.extend(["", "## ATTACK_TO_FINISH"])
    for key, value in result["ATTACK_TO_FINISH"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(["", "## Next Safe Action", result["next_safe_action"], ""])
    return "\n".join(lines)


__all__ = [
    "PACKET_ID",
    "STATE_NAME",
    "REPORT_NAME",
    "run_forex_110_post_closure_local_residue_cleanup_apply_v1",
    "build_report_markdown",
]
