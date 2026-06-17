from pathlib import Path
import inspect
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import forex_delivery.live_arming_evidence_gap as gap  # noqa: E402


def test_gap_analysis_uses_existing_artifacts_and_remains_blocked():
    analysis = gap.build_live_arming_evidence_gap_analysis(repo_root=REPO_ROOT)

    assert analysis["status"] == "BLOCKED_PENDING_HUMAN_OWNER_EXCEPTION_EVIDENCE"
    assert analysis["missing_artifact_paths"] == []
    assert set(analysis["missing_exception_fields"]) == set(
        analysis["required_exception_fields"]
    )
    assert analysis["ready_for_live_arming_review"] is False
    assert analysis["live_execution_allowed"] is False
    assert analysis["order_submit_allowed"] is False
    assert analysis["live_submit_probe"]["blocked"] is True
    assert analysis["requirements"] == {
        "credentials_required": False,
        "network_required": False,
        "broker_sdk_required": False,
        "account_identifiers_required": False,
        "orders_required": False,
        "trades_required": False,
    }
    assert all(value is False for value in analysis["no_live_action_confirmation"].values())


def test_gap_analysis_fails_closed_when_expected_artifacts_are_absent(tmp_path):
    analysis = gap.build_live_arming_evidence_gap_analysis(repo_root=tmp_path)

    assert analysis["status"] == "BLOCKED_EVIDENCE_ARTIFACTS_MISSING"
    assert len(analysis["missing_artifact_paths"]) == len(gap.EXPECTED_EVIDENCE_ARTIFACTS)
    assert analysis["live_submit_probe"]["blocked"] is True
    assert analysis["ready_for_live_arming_review"] is False


def test_gap_analysis_flags_unexpected_live_submit_success(monkeypatch):
    monkeypatch.setattr(gap, "submit_live_order", lambda _: None)

    analysis = gap.build_live_arming_evidence_gap_analysis(repo_root=REPO_ROOT)

    assert analysis["status"] == "UNSAFE_LIVE_SUBMIT_NOT_BLOCKED"
    assert analysis["live_submit_probe"]["blocked"] is False
    assert analysis["ready_for_live_arming_review"] is False
    assert analysis["live_execution_allowed"] is False


def test_gap_markdown_contains_required_sections_without_secret_shapes():
    analysis = gap.build_live_arming_evidence_gap_analysis(repo_root=REPO_ROOT)
    markdown = gap.render_live_arming_evidence_gap_markdown(analysis)

    required_sections = (
        "## Existing Readiness Gates Found",
        "## Existing OANDA Demo/Paper Artifacts Found",
        "## Missing Evidence",
        "## Hard Blockers",
        "## Human Approval Gates Required Later",
        "## Strictly Paper/Demo Only",
        "## No-Live-Action Confirmation",
        "## Exact Next Packet Recommendation",
    )
    for section in required_sections:
        assert section in markdown

    forbidden_secret_shapes = (
        "sk-",
        "Bearer ",
        "Authorization:",
        "BEGIN PRIVATE KEY",
        "password=",
        "api_key=",
    )
    for secret_shape in forbidden_secret_shapes:
        assert secret_shape not in markdown


def test_gap_module_does_not_add_runtime_or_broker_dependencies():
    source = inspect.getsource(gap)

    forbidden_implementation_markers = (
        "os.environ",
        "dotenv",
        "requests",
        "urllib",
        "socket",
        "oandapy",
        "run_governed_paper_flow",
        "create_order(",
    )
    for marker in forbidden_implementation_markers:
        assert marker not in source
