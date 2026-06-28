"""CLI wrapper for review-ready candidate selection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_review_ready_candidate_selector_v1 import (
    candidate_selector_to_jsonable_dict,
    candidate_selector_to_markdown,
    select_review_ready_candidate,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select review-ready Forex candidate")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1_REPORT.md",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--candidate-path", action="append", default=None)
    return parser.parse_args(argv)


def _candidate_defaults() -> list[dict]:
    return [
        {
            "candidate_id": "review-ready-strong",
            "strategy": "sample_strategy",
            "symbol": "EUR_USD",
            "review_ready": True,
            "gate_status": "PASSED",
            "evidence_depth_score": 0.95,
            "statistical_profit_score": 0.96,
            "profit_factor": 1.8,
            "expectancy": 0.4,
            "max_drawdown": 0.03,
            "sample_size": 80,
            "risk_score": 0.9,
            "recency_score": 0.8,
        },
        {
            "candidate_id": "review-ready-weaker",
            "strategy": "sample_strategy",
            "symbol": "EUR_USD",
            "review_ready": True,
            "gate_status": "PASSED",
            "evidence_depth_score": 0.72,
            "statistical_profit_score": 0.70,
            "profit_factor": 1.4,
            "expectancy": 0.2,
            "max_drawdown": 0.05,
            "sample_size": 50,
            "risk_score": 0.6,
            "recency_score": 0.5,
        },
    ]


def _payload_to_candidates(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("candidates"), list):
            return [item for item in payload["candidates"] if isinstance(item, dict)]
        return [payload]
    return []


def _load_candidates(repo_root: Path, paths: list[str] | None, input_path: str | None) -> list[dict]:
    if input_path:
        payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
        return _payload_to_candidates(payload)
    if paths:
        selected = [Path(path) for path in paths]
        payloads: list[dict] = []
        for file_path in selected:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            payloads.extend(_payload_to_candidates(payload))
        return payloads
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
        if Path(file_path).exists():
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            payloads.extend(_payload_to_candidates(payload))
    return [*_candidate_defaults(), *payloads]


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None) -> int:
    args = parse_args(argv)
    out = stdout if stdout is not None else sys.stdout
    repo_root = Path(args.repo_root)
    candidates = _load_candidates(repo_root, args.candidate_path, args.input)
    result = select_review_ready_candidate(candidates, strict=args.strict)
    json_output = json.dumps(candidate_selector_to_jsonable_dict(result), indent=2, sort_keys=True)
    markdown_output = candidate_selector_to_markdown(result)
    output = markdown_output if args.markdown else json_output
    report = Path(args.report_path)
    if not report.is_absolute():
        report = (repo_root / report).resolve()
    if args.write_report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(markdown_output, encoding="utf-8")
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = (repo_root / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_output, encoding="utf-8")
    out.write(output)
    if not output.endswith("\n"):
        out.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
