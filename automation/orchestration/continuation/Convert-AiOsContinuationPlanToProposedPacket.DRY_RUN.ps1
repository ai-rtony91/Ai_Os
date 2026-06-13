param(
    [switch]$OutputJson,
    [string]$RepoRoot = "",
    [string]$ContinuationPlanPath = "",
    [string]$ContinuationPlanJson = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    param([string]$CandidateRoot)

    if (-not [string]::IsNullOrWhiteSpace($CandidateRoot)) {
        try {
            return (Resolve-Path -LiteralPath $CandidateRoot -ErrorAction Stop).Path
        }
        catch {
            throw "Invalid RepoRoot provided: $CandidateRoot"
        }
    }

    try {
        $gitRoot = git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($gitRoot)) {
            return $gitRoot.Trim()
        }
    }
    catch {
        # Ignore and fall back.
    }

    return (Resolve-Path $PSScriptRoot/..).Path
}

function Read-JsonSafe {
    param([string]$Text, [string]$Source)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return [pscustomobject]@{
            _aios_parse_error = "JSON payload was empty."
            _aios_source = $Source
        }
    }

    $candidate = [string]$Text
    $trimmed = $candidate.Trim()
    try {
        return $candidate | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        $start = $candidate.IndexOf("{")
        $end = $candidate.LastIndexOf("}")
        if ($start -lt 0 -or $end -lt $start) {
            return [pscustomobject]@{
                _aios_parse_error = $_.Exception.Message
                _aios_source = $Source
            }
        }
        try {
            return $candidate.Substring($start, $end - $start + 1) | ConvertFrom-Json -ErrorAction Stop
        }
        catch {
            return [pscustomobject]@{
                _aios_parse_error = $_.Exception.Message
                _aios_source = $Source
            }
        }
    }
}

function Invoke-JsonCommand {
    param([string]$Path, [string[]]$Arguments)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $Path @Arguments 2>$null
        if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
        return Read-JsonSafe -Text ($raw | Out-String) -Source $Path
    }
    catch {
        return [pscustomobject]@{
            _aios_parse_error = $_.Exception.Message
            _aios_source = $Path
        }
    }
}

function Has-MemberValue {
    param($Object, [string]$Name)
    if ($null -eq $Object) { return $false }
    return ($Object.PSObject.Properties.Name -contains $Name)
}

function To-StringList {
    param($Value, [string]$Fallback = "")
    if ($null -eq $Value) { return @($Fallback) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } }
    if ($Value -is [string]) {
        return @([string]$Value)
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        return @($Value)
    }
    return @([string]$Value)
}

function Validate-InvariantList {
    param($Collection, [string]$FieldName)
    if ($null -eq $Collection) { return "$FieldName is null." }
    if ($Collection -is [array] -and $Collection.Count -eq 0) { return "$FieldName is empty." }
    if ($Collection -is [string] -and [string]::IsNullOrWhiteSpace($Collection)) { return "$FieldName is empty." }
    return ""
}

$repoRoot = Resolve-RepoRoot -CandidateRoot $RepoRoot
$gitStatusRaw = @(git -C $repoRoot status --short --untracked-files=all 2>$null)
$dirtyOrUntrackedCount = $gitStatusRaw.Count
$branch = (git -C $repoRoot branch --show-current 2>$null).Trim()
if ([string]::IsNullOrWhiteSpace($branch)) { $branch = "UNKNOWN" }

$continuationPlanPathDefault = Join-Path $repoRoot "automation/orchestration/continuation/Get-AiOsSupervisedContinuationPlan.DRY_RUN.ps1"
$continuationPlan = $null

if (-not [string]::IsNullOrWhiteSpace($ContinuationPlanJson)) {
    $continuationPlan = Read-JsonSafe -Text $ContinuationPlanJson -Source "inline-json"
}
elseif (-not [string]::IsNullOrWhiteSpace($ContinuationPlanPath)) {
    if (Test-Path -LiteralPath $ContinuationPlanPath -PathType Leaf) {
        $continuationPlan = Read-JsonSafe -Text (Get-Content -LiteralPath $ContinuationPlanPath -Raw) -Source $ContinuationPlanPath
    }
    else {
        $continuationPlan = [pscustomobject]@{
            _aios_parse_error = "ContinuationPlanPath not found: $ContinuationPlanPath"
            _aios_source = $ContinuationPlanPath
        }
    }
}
else {
    $continuationPlan = Invoke-JsonCommand -Path $continuationPlanPathDefault -Arguments @("-OutputJson")
}

$sourcePlanSchema = if (Has-MemberValue -Object $continuationPlan -Name "schema") { [string]$continuationPlan.schema } else { "UNKNOWN" }
$sourceContinuationStatus = if (Has-MemberValue -Object $continuationPlan -Name "continuation_status") { [string]$continuationPlan.continuation_status } else { "UNKNOWN" }

$executionAllowed = if (Has-MemberValue -Object $continuationPlan -Name "execution_allowed") { [bool]$continuationPlan.execution_allowed } else { $false }
$humanApprovalRequired = if (Has-MemberValue -Object $continuationPlan -Name "human_approval_required") { [bool]$continuationPlan.human_approval_required } else { $true }
$canContinueWithoutAnthony = if (Has-MemberValue -Object $continuationPlan -Name "can_continue_without_anthony") { [bool]$continuationPlan.can_continue_without_anthony } else { $true }

$recommendedPacketId = if (Has-MemberValue -Object $continuationPlan -Name "recommended_next_packet_id") { [string]$continuationPlan.recommended_next_packet_id } else { "" }
$recommendedPacketTitle = if (Has-MemberValue -Object $continuationPlan -Name "recommended_next_packet_title") { [string]$continuationPlan.recommended_next_packet_title } else { "" }
$recommendedLane = if (Has-MemberValue -Object $continuationPlan -Name "recommended_lane") { [string]$continuationPlan.recommended_lane } else { "" }
$recommendedFiles = if (Has-MemberValue -Object $continuationPlan -Name "recommended_files") { To-StringList -Value $continuationPlan.recommended_files } else { @() }
$requiredValidators = if (Has-MemberValue -Object $continuationPlan -Name "required_validators") { To-StringList -Value $continuationPlan.required_validators } else { @() }
$blockedActions = if (Has-MemberValue -Object $continuationPlan -Name "blocked_actions") { To-StringList -Value $continuationPlan.blocked_actions } else { @() }

$invariantFailures = @()
if ($sourceContinuationStatus -ne "READY_FOR_APPROVAL") { $invariantFailures += "continuation_status is not READY_FOR_APPROVAL." }
if ($executionAllowed -ne $false) { $invariantFailures += "execution_allowed is not false." }
if ($humanApprovalRequired -ne $true) { $invariantFailures += "human_approval_required is not true." }
if ($canContinueWithoutAnthony -ne $false) { $invariantFailures += "can_continue_without_anthony is not false." }
if ([string]::IsNullOrWhiteSpace($recommendedPacketId)) { $invariantFailures += "recommended_next_packet_id is empty." }
if (($msg = Validate-InvariantList -Collection $recommendedFiles -FieldName "recommended_files")) { $invariantFailures += $msg }
if (($msg = Validate-InvariantList -Collection $requiredValidators -FieldName "required_validators")) { $invariantFailures += $msg }
if (($msg = Validate-InvariantList -Collection $blockedActions -FieldName "blocked_actions")) { $invariantFailures += $msg }
if (Has-MemberValue -Object $continuationPlan -Name "_aios_parse_error") { $invariantFailures += "continuation plan parse failure." }

if ($dirtyOrUntrackedCount -gt 0) {
    $invariantFailures += "Repository has dirty or untracked state ($dirtyOrUntrackedCount)."
}

$proposedPacketStatus = if ($invariantFailures.Count -eq 0) { "READY_FOR_APPROVAL" } else { "BLOCKED" }
$proposedPacketId = $recommendedPacketId
$proposedPacketPath = "automation/orchestration/work_packets/proposed/AIOS-FOREX-PAPER-STUDY-JOURNAL-APPLY-V1.md"
$exactNextSafeAction = if ($invariantFailures.Count -eq 0) {
    "Anthony review and approval for execution of packet '$proposedPacketId'."
} else {
    "Resolve invariant and repository-state blockers before generating a safe proposal."
}

$blockExecutionText = [System.Collections.Generic.List[string]]::new()
foreach ($item in $blockedActions) {
    [void]$blockExecutionText.Add([string]$item)
}
if ($blockExecutionText.Count -eq 0) {
    $blockExecutionText = @(
        "live trading",
        "broker/OANDA",
        "real orders",
        "real webhooks",
        "real market data",
        "API keys/secrets",
        "scheduler/daemon",
        "worker launch",
        "runtime mutation",
        "telemetry mutation",
        "dashboard mutation",
        "Cloudflare",
        "backup sync",
        "push/PR/merge automation",
        "approval inbox mutation",
        "queue mutation",
        "worker start"
    )
}

$proposedPayload = $null
$packetValidationStatus = "PASS"
if ($proposedPacketStatus -eq "READY_FOR_APPROVAL") {
    $proposedPayload = [ordered]@{
        packet_id = $recommendedPacketId
        mode = "APPLY"
        lane = $recommendedLane
        owner_lane = $recommendedLane
        mission = "build Sprint 18 paper study journal from Sprint 17 continuity review output"
        recommended_files = @($recommendedFiles)
        required_validators = @($requiredValidators)
        blocked_actions = @($blockExecutionText)
        allowed_write_boundary = @($recommendedFiles)
        execution_allowed = $false
        human_approval_required = $true
        can_continue_without_anthony = $false
        stop_condition = "Stop after local commit only; no push/PR/merge automation."
        safety = @(
            "no broker/OANDA",
            "no webhook",
            "no order",
            "no network side-effect",
            "no scheduler/daemon",
            "no worker launch",
            "no runtime mutation",
            "no telemetry mutation",
            "no dashboard mutation",
            "no Cloudflare",
            "no backup sync"
        )
        title = $recommendedPacketTitle
        exact_next_safe_action = $exactNextSafeAction
    }

    $packetValidationStatus = "PASS"
}

$reason = if ($proposedPacketStatus -eq "READY_FOR_APPROVAL") {
    "Continuation plan is ready for approval and all required safety invariants passed."
} else {
    if ($invariantFailures.Count -gt 0) {
        "Blocked until all invariants and safety gates pass. " + ($invariantFailures -join " ")
    } else {
        "Blocked due to unresolved continuity/validation blockers."
    }
}

$result = [ordered]@{
    schema = "AIOS_CONTINUATION_TO_PROPOSED_PACKET_PREVIEW.v1"
    mode = "DRY_RUN_READ_ONLY"
    repo_root = $repoRoot
    branch = $branch
    dirty_or_untracked_count = $dirtyOrUntrackedCount
    source_plan_schema = $sourcePlanSchema
    source_continuation_status = $sourceContinuationStatus
    proposed_packet_status = $proposedPacketStatus
    proposed_packet_id = $proposedPacketId
    proposed_packet_title = $recommendedPacketTitle
    proposed_packet_lane = $recommendedLane
    proposed_packet_path = $proposedPacketPath
    proposed_packet_payload = $proposedPayload
    packet_validation_status = $packetValidationStatus
    execution_allowed = $false
    human_approval_required = $true
    can_continue_without_anthony = $false
    writes_files = $false
    mutates_runtime = $false
    mutates_approval = $false
    mutates_queue = $false
    starts_worker = $false
    blocked_actions = @($blockExecutionText)
    exact_next_safe_action = $exactNextSafeAction
    reason = $reason
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($result | ConvertTo-Json -Depth 20)
