param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
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
    $script:failures.Add("Missing required component: $Label ($RelativePath)") | Out-Null
}

function Test-Category {
    param(
        [string]$Category,
        [string]$Text
    )

    if ($Text -match [regex]::Escape($Category)) {
        Write-Host "[PASS] $Category"
        return
    }

    Write-Host "[FAIL] $Category"
    $script:failures.Add("Missing approval category: $Category") | Out-Null
}

Write-Host 'Task name: AI_OS Stage 12C/12D Approval Queue Validator Dry Run'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, launched, opened, or settings-changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host 'Conceptual queue health: FAIL_BLOCKED'
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    Write-Host "Repo root missing: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO APPROVAL VALIDATION ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$script:ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Host 'Approval component checks:'
Test-Component -Label 'approval queue draft' -RelativePath 'docs\AI_OS\approval\AIOS_APPROVAL_QUEUE_DRAFT.md'
Test-Component -Label 'workflow registry' -RelativePath 'docs\AI_OS\router\AIOS_WORKFLOW_REGISTRY_DRAFT.md'
Test-Component -Label 'workflow router' -RelativePath 'automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1'
Test-Component -Label 'dashboard data contract' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_DATA_CONTRACT_DRAFT.md'
Test-Component -Label 'dashboard workflow state draft' -RelativePath 'docs\AI_OS\dashboard\AIOS_DASHBOARD_WORKFLOW_STATE_DRAFT.md'
Test-Component -Label 'approval-state helper' -RelativePath 'automation\status\Get-AiOsApprovalState.DRY_RUN.ps1'

$approvalQueuePath = Join-Path $script:ResolvedRepoRoot 'docs\AI_OS\approval\AIOS_APPROVAL_QUEUE_DRAFT.md'
$approvalQueueText = ''
if (Test-Path -LiteralPath $approvalQueuePath -PathType Leaf) {
    $approvalQueueText = Get-Content -LiteralPath $approvalQueuePath -Raw
}

Write-Host ''
Write-Host 'Approval-category checks:'
$approvalCategories = @(
    'DRY_RUN_REVIEW',
    'APPLY_PENDING',
    'GIT_CHECKPOINT_PENDING',
    'PROTECTED_FILE_REVIEW',
    'BLOCKED_HIGH_RISK'
)

foreach ($category in $approvalCategories) {
    Test-Category -Category $category -Text $approvalQueueText
}

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
    $queueHealth = 'FAIL_BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $queueHealth = 'WARN_REVIEW_REQUIRED'
}
else {
    $queueHealth = 'HEALTHY'
}

Write-Host "Conceptual queue health: $queueHealth"
Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    Write-Host ('DRY_RUN COMPLETE {0} NO APPROVAL VALIDATION ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'PASS/WARN/FAIL summary: WARN'
    $warnings | ForEach-Object { Write-Host "- $_" }
    Write-Host ('DRY_RUN COMPLETE {0} NO APPROVAL VALIDATION ACTIONS APPLIED.' -f [char]0x2014)
    exit 0
}

Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO APPROVAL VALIDATION ACTIONS APPLIED.' -f [char]0x2014)
