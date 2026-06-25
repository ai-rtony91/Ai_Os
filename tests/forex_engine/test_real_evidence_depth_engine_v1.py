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

import automation.forex_engine.real_evidence_depth_engine_v1 as depth  # noqa: E402
from automation.forex_engine.real_evidence_depth_engine_v1 import (  # noqa: E402
    REAL_EVIDENCE_DEPTH_IMPROVING,
    build_sample_all_blocked_real_evidence_inputs,
    build_sample_mixed_real_evidence_inputs,
    evaluate_real_evidence_depth,
    real_evidence_depth_to_markdown,
    result_to_jsonable_dict,
)
from scripts.forex_delivery.run_real_evidence_depth_engine_v1 import main  # noqa: E402


def test_mixed_sample_surfaces_top_strategy() -> None:
    result = evaluate_real_evidence_depth()

    assert result.top_strategy_id == "supertrend"


def test_supertrend_status_is_surfaced() -> None:
    result = evaluate_real_evidence_depth()

    assert result.supertrend_status["status"] == "SUPER_TREND_PROOF_REVIEW_READY"


def test_expectancy_status_is_strong_for_mixed_sample() -> None:
    result = evaluate_real_evidence_depth()

    assert result.expectancy_status == "EXPECTANCY_STRONG"


def test_profit_factor_strength_is_strong() -> None:
    assert evaluate_real_evidence_depth().profit_factor_strength == "PROFIT_FACTOR_STRONG"


def test_drawdown_strength_is_strong() -> None:
    assert evaluate_real_evidence_depth().drawdown_strength == "DRAWDOWN_STRONG"


def test_sample_depth_is_strong() -> None:
    assert evaluate_real_evidence_depth().sample_depth_strength == "SAMPLE_DEPTH_STRONG"


def test_win_loss_balance_positive() -> None:
    assert evaluate_real_evidence_depth().win_loss_balance == "WIN_LOSS_BALANCE_POSITIVE"


def test_consecutive_loss_risk_low() -> None:
    assert evaluate_real_evidence_depth().consecutive_loss_risk == "CONSECUTIVE_LOSS_RISK_LOW"


def test_proof_confidence_strong() -> None:
    assert evaluate_real_evidence_depth().proof_confidence == "PROOF_CONFIDENCE_STRONG"


def test_22_6_readiness_improving_but_not_approved() -> None:
    result = evaluate_real_evidence_depth()

    assert result.depth_status == REAL_EVIDENCE_DEPTH_IMPROVING
    assert result.trusted_22_6_improvement == "TRUSTED_22_6_IMPROVING_PROOF_REVIEW_READY"
    assert "minimum_22_6_observation_window" in result.proof_missing


def test_all_blocked_sample_has_failed_checks() -> None:
    strategy, readiness = build_sample_all_blocked_real_evidence_inputs()
    result = evaluate_real_evidence_depth(strategy, readiness)

    assert result.failed_checks
    assert result.expectancy_status == "EXPECTANCY_BLOCKED"


def test_no_real_money_allowed() -> None:
    assert evaluate_real_evidence_depth().real_money_allowed is False


def test_no_compounding_allowed() -> None:
    assert evaluate_real_evidence_depth().compounding_allowed is False


def test_no_broker_action_allowed() -> None:
    assert evaluate_real_evidence_depth().broker_action_allowed is False


def test_no_bank_movement_allowed() -> None:
    assert evaluate_real_evidence_depth().bank_movement_allowed is False


def test_no_demo_trade_allowed() -> None:
    assert evaluate_real_evidence_depth().demo_trade_allowed is False


def test_permissions_mapping_all_false() -> None:
    assert evaluate_real_evidence_depth().permissions == {
        "demo_trade_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
    }


def test_json_output_valid() -> None:
    parsed = result_to_jsonable_dict(evaluate_real_evidence_depth())

    assert parsed["top_strategy_id"] == "supertrend"
    assert parsed["depth_status"] == REAL_EVIDENCE_DEPTH_IMPROVING


def test_markdown_output_valid() -> None:
    markdown = real_evidence_depth_to_markdown(evaluate_real_evidence_depth())

    assert "# AIOS Forex Real Evidence Depth Engine V1" in markdown
    assert "## Next Copy/Paste Action" in markdown


def test_runner_json_valid() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["top_strategy_id"] == "supertrend"


def test_runner_markdown_valid() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--markdown"], stdout=stdout)

    assert exit_code == 0
    assert "# AIOS Forex Real Evidence Depth Engine V1" in stdout.getvalue()


def test_runner_all_blocked_operator_text() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-all-blocked"], stdout=stdout)

    assert exit_code == 0
    assert "EXPECTANCY_BLOCKED" in stdout.getvalue()


def test_deterministic_json() -> None:
    left = json.dumps(result_to_jsonable_dict(evaluate_real_evidence_depth()), sort_keys=True)
    right = json.dumps(result_to_jsonable_dict(evaluate_real_evidence_depth()), sort_keys=True)

    assert left == right


def test_money_focused_next_step_is_surfaced() -> None:
    result = evaluate_real_evidence_depth()

    assert "supertrend" in result.money_focused_next_step


def test_checks_include_required_depth_fields() -> None:
    check_ids = {check.check_id for check in evaluate_real_evidence_depth().checks}

    assert {
        "top_strategy_present",
        "supertrend_strong_enough",
        "expectancy_strong_enough",
        "profit_factor_strong_enough",
        "drawdown_acceptable",
        "sample_depth_enough",
        "win_loss_balance_positive",
        "consecutive_loss_risk_acceptable",
        "proof_confidence_enough",
        "trusted_22_6_readiness_improving",
    } <= check_ids


def test_module_imports_no_forbidden_runtime_modules() -> None:
    tree = ast.parse(inspect.getsource(depth))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.lower() for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module.lower())

    forbidden_fragments = (
        "oanda",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "dotenv",
        "credential",
        "secret",
    )
    assert not any(
        fragment in module_name
        for module_name in imported
        for fragment in forbidden_fragments
    )
