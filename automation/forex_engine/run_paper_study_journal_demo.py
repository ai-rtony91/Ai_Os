"""Run a deterministic paper study journal demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.paper_continuity_review import (
    evaluate_decision_for_continuity_review,
)
from automation.forex_engine.paper_risk_decision import (
    evaluate_ledger_for_paper_risk_decision,
)
from automation.forex_engine.paper_signal_intake import (
    build_demo_local_signal,
    evaluate_local_signal_for_ledger,
)
from automation.forex_engine.paper_study_journal import (
    PAPER_STUDY_JOURNAL_READY,
    build_paper_study_journal,
)
from automation.forex_engine.readiness import (
    evaluate_paper_readiness,
    build_valid_mock_signal,
)


def main() -> int:
    """Run the Sprint 18 paper study journal chain with deterministic fixture data."""
    readiness = evaluate_paper_readiness(build_valid_mock_signal())
    if not readiness["accepted_for_paper"]:
        print(json.dumps(readiness, indent=2, sort_keys=True))
        return 1

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
    journal = build_paper_study_journal(
        review,
        generated_at_utc="2026-06-12T00:00:00Z",
        journal_id="sprint_18_journal_record_001",
    )

    print(json.dumps(journal, indent=2, sort_keys=True))
    return (
        0
        if journal["journal_status"] == PAPER_STUDY_JOURNAL_READY and journal["execution_allowed"] is False
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
