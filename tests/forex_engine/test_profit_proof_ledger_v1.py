from __future__ import annotations

import ast
import inspect
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import automation.forex_engine.profit_proof_ledger_v1 as ledger  # noqa: E402
from automation.forex_engine.profit_proof_ledger_v1 import (  # noqa: E402
    PROFIT_PROOF_LEDGER_BLOCKED_DRAWDOWN,
    PROFIT_PROOF_LEDGER_BLOCKED_LOW_PROFIT_FACTOR,
    PROFIT_PROOF_LEDGER_BLOCKED_NEGATIVE_EXPECTANCY,
    PROFIT_PROOF_LEDGER_BLOCKED_SAMPLE_DEPTH,
    PROFIT_PROOF_LEDGER_PROMOTABLE,
    PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY,
    ProfitProofCandidateEvidence,
    build_sample_all_blocked_candidates,
    build_sample_profit_proof_candidates,
    evaluate_profit_proof_candidate,
    evaluate_profit_proof_ledger,
    ledger_to_markdown,
    result_to_jsonable_dict,
)
from scripts.forex_delivery.run_profit_proof_ledger_v1 import main  # noqa: E402


def strong_candidate(**overrides):
    raw = {
        "candidate_id": "test-strong-candidate",
        "strategy_name": "paper_long_run_supervisor_v2",
        "symbol": "EUR_USD",
        "direction": "LONG",
        "evidence_source": "unit_test",
        "total_trades": 40,
        "wins": 27,
        "losses": 13,
        "realized_pl_total": "28.00",
        "expectancy": "0.70",
        "average_win": "1.35",
        "average_loss": "-0.65",
        "profit_factor": "1.90",
        "max_drawdown": "0.020",
        "consecutive_losses": 2,
        "sample_depth_sufficient": True,
        "walk_forward_passed": True,
        "out_of_sample_passed": True,
        "paper_demo_comparison": "paper_demo_consistent",
        "strategy_decay_flag": False,
        "broker_reconciliation_status": "RECONCILED",
        "spread_sensitivity_passed": True,
        "slippage_sensitivity_passed": True,
        "latency_observations": "stable",
        "latency_sensitivity_passed": True,
        "market_regime_coverage": 4,
        "risk_controls_present": True,
    }
    raw.update(overrides)
    return ProfitProofCandidateEvidence.from_mapping(raw)


def test_mixed_sample_returns_promotable_or_review_ready_candidate() -> None:
    result = evaluate_profit_proof_ledger(build_sample_profit_proof_candidates())

    assert result.ledger_status in {
        PROFIT_PROOF_LEDGER_PROMOTABLE,
        PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY,
    }
    assert any(candidate.promotable or candidate.review_ready for candidate in result.rankings)


def test_all_blocked_sample_selects_no_promotable_candidate() -> None:
    result = evaluate_profit_proof_ledger(build_sample_all_blocked_candidates())

    assert result.selected_candidate is None
    assert not any(candidate.promotable for candidate in result.candidate_results)


def test_negative_expectancy_is_blocked() -> None:
    result = evaluate_profit_proof_candidate(strong_candidate(expectancy="-0.01"))

    assert result.classification == PROFIT_PROOF_LEDGER_BLOCKED_NEGATIVE_EXPECTANCY


def test_low_profit_factor_is_blocked() -> None:
    result = evaluate_profit_proof_candidate(strong_candidate(profit_factor="1.10"))

    assert result.classification == PROFIT_PROOF_LEDGER_BLOCKED_LOW_PROFIT_FACTOR


def test_excessive_drawdown_is_blocked() -> None:
    result = evaluate_profit_proof_candidate(strong_candidate(max_drawdown="0.080"))

    assert result.classification == PROFIT_PROOF_LEDGER_BLOCKED_DRAWDOWN


def test_insufficient_sample_depth_is_blocked() -> None:
    result = evaluate_profit_proof_candidate(
        strong_candidate(total_trades=20, sample_depth_sufficient=False)
    )

    assert result.classification == PROFIT_PROOF_LEDGER_BLOCKED_SAMPLE_DEPTH


def test_missing_walk_forward_blocks_promotion() -> None:
    result = evaluate_profit_proof_candidate(strong_candidate(walk_forward_passed=None))

    assert result.promotable is False
    assert "walk-forward proof has not passed" in result.blockers


def test_missing_out_of_sample_blocks_promotion() -> None:
    result = evaluate_profit_proof_candidate(strong_candidate(out_of_sample_passed=None))

    assert result.promotable is False
    assert "out-of-sample proof has not passed" in result.blockers


def test_best_candidate_ranks_first_deterministically() -> None:
    result = evaluate_profit_proof_ledger(build_sample_profit_proof_candidates())

    assert result.rankings[0].candidate_id == "c2-eur-buy-stronger-review-ready"
    assert result.rankings[0].rank == 1


def test_repeated_evaluation_is_deterministic() -> None:
    left = json.dumps(
        result_to_jsonable_dict(evaluate_profit_proof_ledger()),
        sort_keys=True,
    )
    right = json.dumps(
        result_to_jsonable_dict(evaluate_profit_proof_ledger()),
        sort_keys=True,
    )

    assert left == right


def test_real_money_allowed_false() -> None:
    assert evaluate_profit_proof_ledger().real_money_allowed is False


def test_compounding_allowed_false() -> None:
    assert evaluate_profit_proof_ledger().compounding_allowed is False


def test_broker_action_allowed_false() -> None:
    assert evaluate_profit_proof_ledger().broker_action_allowed is False


def test_bank_movement_allowed_false() -> None:
    assert evaluate_profit_proof_ledger().bank_movement_allowed is False


def test_json_output_contains_required_keys() -> None:
    parsed = result_to_jsonable_dict(evaluate_profit_proof_ledger())

    for key in ledger.REQUIRED_JSON_KEYS:
        assert key in parsed


def test_markdown_output_contains_ledger_title() -> None:
    assert "# AIOS Forex Profit Proof Ledger V1" in ledger_to_markdown()


def test_runner_json_emits_valid_json() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["ledger_status"] == PROFIT_PROOF_LEDGER_PROMOTABLE


def test_module_imports_no_forbidden_runtime_modules() -> None:
    tree = ast.parse(inspect.getsource(ledger))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.lower() for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module.lower())

    forbidden_fragments = (
        "oan" + "da",
        "bro" + "ker",
        "cred" + "ential",
        "dot" + "env",
        "live_" + "execution",
        "ba" + "nk",
        "with" + "drawal",
        "dep" + "osit",
        "fund" + "ing",
        "sec" + "ret",
    )
    assert not any(
        fragment in module_name
        for module_name in imported
        for fragment in forbidden_fragments
    )
