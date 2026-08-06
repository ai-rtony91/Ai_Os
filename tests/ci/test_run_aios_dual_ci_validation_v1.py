import importlib.util
import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts/ci/run_aios_dual_ci_validation_v1.py"
SPEC = importlib.util.spec_from_file_location("dual_ci", SCRIPT)
dual_ci = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dual_ci)
SHA = "a" * 40


def result(code=0, stdout=""):
    return subprocess.CompletedProcess([], code, stdout, "")


def passing_run(argv):
    return result(stdout=SHA + "\n") if argv[:2] == ("git", "rev-parse") else result()


def test_exact_sha_and_exact_schema_pass(monkeypatch):
    monkeypatch.setattr(dual_ci, "_execute", lambda *args: (True, "ok"))
    receipt = dual_ci.validate(SHA, passing_run)
    assert receipt["schema"] == "AIOS_DUAL_CI_RECEIPT_V1"
    assert receipt["state"] == "VALIDATION_PASS"
    assert receipt["expected_sha"] == receipt["checked_out_sha"] == SHA
    assert len(receipt["expected_sha"]) == 40
    assert len(receipt["runner_sha256"]) == 64
    assert receipt["command_ids"] == list(dual_ci.COMMAND_IDS)


def test_sha_mismatch_blocks_before_commands(monkeypatch):
    monkeypatch.setattr(dual_ci, "_execute", lambda *args: (_ for _ in ()).throw(AssertionError()))
    assert dual_ci.validate("b" * 40, passing_run)["state"] == "SHA_MISMATCH_BLOCKED"


def test_missing_or_failed_command_fails(monkeypatch):
    monkeypatch.setattr(dual_ci, "COMMANDS", (("missing.command", ()),))
    assert dual_ci.validate(SHA, passing_run)["state"] == "VALIDATION_FAILED"


def test_receipt_serializes_without_environment_or_network(monkeypatch):
    monkeypatch.setattr(dual_ci, "_execute", lambda *args: (True, "ok"))
    receipt = dual_ci.validate(SHA, passing_run)
    encoded = json.dumps(receipt)
    assert "environment" not in encoded.lower()
    assert "credential" not in encoded.lower()
    assert "oanda" not in encoded.lower()
    assert "deployment" not in encoded.lower()


def test_validation_does_not_mutate_repository(monkeypatch):
    monkeypatch.setattr(dual_ci, "_execute", lambda *args: (True, "ok"))
    before = subprocess.check_output(("git", "status", "--porcelain"), cwd=dual_ci.ROOT)
    dual_ci.validate(SHA, passing_run)
    after = subprocess.check_output(("git", "status", "--porcelain"), cwd=dual_ci.ROOT)
    assert after == before


def test_equivalence_requires_same_sha_and_all_passes(monkeypatch):
    monkeypatch.setattr(dual_ci, "_execute", lambda *args: (True, "ok"))
    github = dual_ci.validate(SHA, passing_run)
    azure = json.loads(json.dumps(github))
    assert dual_ci.equivalent_validation_pass(github, azure)
    azure["expected_sha"] = "b" * 40
    assert not dual_ci.equivalent_validation_pass(github, azure)


def test_provider_success_never_authorizes_merge(monkeypatch):
    monkeypatch.setattr(dual_ci, "_execute", lambda *args: (True, "ok"))
    assert dual_ci.validate(SHA, passing_run)["merge_authorized"] is False
