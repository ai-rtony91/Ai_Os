"""Run a deterministic paper learning action router demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.paper_learning_action_router import (
    PAPER_LEARNING_ACTION_READY,
    route_paper_study_journal_to_learning_action,
)
from automation.forex_engine.paper_study_journal import (
    build_paper_study_journal,
    PAPER_STUDY_JOURNAL_READY,
)
from automation.forex_engine.paper_continuity_review import evaluate_decision_for_continuity_review
from automation.forex_engine.paper_risk_decision import evaluate_ledger_for_paper_risk_decision
from automation.forex_engine.paper_signal_intake import build_demo_local_signal, evaluate_local_signal_for_ledger
from automation.forex_engine.readiness import evaluate_paper_readiness, build_valid_mock_signal


def _safe_study_journal() -> dict:
    readiness = evaluate_paper_readiness(build_valid_mock_signal())
    if not readiness["accepted_for_paper"]:
        raise RuntimeError("Sprint 18 readiness fixture must be accepted for study journal.")

    ledger = evaluate_local_signal_for_ledger(
        build_demo_local_signal("sprint_18_journal_signal_001"),
        signal_id="sprint_18_journal_signal_001",
        generated_at_utc="2026-06-12T00:00:00Z",
    )
    decision = evaluate_ledger_for_paper_risk_decision(
        ledger,
        generated_at_utc="2026-06-12T00:00:00Z",
        decision_id="sprint_18_journal_decision_001",
    )
    review = evaluate_decision_for_continuity_review(
        decision,
        generated_at_utc="2026-06-12T00:00:00Z",
        review_id="sprint_18_journal_review_001",
    )
    return build_paper_study_journal(
        review,
        generated_at_utc="2026-06-12T00:00:00Z",
        journal_id="sprint_18_journal_record_001",
    )


def main() -> int:
    journal = _safe_study_journal()
    if journal["journal_status"] != PAPER_STUDY_JOURNAL_READY:
        print(json.dumps(journal, indent=2, sort_keys=True))
        return 1

    result = route_paper_study_journal_to_learning_action(
        journal,
        generated_at_utc="2026-06-12T00:00:00Z",
        router_id="sprint_19_learning_router_record_001",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["route_status"] == PAPER_LEARNING_ACTION_READY and result["execution_allowed"] is False else 1


if __name__ == "__main__":
    raise SystemExit(main())
