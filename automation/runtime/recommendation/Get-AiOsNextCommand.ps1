param(
    [switch]$QuietJson,
    [switch]$OutputJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            parse_error = $_.Exception.Message
            path = $Path
        }
    }
}

function Invoke-AiOsQuietJsonCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string[]]$Arguments = @()
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        $rawOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $Path @Arguments 2>$null
        $jsonText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            return $null
        }
        return $jsonText | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Get-SelfBuildDecisionReadout {
    $consumerPath = "automation/orchestration/autonomy_control_plane/aios_self_build_decision_consumer.py"
    $evidencePath = "Reports/self_build_cycle/latest_self_build_cycle.evidence.json"
    if (-not (Test-Path -LiteralPath $consumerPath -PathType Leaf)) {
        return [ordered]@{
            status = "UNAVAILABLE"
            operator_route = "REPORT_ONLY"
            approval_required = $false
            report_only = $true
            safe_next_action = "Self-build decision consumer is unavailable; run the autonomy status report."
        }
    }
    try {
        $rawOutput = & python $consumerPath --evidence $evidencePath 2>$null
        $jsonText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            throw "consumer produced no JSON output"
        }
        $readout = $jsonText | ConvertFrom-Json
        return [ordered]@{
            status = [string]$readout.normalized_status
            operator_route = [string]$readout.operator_route
            approval_required = [bool]$readout.approval_required
            report_only = [bool]$readout.report_only
            safe_next_action = [string]$readout.safe_next_action
        }
    } catch {
        return [ordered]@{
            status = "REVIEW_REQUIRED"
            operator_route = "APPROVAL_REVIEW_REQUIRED"
            approval_required = $true
            report_only = $true
            safe_next_action = "Review self-build decision consumer failure before choosing the next command."
        }
    }
}

function Get-ApprovalSummaryReadout {
    $summaryPath = "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
    $inboxPath = "automation/orchestration/approval_inbox"
    if (-not (Test-Path -LiteralPath $summaryPath -PathType Leaf)) {
        return [ordered]@{
            available = $false
            pending_count = 0
            blocked_count = 0
            completed_count = 0
            safe_state = "UNAVAILABLE"
            next_review_action = "Approval summary is unavailable; run the approval inbox summary directly if approval state is needed."
        }
    }
    try {
        $rawOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $summaryPath -InboxPath $inboxPath -QuietJson 2>$null
        $jsonText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            throw "approval summary produced no JSON output"
        }
        $summary = $jsonText | ConvertFrom-Json
        $pendingCount = @($summary.pending_approvals).Count
        $blockedCount = @($summary.blocked_actions).Count
        $completedCount = @($summary.approved_actions).Count
        $safeState = if ($blockedCount -gt 0) { "BLOCKED" } elseif (($pendingCount + $completedCount) -gt 0) { "REVIEW" } else { "PASS" }
        return [ordered]@{
            available = $true
            pending_count = $pendingCount
            blocked_count = $blockedCount
            completed_count = $completedCount
            safe_state = $safeState
            next_review_action = [string]$summary.next_safe_command
        }
    } catch {
        return [ordered]@{
            available = $false
            pending_count = 0
            blocked_count = 0
            completed_count = 0
            safe_state = "REVIEW_REQUIRED"
            next_review_action = "Review approval summary failure before choosing the next command."
        }
    }
}

$runtimeStatePath = "automation/runtime/state/AIOS_RUNTIME_STATE.json"
$activePacketRoot = "automation/orchestration/work_packets/active"
$runtimeHealthScript = "automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
$campaignNextTaskScript = "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1"
$validatorRoots = @(
    "automation/validators",
    "automation/orchestration/validators",
    "scripts/validation"
)

$runtimeState = Read-JsonFile -Path $runtimeStatePath
$runtimeHealthReadout = Invoke-AiOsQuietJsonCommand -Path $runtimeHealthScript -Arguments @("-QuietJson")
$campaignReadout = Invoke-AiOsQuietJsonCommand -Path $campaignNextTaskScript -Arguments @("-OutputJson")
$selfBuildDecision = Get-SelfBuildDecisionReadout
$approvalSummary = Get-ApprovalSummaryReadout
$gitStatus = @(git status --short)
$activePackets = @()
if (Test-Path -LiteralPath $activePacketRoot -PathType Container) {
    $activePackets = @(Get-ChildItem -LiteralPath $activePacketRoot -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
}

$validatorPresent = $false
foreach ($validatorRoot in $validatorRoots) {
    if (Test-Path -LiteralPath $validatorRoot -PathType Container) {
        $validatorPresent = $true
        break
    }
}

$packet = $null
if ($activePackets.Count -gt 0) {
    $packet = Read-JsonFile -Path $activePackets[0].FullName
}

$packetStatus = $(if ($packet -and $packet.status) { [string]$packet.status } else { "UNKNOWN" })
$runtimeHealth = $(if ($runtimeHealthReadout -and $runtimeHealthReadout.health) { [string]$runtimeHealthReadout.health } elseif ($runtimeState -and $runtimeState.health) { [string]$runtimeState.health } else { "UNKNOWN" })
$recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/runtime/reports/Write-AiOsRepoStatusReport.ps1"
$why = "Start with an operator-readable repo status report."
$manualWorkRemoved = "Reduces manual checking of git status, packet folders, runtime state, and validator folders."
$safeToRun = "YES - read-only inspection only."
$approvalRequired = "NO"

if (-not $runtimeState) {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/runtime/state/Write-AiOsRuntimeState.ps1"
    $why = "Runtime state is missing and should be regenerated before choosing the next operator command."
    $manualWorkRemoved = "Removes manual reconstruction of current runtime health."
}
elseif ($runtimeState.parse_error) {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/runtime/state/Write-AiOsRuntimeState.ps1"
    $why = "Runtime state JSON could not be parsed."
    $manualWorkRemoved = "Rebuilds the operator summary from runtime health checks."
}
elseif ($runtimeHealth -ne "HEALTHY") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
    $why = "Runtime health is $runtimeHealth."
    $manualWorkRemoved = "Points directly to the health check instead of requiring manual folder inspection."
}
elseif ($activePackets.Count -eq 0 -and $campaignReadout -and [string]$campaignReadout.overall_readiness -eq "READY_FOR_PACKET_PREVIEW") {
    $recommendedCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1 -OutputJson"
    $why = "No active packet is available; campaign registry has a READY packet candidate."
    $manualWorkRemoved = "Uses the canonical campaign registry instead of searching packet folders manually."
}
elseif ($activePackets.Count -eq 0) {
    $recommendedCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1 -OutputJson"
    $why = "No active packet is available and no READY campaign stage was selected."
    $manualWorkRemoved = "Shows the canonical reason routing cannot select a next packet."
}
elseif ($packetStatus -eq "awaiting_approval") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1"
    $why = "The active packet is waiting for approval."
    $manualWorkRemoved = "Narrows the next operator step to approval review."
}
elseif ($packetStatus -eq "blocked" -or $packetStatus -eq "failed") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1"
    $why = "The active packet status is $packetStatus."
    $manualWorkRemoved = "Avoids manual blocker triage."
}
elseif (-not $validatorPresent) {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/runtime/reports/Write-AiOsRepoStatusReport.ps1"
    $why = "No validator folder was found."
    $manualWorkRemoved = "Surfaces validator absence before execution work starts."
}
elseif ($gitStatus.Count -gt 0) {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/runtime/reports/Write-AiOsRepoStatusReport.ps1"
    $why = "Working tree has changes and should be summarized before selective commit decisions."
    $manualWorkRemoved = "Collects changed files and packet context in one operator report."
}
else {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/advancement/Invoke-AiOsPacketAdvancement.DRY_RUN.ps1"
    $why = "Runtime is healthy, validators are present, and an active packet can continue in DRY_RUN."
    $manualWorkRemoved = "Turns packet state into the next safe command."
}

$result = [ordered]@{
    schema = "aios_next_command.v1"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    next_best_step = $recommendedCommand
    why = $why
    manual_work_removed = $manualWorkRemoved
    safe_to_run = $safeToRun
    approval_required = $approvalRequired
    runtime_health = $runtimeHealth
    active_packet_count = $activePackets.Count
    campaign_readiness = if ($campaignReadout -and $campaignReadout.overall_readiness) { [string]$campaignReadout.overall_readiness } else { "UNKNOWN" }
    campaign_next_packet_candidate = if ($campaignReadout -and $campaignReadout.next_packet_candidate) { [string]$campaignReadout.next_packet_candidate } else { "" }
    repo_clean = ($gitStatus.Count -eq 0)
    self_build_decision_status = $selfBuildDecision.status
    self_build_operator_route = $selfBuildDecision.operator_route
    self_build_approval_required = $selfBuildDecision.approval_required
    self_build_report_only = $selfBuildDecision.report_only
    self_build_safe_next_action = $selfBuildDecision.safe_next_action
    approval_summary_available = $approvalSummary.available
    approval_pending_count = $approvalSummary.pending_count
    approval_blocked_count = $approvalSummary.blocked_count
    approval_completed_count = $approvalSummary.completed_count
    approval_safe_state = $approvalSummary.safe_state
    approval_next_review_action = $approvalSummary.next_review_action
    approvals_performed = "NO"
    approval_inbox_mutated = "NO"
    apply_gate_mutated = "NO"
    protected_action_allowed = "NO"
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson -or $OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "NEXT BEST STEP:"
Write-Host $result.next_best_step
Write-Host "WHY:"
Write-Host $result.why
Write-Host "MANUAL WORK REMOVED:"
Write-Host $result.manual_work_removed
Write-Host "SAFE TO RUN:"
Write-Host $result.safe_to_run
Write-Host "APPROVAL REQUIRED:"
Write-Host $result.approval_required
Write-Host "CAMPAIGN READINESS:"
Write-Host $result.campaign_readiness
Write-Host "CAMPAIGN NEXT PACKET:"
Write-Host $result.campaign_next_packet_candidate
Write-Host "SELF-BUILD DECISION:"
Write-Host $result.self_build_decision_status
Write-Host "SELF-BUILD ROUTE:"
Write-Host $result.self_build_operator_route
Write-Host "SELF-BUILD APPROVAL REQUIRED:"
Write-Host $result.self_build_approval_required
Write-Host "SELF-BUILD SAFE NEXT ACTION:"
Write-Host $result.self_build_safe_next_action
Write-Host "APPROVAL STATE SUMMARY:"
Write-Host "available=$($result.approval_summary_available); pending=$($result.approval_pending_count); blocked=$($result.approval_blocked_count); completed=$($result.approval_completed_count); safe_state=$($result.approval_safe_state)"
Write-Host "APPROVAL NEXT REVIEW ACTION:"
Write-Host $result.approval_next_review_action
Write-Host "Approvals performed: NO"
Write-Host "Approval inbox mutated: NO"
Write-Host "Apply gate mutated: NO"
Write-Host "Protected action allowed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
