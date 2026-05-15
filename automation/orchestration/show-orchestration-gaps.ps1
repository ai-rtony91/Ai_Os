Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$ledgerPath = Join-Path $orchestrationRoot "orchestration_gap_ledger.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-StringList {
    param(
        [object[]]$Items
    )

    $visibleItems = @($Items | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })

    if ($visibleItems.Count -eq 0) {
        Write-Host "    - None"
        return
    }

    foreach ($item in $visibleItems) {
        Write-Host "    - $item"
    }
}

function Get-OptionalPropertyValue {
    param(
        [Parameter(Mandatory = $true)]
        [object]$InputObject,

        [Parameter(Mandatory = $true)]
        [string]$PropertyName
    )

    $property = $InputObject.PSObject.Properties[$PropertyName]
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

function Write-GapCollection {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [object[]]$Gaps
    )

    Write-Host $Title

    if ($Gaps.Count -eq 0) {
        Write-Host "  None"
        Write-Host ""
        return
    }

    foreach ($gap in $Gaps) {
        $priority = Get-OptionalPropertyValue -InputObject $gap -PropertyName "priority"
        $riskLevel = Get-OptionalPropertyValue -InputObject $gap -PropertyName "risk_level"
        $blockReason = Get-OptionalPropertyValue -InputObject $gap -PropertyName "block_reason"
        $completedCheckpoint = Get-OptionalPropertyValue -InputObject $gap -PropertyName "completed_checkpoint"
        $completionNotes = Get-OptionalPropertyValue -InputObject $gap -PropertyName "completion_notes"
        $nextAction = Get-OptionalPropertyValue -InputObject $gap -PropertyName "next_action"
        $allowedPaths = Get-OptionalPropertyValue -InputObject $gap -PropertyName "allowed_paths"
        $blockedPaths = Get-OptionalPropertyValue -InputObject $gap -PropertyName "blocked_paths"
        $safetyNotes = Get-OptionalPropertyValue -InputObject $gap -PropertyName "safety_notes"

        Write-Host "  Gap: $($gap.gap_id)"
        Write-Host "    Name: $($gap.gap_name)"
        Write-Host "    Status: $($gap.status)"

        if ($null -ne $priority) {
            Write-Host "    Priority: $priority"
        }

        if (-not [string]::IsNullOrWhiteSpace([string]$riskLevel)) {
            Write-Host "    Risk level: $riskLevel"
        }

        if (-not [string]::IsNullOrWhiteSpace([string]$blockReason)) {
            Write-Host "    Block reason: $blockReason"
        }

        if (-not [string]::IsNullOrWhiteSpace([string]$completedCheckpoint)) {
            Write-Host "    Completed checkpoint: $completedCheckpoint"
        }

        if (-not [string]::IsNullOrWhiteSpace([string]$completionNotes)) {
            Write-Host "    Completion notes: $completionNotes"
        }

        if (-not [string]::IsNullOrWhiteSpace([string]$nextAction)) {
            Write-Host "    Next action: $nextAction"
        }

        Write-Host "    Allowed paths:"
        Write-StringList -Items @($allowedPaths)
        Write-Host "    Blocked paths:"
        Write-StringList -Items @($blockedPaths)
        Write-Host "    Safety notes:"
        Write-StringList -Items @($safetyNotes)
        Write-Host ""
    }
}

$ledger = Read-JsonFile -Path $ledgerPath
$openGaps = @($ledger.open_gaps)
$blockedGaps = @($ledger.blocked_gaps)
$completedGaps = @($ledger.completed_gaps)
$nextSafestGap = $ledger.next_safest_gap

Write-Host "AI_OS Orchestration Gap Ledger Display"
Write-Host "Mode: $($ledger.mode)"
Write-Host "Ledger: $($ledger.ledger_name)"
Write-Host "Purpose: $($ledger.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No gaps are changed. Nothing is launched."
Write-Host ""

Write-Host "Gap summary:"
Write-Host "  Open gaps: $($openGaps.Count)"
Write-Host "  Blocked gaps: $($blockedGaps.Count)"
Write-Host "  Completed gaps: $($completedGaps.Count)"
Write-Host ""

Write-GapCollection -Title "Open gaps:" -Gaps $openGaps
Write-GapCollection -Title "Blocked gaps:" -Gaps $blockedGaps
Write-GapCollection -Title "Completed gaps:" -Gaps $completedGaps

Write-Host "Next safest gap:"
Write-Host "  Gap: $($nextSafestGap.gap_id)"
Write-Host "  Reason: $($nextSafestGap.reason)"
Write-Host "  Next action: $($nextSafestGap.next_action)"
Write-Host ""

Write-Host "Safety rules:"
foreach ($rule in @($ledger.safety_rules)) {
    Write-Host "  - $rule"
}
Write-Host ""

Write-Host "Next safe action: review gap status only; use a separate approved APPLY workflow before changing any ledger state."
