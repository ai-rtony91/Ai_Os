[CmdletBinding()]
param(
    [string]$InboxPath = "automation/orchestration/approval_inbox"
)

$ErrorActionPreference = "Stop"

$requiredFields = @(
    "approval_gate_id",
    "packet_id",
    "requested_mode",
    "approved_mode",
    "approval_status",
    "approved_by_human",
    "approval_timestamp_placeholder",
    "risk_level",
    "allowed_paths",
    "blocked_paths",
    "validator_chain_required",
    "commit_package_required",
    "push_blocked_until_final_review",
    "notes"
)

$validJsonCount = 0
$invalidJsonCount = 0
$missingRequiredFields = [System.Collections.Generic.List[object]]::new()
$approvalItemsBlocked = [System.Collections.Generic.List[string]]::new()
$approvalItemsReady = [System.Collections.Generic.List[string]]::new()
$approvalItemsReviewRequired = [System.Collections.Generic.List[string]]::new()

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

if (-not (Test-Path -LiteralPath $InboxPath)) {
    throw "Approval inbox path not found: $InboxPath"
}

$jsonFiles = @(Get-ChildItem -LiteralPath $InboxPath -Filter "*.json" -File)

foreach ($file in $jsonFiles) {
    $item = $null
    try {
        $item = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
        $validJsonCount++
    }
    catch {
        $invalidJsonCount++
        $approvalItemsBlocked.Add($file.Name) | Out-Null
        continue
    }

    $missing = @(
        foreach ($field in $requiredFields) {
            if (-not ($item.PSObject.Properties.Name -contains $field)) {
                $field
            }
        }
    )

    if ($missing.Count -gt 0) {
        $missingRequiredFields.Add([pscustomobject]@{
            file = $file.Name
            fields = $missing
        }) | Out-Null
        $approvalItemsBlocked.Add($file.Name) | Out-Null
        continue
    }

    $isReady = (
        [string]$item.approval_status -eq "approved_for_apply" -and
        [bool]$item.approved_by_human -and
        [bool]$item.validator_chain_required -and
        [bool]$item.commit_package_required -and
        @($item.allowed_paths).Count -gt 0 -and
        @($item.blocked_paths).Count -gt 0
    )

    if ($isReady) {
        $evidence = $null
        if ($item.PSObject.Properties.Name -contains "approval_evidence") {
            $evidence = $item.approval_evidence
        }
        $approvalTimestamp = ""
        if ($item.PSObject.Properties.Name -contains "approval_timestamp_utc") {
            $approvalTimestamp = [string]$item.approval_timestamp_utc
        }
        elseif ($item.PSObject.Properties.Name -contains "bound_at") {
            $approvalTimestamp = [string]$item.bound_at
        }
        elseif ($item.PSObject.Properties.Name -contains "approval_timestamp_placeholder") {
            $approvalTimestamp = [string]$item.approval_timestamp_placeholder
        }
        $hasHardenedEvidence = (
            $null -ne $evidence -and
            [string]$evidence.type -eq "HMAC_SHA256" -and
            -not [string]::IsNullOrWhiteSpace([string]$evidence.approval_hmac_sha256) -and
            -not [string]::IsNullOrWhiteSpace([string]$evidence.approval_nonce) -and
            -not (Test-AiOsMidnightPlaceholder -Value $approvalTimestamp)
        )
        if ($hasHardenedEvidence) {
            $approvalItemsReady.Add($file.Name) | Out-Null
        }
        else {
            $approvalItemsReviewRequired.Add($file.Name) | Out-Null
            $approvalItemsBlocked.Add($file.Name) | Out-Null
        }
    }
    else {
        $approvalItemsBlocked.Add($file.Name) | Out-Null
    }
}

$status = if ($invalidJsonCount -eq 0 -and $missingRequiredFields.Count -eq 0) { "PASS" } else { "BLOCKED" }

[pscustomobject]@{
    validator = "Test-ApprovalInboxIntegrity.DRY_RUN"
    mode = "DRY_RUN_READ_ONLY"
    status = $status
    inbox_path = $InboxPath
    valid_json_count = $validJsonCount
    invalid_json_count = $invalidJsonCount
    missing_required_fields = $missingRequiredFields
    approval_items_blocked = $approvalItemsBlocked
    approval_items_ready = $approvalItemsReady
    approval_items_review_required = $approvalItemsReviewRequired
    next_safe_action = if ($approvalItemsReady.Count -gt 0) { "Review ready approval items before APPLY." } else { "No approval item is ready for APPLY until human approval is recorded." }
} | ConvertTo-Json -Depth 10
