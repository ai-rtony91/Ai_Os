"""Generate blank DRY_RUN-only human review decision templates."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.operator_relief.human_review_decision_schema import PACKET_ROOT
from automation.operator_relief.human_review_packet_exporter import DECISION_OPTIONS


REPORT_TYPE = "operator_relief_human_review_decision_template_generator_v1"
OUTPUT_ROOT = Path("Reports/operator_relief/human_review_decisions/templates")


@dataclass(frozen=True)
class HumanReviewDecisionTemplateResult:
    report_type: str
    generated_at: str
    executable: bool
    source_human_review_packets: str
    output_root: str
    templates: list[dict[str, Any]]
    templates_generated_count: int
    safe_cleanup_paths: list[str]
    apply_ready_paths: list[str]
    safety: dict[str, Any]
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./")


def _packet_files(repo_root: Path) -> list[Path]:
    packet_root = repo_root / PACKET_ROOT
    if not packet_root.exists():
        return []
    return sorted(path for path in packet_root.glob("*.md") if path.is_file())


def _template_payload(packet_path: Path) -> dict[str, Any]:
    item_id = packet_path.stem
    return {
        "packet_id": item_id,
        "item_id": item_id,
        "reviewer": "",
        "decision": "",
        "rationale": "",
        "allowed_decisions": list(DECISION_OPTIONS),
        "cleanup_approved": False,
        "canonicalization_approved": False,
        "apply_packet_generated": False,
        "executable": False,
        "safe_cleanup_paths": [],
        "apply_ready_paths": [],
    }


def build_templates(repo_root: Path) -> HumanReviewDecisionTemplateResult:
    root = repo_root.resolve()
    templates: list[dict[str, Any]] = []
    for packet_path in _packet_files(root):
        payload = _template_payload(packet_path)
        output_path = OUTPUT_ROOT / f"{payload['item_id']}.json"
        templates.append(
            {
                "packet_path": _normalize_path(packet_path.relative_to(root)),
                "output_path": _normalize_path(output_path),
                "template": payload,
                "executable": False,
            }
        )

    return HumanReviewDecisionTemplateResult(
        report_type=REPORT_TYPE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
        source_human_review_packets=_normalize_path(PACKET_ROOT),
        output_root=_normalize_path(OUTPUT_ROOT),
        templates=templates,
        templates_generated_count=len(templates),
        safe_cleanup_paths=[],
        apply_ready_paths=[],
        safety={
            "executable": False,
            "dry_run_only": True,
            "blank_templates_only": True,
            "decisions_selected": False,
            "approvals_created": False,
            "approvals_inferred": False,
            "cleanup_approved": False,
            "canonicalization_approved": False,
            "apply_packet_generated": False,
            "safe_cleanup_paths_empty": True,
            "apply_ready_paths_empty": True,
        },
        recommended_next_action=(
            "A human reviewer may copy a template, fill reviewer, decision, and rationale, "
            "then submit it through the intake validator; these templates do not approve action."
        ),
    )


def _output_root(repo_root: Path) -> Path:
    root = repo_root.resolve()
    output = (root / OUTPUT_ROOT).resolve()
    allowed_root = (root / OUTPUT_ROOT).resolve()
    if not (output == allowed_root or allowed_root in output.parents):
        raise ValueError("Human review decision templates must be written under Reports/operator_relief/human_review_decisions/templates/.")
    return output


def write_templates(result: HumanReviewDecisionTemplateResult, repo_root: Path) -> list[Path]:
    output_root = _output_root(repo_root)
    output_root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for item in result.templates:
        template = item["template"]
        path = output_root / f"{template['item_id']}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(template, handle, indent=2, sort_keys=True)
            handle.write("\n")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate blank DRY_RUN-only human review decision templates.")
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print template summary without writing files.",
    )
    args = parser.parse_args(argv)
    result = build_templates(Path.cwd())
    payload: dict[str, Any] = result.to_dict()
    if not args.no_write:
        payload["written_files"] = [_normalize_path(path) for path in write_templates(result, Path.cwd())]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
