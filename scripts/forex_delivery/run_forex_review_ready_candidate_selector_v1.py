"""CLI wrapper for review-ready candidate selection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_review_ready_candidate_selector_v1 import (
    candidate_selector_to_jsonable_dict,
    candidate_selector_to_markdown,
    select_review_ready_candidate,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select review-ready Forex candidate")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1_REPORT.md",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--candidate-path", action="append", default=None)
    return parser.parse_args()


def _load_candidates(repo_root: Path, paths: list[str] | None) -> list[dict]:
    if paths:
        selected = [Path(path) for path in paths]
    else:
        base = repo_root / "tests\\fixtures\\forex_delivery\\remaining_closure_v1"
        selected = [
            base / "candidate_complete_review_ready.json",
            base / "candidate_negative_expectancy.json",
            base / "candidate_low_sample.json",
            base / "candidate_high_drawdown.json",
            base / "candidate_low_profit_factor.json",
        ]
    payloads: list[dict] = []
    for file_path in selected:
        payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
        if isinstance(payload, list):
            payloads.extend(payload)
        elif isinstance(payload, dict):
            payloads.append(payload)
    return payloads


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root)
    candidates = _load_candidates(repo_root, args.candidate_path)
    result = select_review_ready_candidate(candidates, strict=args.strict)
    output = (
        json.dumps(candidate_selector_to_jsonable_dict(result), indent=2, sort_keys=True)
        if args.json
        else candidate_selector_to_markdown(result)
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
