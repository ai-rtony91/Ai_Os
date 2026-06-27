from __future__ import annotations

"""CLI runner for AIOS AEE governance validator V1."""

from pathlib import Path
import argparse
import json
import sys

from automation.governance.aios_aee_governance_validator_v1 import (
    build_aee_governance_validation,
    result_to_jsonable_dict,
    result_to_markdown,
    result_to_operator_text,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run AIOS AEE governance validator and produce deterministic output."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--write-report", action="store_true", help="Write markdown report.")
    parser.add_argument(
        "--report-path",
        default="Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md",
        help="Optional explicit report output path.",
    )
    parser.add_argument("--json", action="store_true", help="Write JSON output.")
    parser.add_argument("--strict", action="store_true", help="Nonzero exit on fail.")
    return parser.parse_args()


def run_validation(repo_root: Path, *, strict: bool, json_output: bool, write_report: bool, report_path: str) -> int:
    result = build_aee_governance_validation(repo_root)
    if json_output:
        print(json.dumps(result_to_jsonable_dict(result), sort_keys=True))
    else:
        print(result_to_operator_text(result))
    if write_report:
        report = Path(report_path)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(result_to_markdown(result), encoding="utf-8")
    if strict:
        return 0 if result.status == "PASS" else 1
    return 0


def main() -> int:
    args = _parse_args()
    return run_validation(
        Path(args.repo_root),
        strict=args.strict,
        json_output=args.json,
        write_report=args.write_report,
        report_path=args.report_path,
    )


if __name__ == "__main__":
    sys.exit(main())
