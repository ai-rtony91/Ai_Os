from __future__ import annotations

import json
from pathlib import Path

from automation.governance.aios_aee_governance_validator_v1 import (
    REQUIRED_DAOCTRINE_ARTIFACTS,
    AEEGovernanceValidationResult,
    build_aee_governance_validation,
    result_to_jsonable_dict,
    result_to_markdown,
    result_to_operator_text,
)
from scripts.governance.run_aios_aee_governance_validator_v1 import run_validation


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "fixtures" / "governance" / "aee_validator"
VALIDATOR_DOC = "docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md"
REPORT_PATH = "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md"
CHECKPOINT_PATH = "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md"
PROTECTED_PATH = "docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md"
AUTONOMOUS_DOCTRINE_PATH = "docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md"
AGENTS_PATH = "AGENTS.md"


def _base_artifact_set() -> dict[str, str]:
    common_safe = (
        "This artifact does not authorize broker/API access. "
        "This artifact does not authorize credential access. "
        "This artifact does not authorize trading execution. "
        "This artifact does not authorize money movement. "
        "This artifact does not authorize commit/push/merge without explicit Human Owner approval."
    )

    docs: dict[str, str] = {}

    def add(path: str, title: str, links: str = "") -> None:
        docs[path] = "\n".join(
            [
                f"# {title}",
                "",
                "## Purpose",
                "Validate campaign law and checkpoint behavior.",
                "",
                "## Scope",
                "Validation of AEE artifacts within this campaign.",
                "",
                links,
                "",
                common_safe,
                "",
            ]
        ).strip()

    add(
        "docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md",
        "AIOS Autonomous Execution And Failure Recovery Doctrine V1",
        "Related: AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md AIOS_FAILURE_MEMORY_V1.md",
    )
    add(
        "docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md",
        "AIOS Autonomous Execution Engine V1",
        "Related: AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md",
    )
    add(
        "docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md",
        "AIOS Failure Recovery Playbooks V1",
        "Related: AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md AIOS_FAILURE_MEMORY_V1.md",
    )
    add(
        "docs/governance/AIOS_FAILURE_MEMORY_V1.md",
        "AIOS Failure Memory V1",
        "Related: AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md",
    )
    add(
        "docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md",
        "AIOS Campaign Checkpoint and Resume V1",
        "Related: AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    )
    add(
        "docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md",
        "AIOS Campaign Arbitration Doctrine V1",
        "Related: AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md",
    )
    add(
        "docs/workflows/AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md",
        "AIOS Isolated Worktree Campaign Execution V1",
        "Related: AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    )
    add(
        "docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md",
        "AIOS Long Campaign Codex Operating Mode V1",
        "Related: AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md",
    )
    add(
        "docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md",
        "AIOS Protected Publishing Handoff V1",
        "Related: AI_OS_COMMIT_PUSH_GATE.md AI_OS_PR_LANE_RUNNER.md\n"
        "gh pr checks --watch",
    )
    add(
        "docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md",
        "AIOS GitHub CI Failure Recovery V1",
        "Related: AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md",
    )
    add(
        VALIDATOR_DOC,
        "AIOS AEE Governance Validator V1",
        "Related: AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md",
    )

    docs[PROTECTED_PATH] = "\n".join(
        [
            "# AIOS Protected Publishing Handoff V1",
            "",
            "## Purpose",
            "Protected handoff checks for Codex to owner.",
            "## Scope",
            "Publishing and merge workflow boundaries.",
            "Related: AI_OS_COMMIT_PUSH_GATE.md AI_OS_PR_LANE_RUNNER.md",
            "",
            common_safe,
            "",
            "## Example safe publish block",
            "Block 1: publish/check only",
            "git status --short --branch",
            "git add -- \"docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md\"",
            "git diff --cached --check",
            "git commit -m \"docs: test\"",
            "git push -u origin",
            "gh pr create --base main --head test --title test --body-file test.md",
            "gh pr checks --watch",
            "",
            "Block 2: merge/sync only",
            "gh pr merge --squash test",
            "git switch main",
            "git pull --ff-only origin main",
        ]
    )

    docs[REPORT_PATH] = "\n".join(
        [
            "# AEE Validator Report",
            "",
            "## Scope",
            "Execution of deterministic validator evidence.",
            "",
            "## Purpose",
            "Capture validator results.",
            "",
            "Block 1: publish/check only",
            "git status --short --branch",
            "git add -- \"docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md\"",
            "git diff --cached --check",
            "git commit -m \"docs: test\"",
            "git push -u origin",
            "gh pr create --base main --head test --title test --body-file test.md",
            "",
            "Block 2: merge/sync only",
            "git status --short --branch",
            "gh pr merge 1 --squash",
            "git switch main",
            "git pull --ff-only origin main",
        ]
    )
    docs[CHECKPOINT_PATH] = "\n".join(
        [
            "# Campaign Checkpoint",
            "",
            "## Scope",
            "Execution checkpoint.",
            "## Purpose",
            "Track completion.",
            "",
            "current_phase: phase 0",
        ]
    )
    docs[AGENTS_PATH] = "\n".join(
        [
            "# AGENTS.md",
            "",
            "AIOS AEE Governance Validator V1 pointer",
            "AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
            "AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md",
        ]
    )

    for law in [
        "The lane is the execution target.",
        "The packet is the authorization boundary.",
        "The worktree is the isolation boundary.",
        "Recoverable failures become work items.",
        "Reports are evidence, not endpoints.",
        "Codex continues inside approved scope.",
        "Codex stops at true governance gates.",
    ]:
        docs[AUTONOMOUS_DOCTRINE_PATH] += f"\n{law}"
    return docs


def _write_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp_path


def _run_with_docs(
    tmp_path: Path,
    extra: dict[str, str | None] | None = None,
) -> AEEGovernanceValidationResult:
    payload = _base_artifact_set()
    if extra:
        for key, value in extra.items():
            if value is None:
                payload.pop(key, None)
            else:
                payload[key] = value
    repo = _write_repo(tmp_path, payload)
    return build_aee_governance_validation(
        repo,
        artifact_paths=REQUIRED_DAOCTRINE_ARTIFACTS + [VALIDATOR_DOC, CHECKPOINT_PATH, REPORT_PATH],
    )


def _fixture_scenario_names() -> list[str]:
    return [
        "complete_valid_aee_docs.md",
        "missing_h1.md",
        "missing_purpose.md",
        "missing_scope.md",
        "missing_safety_boundary.md",
        "missing_cross_link.md",
        "unsafe_publish_handoff_combined_merge.md",
        "broad_git_add_detected.md",
        "placeholder_pattern_detected.md",
        "ci_sensitive_assignment_detected.md",
        "report_without_checkpoint.md",
        "checkpoint_without_report.md",
        "1312_rule_missing.md",
        "lane_packet_worktree_law_missing.md",
    ]


def test_fixture_library_exists() -> None:
    assert FIXTURE_ROOT.exists()
    for name in _fixture_scenario_names():
        assert (FIXTURE_ROOT / name).exists()


def test_valid_artifact_set_passes(tmp_path: Path) -> None:
    result = _run_with_docs(tmp_path)
    assert result.status == "PASS", result.findings


def test_missing_h1_fails(tmp_path: Path) -> None:
    result = _run_with_docs(tmp_path, extra={AUTONOMOUS_DOCTRINE_PATH: "#"})
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1101" for item in result.findings)


def test_missing_purpose_fails(tmp_path: Path) -> None:
    broken = _base_artifact_set()
    broken["docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md"] = (
        broken["docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md"].replace(
            "## Purpose\nValidate campaign law and checkpoint behavior.\n", ""
        )
    )
    result = _run_with_docs(tmp_path, extra=broken)
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1102" for item in result.findings)


def test_missing_scope_fails(tmp_path: Path) -> None:
    broken = _base_artifact_set()
    broken["docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md"] = (
        broken["docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md"].replace(
            "## Scope\nValidation of AEE artifacts within this campaign.\n", ""
        )
    )
    result = _run_with_docs(tmp_path, extra=broken)
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1103" for item in result.findings)


def test_missing_safety_phrase_fails(tmp_path: Path) -> None:
    broken = _base_artifact_set()
    broken[VALIDATOR_DOC] = broken[VALIDATOR_DOC].replace(
        "This artifact does not authorize credential access. ", ""
    )
    result = _run_with_docs(tmp_path, extra=broken)
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1201" for item in result.findings)


def test_missing_cross_link_fails(tmp_path: Path) -> None:
    broken = _base_artifact_set()
    broken["docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md"] = (
        broken["docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md"].replace(
            "AIOS_FAILURE_MEMORY_V1.md", ""
        )
    )
    result = _run_with_docs(tmp_path, extra=broken)
    assert result.status in {"PARTIAL", "FAIL"}
    assert any(item["code"] == "AIOS-AEE-V1-1301" for item in result.findings)


def test_combined_handoff_publish_merge_block_fails(tmp_path: Path) -> None:
    broken = {
        PROTECTED_PATH: "\n".join(
            [
                "# Protected",
                "## Purpose",
                "purpose",
                "## Scope",
                "scope",
                "git status --short --branch",
                "Block 1: publish/check",
                "git add -- \"docs/a.md\"",
                "git diff --cached --check",
                "git commit -m \"docs: test\"",
                "git push -u origin",
                "gh pr create --base main --head test --title test --body-file test.md",
                "gh pr checks --watch",
                "git merge --squash main",
                "Block 2: merge/sync only",
                "git merge --ff-only",
            ]
        )
    }
    result = _run_with_docs(tmp_path, extra=broken)
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1503" for item in result.findings)


def test_broad_git_add_detected(tmp_path: Path) -> None:
    broken = {
        CHECKPOINT_PATH: "\n".join(
            [
                "# checkpoint",
                "## Purpose",
                "scope",
                "## Scope",
                "scope",
                "git add .",
            ]
        ),
        REPORT_PATH: "\n".join(
            [
                "# report",
                "## Purpose",
                "scope",
                "## Scope",
                "scope",
            ]
        ),
    }
    result = _run_with_docs(tmp_path, extra=broken)
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1702" for item in result.findings)


def test_placeholder_pattern_detected(tmp_path: Path) -> None:
    broken = {
        CHECKPOINT_PATH: (
            _base_artifact_set()[CHECKPOINT_PATH]
            + "\nUse placeholder path {path} in report"
        )
    }
    result = _run_with_docs(tmp_path, extra=broken)
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1601" for item in result.findings)


def test_ci_sensitive_assignment_detected(tmp_path: Path) -> None:
    broken = {
        "docs/governance/AIOS_FAILURE_MEMORY_V1.md": (
            _base_artifact_set()["docs/governance/AIOS_FAILURE_MEMORY_V1.md"]
            + '\nsecret = "demo"'
        )
    }
    result = _run_with_docs(tmp_path, extra=broken)
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1701" for item in result.findings)


def test_report_without_checkpoint(tmp_path: Path) -> None:
    result = _run_with_docs(tmp_path, extra={CHECKPOINT_PATH: None})
    assert any(item["code"] == "AIOS-AEE-V1-1401" for item in result.findings)


def test_checkpoint_without_report(tmp_path: Path) -> None:
    result = _run_with_docs(tmp_path, extra={REPORT_PATH: None})
    assert any(item["code"] == "AIOS-AEE-V1-1401" for item in result.findings)


def test_1312_rule_missing(tmp_path: Path) -> None:
    bad = {
        CHECKPOINT_PATH: "CreateProcessAsUserW failed: 1312\ncurrent_phase: waiting\n",
    }
    result = _run_with_docs(tmp_path, extra=bad)
    assert any(item["code"] == "AIOS-AEE-V1-1801" for item in result.findings)


def test_law_missing_fails(tmp_path: Path) -> None:
    broken = _base_artifact_set()
    content = broken[AUTONOMOUS_DOCTRINE_PATH]
    for law in [
        "The lane is the execution target.",
        "The packet is the authorization boundary.",
        "The worktree is the isolation boundary.",
        "Recoverable failures become work items.",
        "Reports are evidence, not endpoints.",
        "Codex continues inside approved scope.",
        "Codex stops at true governance gates.",
    ]:
        content = content.replace(f"\n{law}", "")
    result = _run_with_docs(tmp_path, extra={AUTONOMOUS_DOCTRINE_PATH: content})
    assert result.status == "FAIL"
    assert any(item["code"] == "AIOS-AEE-V1-1901" for item in result.findings)


def test_result_jsonable() -> None:
    result = build_aee_governance_validation(
        REPO_ROOT,
        artifact_paths=REQUIRED_DAOCTRINE_ARTIFACTS + [VALIDATOR_DOC, CHECKPOINT_PATH, REPORT_PATH],
    )
    payload = result_to_jsonable_dict(result)
    json.dumps(payload)


def test_markdown_report_includes_findings() -> None:
    result = build_aee_governance_validation(
        REPO_ROOT,
        artifact_paths=REQUIRED_DAOCTRINE_ARTIFACTS + [VALIDATOR_DOC, CHECKPOINT_PATH, REPORT_PATH],
    )
    output = result_to_markdown(result)
    assert "# AIOS AEE Governance Validator V1 Report" in output
    assert "- `AIOS-AEE-V1-1101`" in output or "- `AIOS-AEE-V1-1301`" in output or "- no findings" in output


def test_strict_cli_returns_nonzero_on_fail(tmp_path: Path) -> None:
    broken = _run_with_docs(
        tmp_path,
        extra={CHECKPOINT_PATH: "CreateProcessAsUserW failed: 1312\ncurrent_phase: blocked"},
    )
    assert broken.status != "PASS"
    assert run_validation(tmp_path, strict=True, json_output=False, write_report=False, report_path="unused.md") == 1


def test_non_strict_cli_returns_zero(tmp_path: Path) -> None:
    result = _run_with_docs(tmp_path, extra={REPORT_PATH: "placeholder {path}"})
    assert any(item["code"] == "AIOS-AEE-V1-1601" for item in result.findings)
    assert run_validation(tmp_path, strict=False, json_output=False, write_report=False, report_path="unused.md") == 0


def test_operator_text_stable(tmp_path: Path) -> None:
    result = _run_with_docs(tmp_path)
    text = result_to_operator_text(result)
    assert "failures:" in text
    assert "warnings:" in text


def test_cli_report_generation_path(tmp_path: Path) -> None:
    result = _run_with_docs(tmp_path)
    out_path = tmp_path / "tmp_report.md"
    assert result is not None
    return_code = run_validation(
        tmp_path,
        strict=False,
        json_output=False,
        write_report=True,
        report_path=str(out_path),
    )
    assert return_code == 0
    assert out_path.exists()
