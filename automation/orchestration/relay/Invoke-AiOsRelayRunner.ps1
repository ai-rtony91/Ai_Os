<#
.SYNOPSIS
Runs one local AI_OS relay cycle.

.DESCRIPTION
P1 rebuild of the missing relay runner. This script is intentionally local and
file-based. It reads goal files from relay/goals, converts safe goals into
handoffs, converts handoffs into relay/inbox task packets, simulates worker
completion by writing local stub reports, and moves completed task packets into
relay/done.

PURPOSE
- Restore the tracked relay driver described by AIOS-P1.
- Preserve the observed relay flow from relay/logs/runner.log:
  goal-intake -> handoffs/approvals -> packetize -> inbox -> running -> done.

INPUTS
- relay/goals/*.goal.txt
- relay/handoffs/*.handoff.json
- relay/inbox/*.task.json

OUTPUTS
- relay/logs/runner.log
- relay/handoffs/*.handoff.json and relay/handoffs/processed/*.handoff.json
- relay/approvals/*.approval.json for protected or high-risk goals
- relay/inbox/*.task.json
- relay/running/*.task.json while a local stub task is active
- relay/outbox/*.report.txt
- relay/done/*.task.json
- relay/error/*.task.txt on malformed packets

TIERS
- TIER_0_AUTO: read-only relay inspection, review, and summary goals.
- TIER_1_LOW_RISK: bounded implementation/planning goals without protected terms.
- TIER_2_HUMAN_REQUIRED: commit, push, merge, reset, clean, delete, scheduled task,
  secret, broker, OANDA, webhook, or live trading requests.

GATE
- This runner never stages, commits, pushes, merges, resets, cleans, creates a
  scheduled task, accesses secrets, calls a broker, or places trades.
- TIER_2 requests are routed to relay/approvals and are not packetized.
#>

[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Watch,
    [switch]$Report,
    [ValidateRange(1, 3600)]
    [int]$IntervalSeconds = 2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$RelayRoot = Join-Path $RepoRoot "relay"
$CanWrite = [bool]$Apply
$script:DryRunPlannedTasks = @()

$RelayPaths = [ordered]@{
    approvals = Join-Path $RelayRoot "approvals"
    approved = Join-Path $RelayRoot "approvals\approved"
    rejected = Join-Path $RelayRoot "approvals\rejected"
    done = Join-Path $RelayRoot "done"
    error = Join-Path $RelayRoot "error"
    goals = Join-Path $RelayRoot "goals"
    goalsProcessed = Join-Path $RelayRoot "goals\processed"
    handoffs = Join-Path $RelayRoot "handoffs"
    handoffsProcessed = Join-Path $RelayRoot "handoffs\processed"
    inbox = Join-Path $RelayRoot "inbox"
    logs = Join-Path $RelayRoot "logs"
    outbox = Join-Path $RelayRoot "outbox"
    reports = Join-Path $RelayRoot "reports"
    running = Join-Path $RelayRoot "running"
}

$RunnerLogPath = Join-Path $RelayPaths.logs "runner.log"

function Get-AiOsUtcTimestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Get-AiOsSafeSlug {
    param([Parameter(Mandatory = $true)][string]$Value)

    $base = $Value
    if ($base -match "(?im)^\s*GOAL\s*:\s*(.+)$") {
        $base = $Matches[1]
    }

    $slug = ($base.ToLowerInvariant() -replace "[^a-z0-9]+", "-").Trim("-")
    if ([string]::IsNullOrWhiteSpace($slug)) {
        $slug = "relay-item"
    }

    if ($slug.Length -gt 44) {
        $slug = $slug.Substring(0, 44).Trim("-")
    }

    return $slug
}

function Initialize-AiOsRelayFolders {
    foreach ($path in $RelayPaths.Values) {
        if (-not (Test-Path -LiteralPath $path -PathType Container)) {
            if ($CanWrite) {
                New-Item -ItemType Directory -Path $path -Force | Out-Null
            } else {
                Write-Host "[DRY_RUN] would create missing relay folder: $path"
            }
        }
    }
}

function Write-AiOsRelayLog {
    param([Parameter(Mandatory = $true)][string]$Message)

    $line = "{0} {1}" -f (Get-AiOsUtcTimestamp), $Message
    if ($CanWrite) {
        Add-Content -LiteralPath $RunnerLogPath -Value $line -Encoding UTF8
    }
    Write-Host $line
}

function Test-AiOsProtectedRelayText {
    param([Parameter(Mandatory = $true)][string]$Text)

    return $Text -match "(?i)\b(git\s+add|git\s+commit|git\s+push|git\s+merge|git\s+reset|git\s+clean|commit|push|merge|reset|clean|delete|remove-item|scheduled task|schtasks|service|secret|\.env|api key|credential|broker|oanda|webhook|live trading|real order)\b"
}

function Get-AiOsRelayTier {
    param([Parameter(Mandatory = $true)][string]$Text)

    if (Test-AiOsProtectedRelayText -Text $Text) {
        return "TIER_2_HUMAN_REQUIRED"
    }

    if ($Text -match "(?i)\b(green|read-only|read only|inspect|review|summarize|summary|list|report|analysis only|plan only)\b") {
        return "TIER_0_AUTO"
    }

    return "TIER_1_LOW_RISK"
}

function Get-AiOsGoalTitle {
    param([Parameter(Mandatory = $true)][string]$Text)

    if ($Text -match "(?im)^\s*GOAL\s*:\s*(.+)$") {
        return $Matches[1].Trim()
    }

    $firstLine = (($Text -split "\r?\n") | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
    if ($firstLine) {
        return ([string]$firstLine).Trim()
    }

    return "Relay goal"
}

function New-AiOsApprovalPacket {
    param(
        [Parameter(Mandatory = $true)][string]$GoalText,
        [Parameter(Mandatory = $true)][string]$Slug
    )

    $approvalPath = Join-Path $RelayPaths.approvals ("g-{0}.approval.json" -f $Slug)
    $approval = [ordered]@{
        packet = "approval"
        id = "g-$Slug"
        raised_by = "relay"
        risk = "HIGH"
        tier = "TIER_2_HUMAN_REQUIRED"
        reason = "Goal requested a protected action or protected domain. Relay stopped before worker packet creation."
        proposed = $GoalText
        needs = "Human Owner approval before any APPLY or protected action."
        status = "WAITING"
        created_utc = Get-AiOsUtcTimestamp
    }

    $approval | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $approvalPath -Encoding UTF8
    return $approvalPath
}

function New-AiOsHandoffPacket {
    param(
        [Parameter(Mandatory = $true)][string]$GoalText,
        [Parameter(Mandatory = $true)][string]$Slug,
        [Parameter(Mandatory = $true)][ValidateSet("plan","build")][string]$Kind,
        [Parameter(Mandatory = $true)][string]$Tier
    )

    $worker = if ($Kind -eq "plan") { "claude" } else { "codex" }
    $handoffPath = Join-Path $RelayPaths.handoffs ("g-{0}-{1}.handoff.json" -f $Slug, $Kind)
    $prompt = if ($Kind -eq "plan") {
        "Review this AI_OS relay goal and produce a concise DRY_RUN plan only: `"$GoalText`". Do not modify files. Report risks, allowed paths, validation, and next safe action."
    } else {
        "Implement this goal under AI_OS rules (DRY_RUN before APPLY, smallest safe change): `"$GoalText`". Follow the Claude plan for lane g-$Slug if present. Report files created/changed, validation, and next safe action."
    }

    $handoff = [ordered]@{
        packet = "handoff"
        id = "g-{0}-{1}" -f $Slug, $Kind
        from = "relay"
        to = $worker
        worker = $worker
        mode = "exec"
        lane = "g-$Slug"
        tier = $Tier
        allowed_paths = @("relay/")
        forbidden_paths = @("git add", "git commit", "git push", "git merge", "git reset", "git clean", "secrets", "broker", "OANDA", "live trading")
        goal = $GoalText
        prompt = $prompt
        context = @()
        output = if ($worker -eq "codex") { "json" } else { "text" }
        stop_condition = "When relay/outbox/g-$Slug-$Kind.report.txt exists."
        approval_required = $false
        created_utc = Get-AiOsUtcTimestamp
    }

    $handoff | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $handoffPath -Encoding UTF8
    return $handoffPath
}

function Add-AiOsDryRunPlannedTask {
    param(
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Worker,
        [Parameter(Mandatory = $true)][string]$HandoffName,
        [Parameter(Mandatory = $true)][string]$TaskName
    )

    $existing = @($script:DryRunPlannedTasks | Where-Object { $_.id -eq $Id })
    if ($existing.Count -eq 0) {
        $script:DryRunPlannedTasks += [pscustomobject]@{
            id = $Id
            worker = $Worker
            handoff_name = $HandoffName
            task_name = $TaskName
        }
    }
}

function Invoke-AiOsGoalIntake {
    $goalFiles = @(Get-ChildItem -LiteralPath $RelayPaths.goals -File -Filter "*.goal.txt" -ErrorAction SilentlyContinue | Sort-Object Name)
    if ($goalFiles.Count -eq 0) {
        return 0
    }

    $count = 0
    foreach ($goalFile in $goalFiles) {
        $goalText = Get-Content -LiteralPath $goalFile.FullName -Raw
        $title = Get-AiOsGoalTitle -Text $goalText
        $slug = Get-AiOsSafeSlug -Value $title
        $tier = Get-AiOsRelayTier -Text $goalText

        if ($tier -eq "TIER_2_HUMAN_REQUIRED") {
            Write-AiOsRelayLog "[GOAL] goal-intake GOAL: '$title' -> HUMAN (blocked) [$tier]"
            if ($CanWrite) {
                $approvalPath = New-AiOsApprovalPacket -GoalText $goalText -Slug $slug
                Write-AiOsRelayLog ("[GOAL] goal-intake -> approvals\{0} (no worker packet)" -f (Split-Path -Leaf $approvalPath))
            } else {
                Write-AiOsRelayLog ("[GOAL] goal-intake -> approvals\g-{0}.approval.json (no worker packet) [DRY_RUN]" -f $slug)
            }
        } elseif ($tier -eq "TIER_0_AUTO") {
            Write-AiOsRelayLog "[GOAL] goal-intake GOAL: '$title' -> Claude (plan only) [$tier]"
            if ($CanWrite) {
                $handoffPath = New-AiOsHandoffPacket -GoalText $goalText -Slug $slug -Kind "plan" -Tier $tier
                Write-AiOsRelayLog ("[GOAL] goal-intake -> handoffs\{0}" -f (Split-Path -Leaf $handoffPath))
            } else {
                $id = "g-{0}-plan" -f $slug
                Add-AiOsDryRunPlannedTask -Id $id -Worker "claude" -HandoffName "$id.handoff.json" -TaskName "$id.task.json"
                Write-AiOsRelayLog ("[GOAL] goal-intake -> handoffs\{0}.handoff.json [DRY_RUN]" -f $id)
            }
        } else {
            Write-AiOsRelayLog "[GOAL] goal-intake GOAL: '$title' -> Claude (plan) + Codex (build) [$tier]"
            if ($CanWrite) {
                $planPath = New-AiOsHandoffPacket -GoalText $goalText -Slug $slug -Kind "plan" -Tier $tier
                $buildPath = New-AiOsHandoffPacket -GoalText $goalText -Slug $slug -Kind "build" -Tier $tier
                Write-AiOsRelayLog ("[GOAL] goal-intake -> handoffs\{0}" -f (Split-Path -Leaf $planPath))
                Write-AiOsRelayLog ("[GOAL] goal-intake -> handoffs\{0}" -f (Split-Path -Leaf $buildPath))
            } else {
                $planId = "g-{0}-plan" -f $slug
                $buildId = "g-{0}-build" -f $slug
                Add-AiOsDryRunPlannedTask -Id $planId -Worker "claude" -HandoffName "$planId.handoff.json" -TaskName "$planId.task.json"
                Add-AiOsDryRunPlannedTask -Id $buildId -Worker "codex" -HandoffName "$buildId.handoff.json" -TaskName "$buildId.task.json"
                Write-AiOsRelayLog ("[GOAL] goal-intake -> handoffs\{0}.handoff.json [DRY_RUN]" -f $planId)
                Write-AiOsRelayLog ("[GOAL] goal-intake -> handoffs\{0}.handoff.json [DRY_RUN]" -f $buildId)
            }
        }

        if ($CanWrite) {
            Move-Item -LiteralPath $goalFile.FullName -Destination (Join-Path $RelayPaths.goalsProcessed $goalFile.Name) -Force
        }
        $count++
    }

    Write-AiOsRelayLog "[OK] intook $count goal(s) into handoffs/approvals"
    return $count
}

function Convert-AiOsHandoffToTask {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo]$HandoffFile)

    try {
        $handoff = Get-Content -LiteralPath $HandoffFile.FullName -Raw | ConvertFrom-Json
        $id = if ($handoff.id) { [string]$handoff.id } else { [IO.Path]::GetFileNameWithoutExtension($HandoffFile.Name) -replace "\.handoff$", "" }
        $worker = if ($handoff.worker) { [string]$handoff.worker } elseif ($handoff.to) { [string]$handoff.to } else { "codex" }
        $taskPath = Join-Path $RelayPaths.inbox ("{0}.task.json" -f $id)

        $task = [ordered]@{
            id = $id
            worker = $worker
            mode = if ($handoff.mode) { [string]$handoff.mode } else { "exec" }
            prompt = if ($handoff.prompt) { [string]$handoff.prompt } else { [string]$handoff.goal }
            context = @($handoff.context)
            output = if ($handoff.output) { [string]$handoff.output } else { "text" }
            tier = if ($handoff.tier) { [string]$handoff.tier } else { "UNKNOWN" }
            source_handoff = $HandoffFile.Name
            created_utc = Get-AiOsUtcTimestamp
        }

        if ($CanWrite) {
            $task | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $taskPath -Encoding UTF8
            Move-Item -LiteralPath $HandoffFile.FullName -Destination (Join-Path $RelayPaths.handoffsProcessed $HandoffFile.Name) -Force
        } else {
            Add-AiOsDryRunPlannedTask -Id $id -Worker $worker -HandoffName $HandoffFile.Name -TaskName (Split-Path -Leaf $taskPath)
        }
        Write-AiOsRelayLog ("[PKT] packetize: {0} -> inbox\{1} (worker={2})" -f $HandoffFile.Name, (Split-Path -Leaf $taskPath), $worker)
        return $true
    }
    catch {
        $errorPath = Join-Path $RelayPaths.error ("{0}.task.txt" -f ([IO.Path]::GetFileNameWithoutExtension($HandoffFile.Name)))
        if ($CanWrite) {
            "Failed to packetize $($HandoffFile.Name): $($_.Exception.Message)" | Set-Content -LiteralPath $errorPath -Encoding UTF8
        }
        Write-AiOsRelayLog "[ERR] packetize failed: $($HandoffFile.Name) -> error\$(Split-Path -Leaf $errorPath)"
        return $false
    }
}

function Invoke-AiOsPacketize {
    $handoffFiles = @(Get-ChildItem -LiteralPath $RelayPaths.handoffs -File -Filter "*.handoff.json" -ErrorAction SilentlyContinue | Sort-Object Name)
    if ($handoffFiles.Count -eq 0 -and $script:DryRunPlannedTasks.Count -eq 0) {
        Write-AiOsRelayLog "[PKT] packetize: no pending handoffs"
        return 0
    }

    $count = 0
    foreach ($handoffFile in $handoffFiles) {
        if (Convert-AiOsHandoffToTask -HandoffFile $handoffFile) {
            $count++
        }
    }

    if (-not $CanWrite -and $handoffFiles.Count -eq 0) {
        foreach ($plannedTask in $script:DryRunPlannedTasks) {
            Write-AiOsRelayLog ("[PKT] packetize: {0} -> inbox\{1} (worker={2}) [DRY_RUN]" -f $plannedTask.handoff_name, $plannedTask.task_name, $plannedTask.worker)
            $count++
        }
    }

    Write-AiOsRelayLog "[OK] packetized $count handoff(s) into inbox"
    return $count
}

function Complete-AiOsRelayTask {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo]$TaskFile)

    $started = Get-Date
    $runningPath = Join-Path $RelayPaths.running $TaskFile.Name
    if ($CanWrite) {
        Move-Item -LiteralPath $TaskFile.FullName -Destination $runningPath -Force
    } else {
        $runningPath = $TaskFile.FullName
    }

    try {
        $task = Get-Content -LiteralPath $runningPath -Raw | ConvertFrom-Json
        $id = if ($task.id) { [string]$task.id } else { [IO.Path]::GetFileNameWithoutExtension($TaskFile.Name) -replace "\.task$", "" }
        $worker = if ($task.worker) { [string]$task.worker } else { "unknown" }
        $reportPath = Join-Path $RelayPaths.outbox ("{0}.report.txt" -f $id)

        if ($CanWrite) {
            @(
                "[DRY_RUN STUB] task=$id worker=$worker"
                "No model was called. Plumbing test only."
                ("Prompt length: {0} chars." -f ([string]$task.prompt).Length)
            ) | Set-Content -LiteralPath $reportPath -Encoding UTF8

            Move-Item -LiteralPath $runningPath -Destination (Join-Path $RelayPaths.done $TaskFile.Name) -Force
        }
        $elapsed = [int]((Get-Date) - $started).TotalSeconds
        Write-AiOsRelayLog "[OK] DONE $id worker=$worker ${elapsed}s"
    }
    catch {
        $errorPath = Join-Path $RelayPaths.error ("{0}.task.txt" -f ([IO.Path]::GetFileNameWithoutExtension($TaskFile.Name)))
        if ($CanWrite) {
            "Failed to complete $($TaskFile.Name): $($_.Exception.Message)" | Set-Content -LiteralPath $errorPath -Encoding UTF8
            Move-Item -LiteralPath $runningPath -Destination (Join-Path $RelayPaths.error $TaskFile.Name) -Force
        }
        Write-AiOsRelayLog "[ERR] DONE failed: $($TaskFile.Name) -> error\$(Split-Path -Leaf $errorPath)"
    }
}

function Invoke-AiOsInboxDrain {
    $taskFiles = @(Get-ChildItem -LiteralPath $RelayPaths.inbox -File -Filter "*.task.json" -ErrorAction SilentlyContinue | Sort-Object Name)
    foreach ($taskFile in $taskFiles) {
        Complete-AiOsRelayTask -TaskFile $taskFile
    }

    if (-not $CanWrite -and $taskFiles.Count -eq 0) {
        foreach ($plannedTask in $script:DryRunPlannedTasks) {
            Write-AiOsRelayLog ("[OK] DONE {0} worker={1} 0s [DRY_RUN]" -f $plannedTask.id, $plannedTask.worker)
        }
        return $script:DryRunPlannedTasks.Count
    }

    return $taskFiles.Count
}

function Invoke-AiOsRelayPass {
    Write-AiOsRelayLog ("[INFO] Relay start. DryRun={0} Watch={1} Report={2}" -f (-not $Apply), [bool]$Watch, [bool]$Report)
    [void](Invoke-AiOsGoalIntake)
    [void](Invoke-AiOsPacketize)
    [void](Invoke-AiOsInboxDrain)
    Write-AiOsRelayLog "[INFO] Single pass complete."
}

Initialize-AiOsRelayFolders

do {
    Invoke-AiOsRelayPass
    if ($Watch) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while ($Watch)

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
