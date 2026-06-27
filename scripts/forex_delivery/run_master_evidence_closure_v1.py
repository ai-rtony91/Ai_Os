"""Run the local-only AIOS Forex master evidence closure V1."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.master_evidence_closure_v1 import (  # noqa: E402
    DEFAULT_REPORT_PATH,
    build_master_evidence_closure,
    result_to_jsonable_dict,
    result_to_operator_text,
    write_master_evidence_closure_report,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run AIOS Forex master evidence closure.")
    parser.add_argument("--report-root", default="Reports/forex_delivery")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--validation-result", action="append", default=[])
    args = parser.parse_args(argv)

    result = build_master_evidence_closure(
        args.report_root,
        ROOT,
        metadata=_git_metadata(),
        validation_results=list(args.validation_result),
    )
    if args.write_report:
        write_master_evidence_closure_report(result, args.report_path)
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result))
    return 0


def _git_metadata() -> dict[str, str]:
    return {
        "branch": _git("branch", "--show-current"),
        "base_commit": _git("rev-parse", "origin/main"),
        "current_commit": _git("rev-parse", "HEAD"),
        "pr_baseline": _git("log", "--oneline", "-n", "1", "origin/main"),
    }


def _git(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "UNKNOWN"
    if completed.returncode != 0:
        return "UNKNOWN"
    return completed.stdout.strip() or "UNKNOWN"


if __name__ == "__main__":
    raise SystemExit(main())
