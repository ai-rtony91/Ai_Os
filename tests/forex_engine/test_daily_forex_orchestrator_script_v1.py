from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts/forex_delivery/Invoke-AiOsDailyForexOrchestrator.ps1"


def _script_text() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def _evidence_day_function() -> str:
    script = _script_text()
    start = script.index("function Test-EvidenceDay")
    end = script.index("function Write-OrchestratorReports", start)
    return script[start:end]


def test_current_day_detector_recognizes_only_supported_evidence_record_types() -> None:
    function = _evidence_day_function()

    assert '$supportedRecordTypes = @("REAL_DEMO_DAY", "PAPER_SIMULATION_DAY")' in function
    assert "$supportedRecordTypes -contains [string]$obj.record_type" in function
    assert "$recordTypeMatches[[string]$obj.record_type]++" in function


def test_current_day_detector_keeps_paper_and_real_statuses_distinct() -> None:
    function = _evidence_day_function()

    assert '"TODAY_REAL_DEMO_EVIDENCE_PRESENT"' in function
    assert '"TODAY_PAPER_SIMULATION_PRESENT"' in function
    assert '"TODAY_EVIDENCE_PRESENT"' not in function


def test_current_day_detector_remains_date_bound_and_read_only() -> None:
    function = _evidence_day_function()

    assert '[string]$obj.date -eq $today' in function
    assert "Get-Content -LiteralPath $ledger" in function
    for mutation_command in ("Set-Content", "Add-Content", "Out-File", "Invoke-RestMethod"):
        assert mutation_command not in function


def test_invalid_json_remains_fail_closed_after_the_complete_ledger_scan() -> None:
    function = _evidence_day_function()

    parse_warning = function.index(
        'if ($parseWarnings -gt 0) { $script:EvidenceStatus = "LEDGER_PARSE_WARNING" }'
    )
    missing_evidence = function.index(
        'elseif ($matches -eq 0) { $script:EvidenceStatus = "MISSING_TODAY_EVIDENCE" }'
    )
    assert "$parseWarnings++" in function
    assert parse_warning < missing_evidence


def test_orchestrator_preserves_both_read_only_verdict_stages() -> None:
    script = _script_text()

    assert 'Invoke-Checked -Stage "DEMO_VERDICT"' in script
    assert 'Invoke-Checked -Stage "EXTENDED_EVIDENCE_VERDICT"' in script
    assert "Get-AiOsDemoVerdict.ps1" in script
    assert "Get-AiOsExtendedEvidenceVerdict.ps1" in script


def test_orchestrator_safety_contract_remains_fail_closed() -> None:
    script = _script_text()

    for safety_flag in (
        "broker_calls_allowed = $false",
        "live_orders_allowed = $false",
        "credential_access_allowed = $false",
        "money_movement_allowed = $false",
        "automatic_evidence_append_allowed = $false",
    ):
        assert safety_flag in script
