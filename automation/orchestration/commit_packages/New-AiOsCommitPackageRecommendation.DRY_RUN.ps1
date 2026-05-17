[CmdletBinding()]
param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsChangedPath {
    param([string]$StatusLine)

    if ([string]::IsNullOrWhiteSpace($StatusLine) -or $StatusLine.Length -lt 4) {
        return $null
    }

    $path = $StatusLine.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

function Test-AiOsRuntimePath {
    param([string]$Path)

    $runtimePatterns = @(
        "automation/intake/AIOS_GOAL_INTAKE.json",
        "automation/outbox/AIOS_NEXT_ACTION.json",
        "automation/runtime/state/AIOS_RUNTIME_STATE.json",
        "proof/last_verified.txt",
        "automation/orchestration/work_packets/active/*.json",
        "automation/orchestration/work_packets/blocked/*.json",
        "automation/orchestration/work_packets/complete/*.json",
        "Reports/dispatcher/runtime/*.json",
        "Reports/dispatcher/runtime/**/*.json",
        "Reports/work_intelligence/daily/DAILY_WORK_INTELLIGENCE_SNAPSHOT_*.json",
        "Reports/work_intelligence/briefings/OPERATOR_VOICE_BRIEFING_*.md",
        "Reports/trading_lab/*.log"
    )

    foreach ($pattern in $runtimePatterns) {
        if ($Path -like $pattern) { return $true }
    }

    return $false
}

function Test-AiOsRiskyPath {
    param([string]$Path)

    $riskyPatterns = @(
        "README.md",
        "RISK_POLICY.md",
        "SOURCE_LOG.md",
        "ERROR_LOG.md",
        "HALLUCINATION_LOG.md",
        "AAR.md",
        "DAILY_REPORT.md",
        "ARCHITECTURE.md",
        "DEPLOYMENT.md",
        "WHITEPAPER.md",
        "AGENTS.md",
        "apps/dashboard/*",
        "apps/dashboard/assets/*",
        "apps/trading_lab/*",
        "aios/modules/trader/*",
        "automation/trading_lab/*",
        "automation/trader/*",
        "Reports/security/*",
        ".env",
        ".env.*",
        "*.pem",
        "*.key",
        "*.pfx",
        "*.p12",
        "*.crt"
    )

    foreach ($pattern in $riskyPatterns) {
        if ($Path -like $pattern) { return $true }
    }

    return $false
}

function Test-AiOsSourcePath {
    param([string]$Path)

    if (Test-AiOsRuntimePath -Path $Path) { return $false }
    if (Test-AiOsRiskyPath -Path $Path) { return $false }

    $sourcePatterns = @(
        ".gitignore",
        "aios.ps1",
        "automation/**/*.ps1",
        "automation/**/*.md",
        "automation/**/*.example.json",
        "automation/**/templates/*.json",
        "automation/**/templates/*.md",
        "automation/**/examples/*.json",
        "docs/**/*.md",
        "validation/**/*.ps1",
        "scripts/**/*.ps1"
    )

    foreach ($pattern in $sourcePatterns) {
        if ($Path -like $pattern) { return $true }
    }

    return $false
}

$statusLines = @(git status --short)
if ($LASTEXITCODE -ne 0) {
    throw "git status --short failed."
}

$changedFiles = @(
    foreach ($line in $statusLines) {
        $path = Get-AiOsChangedPath -StatusLine $line
        if ($null -ne $path) { $path }
    }
)

$approvedSourceFiles = @($changedFiles | Where-Object { Test-AiOsSourcePath -Path $_ } | Sort-Object -Unique)
$ignoredRuntimeFiles = @($changedFiles | Where-Object { Test-AiOsRuntimePath -Path $_ } | Sort-Object -Unique)
$riskyFiles = @($changedFiles | Where-Object { Test-AiOsRiskyPath -Path $_ -or ((-not (Test-AiOsSourcePath -Path $_)) -and (-not (Test-AiOsRuntimePath -Path $_))) } | Sort-Object -Unique)

$suggestedGitAddCommands = @(
    foreach ($file in $approvedSourceFiles) {
        "git add -- `"$file`""
    }
)

$suggestedCommitMessage = "Update AIOS operator loop tooling"
if ($approvedSourceFiles.Count -eq 1 -and $approvedSourceFiles[0] -eq ".gitignore") {
    $suggestedCommitMessage = "Add AIOS runtime artifact ignore rules"
}
elseif ($approvedSourceFiles | Where-Object { $_ -like "automation/orchestration/commit_packages/*" -or $_ -like "automation/orchestration/validators/*" -or $_ -eq "aios.ps1" }) {
    $suggestedCommitMessage = "Add AIOS operator loop guidance tools"
}

$result = [ordered]@{
    schema = "aios_commit_package_recommendation.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    approved_source_files = $approvedSourceFiles
    ignored_runtime_files = $ignoredRuntimeFiles
    risky_files = $riskyFiles
    suggested_git_add_commands = $suggestedGitAddCommands
    suggested_commit_message = $suggestedCommitMessage
    push_reminder = "Do not push until commit validation is clean and the operator explicitly approves push."
    blocked_actions = @("git_add_dot", "git_add_all", "commit_without_review", "push_without_approval")
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AIOS Commit Package Recommendation"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "approved_source_files:"
if ($approvedSourceFiles.Count -eq 0) { Write-Host "- none" } else { $approvedSourceFiles | ForEach-Object { Write-Host "- $_" } }
Write-Host ""
Write-Host "ignored_runtime_files:"
if ($ignoredRuntimeFiles.Count -eq 0) { Write-Host "- none" } else { $ignoredRuntimeFiles | ForEach-Object { Write-Host "- $_" } }
Write-Host ""
Write-Host "risky_files:"
if ($riskyFiles.Count -eq 0) { Write-Host "- none" } else { $riskyFiles | ForEach-Object { Write-Host "- $_" } }
Write-Host ""
Write-Host "suggested_git_add_commands:"
if ($suggestedGitAddCommands.Count -eq 0) { Write-Host "- none" } else { $suggestedGitAddCommands | ForEach-Object { Write-Host $_ } }
Write-Host ""
Write-Host "suggested_commit_message:"
Write-Host $suggestedCommitMessage
Write-Host ""
Write-Host "push_reminder:"
Write-Host $result.push_reminder
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
