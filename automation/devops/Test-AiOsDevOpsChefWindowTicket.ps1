param(
    [string]$TicketPath = "apps/dashboard/mock-data/aios-devops-chef-window-ticket.example.json"
)

$ErrorActionPreference = "Stop"

$requiredFields = @(
    "ticket_id",
    "schema_version",
    "window",
    "status",
    "request",
    "labels",
    "safety_check",
    "approval",
    "completion_log",
    "next_safe_action"
)

$requiredWorkflow = @(
    "request",
    "label",
    "safety_check",
    "wait_for_approval",
    "approve_or_reject",
    "log_completion"
)

$requiredBlockedActions = @(
    "dashboard_ui_edits",
    "javascript_dashboard_edits",
    "installs",
    "startup_tasks",
    "secrets_handling",
    "credential_handling",
    "route_changes",
    "trading_lab_logic_changes",
    "broker_orders",
    "live_trading",
    "commits",
    "pushes"
)

if (-not (Test-Path -LiteralPath $TicketPath)) {
    throw "Ticket file not found: $TicketPath"
}

$rawJson = Get-Content -LiteralPath $TicketPath -Raw
$ticket = $rawJson | ConvertFrom-Json
$propertyNames = @($ticket.PSObject.Properties.Name)

$missingFields = @($requiredFields | Where-Object { $_ -notin $propertyNames })
if ($missingFields.Count -gt 0) {
    throw "Missing required ticket fields: $($missingFields -join ', ')"
}

$workflow = @($ticket.workflow)
$missingWorkflow = @($requiredWorkflow | Where-Object { $_ -notin $workflow })
if ($missingWorkflow.Count -gt 0) {
    throw "Missing kitchen-ticket workflow steps: $($missingWorkflow -join ', ')"
}

$blockedActions = @($ticket.safety_check.blocked_actions)
$missingBlockedActions = @($requiredBlockedActions | Where-Object { $_ -notin $blockedActions })
if ($missingBlockedActions.Count -gt 0) {
    throw "Missing blocked actions: $($missingBlockedActions -join ', ')"
}

if ($ticket.safety_check.requires_dry_run -ne $true) {
    throw "Safety gate failed: requires_dry_run must be true."
}

if ($ticket.safety_check.requires_operator_approval -ne $true) {
    throw "Safety gate failed: requires_operator_approval must be true."
}

if ($ticket.status -ne "waiting_for_approval") {
    throw "Ticket status must remain waiting_for_approval for this scaffold."
}

Write-Output "AI_OS DevOps Chef Window ticket validation passed."
Write-Output "Ticket: $($ticket.ticket_id)"
Write-Output "Status: $($ticket.status)"
Write-Output "Required fields: $($requiredFields -join ', ')"
Write-Output "Workflow: $($requiredWorkflow -join ' -> ')"
Write-Output "Blocked actions checked: $($requiredBlockedActions -join ', ')"
