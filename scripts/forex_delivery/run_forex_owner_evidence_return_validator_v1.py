"""CLI runner for the owner evidence return validator module."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_owner_evidence_return_validator_v1 as validator_lib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Forex owner evidence return payloads",
    )
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--min-sample", type=int, default=30)
    parser.add_argument(
        "--evidence-path",
        action="append",
        default=None,
        help="Evidence file path; can be repeated",
    )
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_OWNER_EVIDENCE_RETURN_VALIDATOR_V1_REPORT.md",
    )
    return parser.parse_args()


def _default_evidence_paths(repo_root: Path) -> list[str]:
    base = repo_root / "tests\\fixtures\\forex_delivery\\owner_evidence_return_v1"
    return [str(path) for path in sorted(base.glob("*.md"))[:8]]


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root)
    evidence_paths = args.evidence_path or _default_evidence_paths(repo_root)
    payload = validator_lib.validate_owner_evidence_return_files(
        evidence_paths,
        strict=args.strict,
        min_sample=args.min_sample,
    )
    output = (
        json.dumps(validator_lib.result_to_jsonable_dict(payload), indent=2, sort_keys=True)
        if args.json
        else validator_lib.result_to_markdown(payload)
    )
    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = (repo_root / report_path).resolve()
    if args.write_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
