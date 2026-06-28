"""CLI wrapper for Forex evidence quality validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_evidence_quality_validator_v1 import (
    quality_result_to_jsonable_dict,
    quality_result_to_markdown,
    validate_evidence_bundle,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Forex evidence quality")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_EVIDENCE_QUALITY_VALIDATOR_V1_REPORT.md",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--evidence-path",
        action="append",
        default=None,
        help="Path to evidence file; repeat for multiple files",
    )
    return parser.parse_args()


def _default_targets(repo_root: Path) -> list[str]:
    base = repo_root / "tests\\fixtures\\forex_delivery\\remaining_closure_v1"
    return [
        str(base / "evidence_bundle_clean.md"),
        str(base / "evidence_bundle_missing_sections.md"),
        str(base / "evidence_bundle_broker_command_rejected.md"),
        str(base / "evidence_bundle_insufficient_sample.md"),
        str(base / "evidence_bundle_sensitive_marker_rejected.md"),
    ]


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root)
    targets = args.evidence_path or _default_targets(repo_root)
    result = validate_evidence_bundle(targets, strict=args.strict)
    output = (
        json.dumps(quality_result_to_jsonable_dict(result), indent=2, sort_keys=True)
        if args.json
        else quality_result_to_markdown(result)
    )
    report = Path(args.report_path)
    if not report.is_absolute():
        report = (repo_root / report).resolve()
    if args.write_report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
