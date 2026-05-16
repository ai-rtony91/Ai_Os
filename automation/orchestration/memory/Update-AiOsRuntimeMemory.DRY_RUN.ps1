param(
    [string]$Action = "read",
    [string]$Note = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$memoryPath = "automation/orchestration/memory/AIOS_RUNTIME_MEMORY.json"

if (-not (Test-Path $memoryPath)) {
    @{
        created_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        updated_utc = ""
        last_action = ""
        last_note = ""
        history = @()
    } | ConvertTo-Json -Depth 6 | Set-Content $memoryPath -Encoding UTF8
}

$memory = Get-Content -Raw $memoryPath | ConvertFrom-Json

Write-Host "COPY START - Update-AiOsRuntimeMemory.DRY_RUN.ps1"
Write-Host "AI_OS Runtime Memory" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

if ($Action -eq "write") {
    $utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

    Write-Host "Writing memory note:"
    Write-Host $Note

    if ($Apply) {
        $entry = [pscustomobject]@{
            utc = $utc
            note = $Note
        }

        $memory.updated_utc = $utc
        $memory.last_action = "write"
        $memory.last_note = $Note
        $memory.history = @($memory.history) + $entry

        $memory | ConvertTo-Json -Depth 8 | Set-Content $memoryPath -Encoding UTF8
        Write-Host "Memory updated: YES"
    } else {
        Write-Host "Memory updated: NO"
    }
} else {
    Write-Host "Last action: $($memory.last_action)"
    Write-Host "Last note: $($memory.last_note)"
    Write-Host "History count: $(@($memory.history).Count)"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Update-AiOsRuntimeMemory.DRY_RUN.ps1"
