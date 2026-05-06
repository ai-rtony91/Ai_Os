param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$scriptMode = 'DRY_RUN'
$helperResults = New-Object System.Collections.Generic.List[string]

function Invoke-DryRunHelper {
    param(
        [string]$RepoRoot,
        [string]$RelativePath
    )

    $helperPath = Join-Path $RepoRoot $RelativePath
    Write-Host ''
    Write-Host "Helper path: $RelativePath"

    if (-not (Test-Path -LiteralPath $helperPath -PathType Leaf)) {
        Write-Host 'Helper status: WARN - missing helper, skipped.'
        $script:helperResults.Add("WARN: $RelativePath missing") | Out-Null
        return
    }

    Write-Host 'Helper status: RUNNING'
    try {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $helperPath
        if ($LASTEXITCODE -eq 0) {
            Write-Host 'Helper status: PASS'
            $script:helperResults.Add("PASS: $RelativePath") | Out-Null
        }
        else {
            Write-Host "Helper status: WARN - helper exited with code $LASTEXITCODE"
            $script:helperResults.Add("WARN: $RelativePath exited with code $LASTEXITCODE") | Out-Null
        }
    }
    catch {
        Write-Host 'Helper status: WARN - helper threw an error.'
        Write-Host $_.Exception.Message
        $script:helperResults.Add("WARN: $RelativePath error") | Out-Null
    }
}

Write-Host 'Chain start: AI_OS Stage 10A Operational Chain Dry Run'
Write-Host "Mode: $scriptMode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, or launched.'

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host ''
    Write-Host 'Chain summary: FAIL'
    Write-Host "Reason: repo root does not exist: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO OPERATIONAL CHAIN ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$helpers = @(
    'automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1',
    'automation\sessions\New-AiOsSessionEvidenceLog.DRY_RUN.ps1',
    'automation\checkpoints\New-AiOsCheckpointDraft.DRY_RUN.ps1',
    'automation\reporting\New-AiOsDailyMetricsRow.DRY_RUN.ps1'
)

foreach ($helper in $helpers) {
    Invoke-DryRunHelper -RepoRoot $resolvedRepoRoot -RelativePath $helper
}

Write-Host ''
Write-Host 'Chain summary:'
$helperResults | ForEach-Object { Write-Host "- $_" }

if ($helperResults | Where-Object { $_ -like 'WARN:*' }) {
    Write-Host 'Final summary: WARN'
}
else {
    Write-Host 'Final summary: PASS'
}

Write-Host ('DRY_RUN COMPLETE {0} NO OPERATIONAL CHAIN ACTIONS APPLIED.' -f [char]0x2014)
