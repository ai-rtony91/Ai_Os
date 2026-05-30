[CmdletBinding()]
param(
    [string[]]$ChangedPath = @(),
    [string]$PacketCandidatePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($PacketCandidatePath) {
    $packet = Get-Content -Raw -LiteralPath $PacketCandidatePath | ConvertFrom-Json
    if ($ChangedPath.Count -eq 0 -and $packet.allowed_paths) {
        $ChangedPath = @($packet.allowed_paths)
    }
}

if ($ChangedPath.Count -eq 0) {
    $ChangedPath = @("UNKNOWN")
}

$recommended = [System.Collections.Generic.List[object]]::new()
$required = [System.Collections.Generic.List[string]]::new()
$optional = [System.Collections.Generic.List[string]]::new()
$notes = [System.Collections.Generic.List[string]]::new()
$blockedIfMissing = [System.Collections.Generic.List[string]]::new()

$required.Add("git diff --check")

foreach ($path in $ChangedPath) {
    $normalized = $path -replace "\\", "/"

    if ($normalized -match "^(docs/|README\.md|AGENTS\.md|WHITEPAPER\.md)") {
        $recommended.Add([ordered]@{
            path_pattern = $normalized
            category = "docs_or_governance"
            command = "git diff --check"
            reason = "Documentation or governance paths require whitespace/conflict-marker validation and human review."
        })
    } elseif ($normalized -match "^apps/dashboard/") {
        $command = "manual dashboard review required"
        if (Test-Path -LiteralPath "apps/dashboard/package.json") {
            $command = "npm --prefix apps/dashboard run build"
        }
        $recommended.Add([ordered]@{
            path_pattern = $normalized
            category = "dashboard"
            command = $command
            reason = "Dashboard changes need build/lint validation when package scripts are available."
        })
    } elseif ($normalized -match "^(apps/trading_lab/|aios/modules/trader/|automation/trading_lab/)") {
        $recommended.Add([ordered]@{
            path_pattern = $normalized
            category = "paper_only_trading_lab"
            command = "paper-only safety tests and manual review"
            reason = "Trading Lab paths remain paper-only and require broker/live-execution safety review."
        })
        $blockedIfMissing.Add("paper-only Trading Lab safety evidence")
    } elseif ($normalized -match "^automation/orchestration/") {
        $command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
        if (-not (Test-Path -LiteralPath "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1")) {
            $command = "manual orchestration validator review required"
            $blockedIfMissing.Add("orchestration validator chain")
        }
        $recommended.Add([ordered]@{
            path_pattern = $normalized
            category = "orchestration"
            command = $command
            reason = "Orchestration paths require approval, validator, packet, and lock-aware review."
        })
    } elseif ($normalized -match "^telemetry/auto_loop/") {
        $recommended.Add([ordered]@{
            path_pattern = $normalized
            category = "generated_auto_loop_evidence"
            command = "manual evidence review"
            reason = "Auto-loop telemetry reports are generated evidence, not authority."
        })
    } else {
        $recommended.Add([ordered]@{
            path_pattern = $normalized
            category = "unknown"
            command = "manual review required"
            reason = "No route matched this path."
        })
        $blockedIfMissing.Add("manual review for unknown path")
    }
}

if (Test-Path -LiteralPath "automation/orchestration/validators/Test-ValidatorChainConfig.DRY_RUN.ps1") {
    $optional.Add("powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-ValidatorChainConfig.DRY_RUN.ps1")
}

$result = [ordered]@{
    packet_id = if ($PacketCandidatePath) { $packet.packet_id } else { "UNBOUND_DRY_RUN" }
    changed_path_patterns = $ChangedPath
    recommended_validators = @($recommended)
    required_validators = @($required)
    optional_validators = @($optional)
    blocked_if_missing = @($blockedIfMissing | Select-Object -Unique)
    notes = @(
        "DRY_RUN validator route only.",
        "This script recommends validators but does not run validators.",
        "Validator PASS does not authorize APPLY, commit, push, merge, or protected actions."
    )
    blocked_actions = @("commit", "push", "merge", "live_trading", "broker_execution", "secret_access", "worker_dispatch")
    did = @("Mapped changed paths to validator recommendations.")
    did_not = @("Did not execute validators, mutate queues, mutate approval inboxes, dispatch workers, commit, push, merge, or touch secrets.")
}

Write-Output ($result | ConvertTo-Json -Depth 10)
