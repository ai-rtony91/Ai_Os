[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$CommandText = "",

    [Parameter(Mandatory = $false)]
    [string[]]$ApprovalMarkers = @(),

    [Parameter(Mandatory = $false)]
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$protectedMarkers = @{
    STAGE_EXACT_FILES = "APPROVE_STAGE_EXACT_FILES"
    COMMIT            = "APPROVE_COMMIT"
    PUSH              = "APPROVE_PUSH"
    PR_CREATE         = "APPROVE_PR_CREATE"
    MERGE             = "APPROVE_MERGE"
    BRANCH_DELETE     = "APPROVE_BRANCH_DELETE"
    RESET_OR_CLEAN    = "APPROVE_RESET_OR_CLEAN"
}

function Test-AiOsMarker {
    param(
        [string]$Marker,
        [string[]]$Markers
    )

    return @($Markers | Where-Object { $_ -eq $Marker }).Count -gt 0
}

function New-AiOsGateResult {
    param(
        [string]$Command,
        [string]$RequestedAction,
        [string]$RequiredMarker,
        [string]$Decision,
        [string]$Reason,
        [string]$Severity = "INFO"
    )

    $markerStatus = if ([string]::IsNullOrWhiteSpace($RequiredMarker)) {
        "NOT_APPLICABLE"
    }
    elseif (Test-AiOsMarker -Marker $RequiredMarker -Markers $ApprovalMarkers) {
        "GRANTED"
    }
    else {
        "MISSING"
    }

    [pscustomobject]@{
        command_preview          = $Command
        requested_action         = $RequestedAction
        approval_marker_required = $RequiredMarker
        approval_marker_status   = $markerStatus
        decision                 = $Decision
        severity                 = $Severity
        reason                   = $Reason
    }
}

function Test-AiOsProtectedCommand {
    param([string]$Command)

    $normalized = ($Command -replace "\s+", " ").Trim()

    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "UNKNOWN" `
            -RequiredMarker "" `
            -Decision "HUMAN_APPROVAL_REQUIRED" `
            -Severity "WARN" `
            -Reason "No command text was provided."
    }

    if ($normalized -match "(?i)^git add (\.|-A|--all)(\s|$)") {
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "STAGE_EXACT_FILES" `
            -RequiredMarker "BLOCK_PROTECTED_ACTION" `
            -Decision "BLOCKED" `
            -Severity "BLOCKED" `
            -Reason "Broad staging is blocked. Use exact-file staging only after approval."
    }

    if ($normalized -match "(?i)^git push\s+origin\s+main(\s|$)") {
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "PUSH" `
            -RequiredMarker "BLOCK_PROTECTED_ACTION" `
            -Decision "BLOCKED" `
            -Severity "BLOCKED" `
            -Reason "Direct push to main is blocked for protected work."
    }

    if ($normalized -match "(?i)^git push\b.*\s(--force|-f)(\s|$)") {
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "PUSH" `
            -RequiredMarker "BLOCK_PROTECTED_ACTION" `
            -Decision "BLOCKED" `
            -Severity "BLOCKED" `
            -Reason "Force push is blocked."
    }

    if ($normalized -match "(?i)^git reset\s+--hard(\s|$)") {
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "RESET_OR_CLEAN" `
            -RequiredMarker $protectedMarkers.RESET_OR_CLEAN `
            -Decision "BLOCKED" `
            -Severity "BLOCKED" `
            -Reason "git reset --hard requires a dedicated recovery approval and remains blocked by default."
    }

    if ($normalized -match "(?i)^git clean(\s|$)") {
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "RESET_OR_CLEAN" `
            -RequiredMarker $protectedMarkers.RESET_OR_CLEAN `
            -Decision "BLOCKED" `
            -Severity "BLOCKED" `
            -Reason "git clean requires a dedicated recovery approval and remains blocked by default."
    }

    if ($normalized -match "(?i)^git branch\s+-D(\s|$)|^git push\s+origin\s+--delete(\s|$)") {
        $required = $protectedMarkers.BRANCH_DELETE
        $decision = if (Test-AiOsMarker -Marker $required -Markers $ApprovalMarkers) { "HUMAN_APPROVAL_REQUIRED" } else { "BLOCKED" }
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "BRANCH_DELETE" `
            -RequiredMarker $required `
            -Decision $decision `
            -Severity "WARN" `
            -Reason "Branch deletion requires separate approval and must not be inferred from merge approval."
    }

    if ($normalized -match "(?i)^gh pr merge(\s|$)|^git merge(\s|$)") {
        $required = $protectedMarkers.MERGE
        $decision = if (Test-AiOsMarker -Marker $required -Markers $ApprovalMarkers) { "HUMAN_APPROVAL_REQUIRED" } else { "BLOCKED" }
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "MERGE" `
            -RequiredMarker $required `
            -Decision $decision `
            -Severity "WARN" `
            -Reason "Merge requires APPROVE_MERGE. CI pass and validator output do not authorize merge."
    }

    if ($normalized -match "(?i)^git commit(\s|$)") {
        $required = $protectedMarkers.COMMIT
        $decision = if (Test-AiOsMarker -Marker $required -Markers $ApprovalMarkers) { "HUMAN_APPROVAL_REQUIRED" } else { "BLOCKED" }
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "COMMIT" `
            -RequiredMarker $required `
            -Decision $decision `
            -Severity "WARN" `
            -Reason "Commit requires APPROVE_COMMIT and cached diff evidence."
    }

    if ($normalized -match "(?i)^git push(\s|$)") {
        $required = $protectedMarkers.PUSH
        $decision = if (Test-AiOsMarker -Marker $required -Markers $ApprovalMarkers) { "HUMAN_APPROVAL_REQUIRED" } else { "BLOCKED" }
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "PUSH" `
            -RequiredMarker $required `
            -Decision $decision `
            -Severity "WARN" `
            -Reason "Push requires APPROVE_PUSH. Commit approval does not approve push."
    }

    if ($normalized -match "(?i)^gh pr create(\s|$)") {
        $required = $protectedMarkers.PR_CREATE
        $decision = if (Test-AiOsMarker -Marker $required -Markers $ApprovalMarkers) { "HUMAN_APPROVAL_REQUIRED" } else { "BLOCKED" }
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "PR_CREATE" `
            -RequiredMarker $required `
            -Decision $decision `
            -Severity "WARN" `
            -Reason "PR creation requires APPROVE_PR_CREATE."
    }

    if ($normalized -match "(?i)^git add(\s|$)") {
        $required = $protectedMarkers.STAGE_EXACT_FILES
        $decision = if (Test-AiOsMarker -Marker $required -Markers $ApprovalMarkers) { "HUMAN_APPROVAL_REQUIRED" } else { "BLOCKED" }
        return New-AiOsGateResult `
            -Command $Command `
            -RequestedAction "STAGE_EXACT_FILES" `
            -RequiredMarker $required `
            -Decision $decision `
            -Severity "WARN" `
            -Reason "Staging requires APPROVE_STAGE_EXACT_FILES and exact file scope."
    }

    return New-AiOsGateResult `
        -Command $Command `
        -RequestedAction "READ_OR_UNKNOWN" `
        -RequiredMarker "" `
        -Decision "PASS" `
        -Severity "INFO" `
        -Reason "No protected action pattern was detected."
}

$commandsToCheck = if ([string]::IsNullOrWhiteSpace($CommandText)) {
    @(
        "git add .",
        "git add -A",
        "git add --all",
        "git push origin main",
        "git push --force",
        "git reset --hard HEAD~1",
        "git clean -fd",
        "gh pr merge 240 --squash",
        "git branch -D feature/example",
        "git commit -m `"example`"",
        "git push origin feature/example"
    )
}
else {
    @($CommandText)
}

$results = @($commandsToCheck | ForEach-Object { Test-AiOsProtectedCommand -Command $_ })
$blockedCount = @($results | Where-Object { $_.decision -eq "BLOCKED" }).Count
$warnCount = @($results | Where-Object { $_.severity -eq "WARN" }).Count
$passCount = @($results | Where-Object { $_.decision -eq "PASS" }).Count

$summary = [pscustomobject]@{
    schema                     = "AIOS_PROTECTED_ACTION_GATE_DRY_RUN.v1"
    mode                       = "DRY_RUN"
    mutation_performed         = $false
    staging_performed          = $false
    commit_performed           = $false
    push_performed             = $false
    merge_performed            = $false
    deletion_performed         = $false
    reset_or_clean_performed   = $false
    commands_checked           = $results.Count
    pass_count                 = $passCount
    warn_count                 = $warnCount
    blocked_count              = $blockedCount
    gate_status                = if ($blockedCount -gt 0) { "BLOCKED" } elseif ($warnCount -gt 0) { "WARN" } else { "PASS" }
    next_safe_action           = "Review protected action findings. Do not execute protected actions without exact current-session Human Owner approval."
    results                    = $results
}

if ($OutputJson) {
    $summary | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Protected Action Gate Validator"
Write-Host "Mode: DRY_RUN"
Write-Host "Mutation performed: NO"
Write-Host "Staging performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Merge performed: NO"
Write-Host "Deletion performed: NO"
Write-Host "Reset or clean performed: NO"
Write-Host ""
Write-Host ("Gate status: {0}" -f $summary.gate_status)
Write-Host ("Commands checked: {0}" -f $summary.commands_checked)
Write-Host ("Blocked: {0}" -f $summary.blocked_count)
Write-Host ("Warnings: {0}" -f $summary.warn_count)
Write-Host ("Pass: {0}" -f $summary.pass_count)
Write-Host ""

foreach ($result in $results) {
    Write-Host ("[{0}] {1}" -f $result.decision, $result.command_preview)
    Write-Host ("  required marker: {0}" -f $result.approval_marker_required)
    Write-Host ("  marker status: {0}" -f $result.approval_marker_status)
    Write-Host ("  reason: {0}" -f $result.reason)
}

Write-Host ""
Write-Host "JSON-style summary:"
$summary | ConvertTo-Json -Depth 8
