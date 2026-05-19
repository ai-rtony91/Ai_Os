param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Test-ApprovalComponent {
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

Write-Host 'Task name: AI_OS Stage 12A/12B Approval State Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual approval queue state: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO APPROVAL QUEUE ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'Approval component checks:'
Test-ApprovalComponent -Label 'workflow registry' -RelativePath 'docs\AI_OS\router\AIOS_WORKFLOW_REGISTRY_DRAFT.md'
Test-ApprovalComponent -Label 'workflow router' -RelativePath 'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1'
Test-ApprovalComponent -Label 'dashboard workflow state draft' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_WORKFLOW_STATE_DRAFT.md'
Test-ApprovalComponent -Label 'approval queue draft' -RelativePath 'docs\AI_OS\approval\AIOS_APPROVAL_QUEUE_DRAFT.md'
Test-ApprovalComponent -Label 'dashboard data contract' -RelativePath 'docs\specs\aios-dashboard-data-contracts.md'

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
    $queueState = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $queueState = 'WARN_REVIEW_REQUIRED'
}
else {
    $queueState = 'DRY_RUN_READY'
}

Write-Host "Conceptual approval queue state: $queueState"
Write-Host ''
Write-Host 'Conceptual pending approvals:'
Write-Host '- APPLY approvals: REVIEW_REQUIRED_BEFORE_APPLY'
Write-Host '- git checkpoint approvals: REVIEW_REQUIRED_BEFORE_GIT_ADD_COMMIT_PUSH'
Write-Host '- protected file approvals: REVIEW_REQUIRED_BEFORE_PROTECTED_FILE_CHANGE'
Write-Host ''
Write-Host 'Risk escalation summary:'
Write-Host '- LOW: read-only DRY_RUN console-output.'
Write-Host '- MEDIUM: creates approved files but no git commit.'
Write-Host '- HIGH: requires explicit human review.'
Write-Host '- BLOCKED: no action until explicit human review.'

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO APPROVAL QUEUE ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO APPROVAL QUEUE ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO APPROVAL QUEUE ACTIONS APPLIED.' -f [char]0x2014)
