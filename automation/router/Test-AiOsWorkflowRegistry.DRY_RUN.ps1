param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
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

function Test-RequiredText {
    param(
        [string]$Label,
        [string]$Text,
        [string]$Expected,
        [string]$MissingLevel
    )

    if ($Text -match [regex]::Escape($Expected)) {
        Write-Host "[PASS] $Label"
        return
    }

    Write-Host "[$MissingLevel] $Label"
    if ($MissingLevel -eq 'FAIL') {
        $script:failures.Add("Missing expected text: $Expected") | Out-Null
    }
    else {
        $script:warnings.Add("Missing expected text: $Expected") | Out-Null
    }
}

Write-Host 'Task name: AI_OS Stage 10E/10F Workflow Registry Dry Run Validator'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Final summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW REGISTRY ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'File checks:'
$requiredFiles = @(
    'docs\AI_OS\router\AIOS_WORKFLOW_REGISTRY_DRAFT.md',
    'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1',
    'docs\AI_OS\operator\AIOS_OPERATOR_COMMAND_MAP_DRAFT.md'
)

foreach ($file in $requiredFiles) {
    Test-FilePresence -RepoRoot $resolvedRepoRoot -RelativePath $file | Out-Null
}

$registryPath = Join-Path $resolvedRepoRoot 'docs\AI_OS\router\AIOS_WORKFLOW_REGISTRY_DRAFT.md'
$routerPath = Join-Path $resolvedRepoRoot 'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1'
$registryText = ''
$routerText = ''

if (Test-Path -LiteralPath $registryPath -PathType Leaf) {
    $registryText = Get-Content -LiteralPath $registryPath -Raw
}

if (Test-Path -LiteralPath $routerPath -PathType Leaf) {
    $routerText = Get-Content -LiteralPath $routerPath -Raw
}

$workflowNames = @(
    'REPO_HEALTH',
    'DAILY_START',
    'WORK_SESSION',
    'CHECKPOINT_ONLY',
    'DAILY_METRICS_DRAFT',
    'FULL_DRY_RUN_CHAIN'
)

Write-Host ''
Write-Host 'Registry workflow checks:'
foreach ($workflowName in $workflowNames) {
    Test-RequiredText -Label $workflowName -Text $registryText -Expected $workflowName -MissingLevel 'FAIL'
}

Write-Host ''
Write-Host 'Router workflow checks:'
foreach ($workflowName in $workflowNames) {
    Test-RequiredText -Label $workflowName -Text $routerText -Expected $workflowName -MissingLevel 'FAIL'
}

Write-Host ''
Write-Host 'Safety-field checks:'
$safetyFields = @(
    'risk level LOW',
    'DRY_RUN',
    'writes files NO',
    'requires human review YES'
)

foreach ($field in $safetyFields) {
    Test-RequiredText -Label $field -Text $registryText -Expected $field -MissingLevel 'WARN'
}

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'Final summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW REGISTRY ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'Final summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW REGISTRY ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'Final summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW REGISTRY ACTIONS APPLIED.' -f [char]0x2014)
