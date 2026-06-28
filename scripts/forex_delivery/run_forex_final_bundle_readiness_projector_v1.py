"""CLI wrapper for final bundle readiness projection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_evidence_quality_validator_v1 as quality
from automation.forex_engine import (
    forex_missing_evidence_catalog_v1 as catalog_lib,
    forex_review_ready_candidate_selector_v1 as selector_lib,
)
from automation.forex_engine.forex_final_bundle_readiness_projector_v1 import (
    project_final_bundle_readiness,
    readiness_to_jsonable_dict,
    readiness_to_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Project final Forex bundle readiness")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_FINAL_BUNDLE_READINESS_PROJECTOR_V1_REPORT.md",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _payloads(repo_root: Path, *, strict: bool) -> tuple[dict, dict, dict]:
    catalog = catalog_lib.build_missing_evidence_catalog(
        explicit_records=[{"name": "candidate evidence", "classification": "ALREADY_PRESENT"}],
    )
    quality_result = quality.validate_evidence_bundle(
        [repo_root / "tests\\fixtures\\forex_delivery\\remaining_closure_v1\\evidence_bundle_clean.md"],
        strict=strict,
    )
    selector_result = selector_lib.select_review_ready_candidate(
        [
            {"candidate_id":"review-ready","evidence_completeness":0.95,"sample_count":120,"expectancy":1.5,"profit_factor":1.8,"drawdown":0.1}
            ],
            strict=strict,
    )
    return catalog, quality_result, selector_result


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root)
    catalog, quality_result, selector_result = _payloads(repo_root, strict=args.strict)
    projection = project_final_bundle_readiness(catalog, quality_result, selector_result)
    output = (
        json.dumps(readiness_to_jsonable_dict(projection), indent=2, sort_keys=True)
        if args.json
        else readiness_to_markdown(projection)
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
