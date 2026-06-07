"""Export DRY_RUN-only human review queue items as markdown packets."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_TYPE = "operator_relief_human_review_packet_export_v1"
QUEUE_PATH = Path("Reports/operator_relief/human_review_queue/human_review_queue.json")
OUTPUT_ROOT = Path("Reports/operator_relief/human_review_packets")
DECISION_OPTIONS = (
    "KEEP_CANONICAL_AS_IS",
    "MERGE_DUPLICATE_INTO_CANONICAL_LATER",
    "KEEP_BOTH_WITH_SCOPE_NOTE",
    "PARK_UNTIL_GOVERNANCE_REVIEW",
    "MARK_DEPENDENCY_ONLY",
)


@dataclass(frozen=True)
class PacketExportResult:
    report_type: str
    generated_at: str
    executable: bool
    source_human_review_queue: str
    packets: list[dict[str, Any]]
    packet_count: int
    safe_cleanup_paths: list[str]
    apply_ready_paths: list[str]
    safety: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "review_item"


def _item_label(item: dict[str, Any]) -> str:
    return str(item.get("group_key") or item.get("path") or f"item_{item.get('rank', 'unknown')}")


def _item_id(item: dict[str, Any]) -> str:
    rank = int(item.get("rank", 0))
    return f"HRQ-{rank:03d}-{_slug(_item_label(item))}"


def _severity(item: dict[str, Any]) -> str:
    queue_type = item.get("queue_type")
    if queue_type == "PROTECTED_AUTHORITY":
        return "HIGH"
    if queue_type == "WORKFLOW_AUTHORITY_CONFLICT":
        return "MEDIUM"
    return "LOW"


def _authority_type(item: dict[str, Any]) -> str:
    queue_type = str(item.get("queue_type", ""))
    if queue_type == "PROTECTED_AUTHORITY":
        return "PROTECTED_AUTHORITY"
    if queue_type == "WORKFLOW_AUTHORITY_CONFLICT":
        return "WORKFLOW_AUTHORITY_CONFLICT"
    if queue_type == "NON_CANONICAL_DEPENDENCY":
        return "NON_CANONICAL_DEPENDENCY"
    return "DEPENDENCY_OR_EVIDENCE"


def _files_involved(item: dict[str, Any]) -> list[str]:
    paths = item.get("paths")
    if isinstance(paths, list):
        return [str(path) for path in paths if isinstance(path, str)]
    path = item.get("path")
    return [str(path)] if isinstance(path, str) else []


def _blocked_actions(item: dict[str, Any]) -> list[str]:
    actions = [
        "cleanup",
        "canonicalize",
        "generate APPLY packet",
        "delete",
        "move",
        "rename",
        "rewrite",
        "commit",
        "push",
    ]
    if item.get("queue_type") == "PROTECTED_AUTHORITY":
        actions.insert(0, "touch without human review")
    return actions


def _packet_metadata(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": _item_id(item),
        "category": item.get("queue_type"),
        "severity": _severity(item),
        "authority_type": _authority_type(item),
        "files_involved": _files_involved(item),
        "reason_human_review_required": item.get("reason"),
        "blocked_actions": _blocked_actions(item),
        "dependency_classification": item.get("classification"),
        "safety_flags": {
            "executable": False,
            "dry_run_only": True,
            "cleanup_approved": False,
            "canonicalization_approved": False,
            "apply_packet_generated": False,
            "apply_ready": False,
        },
        "recommended_human_decision_options": list(DECISION_OPTIONS),
    }


def _markdown_for_packet(metadata: dict[str, Any]) -> str:
    files = "\n".join(f"- `{path}`" for path in metadata["files_involved"]) or "- None recorded"
    blocked = "\n".join(f"- {action}" for action in metadata["blocked_actions"])
    options = "\n".join(f"- {option}" for option in metadata["recommended_human_decision_options"])
    safety = "\n".join(f"- `{key}`: `{str(value).lower()}`" for key, value in metadata["safety_flags"].items())
    dependency = metadata.get("dependency_classification") or "N/A"
    return (
        f"# Human Review Packet: {metadata['item_id']}\n\n"
        "```json\n"
        "{\n"
        '  "executable": false\n'
        "}\n"
        "```\n\n"
        f"- Item ID: `{metadata['item_id']}`\n"
        f"- Category: `{metadata['category']}`\n"
        f"- Severity: `{metadata['severity']}`\n"
        f"- Authority type: `{metadata['authority_type']}`\n"
        f"- Dependency classification: `{dependency}`\n\n"
        "## Files Involved\n\n"
        f"{files}\n\n"
        "## Reason Human Review Is Required\n\n"
        f"{metadata.get('reason_human_review_required') or 'Human review required by queue status.'}\n\n"
        "## Blocked Actions\n\n"
        f"{blocked}\n\n"
        "## Safety Flags\n\n"
        f"{safety}\n\n"
        "## Recommended Human Decision Options\n\n"
        f"{options}\n"
    )


def build_packets(repo_root: Path) -> PacketExportResult:
    root = repo_root.resolve()
    queue = _load_json(root / QUEUE_PATH)
    queue_items = [item for item in queue.get("queue_items", []) if isinstance(item, dict)]
    packets: list[dict[str, Any]] = []
    for item in queue_items:
        metadata = _packet_metadata(item)
        filename = f"{metadata['item_id']}.md"
        packets.append(
            {
                "item_id": metadata["item_id"],
                "filename": filename,
                "output_path": _normalize_path(OUTPUT_ROOT / filename),
                "executable": False,
                "metadata": metadata,
                "markdown": _markdown_for_packet(metadata),
            }
        )
    return PacketExportResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_human_review_queue=_normalize_path(QUEUE_PATH),
        packets=packets,
        packet_count=len(packets),
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "cleanup_approved": False,
            "canonicalization_approved": False,
            "apply_packet_generated": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
    )


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed or allowed in output.parents):
        raise ValueError("Human review packets must be written under Reports/operator_relief/human_review_packets/.")
    return output


def write_packets(result: PacketExportResult, repo_root: Path) -> list[Path]:
    output = _output_root(repo_root)
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for packet in result.packets:
        filename = str(packet["filename"])
        path = output / filename
        path.write_text(str(packet["markdown"]), encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export DRY_RUN-only human review packets.")
    parser.add_argument("--write-packets", action="store_true", help="Write markdown packets under Reports/operator_relief/human_review_packets/.")
    args = parser.parse_args(argv)
    result = build_packets(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if args.write_packets:
        payload["written_files"] = [_normalize_path(path) for path in write_packets(result, Path.cwd())]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
