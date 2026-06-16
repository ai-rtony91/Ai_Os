param(
    [string]$RepoRoot = "",
    [string]$DirtyTreeJsonPath = "",
    [switch]$OutputJson
)

$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    param([string]$Candidate)
    if ($Candidate -and $Candidate.Trim().Length -gt 0) {
        return (Resolve-Path -LiteralPath $Candidate).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
}

try {
    $resolvedRoot = Resolve-AiOsRepoRoot -Candidate $RepoRoot
    $scriptPath = Join-Path $resolvedRoot "automation\security\aios_preemptive_security_layer.py"
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        throw "Missing preemptive security scanner: $scriptPath"
    }

    $argsList = @($scriptPath, "--repo-root", $resolvedRoot)
    if ($DirtyTreeJsonPath -and $DirtyTreeJsonPath.Trim().Length -gt 0) {
        $argsList += @("--dirty-tree-json", (Resolve-Path -LiteralPath $DirtyTreeJsonPath).Path)
    }

    $json = & python @argsList
    if ($LASTEXITCODE -ne 0) {
        throw "Python scanner exited with code $LASTEXITCODE"
    }

    if ($OutputJson) {
        $json
    } else {
        $state = $json | ConvertFrom-Json
        [ordered]@{
            schema = $state.schema
            overall_state = $state.overall_state
            security_status = $state.security_status
            event_count = $state.event_count
            safe_for_dry_run = $state.safe_for_dry_run
            safe_for_apply = $state.safe_for_apply
            sos_required = $state.sos_required
            stop_required = $state.stop_required
            review_required = $state.review_required
            shield_state = $state.shield_state
            vault_lock_state = $state.vault_lock_state
            next_safe_action = $state.next_safe_action
        } | ConvertTo-Json -Depth 8
    }
    exit 0
} catch {
    $failure = [ordered]@{
        schema = "AIOS_PREEMPTIVE_SECURITY_STATE.v1"
        generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        repo_root = $RepoRoot
        component = "preemptive_security_layer"
        overall_state = "STOP"
        security_status = "SECURITY_SCANNER_FAILURE"
        safe_for_dry_run = $false
        safe_for_apply = $false
        sos_required = $false
        stop_required = $true
        review_required = $true
        event_count = 1
        events = @(
            [ordered]@{
                schema = "AIOS_PREEMPTIVE_SECURITY_EVENT.v1"
                event_id = "scanner_failure"
                category = "UNKNOWN_SECURITY_RISK"
                severity = "STOP"
                source_type = "scanner"
                source_path = "automation/security/aios_preemptive_security_layer.py"
                source_role = "security_scanner"
                reason = "Preemptive security scanner failed closed."
                indicators = @("scanner_failure")
                confidence = 1.0
                action = "STOP"
                matched_values_printed = $false
                values_redacted = $true
                contributes_to_stop = $true
                blocked_actions = @("APPLY", "git add", "git commit", "git push")
                next_safe_action = "Stop and inspect the scanner failure before continuing."
                safety = [ordered]@{
                    read_only = $true
                    secret_values_redacted = $true
                    network_access = $false
                    broker_access = $false
                    live_trading = $false
                    production_mutation = $false
                    dashboard_mutation = $false
                    scheduler_activation = $false
                    worker_launch = $false
                }
            }
        )
        category_counts = [ordered]@{ UNKNOWN_SECURITY_RISK = 1 }
        shield_state = "RED"
        vault_lock_state = "LOCKED_REVIEW"
        radar_events = @()
        tripwire_events = @()
        boss_alert = [ordered]@{ active = $true; level = "STOP"; reason = "Preemptive security scanner failed closed." }
        blocked_actions = @("APPLY", "git add", "git commit", "git push")
        next_safe_action = "Stop and inspect the scanner failure before continuing."
        safety = [ordered]@{
            read_only = $true
            stdout_only_by_default = $true
            secret_values_printed = $false
            writes_reports_by_default = $false
            network_access = $false
            broker_access = $false
            live_trading = $false
            real_order_execution = $false
            production_mutation = $false
            dashboard_mutation = $false
            scheduler_activation = $false
            daemon_activation = $false
            worker_launch = $false
        }
    }
    $failure | ConvertTo-Json -Depth 20
    exit 1
}
