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

function Test-AiOsMidnightPlaceholder {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }
    if ($Value -eq "2026-06-08T00:00:00Z" -or $Value -eq "2026-06-02T00:00:00Z") {
        return $true
    }
    return ($Value -match "T00:00:00Z$")
}

function Get-AiOsApprovalEvidence {
    param([object]$Gate)
    if ($Gate.PSObject.Properties.Name -contains "approval_evidence") {
        return $Gate.approval_evidence
    }
    return $null
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
    $applyStatuses = @("approved_for_apply", "completed", "pending_review")
    $requestedApplyAllowed = ([string]$gate.requested_mode -ne "APPLY") -or ([string]$gate.approval_status -in $applyStatuses)
    Add-Result -Results $results -Check "requested_mode_apply_status_allowed" -Passed $requestedApplyAllowed -Message "requested_mode APPLY must be approved_for_apply, completed evidence, or pending_review safe state."

    $isApplyApproved = ([string]$gate.approval_status -eq "approved_for_apply")
    $evidence = Get-AiOsApprovalEvidence -Gate $gate
    $hasHardenedEvidence = (
        $null -ne $evidence -and
        [string]$evidence.type -eq "HMAC_SHA256" -and
        -not [string]::IsNullOrWhiteSpace([string]$evidence.approval_hmac_sha256) -and
        -not [string]::IsNullOrWhiteSpace([string]$evidence.approval_nonce)
    )
    $approvalTimestamp = ""
    if ($gate.PSObject.Properties.Name -contains "approval_timestamp_utc") {
        $approvalTimestamp = [string]$gate.approval_timestamp_utc
    }
    elseif ($gate.PSObject.Properties.Name -contains "bound_at") {
        $approvalTimestamp = [string]$gate.bound_at
    }
    elseif ($gate.PSObject.Properties.Name -contains "approval_timestamp_placeholder") {
        $approvalTimestamp = [string]$gate.approval_timestamp_placeholder
    }

    Add-Result -Results $results -Check "approved_by_human_before_apply" -Passed ((-not $isApplyApproved) -or [bool]$gate.approved_by_human) -Message "approved_for_apply requires approved_by_human=true."
    Add-Result -Results $results -Check "hardened_approval_evidence_required" -Passed ((-not $isApplyApproved) -or $hasHardenedEvidence) -Message "approved_for_apply requires out-of-band hardened approval evidence."
    Add-Result -Results $results -Check "approval_timestamp_not_placeholder" -Passed ((-not $isApplyApproved) -or (-not (Test-AiOsMidnightPlaceholder -Value $approvalTimestamp))) -Message "approved_for_apply must not use placeholder or midnight approval timestamps."
    Add-Result -Results $results -Check "bound_by_not_standalone_authority" -Passed ((-not $isApplyApproved) -or $hasHardenedEvidence) -Message "free-text bound_by is evidence only and cannot approve APPLY by itself."
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
