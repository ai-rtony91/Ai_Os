<#
AI-OS Morning Workflow
Phase: BUILD
Mode: DRY_RUN
Author: AI_OS
Purpose:
- Detect open windows
- Generate morning brief
- Launch approved workday apps
- Prevent unscheduled startup clutter
#>

param(
    [switch]$DryRun = $true
)

$WorkflowStart = Get-Date

Write-Host ""
Write-Host "====================================="
Write-Host " AI-OS Morning Workflow Starting"
Write-Host "====================================="
Write-Host ""

Write-Host "Mode: DRY_RUN"
Write-Host "Session Start: $WorkflowStart"
Write-Host ""

# [S1] Fixed Morning Work Profile
$MorningProfile = [ordered]@{
    ProfileName = "AI_OS Morning Launch"
    WorkMode = "BUILD"
    RequiredApps = @(
        "Firefox",
        "Code",
        "PowerShell",
        "ChatGPT",
        "ProtonVPN.Client"
    )
    RequiredWebsites = @(
        "https://github.com/ai-rtony91/Ai_Os",
        "https://chatgpt.com",
        "https://chat.openai.com"
    )
    RequiredSecurityState = @(
        "ProtonVPN.Client running",
        "Bitwarden available",
        "Windows Security running"
    )
    TodayObjective = "Continue AI_OS feature development from the current repo state."
    NextSteps = @(
        "Run Morning Workflow in DRY_RUN mode.",
        "Verify required tools are detected.",
        "Generate Morning Brief report.",
        "Only enable APPLY mode after DRY_RUN passes."
    )

}

$ApprovedApps = $MorningProfile.RequiredApps
# [S2] Detect running processes
$RunningProcesses = Get-Process | Sort-Object ProcessName

Write-Host "Detected Processes:"
Write-Host ""

$RunningProcesses |
    Select-Object ProcessName, Id |
    Format-Table -AutoSize

    # [S3] Classification groups
$SystemProcesses = @(
    "svchost",
    "RuntimeBroker",
    "dllhost",
    "conhost",
    "csrss",
    "winlogon",
    "services",
    "System"
)

$AiProcesses = @(
    "ChatGPT",
    "claude",
    "codex",
    "Code",
    "node"
)

$GamingProcesses = @(
    "EADesktop",
    "EABackgroundService",
    "EACefSubProcess",
    "PnkBstrA",
    "PnkBstrB"
)

$SecurityProcesses = @(
    "ProtonVPN.Client",
    "ProtonVPNService",
    "Bitwarden",
    "SecurityHealthService"
)

Write-Host ""
Write-Host "====================================="
Write-Host " AI-OS Classification Engine"
Write-Host "====================================="
Write-Host ""

foreach ($Process in $RunningProcesses) {

    $Name = $Process.ProcessName

    if ($SystemProcesses -contains $Name) {
        Write-Host "[SYSTEM] $Name"
    }
    elseif ($AiProcesses -contains $Name) {
        Write-Host "[AI] $Name"
    }
    elseif ($GamingProcesses -contains $Name) {
        Write-Host "[GAMING] $Name"
    }
    elseif ($SecurityProcesses -contains $Name) {
        Write-Host "[SECURITY] $Name"
    }
    elseif ($ApprovedApps -contains $Name) {
        Write-Host "[APPROVED] $Name"
    }
}
# [S4] Morning Brief report generation

$ReportDate = Get-Date -Format "yyyy-MM-dd"

$ReportDirectory = ".\Reports\daily"

if (!(Test-Path $ReportDirectory)) {
    New-Item -ItemType Directory -Path $ReportDirectory | Out-Null
}

$MorningBriefPath = "$ReportDirectory\MORNING_BRIEF_$ReportDate.md"

$MorningBrief = @"
# AI-OS Morning Brief

## Profile
$($MorningProfile.ProfileName)

## Work Mode
$($MorningProfile.WorkMode)

## Objective
$($MorningProfile.TodayObjective)

## Required Applications
$($MorningProfile.RequiredApps -join "`n")

## Required Websites
$($MorningProfile.RequiredWebsites -join "`n")

## Security Requirements
$($MorningProfile.RequiredSecurityState -join "`n")

## Next Steps
$($MorningProfile.NextSteps -join "`n")

## Session Start
$WorkflowStart

## DRY_RUN Status
Enabled

## Startup Health
Pending until validation section completes.

"@

Set-Content -Path $MorningBriefPath -Value $MorningBrief

Write-Host ""
Write-Host "Morning Brief Generated:"
Write-Host $MorningBriefPath

# [S5] Required Tool Validation Engine

Write-Host ""
Write-Host "====================================="
Write-Host " AI-OS Required Tool Validation"
Write-Host "====================================="
Write-Host ""

$RunningProcessNames = $RunningProcesses.ProcessName | Sort-Object -Unique

foreach ($RequiredApp in $MorningProfile.RequiredApps) {
    if ($RunningProcessNames -contains $RequiredApp) {
        Write-Host "[PASS] $RequiredApp is running"
    }
    else {
        Write-Host "[WARNING] $RequiredApp is missing"
    }
}

if ($RunningProcessNames -contains "EADesktop" -or $RunningProcessNames -contains "EABackgroundService") {
    Write-Host "[WARNING] EA gaming stack detected during AI_OS morning workflow"
}
else {
    Write-Host "[PASS] No EA gaming stack detected"
}

# [S6] Startup Health Summary

Write-Host ""
Write-Host "====================================="
Write-Host " AI-OS Startup Health Summary"
Write-Host "====================================="
Write-Host ""

$MissingRequiredApps = @()

foreach ($RequiredApp in $MorningProfile.RequiredApps) {
    if ($RunningProcessNames -notcontains $RequiredApp) {
        $MissingRequiredApps += $RequiredApp
    }
}

$GamingStackDetected = (
    $RunningProcessNames -contains "EADesktop" -or
    $RunningProcessNames -contains "EABackgroundService"
)

if ($MissingRequiredApps.Count -eq 0 -and -not $GamingStackDetected) {
    $StartupHealth = "PASS"
}
elseif ($MissingRequiredApps.Count -eq 0 -and $GamingStackDetected) {
    $StartupHealth = "WARNING"
}
else {
    $StartupHealth = "FAIL"
}

Write-Host "Startup Health: $StartupHealth"

if ($MissingRequiredApps.Count -gt 0) {
    Write-Host "Missing Required Apps:"
    foreach ($MissingApp in $MissingRequiredApps) {
        Write-Host "- $MissingApp"
    }
}

if ($GamingStackDetected) {
    Write-Host "Warning:"
    Write-Host "- EA gaming stack detected during AI_OS morning workflow"
}

# [S7] Append Startup Health to Morning Brief

Add-Content -Path $MorningBriefPath -Value ""
Add-Content -Path $MorningBriefPath -Value "## Final Startup Health"
Add-Content -Path $MorningBriefPath -Value $StartupHealth

if ($GamingStackDetected) {
    Add-Content -Path $MorningBriefPath -Value ""
    Add-Content -Path $MorningBriefPath -Value "## Startup Warnings"
    Add-Content -Path $MorningBriefPath -Value "- EA gaming stack detected during AI_OS morning workflow"
}

if ($MissingRequiredApps.Count -gt 0) {
    Add-Content -Path $MorningBriefPath -Value ""
    Add-Content -Path $MorningBriefPath -Value "## Missing Required Apps"
    foreach ($MissingApp in $MissingRequiredApps) {
        Add-Content -Path $MorningBriefPath -Value "- $MissingApp"
    }
}

Write-Host ""
Write-Host "Startup Health appended to Morning Brief."