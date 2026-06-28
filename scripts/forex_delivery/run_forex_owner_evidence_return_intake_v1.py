"""CLI runner for the owner evidence return intake module."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_owner_evidence_return_intake_v1 as intake_lib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Forex owner evidence return intake")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_OWNER_EVIDENCE_RETURN_INTAKE_V1_REPORT.md",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--include-already-present", action="store_true")
    parser.add_argument(
        "--catalog-path",
        action="append",
        default=None,
        help="catalog path, can be repeated",
    )
    return parser.parse_args()


def _default_catalog_paths(repo_root: Path) -> list[str]:
    return [str(repo_root / "tests\\fixtures\\forex_delivery\\owner_evidence_return_v1")]


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root)
    catalog_paths = args.catalog_path or _default_catalog_paths(repo_root)
    payload = intake_lib.build_owner_evidence_return_intake(
        catalog_payload=None,
        catalog_paths=catalog_paths,
        include_already_present=args.include_already_present,
        strict=args.strict,
    )
    output = (
        json.dumps(intake_lib.intake_to_jsonable_dict(payload), indent=2, sort_keys=True)
        if args.json
        else intake_lib.intake_to_markdown(payload)
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
