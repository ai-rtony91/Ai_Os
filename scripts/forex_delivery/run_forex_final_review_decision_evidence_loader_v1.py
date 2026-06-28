"""CLI runner for final review decision evidence loader."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_final_review_decision_evidence_loader_v1 as loader_lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load Forex final review evidence")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_FINAL_REVIEW_DECISION_EVIDENCE_LOADER_V1_REPORT.md",
    )
    parser.add_argument(
        "--evidence-path",
        action="append",
        default=None,
        help="Optional file/folder path for evidence records",
    )
    return parser.parse_args(argv)


def run_cli(argv: list[str] | None = None) -> str:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    default_paths = [repo_root / "tests\\fixtures\\forex_delivery\\final_review_decision_gate_v1"]
    evidence_paths = [Path(path) for path in (args.evidence_path or default_paths)]

    payload = loader_lib.load_final_review_evidence_paths(
        evidence_paths,
        strict=args.strict,
        source_family="final_review_decision_gate_v1",
    )
    output = (
        json.dumps(loader_lib.final_review_evidence_to_jsonable_dict(payload), indent=2, sort_keys=True)
        if args.json
        else loader_lib.final_review_evidence_to_markdown(payload)
    )
    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = (repo_root / report_path).resolve()
    if args.write_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
    return output


def main() -> None:
    run_cli()


if __name__ == "__main__":
    print(run_cli())
