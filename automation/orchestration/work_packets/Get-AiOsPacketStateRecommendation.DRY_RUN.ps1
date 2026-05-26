[CmdletBinding()]
param(
    [string]$PacketPath = "",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Resolve-AiOsRelativePath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    $root = (Get-Location).Path + [IO.Path]::DirectorySeparatorChar
    return ((Resolve-Path -LiteralPath $Path).Path.Replace($root, "") -replace "\\", "/")
}

function Get-AiOsNewestActivePacketPath {
    $activePacketRoot = "automation/orchestration/work_packets/active"
    if (-not (Test-Path -LiteralPath $activePacketRoot -PathType Container)) {
        return ""
    }

    $packet = Get-ChildItem -LiteralPath $activePacketRoot -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $packet) { return "" }
    return $packet.FullName
}

function Invoke-AiOsQuietJson {
    param([string]$ScriptPath)

    if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        return $null
    }

    return powershell -ExecutionPolicy Bypass -File $ScriptPath -QuietJson | ConvertFrom-Json
}

function Normalize-AiOsPacketState {
    param([string]$State)

    switch ($State) {
        "active" { "draft"; break }
        "new" { "draft"; break }
        "dry_run_done" { "validation_ready"; break }
        "validated" { "validation_ready"; break }
        "awaiting_approval" { "approval_ready"; break }
        "approved" { "commit_ready"; break }
        "applying" { "commit_ready"; break }
        "failed" { "blocked"; break }
        default { if ([string]::IsNullOrWhiteSpace($State)) { "draft" } else { $State } }
    }
}

function Test-AiOsMissingPacketField {
    param($Packet, [string]$FieldName)

    return (-not ($Packet.PSObject.Properties.Name -contains $FieldName) -or [string]::IsNullOrWhiteSpace([string]$Packet.$FieldName))
}

if ([string]::IsNullOrWhiteSpace($PacketPath)) {
    $PacketPath = Get-AiOsNewestActivePacketPath
}

$warnings = @()
$packet = $null
$packetId = "UNKNOWN"
$currentState = "UNKNOWN"
$normalizedState = "blocked"
$recommendedNextState = "blocked"
$transitionAllowed = $false
$reason = "Packet could not be evaluated."
$requiredOperatorAction = "Review packet path and JSON parse result."
$commandToApplyLater = "No APPLY command recommended."

if ([string]::IsNullOrWhiteSpace($PacketPath) -or -not (Test-Path -LiteralPath $PacketPath -PathType Leaf)) {
    $warnings += "No active packet JSON file found."
}
else {
    try {
        $packet = Get-Content -LiteralPath $PacketPath -Raw | ConvertFrom-Json
        $packetId = if ($packet.packet_id) { [string]$packet.packet_id } else { Split-Path -LeafBase $PacketPath }
        $currentState = if ($packet.status) { [string]$packet.status } else { "draft" }
        $normalizedState = Normalize-AiOsPacketState -State $currentState
    }
    catch {
        $warnings += "Packet JSON parse failed: $($_.Exception.Message)"
    }
}

$repoBranch = git branch --show-current
$gitStatus = @(git status --short --untracked-files=all)
$validatorRecommendation = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1"
$commitPackageRecommendation = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"
$approvalSummary = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
$workerLockStatus = Invoke-AiOsQuietJson -ScriptPath "automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1"

if ($packet) {
    $missingFields = @()
    foreach ($field in @("packet_id", "owner_lane", "repo", "branch")) {
        if (Test-AiOsMissingPacketField -Packet $packet -FieldName $field) { $missingFields += $field }
    }
    if ((Test-AiOsMissingPacketField -Packet $packet -FieldName "title") -and (Test-AiOsMissingPacketField -Packet $packet -FieldName "intent")) {
        $missingFields += "title_or_intent"
    }
    if ($missingFields.Count -gt 0) {
        $warnings += "Missing packet fields: $($missingFields -join ', ')."
    }

    if ($packet.branch -and [string]$packet.branch -ne $repoBranch) {
        $warnings += "Packet branch '$($packet.branch)' does not match current repo branch '$repoBranch'."
    }

    if (@($packet.blocked_by).Count -gt 0) {
        $warnings += "Packet has blocked_by entries: $(@($packet.blocked_by) -join ', ')."
    }
}

if ($commitPackageRecommendation -and @($commitPackageRecommendation.risky_files).Count -gt 0) {
    $warnings += "Commit package recommendation includes risky files."
}

if ($approvalSummary -and @($approvalSummary.blocked_actions).Count -gt 0) {
    $warnings += "Approval inbox contains blocked actions."
}

if ($workerLockStatus) {
    foreach ($lock in @($workerLockStatus.locks)) {
        if ($lock.stale_lock_warning -and [string]$lock.stale_lock_warning -ne "NO") {
            $warnings += "Worker lock warning: $($lock.stale_lock_warning)"
        }
    }
}

$hasHardWarning = ($warnings | Where-Object { $_ -like "Packet JSON parse failed:*" -or $_ -like "Missing packet fields:*" -or $_ -like "Packet has blocked_by entries:*" -or $_ -like "Commit package recommendation includes risky files.*" -or $_ -like "Approval inbox contains blocked actions.*" -or $_ -like "Worker lock warning:*" }).Count -gt 0

if ($hasHardWarning) {
    $recommendedNextState = "blocked"
    $transitionAllowed = $normalizedState -ne "complete"
    $reason = "Blocking warning found; packet should be reviewed before advancement."
    $requiredOperatorAction = "Resolve warnings before applying a state transition."
}
elseif ($normalizedState -eq "complete") {
    $recommendedNextState = "complete"
    $transitionAllowed = $false
    $reason = "Packet is already complete."
    $requiredOperatorAction = "No transition needed."
}
elseif ($normalizedState -eq "blocked") {
    $recommendedNextState = "routed"
    $transitionAllowed = $true
    $reason = "No hard blocker currently detected; blocked packet may be routed after operator review."
    $requiredOperatorAction = "Operator reviews blocker clearance before applying transition."
}
elseif ($normalizedState -eq "draft") {
    $recommendedNextState = "routed"
    $transitionAllowed = $true
    $reason = "Packet has enough routing metadata for routed state."
    $requiredOperatorAction = "Operator may route packet after review."
}
elseif ($normalizedState -eq "routed") {
    $recommendedNextState = "validation_ready"
    $transitionAllowed = $true
    $reason = "Validator recommendation is available and no packet blocker is listed."
    $requiredOperatorAction = "Run or review validator recommendation before applying transition."
}
elseif ($normalizedState -eq "validation_ready") {
    if ($validatorRecommendation -and [string]$validatorRecommendation.approval_required -eq "NO") {
        $recommendedNextState = "approval_ready"
        $transitionAllowed = $true
        $reason = "Validation path exists and approval is not required for the validator recommendation."
        $requiredOperatorAction = "Operator reviews validation output and prepares approval."
    }
    else {
        $recommendedNextState = "blocked"
        $transitionAllowed = $true
        $reason = "Validator recommendation requires approval or is unavailable."
        $requiredOperatorAction = "Resolve validator approval before transition."
    }
}
elseif ($normalizedState -eq "approval_ready") {
    if ($approvalSummary -and @($approvalSummary.approved_actions).Count -gt 0 -and $commitPackageRecommendation -and @($commitPackageRecommendation.approved_source_files).Count -gt 0) {
        $recommendedNextState = "commit_ready"
        $transitionAllowed = $true
        $reason = "Approved action and commit package source files are available."
        $requiredOperatorAction = "Review exact commit package before applying transition."
    }
    else {
        $recommendedNextState = "approval_ready"
        $transitionAllowed = $false
        $reason = "No matching approved action or approved source files are available."
        $requiredOperatorAction = "Record operator approval and prepare exact commit package."
    }
}
elseif ($normalizedState -eq "commit_ready") {
    $recommendedNextState = "complete"
    $transitionAllowed = $true
    $reason = "Commit-ready packet may complete after final validation and operator closeout."
    $requiredOperatorAction = "Run final validation and review git status before applying complete."
}
else {
    $recommendedNextState = "blocked"
    $transitionAllowed = $true
    $reason = "Unknown normalized state."
    $requiredOperatorAction = "Review packet status and update state rules."
}

if ($transitionAllowed -and $packet -and $recommendedNextState -ne $normalizedState) {
    $relativePacketPath = Resolve-AiOsRelativePath -Path $PacketPath
    $commandToApplyLater = "Separate APPLY packet-state helper required after operator approval."
}

$result = [ordered]@{
    schema = "aios_packet_state_recommendation.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    packet_id = $packetId
    current_state = $currentState
    normalized_state = $normalizedState
    recommended_next_state = $recommendedNextState
    transition_allowed = $transitionAllowed
    reason = $reason
    warnings = $warnings
    required_operator_action = $requiredOperatorAction
    command_to_apply_later = $commandToApplyLater
    current_branch = $repoBranch
    git_status_count = $gitStatus.Count
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AIOS Packet State Recommendation"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "packet_id: $packetId"
Write-Host "current_state: $currentState"
Write-Host "normalized_state: $normalizedState"
Write-Host "recommended_next_state: $recommendedNextState"
Write-Host "transition_allowed: $transitionAllowed"
Write-Host "reason: $reason"
Write-Host "warnings:"
if ($warnings.Count -eq 0) { Write-Host "- none" } else { $warnings | ForEach-Object { Write-Host "- $_" } }
Write-Host "required_operator_action: $requiredOperatorAction"
Write-Host "command_to_apply_later:"
Write-Host $commandToApplyLater
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
