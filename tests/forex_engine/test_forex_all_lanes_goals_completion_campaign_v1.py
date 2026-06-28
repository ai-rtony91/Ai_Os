from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine import forex_all_lanes_completion_orchestrator_v1 as orchestrator_lib
from automation.forex_engine import forex_all_lanes_completion_router_v1 as router_lib
from automation.forex_engine import forex_all_lanes_final_bundle_v1 as final_bundle_lib
from automation.forex_engine import forex_all_lanes_gap_classifier_v1 as classifier_lib
from automation.forex_engine import forex_all_lanes_goal_manifest_v1 as manifest_lib
from automation.forex_engine import forex_all_lanes_operating_readiness_projector_v1 as projector_lib
from automation.forex_engine import forex_all_lanes_owner_boundary_gate_v1 as owner_gate_lib
from scripts.forex_delivery import run_forex_all_lanes_completion_orchestrator_v1 as orchestrator_runner
from scripts.forex_delivery import run_forex_all_lanes_completion_router_v1 as router_runner
from scripts.forex_delivery import run_forex_all_lanes_final_bundle_v1 as final_bundle_runner
from scripts.forex_delivery import run_forex_all_lanes_gap_classifier_v1 as classifier_runner
from scripts.forex_delivery import run_forex_all_lanes_goal_manifest_v1 as manifest_runner
from scripts.forex_delivery import run_forex_all_lanes_operating_readiness_projector_v1 as projector_runner
from scripts.forex_delivery import run_forex_all_lanes_owner_boundary_gate_v1 as owner_gate_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "forex_delivery" / "all_lanes_goals_completion_campaign_v1"

MODULE_PATHS = [
    REPO_ROOT / "automation" / "forex_engine" / "forex_all_lanes_goal_manifest_v1.py",
    REPO_ROOT / "automation" / "forex_engine" / "forex_all_lanes_gap_classifier_v1.py",
    REPO_ROOT / "automation" / "forex_engine" / "forex_all_lanes_completion_router_v1.py",
    REPO_ROOT / "automation" / "forex_engine" / "forex_all_lanes_operating_readiness_projector_v1.py",
    REPO_ROOT / "automation" / "forex_engine" / "forex_all_lanes_owner_boundary_gate_v1.py",
    REPO_ROOT / "automation" / "forex_engine" / "forex_all_lanes_final_bundle_v1.py",
    REPO_ROOT / "automation" / "forex_engine" / "forex_all_lanes_completion_orchestrator_v1.py",
]

SCRIPT_PATHS = [
    REPO_ROOT / "scripts" / "forex_delivery" / "run_forex_all_lanes_goal_manifest_v1.py",
    REPO_ROOT / "scripts" / "forex_delivery" / "run_forex_all_lanes_gap_classifier_v1.py",
    REPO_ROOT / "scripts" / "forex_delivery" / "run_forex_all_lanes_completion_router_v1.py",
    REPO_ROOT / "scripts" / "forex_delivery" / "run_forex_all_lanes_operating_readiness_projector_v1.py",
    REPO_ROOT / "scripts" / "forex_delivery" / "run_forex_all_lanes_owner_boundary_gate_v1.py",
    REPO_ROOT / "scripts" / "forex_delivery" / "run_forex_all_lanes_final_bundle_v1.py",
    REPO_ROOT / "scripts" / "forex_delivery" / "run_forex_all_lanes_completion_orchestrator_v1.py",
]

FIXTURE_PATHS = sorted(FIXTURE_DIR.glob("*.json")) if FIXTURE_DIR.exists() else []
STATUS_VALUES = sorted(manifest_lib.ALLOWED_STATUSES)


def _load_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fixture_directory_exists() -> None:
    assert FIXTURE_DIR.exists()


def test_fixture_directory_has_at_least_55_files() -> None:
    assert len(FIXTURE_PATHS) >= 55


@pytest.mark.parametrize("fixture_path", FIXTURE_PATHS)
def test_fixture_file_is_valid_json(fixture_path: Path) -> None:
    payload = _load_fixture(fixture_path)
    assert payload["fixture_version"] == "1.0"
    assert payload["packet_id"] == manifest_lib.PACKET_ID


@pytest.mark.parametrize("fixture_path", FIXTURE_PATHS)
def test_fixture_status_is_allowed(fixture_path: Path) -> None:
    payload = _load_fixture(fixture_path)
    assert payload["expected_status"] in manifest_lib.ALLOWED_STATUSES


@pytest.mark.parametrize("fixture_path", FIXTURE_PATHS)
def test_fixture_preserves_no_execution_boundary(fixture_path: Path) -> None:
    payload = _load_fixture(fixture_path)
    safety = payload["safety"]
    assert safety["broker_api_calls"] is False
    assert safety["credential_access"] is False
    assert safety["demo_live_execution"] is False
    assert safety["money_movement"] is False
    assert safety["production_activation"] is False
    assert safety["profit_claims"] is False


@pytest.mark.parametrize("fixture_path", FIXTURE_PATHS)
def test_fixture_has_required_goal_fields(fixture_path: Path) -> None:
    payload = _load_fixture(fixture_path)
    goal = payload["goal"]
    for key in (
        "goal_id",
        "source_file_path",
        "source_type",
        "current_status",
        "blocker_class",
        "repo_actionable",
        "protected_owner_required",
        "external_evidence_required",
        "safety_class",
        "proposed_closure_action",
        "target_artifact",
        "validation_required",
        "completion_status",
    ):
        assert key in goal


@pytest.mark.parametrize("status", STATUS_VALUES)
def test_allowed_statuses_round_trip(status: str) -> None:
    assert status in manifest_lib.ALLOWED_STATUSES


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_campaign_modules_exist(module_path: Path) -> None:
    assert module_path.exists()


@pytest.mark.parametrize("script_path", SCRIPT_PATHS)
def test_campaign_scripts_exist(script_path: Path) -> None:
    assert script_path.exists()


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_campaign_modules_have_no_forbidden_runtime_imports(module_path: Path) -> None:
    text = module_path.read_text(encoding="utf-8").lower()
    forbidden = ("import subprocess", "from subprocess", "import requests", "import socket", "import urllib")
    assert not any(item in text for item in forbidden)


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_campaign_modules_do_not_read_environment(module_path: Path) -> None:
    text = module_path.read_text(encoding="utf-8").lower()
    assert "os.environ" not in text
    assert "getenv(" not in text
    assert ".env" not in text


@pytest.mark.parametrize("script_path", SCRIPT_PATHS)
def test_campaign_scripts_do_not_embed_git_or_gh_commands(script_path: Path) -> None:
    text = script_path.read_text(encoding="utf-8").lower()
    assert "git add" not in text
    assert "git commit" not in text
    assert "git push" not in text
    assert "gh pr" not in text


def test_manifest_builds_repo_derived_goals() -> None:
    manifest = manifest_lib.build_all_lanes_goal_manifest(repo_root=REPO_ROOT, strict=True)
    assert manifest["goal_count"] >= len(manifest_lib.BRANCH_SIGNAL_HINTS)
    assert manifest["repo_actionable_open_count"] == 0
    assert manifest["safety"]["broker_api_calls"] is False


def test_manifest_contains_campaign_artifacts_as_closed_by_campaign() -> None:
    manifest = manifest_lib.build_all_lanes_goal_manifest(repo_root=REPO_ROOT, strict=True)
    by_path = {goal["source_file_path"]: goal for goal in manifest["goals"]}
    existing_campaign_paths = [
        path
        for path in manifest_lib.CAMPAIGN_ARTIFACTS
        if (REPO_ROOT / path).exists()
    ]
    assert existing_campaign_paths
    for path in existing_campaign_paths[:20]:
        assert by_path[path]["current_status"] == manifest_lib.CLOSED_BY_THIS_CAMPAIGN


def test_manifest_goal_records_have_all_required_packet_fields() -> None:
    manifest = manifest_lib.build_all_lanes_goal_manifest(repo_root=REPO_ROOT, strict=True)
    for goal in manifest["goals"][:50]:
        assert goal["goal_id"]
        assert goal["source_type"] in {
            "module",
            "script",
            "test",
            "report",
            "doc",
            "schema",
            "branch",
            "epic",
            "fixture",
        }
        assert goal["current_status"] in manifest_lib.ALLOWED_STATUSES
        assert isinstance(goal["repo_actionable"], bool)


def test_classifier_closes_repo_actionable_work() -> None:
    manifest = manifest_lib.build_all_lanes_goal_manifest(repo_root=REPO_ROOT, strict=True)
    classifier = classifier_lib.classify_all_lanes_gaps(manifest)
    assert classifier["repo_actionable_open_count"] == 0
    assert classifier["repo_actionable_closed_count"] > 0


def test_classifier_reports_remaining_owner_or_external_gaps() -> None:
    manifest = manifest_lib.build_all_lanes_goal_manifest(repo_root=REPO_ROOT, strict=True)
    classifier = classifier_lib.classify_all_lanes_gaps(manifest)
    assert classifier["remaining_gap_count"] >= 0
    assert classifier["status"] in {
        classifier_lib.CLASSIFIER_ALL_REPO_ACTIONABLE_CLOSED,
        classifier_lib.CLASSIFIER_OWNER_REVIEW_REQUIRED,
    }


def test_router_separates_closed_and_protected_routes() -> None:
    manifest = manifest_lib.build_all_lanes_goal_manifest(repo_root=REPO_ROOT, strict=True)
    classifier = classifier_lib.classify_all_lanes_gaps(manifest)
    router = router_lib.route_all_lanes_completion(manifest, classifier)
    data = router_lib.router_to_jsonable_dict(router)
    assert data["route"] == router_lib.ROUTE_ALL_REPO_ACTIONABLE_CLOSED
    assert data["closed_by_this_campaign_count"] > 0
    assert data["repo_actionable_open_count"] == 0


def test_projector_defers_operating_readiness_to_owner() -> None:
    manifest = manifest_lib.build_all_lanes_goal_manifest(repo_root=REPO_ROOT, strict=True)
    classifier = classifier_lib.classify_all_lanes_gaps(manifest)
    router = router_lib.route_all_lanes_completion(manifest, classifier)
    projection = projector_lib.project_all_lanes_operating_readiness(router)
    assert projection["final_operating_readiness_status"] == projector_lib.DEFERRED_OWNER_VALIDATION
    assert projection["readiness_flags"]["demo_live_execution_allowed"] is False
    assert projection["readiness_flags"]["profit_claim_supported"] is False


def test_owner_boundary_gate_blocks_protected_actions() -> None:
    boundary = owner_gate_lib.evaluate_all_lanes_owner_boundary()
    flags = boundary["boundary_flags"]
    assert boundary["status"] == owner_gate_lib.OWNER_BOUNDARY_ENFORCED
    assert flags["auto_approval_allowed"] is False
    assert flags["broker_api_called"] is False
    assert flags["money_moved"] is False


def test_final_bundle_contains_owner_publish_and_merge_blocks() -> None:
    bundle = final_bundle_lib.build_all_lanes_final_bundle()
    assert "git status --short --branch --untracked-files=all" in bundle["owner_publish_block"]
    assert "git add -- $campaignFiles" in bundle["owner_publish_block"]
    assert "gh pr checks PR_NUMBER --watch" in bundle["owner_merge_sync_block"]
    assert bundle["status"] == final_bundle_lib.FINAL_BUNDLE_DEFERRED_OWNER_VALIDATION


def test_final_bundle_file_list_is_campaign_scoped() -> None:
    files = final_bundle_lib.campaign_file_list()
    assert "automation/forex_engine/forex_all_lanes_goal_manifest_v1.py" in files
    assert "tests/forex_engine/test_forex_all_lanes_goals_completion_campaign_v1.py" in files
    assert all(
        path.startswith(
            (
                "automation/forex_engine/",
                "scripts/forex_delivery/",
                "tests/forex_engine/",
                "tests/fixtures/forex_delivery/",
                "docs/workflows/",
                "docs/governance/programs/epics/",
                "schemas/aios/forex/",
                "Reports/forex_delivery/",
            ),
        )
        for path in files
    )


def test_orchestrator_runs_all_stages() -> None:
    result = orchestrator_lib.run_all_lanes_completion_orchestrator(repo_root=REPO_ROOT, strict=True)
    assert result["status"] == orchestrator_lib.ORCHESTRATOR_DEFERRED_OWNER_VALIDATION
    assert result["manifest"]["goal_count"] > 0
    assert result["checkpoint"]["events"]


def test_orchestrator_markdown_includes_required_final_status() -> None:
    result = orchestrator_lib.run_all_lanes_completion_orchestrator(repo_root=REPO_ROOT, strict=True)
    markdown = orchestrator_lib.orchestrator_to_markdown(result)
    assert "final status: DEFERRED_OWNER_VALIDATION" in markdown
    assert "Exact Owner PowerShell Publish / Check Block" in markdown


def test_orchestrator_report_writer_uses_report_directory(tmp_path: Path) -> None:
    result = orchestrator_lib.run_all_lanes_completion_orchestrator(repo_root=tmp_path, strict=True)
    orchestrator_lib.write_orchestrator_reports(result, repo_root=tmp_path)
    report = tmp_path / "Reports" / "forex_delivery" / "AIOS_FOREX_ALL_LANES_GOALS_COMPLETION_CAMPAIGN_V1_REPORT.md"
    assert report.exists()
    assert "DEFERRED_OWNER_VALIDATION" in report.read_text(encoding="utf-8")


def test_schema_is_valid_json() -> None:
    path = REPO_ROOT / "schemas" / "aios" / "forex" / "FOREX_ALL_LANES_GOALS_COMPLETION_CAMPAIGN.v1.schema.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["title"] == "AIOS Forex All-Lanes Goals Completion Campaign V1"


def test_goal_manifest_cli_json_output() -> None:
    output = manifest_runner.run_cli(["--repo-root", str(REPO_ROOT), "--json", "--strict"])
    payload = json.loads(output)
    assert payload["packet_id"] == manifest_lib.PACKET_ID


def test_gap_classifier_cli_markdown_output() -> None:
    output = classifier_runner.run_cli(["--repo-root", str(REPO_ROOT), "--strict"])
    assert "AIOS Forex All-Lanes Gap Classifier V1" in output


def test_completion_router_cli_markdown_output() -> None:
    output = router_runner.run_cli(["--repo-root", str(REPO_ROOT), "--strict"])
    assert "AIOS Forex All-Lanes Completion Router V1" in output


def test_operating_readiness_cli_markdown_output() -> None:
    output = projector_runner.run_cli(["--repo-root", str(REPO_ROOT), "--strict"])
    assert "Operating Readiness Projector" in output


def test_owner_boundary_cli_markdown_output() -> None:
    output = owner_gate_runner.run_cli(["--repo-root", str(REPO_ROOT), "--strict"])
    assert "Owner Boundary Gate" in output


def test_final_bundle_cli_markdown_output() -> None:
    output = final_bundle_runner.run_cli(["--repo-root", str(REPO_ROOT), "--strict"])
    assert "Final Bundle" in output


def test_orchestrator_cli_markdown_output() -> None:
    output = orchestrator_runner.run_cli(["--repo-root", str(REPO_ROOT), "--strict"])
    assert "Goals Completion Campaign V1 Report" in output
