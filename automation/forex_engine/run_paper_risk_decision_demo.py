"""Run a deterministic local paper risk decision router demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.paper_risk_decision import (
    evaluate_ledger_for_paper_risk_decision,
)
from automation.forex_engine.paper_signal_intake import build_demo_local_signal, evaluate_local_signal_for_ledger


def main() -> int:
    ledger = evaluate_local_signal_for_ledger(build_demo_local_signal())
    result = evaluate_ledger_for_paper_risk_decision(ledger)
    print(json.dumps(result, indent=2, sort_keys=True))
    return (
        0
        if result["decision"] == "PAPER_ACCEPT" and result["execution_allowed"] is False
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
