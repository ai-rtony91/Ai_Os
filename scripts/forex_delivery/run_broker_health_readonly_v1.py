"""Run the local-only AIOS Forex broker health read-only engine V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.broker_health_readonly_v1 import (  # noqa: E402
    build_sample_snapshot,
    evaluate_broker_health_readonly,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Broker Health Read-Only V1 sample.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--blocked", action="store_true", help="Use a deterministic blocked sample.")
    args = parser.parse_args(argv)

    snapshot = build_sample_snapshot()
    if args.blocked:
        snapshot["snapshot_age_minutes"] = 99
    result = evaluate_broker_health_readonly(snapshot)
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
