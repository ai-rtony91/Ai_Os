from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import (
    oanda_live_microtrade_routed_proof_owner_decision_gate_v1 as decision_gate,
)
from automation.forex_engine import (
    oanda_live_microtrade_result_to_next_proof_router_v1 as source_router,
)
from scripts.forex_delivery import (
    run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation/forex_engine/oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py"
)
RUNNER_PATH = (
    REPO_ROOT
    / "scripts/forex_delivery/run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py"
)
TEST_PATH = (
    REPO_ROOT
    / "tests/forex_engine/test_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_GATE_V1.md"
)
MANUAL_REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_GATE_MANUAL_FINALIZATION_V1.md"
)

SAMPLE_CASES = (
    (
        "profit",
        decision_gate.build_sample_profit_decision_input,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW,
        source_router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW,
        "live_proof_candidate_review",
        "profit_proof_candidate_review",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1",
        decision_gate.PROFIT_PROOF_WARNING,
        decision_gate.PROFIT_STATISTICAL_WARNING,
    ),
    (
        "loss",
        decision_gate.build_sample_loss_decision_input,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW,
        source_router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW,
        "loss_review_and_next_profit_candidate_gate",
        "loss_review_and_next_profit_candidate_gate",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1",
        decision_gate.LOSS_PROOF_WARNING,
        decision_gate.LOSS_STATISTICAL_WARNING,
    ),
    (
        "breakeven",
        decision_gate.build_sample_breakeven_decision_input,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_REQUIRE_MORE_EVIDENCE,
        source_router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_REQUIRE_MORE_EVIDENCE,
        "more_evidence_required",
        "more_evidence_required",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-BREAKEVEN-MORE-EVIDENCE-V1",
        decision_gate.MORE_EVIDENCE_PROOF_WARNING,
        decision_gate.MORE_EVIDENCE_STATISTICAL_WARNING,
    ),
    (
        "missing",
        decision_gate.build_sample_missing_owner_result_decision_input,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_NO_OWNER_RESULT,
        source_router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_NO_OWNER_RESULT,
        "owner_result_evidence_required",
        "owner_result_evidence_required",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-OWNER-RESULT-EVIDENCE-REQUIRED-V1",
        decision_gate.MISSING_OWNER_PROOF_WARNING,
        decision_gate.MISSING_OWNER_STATISTICAL_WARNING,
    ),
    (
        "unsafe",
        decision_gate.build_sample_unsafe_decision_input,
        decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_UNSAFE,
        source_router.OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_UNSAFE,
        "unsafe_result_repair",
        "unsafe_result_repair",
        "AIOS-FOREX-OANDA-LIVE-MICROTRADE-UNSAFE-RESULT-REPAIR-V1",
        decision_gate.UNSAFE_PROOF_WARNING,
        decision_gate.UNSAFE_STATISTICAL_WARNING,
    ),
)

REQUIRED_RESULT_FIELDS = (
    "version",
    "packet_id",
    "classification",
    "source_router_status",
    "source_next_proof_lane",
    "source_next_proof_packet_preview",
    "source_routing_reason",
    "selected_review_lane",
    "selected_packet_preview",
    "owner_decision_label",
    "owner_review_required",
    "selected_packet_preview_only",
    "preview_only",
    "decision_gate_only",
    "required_owner_action",
    "blocked_items",
    "proof_warning",
    "statistical_warning",
    "exact_next_owner_action",
    "exact_next_codex_packet_policy",
    "one_sentence_answer",
    "next_safe_action",
    "protected_flags",
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
    "No selected packet execution approval was granted.",
    "No real money approval was granted.",
    "No compounding approval was granted.",
    "No bank movement approval was granted.",
    "No autonomous execution was granted.",
    "Unattended vacation mode remains blocked.",
    "Vacation profit trial remains blocked unless Anthony separately approves.",
    "Profit is not guaranteed.",
    "One result does not prove statistical profitability.",
    "All protected flags remain false.",
    "Decision gate preview only.",
    "Read-only only.",
)


def _result(builder=decision_gate.build_sample_profit_decision_input):
    return decision_gate.evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate(
        builder()
    )


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_sample_decision_mapping(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    result = _result(builder)
    assert result.classification == classification
    assert result.source_router_status == source_status
    assert result.source_next_proof_lane == source_lane
    assert result.selected_review_lane == selected_lane
    assert result.selected_packet_preview == packet


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_sample_classifications(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    assert _result(builder).classification == classification


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_sample_selected_lanes(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    assert _result(builder).selected_review_lane == selected_lane


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_sample_packet_previews(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    assert _result(builder).selected_packet_preview == packet


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_sample_proof_warnings(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    assert _result(builder).proof_warning == proof_warning


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_sample_statistical_warnings(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    assert _result(builder).statistical_warning == statistical_warning


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_json_serializable_outputs(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    json.dumps(decision_gate.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_deterministic_outputs(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    assert decision_gate.to_jsonable_dict(_result(builder)) == decision_gate.to_jsonable_dict(
        _result(builder)
    )


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_markdown_outputs(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    text = decision_gate.to_markdown(_result(builder))
    assert "# AIOS Forex OANDA Live Microtrade Routed Proof Owner Decision Gate V1" in text
    assert packet in text


@pytest.mark.parametrize(
    (
        "name",
        "builder",
        "classification",
        "source_status",
        "source_lane",
        "selected_lane",
        "packet",
        "proof_warning",
        "statistical_warning",
    ),
    SAMPLE_CASES,
)
def test_operator_text_outputs(
    name,
    builder,
    classification,
    source_status,
    source_lane,
    selected_lane,
    packet,
    proof_warning,
    statistical_warning,
):
    text = decision_gate.to_operator_text(_result(builder))
    assert "Routed proof owner decision status" in text
    assert packet in text


@pytest.mark.parametrize("field_name", REQUIRED_RESULT_FIELDS)
def test_required_result_fields_present(field_name: str):
    assert hasattr(_result(), field_name)


@pytest.mark.parametrize("flag_name", decision_gate.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_in_map(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize("flag_name", decision_gate.PROTECTED_FLAG_NAMES)
def test_protected_flags_false_on_result(flag_name: str):
    assert getattr(_result(), flag_name) is False


@pytest.mark.parametrize(
    "flag_name",
    (
        "next_trade_authorized",
        "selected_packet_execution_authorized",
        "selected_packet_commit_authorized",
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
        "credential_access_allowed",
        "account_id_persistence_allowed",
        "codex_live_execution_authorized",
    ),
)
def test_high_risk_flags_false(flag_name: str):
    assert getattr(_result(), flag_name) is False


@pytest.mark.parametrize(
    ("field_name", "expected"),
    (
        ("preview_only", True),
        ("decision_gate_only", True),
        ("selected_packet_preview_only", True),
        ("owner_review_required", True),
    ),
)
def test_descriptive_flags_true(field_name: str, expected: bool):
    assert getattr(_result(), field_name) is expected


def test_profit_decision_selects_profit_proof_candidate_review():
    result = _result(decision_gate.build_sample_profit_decision_input)
    assert result.selected_review_lane == "profit_proof_candidate_review"


def test_loss_decision_selects_loss_review_and_next_profit_candidate_gate():
    result = _result(decision_gate.build_sample_loss_decision_input)
    assert result.selected_review_lane == "loss_review_and_next_profit_candidate_gate"


def test_breakeven_decision_selects_more_evidence():
    result = _result(decision_gate.build_sample_breakeven_decision_input)
    assert result.selected_review_lane == "more_evidence_required"


def test_missing_decision_selects_owner_result_evidence_required():
    result = _result(decision_gate.build_sample_missing_owner_result_decision_input)
    assert result.selected_review_lane == "owner_result_evidence_required"
    assert "owner_result_payload_missing" in result.blocked_items


def test_unsafe_decision_selects_unsafe_result_repair():
    result = _result(decision_gate.build_sample_unsafe_decision_input)
    assert result.selected_review_lane == "unsafe_result_repair"
    assert "unsafe_result_material_blocks_owner_decision" in result.blocked_items


def test_exact_next_owner_action_present():
    assert _result().exact_next_owner_action == decision_gate.EXACT_NEXT_OWNER_ACTION


def test_exact_next_codex_packet_policy_present():
    assert (
        _result().exact_next_codex_packet_policy
        == decision_gate.EXACT_NEXT_CODEX_PACKET_POLICY
    )


def test_one_sentence_answer_exact():
    assert _result().one_sentence_answer == decision_gate.ONE_SENTENCE_ANSWER


def test_required_owner_action_matches_exact_next_owner_action():
    result = _result()
    assert result.required_owner_action == result.exact_next_owner_action


def test_mapping_router_output_can_be_evaluated():
    source_result = source_router.to_jsonable_dict(
        source_router.route_oanda_live_microtrade_result_to_next_proof(
            source_router.build_sample_profit_router_input()
        )
    )
    result = decision_gate.evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate(
        {"router_input": source_result}
    )
    assert result.selected_review_lane == "profit_proof_candidate_review"


def test_raw_router_input_can_be_evaluated():
    result = decision_gate.evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate(
        {"router_input": source_router.build_sample_profit_router_input()}
    )
    assert result.selected_review_lane == "profit_proof_candidate_review"


def test_unsafe_owner_decision_label_does_not_authorize():
    result = decision_gate.evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate(
        {
            "router_input": source_router.build_sample_profit_router_input(),
            "owner_decision_label": "approve next live trade",
        }
    )
    assert result.owner_decision_label == "pending_owner_review"
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


@pytest.mark.parametrize(
    "fragment",
    (
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "import subprocess",
        "def place_order",
        "def submit_order",
        "def execute_order",
        ".env",
    ),
)
def test_static_safety_no_forbidden_fragments_in_runner(fragment: str):
    assert fragment not in RUNNER_PATH.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize(
    "path", (MODULE_PATH, RUNNER_PATH, TEST_PATH, REPORT_PATH, MANUAL_REPORT_PATH)
)
def test_created_paths_exist(path: Path):
    assert path.exists()


@pytest.mark.parametrize("phrase", REPORT_SAFETY_PHRASES)
def test_report_required_safety_phrases(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "heading",
    (
        "# AIOS Forex OANDA Live Microtrade Routed Proof Owner Decision Gate V1",
        "## Packet ID",
        "## Source Chain Read",
        "## Files Created",
        "## Decision Classifications",
        "## Decision Mapping",
        "## Profit Sample Decision",
        "## Loss Sample Decision",
        "## Breakeven Sample Decision",
        "## Missing Owner Result Sample Decision",
        "## Unsafe Sample Decision",
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
        "python -m py_compile automation/forex_engine/oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py scripts/forex_delivery/run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py tests/forex_engine/test_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py",
        "python -m pytest tests/forex_engine/test_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py -q",
        "python scripts/forex_delivery/run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py --sample-profit --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py --sample-loss --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py --sample-breakeven --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py --sample-missing --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py --sample-unsafe --json",
        "python scripts/forex_delivery/run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.py --sample-profit --markdown",
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
            decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW,
        ),
        (
            ["runner", "--sample-loss", "--json"],
            "loss_review_and_next_profit_candidate_gate",
        ),
        (
            ["runner", "--sample-breakeven", "--json"],
            decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_REQUIRE_MORE_EVIDENCE,
        ),
        (
            ["runner", "--sample-missing", "--json"],
            decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_NO_OWNER_RESULT,
        ),
        (
            ["runner", "--sample-unsafe", "--json"],
            decision_gate.OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_UNSAFE,
        ),
        (
            ["runner", "--sample-profit", "--markdown"],
            "# AIOS Forex OANDA Live Microtrade Routed Proof Owner Decision Gate V1",
        ),
    ),
)
def test_runner_outputs(monkeypatch, capsys, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert run_oanda_live_microtrade_routed_proof_owner_decision_gate_v1.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize(
    "phrase",
    (
        "profit route -> profit proof candidate review preview",
        "loss route -> loss review and next profit candidate gate preview",
        "breakeven route -> more evidence preview",
        "missing owner result route -> owner result evidence required preview",
        "unsafe result route -> unsafe result repair preview",
    ),
)
def test_report_decision_mapping_phrases(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "phrase",
    (
        "Profit route is a proof candidate only, not approval for repeat trading.",
        "One result does not prove statistical profitability.",
        "Loss route must repair candidate evidence before any future owner decision.",
        "One loss does not prove the system is invalid, but it blocks profit proof.",
        "Evidence is insufficient for proof promotion.",
        "Additional sanitized results are required.",
        "owner_result_payload_missing",
        "unsafe_result_material_blocks_owner_decision",
    ),
)
def test_report_decision_warnings_and_blocks(phrase: str):
    assert phrase in REPORT_PATH.read_text(encoding="utf-8")
