[CmdletBinding()]
param(
    [string]$GatePath = "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"
)

$ErrorActionPreference = "Stop"

function Add-Result {
    param(
        [System.Collections.Generic.List[object]]$Results,
        [string]$Check,
        [bool]$Passed,
        [string]$Message
    )

    $Results.Add([pscustomobject]@{
        check = $Check
        passed = $Passed
        message = $Message
    }) | Out-Null
}

$results = [System.Collections.Generic.List[object]]::new()
$gate = $null

if (Test-Path -LiteralPath $GatePath) {
    Add-Result -Results $results -Check "approval_gate_file_exists" -Passed $true -Message "Approval gate file exists."
    try {
        $gate = Get-Content -LiteralPath $GatePath -Raw | ConvertFrom-Json
        Add-Result -Results $results -Check "approval_gate_json_parse" -Passed $true -Message "Approval gate JSON parsed."
    }
    catch {
        Add-Result -Results $results -Check "approval_gate_json_parse" -Passed $false -Message "Approval gate JSON is invalid."
    }
}
else {
    Add-Result -Results $results -Check "approval_gate_file_exists" -Passed $false -Message "Approval gate file is missing."
}

if ($null -ne $gate) {
    $applyStatuses = @("approved_for_apply", "completed")
    $requestedApplyAllowed = ([string]$gate.requested_mode -ne "APPLY") -or ([string]$gate.approval_status -in $applyStatuses)
    Add-Result -Results $results -Check "requested_mode_apply_status_allowed" -Passed $requestedApplyAllowed -Message "requested_mode APPLY requires approved_for_apply or completed status."

    Add-Result -Results $results -Check "approved_by_human_before_apply" -Passed ([bool]$gate.approved_by_human) -Message "approved_by_human must be true before APPLY."
    Add-Result -Results $results -Check "allowed_paths_present" -Passed (@($gate.allowed_paths).Count -gt 0) -Message "allowed_paths must be present."
    Add-Result -Results $results -Check "blocked_paths_present" -Passed (@($gate.blocked_paths).Count -gt 0) -Message "blocked_paths must be present."
    Add-Result -Results $results -Check "validator_chain_required" -Passed ([bool]$gate.validator_chain_required) -Message "validator_chain_required must be true."
    Add-Result -Results $results -Check "commit_package_required" -Passed ([bool]$gate.commit_package_required) -Message "commit_package_required must be true."
}

$failed = @($results | Where-Object { -not $_.passed })
$status = if ($failed.Count -eq 0) { "PASS" } else { "BLOCKED" }

[pscustomobject]@{
    validator = "Test-ApplyApprovalGate.DRY_RUN"
    mode = "DRY_RUN_READ_ONLY"
    status = $status
    checks_run = $results.Count
    failed_count = $failed.Count
    results = $results
    next_safe_action = if ($status -eq "PASS") { "Approval gate structure is valid. Human approval is still required before APPLY." } else { "Review failed approval gate checks before APPLY." }
} | ConvertTo-Json -Depth 10
