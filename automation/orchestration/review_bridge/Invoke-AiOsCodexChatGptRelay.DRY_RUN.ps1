param(
    [switch]$Latest,
    [string]$PacketId = "",
    [ValidateSet("DRY_RUN", "APPLY")][string]$Mode = "DRY_RUN",
    [switch]$OutputJson,
    [switch]$AsPromptBlock,
    [switch]$ShowNextAction
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-LatestReport {
    param(
        [Parameter(Mandatory = $true)][string]$Directory,
        [string]$PacketIdFilter
    )

    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) {
        return $null
    }

    $items = Get-ChildItem -LiteralPath $Directory -Filter "*.json" -File |
        Sort-Object -Property LastWriteTime -Descending

    if (-not $PacketIdFilter) {
        return ($items | Select-Object -First 1)
    }

    foreach ($item in $items) {
        try {
            $obj = Get-Content -LiteralPath $item.FullName -Raw | ConvertFrom-Json -ErrorAction Stop
            if ($obj.packet_id -eq $PacketIdFilter) {
                return $item
            }
        }
        catch {
            continue
        }
    }

    return $null
}

function Build-PromptText {
    param([pscustomobject]$Report)
    $parts = @(
        "ChatGPT must review this Codex report and return one PowerShell block only.",
        "",
        "Packet ID: $($Report.packet_id)",
        "Branch: $($Report.branch)",
        "Changed files: $($Report.files_changed -join ', ')",
        "Tests run: $($Report.tests_run)",
        "Blocked tests: $($Report.tests_blocked -join ', ')",
        "Validation claims: $($Report.validation_claims -join '; ')",
        "Safety claims: $($Report.safety_claims -join '; ')",
        "Requested next action: $($Report.requested_next_action)"
    )
    return ($parts -join "`n")
}

$repoRoot = (Get-Location).Path
$reportsDir = Join-Path $repoRoot "control/review_bridge/codex_reports"
$promptsDir = Join-Path $repoRoot "control/review_bridge/chatgpt_prompts"
$pastebackDir = Join-Path $repoRoot "control/review_bridge/pasteback"

$mode = if ($Mode -eq "APPLY") { "APPLY" } else { "DRY_RUN" }
$isApply = ($mode -eq "APPLY")

$reportFilter = ""
if ($PacketId) {
    $reportFilter = $PacketId
} elseif ($Latest) {
    $reportFilter = ""
} else {
    $reportFilter = ""
}

$reportFile = Get-LatestReport -Directory $reportsDir -PacketIdFilter $reportFilter
if (-not $reportFile) {
    $blockedOutput = [ordered]@{
        schema = "AIOS_CODEX_CHATGPT_RELAY_PROMPT.v1"
        mode = "DRY_RUN_READ_ONLY"
        wrote_prompt_file = $false
        packet_id = $PacketId
        branch = ""
        relay_report_file = ""
        prompt_text = ""
        requested_chatgpt_review = "ChatGPT must review this Codex report and return one PowerShell block only."
        exact_next_safe_action = "Save a Codex report item first using New-AiOsCodexReportRelayItem.DRY_RUN.ps1."
        blocked = $true
        reason = "No matching Codex report relay item found."
        blocked_actions = @("No report item found.")
    }
    if ($OutputJson) {
        $blockedOutput | ConvertTo-Json -Depth 20
        exit 0
    }
    Write-Output ($blockedOutput | ConvertTo-Json -Depth 20)
    exit 0
}

$report = Get-Content -LiteralPath $reportFile.FullName -Raw | ConvertFrom-Json
$prompt = Build-PromptText -Report $report

$latestPasteback = $null
if (Test-Path -LiteralPath $pastebackDir -PathType Container) {
    $latestPasteback = Get-ChildItem -LiteralPath $pastebackDir -Filter "*.json" -File |
        Sort-Object -Property LastWriteTime -Descending |
        Select-Object -First 1
}

$nextAction = [ordered]@{
    reviewed_command_file = ""
    branch = $report.branch
    packet_id = $report.packet_id
    pasteback_passed_safety_scan = $false
    exact_next_command = ""
}
if ($latestPasteback) {
    $nextAction.reviewed_command_file = $latestPasteback.FullName
    $nextAction.pasteback_passed_safety_scan = $true
    $nextAction.exact_next_command = "powershell -NoProfile -ExecutionPolicy Bypass -File " + $latestPasteback.FullName
}

$outputObj = [ordered]@{
    schema = "AIOS_CODEX_CHATGPT_RELAY_PROMPT.v1"
    mode = if ($Mode -eq "APPLY") { "APPLY" } else { "DRY_RUN_READ_ONLY" }
    wrote_prompt_file = $false
    packet_id = $report.packet_id
    branch = $report.branch
    relay_report_file = $reportFile.FullName
    prompt_text = $prompt
    requested_chatgpt_review = "ChatGPT must review this Codex report and return one PowerShell block only."
    exact_next_safe_action = "Paste reviewed command in PowerShell only after Anthony approval."
    blocked_actions = @("No runtime mutation", "No force push", "No git add .", "No direct secrets")
}

if ($isApply) {
    if (-not (Test-Path -LiteralPath $promptsDir -PathType Container)) {
        New-Item -ItemType Directory -Path $promptsDir -Force | Out-Null
    }
    $promptFileName = "prompt_{0}_{1}.txt" -f ($report.packet_id -replace "[^A-Za-z0-9._-]", "_"), (Get-Date).ToString("yyyy-MM-ddTHH-mm-ssZ")
    $promptFile = Join-Path $promptsDir $promptFileName
    $promptPayload = '```powershell' + "`n" + $prompt.Trim() + "`n" + '```'
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($promptFile, $promptPayload, $utf8NoBOM)
    $outputObj.wrote_prompt_file = $true
    $outputObj.prompt_file = $promptFile
}

if ($AsPromptBlock) {
    Write-Output '```powershell'
    Write-Output $prompt.Trim()
    Write-Output '```'
    exit 0
}

if ($ShowNextAction) {
    $outputObj.next_action = $nextAction
} else {
    $outputObj.next_action = $null
}

if ($OutputJson) {
    $outputObj | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($outputObj | ConvertTo-Json -Depth 20)
