from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_review_ready_candidate_selector_v1 as selector
from scripts.forex_delivery import run_forex_review_ready_candidate_selector_v1 as runner


RUNNER = (
    ROOT
    / "scripts"
    / "forex_delivery"
    / "run_forex_review_ready_candidate_selector_v1.py"
)


def candidate(candidate_id: str, **overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "candidate_id": candidate_id,
        "strategy": "sample_strategy",
        "symbol": "EUR_USD",
        "direction": "LONG",
        "review_ready": True,
        "gate_status": "PASSED",
        "evidence_depth_score": 0.75,
        "statistical_profit_score": 0.70,
        "profit_factor": 1.50,
        "expectancy": 0.20,
        "max_drawdown": 0.030,
        "sample_size": 50,
        "risk_score": 0.60,
        "recency_score": 0.50,
        "proof_flags": {},
    }
    base.update(overrides)
    return base


def test_selects_highest_scoring_review_ready_candidate() -> None:
    result = selector.select_review_ready_candidate(
        [
            candidate("weaker", statistical_profit_score=0.65, evidence_depth_score=0.70),
            candidate("stronger", statistical_profit_score=0.90, evidence_depth_score=0.95),
        ]
    )

    assert result["selected"] is True
    assert result["selected_candidate_id"] == "stronger"
    assert result["ranking"][0]["candidate_id"] == "stronger"


def test_rejects_blocked_candidates() -> None:
    result = selector.select_review_ready_candidate(
        [
            candidate("blocked", blocked=True),
            candidate("safe", statistical_profit_score=0.80),
        ]
    )

    assert result["selected_candidate_id"] == "safe"
    assert "candidate is explicitly blocked" in result["rejection_reasons"]["blocked"]


def test_rejects_candidates_with_reject_block_fail_not_ready_statuses() -> None:
    result = selector.select_review_ready_candidate(
        [
            candidate("reject", gate_status="GATE_REJECTED"),
            candidate("block", readiness_status="BLOCKED_BY_EVIDENCE"),
            candidate("fail", gate_status="FAILED_PROOF"),
            candidate("not-ready", readiness_status="NOT_READY"),
        ]
    )

    assert result["selected"] is False
    assert set(result["rejection_reasons"]) == {
        "block",
        "fail",
        "not-ready",
        "reject",
    }


def test_rejects_missing_sample_size() -> None:
    result = selector.select_review_ready_candidate([candidate("missing", sample_size=None)])

    assert result["selected"] is False
    assert "sample_size is missing" in result["rejection_reasons"]["missing"]


def test_rejects_missing_evidence_depth() -> None:
    result = selector.select_review_ready_candidate(
        [candidate("missing", evidence_depth_score=None)]
    )

    assert result["selected"] is False
    assert "evidence_depth_score is missing" in result["rejection_reasons"]["missing"]


def test_deterministic_tie_breaker_by_candidate_id() -> None:
    result = selector.select_review_ready_candidate(
        [candidate("b-candidate"), candidate("a-candidate")]
    )

    assert result["ranking"][0]["total_score"] == result["ranking"][1]["total_score"]
    assert result["selected_candidate_id"] == "a-candidate"


def test_min_score_prevents_weak_selection() -> None:
    result = selector.select_review_ready_candidate(
        [candidate("weak", statistical_profit_score=0.10, evidence_depth_score=0.10)],
        min_score=100.0,
    )

    assert result["selected"] is False
    assert result["selected_candidate_id"] is None
    assert "weak" in result["rejection_reasons"]


def test_no_candidates_returns_safe_no_selection() -> None:
    result = selector.select_review_ready_candidate([])

    assert result["selected"] is False
    assert result["selected_candidate_id"] is None
    assert result["eligible_count"] == 0
    assert result["execution_allowed"] is False


def test_invalid_candidate_list_returns_safe_no_selection() -> None:
    result = selector.select_review_ready_candidate(None)  # type: ignore[arg-type]

    assert result["selected"] is False
    assert result["rejection_reasons"]["input"]
    assert result["trade_action_allowed"] is False


def test_result_always_blocks_broker_trade_and_production_actions() -> None:
    result = selector.select_review_ready_candidate([candidate("ready")])

    assert set(selector.BLOCKED_ACTIONS).issubset(set(result["blocked_actions"]))
    assert result["broker_access_allowed"] is False
    assert result["credential_access_allowed"] is False
    assert result["account_access_allowed"] is False
    assert result["trade_action_allowed"] is False
    assert result["live_trade_allowed"] is False
    assert result["demo_trade_allowed"] is False
    assert result["paper_trade_allowed"] is False
    assert result["production_activation_allowed"] is False


def test_selector_does_not_require_broker_or_oanda_imports() -> None:
    source = Path(selector.__file__).read_text(encoding="utf-8").lower()

    assert "import broker" not in source
    assert "from broker" not in source
    assert "import oanda" not in source
    assert "from oanda" not in source
    assert not [
        name
        for name in sys.modules
        if name.startswith("broker") or name.startswith("oanda")
    ]


def test_cli_runs_with_sample_data_and_returns_json() -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["selector_version"] == selector.SELECTOR_VERSION
    assert payload["selected_candidate_id"] == "review-ready-strong"
    assert payload["execution_allowed"] is False


def test_cli_supports_input_file_with_candidates_key(tmp_path: Path) -> None:
    input_file = tmp_path / "candidates.json"
    input_file.write_text(
        json.dumps({"candidates": [candidate("from-file")]}),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--input", str(input_file)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["selected_candidate_id"] == "from-file"


def test_cli_output_file_writes_only_when_explicitly_supplied(tmp_path: Path) -> None:
    stdout = io.StringIO()
    exit_code = runner.main([], stdout=stdout)

    assert exit_code == 0
    assert not list(tmp_path.iterdir())

    output_file = tmp_path / "selector_output.json"
    stdout = io.StringIO()
    exit_code = runner.main(["--output", str(output_file)], stdout=stdout)

    assert exit_code == 0
    assert output_file.exists()
    assert json.loads(output_file.read_text(encoding="utf-8"))["selected"] is True
    assert json.loads(stdout.getvalue())["selected"] is True


def test_ranking_includes_eligible_candidates() -> None:
    result = selector.select_review_ready_candidate(
        [candidate("first"), candidate("second", statistical_profit_score=0.80)]
    )

    ranked_ids = [entry["candidate_id"] for entry in result["ranking"]]
    assert ranked_ids == ["second", "first"]
    assert result["eligible_count"] == 2


def test_rejection_reasons_include_rejected_candidate_ids() -> None:
    result = selector.select_review_ready_candidate(
        [candidate("bad", blocked_reasons=["manual_hold"]), candidate("good")]
    )

    assert "bad" in result["rejection_reasons"]
    assert any("manual_hold" in reason for reason in result["rejection_reasons"]["bad"])


def test_status_aliases_can_mark_review_ready() -> None:
    result = selector.select_review_ready_candidate(
        [candidate("alias", review_ready=False, status="READY_FOR_REVIEW")]
    )

    assert result["selected_candidate_id"] == "alias"


def test_field_aliases_are_accepted() -> None:
    aliased = candidate("unused")
    aliased.pop("candidate_id")
    aliased.pop("strategy")
    aliased.pop("symbol")
    aliased.update({"id": "alias-id", "strategy_id": "alias-strategy", "instrument": "GBP_USD"})

    result = selector.select_review_ready_candidate([aliased])

    assert result["selected_candidate_id"] == "alias-id"
    assert result["selected_candidate"]["strategy"] == "alias-strategy"
    assert result["selected_candidate"]["symbol"] == "GBP_USD"
