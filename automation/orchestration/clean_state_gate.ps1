[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Write-Result {
    param(
        [string]$Name,
        [string]$Value
    )

    Write-Host ("{0}: {1}" -f $Name, $Value)
}

$repoPath = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $repoPath

$branch = git branch --show-current
if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "UNKNOWN"
}

$statusLines = @(git status --short)
$packetQueueExists = Test-Path (Join-Path $repoPath "automation\orchestration\packet_queue.example.json")
$assignmentLocksExist = Test-Path (Join-Path $repoPath "automation\orchestration\assignment_locks.example.json")

$blocked = $false
$blockReasons = New-Object System.Collections.Generic.List[string]

if ($statusLines.Count -gt 0) {
    $blocked = $true
    $blockReasons.Add("git working tree is not clean")
}

if (-not $packetQueueExists) {
    $blocked = $true
    $blockReasons.Add("packet queue example is missing")
}

if (-not $assignmentLocksExist) {
    $blocked = $true
    $blockReasons.Add("assignment locks example is missing")
}

Write-Host "AI_OS Clean State Gate"
Write-Host "Mode: DRY_RUN"
Write-Host ""
Write-Result "Repo path" $repoPath
Write-Result "Current branch" $branch
Write-Result "Git status entries" $statusLines.Count
Write-Result "Packet queue exists" $packetQueueExists
Write-Result "Assignment locks exist" $assignmentLocksExist

if ($blocked) {
    Write-Result "Gate result" "BLOCKED"
    Write-Host "Block reasons:"
    foreach ($reason in $blockReasons) {
        Write-Host ("- {0}" -f $reason)
    }
}
else {
    Write-Result "Gate result" "ALLOWED"
}

Write-Host ""
Write-Host "No files were changed. No locks were created. No workers were launched. No commit or push was performed."
