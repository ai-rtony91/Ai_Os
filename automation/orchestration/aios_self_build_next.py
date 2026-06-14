"""Select the next AI_OS campaign task and render a safe packet preview.

This command is read-only. It reads the campaign registry, selects the highest
priority READY stage whose stage dependencies are COMPLETE and whose blockers
are empty, then prints a JSON packet preview to stdout. With --write-packet it
may also write the preview packet text to an explicitly guarded preview path.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY_PATH = (
    Path("automation")
    / "orchestration"
    / "campaign_registry"
    / "AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json"
)
DEFAULT_PACKET_OUTPUT_DIR = (
    Path("automation")
    / "orchestration"
    / "work_packets"
    / "preview"
)
FORBIDDEN_OUTPUT_PREFIXES = (
    Path("Reports"),
    Path("control") / "review_bridge",
)
FORBIDDEN_OUTPUT_PARTS = {
    "active",
    "complete",
    "blocked",
    "queue",
    "approval",
    "workers",
}

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "normal": 2,
    "low": 3,
}

SAFETY = {
    "execution": False,
    "mutation": False,
    "queue_mutation": False,
    "approval_mutation": False,
    "worker_launch": False,
    "runtime_launch": False,
    "broker_live_trading": False,
    "commits": False,
    "pushes": False,
}

DEFAULT_FINAL_REPORT_FORMAT = [
    "SUMMARY:",
    "FILES INSPECTED:",
    "FINDINGS:",
    "VALIDATORS RUN:",
    "VALIDATION RESULT:",
    "GIT STATUS:",
    "COMMIT STATUS:",
    "PUSH STATUS:",
    "NEXT SAFE ACTION:",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_path_text(path: Path) -> str:
    return path.as_posix().strip().lstrip("./")


def priority_rank(priority: Any) -> int:
    return PRIORITY_ORDER.get(str(priority or "").strip().lower(), 99)


def stage_map(campaigns: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for campaign in campaigns:
        for stage in campaign.get("stages", []) or []:
            stage_id = str(stage.get("stage_id") or "").strip()
            if stage_id:
                mapped[stage_id] = stage
    return mapped


def dependencies_complete(stage: dict[str, Any], mapped_stages: dict[str, dict[str, Any]]) -> bool:
    for dependency in stage.get("depends_on", []) or []:
        dependency_id = str(dependency or "").strip()
        if not dependency_id:
            continue
        if dependency_id not in mapped_stages:
            return False
        if str(mapped_stages[dependency_id].get("status") or "") != "COMPLETE":
            return False
    return True


def nonempty_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def safe_filename(value: str) -> str:
    safe = []
    for char in value:
        if char.isalnum() or char in {"-", "_", "."}:
            safe.append(char)
        else:
            safe.append("-")
    return "".join(safe).strip(".-") or "AIOS_PACKET_PREVIEW"


def path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_output_dir(repo_root: str | Path, output_dir: str | Path | None = None) -> Path:
    root = Path(repo_root).resolve()
    target = Path(output_dir) if output_dir is not None else DEFAULT_PACKET_OUTPUT_DIR
    if not target.is_absolute():
        target = root / target
    target = target.resolve()

    if path_is_relative_to(target, root):
        scoped_path = target.relative_to(root)
    else:
        scoped_path = target
    scoped_text = normalize_path_text(scoped_path)
    scoped_parts = {part.lower() for part in scoped_path.parts}

    for prefix in FORBIDDEN_OUTPUT_PREFIXES:
        prefix_text = normalize_path_text(prefix)
        if scoped_text == prefix_text or scoped_text.startswith(prefix_text + "/"):
            raise ValueError(f"output_dir is blocked: {scoped_text}")

    if FORBIDDEN_OUTPUT_PARTS.intersection(scoped_parts):
        raise ValueError(f"output_dir contains a blocked path segment: {scoped_text}")

    return target


def render_packet_text(packet_preview: dict[str, Any]) -> str:
    allowed_paths = "\n".join(f"- {path}" for path in packet_preview["allowed_paths"])
    forbidden_paths = "\n".join(f"- {path}" for path in packet_preview["forbidden_paths"])
    validators = "\n".join(f"- {validator}" for validator in packet_preview["validators"])
    final_report = "\n".join(packet_preview["final_report_format"])

    return (
        "CODEX-ONLY PROMPT\n\n"
        "AI_OS EXECUTION TOKEN\n"
        "AI_OS BOOTSTRAP REQUIRED\n\n"
        f"PACKET ID: {packet_preview['packet_id']}\n"
        f"MODE: {packet_preview['mode']}\n"
        f"ZONE: {packet_preview['zone']}\n"
        f"WORKER: {packet_preview['worker']}\n"
        f"LANE: {packet_preview['lane']}\n"
        f"BRANCH: {packet_preview['branch']}\n"
        f"WORKTREE: {packet_preview['worktree']}\n\n"
        "MISSION:\n"
        f"{packet_preview['mission']}\n\n"
        "ALLOWED PATHS:\n"
        f"{allowed_paths}\n\n"
        "FORBIDDEN PATHS:\n"
        f"{forbidden_paths}\n\n"
        "VALIDATORS:\n"
        f"{validators}\n\n"
        "STOP POINT:\n"
        f"{packet_preview['stop_point']}\n\n"
        "FINAL REPORT FORMAT:\n"
        f"{final_report}\n"
    )


def write_packet_preview(
    packet_preview: dict[str, Any],
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
) -> Path:
    target_dir = resolve_output_dir(repo_root, output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{safe_filename(str(packet_preview['packet_id']))}.txt"
    target_path = target_dir / filename
    target_path.write_text(render_packet_text(packet_preview), encoding="utf-8")
    return target_path


def find_ready_candidates(registry: dict[str, Any]) -> list[dict[str, Any]]:
    campaigns = list(registry.get("campaigns", []) or [])
    mapped_stages = stage_map(campaigns)
    candidates: list[dict[str, Any]] = []

    for campaign in campaigns:
        campaign_blockers = nonempty_list(campaign.get("blocked_by"))
        phases = {str(phase.get("phase_id")): phase for phase in campaign.get("phases", []) or []}
        for stage in campaign.get("stages", []) or []:
            if str(stage.get("status") or "") != "READY":
                continue
            stage_blockers = nonempty_list(stage.get("blocked_by"))
            if campaign_blockers or stage_blockers:
                continue
            if not dependencies_complete(stage, mapped_stages):
                continue

            phase = phases.get(str(stage.get("phase_id"))) or {}
            candidates.append(
                {
                    "campaign": campaign,
                    "phase": phase,
                    "stage": stage,
                    "priority_rank": priority_rank(stage.get("priority")),
                    "campaign_priority_rank": priority_rank(campaign.get("priority")),
                }
            )

    return sorted(
        candidates,
        key=lambda item: (
            item["priority_rank"],
            item["campaign_priority_rank"],
            str(item["campaign"].get("campaign_id") or ""),
            str(item["stage"].get("stage_id") or ""),
        ),
    )


def select_next_stage(registry: dict[str, Any]) -> dict[str, Any] | None:
    candidates = find_ready_candidates(registry)
    return candidates[0] if candidates else None


def build_packet_preview(selected: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    campaign = selected["campaign"]
    phase = selected["phase"]
    stage = selected["stage"]
    stage_id = str(stage.get("stage_id") or "UNKNOWN_STAGE")
    packet_id = str(stage.get("next_packet_candidate") or f"PKT-{stage_id}")
    validators = nonempty_list(campaign.get("validation_commands")) or ["git diff --check"]

    return {
        "packet_id": packet_id,
        "mission": str(stage.get("title") or campaign.get("objective") or "Review next AI_OS task."),
        "worker": str(campaign.get("recommended_worker") or "EAST_OCC_01"),
        "lane": str(campaign.get("crew_lane") or "self-build-next-runner"),
        "branch": str(registry.get("active_branch") or "main"),
        "worktree": str(registry.get("active_worktree") or r"C:\Dev\Ai.Os"),
        "allowed_paths": nonempty_list(campaign.get("allowed_paths")),
        "forbidden_paths": nonempty_list(campaign.get("blocked_paths")),
        "validators": validators,
        "stop_point": str(campaign.get("stop_condition") or "Stop after DRY_RUN report. Do not stage, commit, or push."),
        "final_report_format": DEFAULT_FINAL_REPORT_FORMAT,
        "preview_only": True,
        "mode": "DRY_RUN",
        "zone": str(phase.get("title") or campaign.get("title") or "AI_OS self-build"),
    }


def relative_output_path(repo_root: str | Path, path: Path) -> str:
    root = Path(repo_root).resolve()
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_report(
    repo_root: str | Path = ".",
    *,
    write_packet: bool = False,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    registry_path = root / DEFAULT_REGISTRY_PATH
    registry = load_json(registry_path)
    selected = select_next_stage(registry)

    if selected is None:
        report = {
            "schema": "AIOS_SELF_BUILD_NEXT.v1",
            "mode": "DRY_RUN_READ_ONLY",
            "generated_at_utc": utc_now(),
            "selected_stage": None,
            "packet_preview": None,
            "written_packet_path": None,
            "reason": "No READY stage with complete dependencies and no blockers was found.",
            "blockers": ["NO_READY_STAGE"],
            "safety": SAFETY.copy(),
        }
        return report

    campaign = selected["campaign"]
    phase = selected["phase"]
    stage = selected["stage"]

    packet_preview = build_packet_preview(selected, registry)
    written_packet_path = None
    if write_packet:
        written_path = write_packet_preview(packet_preview, root, output_dir)
        written_packet_path = relative_output_path(root, written_path)

    return {
        "schema": "AIOS_SELF_BUILD_NEXT.v1",
        "mode": "DRY_RUN_READ_ONLY",
        "generated_at_utc": utc_now(),
        "selected_campaign": {
            "campaign_id": campaign.get("campaign_id"),
            "title": campaign.get("title"),
            "status": campaign.get("status"),
            "priority": campaign.get("priority"),
        },
        "selected_phase": {
            "phase_id": phase.get("phase_id") or stage.get("phase_id"),
            "title": phase.get("title") or "UNKNOWN",
            "status": phase.get("status") or "UNKNOWN",
        },
        "selected_stage": {
            "stage_id": stage.get("stage_id"),
            "title": stage.get("title"),
            "status": stage.get("status"),
            "priority": stage.get("priority"),
            "depends_on": nonempty_list(stage.get("depends_on")),
            "next_packet_candidate": stage.get("next_packet_candidate"),
        },
        "reason": "Selected highest-priority READY stage with complete dependencies and no blockers.",
        "packet_preview": packet_preview,
        "written_packet_path": written_packet_path,
        "safety": SAFETY.copy(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the next AI_OS self-build packet preview.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--write-packet", action="store_true", help="Write the selected Codex packet preview to a guarded .txt file.")
    parser.add_argument("--output-dir", default=None, help="Packet preview output directory. Defaults to automation/orchestration/work_packets/preview.")
    args = parser.parse_args()

    report = build_report(args.repo_root, write_packet=args.write_packet, output_dir=args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
