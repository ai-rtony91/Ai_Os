"""Run the local-only AIOS Forex closure integration bridge V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_closure_integration_bridge_v1 import (  # noqa: E402
    build_sample_integration_input,
    result_to_jsonable_dict,
    result_to_operator_text,
    run_forex_closure_integration_bridge,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Forex Closure Integration Bridge V1 sample.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--blocked", action="store_true", help="Use deterministic blocked sample.")
    args = parser.parse_args(argv)

    payload = build_sample_integration_input()
    if args.blocked:
        payload["operator_halt_state"]["halt_requested"] = True
    result = run_forex_closure_integration_bridge(payload)
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
