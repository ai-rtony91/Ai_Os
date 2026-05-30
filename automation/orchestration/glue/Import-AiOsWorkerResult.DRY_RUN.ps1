[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [switch]$Apply,
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsUtcTimestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Get-AiOsFileTimestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
}

function Read-AiOsResultText {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Worker result input not found: $Path"
    }
    return Get-Content -LiteralPath $Path -Raw
}

function Get-AiOsResultStatus {
    param([string]$Text)
    $lower = $Text.ToLowerInvariant()
    if ($lower -match "failed|failure|error") { return "FAILED" }
    if ($lower -match "blocked|cannot continue|stop condition") { return "BLOCKED" }
    if ($lower -match "needs approval|approval required|human approval|approve") { return "NEEDS_APPROVAL" }
    if ($lower -match "warn|warning|review required") { return "WARN" }
    if ($lower -match "validation passed|pass|completed") { return "PASS" }
    return "WARN"
}

function Get-AiOsDetectedSignals {
    param([string]$Text)
    $signals = @()
    $checks = [ordered]@{
        no_commit         = "no commit"
        no_push           = "no push"
        no_merge          = "no merge"
        validation_passed = "validation passed"
        git_status        = "git status"
        blocked           = "blocked"
        failed            = "failed"
        pr_url            = "https://github.com/.+/pull/[0-9]+"
        commit_hash       = "\b[0-9a-f]{7,40}\b"
    }
    foreach ($name in $checks.Keys) {
        if ($Text -match $checks[$name]) {
            $signals += $name
        }
    }
    return @($signals | Select-Object -Unique)
}

$text = Read-AiOsResultText -Path $InputPath
$status = Get-AiOsResultStatus -Text $text
$signals = @(Get-AiOsDetectedSignals -Text $text)
$timestamp = Get-AiOsFileTimestamp

$normalized = [ordered]@{
    schema           = "AIOS_OPERATION_GLUE_WORKER_RESULT.v0_1"
    result_id        = "WORKER_RESULT_{0}" -f $timestamp
    source_path      = $InputPath
    imported_at      = Get-AiOsUtcTimestamp
    status           = $status
    detected_signals = $signals
    summary          = (($text -split "\r?\n") | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -First 5) -join " "
    no_commit        = $signals -contains "no_commit"
    no_push          = $signals -contains "no_push"
    no_merge         = $signals -contains "no_merge"
    validation_passed = $signals -contains "validation_passed"
    next_safe_action = if ($status -eq "PASS") {
        "Update the approval inbox and review the next safe action."
    } elseif ($status -eq "NEEDS_APPROVAL") {
        "Route this result to the approval inbox for Human Owner review."
    } else {
        "Review the worker result before assigning follow-up work."
    }
}

$outputPath = "DRY_RUN_NO_FILE_WRITTEN"
if ($Apply) {
    $outDir = "telemetry/operation_glue/worker_results"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $outputPath = Join-Path $outDir ("{0}.json" -f $normalized.result_id)
    $normalized | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outputPath -Encoding UTF8
}

$result = [ordered]@{
    schema           = "AIOS_OPERATION_GLUE_RESULT_INTAKE_REPORT.v0_1"
    mode             = if ($Apply) { "APPLY" } else { "DRY_RUN" }
    input_path       = $InputPath
    output_path      = $outputPath
    wrote_file       = [bool]$Apply
    normalized_result = $normalized
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Operation Glue - Worker Result Intake"
Write-Host ("Mode: {0}" -f $result.mode)
Write-Host ("Input: {0}" -f $InputPath)
Write-Host ("Status: {0}" -f $status)
Write-Host ("Signals: {0}" -f ($signals -join ", "))
Write-Host ("Output: {0}" -f $outputPath)
Write-Host ("Next safe action: {0}" -f $normalized.next_safe_action)
Write-Host "No commit, push, merge, reset, clean, branch deletion, or protected action performed."
Write-Host ""
$result | ConvertTo-Json -Depth 10
