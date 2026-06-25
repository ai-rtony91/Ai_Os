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

import automation.forex_engine.strategy_promotion_router_v1 as router  # noqa: E402
from automation.forex_engine.strategy_promotion_router_v1 import (  # noqa: E402
    STRATEGY_PROMOTION_BLOCKED,
    STRATEGY_PROMOTION_REVIEW_READY,
    build_sample_all_blocked_promotion_input,
    promotion_route_to_markdown,
    result_to_jsonable_dict,
    route_strategy_promotion,
)
from scripts.forex_delivery.run_strategy_promotion_router_v1 import main  # noqa: E402


def test_mixed_sample_promotes_review_ready_only() -> None:
    result = route_strategy_promotion()

    assert result.promotion_status == STRATEGY_PROMOTION_REVIEW_READY
    assert result.review_recommendation == "REVIEW_STRATEGY_FOR_DEMO_PACKAGE_ONLY"


def test_best_strategy_is_supertrend() -> None:
    assert route_strategy_promotion().best_strategy == "supertrend"


def test_supertrend_status_is_surfaced() -> None:
    result = route_strategy_promotion()

    assert result.supertrend_status["status"] == "SUPER_TREND_PROOF_REVIEW_READY"


def test_promotion_score_is_full_for_mixed_sample() -> None:
    assert result_to_jsonable_dict(route_strategy_promotion())["promotion_score"] == "100.00"


def test_expectancy_status_is_strong() -> None:
    assert route_strategy_promotion().expectancy_status == "EXPECTANCY_STRONG"


def test_proof_status_is_improving() -> None:
    assert route_strategy_promotion().proof_status == "PROOF_IMPROVING"


def test_expectancy_and_proof_improving_flags_are_true() -> None:
    result = route_strategy_promotion()

    assert result.expectancy_improving is True
    assert result.proof_improving is True


def test_all_blocked_sample_is_blocked() -> None:
    result = route_strategy_promotion(build_sample_all_blocked_promotion_input())

    assert result.promotion_status == STRATEGY_PROMOTION_BLOCKED
    assert result.failed_checks


def test_all_blocked_has_no_review_ready_recommendation() -> None:
    result = route_strategy_promotion(build_sample_all_blocked_promotion_input())

    assert result.review_recommendation == "COLLECT_MORE_PROOF_BEFORE_DEMO_REVIEW"


def test_blockers_include_22_6_missing_proof() -> None:
    result = route_strategy_promotion()

    assert "minimum_22_6_observation_window" in result.blockers


def test_what_must_improve_next_is_surfaced() -> None:
    result = route_strategy_promotion()

    assert "human demo-review package still required before any execution" in (
        result.what_must_improve_next
    )


def test_next_safe_action_blocks_execution() -> None:
    result = route_strategy_promotion()

    assert "keep demo execution" in result.next_safe_action


def test_demo_execution_allowed_false() -> None:
    assert route_strategy_promotion().demo_execution_allowed is False


def test_real_money_allowed_false() -> None:
    assert route_strategy_promotion().real_money_allowed is False


def test_compounding_allowed_false() -> None:
    assert route_strategy_promotion().compounding_allowed is False


def test_broker_action_allowed_false() -> None:
    assert route_strategy_promotion().broker_action_allowed is False


def test_bank_movement_allowed_false() -> None:
    assert route_strategy_promotion().bank_movement_allowed is False


def test_permissions_mapping_all_false() -> None:
    assert route_strategy_promotion().permissions == {
        "demo_execution_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
    }


def test_json_output_valid() -> None:
    parsed = result_to_jsonable_dict(route_strategy_promotion())

    assert parsed["best_strategy"] == "supertrend"
    assert parsed["permissions"]["demo_execution_allowed"] is False


def test_markdown_output_valid() -> None:
    markdown = promotion_route_to_markdown(route_strategy_promotion())

    assert "# AIOS Forex Strategy Promotion Router V1" in markdown
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
    assert "# AIOS Forex Strategy Promotion Router V1" in stdout.getvalue()


def test_runner_all_blocked_operator_text() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-all-blocked"], stdout=stdout)

    assert exit_code == 0
    assert "STRATEGY_PROMOTION_BLOCKED" in stdout.getvalue()


def test_deterministic_json() -> None:
    left = json.dumps(result_to_jsonable_dict(route_strategy_promotion()), sort_keys=True)
    right = json.dumps(result_to_jsonable_dict(route_strategy_promotion()), sort_keys=True)

    assert left == right


def test_checks_include_required_fields() -> None:
    check_ids = {check.check_id for check in route_strategy_promotion().checks}

    assert {
        "best_strategy_present",
        "supertrend_review_ready",
        "expectancy_strong",
        "proof_improving",
        "profit_factor_ready",
        "drawdown_ready",
        "sample_depth_ready",
        "demo_execution_locked",
        "money_permissions_locked",
    } <= check_ids


def test_module_imports_no_forbidden_runtime_modules() -> None:
    tree = ast.parse(inspect.getsource(router))
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
