Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$supervisorPath = Join-Path $orchestrationRoot "validator_routing_supervisor.v1.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-List {
    param([object[]]$Items)

    if ($Items.Count -eq 0) {
        Write-Host "    - None"
        return
    }

    foreach ($item in $Items) {
        Write-Host "    - $item"
    }
}

$supervisor = Read-JsonFile -Path $supervisorPath
$routes = @($supervisor.validator_routes)
$backlog = $supervisor.validator_backlog

Write-Host "AI_OS Validator Routing Supervisor Display"
Write-Host "Mode: $($supervisor.mode)"
Write-Host "Supervisor: $($supervisor.supervisor_name)"
Write-Host "Purpose: $($supervisor.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No validators are run. No workers, scheduled tasks, or startup tasks are launched."
Write-Host ""

if ($routes.Count -eq 0) {
    Write-Host "Validator routes: none found in validator_routing_supervisor.v1.example.json"
    exit 0
}

$requiredRoutes = @($routes | Where-Object { $_.required -eq $true })
$readyRoutes = @($routes | Where-Object { $_.ready -eq $true })
$blockedRoutes = @($routes | Where-Object { $_.blocked -eq $true -or $_.status -eq "blocked" })
$waitingRoutes = @($routes | Where-Object { $_.status -match "waiting" })
$categories = @($routes | Group-Object category)

Write-Host "Validator summary:"
Write-Host "  Total routes: $($routes.Count)"
Write-Host "  Required routes: $($requiredRoutes.Count)"
Write-Host "  Ready routes: $($readyRoutes.Count)"
Write-Host "  Waiting routes: $($waitingRoutes.Count)"
Write-Host "  Blocked routes: $($blockedRoutes.Count)"
Write-Host "  Validation backlog: $($backlog.validation_backlog)"
Write-Host ""

Write-Host "Validator categories:"
foreach ($category in $categories) {
    Write-Host "  - $($category.Name): $($category.Count)"
}
Write-Host ""

Write-Host "Validator assignments:"
foreach ($route in ($routes | Sort-Object backlog_position, validator_id)) {
    $blockReason = if ([string]::IsNullOrWhiteSpace([string]$route.block_reason)) { "none" } else { $route.block_reason }
    $backlogPosition = if ([string]::IsNullOrWhiteSpace([string]$route.backlog_position)) { "none" } else { $route.backlog_position }

    Write-Host "  Validator: $($route.validator_id)"
    Write-Host "    Name: $($route.validator_name)"
    Write-Host "    Category: $($route.category)"
    Write-Host "    Assigned packet: $($route.assigned_packet_id)"
    Write-Host "    Required: $($route.required)"
    Write-Host "    Ready: $($route.ready)"
    Write-Host "    Status: $($route.status)"
    Write-Host "    Blocked: $($route.blocked)"
    Write-Host "    Block reason: $blockReason"
    Write-Host "    Backlog position: $backlogPosition"
    Write-Host "    Notes: $($route.notes)"
}
Write-Host ""

Write-Host "Blocked actions:"
Write-List -Items @($supervisor.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review validator routing only; use a separate approved workflow before running validators."
