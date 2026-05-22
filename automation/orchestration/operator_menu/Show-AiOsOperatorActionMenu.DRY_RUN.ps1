[CmdletBinding()]
param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$menuActions = @(
    [ordered]@{
        number = 1
        action_name = "Run operator session bootstrap"
        command_to_copy = "powershell -ExecutionPolicy Bypass -File automation/orchestration/session/Start-AiOsOperatorSession.DRY_RUN.ps1"
        safety_level = "READ_ONLY"
        approval_required = "NO"
        reason = "Runs the current session startup guidance bundle without staging, committing, pushing, or editing files."
    },
    [ordered]@{
        number = 2
        action_name = "Run operator queue runner"
        command_to_copy = "powershell -ExecutionPolicy Bypass -File automation/orchestration/queue_runner/Invoke-AiOsOperatorQueueRunner.DRY_RUN.ps1"
        safety_level = "READ_ONLY"
        approval_required = "NO"
        reason = "Shows the active packet, next command, handoff, validator, commit package, approval, and lock summaries."
    },
    [ordered]@{
        number = 3
        action_name = "Run Codex handoff generator"
        command_to_copy = "powershell -ExecutionPolicy Bypass -File automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1"
        safety_level = "READ_ONLY"
        approval_required = "NO"
        reason = "Creates ready-to-paste Codex and PowerShell text for the next operator handoff."
    },
    [ordered]@{
        number = 4
        action_name = "Run validator recommendation"
        command_to_copy = "powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1"
        safety_level = "READ_ONLY"
        approval_required = "NO"
        reason = "Recommends the validation command based on changed files without running APPLY work."
    },
    [ordered]@{
        number = 5
        action_name = "Run commit package recommendation"
        command_to_copy = "powershell -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"
        safety_level = "READ_ONLY"
        approval_required = "NO"
        reason = "Separates source files from runtime/generated files and prints exact staging suggestions only."
    },
    [ordered]@{
        number = 6
        action_name = "Run runtime health check"
        command_to_copy = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
        safety_level = "READ_ONLY"
        approval_required = "NO"
        reason = "Checks runtime health status without changing repo, broker, dashboard, or startup state."
    },
    [ordered]@{
        number = 7
        action_name = "Show git status"
        command_to_copy = "git status --short --branch"
        safety_level = "READ_ONLY"
        approval_required = "NO"
        reason = "Shows branch and changed files without staging, committing, or pushing."
    },
    [ordered]@{
        number = 8
        action_name = "Stop and wait"
        command_to_copy = "Stop. Wait for operator approval before taking action."
        safety_level = "WAIT"
        approval_required = "YES_FOR_ANY_NEXT_APPLY_OR_GIT_ACTION"
        reason = "Use when output shows blocked paths, stale locks, unclear approvals, or uncertainty."
    }
)

$result = [ordered]@{
    schema = "aios_operator_action_menu.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    menu_actions = $menuActions
    blocked_actions = @(
        "automatic_command_execution",
        "git_add",
        "commit",
        "push",
        "delete",
        "dashboard_work",
        "broker_trading_execution",
        "scheduled_tasks",
        "startup_task_changes",
        "secrets"
    )
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AIOS Operator Action Menu"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
foreach ($action in $menuActions) {
    Write-Host "$($action.number). $($action.action_name)"
    Write-Host "   command_to_copy: $($action.command_to_copy)"
    Write-Host "   safety_level: $($action.safety_level)"
    Write-Host "   approval_required: $($action.approval_required)"
    Write-Host "   reason: $($action.reason)"
    Write-Host ""
}
Write-Host "No commands were executed from this menu."
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
