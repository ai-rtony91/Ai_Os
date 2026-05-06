param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-FilePresence {
    param(
        [string]$RepoRoot,
        [string]$RelativePath
    )

    $path = Join-Path $RepoRoot $RelativePath
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        Write-Host "[PASS] $RelativePath"
        return $true
    }

    Write-Host "[FAIL] $RelativePath"
    $script:failures.Add("Missing file: $RelativePath") | Out-Null
    return $false
}

function Test-TextPresence {
    param(
        [string]$Label,
        [string]$Text,
        [string]$Pattern,
        [string]$MissingLevel
    )

    if ($Text -match [regex]::Escape($Pattern)) {
        Write-Host "[PASS] $Label"
        return
    }

    Write-Host "[$MissingLevel] $Label"
    if ($MissingLevel -eq 'FAIL') {
        $script:failures.Add("Missing expected text: $Pattern") | Out-Null
    }
    else {
        $script:warnings.Add("Missing expected text: $Pattern") | Out-Null
    }
}

Write-Host 'Task name: AI_OS Stage 10C/10D Router Command Map Dry Run Test'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Final summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO ROUTER COMMAND MAP ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File presence checks:'
$requiredFiles = @(
    'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1',
    'docs\AI_OS\router\AIOS_WORKFLOW_ROUTER_DRAFT.md',
    'docs\AI_OS\router\AIOS_WORKFLOW_ROUTER_RUNBOOK_DRAFT.md',
    'docs\AI_OS\operator\AIOS_OPERATOR_COMMAND_MAP_DRAFT.md'
)

foreach ($file in $requiredFiles) {
    Test-FilePresence -RepoRoot $resolvedRepoRoot -RelativePath $file | Out-Null
}

$routerScriptPath = Join-Path $resolvedRepoRoot 'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1'
$operatorMapPath = Join-Path $resolvedRepoRoot 'docs\AI_OS\operator\AIOS_OPERATOR_COMMAND_MAP_DRAFT.md'
$routerText = ''
$operatorText = ''

if (Test-Path -LiteralPath $routerScriptPath -PathType Leaf) {
    $routerText = Get-Content -LiteralPath $routerScriptPath -Raw
}

if (Test-Path -LiteralPath $operatorMapPath -PathType Leaf) {
    $operatorText = Get-Content -LiteralPath $operatorMapPath -Raw
}

Write-Host ''
Write-Host 'Workflow name checks:'
$workflowNames = @(
    'REPO_HEALTH',
    'DAILY_START',
    'WORK_SESSION',
    'CHECKPOINT_ONLY',
    'DAILY_METRICS_DRAFT',
    'FULL_DRY_RUN_CHAIN'
)

foreach ($workflowName in $workflowNames) {
    Test-TextPresence -Label $workflowName -Text $routerText -Pattern $workflowName -MissingLevel 'FAIL'
}

Write-Host ''
Write-Host 'Operator phrase checks:'
$operatorPhrases = @(
    'check repo health',
    'start daily work',
    'log work session',
    'draft checkpoint',
    'draft daily metrics',
    'run full dry chain',
    'bad mode safety test'
)

foreach ($phrase in $operatorPhrases) {
    Test-TextPresence -Label $phrase -Text $operatorText -Pattern $phrase -MissingLevel 'WARN'
}

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'Final summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO ROUTER COMMAND MAP ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'Final summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO ROUTER COMMAND MAP ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'Final summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO ROUTER COMMAND MAP ACTIONS APPLIED.' -f [char]0x2014)
