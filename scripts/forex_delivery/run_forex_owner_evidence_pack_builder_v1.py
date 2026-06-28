"""CLI wrapper for owner evidence pack generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_missing_evidence_catalog_v1 import build_missing_evidence_catalog
from automation.forex_engine.forex_owner_evidence_pack_builder_v1 import (
    build_owner_evidence_pack,
    owner_pack_to_jsonable_dict,
    owner_pack_to_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Forex owner evidence pack")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_OWNER_EVIDENCE_PACK_V1.md",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--include-templates", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = build_missing_evidence_catalog()
    pack = build_owner_evidence_pack(
        catalog,
        strict=args.strict,
        include_templates=args.include_templates,
    )
    output = (
        json.dumps(owner_pack_to_jsonable_dict(pack), indent=2, sort_keys=True)
        if args.json
        else owner_pack_to_markdown(pack)
    )
    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = (Path(args.repo_root) / report_path).resolve()
    if args.write_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
