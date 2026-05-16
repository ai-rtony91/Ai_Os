param(
    [Parameter(Mandatory = $true)][string]$Phase,
    [Parameter(Mandatory = $true)][string]$Capability,
    [string]$PrNumber = "",
    [string]$OperationalImpact = "",
    [string]$NextTarget = ""
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$utc = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")

$fileName = "$utc-$($Phase.ToLower().Replace(' ','-')).json"
$path = Join-Path "automation/history/milestones" $fileName

$branch = git branch --show-current
$commit = git rev-parse HEAD

$record = [pscustomobject]@{
    utc = $utc
    phase = $Phase
    capability = $Capability
    pr_number = $PrNumber
    branch = $branch
    commit = $commit
    operational_impact = $OperationalImpact
    next_target = $NextTarget
}

$record | ConvertTo-Json -Depth 6 | Set-Content $path -Encoding UTF8

Write-Host "COPY START — New-AiOsMilestone.ps1"
Write-Host "AI_OS Milestone Registry" -ForegroundColor Cyan
Write-Host "Milestone written: $path"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — New-AiOsMilestone.ps1"
