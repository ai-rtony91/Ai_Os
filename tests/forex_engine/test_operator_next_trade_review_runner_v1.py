from __future__ import annotations

import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.forex_delivery.run_operator_next_trade_review_composer_v1 import (  # noqa: E402
    RUNNER_SAFETY,
    main,
)


def conservative_safety() -> dict:
    return {
        "local_only": True,
        "broker_calls_allowed": False,
        "credential_access_allowed": False,
        "order_placement_allowed": False,
        "order_close_allowed": False,
        "live_endpoint_allowed": False,
        "repo_mutation_outside_allowed_files": False,
        "uses_network": False,
    }


def passing_evidence() -> dict:
    return {
        "loss_review_metrics_gate": {
            "allowed": True,
            "decision": "REVIEW_READY_FOR_OWNER_APPROVAL",
            "blocked_reasons": [],
            "missing_metrics": {},
            "safety": conservative_safety(),
        },
        "trade_latency_baseline": {
            "allowed": True,
            "decision": "LATENCY_READY_FOR_REVIEW",
            "blocked_reasons": [],
            "missing_timestamps": [],
            "invalid_timestamps": [],
            "slow_segments": [],
            "safety": conservative_safety(),
        },
        "operator_context": {
            "operator_name": "Anthony",
            "instrument": "EUR_USD",
            "direction": "LONG",
            "strategy_name": "paper_edge_candidate",
            "candidate_id": "c1-eur-buy",
            "last_trade_id": 334,
            "last_trade_result": "FILLED_TRADE_PL_NEGATIVE",
            "wants_next_demo_review": True,
        },
    }


def run_main(args: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = main(args, stdout=stdout, stderr=stderr)
    return exit_code, stdout.getvalue(), stderr.getvalue()


def test_no_evidence_option_returns_blocked_plain_output_and_exit_code_zero() -> None:
    exit_code, output, _ = run_main([])

    assert exit_code == 0
    assert "AIOS Operator Next Trade Review" in output
    assert "decision: BLOCK_REVIEW_INVALID_EVIDENCE" in output
    assert "allowed: false" in output


def test_sample_trade_334_returns_blocked_and_broker_action_false() -> None:
    exit_code, output, _ = run_main(["--sample-blocked-trade-334"])

    assert exit_code == 0
    assert "decision: BLOCK_REVIEW_MISSING_PROOF" in output
    assert "broker_action_allowed: false" in output
    assert "trade 334" in output.lower()


def test_valid_evidence_json_path_returns_output_based_on_composer_result(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(passing_evidence()), encoding="utf-8")

    exit_code, output, _ = run_main(["--evidence-json", str(evidence_path), "--json"])
    parsed = json.loads(output)

    assert exit_code == 0
    assert parsed["decision"] == "REVIEW_READY_FOR_OWNER_APPROVAL"
    assert parsed["allowed"] is True
    assert parsed["broker_action_allowed"] is False


def test_malformed_json_file_returns_exit_code_two(tmp_path: Path) -> None:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text("{not-json", encoding="utf-8")

    exit_code, output, _ = run_main(["--evidence-json", str(evidence_path)])

    assert exit_code == 2
    assert "BLOCK_REVIEW_INVALID_EVIDENCE" in output
    assert "could not be parsed" in output


def test_missing_json_file_returns_exit_code_two(tmp_path: Path) -> None:
    evidence_path = tmp_path / "missing.json"

    exit_code, output, _ = run_main(["--evidence-json", str(evidence_path)])

    assert exit_code == 2
    assert "BLOCK_REVIEW_INVALID_EVIDENCE" in output
    assert "was not found" in output


def test_json_flag_emits_valid_json() -> None:
    exit_code, output, _ = run_main(["--sample-blocked-trade-334", "--json"])
    parsed = json.loads(output)

    assert exit_code == 0
    assert parsed["decision"] == "BLOCK_REVIEW_MISSING_PROOF"
    assert parsed["broker_action_allowed"] is False


def test_default_output_is_plain() -> None:
    exit_code, output, _ = run_main(["--sample-blocked-trade-334"])

    assert exit_code == 0
    assert output.startswith("AIOS Operator Next Trade Review")
    assert not output.lstrip().startswith("{")


def test_plain_output_includes_required_operator_fields() -> None:
    _, output, _ = run_main(["--sample-blocked-trade-334"])

    assert "decision:" in output
    assert "allowed:" in output
    assert "operator_answer:" in output
    assert "next_safe_action:" in output
    assert "broker_action_allowed:" in output


def test_script_does_not_include_broker_network_or_order_mutation_commands() -> None:
    script_path = (
        ROOT / "scripts/forex_delivery/run_operator_next_trade_review_composer_v1.py"
    )
    source = script_path.read_text(encoding="utf-8").lower()

    forbidden_runtime_imports = ["subprocess", "socket", "requests", "urllib"]
    forbidden_mutation_calls = ["git add", "git commit", "git push", "ordercreate"]
    for marker in forbidden_runtime_imports + forbidden_mutation_calls:
        assert marker not in source


def test_runner_remains_local_only_and_does_not_mutate_repo_state() -> None:
    assert RUNNER_SAFETY["local_only"] is True
    assert RUNNER_SAFETY["repo_mutation_performed"] is False
    assert RUNNER_SAFETY["broker_calls_allowed"] is False
    assert RUNNER_SAFETY["order_placement_allowed"] is False


def test_operator_facing_language_is_present() -> None:
    _, output, _ = run_main(["--sample-blocked-trade-334"])

    assert "AIOS Operator Next Trade Review" in output
    assert "Blocked:" in output
    assert "next_safe_action:" in output
