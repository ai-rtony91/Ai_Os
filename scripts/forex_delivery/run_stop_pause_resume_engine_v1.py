"""Run the local-only AIOS Forex stop/pause/resume engine V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.broker_health_readonly_v1 import build_sample_snapshot, evaluate_broker_health_readonly  # noqa: E402
from automation.forex_engine.profitability_evidence_v1 import (  # noqa: E402
    build_sample_closed_trades,
    build_sample_replay_summaries,
    build_sample_thresholds,
    build_sample_walk_forward_summaries,
    evaluate_profitability_evidence,
)
from automation.forex_engine.risk_budget_engine_v1 import build_sample_candidate, build_sample_risk_caps, evaluate_risk_budget  # noqa: E402
from automation.forex_engine.stop_pause_resume_engine_v1 import (  # noqa: E402
    build_sample_dashboard_state,
    build_sample_operator_halt_state,
    evaluate_stop_pause_resume,
    result_to_jsonable_dict,
    result_to_operator_text,
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stop/Pause/Resume Engine V1 sample.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--halt", action="store_true", help="Use deterministic operator halt sample.")
    args = parser.parse_args(argv)

    halt = build_sample_operator_halt_state()
    if args.halt:
        halt["halt_requested"] = True
        halt["operator_reason"] = "sample halt"
    result = evaluate_stop_pause_resume(
        evaluate_risk_budget(build_sample_candidate(), build_sample_risk_caps()),
        evaluate_broker_health_readonly(build_sample_snapshot()),
        evaluate_profitability_evidence(
            build_sample_closed_trades(),
            build_sample_replay_summaries(),
            build_sample_walk_forward_summaries(),
            build_sample_thresholds(),
        ),
        build_sample_dashboard_state(),
        halt,
    )
    out = stdout if stdout is not None else sys.stdout
    if args.json:
        json.dump(result_to_jsonable_dict(result), out, indent=2, sort_keys=True)
        out.write("\n")
    else:
        out.write(result_to_operator_text(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
