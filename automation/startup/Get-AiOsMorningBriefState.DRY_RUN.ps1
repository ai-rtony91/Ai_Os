param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-MorningBriefComponent {
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

Write-Host 'Task name: AI_OS Stage 13A/13B Morning Brief State Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual Morning Brief state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'Morning Brief component checks:'
Test-MorningBriefComponent -Label 'workflow router' -RelativePath 'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1'
Test-MorningBriefComponent -Label 'workflow registry' -RelativePath 'docs\AI_OS\router\AIOS_WORKFLOW_REGISTRY_DRAFT.md'
Test-MorningBriefComponent -Label 'approval queue draft' -RelativePath 'docs\AI_OS\approval\AIOS_APPROVAL_QUEUE_DRAFT.md'
Test-MorningBriefComponent -Label 'dashboard workflow state draft' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_WORKFLOW_STATE_DRAFT.md'
Test-MorningBriefComponent -Label 'dashboard data contract' -RelativePath 'docs\specs\aios-dashboard-data-contracts.md'
Test-MorningBriefComponent -Label 'approval validator' -RelativePath 'automation\status\Test-AiOsApprovalQueueValidator.DRY_RUN.ps1'
Test-MorningBriefComponent -Label 'workflow-state helper' -RelativePath 'automation\status\Get-AiOsWorkflowState.DRY_RUN.ps1'

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
    $briefState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $briefState = 'WARN_REVIEW_REQUIRED'
}
else {
    $briefState = 'READY_FOR_REVIEW'
}

Write-Host "Conceptual Morning Brief state: $briefState"
Write-Host ''
Write-Host 'Conceptual warnings:'
if ($warnings.Count -gt 0) {
    $warnings | ForEach-Object { Write-Host "- $_" }
}
else {
    Write-Host '- NONE'
}
Write-Host ''
Write-Host 'Conceptual pending approvals:'
Write-Host '- APPLY approvals: REQUIRED_BEFORE_APPLY'
Write-Host '- git checkpoint approvals: REQUIRED_BEFORE_GIT_ADD_COMMIT_PUSH'
Write-Host '- protected file approvals: REQUIRED_BEFORE_PROTECTED_FILE_CHANGE'
Write-Host ''
Write-Host 'Conceptual next safe action:'
Write-Host '- continue DRY_RUN review'
Write-Host '- inspect warnings'
Write-Host '- request APPLY approval'
Write-Host '- perform git checkpoint'

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF ACTIONS APPLIED.' -f [char]0x2014)
