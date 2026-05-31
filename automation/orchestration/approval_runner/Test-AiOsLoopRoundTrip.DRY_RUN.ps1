<#
.SYNOPSIS
Proves the relay approval -> resume -> runner loop with sample artifacts only.

.DESCRIPTION
Seeds one clearly labeled _roundtrip origin task and approval record, runs the
P3 resume helper with -Apply, runs the P1 relay runner with -Apply, verifies the
sample resume packet reaches relay/done, and cleans up all _roundtrip artifacts
on exit. This test never executes an approved action; it only proves re-queue
and relay movement.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$relayRoot = Join-Path $repoRoot "relay"
$p3Runner = Join-Path $PSScriptRoot "Invoke-AiOsApprovedActionResume.DRY_RUN.ps1"
$p1Runner = Join-Path $repoRoot "automation\orchestration\relay\Invoke-AiOsRelayRunner.ps1"

$originId = "_roundtrip-origin"
$resumeId = "resume-$originId"
$originPath = Join-Path $relayRoot "done\$originId.task.json"
$approvalPath = Join-Path $relayRoot "approvals\approved\_roundtrip.approval.json"
$resumeInboxPath = Join-Path $relayRoot "inbox\$resumeId.task.json"
$resumeRunningPath = Join-Path $relayRoot "running\$resumeId.task.json"
$resumeDonePath = Join-Path $relayRoot "done\$resumeId.task.json"
$resumeReportPath = Join-Path $relayRoot "outbox\$resumeId.report.txt"
$trace = New-Object System.Collections.Generic.List[string]
$failures = New-Object System.Collections.Generic.List[string]

function Add-Trace {
    param([string]$Message)
    $trace.Add($Message) | Out-Null
    Write-Host $Message
}

function Add-Failure {
    param([string]$Message)
    $failures.Add($Message) | Out-Null
    Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Remove-RoundTripArtifacts {
    foreach ($path in @($originPath, $approvalPath, $resumeInboxPath, $resumeRunningPath, $resumeDonePath, $resumeReportPath)) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            Remove-Item -LiteralPath $path -Force
        }
    }
}

Write-Host "AI_OS Loop Round-Trip Test"
Write-Host "Mode: DRY_RUN test harness with sample-only APPLY calls"
Write-Host "P3: $p3Runner"
Write-Host "P1: $p1Runner"
Write-Host ""

if (-not (Test-Path -LiteralPath $p3Runner -PathType Leaf)) {
    Add-Failure "P3 resume helper missing: $p3Runner"
}
if (-not (Test-Path -LiteralPath $p1Runner -PathType Leaf)) {
    Add-Failure "P1 relay runner missing: $p1Runner"
}

try {
    Remove-RoundTripArtifacts

    if ($failures.Count -eq 0) {
        $origin = [ordered]@{
            id = $originId
            worker = "codex"
            mode = "exec"
            prompt = "ROUNDTRIP SAMPLE ONLY. Reply with ROUNDTRIP OK. Do not modify files."
            context = @()
            output = "json"
            gate_flags = [ordered]@{
                approval_required = $true
                allowed_paths = @("relay/")
                forbidden_paths = @("git add", "git commit", "git push", "git merge", "git reset", "git clean", "secrets", "broker", "OANDA", "live trading")
                tier = "ROUNDTRIP_SAMPLE"
                stop_condition = "Sample reaches relay/done."
            }
        }
        $origin | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $originPath -Encoding UTF8
        Add-Trace "SEEDED origin: relay/done/$originId.task.json"

        $approval = [ordered]@{
            packet = "approval"
            id = "_roundtrip-approval"
            status = "APPROVED"
            origin_id = $originId
            risk = "SAMPLE_ONLY"
            reason = "Round-trip sample approval for P3.5 test."
            proposed = "Requeue sample origin only."
            approved_by_human = $true
            created_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
        $approval | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $approvalPath -Encoding UTF8
        Add-Trace "SEEDED approval: relay/approvals/approved/_roundtrip.approval.json"

        $p3Output = (& powershell -NoProfile -ExecutionPolicy Bypass -File $p3Runner -Apply) 2>&1 | Out-String
        Add-Trace "P3 OUTPUT BEGIN"
        Add-Trace $p3Output.Trim()
        Add-Trace "P3 OUTPUT END"

        if (-not (Test-Path -LiteralPath $resumeInboxPath -PathType Leaf)) {
            Add-Failure "P3 did not write sample resume packet to relay/inbox."
        } else {
            Add-Trace "P3 WROTE resume packet: relay/inbox/$resumeId.task.json"
        }

        if ($failures.Count -eq 0) {
            $p1Output = (& powershell -NoProfile -ExecutionPolicy Bypass -File $p1Runner -Apply) 2>&1 | Out-String
            Add-Trace "P1 OUTPUT BEGIN"
            Add-Trace $p1Output.Trim()
            Add-Trace "P1 OUTPUT END"

            if (Test-Path -LiteralPath $resumeDonePath -PathType Leaf) {
                Add-Trace "P1 MOVED resume packet: relay/inbox -> relay/running -> relay/done"
            } else {
                Add-Failure "P1 did not leave sample resume packet in relay/done."
            }

            if (-not $p1Output.Contains("[OK] DONE $resumeId")) {
                Add-Failure "P1 output did not include expected DONE token for $resumeId."
            }
        }
    }
}
finally {
    Remove-RoundTripArtifacts
    Add-Trace "CLEANUP complete for _roundtrip sample artifacts."
}

Write-Host ""
Write-Host "ROUND-TRIP TRACE:"
foreach ($line in $trace) {
    Write-Host $line
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "RESULT: PASS" -ForegroundColor Green
    Write-Host 'LOOP STATUS: "U"->"O" confirmed for sample approval path.'
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    exit 0
}

Write-Host "RESULT: FAIL" -ForegroundColor Red
Write-Host "Failures:"
foreach ($failure in $failures) {
    Write-Host "- $failure"
}
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
exit 1
