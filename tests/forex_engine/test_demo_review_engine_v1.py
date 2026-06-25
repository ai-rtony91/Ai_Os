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

import automation.forex_engine.demo_review_engine_v1 as engine  # noqa: E402
from automation.forex_engine.demo_review_engine_v1 import (  # noqa: E402
    DEMO_REVIEW_BLOCKED,
    DEMO_REVIEW_READY,
    build_sample_all_blocked_demo_review_input,
    demo_review_to_markdown,
    evaluate_demo_review,
    result_to_jsonable_dict,
)
from scripts.forex_delivery.run_demo_review_engine_v1 import main  # noqa: E402


def test_mixed_sample_is_demo_review_ready_only() -> None:
    result = evaluate_demo_review()

    assert result.demo_review_status == DEMO_REVIEW_READY


def test_best_strategy_is_supertrend() -> None:
    assert evaluate_demo_review().best_strategy == "supertrend"


def test_supertrend_status_is_surfaced() -> None:
    result = evaluate_demo_review()

    assert result.supertrend_status["status"] == "SUPER_TREND_PROOF_REVIEW_READY"


def test_why_explains_review_reason() -> None:
    result = evaluate_demo_review()

    assert "strongest local evidence" in result.why


def test_expectancy_status_is_strong() -> None:
    assert evaluate_demo_review().expectancy_status == "EXPECTANCY_STRONG"


def test_proof_status_is_improving() -> None:
    assert evaluate_demo_review().proof_status == "PROOF_IMPROVING"


def test_expectancy_improving_true() -> None:
    assert evaluate_demo_review().expectancy_improving is True


def test_proof_improving_true() -> None:
    assert evaluate_demo_review().proof_improving is True


def test_promotion_score_surfaced() -> None:
    assert result_to_jsonable_dict(evaluate_demo_review())["promotion_score"] == "100.00"


def test_all_blocked_sample_blocks_demo_review() -> None:
    result = evaluate_demo_review(build_sample_all_blocked_demo_review_input())

    assert result.demo_review_status == DEMO_REVIEW_BLOCKED


def test_all_blocked_sample_surfaces_blockers() -> None:
    result = evaluate_demo_review(build_sample_all_blocked_demo_review_input())

    assert result.blockers


def test_missing_proof_is_surfaced() -> None:
    result = evaluate_demo_review()

    assert "minimum_22_6_observation_window" in result.blockers


def test_what_must_improve_next_is_surfaced() -> None:
    result = evaluate_demo_review()

    assert "human demo-review package still required before any execution" in (
        result.what_must_improve_next
    )


def test_next_safe_action_blocks_execution() -> None:
    result = evaluate_demo_review()

    assert "do not run demo execution" in result.next_safe_action


def test_demo_execution_allowed_false() -> None:
    assert evaluate_demo_review().demo_execution_allowed is False


def test_real_money_allowed_false() -> None:
    assert evaluate_demo_review().real_money_allowed is False


def test_compounding_allowed_false() -> None:
    assert evaluate_demo_review().compounding_allowed is False


def test_broker_action_allowed_false() -> None:
    assert evaluate_demo_review().broker_action_allowed is False


def test_bank_movement_allowed_false() -> None:
    assert evaluate_demo_review().bank_movement_allowed is False


def test_permissions_mapping_all_false() -> None:
    assert evaluate_demo_review().permissions == {
        "demo_execution_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
    }


def test_json_output_valid() -> None:
    parsed = result_to_jsonable_dict(evaluate_demo_review())

    assert parsed["best_strategy"] == "supertrend"
    assert parsed["permissions"]["real_money_allowed"] is False


def test_markdown_output_valid() -> None:
    markdown = demo_review_to_markdown(evaluate_demo_review())

    assert "# AIOS Forex Demo Review Engine V1" in markdown
    assert "## Next Copy/Paste Action" in markdown


def test_runner_json_valid() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["best_strategy"] == "supertrend"


def test_runner_markdown_valid() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--markdown"], stdout=stdout)

    assert exit_code == 0
    assert "# AIOS Forex Demo Review Engine V1" in stdout.getvalue()


def test_runner_all_blocked_operator_text() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-all-blocked"], stdout=stdout)

    assert exit_code == 0
    assert "DEMO_REVIEW_BLOCKED" in stdout.getvalue()


def test_deterministic_json() -> None:
    left = json.dumps(result_to_jsonable_dict(evaluate_demo_review()), sort_keys=True)
    right = json.dumps(result_to_jsonable_dict(evaluate_demo_review()), sort_keys=True)

    assert left == right


def test_module_imports_no_forbidden_runtime_modules() -> None:
    tree = ast.parse(inspect.getsource(engine))
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
