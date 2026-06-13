"""Run a deterministic paper continuity review demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.paper_continuity_review import (
    PAPER_REVIEW_READY,
    evaluate_decision_for_continuity_review,
)
from automation.forex_engine.paper_signal_intake import build_demo_local_signal, evaluate_local_signal_for_ledger
from automation.forex_engine.paper_risk_decision import evaluate_ledger_for_paper_risk_decision
from automation.forex_engine.readiness import evaluate_paper_readiness, build_valid_mock_signal


def main() -> int:
    readiness = evaluate_paper_readiness(build_valid_mock_signal())
    if not readiness["accepted_for_paper"]:
        return 1

    ledger = evaluate_local_signal_for_ledger(
        build_demo_local_signal("continuity_demo_signal_001"),
        signal_id="continuity_demo_signal_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )
    decision = evaluate_ledger_for_paper_risk_decision(ledger)
    result = evaluate_decision_for_continuity_review(decision)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["review_status"] == PAPER_REVIEW_READY and result["execution_allowed"] is False else 1


if __name__ == "__main__":
    raise SystemExit(main())
