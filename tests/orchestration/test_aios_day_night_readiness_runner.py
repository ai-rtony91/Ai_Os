from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "automation/orchestration/supervisor/Get-AiOsDayNightReadiness.DRY_RUN.ps1"
PACKET_ROUTER_RUNNER = REPO_ROOT / "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1"
SELF_AUDIT_RUNNER = REPO_ROOT / "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1"
VALIDATOR_ROUTER_RUNNER = REPO_ROOT / "automation/orchestration/validators/Get-AiOsValidatorEvidenceRouter.DRY_RUN.ps1"


def _run_runner(*args: str, cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RUNNER),
            *args,
        ],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"runner failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    return result


def _file_set(root: Path, relative: str) -> set[str]:
    target = root / relative
    if not target.exists():
        return set()
    return {
        str(path.relative_to(root)).replace("\\", "/")
        for path in target.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def test_runner_has_no_forbidden_parameters() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    match = re.search(r"param\((.*?)\)\s*Set-StrictMode", text, flags=re.DOTALL)

    assert match is not None
    param_block = match.group(1)
    for forbidden in ("OutputPath", "$Mode", "$Apply", "$Write", "$Persist", "StartRuntime", "LaunchWorker", "Schedule"):
        assert forbidden not in param_block


def test_runner_emits_json_only_with_output_json() -> None:
    result = _run_runner("-OutputJson")
    raw = result.stdout.strip()
    parsed = json.loads(raw)

    assert raw.startswith("{")
    assert "AIOS Day Night Readiness" not in raw
    assert parsed["schema"] == "AIOS_DAY_NIGHT_READINESS_RESULT.v1"


def test_runner_console_mode_includes_expected_sections() -> None:
    result = _run_runner()
    out = result.stdout

    for section in (
        "CURRENT STATE",
        "READINESS",
        "OPERATOR MODES",
        "EVIDENCE SOURCES",
        "VALIDATOR STATUS",
        "APPROVAL STATE",
        "RUNTIME WORKER STATE",
        "BACKUP INTERFERENCE",
        "NO-WRITE PROOF",
        "STOP CONDITIONS",
        "NEXT SAFE ACTION",
    ):
        assert section in out


def test_runner_refuses_dirty_worktree_outside_exact_allowed_files(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=str(tmp_path), text=True, capture_output=True, check=False)
    if subprocess.run(["git", "branch", "--show-current"], cwd=str(tmp_path), text=True, capture_output=True).stdout.strip() != "main":
        subprocess.run(["git", "checkout", "-b", "main"], cwd=str(tmp_path), text=True, capture_output=True, check=False)

    (tmp_path / "AGENTS.md").write_text("authority\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("front door\n", encoding="utf-8")
    (tmp_path / "RISK_POLICY.md").write_text("risk\n", encoding="utf-8")
    contract = tmp_path / "docs/AI_OS/autonomy/AIOS_SELF_AUDIT_LOOP_CONTRACT_V1.md"
    contract.parent.mkdir(parents=True)
    contract.write_text("contract\n", encoding="utf-8")
    governance = tmp_path / "docs/governance"
    governance.mkdir(parents=True)
    (governance / "aios-identity-and-lane-governance.md").write_text("identity\n", encoding="utf-8")
    (governance / "AI_OS_REPO_MEMORY.md").write_text("memory\n", encoding="utf-8")

    result = _run_runner("-RepoRoot", str(tmp_path), "-OutputJson", cwd=tmp_path, check=False)
    parsed = json.loads(result.stdout)

    assert result.returncode != 0
    assert parsed["readiness"]["classification"] == "BLOCKED_BY_DIRTY_REPO"
    assert "DIRTY_WORKTREE" in parsed["stop_conditions"]
    assert parsed["repo_state"]["dirty_allowed_for_day_night_readiness_validation"] is False


def test_runner_no_write_proof_does_not_create_forbidden_files() -> None:
    protected_roots = [
        "Reports",
        "telemetry",
        "automation/orchestration/work_packets",
        "control/relay_bus/messages",
        "automation/orchestration/queue",
        "automation/orchestration/command_queue",
        "automation/orchestration/locks",
        "automation/orchestration/approval_inbox",
        "automation/orchestration/runtime",
        "automation/orchestration/workers/inbox",
    ]
    before = {root: _file_set(REPO_ROOT, root) for root in protected_roots}
    result = _run_runner("-OutputJson")
    after = {root: _file_set(REPO_ROOT, root) for root in protected_roots}
    parsed = json.loads(result.stdout)

    assert parsed["safety"]["writes_files"] is False
    assert parsed["no_write_proof"]["changed"] is False
    assert before == after


def test_runner_no_write_proof_contains_forbidden_delta_detection() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert "forbidden_surface_changed" in text
    assert "Compare-NoWriteState" in text
    assert "automation/orchestration/work_packets" in text


def test_prior_routers_allow_exact_day_night_files_without_broad_directory() -> None:
    expected = (
        "automation/orchestration/supervisor/Get-AiOsDayNightReadiness.DRY_RUN.ps1",
        "automation/orchestration/supervisor/aios_day_night_readiness.py",
        "schemas/aios/orchestration/AIOS_DAY_NIGHT_READINESS_RESULT.v1.schema.json",
        "tests/orchestration/test_aios_day_night_readiness.py",
        "tests/orchestration/test_aios_day_night_readiness_runner.py",
    )
    for runner, function_name in (
        (PACKET_ROUTER_RUNNER, "Test-RouterValidationDirtyState"),
        (SELF_AUDIT_RUNNER, "Test-SelfAuditValidationDirtyState"),
        (VALIDATOR_ROUTER_RUNNER, "Test-ValidatorEvidenceRouterDirtyState"),
    ):
        text = runner.read_text(encoding="utf-8")
        match = re.search(
            rf"function {function_name} \{{(.*?)function ConvertTo-StableJson",
            text,
            flags=re.DOTALL,
        )
        assert match is not None
        block = match.group(1)
        for path in expected:
            assert path in block
        assert ".StartsWith(" not in block
