[CmdletBinding()]
param(
    [string]$ConfigPath = "automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json"
)

$ErrorActionPreference = "Stop"

function Add-CheckResult {
    param(
        [System.Collections.Generic.List[object]]$Results,
        [string]$Check,
        [string]$Result,
        [string]$Notes
    )

    $Results.Add([pscustomobject]@{
        check = $Check
        result = $Result
        notes = $Notes
    }) | Out-Null
}

$results = [System.Collections.Generic.List[object]]::new()
$config = $null

if (Test-Path -LiteralPath $ConfigPath) {
    Add-CheckResult -Results $results -Check "config_exists" -Result "PASS" -Notes "Config exists."
    try {
        $config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
        Add-CheckResult -Results $results -Check "config_parses_json" -Result "PASS" -Notes "Config parses as JSON."
    }
    catch {
        Add-CheckResult -Results $results -Check "config_parses_json" -Result "FAIL" -Notes "Config JSON parse failed."
    }
}
else {
    Add-CheckResult -Results $results -Check "config_exists" -Result "FAIL" -Notes "Config is missing."
}

if ($null -ne $config) {
    $requiredValidators = @(
        "git_clean_state",
        "allowed_paths",
        "blocked_paths",
        "json_integrity",
        "powershell_syntax",
        "markdown_exists",
        "no_secrets",
        "no_live_trading_enablement",
        "approval_gate",
        "commit_package_review",
        "final_git_status"
    )

    $validatorNames = @($config.validators | ForEach-Object { [string]$_.name })
    $missingValidators = @($requiredValidators | Where-Object { $_ -notin $validatorNames })

    if ($missingValidators.Count -eq 0) {
        Add-CheckResult -Results $results -Check "required_validator_list_exists" -Result "PASS" -Notes "All required validators are present."
    }
    else {
        Add-CheckResult -Results $results -Check "required_validator_list_exists" -Result "FAIL" -Notes ("Missing validators: {0}" -f ($missingValidators -join ", "))
    }

    foreach ($ruleName in @("required_before_apply", "required_before_commit", "required_before_push")) {
        $hasRule = $config.PSObject.Properties.Name -contains $ruleName
        $isTrue = $hasRule -and ([bool]$config.$ruleName)
        Add-CheckResult -Results $results -Check $ruleName -Result $(if ($isTrue) { "PASS" } else { "FAIL" }) -Notes "$ruleName must exist and be true."
    }

    $duplicates = @(
        $validatorNames |
            Group-Object |
            Where-Object { $_.Count -gt 1 } |
            ForEach-Object { $_.Name }
    )

    if ($duplicates.Count -eq 0) {
        Add-CheckResult -Results $results -Check "no_duplicate_validator_names" -Result "PASS" -Notes "No duplicate validator names found."
    }
    else {
        Add-CheckResult -Results $results -Check "no_duplicate_validator_names" -Result "FAIL" -Notes ("Duplicate validators: {0}" -f ($duplicates -join ", "))
    }
}

$failed = @($results | Where-Object { $_.result -eq "FAIL" })
$status = if ($failed.Count -eq 0) { "PASS" } else { "FAIL" }

[pscustomobject]@{
    script = "Test-ValidatorChainConfig.DRY_RUN.ps1"
    mode = "DRY_RUN_READ_ONLY"
    status = $status
    checks_run = $results.Count
    failed_count = $failed.Count
    results = $results
    next_safe_action = if ($status -eq "PASS") { "Run Invoke-OrchestrationValidatorChain.DRY_RUN.ps1 before APPLY, commit, or push." } else { "Fix validator chain config before using it." }
} | ConvertTo-Json -Depth 10

