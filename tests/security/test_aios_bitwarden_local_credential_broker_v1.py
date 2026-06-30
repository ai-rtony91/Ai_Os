from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = REPO_ROOT / "scripts" / "security"
DOC_DIR = REPO_ROOT / "docs" / "security"

START_HELPER = SCRIPT_DIR / "Start-AiosBitwardenSession.ps1"
CLEAR_HELPER = SCRIPT_DIR / "Clear-AiosBitwardenSession.ps1"
REGISTER_HELPER = SCRIPT_DIR / "Register-AiosBitwardenLocalCredential.ps1"
REMOVE_HELPER = SCRIPT_DIR / "Remove-AiosBitwardenLocalCredential.ps1"
TEST_HELPER = SCRIPT_DIR / "Test-AiosBitwardenLocalCredentialBroker.ps1"

RUNTIME_DOC = DOC_DIR / "AIOS_BITWARDEN_RUNTIME_SESSION_HARDENING_V1.md"
BROKER_DOC = DOC_DIR / "AIOS_BITWARDEN_LOCAL_CREDENTIAL_BROKER_V1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_register_script_stores_in_localappdata_dpapi_file() -> None:
    text = _read(REGISTER_HELPER)
    assert "$env:LOCALAPPDATA" in text
    assert "AIOS\\Security" in text
    assert "bitwarden-master-password.dpapi" in text
    assert "Set-Content" in text


def test_register_script_uses_secure_prompt_and_encrypt() -> None:
    text = _read(REGISTER_HELPER)
    assert "Read-Host" in text
    assert "-AsSecureString" in text
    assert "ConvertFrom-SecureString" in text


def test_register_script_does_not_print_secret_literals() -> None:
    text = _read(REGISTER_HELPER).lower()
    assert "convertfrom-securestring | set-content" in text
    assert "asplaintext" not in text
    assert "write-output" in text
    assert "aios_bitwarden_local_credential_registered" in text
    assert not re.search(r'Write-Output\s+.*\$\w+_password', text)


def test_start_helper_uses_passwordenv_and_never_plain_unlock() -> None:
    text = _read(START_HELPER).lower()
    assert "bw unlock --raw" not in text
    assert "bw unlock --passwordenv bw_password --raw" in text
    assert "remove-item env:bw_password" in text
    assert "--passwordfile" not in text
    assert "read-host" not in text


def test_start_helper_clears_bw_password_after_attempt() -> None:
    text = _read(START_HELPER).lower()
    assert "finally {" in text
    assert "remove-item env:bw_password" in text


def test_start_helper_does_not_decrypt_or_write_repo_file() -> None:
    text = _read(START_HELPER)
    assert "$env:LOCALAPPDATA" in text
    assert "bitwarden-master-password.dpapi" in text
    assert "C:\\Dev\\Ai.Os" not in text
    assert "bw_session" in text.lower()


def test_clear_helper_removes_credentials_in_process() -> None:
    text = _read(CLEAR_HELPER).lower()
    assert "remove-item env:bw_password" in text
    assert "remove-item env:bw_session" in text
    assert "& bw lock" in text


def test_remove_helper_deletes_local_credential_only() -> None:
    text = _read(REMOVE_HELPER)
    assert "$credentialPath" in text
    assert "AIOS\\Security" in text
    assert "bitwarden-master-password.dpapi" in text
    assert "remove-item -literalpath $credentialpath" in text.lower()
    assert "clearSession" in text or "env:bw_session" in text.lower()


def test_broker_docs_risk_and_instructions_present() -> None:
    text = _read(BROKER_DOC)
    assert "AIOS does not" in text.lower() or "Purpose" in text
    assert "Risk" in text
    assert "Register once" in text
    assert "Start runtime" in text
    assert "Do not use `--passwordfile`" in text


def test_runtime_hardening_refers_to_local_broker_and_no_prompt_requirement() -> None:
    text = _read(RUNTIME_DOC)
    assert "AIOS_BITWARDEN_LOCAL_CREDENTIAL_BROKER_V1.md" in text
    assert "never prompt for a master password" in text.lower()
    assert "bw unlock --passwordenv bw_password --raw" in text.lower()


def test_scripts_do_not_print_secret_env_values() -> None:
    scripts = [
        START_HELPER,
        CLEAR_HELPER,
        REGISTER_HELPER,
        REMOVE_HELPER,
        TEST_HELPER,
    ]
    for path in scripts:
        for line in _read(path).splitlines():
            if "Write-Output" in line or "Write-Output" in line.lower():
                assert not re.search(r'\$env:BW_(PASSWORD|SESSION)', line, flags=re.IGNORECASE)
                assert "vault" not in line.lower()


def test_documents_and_scripts_no_plain_token_values() -> None:
    paths = [
        START_HELPER,
        CLEAR_HELPER,
        REGISTER_HELPER,
        REMOVE_HELPER,
        TEST_HELPER,
        BROKER_DOC,
        RUNTIME_DOC,
    ]

    for path in paths:
        text = _read(path)
        assert re.search(r'BW_PASSWORD\s*=\s*["\'][A-Za-z0-9+/=]{20,}["\']', text) is None
        assert re.search(r'BW_SESSION\s*=\s*["\'][A-Za-z0-9+/=]{20,}["\']', text) is None
        assert re.search(r'account[_-]?id\s*=\s*["\'][A-Za-z0-9]+["\']', text.lower(), re.IGNORECASE) is None


def test_test_helper_only_validates_when_explicit_switch_set() -> None:
    text = _read(TEST_HELPER).lower()
    assert "param(" in text
    assert "param(" in text and "validateunlock" in text
    assert "if ($validateunlock -and $credentialpresent)" in text
    assert "bw unlock --passwordenv bw_password --raw" in text
    assert "aios_bitwarden_local_credential_present" in text.lower()
