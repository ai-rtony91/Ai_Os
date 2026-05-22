param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-Component {
    param(
        [string]$Label,
        [string]$RelativePath
    )

    $path = Join-Path $script:ResolvedRepoRoot $RelativePath
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        Write-Host "[PASS] $Label`: $RelativePath"
        return
    }

    Write-Host "[FAIL] $Label`: $RelativePath"
    $script:failures.Add("Missing component: $Label ($RelativePath)") | Out-Null
}

Write-Host 'Task name: AI_OS Stage 11A/11B Workflow State Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Suggested dashboard state: FAIL_BLOCKED'
    Write-Host 'Final summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW STATE ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'Workflow component checks:'
Test-Component -Label 'workflow router' -RelativePath 'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1'
Test-Component -Label 'workflow registry' -RelativePath 'docs\AI_OS\router\AIOS_WORKFLOW_REGISTRY_DRAFT.md'
Test-Component -Label 'operator command map' -RelativePath 'docs\AI_OS\operator\AIOS_OPERATOR_COMMAND_MAP_DRAFT.md'
Test-Component -Label 'orchestration framework' -RelativePath 'docs\concepts\aios-dispatcher-orchestration-concepts.md'
Test-Component -Label 'repo health helper' -RelativePath 'automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1'

Write-Host ''
Write-Host 'Git status check:'
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    Write-Host '[WARN] git command unavailable.'
    $warnings.Add('git command unavailable.') | Out-Null
}
else {
    Push-Location -LiteralPath $script:ResolvedRepoRoot
    try {
        $gitStatus = @(& git status --short --branch 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[WARN] git status failed.'
            $gitStatus | ForEach-Object { Write-Host $_ }
            $warnings.Add('git status failed.') | Out-Null
        }
        else {
            $gitStatus | ForEach-Object { Write-Host $_ }
            if ($gitStatus.Count -gt 1) {
                Write-Host '[WARN] git status is not clean.'
                $warnings.Add('git status is not clean.') | Out-Null
            }
            else {
                Write-Host '[PASS] git status has no listed changes.'
            }
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host ''
if ($failures.Count -gt 0) {
    $suggestedState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $suggestedState = 'WARN_REVIEW_REQUIRED'
}
else {
    $suggestedState = 'DRY_RUN_READY'
}

Write-Host "Suggested dashboard state: $suggestedState"
Write-Host ''
Write-Host 'Conceptual dashboard panels:'
Write-Host '- Repo Health'
Write-Host '- Workflow Router'
Write-Host '- Session Evidence'
Write-Host '- Checkpoint Drafts'
Write-Host '- Daily Metrics Drafts'
Write-Host '- Approval Queue'

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW STATE ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW STATE ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW STATE ACTIONS APPLIED.' -f [char]0x2014)
