"""Read-only AI_OS worker route recommender.

Standard library only. Emits JSON to stdout by default. If --write-report is
passed, it writes latest_worker_route_recommendation.json under
automation/orchestration/worker_routing/. It does not execute packets, launch
workers, edit packets, mutate queues, commit, push, merge, touch trading
systems, or call Codex/Claude.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "AIOS_WORKER_ROUTE_RECOMMENDER.v1"
REPORT_RELATIVE_PATH = Path("automation/orchestration/worker_routing/latest_worker_route_recommendation.json")
PACKET_FOLDERS = (
    Path("automation/orchestration/work_packets"),
    Path("work_packets"),
)
ACTIVE_PACKET_FOLDERS = (
    Path("automation/orchestration/work_packets/active"),
    Path("work_packets/active"),
)

HUMAN_OWNER_TERMS = (
    "approval",
    "approve",
    "human owner",
    "merge",
    "push",
    "secret",
    "credential",
    "api-key",
    "api key",
    "broker",
    "oanda",
    "live trading",
    "live-order",
    "live order",
    "destructive",
    "delete",
    "remove-item",
    "reset --hard",
)

VALIDATOR_TERMS = (
    "validation",
    "validate",
    "validator",
    "parse",
    "test",
    "check",
    "audit",
    "diff --check",
    "py_compile",
)

CLAUDE_WEST_TERMS = (
    "review",
    "architecture",
    "risk",
    "design",
    "critique",
    "strategy",
    "dry_run",
    "dry-run",
    "inspect",
)

CODEX_EAST_TERMS = (
    "build",
    "apply",
    "code",
    "script",
    "implementation",
    "implement",
    "tests",
    "create",
    "update",
    "patch",
)


@dataclass
class GitState:
    branch: str = "UNKNOWN"
    status_line: str = ""
    changed_files: list[str] = field(default_factory=list)
    untracked_files: list[str] = field(default_factory=list)
    git_error: str = ""


@dataclass
class RouteRecommendation:
    packet_id: str
    file_path: str
    recommended_worker: str
    reason: str
    risk_level: str
    blocked_actions: list[str]
    next_safe_action: str
    needs_human_approval: bool


@dataclass
class RouteReport:
    schema: str
    mode: str
    generated_at: str
    repo_root: str
    execution_enabled: bool
    worker_launch_enabled: bool
    packet_mutation_enabled: bool
    git_state: GitState
    scanned_packet_folders: list[str]
    recommendations: list[RouteRecommendation]
    blocked_capabilities: list[str] = field(
        default_factory=lambda: [
            "packet_execution",
            "worker_launch",
            "codex_or_claude_calls",
            "packet_mutation",
            "queue_mutation",
            "approval_mutation",
            "network_calls",
            "commit",
            "push",
            "merge",
            "broker_or_trading_execution",
        ]
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def run_git_status(repo_root: Path) -> GitState:
    state = GitState()
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain=v1", "--branch"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001 - fail-closed JSON evidence
        state.git_error = str(exc)
        return state

    if completed.returncode != 0:
        state.git_error = completed.stderr.strip() or completed.stdout.strip() or f"git status returned {completed.returncode}"
        return state

    for line in completed.stdout.splitlines():
        if line.startswith("## "):
            state.status_line = line
            state.branch = line[3:].split("...", maxsplit=1)[0].strip() or "UNKNOWN"
            continue

        if not line.strip():
            continue

        status = line[:2]
        path = normalize_path(line[3:].strip().strip('"'))
        if " -> " in path:
            path = path.split(" -> ", maxsplit=1)[1]

        if status == "??":
            state.untracked_files.append(path)
        else:
            state.changed_files.append(path)

    state.changed_files.sort()
    state.untracked_files.sort()
    return state


def read_text_safely(path: Path, max_bytes: int = 200_000) -> str:
    data = path.read_bytes()[:max_bytes]
    return data.decode("utf-8", errors="replace")


def packet_scan_roots(repo_root: Path) -> tuple[Path, ...]:
    active_roots = tuple(path for path in ACTIVE_PACKET_FOLDERS if (repo_root / path).is_dir())
    if active_roots:
        return active_roots
    return tuple(path for path in PACKET_FOLDERS if (repo_root / path).is_dir())


def iter_packet_files(repo_root: Path) -> Iterable[Path]:
    allowed_suffixes = {".json", ".md", ".txt", ".yaml", ".yml"}
    for folder in packet_scan_roots(repo_root):
        full_folder = repo_root / folder
        for path in sorted(full_folder.glob("*")):
            if path.is_file() and path.suffix.lower() in allowed_suffixes:
                yield path


def find_packet_id(text: str, fallback: str) -> str:
    try:
        payload = json.loads(text)
        if isinstance(payload, dict) and payload.get("packet_id"):
            return str(payload["packet_id"])
    except json.JSONDecodeError:
        pass

    match = re.search(r"(?im)^\s*PACKET ID\s*:\s*(.+?)\s*$", text)
    if match:
        return match.group(1).strip()
    match = re.search(r"(?im)^\s*[\"']?packet_id[\"']?\s*[:=]\s*[\"']?([^\"'\n\r,}]+)", text)
    if match:
        return match.group(1).strip()
    return fallback


def matched_terms(text: str, terms: Iterable[str]) -> list[str]:
    lowered = text.lower()
    return sorted({term for term in terms if term in lowered})


def build_recommendation(packet_id: str, file_path: str, text: str) -> RouteRecommendation:
    human_matches = matched_terms(text, HUMAN_OWNER_TERMS)
    validator_matches = matched_terms(text, VALIDATOR_TERMS)
    west_matches = matched_terms(text, CLAUDE_WEST_TERMS)
    east_matches = matched_terms(text, CODEX_EAST_TERMS)

    blocked_actions = human_matches.copy()
    needs_human_approval = bool(human_matches)

    if human_matches:
        return RouteRecommendation(
            packet_id=packet_id,
            file_path=file_path,
            recommended_worker="HUMAN_OWNER",
            reason=f"Human-gated terms found: {', '.join(human_matches)}.",
            risk_level="HIGH",
            blocked_actions=blocked_actions,
            next_safe_action="Human Owner must review and explicitly approve the next action. Do not launch workers automatically.",
            needs_human_approval=True,
        )

    if validator_matches:
        return RouteRecommendation(
            packet_id=packet_id,
            file_path=file_path,
            recommended_worker="VALIDATOR",
            reason=f"Validation terms found: {', '.join(validator_matches)}.",
            risk_level="MEDIUM",
            blocked_actions=blocked_actions,
            next_safe_action="Route to validator for read-only evidence, parse, test, check, or audit output.",
            needs_human_approval=needs_human_approval,
        )

    if west_matches and not east_matches:
        return RouteRecommendation(
            packet_id=packet_id,
            file_path=file_path,
            recommended_worker="CLAUDE_WEST",
            reason=f"Review/strategy terms found: {', '.join(west_matches)}.",
            risk_level="MEDIUM",
            blocked_actions=blocked_actions,
            next_safe_action="Route to Claude West for bounded review, architecture, risk, design, critique, or strategy.",
            needs_human_approval=needs_human_approval,
        )

    if east_matches:
        return RouteRecommendation(
            packet_id=packet_id,
            file_path=file_path,
            recommended_worker="CODEX_EAST",
            reason=f"Build/apply terms found: {', '.join(east_matches)}.",
            risk_level="MEDIUM",
            blocked_actions=blocked_actions,
            next_safe_action="Route to Codex East for scoped implementation only after allowed paths and validation are clear.",
            needs_human_approval=needs_human_approval,
        )

    return RouteRecommendation(
        packet_id=packet_id,
        file_path=file_path,
        recommended_worker="HUMAN_OWNER",
        reason="Uncertain route. No decisive worker classification terms were found.",
        risk_level="HIGH",
        blocked_actions=["uncertain_route"],
        next_safe_action="Fail closed. Human Owner should clarify lane, allowed paths, stop condition, and validator chain.",
        needs_human_approval=True,
    )


def _packet_text(packet: dict[str, Any]) -> str:
    parts = []
    for key in (
        "packet_id",
        "task_id",
        "title",
        "packet_title",
        "mode",
        "status",
        "lane",
        "summary",
        "description",
        "next_safe_action",
        "status_reason",
    ):
        value = packet.get(key)
        if value:
            parts.append(f"{key}: {value}")
    for value in packet.get("related_files") or []:
        parts.append(f"related_file: {value}")
    return "\n".join(parts)


def recommend_route_for_packet(packet: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Return routing recommendation for one queue_scanner packet object."""
    root = Path(repo_root).resolve()
    packet_id = str(packet.get("packet_id") or packet.get("task_id") or "UNKNOWN")
    file_path = normalize_path(packet.get("source_path") or packet.get("packet_path") or packet_id)
    text = _packet_text(packet)
    if not text and file_path:
        candidate = root / file_path
        if candidate.is_file():
            text = read_text_safely(candidate)
    recommendation = build_recommendation(packet_id, file_path, text)
    return asdict(recommendation)


def recommend_routes_for_packets(packets: list[dict[str, Any]], repo_root: Path) -> list[dict[str, Any]]:
    """Return route recommendations for queue_scanner packet objects."""
    return [recommend_route_for_packet(packet, repo_root) for packet in packets]


def merge_route_with_worker_profile(route: dict[str, Any], profiles: dict[str, Any]) -> dict[str, Any]:
    """Attach assigned_worker/profile evidence without overriding classifier blindly."""
    workers = profiles.get("workers", profiles if isinstance(profiles, list) else [])
    by_id = {str(worker.get("worker_id")): worker for worker in workers if isinstance(worker, dict) and worker.get("worker_id")}
    recommended = str(route.get("recommended_worker") or "")
    profile = by_id.get(recommended)
    if not profile:
        return {**route, "assigned_worker": "", "profile_match": False}
    return {
        **route,
        "assigned_worker": recommended,
        "profile_match": True,
        "profile_display_title": str(profile.get("display_title") or recommended),
    }


def build_git_state_recommendation(git_state: GitState) -> RouteRecommendation:
    if git_state.git_error:
        return RouteRecommendation(
            packet_id="GIT_STATE",
            file_path="__git_status__",
            recommended_worker="HUMAN_OWNER",
            reason=f"git status failed: {git_state.git_error}",
            risk_level="HIGH",
            blocked_actions=["git_status_failed"],
            next_safe_action="Stop and resolve git status failure before routing work.",
            needs_human_approval=True,
        )

    dirty_files = [*git_state.changed_files, *git_state.untracked_files]
    if dirty_files:
        return RouteRecommendation(
            packet_id="GIT_STATE_DIRTY",
            file_path="__git_status__",
            recommended_worker="HUMAN_OWNER",
            reason="Working tree has changed or untracked files; commit/push routing remains human-gated.",
            risk_level="MEDIUM",
            blocked_actions=["commit", "push", "merge"],
            next_safe_action="Review changed files and route only approved paths to the correct worker.",
            needs_human_approval=True,
        )

    return RouteRecommendation(
        packet_id="GIT_STATE_CLEAN",
        file_path="__git_status__",
        recommended_worker="CLAUDE_WEST",
        reason="No work packets found and git state is clean; strategy/review is the safest next route.",
        risk_level="LOW",
        blocked_actions=[],
        next_safe_action="Provide a packet or ask Claude West for review/strategy before APPLY work.",
        needs_human_approval=False,
    )


def build_route_report(repo_root: str | Path) -> RouteReport:
    resolved_root = Path(repo_root).resolve()
    git_state = run_git_status(resolved_root)
    scanned_folders = [normalize_path(path) for path in packet_scan_roots(resolved_root)]
    recommendations: list[RouteRecommendation] = []

    if not resolved_root.exists() or not resolved_root.is_dir():
        git_state.git_error = f"Repository root not found: {resolved_root}"
        recommendations.append(build_git_state_recommendation(git_state))
    else:
        for packet_file in iter_packet_files(resolved_root):
            relative_path = normalize_path(packet_file.relative_to(resolved_root))
            try:
                text = read_text_safely(packet_file)
            except Exception as exc:  # noqa: BLE001 - fail closed on unreadable packets
                recommendations.append(
                    RouteRecommendation(
                        packet_id=relative_path,
                        file_path=relative_path,
                        recommended_worker="HUMAN_OWNER",
                        reason=f"Packet could not be read safely: {exc}",
                        risk_level="HIGH",
                        blocked_actions=["unreadable_packet"],
                        next_safe_action="Human Owner should inspect the packet manually before routing.",
                        needs_human_approval=True,
                    )
                )
                continue

            packet_id = find_packet_id(text, relative_path)
            recommendations.append(build_recommendation(packet_id, relative_path, text))

        if not recommendations:
            recommendations.append(build_git_state_recommendation(git_state))

    return RouteReport(
        schema=SCHEMA,
        mode="DRY_RUN",
        generated_at=utc_now(),
        repo_root=str(resolved_root),
        execution_enabled=False,
        worker_launch_enabled=False,
        packet_mutation_enabled=False,
        git_state=git_state,
        scanned_packet_folders=scanned_folders,
        recommendations=recommendations,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit read-only AI_OS worker route recommendations.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument(
        "--write-report",
        action="store_true",
        help=(
            "Write latest_worker_route_recommendation.json under "
            "automation/orchestration/worker_routing/."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report = build_route_report(repo_root)
    payload = json.dumps(asdict(report), indent=2 if args.pretty else None, sort_keys=True)

    if args.write_report:
        report_path = repo_root / REPORT_RELATIVE_PATH
        if report_path.parent != repo_root / "automation" / "orchestration" / "worker_routing":
            raise RuntimeError("Report path escaped approved worker_routing directory.")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(payload + "\n", encoding="utf-8")

    print(payload)
    return 1 if report.git_state.git_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
