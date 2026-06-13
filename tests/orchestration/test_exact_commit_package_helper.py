import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / "automation/orchestration/commit_packages/Invoke-AiOsExactCommitPackage.ps1"


def test_exact_commit_helper_collects_multifile_tokens_without_positional_binding():
    text = HELPER.read_text(encoding="utf-8")

    assert "[CmdletBinding(PositionalBinding = $false)]" in text
    assert "ValueFromRemainingArguments = $true" in text
    assert "[string[]]$AdditionalFiles" in text
    assert "$effectiveFiles = @($Files) + @($AdditionalFiles)" in text
    assert 'return "unexpected parameter-like token"' in text


def test_exact_commit_helper_help_documents_normal_powershell_array_usage():
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(HELPER),
            "-Help",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "$files = @(" in completed.stdout
    assert "-Files $files -Message" in completed.stdout
    assert 'Direct multi-file form:' in completed.stdout
