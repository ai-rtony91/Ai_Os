param(
    [Parameter(Mandatory = $true)]
    [string]$WorkflowName,
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$routerMode = 'DRY_RUN'
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
$validWorkflows = @(
    'REPO_HEALTH',
    'DAILY_START',
    'WORK_SESSION',
    'CHECKPOINT_ONLY',
    'DAILY_METRICS_DRAFT',
    'FULL_DRY_RUN_CHAIN'
)
$warnings = New-Object System.Collections.Generic.List[string]
$failures = New-Object System.Collections.Generic.List[string]
$blocked = New-Object System.Collections.Generic.List[string]

function Write-ItemList {
    param(
        [string]$Title,
        [string[]]$Items
    )

    Write-Host "${Title}:"
    foreach ($item in $Items) {
        Write-Host "- $item"
    }
}

function New-HelperSpec {
    param(
        [string]$Path,
        [string[]]$Arguments = @()
    )

    [PSCustomObject]@{
        Path = $Path
        Arguments = $Arguments
    }
}

function Invoke-RouterHelper {
    param(
        [string]$ResolvedRepoRoot,
        [object]$Helper
    )

    $relativePath = $Helper.Path
    $helperPath = Join-Path $ResolvedRepoRoot $relativePath
    Write-Host ''
    Write-Host "Helper path: $relativePath"

    if ($relativePath -notlike '*.DRY_RUN.*') {
        Write-Host 'Helper status: BLOCKED - helper is not marked as DRY_RUN.'
        $script:blocked.Add("$relativePath is not marked as DRY_RUN.") | Out-Null
        return
    }

    if (-not (Test-Path -LiteralPath $helperPath -PathType Leaf)) {
        Write-Host 'Helper status: WARN - missing helper, skipped.'
        $script:warnings.Add("$relativePath missing.") | Out-Null
        return
    }

    Write-Host 'Helper status: PASS - found DRY_RUN helper.'
    Write-Host 'Helper action: CALLING existing DRY_RUN helper.'

    try {
        if ($Helper.Arguments.Count -gt 0) {
            & powershell -NoProfile -ExecutionPolicy Bypass -File $helperPath @($Helper.Arguments)
        }
        else {
            & powershell -NoProfile -ExecutionPolicy Bypass -File $helperPath
        }

        if ($LASTEXITCODE -eq 0) {
            Write-Host 'Helper run result: PASS'
        }
        else {
            Write-Host "Helper run result: WARN - helper exited with code $LASTEXITCODE"
            $script:warnings.Add("$relativePath exited with code $LASTEXITCODE.") | Out-Null
        }
    }
    catch {
        Write-Host 'Helper run result: WARN - helper threw an error.'
        Write-Host $_.Exception.Message
        $script:warnings.Add("$relativePath threw an error.") | Out-Null
    }
}

$selectedWorkflow = $WorkflowName.ToUpperInvariant()

Write-Host 'Task name: AI_OS Stage 10B Workflow Router Dry Run'
Write-Host "Router mode: $routerMode"
Write-Host "Repo root: $RepoRoot"
Write-Host "Selected workflow: $selectedWorkflow"
Write-Host "Current timestamp: $timestamp"
Write-Host ''

$allowedActions = @(
    'Select a named workflow.',
    'Print helper mapping and safety rules.',
    'Verify helper availability.',
    'Call existing DRY_RUN helper scripts only.'
)

$blockedActions = @(
    'No file creation, editing, moving, renaming, or deletion.',
    'No git add, commit, or push.',
    'No app launch or browser opening.',
    'No startup setting or scheduled task change.',
    'No broker, trading, credential, secret, registry, firewall, VPN, BIOS/UEFI, BitLocker, browser policy, or Task Scheduler action.',
    'No Reports\DAILY_METRICS.csv edit.',
    'No Reports\CHECKPOINT_INDEX.md edit.'
)

Write-ItemList -Title 'Allowed actions' -Items $allowedActions
Write-Host ''
Write-ItemList -Title 'Blocked actions' -Items $blockedActions
Write-Host ''
Write-Host 'Approval requirement: Human approval is required before any APPLY, git add, commit, push, app launch, browser open, startup change, report write, or protected file edit.'

if ($validWorkflows -notcontains $selectedWorkflow) {
    Write-Host ''
    Write-Host 'Final summary: FAIL'
    Write-Host "Unknown workflow: $WorkflowName"
    Write-ItemList -Title 'Valid workflow names' -Items $validWorkflows
    Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host ''
    Write-Host 'Final summary: FAIL'
    Write-Host "Repo root does not exist: $RepoRoot"
    Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW ACTIONS APPLIED.' -f [char]0x2014)
    exit 1
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$workflowHelpers = @{
    REPO_HEALTH = @(
        (New-HelperSpec -Path 'automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1')
    )
    DAILY_START = @(
        (New-HelperSpec -Path 'automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1'),
        (New-HelperSpec -Path 'automation\modes\Test-AiOsModeSelection.DRY_RUN.ps1' -Arguments @('-ModeName', 'WORK_MODE')),
        (New-HelperSpec -Path 'automation\sessions\New-AiOsSessionEvidenceLog.DRY_RUN.ps1')
    )
    WORK_SESSION = @(
        (New-HelperSpec -Path 'automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1'),
        (New-HelperSpec -Path 'automation\sessions\New-AiOsSessionEvidenceLog.DRY_RUN.ps1')
    )
    CHECKPOINT_ONLY = @(
        (New-HelperSpec -Path 'automation\checkpoints\New-AiOsCheckpointDraft.DRY_RUN.ps1')
    )
    DAILY_METRICS_DRAFT = @(
        (New-HelperSpec -Path 'automation\reporting\New-AiOsDailyMetricsRow.DRY_RUN.ps1')
    )
    FULL_DRY_RUN_CHAIN = @(
        (New-HelperSpec -Path 'automation\orchestration\Test-AiOsOperationalChain.DRY_RUN.ps1')
    )
}

$helpers = @($workflowHelpers[$selectedWorkflow])
Write-Host ''
Write-Host 'Helper scripts that would be used:'
foreach ($helper in $helpers) {
    $argumentText = if ($helper.Arguments.Count -gt 0) { ' ' + ($helper.Arguments -join ' ') } else { '' }
    Write-Host "- $($helper.Path)$argumentText"
}

Write-Host ''
Write-Host 'Helper scripts found/missing:'
foreach ($helper in $helpers) {
    Invoke-RouterHelper -ResolvedRepoRoot $resolvedRepoRoot -Helper $helper
}

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'Final summary: FAIL'
    $failures | ForEach-Object { Write-Host "- $_" }
}
elseif ($blocked.Count -gt 0) {
    Write-Host 'Final summary: FAIL'
    Write-Host 'Blocked helpers:'
    $blocked | ForEach-Object { Write-Host "- $_" }
}
elseif ($warnings.Count -gt 0) {
    Write-Host 'Final summary: WARN'
    Write-Host 'Warnings:'
    $warnings | ForEach-Object { Write-Host "- $_" }
}
else {
    Write-Host 'Final summary: PASS'
}

Write-Host ('DRY_RUN COMPLETE {0} NO WORKFLOW ACTIONS APPLIED.' -f [char]0x2014)
