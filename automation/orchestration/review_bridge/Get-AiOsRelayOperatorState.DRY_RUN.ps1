param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RelayLatestFile {
    param([string]$Directory, [string]$Pattern = "*.json")

    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) {
        return $null
    }

    return Get-ChildItem -LiteralPath $Directory -Filter $Pattern -File |
        Sort-Object -Property LastWriteTime -Descending |
        Select-Object -First 1
}

function Parse-RelayJson {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
}

function Get-ActorRelayBusState {
    param([string]$RepoRoot)

    $relayBusStateScript = Join-Path $RepoRoot "automation/orchestration/relay_bus/Get-AiOsRelayBusState.DRY_RUN.ps1"
    if (-not (Test-Path -LiteralPath $relayBusStateScript -PathType Leaf)) {
        return $null
    }

    try {
        $rawOutput = powershell -NoProfile -ExecutionPolicy Bypass -File $relayBusStateScript -OutputJson 2>$null
        $rawText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($rawText)) {
            return $null
        }
        return $rawText | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
    return $null
  }
}

function Get-SosEscalationState {
    param([string]$RepoRoot)

    $sosScript = Join-Path $PSScriptRoot "..\\relay_bus\\Get-AiOsSosEscalationPolicy.DRY_RUN.ps1"
    if (-not (Test-Path -LiteralPath $sosScript -PathType Leaf)) {
        return $null
    }

    try {
        $rawOutput = & $sosScript -OutputJson 2>$null
        $rawText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($rawText)) {
            return $null
        }

        return $rawText | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
}

$repoRoot = (Get-Location).Path
$state = [ordered]@{
    relay_root = Join-Path $repoRoot "control/review_bridge"
    codex_reports_dir = Join-Path $repoRoot "control/review_bridge/codex_reports"
    chatgpt_prompts_dir = Join-Path $repoRoot "control/review_bridge/chatgpt_prompts"
    pasteback_dir = Join-Path $repoRoot "control/review_bridge/pasteback"
    archive_dir = Join-Path $repoRoot "control/review_bridge/archive"
}

$actorRelayState = Get-ActorRelayBusState -RepoRoot $repoRoot
$actorRelayBusStatus = if ($actorRelayState) { [string]$actorRelayState.relay_status } else { "EMPTY" }
$actorRelayLatestMessagePath = if ($actorRelayState) { [string]$actorRelayState.latest_message_path } else { "" }
$actorRelayLatestActor = if ($actorRelayState) { [string]$actorRelayState.latest_actor } else { "" }
$actorRelayLatestTargetActor = if ($actorRelayState) { [string]$actorRelayState.latest_target_actor } else { "" }
$actorRelayNextAction = if ($actorRelayState) { [string]$actorRelayState.exact_next_action } else { "Use New-AiOsRelayMessage.DRY_RUN.ps1 with Mode APPLY to write the first relay message." }

$sosEscalationStatus = "NOT_APPLICABLE"
$sosAnthonyRequired = $false
$sosRoutineReviewAllowed = $false
$sosSafeNextAction = ""
$sosMatchedCategories = New-Object System.Collections.Generic.List[string]
$routineReviewContinuationAllowed = $false
$routineReviewContinuationReason = "No routine relay review continuation context is active."
$routineReviewNextAction = ""
$routineReviewResolverCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1 -OutputJson"

if ($actorRelayBusStatus -eq "NEEDS_HUMAN_REVIEW") {
    $sosState = Get-SosEscalationState -RepoRoot $repoRoot
    if ($sosState -ne $null) {
        $sosEscalationStatus = [string]$sosState.escalation_status
        $sosAnthonyRequired = if ($sosState.PSObject.Properties.Name -contains "anthony_required") {
            [bool]$sosState.anthony_required
        }
        else {
            $false
        }
        $sosRoutineReviewAllowed = if ($sosState.PSObject.Properties.Name -contains "routine_review_allowed") {
            [bool]$sosState.routine_review_allowed
        }
        else {
            $false
        }
        if ($sosState.PSObject.Properties.Name -contains "safe_next_action") {
            $sosSafeNextAction = [string]$sosState.safe_next_action
        }
        if ($sosState.PSObject.Properties.Name -contains "matched_sos_categories") {
            foreach ($category in @($sosState.matched_sos_categories)) {
                if ($null -ne $category) {
                    [void]$sosMatchedCategories.Add([string]$category)
                }
            }
        }
    }

    if ($sosEscalationStatus -eq "SOS_ESCALATION" -or $sosAnthonyRequired) {
        $routineReviewContinuationAllowed = $false
        $routineReviewContinuationReason = "Relay review is SOS escalation or Anthony-required; continuation without Anthony is blocked."
        $routineReviewNextAction = "STOP: Anthony review required before continuation. No continuation command is recommended."
    }
    elseif ($sosEscalationStatus -eq "ROUTINE_REVIEW" -and (-not $sosAnthonyRequired) -and $sosRoutineReviewAllowed) {
        $routineReviewContinuationAllowed = $true
        $routineReviewContinuationReason = "Relay review is ROUTINE_REVIEW, Anthony is not required, and SOS policy allows governed review continuation."
        $routineReviewNextAction = $routineReviewResolverCommand
    }
    else {
        $routineReviewContinuationAllowed = $false
        $routineReviewContinuationReason = "Relay review does not meet the routine continuation gate."
        $routineReviewNextAction = "Review SOS classification before continuation."
    }
}

$latestReportFile = Get-RelayLatestFile -Directory $state.codex_reports_dir
$latestPromptFile = Get-RelayLatestFile -Directory $state.chatgpt_prompts_dir -Pattern "*.txt"
if (-not $latestPromptFile) {
    $latestPromptFile = Get-RelayLatestFile -Directory $state.chatgpt_prompts_dir -Pattern "*.json"
}
$latestPastebackFile = Get-RelayLatestFile -Directory $state.pasteback_dir

$latestReport = if ($latestReportFile) { Parse-RelayJson -Path $latestReportFile.FullName } else { $null }
$latestPrompt = $null
if ($latestPromptFile) {
    try {
        $latestPrompt = Get-Content -LiteralPath $latestPromptFile.FullName -Raw
    }
    catch {
        $latestPrompt = $null
    }
}
$latestPasteback = if ($latestPastebackFile) { Parse-RelayJson -Path $latestPastebackFile.FullName } else { $null }

$hasReport = [bool]$latestReport
$hasPrompt = [bool]$latestPrompt
$hasPasteback = [bool]$latestPasteback
$pastebackSafe = $false
$pastebackStatus = "NOT_APPLICABLE"
if ($hasPasteback) {
    $pastebackSafe = [bool]($latestPasteback.PSObject.Properties.Name -contains "safety_scan_passed" -and $latestPasteback.safety_scan_passed)
    if ($pastebackSafe) {
        $pastebackStatus = "PASSED"
    }
    else {
        $pastebackStatus = "FAILED"
    }
}

$relayStatus = "EMPTY"
$legacyNextAction = ""
$needsReport = $true
$needsPrompt = $false
$needsReview = $false
$needsPasteback = $false

if ($hasReport) {
    $needsReport = $false
    if (-not $hasPrompt) {
        $relayStatus = "NEEDS_CHATGPT_PROMPT"
        $needsPrompt = $true
        $needsReview = $false
        $needsPasteback = $true
        $legacyNextAction = "Generate a ChatGPT prompt with Invoke-AiOsCodexChatGptRelay.DRY_RUN.ps1 -Latest -OutputJson and share it manually."
    }
    elseif (-not $hasPasteback) {
        $relayStatus = "NEEDS_CHATGPT_REVIEW"
        $needsReview = $true
        $needsPasteback = $true
        $legacyNextAction = "Paste the prompt to ChatGPT and save reviewed output using New-AiOsChatGptPastebackItem.DRY_RUN.ps1 -Mode APPLY."
    }
    elseif ($pastebackSafe) {
        $relayStatus = "PASTEBACK_READY"
        $needsPasteback = $false
        $legacyNextAction = "Run the reviewed PowerShell command manually in this session."
    }
    else {
        $relayStatus = "PASTEBACK_REVIEW_REQUIRED"
        $needsPasteback = $false
        $legacyNextAction = "Fix safety issues in the pasteback artifact, then re-run New-AiOsChatGptPastebackItem.DRY_RUN.ps1."
    }
} else {
    $legacyNextAction = "Store a Codex report using New-AiOsCodexReportRelayItem.DRY_RUN.ps1 -Mode APPLY."
}

$exactNextAction = $legacyNextAction
$actorRelayBusReadyOrEmpty = @("EMPTY", "READY", "NEEDS_HUMAN_REVIEW") -contains $actorRelayBusStatus
if ($actorRelayBusReadyOrEmpty -and (-not [string]::IsNullOrWhiteSpace($actorRelayNextAction))) {
    $exactNextAction = $actorRelayNextAction
}
if (
    $actorRelayBusStatus -eq "NEEDS_HUMAN_REVIEW" -and
    (-not [string]::IsNullOrWhiteSpace($routineReviewNextAction)) -and
    ($routineReviewContinuationAllowed -or $sosEscalationStatus -eq "SOS_ESCALATION" -or $sosAnthonyRequired)
) {
    $exactNextAction = $routineReviewNextAction
}

$output = [ordered]@{
    schema = "AIOS_RELAY_OPERATOR_STATE.v1"
    mode = "DRY_RUN_READ_ONLY"
    relay_status = $relayStatus
    actor_relay_bus_status = $actorRelayBusStatus
    actor_relay_latest_message_path = $actorRelayLatestMessagePath
    actor_relay_latest_actor = $actorRelayLatestActor
    actor_relay_latest_target_actor = $actorRelayLatestTargetActor
    actor_relay_next_action = $actorRelayNextAction
    sos_escalation_status = $sosEscalationStatus
    sos_anthony_required = $sosAnthonyRequired
    sos_routine_review_allowed = $sosRoutineReviewAllowed
    sos_safe_next_action = $sosSafeNextAction
    sos_matched_categories = @($sosMatchedCategories)
    routine_review_continuation_allowed = $routineReviewContinuationAllowed
    routine_review_continuation_reason = $routineReviewContinuationReason
    routine_review_next_action = $routineReviewNextAction
    latest_codex_report_path = if ($latestReportFile) { $latestReportFile.FullName } else { "" }
    latest_chatgpt_prompt_path = if ($latestPromptFile) { $latestPromptFile.FullName } else { "" }
    latest_pasteback_path = if ($latestPastebackFile) { $latestPastebackFile.FullName } else { "" }
    needs_codex_report = $needsReport
    needs_chatgpt_prompt = $needsPrompt
    needs_chatgpt_review = $needsReview
    needs_pasteback = $needsPasteback
    pasteback_ready = $pastebackSafe
    pasteback_safety_status = $pastebackStatus
    exact_next_action = $exactNextAction
    next_safe_action = $exactNextAction
    related_existing_notes = @(
        "docs/AI_OS/autonomy/AIOS_CODEX_CHATGPT_POWERSHELL_RELAY_V1.md",
        "docs/AI_OS/autonomy/AIOS_CHATGPT_REVIEWED_PR_LIFECYCLE_BRIDGE_V1.md",
        "docs/AI_OS/autonomy/AIOS_ACTOR_RELAY_BUS_V1.md",
        "docs/AI_OS/autonomy/AIOS_RELAY_OPERATOR_MODE_V1.md"
    )
    related_existing_scripts = @(
        "automation/orchestration/review_bridge/New-AiOsCodexReportRelayItem.DRY_RUN.ps1",
        "automation/orchestration/review_bridge/Invoke-AiOsCodexChatGptRelay.DRY_RUN.ps1",
        "automation/orchestration/review_bridge/New-AiOsChatGptPastebackItem.DRY_RUN.ps1"
    )
}

$outputJsonText = $output | ConvertTo-Json -Depth 20
if ($OutputJson) {
    Write-Output $outputJsonText
    return
}

Write-Host "AI_OS Relay Operator"
Write-Host "status: $($output.relay_status)"
if ($latestReportFile) {
    Write-Host "latest_report: $($output.latest_codex_report_path)"
}
if ($latestPromptFile) {
    Write-Host "latest_prompt: $($output.latest_chatgpt_prompt_path)"
}
if ($latestPastebackFile) {
    Write-Host "latest_pasteback: $($output.latest_pasteback_path)"
}
Write-Host "next_action: $($output.exact_next_action)"
