<#
.SYNOPSIS
Writes a compact AI_OS morning brief from local night-cycle evidence.
#>

[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$Date = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$relayRoot = Join-Path $repoRoot "relay"
$reportDir = Join-Path $relayRoot "reports"
$briefPath = Join-Path $reportDir ("MORNING_BRIEF_{0}.md" -f $Date)
$cycleMarkerPath = Join-Path $repoRoot "control\cycle\last_marker.json"
$morningDigestPath = Join-Path $repoRoot "telemetry\morning_digest\MORNING_DIGEST_LATEST.md"
$morningDigestStatePath = Join-Path $repoRoot "telemetry\morning_digest\MORNING_DIGEST_STATE.json"
$bridgeStatePath = Join-Path $repoRoot "telemetry\night_supervisor\AUTONOMY_BRIDGE_STATE.json"

function Get-AiOsTaskJson {
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Get-AiOsGroupedCount {
    param(
        [AllowEmptyCollection()]
        [object[]]$Objects,
        [Parameter(Mandatory = $true)][string]$Property
    )

    $values = @(
        foreach ($object in $Objects) {
            if ($null -ne $object -and $object.PSObject.Properties.Name -contains $Property -and -not [string]::IsNullOrWhiteSpace([string]$object.$Property)) {
                [string]$object.$Property
            } else {
                "UNKNOWN"
            }
        }
    )

    if ($values.Count -eq 0) { return "none" }
    return (($values | Group-Object | Sort-Object Name | ForEach-Object { "{0}={1}" -f $_.Name, $_.Count }) -join ", ")
}

function Get-AiOsGitStatus {
    Push-Location -LiteralPath $repoRoot
    try {
        $lines = @(git status --short 2>$null | ForEach-Object { [string]$_ })
        return [pscustomobject]@{
            clean = ($lines.Count -eq 0)
            count = $lines.Count
            lines = $lines
        }
    }
    finally {
        Pop-Location
    }
}

function Get-AiOsTrustGate {
    param([Parameter(Mandatory = $true)][datetime]$Now)

    $reasons = New-Object System.Collections.Generic.List[string]
    $marker = $null
    if (-not (Test-Path -LiteralPath $cycleMarkerPath -PathType Leaf)) {
        $reasons.Add("missing cycle marker: control/cycle/last_marker.json")
    } else {
        $marker = Get-AiOsTaskJson -Path $cycleMarkerPath
        if ($null -eq $marker) {
            $reasons.Add("cycle marker is unreadable JSON: control/cycle/last_marker.json")
        } elseif ($marker.PSObject.Properties.Name -notcontains "phase_state") {
            $reasons.Add("cycle marker missing phase_state: control/cycle/last_marker.json")
        } elseif ([string]$marker.phase_state -ne "CYCLE_COMPLETE") {
            $actualPhaseState = [string]$marker.phase_state
            $reasons.Add("cycle marker phase_state is '$actualPhaseState', expected CYCLE_COMPLETE")
        }
    }

    foreach ($evidence in @(
        [pscustomobject]@{ Label = "morning digest"; Path = $morningDigestPath },
        [pscustomobject]@{ Label = "morning digest state"; Path = $morningDigestStatePath },
        [pscustomobject]@{ Label = "autonomy bridge state"; Path = $bridgeStatePath }
    )) {
        if (-not (Test-Path -LiteralPath $evidence.Path -PathType Leaf)) {
            $reasons.Add("missing $($evidence.Label): $($evidence.Path.Substring($repoRoot.Length + 1))")
            continue
        }

        $file = Get-Item -LiteralPath $evidence.Path
        if ($file.Length -le 0) {
            $reasons.Add("empty $($evidence.Label): $($evidence.Path.Substring($repoRoot.Length + 1))")
            continue
        }
        if (($Now.ToUniversalTime() - $file.LastWriteTimeUtc).TotalHours -gt 18) {
            $reasons.Add("stale $($evidence.Label): $($evidence.Path.Substring($repoRoot.Length + 1))")
        }
    }

    if ($reasons.Count -gt 0) {
        return [pscustomobject]@{ Status = "REVIEW"; Reason = ($reasons -join "; ") }
    }
    return [pscustomobject]@{ Status = "READY"; Reason = "cycle marker and morning evidence are current" }
}

function Get-AiOsEvidenceFreshness {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][datetime]$Now,
        [int]$MaxAgeHours = 18
    )

    $relative = if ($Path.StartsWith($repoRoot)) { $Path.Substring($repoRoot.Length + 1) } else { $Path }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{ label = $Label; path = $relative; status = "BLOCKED"; detail = "missing"; age_hours = $null; generated_at = "" }
    }

    $file = Get-Item -LiteralPath $Path
    if ($file.Length -le 0) {
        return [pscustomobject]@{ label = $Label; path = $relative; status = "BLOCKED"; detail = "empty"; age_hours = $null; generated_at = "" }
    }

    $generatedAt = ""
    $basisTime = $file.LastWriteTimeUtc
    $detail = "modified_time"
    if ($Path.EndsWith(".json", [System.StringComparison]::OrdinalIgnoreCase)) {
        $json = Get-AiOsTaskJson -Path $Path
        if ($null -ne $json -and $json.PSObject.Properties.Name -contains "generated_at" -and -not [string]::IsNullOrWhiteSpace([string]$json.generated_at)) {
            $generatedAt = [string]$json.generated_at
            $parsed = [datetime]::MinValue
            if ([datetime]::TryParse($generatedAt, [ref]$parsed)) {
                $basisTime = $parsed.ToUniversalTime()
                $detail = "generated_at"
            } else {
                return [pscustomobject]@{ label = $Label; path = $relative; status = "WARN"; detail = "generated_at_unreadable"; age_hours = $null; generated_at = $generatedAt }
            }
        }
    }

    $ageHours = [math]::Round(($Now.ToUniversalTime() - $basisTime.ToUniversalTime()).TotalHours, 2)
    if ($ageHours -gt $MaxAgeHours) {
        return [pscustomobject]@{ label = $Label; path = $relative; status = "WARN"; detail = "STALE by $detail"; age_hours = $ageHours; generated_at = $generatedAt }
    }
    return [pscustomobject]@{ label = $Label; path = $relative; status = "PASS"; detail = "fresh by $detail"; age_hours = $ageHours; generated_at = $generatedAt }
}

$doneFiles = @(Get-ChildItem -LiteralPath (Join-Path $relayRoot "done") -File -Filter "*.task.json" -ErrorAction SilentlyContinue)
$errorFiles = @(Get-ChildItem -LiteralPath (Join-Path $relayRoot "error") -File -Filter "*.task.json" -ErrorAction SilentlyContinue)
$doneTasks = @($doneFiles | ForEach-Object { Get-AiOsTaskJson -Path $_.FullName })
$errorTasks = @($errorFiles | ForEach-Object { Get-AiOsTaskJson -Path $_.FullName })

$approvalFiles = @(Get-ChildItem -LiteralPath (Join-Path $relayRoot "approvals") -File -Filter "*" -ErrorAction SilentlyContinue)
$now = Get-Date
$trustGate = Get-AiOsTrustGate -Now $now
$freshness = @(
    Get-AiOsEvidenceFreshness -Label "morning_digest" -Path $morningDigestPath -Now $now
    Get-AiOsEvidenceFreshness -Label "morning_digest_state" -Path $morningDigestStatePath -Now $now
    Get-AiOsEvidenceFreshness -Label "autonomy_bridge_state" -Path $bridgeStatePath -Now $now
)
$morningEvidenceStatus = if ($freshness | Where-Object { $_.status -eq "BLOCKED" }) {
    "BLOCKED"
} elseif (($freshness | Where-Object { $_.status -eq "WARN" }) -or $trustGate.Status -eq "REVIEW") {
    "WARN"
} else {
    "PASS"
}
$digestFreshness = ($freshness | ForEach-Object { "$($_.label)=$($_.status) age_hours=$($_.age_hours) detail=$($_.detail)" }) -join "; "
$morningNextSafeAction = if ($morningEvidenceStatus -eq "PASS") {
    "Morning evidence is current; review it before any protected action."
} elseif ($morningEvidenceStatus -eq "WARN") {
    "Refresh Morning Digest and Autonomy Bridge evidence before using it as deployment proof."
} else {
    "Run the Night Supervisor and Autonomy Bridge evidence chain before deployment proof."
}
$approvalLines = @(
    foreach ($file in $approvalFiles | Sort-Object Name) {
        $age = [int]($now.ToUniversalTime() - $file.LastWriteTimeUtc).TotalHours
        "- $($file.Name) age_hours=$age"
    }
)
if ($approvalLines.Count -eq 0) { $approvalLines = @("- none") }

$telemetryDir = Join-Path $repoRoot ("telemetry\night_supervisor\{0}" -f $Date)
$telemetryFiles = @(Get-ChildItem -LiteralPath $telemetryDir -File -ErrorAction SilentlyContinue)
$telemetryText = if ($telemetryFiles.Count -eq 0) { "not found" } else { "{0} file(s)" -f $telemetryFiles.Count }
$blockedCount = 0
$validatorText = "none"
foreach ($file in $telemetryFiles) {
    try {
        $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
        if ($json.PSObject.Properties.Name -contains "blocked_count") { $blockedCount += [int]$json.blocked_count }
        if ($json.PSObject.Properties.Name -contains "validator_results") { $validatorText = "present" }
    }
    catch {
        # Ignore non-JSON telemetry in the compact morning brief.
    }
}

$backlogPath = Join-Path $repoRoot "control\self_continuation\BACKLOG.json"
$readyByTier = "not found"
if (Test-Path -LiteralPath $backlogPath -PathType Leaf) {
    $backlog = Get-Content -LiteralPath $backlogPath -Raw | ConvertFrom-Json
    $items = if ($backlog.PSObject.Properties.Name -contains "items") { @($backlog.items) } else { @($backlog.candidates) }
    $ready = @($items | Where-Object { [string]$_.status -eq "READY" })
    $readyByTier = if ($ready.Count -eq 0) {
        "none"
    } else {
        (($ready | Group-Object { if ($_.PSObject.Properties.Name -contains "risk_tier") { $_.risk_tier } else { $_.risk_level } } | Sort-Object Name | ForEach-Object { "{0}={1}" -f $_.Name, $_.Count }) -join ", ")
    }
}

$git = Get-AiOsGitStatus
$repoState = if ($git.clean) { "clean" } else { "dirty count=$($git.count)" }
$nextCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File automation\orchestration\Invoke-AiOsNightCycle.ps1"
$digestReference = if (Test-Path -LiteralPath $morningDigestPath -PathType Leaf) {
    "telemetry/morning_digest/MORNING_DIGEST_LATEST.md"
} else {
    "telemetry/morning_digest/MORNING_DIGEST_LATEST.md (missing)"
}

$lines = @(
    "# AI_OS Morning Brief - $Date"
    ""
    "STATUS = $($trustGate.Status)"
    "Reason: $($trustGate.Reason)"
    "Canonical digest: $digestReference"
    "morning_evidence_status = $morningEvidenceStatus"
    "digest_path = $digestReference"
    "digest_freshness = $digestFreshness"
    "next_safe_action = $morningNextSafeAction"
    ""
    "## WHAT THE NIGHT DID"
    "- done_count=$($doneFiles.Count)"
    "- done_by_worker=$(Get-AiOsGroupedCount -Objects $doneTasks -Property worker)"
    "- done_by_tier=$(Get-AiOsGroupedCount -Objects $doneTasks -Property tier)"
    "- error_count=$($errorFiles.Count)"
    ""
    "## WHAT NEEDS YOUR EYES"
    "- pending_approvals=$($approvalFiles.Count)"
) + $approvalLines + @(
    ""
    "## WHAT IS QUEUED"
    "- backlog_ready_by_tier=$readyByTier"
    "- night_supervisor=$telemetryText blocked_count=$blockedCount validators=$validatorText"
    ""
    "## REPO STATE"
    "- $repoState"
    ""
    "## NEXT SAFE ACTION"
    "- $morningNextSafeAction"
    "- Rebuild command: $nextCommand"
)

if ($lines.Count -ge 100) {
    throw "Morning brief line count must stay below 100; got $($lines.Count)."
}

if ($Apply) {
    if (-not (Test-Path -LiteralPath $reportDir -PathType Container)) {
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
    }
    $lines | Set-Content -LiteralPath $briefPath -Encoding UTF8
    Write-Host "MORNING_BRIEF_WRITTEN path=$briefPath lines=$($lines.Count)"
} else {
    Write-Host "MORNING_BRIEF_PREVIEW path=$briefPath lines=$($lines.Count)"
    Write-Host "morning_evidence_status=$morningEvidenceStatus"
    Write-Host "digest_path=$digestReference"
    Write-Host "digest_freshness=$digestFreshness"
    Write-Host "next_safe_action=$morningNextSafeAction"
    $lines | Write-Output
}
