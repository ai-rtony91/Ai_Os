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

$repoRoot = (Get-Location).Path
$state = [ordered]@{
    relay_root = Join-Path $repoRoot "control/review_bridge"
    codex_reports_dir = Join-Path $repoRoot "control/review_bridge/codex_reports"
    chatgpt_prompts_dir = Join-Path $repoRoot "control/review_bridge/chatgpt_prompts"
    pasteback_dir = Join-Path $repoRoot "control/review_bridge/pasteback"
    archive_dir = Join-Path $repoRoot "control/review_bridge/archive"
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
$nextAction = ""
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
        $nextAction = "Generate a ChatGPT prompt with Invoke-AiOsCodexChatGptRelay.DRY_RUN.ps1 -Latest -OutputJson and share it manually."
    }
    elseif (-not $hasPasteback) {
        $relayStatus = "NEEDS_CHATGPT_REVIEW"
        $needsReview = $true
        $needsPasteback = $true
        $nextAction = "Paste the prompt to ChatGPT and save reviewed output using New-AiOsChatGptPastebackItem.DRY_RUN.ps1 -Mode APPLY."
    }
    elseif ($pastebackSafe) {
        $relayStatus = "PASTEBACK_READY"
        $needsPasteback = $false
        $nextAction = "Run the reviewed PowerShell command manually in this session."
    }
    else {
        $relayStatus = "PASTEBACK_REVIEW_REQUIRED"
        $needsPasteback = $false
        $nextAction = "Fix safety issues in the pasteback artifact, then re-run New-AiOsChatGptPastebackItem.DRY_RUN.ps1."
    }
} else {
    $nextAction = "Store a Codex report using New-AiOsCodexReportRelayItem.DRY_RUN.ps1 -Mode APPLY."
}

$output = [ordered]@{
    schema = "AIOS_RELAY_OPERATOR_STATE.v1"
    mode = "DRY_RUN_READ_ONLY"
    relay_status = $relayStatus
    latest_codex_report_path = if ($latestReportFile) { $latestReportFile.FullName } else { "" }
    latest_chatgpt_prompt_path = if ($latestPromptFile) { $latestPromptFile.FullName } else { "" }
    latest_pasteback_path = if ($latestPastebackFile) { $latestPastebackFile.FullName } else { "" }
    needs_codex_report = $needsReport
    needs_chatgpt_prompt = $needsPrompt
    needs_chatgpt_review = $needsReview
    needs_pasteback = $needsPasteback
    pasteback_ready = $pastebackSafe
    pasteback_safety_status = $pastebackStatus
    exact_next_action = $nextAction
    related_existing_notes = @(
        "docs/AI_OS/autonomy/AIOS_CODEX_CHATGPT_POWERSHELL_RELAY_V1.md",
        "docs/AI_OS/autonomy/AIOS_CHATGPT_REVIEWED_PR_LIFECYCLE_BRIDGE_V1.md",
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
