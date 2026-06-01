<#
.SYNOPSIS
Previews or writes relay resume packets from approved approval records.

.DESCRIPTION
This P3 loop-closer helper re-queues only. It never performs the approved action.
Default mode prints a mapping table and writes nothing. With -Apply, the only
write target is relay/inbox/ and only for approvals that contain an explicit,
matched origin reference.

Origin-match rule:
1. Parse approved approval records for an explicit origin reference field or line:
   origin_id, origin, source_packet, source_handoff, original_packet_id,
   original_handoff, original_task, resumes, resume_from, resumed_from.
2. Normalize the origin to a stem by removing .task.json, .handoff.json,
   .approval.json, path folders, and common prefixes.
3. Match that stem to relay/done/<stem>.task.json or
   relay/handoffs/<stem>.handoff.json or relay/handoffs/processed/<stem>.handoff.json.
4. If no explicit origin is present or no exact origin file exists, mark UNRESOLVED.

The helper intentionally does not infer origin from prose, proposed commands, or
approval filenames. Guessing would risk re-queuing the wrong protected action.
#>

[CmdletBinding()]
param(
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$relayRoot = Join-Path $repoRoot "relay"
$approvedDir = Join-Path $relayRoot "approvals\approved"
$resumedDir = Join-Path $approvedDir "resumed"
$doneDir = Join-Path $relayRoot "done"
$handoffDirs = @(
    (Join-Path $relayRoot "handoffs"),
    (Join-Path $relayRoot "handoffs\processed")
)
$inboxDir = Join-Path $relayRoot "inbox"
$runnerLogPath = Join-Path $relayRoot "logs\approval_resume.log"

$originFields = @(
    "origin_id",
    "origin",
    "source_packet",
    "source_handoff",
    "original_packet_id",
    "original_handoff",
    "original_task",
    "resumes",
    "resume_from",
    "resumed_from"
)

function ConvertTo-AiOsOriginStem {
    param([AllowNull()][object]$Value)

    if ($null -eq $Value) { return "" }
    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) { return "" }

    $leaf = Split-Path -Leaf ($text -replace "\\", "/")
    $stem = $leaf
    foreach ($suffix in @(".task.json", ".handoff.json", ".approval.json", ".json", ".md", ".txt")) {
        if ($stem.EndsWith($suffix, [System.StringComparison]::OrdinalIgnoreCase)) {
            $stem = $stem.Substring(0, $stem.Length - $suffix.Length)
            break
        }
    }
    return $stem.Trim()
}

function Read-AiOsApprovalRecord {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo]$File)

    $raw = Get-Content -LiteralPath $File.FullName -Raw
    $json = $null
    if ($File.Extension -eq ".json") {
        try {
            $json = $raw | ConvertFrom-Json
        } catch {
            $json = $null
        }
    }

    [pscustomobject]@{
        file = $File
        raw = $raw
        json = $json
    }
}

function Get-AiOsExplicitOrigin {
    param([Parameter(Mandatory = $true)]$Approval)

    if ($Approval.json) {
        foreach ($field in $originFields) {
            if ($Approval.json.PSObject.Properties.Name -contains $field) {
                $stem = ConvertTo-AiOsOriginStem -Value $Approval.json.$field
                if ($stem) { return $stem }
            }
        }

        if ($Approval.json.PSObject.Properties.Name -contains "provenance") {
            $provenance = $Approval.json.provenance
            foreach ($field in $originFields) {
                if ($provenance -and $provenance.PSObject.Properties.Name -contains $field) {
                    $stem = ConvertTo-AiOsOriginStem -Value $provenance.$field
                    if ($stem) { return $stem }
                }
            }
        }
    }

    foreach ($line in ($Approval.raw -split "\r?\n")) {
        $trimmed = $line.Trim().TrimStart("-", "*").Trim()
        if ($trimmed -match "^(origin_id|origin|source_packet|source_handoff|original_packet_id|original_handoff|original_task|resumes|resume_from|resumed_from)\s*[:=]\s*(.+)$") {
            $originValue = ($Matches[2].Trim() -replace "^[`'`"]+", "" -replace "[`'`"]+$", "")
            $stem = ConvertTo-AiOsOriginStem -Value $originValue
            if ($stem) { return $stem }
        }
    }

    return ""
}

function Find-AiOsOriginFile {
    param([Parameter(Mandatory = $true)][string]$OriginStem)

    $taskPath = Join-Path $doneDir ("{0}.task.json" -f $OriginStem)
    if (Test-Path -LiteralPath $taskPath -PathType Leaf) {
        return [pscustomobject]@{ path = $taskPath; type = "task" }
    }

    foreach ($dir in $handoffDirs) {
        $handoffPath = Join-Path $dir ("{0}.handoff.json" -f $OriginStem)
        if (Test-Path -LiteralPath $handoffPath -PathType Leaf) {
            return [pscustomobject]@{ path = $handoffPath; type = "handoff" }
        }
    }

    return $null
}

function Read-AiOsOriginPayload {
    param([Parameter(Mandatory = $true)]$Origin)

    $payload = Get-Content -LiteralPath $Origin.path -Raw | ConvertFrom-Json
    if ($Origin.type -eq "handoff") {
        return [ordered]@{
            id = [string]$payload.id
            worker = if ($payload.worker) { [string]$payload.worker } elseif ($payload.to) { [string]$payload.to } else { "UNKNOWN" }
            mode = if ($payload.mode) { [string]$payload.mode } else { "exec" }
            prompt = if ($payload.prompt) { [string]$payload.prompt } else { [string]$payload.goal }
            context = @($payload.context)
            output = if ($payload.output) { [string]$payload.output } else { "json" }
            gate_flags = [ordered]@{
                approval_required = if ($null -ne $payload.approval_required) { [bool]$payload.approval_required } else { $true }
                allowed_paths = @($payload.allowed_paths)
                forbidden_paths = @($payload.forbidden_paths)
                tier = if ($payload.tier) { [string]$payload.tier } else { "UNKNOWN" }
                stop_condition = if ($payload.stop_condition) { [string]$payload.stop_condition } else { "Review resumed packet before execution." }
            }
        }
    }

    return [ordered]@{
        id = [string]$payload.id
        worker = if ($payload.worker) { [string]$payload.worker } else { "UNKNOWN" }
        mode = if ($payload.mode) { [string]$payload.mode } else { "exec" }
        prompt = [string]$payload.prompt
        context = @($payload.context)
        output = if ($payload.output) { [string]$payload.output } else { "json" }
        gate_flags = [ordered]@{
            approval_required = $true
            allowed_paths = @()
            forbidden_paths = @("git add", "git commit", "git push", "git merge", "git reset", "git clean", "secrets", "broker", "OANDA", "live trading")
            tier = "RESUMED_APPROVAL"
            stop_condition = "Review resumed packet before execution."
        }
    }
}

function New-AiOsResumePacket {
    param(
        [Parameter(Mandatory = $true)]$Approval,
        [Parameter(Mandatory = $true)]$Origin,
        [Parameter(Mandatory = $true)]$OriginPayload
    )

    $originId = [string]$OriginPayload.id
    $resumeId = "resume-{0}" -f $originId
    [ordered]@{
        id = $resumeId
        worker = [string]$OriginPayload.worker
        mode = [string]$OriginPayload.mode
        prompt = [string]$OriginPayload.prompt
        context = @($OriginPayload.context)
        output = [string]$OriginPayload.output
        gate_flags = $OriginPayload.gate_flags
        provenance = [ordered]@{
            resumed_from_approval = $Approval.file.FullName.Substring($repoRoot.Length + 1) -replace "\\", "/"
            origin_path = $Origin.path.Substring($repoRoot.Length + 1) -replace "\\", "/"
            origin_type = $Origin.type
            origin_id = $originId
        }
        resume_only = $true
        executes_approved_action = $false
        created_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
}

function Write-AiOsApprovalResumeLog {
    param([Parameter(Mandatory = $true)][string]$Message)

    $line = "{0} {1}" -f (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $Message
    if ($Apply) {
        $logDir = Split-Path -Parent $runnerLogPath
        if (-not (Test-Path -LiteralPath $logDir -PathType Container)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }
        Add-Content -LiteralPath $runnerLogPath -Value $line
    }
    Write-Host $line
}

if (-not (Test-Path -LiteralPath $approvedDir -PathType Container)) {
    if ($Apply) {
        New-Item -ItemType Directory -Path $approvedDir -Force | Out-Null
    } else {
        Write-Host "[DRY_RUN] approved approval folder not found: $approvedDir"
    }
}

$approvalCandidates = @()
if (Test-Path -LiteralPath $approvedDir -PathType Container) {
    $approvalCandidates = @(Get-ChildItem -LiteralPath $approvedDir -File -ErrorAction SilentlyContinue)
}

$approvalFiles = @(
    $approvalCandidates |
    Where-Object { $_.Name -ne ".keep" } |
    Sort-Object Name
)

$mappings = @()
$unresolved = @()

foreach ($file in $approvalFiles) {
    $approval = Read-AiOsApprovalRecord -File $file
    $originStem = Get-AiOsExplicitOrigin -Approval $approval
    $origin = if ($originStem) { Find-AiOsOriginFile -OriginStem $originStem } else { $null }

    if (-not $origin) {
        $reason = if ($originStem) { "origin not found: $originStem" } else { "missing explicit origin reference" }
        $row = [pscustomobject]@{
            approval = $file.Name
            origin = if ($originStem) { $originStem } else { "UNRESOLVED" }
            resume_target = "NONE"
            status = "UNRESOLVED"
            reason = $reason
        }
        $mappings += $row
        $unresolved += $row
        continue
    }

    $originPayload = Read-AiOsOriginPayload -Origin $origin
    $resumePacket = New-AiOsResumePacket -Approval $approval -Origin $origin -OriginPayload $originPayload
    $resumeTarget = Join-Path $inboxDir ("{0}.task.json" -f $resumePacket.id)
    $resumedTarget = Join-Path $resumedDir $file.Name
    $alreadyResumed = (Test-Path -LiteralPath $resumeTarget -PathType Leaf) -or (Test-Path -LiteralPath $resumedTarget -PathType Leaf)

    $mappings += [pscustomobject]@{
        approval = $file.Name
        origin = $origin.path.Substring($repoRoot.Length + 1) -replace "\\", "/"
        resume_target = $resumeTarget.Substring($repoRoot.Length + 1) -replace "\\", "/"
        status = if ($alreadyResumed) { "ALREADY_RESUMED" } else { "MATCHED" }
        reason = if ($alreadyResumed) { "resume target or resumed approval already exists" } else { "explicit origin matched" }
    }

    if ($Apply -and -not $alreadyResumed) {
        if (-not (Test-Path -LiteralPath $inboxDir -PathType Container)) {
            New-Item -ItemType Directory -Path $inboxDir -Force | Out-Null
        }
        if (-not (Test-Path -LiteralPath $resumedDir -PathType Container)) {
            New-Item -ItemType Directory -Path $resumedDir -Force | Out-Null
        }
        $resumePacket | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $resumeTarget -Encoding UTF8
        Move-Item -LiteralPath $file.FullName -Destination $resumedTarget
        Write-AiOsApprovalResumeLog -Message ("RESUMED approval={0} origin={1} target={2}" -f $file.Name, $originPayload.id, ($resumeTarget.Substring($repoRoot.Length + 1) -replace "\\", "/"))
    }
}

Write-Host "AI_OS Approved Action Resume"
Write-Host ("Mode: {0}" -f $(if ($Apply) { "APPLY" } else { "DRY_RUN" }))
Write-Host "Cardinal limit: re-queues only; approved actions are never executed."
Write-Host ""
Write-Host "MAPPING TABLE"
if ($mappings.Count -eq 0) {
    Write-Host "No approved approval files found."
} else {
    $mappings | Format-Table approval, origin, resume_target, status, reason -AutoSize | Out-String | Write-Host
}

Write-Host "UNRESOLVED"
if ($unresolved.Count -eq 0) {
    Write-Host "None"
} else {
    $unresolved | ForEach-Object { Write-Host ("- {0}: {1}" -f $_.approval, $_.reason) }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"

if ($unresolved.Count -gt 0) {
    exit 2
}
