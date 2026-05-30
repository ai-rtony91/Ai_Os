[CmdletBinding()]
param(
    [string]$ExpectedBranch = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-AiOsCheck {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$Message
    )

    [ordered]@{
        name = $Name
        status = $Status
        message = $Message
    }
}

$checks = @()
$worktree = (Get-Location).Path
$branch = (& git branch --show-current 2>$null)
$status = (& git status --short --branch 2>$null)
$remote = (& git remote -v 2>$null)

if ($worktree -eq "C:\Dev\Ai.Os") {
    $checks += New-AiOsCheck -Name "worktree" -Status "PASS" -Message $worktree
} else {
    $checks += New-AiOsCheck -Name "worktree" -Status "BLOCK" -Message "Expected C:\Dev\Ai.Os; found $worktree."
}

if ($branch -eq $ExpectedBranch) {
    $checks += New-AiOsCheck -Name "branch" -Status "PASS" -Message $branch
} else {
    $checks += New-AiOsCheck -Name "branch" -Status "BLOCK" -Message "Expected $ExpectedBranch; found $branch."
}

if (($remote -join "`n") -match "ai-rtony91/Ai_Os") {
    $checks += New-AiOsCheck -Name "remote" -Status "PASS" -Message "origin points at ai-rtony91/Ai_Os."
} else {
    $checks += New-AiOsCheck -Name "remote" -Status "BLOCK" -Message "Expected origin to reference ai-rtony91/Ai_Os."
}

if (($status -join "`n") -match "^(AA|DD|UU|AU|UA|DU|UD) ") {
    $checks += New-AiOsCheck -Name "merge_state" -Status "BLOCK" -Message "Unresolved merge conflict markers appear in git status."
} else {
    $checks += New-AiOsCheck -Name "merge_state" -Status "PASS" -Message "No unresolved merge status detected."
}

$systemPaths = [ordered]@{
    packet_queue = "automation/orchestration/work_packets"
    worker_registry = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
    worker_inbox = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
    approval_inbox = "automation/orchestration/approval_inbox"
    validator_system = "automation/orchestration/validators"
    commit_package_system = "automation/orchestration/commit_packages"
    clean_state_gate = "automation/orchestration/clean_state_gate.ps1"
    telemetry = "telemetry"
}

$found = [ordered]@{}
foreach ($key in $systemPaths.Keys) {
    $path = $systemPaths[$key]
    $exists = Test-Path -LiteralPath $path
    $found[$key] = $exists
    if ($exists) {
        $checks += New-AiOsCheck -Name $key -Status "PASS" -Message "Found $path."
    } else {
        $checks += New-AiOsCheck -Name $key -Status "WARN" -Message "Missing or unavailable: $path."
    }
}

$blockedCount = @($checks | Where-Object { $_.status -eq "BLOCK" }).Count
$warnCount = @($checks | Where-Object { $_.status -eq "WARN" }).Count
$overall = if ($blockedCount -gt 0) { "BLOCK" } elseif ($warnCount -gt 0) { "WARN" } else { "PASS" }

$result = [ordered]@{
    task = "AI_OS auto-loop preflight DRY_RUN"
    status = $overall
    worktree = $worktree
    branch = $branch
    expected_branch = $ExpectedBranch
    active_systems_found = $found
    checks = $checks
    blocked_actions = @("commit", "push", "merge", "live_trading", "broker_execution", "secret_access", "active_state_mutation")
    did = @("Checked repo location, branch, remote, merge status, and key active-system paths.")
    did_not = @("Did not mutate queues, approval inbox, worker registry, telemetry runtime, commits, pushes, merges, broker paths, or secrets.")
}

Write-Output ($result | ConvertTo-Json -Depth 10)
