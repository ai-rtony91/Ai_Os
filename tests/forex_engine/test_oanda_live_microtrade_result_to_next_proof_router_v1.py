from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import oanda_owner_run_live_microtrade_result_capture_epic_v1 as capture_epic
from automation.forex_engine import oanda_live_microtrade_result_to_next_proof_router_v1 as router
from scripts.forex_delivery import run_oanda_live_microtrade_result_to_next_proof_router_v1


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation/forex_engine/oanda_live_microtrade_result_to_next_proof_router_v1.py"
)
RUNNER_PATH = (
    REPO_ROOT
    / "scripts/forex_delivery/run_oanda_live_microtrade_result_to_next_proof_router_v1.py"
)
TEST_PATH = (
    REPO_ROOT
    / "tests/forex_engine/test_oanda_live_microtrade_result_to_next_proof_router_v1.py"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_V1.md"
)
MANUAL_REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_MANUAL_FINALIZATION_V1.md"
)

SAMPLE_CASES = (
    (
        "profit",
        router.build_sample_profit_router_input,
        router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW,
        "profit",
        "live_proof_candidate_review",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1",
        router.PROFIT_ROUTING_REASON,
    ),
    (
        "loss",
        router.build_sample_loss_router_input,
        router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW,
        "loss",
        "loss_review_and_next_profit_candidate_gate",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1",
        router.LOSS_ROUTING_REASON,
    ),
    (
        "breakeven",
        router.build_sample_breakeven_router_input,
        router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_REQUIRE_MORE_EVIDENCE,
        "breakeven",
        "more_evidence_required",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-BREAKEVEN-MORE-EVIDENCE-V1",
        router.BREAKEVEN_ROUTING_REASON,
    ),
    (
        "missing",
        router.build_sample_missing_owner_result_router_input,
        router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_NO_OWNER_RESULT,
        "missing",
        "owner_result_evidence_required",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-OWNER-RESULT-EVIDENCE-REQUIRED-V1",
        router.MISSING_OWNER_ROUTING_REASON,
    ),
    (
        "unsafe",
        router.build_sample_unsafe_router_input,
        router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_UNSAFE,
        "unsafe",
        "unsafe_result_repair",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-UNSAFE-RESULT-REPAIR-V1",
        router.UNSAFE_ROUTING_REASON,
    ),
)

REQUIRED_FIELDS = (
    "version",
    "packet_id",
    "classification",
    "source_result_capture_status",
    "source_result_bucket",
    "source_classifier_status",
    "source_reconciliation_status",
    "source_ledger_bridge_status",
    "realized_pl",
    "realized_r",
    "risk_breach",
    "max_loss_respected",
    "next_proof_lane",
    "next_proof_packet_preview",
    "routing_reason",
    "owner_review_required",
    "preview_only",
    "router_only",
    "result_capture_only",
    "required_owner_decision",
    "blocked_items",
    "protected_flags",
    "exact_next_owner_action",
    "exact_next_codex_packet",
    "one_sentence_answer",
    "next_safe_action",
)

REPORT_SAFETY_PHRASES = (
    "No trade placed by this packet.",
    "No broker call was made by this packet.",
    "No credential access occurred.",
    "No account ID was persisted.",
    "No broker order ID was persisted.",
    "No raw broker payload was persisted.",
    "No live approval was granted.",
    "No repeat trading approval was granted.",
    "No next trade approval was granted.",
    "No real money approval was granted.",
    "No compounding approval was granted.",
    "No bank movement approval was granted.",
    "No autonomous execution was granted.",
    "Unattended vacation mode remains blocked.",
    "Vacation profit trial remains blocked unless Anthony separately approves.",
    "Profit is not guaranteed.",
    "One result does not prove statistical profitability.",
    "All protected flags remain false.",
    "Router preview only.",
    "Read-only only.",
)


def _result(builder=router.build_sample_profit_router_input):
    return router.route_oanda_live_microtrade_result_to_next_proof(builder())


@pytest.mark.parametrize(
    ("name", "builder", "classification", "bucket", "lane", "packet", "reason"),
    SAMPLE_CASES,
)
def test_sample_routes(name, builder, classification, bucket, lane, packet, reason):
    result = _result(builder)
    assert result.classification == classification
    assert result.source_result_bucket == bucket
    assert result.next_proof_lane == lane
    assert result.next_proof_packet_preview == packet
    assert result.routing_reason == reason


@pytest.mark.parametrize(
    ("name", "builder", "classification", "bucket", "lane", "packet", "reason"),
    SAMPLE_CASES,
)
def test_sample_classifications(name, builder, classification, bucket, lane, packet, reason):
    assert _result(builder).classification == classification


@pytest.mark.parametrize(
    ("name", "builder", "classification", "bucket", "lane", "packet", "reason"),
    SAMPLE_CASES,
)
def test_sample_next_lanes(name, builder, classification, bucket, lane, packet, reason):
    assert _result(builder).next_proof_lane == lane


@pytest.mark.parametrize(
    ("name", "builder", "classification", "bucket", "lane", "packet", "reason"),
    SAMPLE_CASES,
)
def test_sample_packet_previews(name, builder, classification, bucket, lane, packet, reason):
    assert _result(builder).next_proof_packet_preview == packet


@pytest.mark.parametrize(
    ("name", "builder", "classification", "bucket", "lane", "packet", "reason"),
    SAMPLE_CASES,
)
def test_sample_routing_reasons(name, builder, classification, bucket, lane, packet, reason):
    assert _result(builder).routing_reason == reason


@pytest.mark.parametrize(
    ("name", "builder", "classification", "bucket", "lane", "packet", "reason"),
    SAMPLE_CASES,
)
def test_json_serializable_outputs(name, builder, classification, bucket, lane, packet, reason):
    json.dumps(router.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    ("name", "builder", "classification", "bucket", "lane", "packet", "reason"),
    SAMPLE_CASES,
)
def test_deterministic_outputs(name, builder, classification, bucket, lane, packet, reason):
    assert router.to_jsonable_dict(_result(builder)) == router.to_jsonable_dict(
        _result(builder)
    )


@pytest.mark.parametrize("field_name", REQUIRED_FIELDS)
def test_required_result_fields_present(field_name: str):
    assert hasattr(_result(), field_name)


@pytest.mark.parametrize("flag_name", router.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_in_map(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize("flag_name", router.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_on_result(flag_name: str):
    assert getattr(_result(), flag_name) is False


@pytest.mark.parametrize(
    "flag_name",
    (
        "next_trade_authorized",
        "result_proves_profitability",
        "statistical_profitability_confirmed",
        "repeat_live_trade_allowed",
        "live_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "unattended_vacation_mode_allowed",
        "vacation_profit_trial_allowed",
    ),
)
def test_high_risk_flags_false(flag_name: str):
    assert getattr(_result(), flag_name) is False


@pytest.mark.parametrize(
    ("field_name", "expected"),
    (
        ("preview_only", True),
        ("router_only", True),
        ("result_capture_only", True),
        ("owner_review_required", True),
    ),
)
def test_descriptive_flags_true(field_name: str, expected: bool):
    assert getattr(_result(), field_name) is expected


def test_exact_next_owner_action_present():
    assert _result().exact_next_owner_action == router.EXACT_NEXT_OWNER_ACTION


def test_exact_next_codex_packet_policy_present():
    assert _result().exact_next_codex_packet == router.EXACT_NEXT_CODEX_PACKET


def test_one_sentence_answer_exact():
    assert _result().one_sentence_answer == router.EXACT_ONE_SENTENCE_ANSWER


def test_markdown_output():
    text = router.to_markdown(_result())
    assert text.startswith("# AIOS Forex OANDA Live Microtrade Result-To-Next-Proof Router V1")
    assert "No next trade approval was granted." in text


def test_operator_text_output():
    text = router.to_operator_text(_result())
    assert "Result-to-next-proof router status" in text
    assert "No next trade approval was granted." in text


def test_mapping_capture_output_can_be_routed():
    first = capture_epic.to_jsonable_dict(
        capture_epic.run_oanda_owner_run_live_microtrade_result_capture_epic(
            capture_epic.build_sample_profit_result_input()
        )
    )
    result = router.route_oanda_live_microtrade_result_to_next_proof(
        router.OandaLiveMicrotradeResultToNextProofRouterInput(first)
    )
    assert result.next_proof_lane == "live_proof_candidate_review"


def test_unsafe_owner_review_decision_does_not_authorize():
    result = router.route_oanda_live_microtrade_result_to_next_proof(
        {
            "result_capture_input": router.build_sample_profit_router_input().result_capture_input,
            "owner_review_decision": "approve another trade",
        }
    )
    assert result.required_owner_decision == "pending_owner_review"
    assert result.next_trade_authorized is False


@pytest.mark.parametrize(
    "fragment",
    (
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "import subprocess",
        "from oanda",
        "import oanda",
        "broker_mutation",
        "oanda_trade_execution",
        "oanda_execution",
        "broker_execution",
        "def place_order",
        "def submit_order",
        "def execute_order",
        ".env",
    ),
)
def test_static_safety_no_forbidden_fragments_in_module(fragment: str):
    assert fragment not in MODULE_PATH.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("path", (MODULE_PATH, RUNNER_PATH, TEST_PATH, REPORT_PATH, MANUAL_REPORT_PATH))
def test_created_paths_exist(path: Path):
    assert path.exists()


@pytest.mark.parametrize("phrase", REPORT_SAFETY_PHRASES)
def test_report_required_safety_phrases(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "heading",
    (
        "# AIOS Forex OANDA Live Microtrade Result-To-Next-Proof Router V1",
        "## Packet ID",
        "## Source Chain Read",
        "## Files Created",
        "## Router Classifications",
        "## Routing Map",
        "## Profit Sample Result",
        "## Loss Sample Result",
        "## Breakeven Sample Result",
        "## Missing Owner Result Sample",
        "## Unsafe Sample Result",
        "## Exact Next Owner Action",
        "## Exact Next Codex Packet Policy",
        "## Protected Flags",
        "## Safety Boundary",
        "## Validators Run",
        "## Validators Passed",
        "## Validators Failed",
        "## Git Status If Available",
        "## Next Safe Action",
    ),
)
def test_report_required_sections(heading: str):
    assert heading in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "command",
    (
        "python -m py_compile automation/forex_engine/oanda_live_microtrade_result_to_next_proof_router_v1.py scripts/forex_delivery/run_oanda_live_microtrade_result_to_next_proof_router_v1.py tests/forex_engine/test_oanda_live_microtrade_result_to_next_proof_router_v1.py",
        "python -m pytest tests/forex_engine/test_oanda_live_microtrade_result_to_next_proof_router_v1.py -q",
        "python scripts/forex_delivery/run_oanda_live_microtrade_result_to_next_proof_router_v1.py --sample-profit --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_result_to_next_proof_router_v1.py --sample-loss --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_result_to_next_proof_router_v1.py --sample-breakeven --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_result_to_next_proof_router_v1.py --sample-missing --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_result_to_next_proof_router_v1.py --sample-unsafe --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_result_to_next_proof_router_v1.py --sample-profit --markdown",
        "git diff --check",
        "git status --short --branch",
    ),
)
def test_manual_report_commands(command: str):
    assert command in MANUAL_REPORT_PATH.read_text(encoding="utf-8")


def test_manual_report_says_do_not_compile_markdown_reports():
    assert (
        "Do not include Markdown report files in python -m py_compile."
        in MANUAL_REPORT_PATH.read_text(encoding="utf-8")
    )


@pytest.mark.parametrize(
    ("argv", "expected"),
    (
        (
            ["runner", "--sample-profit", "--json"],
            router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW,
        ),
        (
            ["runner", "--sample-loss", "--json"],
            "loss_review_and_next_profit_candidate_gate",
        ),
        (
            ["runner", "--sample-breakeven", "--json"],
            router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_REQUIRE_MORE_EVIDENCE,
        ),
        (
            ["runner", "--sample-missing", "--json"],
            router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_NO_OWNER_RESULT,
        ),
        (
            ["runner", "--sample-unsafe", "--json"],
            router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_UNSAFE,
        ),
        (
            ["runner", "--sample-profit", "--markdown"],
            "# AIOS Forex OANDA Live Microtrade Result-To-Next-Proof Router V1",
        ),
    ),
)
def test_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert run_oanda_live_microtrade_result_to_next_proof_router_v1.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize(
    "phrase",
    (
        "profit result -> live proof candidate review packet preview",
        "loss result -> loss review and next profit candidate gate packet preview",
        "breakeven result -> more evidence packet preview",
        "missing owner result -> owner result evidence required packet preview",
        "unsafe result -> unsafe result repair packet preview",
    ),
)
def test_report_routing_map_phrases(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")
