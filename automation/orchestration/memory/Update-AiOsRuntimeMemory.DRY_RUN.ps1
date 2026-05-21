param(
    [string]$Action = "read",
    [string]$Note = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$memoryPath = "automation/orchestration/memory/AIOS_RUNTIME_MEMORY.json"
$memoryExists = Test-Path $memoryPath
$memory = $null

if ($memoryExists) {
    $memory = Get-Content -Raw $memoryPath | ConvertFrom-Json
}

Write-Host "COPY START - Update-AiOsRuntimeMemory.DRY_RUN.ps1"
Write-Host "AI_OS Runtime Memory" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Apply requested: $(if ($Apply) { 'YES - SKIPPED' } else { 'NO' })"
Write-Host "Memory path: $memoryPath"
Write-Host "Memory exists: $(if ($memoryExists) { 'YES' } else { 'NO' })"

if (-not $memoryExists) {
    Write-Host "SKIPPED: Runtime memory creation is not allowed in DRY_RUN."
}

if ($Action -eq "write") {
    $utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

    Write-Host "Requested memory note:"
    Write-Host $Note
    Write-Host "Requested UTC: $utc"
    Write-Host "SKIPPED: Runtime memory update is not allowed in DRY_RUN."
    Write-Host "Memory updated: NO"
} else {
    if ($memoryExists) {
        Write-Host "Last action: $($memory.last_action)"
        Write-Host "Last note: $($memory.last_note)"
        Write-Host "History count: $(@($memory.history).Count)"
    } else {
        Write-Host "Last action: UNKNOWN"
        Write-Host "Last note: UNKNOWN"
        Write-Host "History count: UNKNOWN"
    }
}

Write-Host "Files changed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Next safe action: Request APPLY approval before any runtime memory mutation."
Write-Host "COPY END - Update-AiOsRuntimeMemory.DRY_RUN.ps1"
