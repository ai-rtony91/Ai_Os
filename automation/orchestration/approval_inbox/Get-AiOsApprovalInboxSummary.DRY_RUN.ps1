[CmdletBinding()]
param(
    [string]$InboxPath = "automation/orchestration/approval_inbox",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Read-AiOsJsonFile {
    param([string]$Path)

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            file = $Path
            approval_status = "blocked"
            requested_action = "JSON_PARSE_FAILED"
            packet_id = "UNKNOWN"
            error = $_.Exception.Message
        }
    }
}

function Test-AiOsJsonProperty {
    param(
        [object]$Item,
        [string]$Name
    )

    return ($null -ne $Item -and $null -ne $Item.PSObject.Properties[$Name])
}

function Test-AiOsFieldHasValue {
    param(
        [object]$Item,
        [string]$Name
    )

    if (-not (Test-AiOsJsonProperty -Item $Item -Name $Name)) {
        return $false
    }

    $value = $Item.PSObject.Properties[$Name].Value
    if ($null -eq $value) {
        return $false
    }

    if ($value -is [string]) {
        return -not [string]::IsNullOrWhiteSpace($value)
    }

    if ($value -is [array]) {
        return ($value.Count -gt 0)
    }

    return $true
}

function Test-AiOsTruthy {
    param([object]$Value)

    if ($Value -is [bool]) {
        return $Value
    }

    if ($null -eq $Value) {
        return $false
    }

    return ([string]$Value).Trim().ToLowerInvariant() -eq "true"
}

function Get-AiOsMissingRequiredApprovalFields {
    param([object]$Item)

    $requiredFields = @(
        "requested_mode",
        "approved_mode",
        "approval_timestamp_placeholder",
        "risk_level",
        "allowed_paths",
        "blocked_paths",
        "validator_chain_required",
        "commit_package_required",
        "push_blocked_until_final_review",
        "notes"
    )

    $missing = @()
    foreach ($field in $requiredFields) {
        if (-not (Test-AiOsFieldHasValue -Item $Item -Name $field)) {
            $missing += $field
        }
    }

    return $missing
}

if (-not (Test-Path -LiteralPath $InboxPath -PathType Container)) {
    throw "Approval inbox path not found: $InboxPath"
}

$approvalFiles = @(Get-ChildItem -LiteralPath $InboxPath -File -Filter "*.json" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notlike "*.example.json" } | Sort-Object Name)
$pendingApprovals = @()
$approvedActions = @()
$blockedActions = @()
$completedRecords = @()

foreach ($file in $approvalFiles) {
    $item = Read-AiOsJsonFile -Path $file.FullName
    $status = if ($item.approval_status) { [string]$item.approval_status } else { "UNKNOWN" }
    $packetId = if ($item.packet_id) { [string]$item.packet_id } else { "UNKNOWN" }
    $requestedAction = if ($item.requested_action) { [string]$item.requested_action } elseif ($item.requested_mode) { [string]$item.requested_mode } else { "UNKNOWN" }

    $summary = [ordered]@{
        file = $file.Name
        packet_id = $packetId
        requested_action = $requestedAction
        approval_status = $status
        risk_level = if ($item.risk_level) { [string]$item.risk_level } else { "UNKNOWN" }
    }

    if ($item.error) {
        $summary["classification_reason"] = "JSON_PARSE_FAILED"
        $blockedActions += [pscustomobject]$summary
    }
    elseif ($status -eq "pending_review") {
        $summary["classification_reason"] = "PENDING_HUMAN_REVIEW"
        $pendingApprovals += [pscustomobject]$summary
    }
    elseif ($status -in @("approved_for_apply", "approved")) {
        $missingFields = @(Get-AiOsMissingRequiredApprovalFields -Item $item)
        $approvedByHuman = if (Test-AiOsJsonProperty -Item $item -Name "approved_by_human") { Test-AiOsTruthy -Value $item.approved_by_human } else { $false }

        if ($approvedByHuman -and $missingFields.Count -eq 0) {
            $summary["classification_reason"] = "SCHEMA_VALID_APPROVED_BY_HUMAN"
            $approvedActions += [pscustomobject]$summary
        }
        else {
            $summary["classification_reason"] = "SCHEMA_BLOCKED_APPROVED_STATUS"
            $summary["approved_by_human"] = $approvedByHuman
            $summary["missing_required_fields"] = $missingFields
            $blockedActions += [pscustomobject]$summary
        }
    }
    elseif ($status -eq "completed") {
        $summary["classification_reason"] = "COMPLETED_HISTORICAL_NON_ACTIONABLE"
        $completedRecords += [pscustomobject]$summary
    }
    elseif ($status -in @("blocked", "rejected", "expired")) {
        $summary["classification_reason"] = "NON_ACTIONABLE_STOP_STATUS"
        $blockedActions += [pscustomobject]$summary
    }
    else {
        $summary["classification_reason"] = "UNKNOWN_STATUS_FAIL_CLOSED"
        $blockedActions += [pscustomobject]$summary
    }
}

$nextSafeCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
if ($blockedActions.Count -gt 0) {
    $nextSafeCommand = "Review blocked approval items before APPLY."
}
elseif ($approvedActions.Count -gt 0) {
    $nextSafeCommand = "Review approved actions, validators, and commit package before APPLY."
}
elseif ($pendingApprovals.Count -gt 0) {
    $nextSafeCommand = "Operator reviews pending approvals; no APPLY is authorized by this summary."
}

$result = [ordered]@{
    schema = "aios_approval_inbox_summary.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    pending_approvals = $pendingApprovals
    approved_actions = $approvedActions
    blocked_actions = $blockedActions
    completed_records = $completedRecords
    next_safe_command = $nextSafeCommand
    commit_performed = "NO"
    push_performed = "NO"
}

$approvalRequired = ($pendingApprovals.Count -gt 0 -or $approvedActions.Count -gt 0 -or $blockedActions.Count -gt 0)
$blockedReason = if ($blockedActions.Count -gt 0) { "Blocked approval items are present." } else { "none" }
$severity = if ($blockedActions.Count -gt 0) { "BLOCKED" } elseif ($approvalRequired) { "REVIEW" } else { "INFO" }
$status = if ($blockedActions.Count -gt 0) { "BLOCKED" } elseif ($approvalRequired) { "REVIEW" } else { "PASS" }
$result["orchestration_result_contract"] = [ordered]@{
    status = $status
    severity = $severity
    packet_id = "APPROVAL_INBOX_SUMMARY"
    worker_identity = "UNKNOWN"
    validator_results = @()
    approval_required = $approvalRequired
    blocked_reason = $blockedReason
    escalation_reason = if ($approvalRequired) { "Approval inbox contains items requiring Human Owner review." } else { "none" }
    commit_candidate = $false
    next_safe_action = $nextSafeCommand
    stop_condition = "REPORT_ONLY_NO_APPROVAL_MUTATION"
    runtime_notes = @(
        "DRY_RUN_READ_ONLY",
        "No approval state was created, updated, cleared, or approved.",
        "No commit or push was performed."
    )
    evidence = [ordered]@{
        pending_approval_count = $pendingApprovals.Count
        approved_action_count = $approvedActions.Count
        blocked_action_count = $blockedActions.Count
        completed_record_count = $completedRecords.Count
    }
    generated_at = $result.generated_utc
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AIOS Approval Inbox Summary"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "pending_approvals:"
if ($pendingApprovals.Count -eq 0) { Write-Host "- none" } else { $pendingApprovals | ForEach-Object { Write-Host "- $($_.file): $($_.packet_id) [$($_.approval_status)] $($_.requested_action)" } }
Write-Host ""
Write-Host "approved_actions:"
if ($approvedActions.Count -eq 0) { Write-Host "- none" } else { $approvedActions | ForEach-Object { Write-Host "- $($_.file): $($_.packet_id) [$($_.approval_status)] $($_.requested_action)" } }
Write-Host ""
Write-Host "blocked_actions:"
if ($blockedActions.Count -eq 0) { Write-Host "- none" } else { $blockedActions | ForEach-Object { Write-Host "- $($_.file): $($_.packet_id) [$($_.approval_status)] $($_.requested_action)" } }
Write-Host ""
Write-Host "completed_records:"
if ($completedRecords.Count -eq 0) { Write-Host "- none" } else { $completedRecords | ForEach-Object { Write-Host "- $($_.file): $($_.packet_id) [$($_.approval_status)] $($_.requested_action)" } }
Write-Host ""
Write-Host "next_safe_command:"
Write-Host $nextSafeCommand
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
