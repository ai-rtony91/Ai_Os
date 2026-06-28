"""CLI runner for final review decision orchestration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_final_review_decision_orchestrator_v1 as orchestrator_lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Forex final review decision orchestration")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_FINAL_REVIEW_DECISION_ORCHESTRATOR_V1_REPORT.md",
    )
    parser.add_argument(
        "--checkpoint-report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_FINAL_REVIEW_DECISION_ORCHESTRATOR_V1_CHECKPOINT.md",
    )
    parser.add_argument("--path", action="append", default=None, help="Optional final decision evidence paths")
    return parser.parse_args(argv)


def run_cli(argv: list[str] | None = None) -> str:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    paths = args.path
    if paths is None:
        paths = [str(repo_root / "tests\\fixtures\\forex_delivery\\final_review_decision_gate_v1")]
    result = orchestrator_lib.run_final_review_decision_orchestration(
        repo_root=repo_root,
        evidence_paths=[Path(path) for path in paths],
        strict=args.strict,
    )
    if args.json:
        output = json.dumps(orchestrator_lib.final_review_decision_orchestration_to_jsonable_dict(result), indent=2, sort_keys=True)
    else:
        output = orchestrator_lib.final_review_decision_orchestration_to_markdown(result)

    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = (repo_root / report_path).resolve()
    if args.write_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")

        checkpoint = orchestrator_lib.final_review_decision_orchestration_to_jsonable_dict(result)["checkpoint_ledger"]
        checkpoint_path = Path(args.checkpoint_report_path)
        if not checkpoint_path.is_absolute():
            checkpoint_path = (repo_root / checkpoint_path).resolve()
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True), encoding="utf-8")
    return output


def main() -> None:
    print(run_cli())


if __name__ == "__main__":
    main()
