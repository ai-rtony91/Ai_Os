"""Generate review-only canonical authority decision packets."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TRIAGE_REPORT_ROOT = Path("Reports/operator_relief/audits")
DECISION_PACKET_ROOT = Path("Reports/operator_relief/decision_packets")
REPORT_TYPE = "operator_relief_canonical_decision_packet_v1"
INDEX_REPORT_TYPE = "operator_relief_canonical_decision_packet_index_v1"
DECISION_OPTIONS = (
    "KEEP_AS_CANONICAL",
    "DEPRECATE_AFTER_REVIEW",
    "KEEP_AS_ARCHIVE_OR_EVIDENCE",
    "MERGE_CONTENT_LATER",
    "DO_NOT_TOUCH",
    "NEEDS_HUMAN_REVIEW",
)
PRIORITY_GROUP_KEYS = (
    "worker branch and lane rules",
    "parallel codex workflow",
    "apply routing chain",
    "file placement rules",
    "repo folder ownership map",
    "portal zone model",
)
PROTECTED_BUCKET = "PROTECTED_HUMAN_REVIEW"
CANONICALIZATION_BUCKET = "CANONICALIZATION_REVIEW_CANDIDATE"


@dataclass(frozen=True)
class DecisionPacketBuildResult:
    source_triage_report: str | None
    packets: list[dict[str, Any]]
    index: dict[str, Any]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "canonical_target"


def find_latest_triage_report(repo_root: Path) -> Path | None:
    report_root = repo_root.resolve() / TRIAGE_REPORT_ROOT
    if not report_root.exists():
        return None
    candidates = sorted(
        report_root.glob("canonical_authority_triage_*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _entry_pool(triage_report: dict[str, Any]) -> list[dict[str, Any]]:
    pool: list[dict[str, Any]] = []
    for key in (
        "top_10_next_review_targets",
        "canonicalization_review_candidates",
        "protected_human_review",
        "active_canonical_conflicts",
    ):
        for entry in triage_report.get(key, []):
            if isinstance(entry, dict):
                pool.append(entry)
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for entry in pool:
        group_key = str(entry.get("group_key", ""))
        if not group_key or group_key in seen:
            continue
        seen.add(group_key)
        unique.append(entry)
    return unique


def _priority_rank(entry: dict[str, Any]) -> tuple[int, int, str]:
    group_key = str(entry.get("group_key", "")).lower()
    try:
        priority_index = PRIORITY_GROUP_KEYS.index(group_key)
    except ValueError:
        priority_index = len(PRIORITY_GROUP_KEYS)
    rank = int(entry.get("rank", 999))
    return (priority_index, rank, group_key)


def _selected_entries(triage_report: dict[str, Any]) -> list[dict[str, Any]]:
    pool = _entry_pool(triage_report)
    selected = sorted(pool, key=_priority_rank)
    return selected[:10]


def _is_protected(entry: dict[str, Any]) -> bool:
    return bool(entry.get("protected_review_required")) or entry.get("bucket") == PROTECTED_BUCKET


def _candidate_is_operator_workflow(path: str) -> bool:
    return path.startswith("docs/workflows/")


def _candidate_is_aios_operator(path: str) -> bool:
    return path.startswith("docs/AI_OS/operator/") or path.startswith("docs/AI_OS/operator_workflows/")


def _candidate_is_mixed_dependency(path: str, group_key: str) -> bool:
    lower = path.lower()
    if group_key == "apply routing chain" and "trading" in lower:
        return True
    return any(token in lower for token in ("trading", "broker", "openai_api_bridge", "security/phase_", "audits/phase-"))


def _current_canonical_candidate(entry: dict[str, Any]) -> str | None:
    if _is_protected(entry):
        return None
    paths = [str(path) for path in entry.get("paths", [])]
    group_key = str(entry.get("group_key", "")).lower()
    workflow_candidates = [
        path for path in paths if _candidate_is_operator_workflow(path) and not _candidate_is_mixed_dependency(path, group_key)
    ]
    if workflow_candidates and any(_candidate_is_aios_operator(path) for path in paths):
        return sorted(workflow_candidates)[0]
    non_dependency = [path for path in paths if not _candidate_is_mixed_dependency(path, group_key)]
    return sorted(non_dependency or paths)[0] if paths else None


def _duplicate_candidates(entry: dict[str, Any], current: str | None) -> list[str]:
    return [str(path) for path in entry.get("paths", []) if str(path) != current]


def _risks(entry: dict[str, Any]) -> list[str]:
    risks = [
        "Generated packet is review-only and must not be treated as cleanup approval.",
        "Human owner must confirm canonical authority before any later content change.",
    ]
    if _is_protected(entry):
        risks.append("Protected review required; DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW applies.")
    group_key = str(entry.get("group_key", "")).lower()
    mixed_paths = [path for path in entry.get("paths", []) if _candidate_is_mixed_dependency(str(path), group_key)]
    if mixed_paths:
        risks.append("Mixed or accidental dependency paths detected; do not treat them as canonical candidates.")
    if entry.get("bucket") == CANONICALIZATION_BUCKET:
        risks.append("Cross-location workflow duplicate may contain unique content in both locations.")
    return risks


def _dependencies(entry: dict[str, Any]) -> list[str]:
    group_key = str(entry.get("group_key", "")).lower()
    dependencies = [
        str(path)
        for path in entry.get("paths", [])
        if _candidate_is_mixed_dependency(str(path), group_key)
    ]
    if _is_protected(entry):
        dependencies.append("Human review of protected authority required before any later APPLY packet.")
    return sorted(set(dependencies))


def _keep_reason(entry: dict[str, Any], current: str | None) -> str:
    if _is_protected(entry):
        return "Protected governance/security/authority group; canonical owner must be chosen by human review."
    if current and _candidate_is_operator_workflow(current):
        return "docs/workflows is the likely operator-facing canonical location for workflow authority."
    return "Candidate selected as current best review anchor from non-dependency paths."


def _deprecate_reason(entry: dict[str, Any], current: str | None) -> str:
    duplicates = _duplicate_candidates(entry, current)
    if not duplicates:
        return "No duplicate candidate selected for deprecate review."
    if _is_protected(entry):
        return "Do not deprecate protected authority without human review and a later approved APPLY packet."
    return "Duplicate candidates may be deprecate candidates only after human review confirms no unique authority remains."


def _recommended_next_action(entry: dict[str, Any]) -> str:
    if _is_protected(entry):
        return "DO_NOT_TOUCH_WITHOUT_HUMAN_REVIEW; choose NEEDS_HUMAN_REVIEW or DO_NOT_TOUCH unless a later approved packet scopes changes."
    return "Review packet, select a decision option, and generate a later APPLY packet only after human approval."


def _packet_for_entry(entry: dict[str, Any], source_report: str | None, rank: int) -> dict[str, Any]:
    current = _current_canonical_candidate(entry)
    return {
        "report_type": REPORT_TYPE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executable": False,
        "source_triage_report": source_report,
        "rank": rank,
        "group_key": entry.get("group_key"),
        "bucket": entry.get("bucket"),
        "protected_review_required": _is_protected(entry),
        "paths": entry.get("paths", []),
        "current_canonical_candidate": current,
        "duplicate_candidates": _duplicate_candidates(entry, current),
        "keep_candidate_reason": _keep_reason(entry, current),
        "deprecate_candidate_reason": _deprecate_reason(entry, current),
        "risks": _risks(entry),
        "dependencies": _dependencies(entry),
        "human_decision_required": True,
        "recommended_decision_options": list(DECISION_OPTIONS),
        "recommended_next_action": _recommended_next_action(entry),
    }


def build_decision_packets(repo_root: Path) -> DecisionPacketBuildResult:
    root = repo_root.resolve()
    source_path = find_latest_triage_report(root)
    triage_report = _load_json(source_path)
    source_report = _normalize_path(source_path.relative_to(root)) if source_path else None
    packets = [
        _packet_for_entry(entry, source_report, rank)
        for rank, entry in enumerate(_selected_entries(triage_report), start=1)
    ]
    index = {
        "report_type": INDEX_REPORT_TYPE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executable": False,
        "source_triage_report": source_report,
        "packet_count": len(packets),
        "packets": [
            {
                "rank": packet["rank"],
                "group_key": packet["group_key"],
                "bucket": packet["bucket"],
                "protected_review_required": packet["protected_review_required"],
                "packet_file": f"canonical_decision_packet_{packet['rank']:02d}_{_safe_slug(str(packet['group_key']))}.json",
                "recommended_next_action": packet["recommended_next_action"],
                "executable": False,
            }
            for packet in packets
        ],
        "human_decision_required": True,
        "recommended_next_action": "Review packets and choose decision options; no cleanup is authorized by this index.",
    }
    return DecisionPacketBuildResult(source_report, packets, index, executable=False)


def _resolve_output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output_root = (root / DECISION_PACKET_ROOT).resolve()
    allowed_root = (root / DECISION_PACKET_ROOT).resolve()
    if not (output_root == allowed_root or allowed_root in output_root.parents):
        raise ValueError("Decision packets must be written under Reports/operator_relief/decision_packets/.")
    return output_root


def write_decision_packets(result: DecisionPacketBuildResult, repo_root: Path) -> list[Path]:
    output_root = _resolve_output_root(repo_root)
    output_root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for packet in result.packets:
        filename = f"canonical_decision_packet_{packet['rank']:02d}_{_safe_slug(str(packet['group_key']))}.json"
        path = output_root / filename
        with path.open("w", encoding="utf-8") as handle:
            json.dump(packet, handle, indent=2, sort_keys=True)
            handle.write("\n")
        written.append(path)
    index_path = output_root / "canonical_decision_packet_index.json"
    with index_path.open("w", encoding="utf-8") as handle:
        json.dump(result.index, handle, indent=2, sort_keys=True)
        handle.write("\n")
    written.append(index_path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate canonical authority decision packets.")
    parser.add_argument("--write-packets", action="store_true", help="Write decision packets under Reports/operator_relief/decision_packets/.")
    args = parser.parse_args(argv)
    result = build_decision_packets(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_packets:
        written = write_decision_packets(result, Path.cwd())
        payload["written_files"] = [_normalize_path(path) for path in written]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
