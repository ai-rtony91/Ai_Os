[CmdletBinding()]
param(
    [string]$PacketId,
    [string]$ResumePath,
    [string]$StateDirectory = "automation/orchestration/auto_loop/state",
    [switch]$Latest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) { return [System.IO.Path]::GetFullPath($Path) }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Path))
}

function Test-AiOsPathInside {
    param([string]$Path, [string]$AllowedRoot)
    $fullPath = Get-AiOsFullPath -Path $Path
    $fullRoot = Get-AiOsFullPath -Path $AllowedRoot
    return $fullPath.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)
}

if (-not (Test-AiOsPathInside -Path $StateDirectory -AllowedRoot "automation/orchestration/auto_loop/state")) {
    throw "StateDirectory must stay under automation/orchestration/auto_loop/state."
}

$resumeDir = Join-Path $StateDirectory "resume"
if ($ResumePath) {
    if (-not (Test-AiOsPathInside -Path $ResumePath -AllowedRoot "automation/orchestration/auto_loop/state/resume")) {
        throw "ResumePath must stay under automation/orchestration/auto_loop/state/resume."
    }
    $target = $ResumePath
} elseif ($PacketId) {
    $target = Join-Path $resumeDir "RESUME_$PacketId.json"
} elseif ($Latest) {
    $latestRecord = Get-ChildItem -Path $resumeDir -Filter "RESUME_*.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $latestRecord) { throw "No resume records found." }
    $target = $latestRecord.FullName
} else {
    throw "Provide -ResumePath, -PacketId, or -Latest."
}

if (-not (Test-Path -LiteralPath $target)) {
    throw "Resume record not found: $target"
}

$record = Get-Content -Raw -LiteralPath $target | ConvertFrom-Json
$summary = [ordered]@{
    packet_id = $record.packet_id
    current_step = $record.current_step
    last_completed_step = $record.last_completed_step
    next_required_step = $record.next_required_step
    stop_reason = $record.stop_reason
    report_path = $record.report_path
    codex_resume_prompt = $record.codex_resume_prompt
    next_safe_human_action = $record.human_resume_instruction
    resume_path = $target
    did = @("Read sandbox resume record and printed resume context.")
    did_not = @("Did not mutate active state, queues, inboxes, registries, runtime, telemetry/runtime, stage, commit, push, merge, or rebase.")
}

Write-Output ($summary | ConvertTo-Json -Depth 8)
