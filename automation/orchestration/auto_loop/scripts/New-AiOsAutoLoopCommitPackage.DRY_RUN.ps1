[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-AiOsPathStartsWith {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Prefixes
    )

    $normalized = ($Path -replace "\\", "/").TrimStart("/")
    foreach ($prefix in $Prefixes) {
        $normalizedPrefix = ($prefix -replace "\\", "/").TrimStart("/")
        if ($normalized.StartsWith($normalizedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

$forbiddenPrefixes = @(
    "automation/orchestration/work_packets/",
    "automation/orchestration/approval_inbox/",
    "automation/orchestration/command_queue/",
    "automation/orchestration/workers/",
    "runtime/",
    "services/runtime/",
    "services/supervisor/",
    "services/orchestrator/",
    "apps/trading_lab/trading_lab/execution/",
    "aios/modules/trader/",
    "secrets/",
    "credentials/",
    "broker/",
    "OANDA/"
)

$safePrefixes = @(
    "automation/orchestration/auto_loop/",
    "telemetry/auto_loop/README.md",
    "telemetry/auto_loop/examples/"
)

$generatedPrefixes = @(
    "telemetry/auto_loop/reports/",
    "telemetry/night_supervisor/",
    "telemetry/backup_reports/"
)

$statusLines = @(& git status --porcelain=v1 --untracked-files=all)
$safeFiles = [System.Collections.Generic.List[string]]::new()
$untrackedCandidates = [System.Collections.Generic.List[string]]::new()
$riskyFiles = [System.Collections.Generic.List[string]]::new()
$generatedFiles = [System.Collections.Generic.List[string]]::new()
$forbiddenFiles = [System.Collections.Generic.List[string]]::new()

foreach ($line in $statusLines) {
    if (-not $line) {
        continue
    }

    $path = $line.Substring(3)
    $state = $line.Substring(0, 2)
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1]
    }

    if (Test-AiOsPathStartsWith -Path $path -Prefixes $forbiddenPrefixes) {
        $forbiddenFiles.Add($path)
    } elseif (Test-AiOsPathStartsWith -Path $path -Prefixes $generatedPrefixes) {
        $generatedFiles.Add($path)
    } elseif (Test-AiOsPathStartsWith -Path $path -Prefixes $safePrefixes) {
        if ($state -eq "??") {
            $untrackedCandidates.Add($path)
        } else {
            $safeFiles.Add($path)
        }
    } else {
        $riskyFiles.Add($path)
    }
}

$stageCandidates = @($safeFiles + $untrackedCandidates)
$gitAddCommands = @($stageCandidates | ForEach-Object { "git add -- `"$($_)`"" })

$record = [ordered]@{
    packet_id = "UNBOUND_DRY_RUN"
    safe_files_to_stage = @($safeFiles)
    untracked_candidates = @($untrackedCandidates)
    risky_files_to_review = @($riskyFiles)
    generated_files_to_exclude = @($generatedFiles)
    forbidden_files = @($forbiddenFiles)
    suggested_commit_message = "Add supervised auto-loop DRY_RUN bridge"
    recommended_git_add_commands = @($gitAddCommands)
    git_add_dot_allowed = $false
    commit_allowed = $false
    push_allowed = $false
    human_approval_required = $true
    blocked_actions = @("commit", "push", "merge", "live_trading", "broker_execution", "secret_access")
    did = @("Read git status and separated safe candidates, generated evidence, risky files, and forbidden files.")
    did_not = @("Did not stage files, commit, push, merge, mutate active queues, mutate active approval inbox, dispatch workers, or touch secrets.")
}

Write-Output ($record | ConvertTo-Json -Depth 10)
