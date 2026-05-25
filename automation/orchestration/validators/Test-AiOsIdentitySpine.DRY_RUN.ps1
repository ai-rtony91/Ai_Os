[CmdletBinding()]
param(
    [string]$PacketPath = "automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json"
)

$ErrorActionPreference = "Stop"

function Add-Result {
    param(
        [System.Collections.Generic.List[object]]$Results,
        [string]$Check,
        [string]$Result,
        [string]$Evidence,
        [string]$NextSafeAction
    )

    $Results.Add([pscustomobject]@{
        check = $Check
        result = $Result
        evidence = $Evidence
        next_safe_action = $NextSafeAction
    }) | Out-Null
}

function Get-RepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }
    return $root.Trim()
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot

$results = [System.Collections.Generic.List[object]]::new()
$requiredFiles = @(
    "docs/governance/aios-identity-and-lane-governance.md",
    "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
    "docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md",
    "docs/workflows/VALIDATOR_EXECUTION_STANDARD.md",
    "automation/orchestration/locks/PATH_CONFLICT_POLICY_001.md",
    "automation/orchestration/validators/VALIDATOR_CHAIN_RUNBOOK_001.md"
)

foreach ($path in $requiredFiles) {
    $fullPath = Join-Path $repoRoot $path
    if (Test-Path -LiteralPath $fullPath) {
        Add-Result -Results $results -Check "required_file:$path" -Result "PASS" -Evidence "File exists." -NextSafeAction "Continue identity-spine validation."
    }
    else {
        Add-Result -Results $results -Check "required_file:$path" -Result "BLOCKED" -Evidence "File missing." -NextSafeAction "Restore or create the approved identity-spine authority file before APPLY."
    }
}

$resolvedPacketPath = Join-Path $repoRoot $PacketPath
$packet = $null
if (Test-Path -LiteralPath $resolvedPacketPath) {
    try {
        $packet = Get-Content -LiteralPath $resolvedPacketPath -Raw | ConvertFrom-Json
        Add-Result -Results $results -Check "packet_json" -Result "PASS" -Evidence "Packet JSON parsed." -NextSafeAction "Check required packet identity fields."
    }
    catch {
        Add-Result -Results $results -Check "packet_json" -Result "BLOCKED" -Evidence "Packet JSON failed to parse." -NextSafeAction "Fix packet JSON before APPLY."
    }
}
else {
    Add-Result -Results $results -Check "packet_json" -Result "BLOCKED" -Evidence "Packet path missing: $PacketPath" -NextSafeAction "Restore packet template before APPLY."
}

if ($null -ne $packet) {
    $requiredPacketFields = @(
        "packet_id",
        "identity_marker",
        "supervisor_identity",
        "zone",
        "worker_identity",
        "mode",
        "owner_lane",
        "assigned_worker",
        "branch",
        "worktree",
        "allowed_write_boundary",
        "blocked_paths",
        "forbidden_paths",
        "approval_authority",
        "validator_chain",
        "lock_id",
        "stop_condition"
    )

    foreach ($field in $requiredPacketFields) {
        if ($packet.PSObject.Properties.Name -contains $field) {
            Add-Result -Results $results -Check "packet_field:$field" -Result "PASS" -Evidence "Field exists." -NextSafeAction "Continue packet field validation."
        }
        else {
            Add-Result -Results $results -Check "packet_field:$field" -Result "BLOCKED" -Evidence "Field missing." -NextSafeAction "Add the missing packet identity field before APPLY."
        }
    }

    if ($packet.mode -in @("DRY_RUN", "APPLY", "")) {
        Add-Result -Results $results -Check "packet_mode" -Result "PASS" -Evidence "Mode is DRY_RUN, APPLY, or blank template placeholder." -NextSafeAction "Use explicit DRY_RUN or APPLY in executable packets."
    }
    else {
        Add-Result -Results $results -Check "packet_mode" -Result "BLOCKED" -Evidence "Invalid mode: $($packet.mode)" -NextSafeAction "Set mode to DRY_RUN or APPLY."
    }
}

$textChecks = @(
    @{
        path = "docs/governance/aios-identity-and-lane-governance.md"
        patterns = @("Human Owner", "Business GPT", "Claude Chat", "Codex East", "Claude Code West", "EAST_OCC_##", "WEST_OCC_##", "VALIDATOR_##", "LOCK_<ZONE>_<LANE>_<WORKER>", "No packet means no work")
    },
    @{
        path = "automation/orchestration/locks/PATH_CONFLICT_POLICY_001.md"
        patterns = @("LOCK_<ZONE>_<LANE>_<WORKER>", "East and West")
    },
    @{
        path = "automation/orchestration/validators/VALIDATOR_CHAIN_RUNBOOK_001.md"
        patterns = @("identity_spine")
    }
)

foreach ($item in $textChecks) {
    $fullPath = Join-Path $repoRoot $item.path
    if (-not (Test-Path -LiteralPath $fullPath)) { continue }
    $content = Get-Content -LiteralPath $fullPath -Raw
    foreach ($pattern in $item.patterns) {
        if ($content -like "*$pattern*") {
            Add-Result -Results $results -Check "text:$($item.path):$pattern" -Result "PASS" -Evidence "Required text found." -NextSafeAction "Continue identity-spine validation."
        }
        else {
            Add-Result -Results $results -Check "text:$($item.path):$pattern" -Result "BLOCKED" -Evidence "Required text missing." -NextSafeAction "Add the required identity-spine text before APPLY."
        }
    }
}

$blockedCount = @($results | Where-Object { $_.result -eq "BLOCKED" }).Count
$overall = if ($blockedCount -gt 0) { "BLOCKED" } else { "PASS" }

Write-Output "AI_OS identity-spine validator results:"
foreach ($result in $results) {
    Write-Output ("{0}: {1} - {2}" -f $result.check, $result.result, $result.evidence)
}

[pscustomobject]@{
    validator = "Test-AiOsIdentitySpine.DRY_RUN.ps1"
    mode = "DRY_RUN_READ_ONLY"
    overall_result = $overall
    blocked_count = $blockedCount
    modifies_files = $false
    commits = $false
    pushes = $false
    next_safe_action = if ($overall -eq "PASS") { "Identity-spine validation passed. Human approval is still required before APPLY, commit, or push." } else { "Resolve BLOCKED identity-spine checks before APPLY, commit, or push." }
} | ConvertTo-Json -Depth 5
