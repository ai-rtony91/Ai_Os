"""Run deterministic AIOS Forex replay evidence intake."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.replay_evidence_intake_v1 import (  # noqa: E402
    intake_replay_evidence,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run AIOS Forex replay evidence intake.")
    parser.add_argument("--report-root", default="Reports/forex_delivery")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = intake_replay_evidence(args.report_root)
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
