param(
    [string]$DiscoveryReportPath = "",
    [string]$ControlPlaneEvidencePath = "",
    [string]$RouterEvidencePath = "",
    [string]$WorkerChannelMapPath = "",
    [string]$OutputMarkdownPath = "Reports/autonomy_control_plane/autonomy_status_report.md",
    [string]$OutputJsonPath = "Reports/autonomy_control_plane/autonomy_status_report.json"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Get-AiOsRepoRoot {
    $candidate = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($candidate)) {
        throw "REVIEW_REQUIRED: Unable to resolve repository root."
    }
    return $candidate.Trim()
}

function Resolve-AiOsPath {
    param(
        [Parameter(Mandatory = $true)][string]$PathHint,
        [Parameter(Mandatory = $true)][string]$RepoRoot
    )

    if ([string]::IsNullOrWhiteSpace($PathHint)) {
        return [string]::Empty
    }

    if ([System.IO.Path]::IsPathRooted($PathHint)) {
        return [System.IO.Path]::GetFullPath($PathHint)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $PathHint))
}

function Read-JsonOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        $raw = Get-Content -LiteralPath $Path -Raw
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return $null
        }
        return $raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Write-TextAtomic {
    param([string]$Path, [string]$Text)
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $tmp = Join-Path $parent ([guid]::NewGuid().ToString("N") + ".tmp")
    [System.IO.File]::WriteAllText($tmp, $Text, [System.Text.UTF8Encoding]::new($false))
    Move-Item -Force -LiteralPath $tmp -Destination $Path
}

function Emit-BlockedSummary {
    param([hashtable[]]$Items)
    if ($Items.Count -eq 0) {
        return @("No blockers detected.")
    }
    return $Items | ForEach-Object { if ($_.reason) { $_.reason } else { $_.item } }
}

function ConvertTo-BoolText {
    param([Parameter(Mandatory = $true)]$Value)
    if ($Value) { return "YES" }
    return "NO"
}

try {
    $repoRoot = Get-AiOsRepoRoot
    Set-Location -Path $repoRoot
    $outputMarkdownPath = Resolve-AiOsPath -PathHint $OutputMarkdownPath -RepoRoot $repoRoot
    $outputJsonPath = Resolve-AiOsPath -PathHint $OutputJsonPath -RepoRoot $repoRoot
    $discoveryPath = Resolve-AiOsPath -PathHint $DiscoveryReportPath -RepoRoot $repoRoot
    $controlPath = Resolve-AiOsPath -PathHint $ControlPlaneEvidencePath -RepoRoot $repoRoot
    $routerPath = Resolve-AiOsPath -PathHint $RouterEvidencePath -RepoRoot $repoRoot
    $channelPath = Resolve-AiOsPath -PathHint $WorkerChannelMapPath -RepoRoot $repoRoot

    $discovery = Read-JsonOrNull -Path $discoveryPath
    $control = Read-JsonOrNull -Path $controlPath
    $router = Read-JsonOrNull -Path $routerPath
    $channels = Read-JsonOrNull -Path $channelPath

    $controlStatus = if ($control -and $control.status) { [string]$control.status } else { "UNKNOWN" }
    $routerAction = if ($router -and $router.next_action) { [string]$router.next_action } else { "UNKNOWN" }

    $blockers = [System.Collections.Generic.List[object]]::new()
    if (-not $discovery) { $blockers.Add([ordered]@{ item = "discovery"; reason = "discovery report missing or unreadable"; source = $DiscoveryReportPath }) }
    if (-not $control) { $blockers.Add([ordered]@{ item = "control_plane"; reason = "control plane evidence missing or unreadable"; source = $ControlPlaneEvidencePath }) }
    if (-not $router) { $blockers.Add([ordered]@{ item = "router"; reason = "router route evidence missing or unreadable"; source = $RouterEvidencePath }) }
    if (-not $channels) { $blockers.Add([ordered]@{ item = "channels"; reason = "worker-channel map missing or unreadable"; source = $WorkerChannelMapPath }) }
    if ($channels -and -not $channels.channels) {
        $blockers.Add([ordered]@{ item = "channels"; reason = "worker-channel map has no channels"; source = $WorkerChannelMapPath })
    }

    if ($controlStatus -eq "VALIDATION_FAILED") {
        $blockers.Add([ordered]@{ item = "control_plane"; reason = "control plane validation failed"; source = $controlPath })
    }
    if ($controlStatus -eq "PROTECTED_ACTION_REQUIRED") {
        $blockers.Add([ordered]@{ item = "control_plane"; reason = "PROTECTED_ACTION_REQUIRED: manual approval required"; source = $controlPath })
    }
    if ($controlStatus -eq "SOS_REQUIRED") {
        $blockers.Add([ordered]@{ item = "control_plane"; reason = "SOS_REQUIRED: escalate for operator review"; source = $controlPath })
    }
    if ($controlStatus -eq "BLOCKED") {
        $blockers.Add([ordered]@{ item = "control_plane"; reason = "control plane reported BLOCKED"; source = $controlPath })
    }

    $controlsReady = @("READY_FOR_CODEX", "PROTECTED_ACTION_REQUIRED", "SOS_REQUIRED")
    $canAct = [System.Collections.Generic.List[object]]::new()
    $requireApproval = [System.Collections.Generic.List[object]]::new()
    if ($controlStatus -eq "READY_FOR_CODEX") {
        $canAct.Add([ordered]@{ action = "RUN_CODEX_WITH_PACKET"; command = ".\\aios.ps1 -Mode autonomy -Goal ""..." ; note = "Control plane is ready and packet validation passed" })
    }
    if ($controlStatus -eq "VALIDATION_FAILED") {
        $canAct.Add([ordered]@{ action = "FIX_VALIDATION"; command = "Review control plane validation output and fix errors"; note = "Validation output must pass before autonomous progression" })
    }
    if ($controlStatus -eq "PROTECTED_ACTION_REQUIRED") {
        $requireApproval.Add([ordered]@{ action = "REQUEST_APPROVAL"; reason = "Protected authority or policy path is required"; command = ".\\aios.ps1 -Mode autonomy -Goal ""..." })
    }
    if ($routerAction -eq "ESCALATE_SOS") {
        $requireApproval.Add([ordered]@{ action = "ESCALATE_SOS"; reason = "System escalation is needed"; command = ".\\aios.ps1 -Mode autonomy-status" })
    }
    if ($controlStatus -eq "READY_FOR_CODEX") {
        $canAct.Add([ordered]@{ action = "OPEN_PR"; command = ".\\aios.ps1 -Mode autonomy-next"; note = "Generate PR when ready." })
    }

    $forexChecks = @()
    $forexChecks += if ($discovery -and $discovery.components -and $discovery.components.trading) {
        if ($discovery.components.trading.automation_exists) { $true } else { $false }
    } else { $false }
    $forexChecks += if ($discovery -and $discovery.components.packet_runner -and $discovery.components.packet_runner.exists) { $true } else { $false }
    $forexChecks += if ($discovery -and $discovery.components.autonomy_loop -and $discovery.components.autonomy_loop.exists) { $true } else { $false }
    $forexChecks += if ($discovery -and $discovery.components.coordination_spine -and $discovery.components.coordination_spine.exists) { $true } else { $false }

    $forexReadyCount = (($forexChecks | Where-Object { $_ } | Measure-Object).Count)
    $forexReadyScore = [int](($forexReadyCount * 100) / [Math]::Max($forexChecks.Count, 1))
    $forexReadiness = if ($forexReadyScore -ge 75 -and $controlStatus -in $controlsReady) { "READY" } elseif ($forexReadyScore -ge 50) { "PARTIAL" } else { "BLOCKED" }
    if ($controlStatus -eq "BLOCKED" -or $controlStatus -eq "VALIDATION_FAILED") { $forexReadiness = "BLOCKED" }

    $readiness = if ($controlStatus -eq "READY_FOR_CODEX") { "READY" } elseif ($controlStatus -in @("PROTECTED_ACTION_REQUIRED", "SOS_REQUIRED")) { "BLOCKED" } elseif ($controlStatus -eq "VALIDATION_FAILED") { "BLOCKED" } elseif ($control -and $control.status) { "PARTIAL" } else { "UNKNOWN" }

    $summary = [ordered]@{
        schema_version = "AIOS-AUTONOMY-STATUS-REPORT-V1"
        created_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        autonomy_readiness = $readiness
        sources = [ordered]@{
            discovery_report = if ($discoveryPath) { $discoveryPath } else { $null }
            control_plane_evidence = if ($controlPath) { $controlPath } else { $null }
            router_evidence = if ($routerPath) { $routerPath } else { $null }
            worker_channel_map = if ($channelPath) { $channelPath } else { $null }
        }
        control_status = $controlStatus
        next_action = $routerAction
        can_autonomously_do_next = @($canAct)
        requires_anthony_approval = @($requireApproval)
        forex_builder_readiness = [ordered]@{
            status = $forexReadiness
            readiness_score = $forexReadyScore
            controls_required = @("autonomy loop", "packet runner", "control evidence", "validation evidence")
        }
        blocker_summary = @(
            Emit-BlockedSummary -Items $blockers
        )
        created_markdown_path = $outputMarkdownPath
        created_json_path = $outputJsonPath
    }

    if ($summary.blocker_summary.Count -eq 1 -and $summary.blocker_summary[0] -eq "No blockers detected.") {
        $summary.blockers_exist = $false
    } else {
        $summary.blockers_exist = $true
    }

    $markdown = @"
# AIOS Autonomy Status Report

## Current Autonomy Readiness

- Readiness: $($summary.autonomy_readiness)
- Control status: $($summary.control_status)
- Router next action: $($summary.next_action)
- Forex builder readiness: $($summary.forex_builder_readiness.status) (score: $($summary.forex_builder_readiness.readiness_score))

## What AI_OS can do automatically next
@" + (
        if ($summary.can_autonomously_do_next.Count -gt 0) {
            ($summary.can_autonomously_do_next | ForEach-Object { "`n- $($_.action): $($_.note); command: $($_.command)" }) -join ""
        } else {
            "`n- No autonomous action is currently safe."
        }
    ) + @"

## What Anthony must still approve
@" + (
        if ($summary.requires_anthony_approval.Count -gt 0) {
            ($summary.requires_anthony_approval | ForEach-Object { "`n- $($_.action): $($_.reason)" }) -join ""
        } else {
            "`n- No explicit approval action is currently required."
        }
    ) + @"

## Blocker summary
"@
    foreach ($line in $summary.blocker_summary) {
        $markdown += "`n- $line"
    }

    $markdown += @"

## Command surface

- .\aios.ps1 -Mode autonomy -Goal "..."
- .\aios.ps1 -Mode packet -Path "..."
- .\aios.ps1 -Mode forex-build -Goal "..."
- .\aios.ps1 -Mode autonomy-status
- .\aios.ps1 -Mode autonomy-next

## Notes

- This report is DRY-RUN only and does not execute merges, applies, broker actions, live trading, or secret commands.
"@

    Write-TextAtomic -Path $outputJsonPath -Text ($summary | ConvertTo-Json -Depth 20)
    Write-TextAtomic -Path $outputMarkdownPath -Text $markdown

    Write-Output ($summary | ConvertTo-Json -Depth 20)

    if ($summary.blockers_exist -or $controlStatus -eq "UNKNOWN") {
        exit 1
    }
    exit 0
} catch {
    $errorMessage = $_.Exception.Message
    Write-Error "REVIEW_REQUIRED: $errorMessage"
    exit 1
}
