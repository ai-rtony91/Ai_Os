import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/ci/run_aios_dual_ci_validation_v1.py"
SPEC = importlib.util.spec_from_file_location("dual_ci", RUNNER)
dual_ci = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dual_ci)


def receipt(provider="GITHUB_ACTIONS"):
    sha = "a" * 40
    return {
        "schema": dual_ci.SCHEMA, "provider": provider, "state": "VALIDATION_PASS",
        "expected_sha": sha, "checked_out_sha": sha, "runner_sha256": "b" * 64,
        "command_manifest_sha256": "c" * 64, "python_version": "3.12.4",
        "dependency_lock_sha256": "d" * 64,
        "command_ids": list(dual_ci.REQUIRED_COMMAND_IDS),
        "commands": [{"id": x, "state": "PASS"} for x in dual_ci.REQUIRED_COMMAND_IDS],
        "merge_authorized": False,
    }


def test_stable_command_ids_preserve_all_legacy_protections():
    assert dual_ci.REQUIRED_COMMAND_IDS == (
        "static.required_governance_files", "static.workflow_shape",
        "syntax.powershell_tracked", "syntax.python_tracked_core",
        "static.placeholder_identity", "static.secret_assignments",
        "compile.phase_bridge", "compile.governance_validator",
        "compile.assignment_executor", "compile.assignment_validator",
        "compile.self_build_inspector", "sample.governance_validator",
        "sample.assignment_validator",
    )


def test_tracked_inventory_uses_git_and_excludes_untracked(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "tracked.py").write_text("x=1")
    (tmp_path / "untracked.py").write_text("bad syntax (")
    subprocess.run(["git", "add", "tracked.py"], cwd=tmp_path, check=True)
    assert dual_ci.tracked_files(tmp_path) == ["tracked.py"]


def test_python_core_compiles_tracked_only(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/good.py").write_text("x=1")
    (tmp_path / "scripts/untracked.py").write_text("bad syntax (")
    dual_ci._python_core(tmp_path, ["scripts/good.py"])
    assert not list(tmp_path.rglob("__pycache__"))


def test_powershell_parser_covers_each_tracked_ps1(monkeypatch, tmp_path):
    calls = []
    def fake_run(args, root, text=True):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "7.4", "")
    monkeypatch.setattr(dual_ci, "_run", fake_run)
    dual_ci._powershell(tmp_path, ["a.ps1", "nested/b.ps1", "not.psm1"])
    assert [c[-1] for c in calls[1:]] == ["a.ps1", "nested/b.ps1"]


def test_missing_pwsh_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(dual_ci, "_run", lambda *a, **k: subprocess.CompletedProcess([], 127, "", "missing"))
    with pytest.raises(dual_ci.ValidationBlocked, match="POWERSHELL_UNAVAILABLE_BLOCKED"):
        dual_ci._powershell(tmp_path, [])


def test_sha_mismatch_blocks_before_inventory(monkeypatch, tmp_path):
    monkeypatch.setattr(dual_ci, "checked_out_sha", lambda root: "b" * 40)
    monkeypatch.setattr(dual_ci, "tracked_files", lambda root: pytest.fail("commands began"))
    with pytest.raises(dual_ci.ValidationBlocked, match="SHA_MISMATCH_BLOCKED"):
        dual_ci.run_validation(tmp_path, "LOCAL_VALIDATION", "a" * 40)


@pytest.mark.parametrize("value", ["", "A" * 40, "a" * 39, "unknown"])
def test_missing_or_malformed_azure_pr_sha_blocks_without_fallback(value):
    env = {"BUILD_REASON": "PullRequest", "SYSTEM_PULLREQUEST_SOURCECOMMITID": value, "BUILD_SOURCEVERSION": "a" * 40}
    with pytest.raises(dual_ci.ValidationBlocked, match="SHA_SOURCE_UNAVAILABLE_BLOCKED"):
        dual_ci.resolve_azure_expected_sha(env)


def test_non_pr_azure_may_use_build_source_version():
    assert dual_ci.resolve_azure_expected_sha({"BUILD_REASON": "Manual", "BUILD_SOURCEVERSION": "a" * 40}) == "a" * 40


def test_equivalence_passes_for_distinct_required_providers():
    assert dual_ci.equivalent(receipt(), receipt("AZURE_PIPELINES")) == "EQUIVALENT_VALIDATION_PASS"


@pytest.mark.parametrize("second", ["GITHUB_ACTIONS", "LOCAL_VALIDATION"])
def test_same_or_wrong_provider_equivalence_blocks(second):
    with pytest.raises(dual_ci.ValidationBlocked, match="PROVIDER_MISMATCH_BLOCKED"):
        dual_ci.equivalent(receipt(), receipt(second))


@pytest.mark.parametrize("field", ["runner_sha256", "command_manifest_sha256", "dependency_lock_sha256", "expected_sha"])
def test_equivalence_identity_mismatch_blocks(field):
    other = receipt("AZURE_PIPELINES")
    other[field] = "e" * (40 if field == "expected_sha" else 64)
    if field == "expected_sha": other["checked_out_sha"] = other[field]
    with pytest.raises(dual_ci.ValidationBlocked, match="EQUIVALENCE_MISMATCH_BLOCKED"):
        dual_ci.equivalent(receipt(), other)


def test_empty_command_results_block():
    other = receipt("AZURE_PIPELINES"); other["commands"] = []
    with pytest.raises(dual_ci.ValidationBlocked, match="COMMAND_SET_INVALID_BLOCKED"):
        dual_ci.equivalent(receipt(), other)


def test_merge_authorized_true_always_blocks():
    other = receipt("AZURE_PIPELINES"); other["merge_authorized"] = True
    with pytest.raises(dual_ci.ValidationBlocked, match="RECEIPT_INVALID_BLOCKED"):
        dual_ci.equivalent(receipt(), other)


def test_workflows_are_evidence_only_exact_sha_and_no_pr_fallback():
    github = (ROOT / ".github/workflows/ci.yml").read_text()
    azure = (ROOT / "azure-pipelines.yml").read_text()
    assert "pull_request.head.sha" in github and "persist-credentials: false" in github
    pr_block = azure.split('if [[ "${BUILD_REASON:-}" == PullRequest ]]')[1].split("else")[0]
    assert "SYSTEM_PULLREQUEST_SOURCECOMMITID" in pr_block
    assert "BUILD_SOURCEVERSION" not in pr_block
    forbidden = ("AzureCLI", "AzureWebApp", "subscription", "deployment:", "environment:", "variable group", "secure file", "publish profile", "OANDA", "broker credentials", "git merge")
    assert not any(word.lower() in azure.lower() for word in forbidden)


def test_runner_has_no_network_or_credential_access_and_receipt_outside_repo():
    source = RUNNER.read_text()
    assert "requests" not in source and "urllib" not in source and "socket" not in source
    assert ".env" not in source and "credentials/" not in source
    assert "runner.temp" in (ROOT / ".github/workflows/ci.yml").read_text()
    assert "AGENT_TEMPDIRECTORY" in (ROOT / "azure-pipelines.yml").read_text()
