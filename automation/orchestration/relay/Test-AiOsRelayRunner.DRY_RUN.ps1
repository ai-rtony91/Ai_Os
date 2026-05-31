<#
.SYNOPSIS
Smoke-tests the AI_OS relay runner in non-mutating DRY_RUN mode.

.DESCRIPTION
Creates one temporary smoketest goal, invokes Invoke-AiOsRelayRunner.ps1 without
-Apply, verifies the expected relay tokens and transition previews appear, and
cleans up the temporary goal on exit. The test does not mutate real relay queue
items and does not stage, commit, push, schedule, or call external services.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$runnerPath = Join-Path $PSScriptRoot "Invoke-AiOsRelayRunner.ps1"
$relayRoot = Join-Path $repoRoot "relay"
$goalDir = Join-Path $relayRoot "goals"
$smokeId = "smoketest-{0}" -f (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmss")
$smokeGoalPath = Join-Path $goalDir ("_{0}.goal.txt" -f $smokeId)

$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    $failures.Add($Message) | Out-Null
}

function Get-FileSnapshot {
    param([string[]]$Paths)

    $snapshot = @{}
    foreach ($path in $Paths) {
        if (Test-Path -LiteralPath $path -PathType Container) {
            $snapshot[$path] = @(
                Get-ChildItem -LiteralPath $path -File -ErrorAction SilentlyContinue |
                    Sort-Object Name |
                    ForEach-Object { $_.Name }
            )
        } else {
            $snapshot[$path] = @()
        }
    }
    return $snapshot
}

function Compare-FileSnapshot {
    param(
        [hashtable]$Before,
        [hashtable]$After
    )

    $changes = @()
    foreach ($path in $Before.Keys) {
        $beforeText = (@($Before[$path]) -join "`n")
        $afterText = (@($After[$path]) -join "`n")
        if ($beforeText -ne $afterText) {
            $changes += $path
        }
    }
    return $changes
}

Write-Host "AI_OS Relay Runner Smoke Test"
Write-Host "Mode: DRY_RUN"
Write-Host "Runner: $runnerPath"
Write-Host "Smoke goal: $smokeGoalPath"

if (-not (Test-Path -LiteralPath $runnerPath -PathType Leaf)) {
    Add-Failure "Runner missing: $runnerPath"
}

if (-not (Test-Path -LiteralPath $goalDir -PathType Container)) {
    Add-Failure "Goal directory missing: $goalDir"
}

$watchedDirs = @(
    (Join-Path $relayRoot "approvals"),
    (Join-Path $relayRoot "handoffs"),
    (Join-Path $relayRoot "inbox"),
    (Join-Path $relayRoot "running"),
    (Join-Path $relayRoot "done"),
    (Join-Path $relayRoot "outbox"),
    (Join-Path $relayRoot "error")
)

$before = Get-FileSnapshot -Paths $watchedDirs
$output = ""

try {
    if ($failures.Count -eq 0) {
        @(
            "GOAL: Smoke test relay dry cycle."
            ""
            "Purpose: Verify the tracked relay runner previews goal-intake, handoff, packetize, inbox, running, and done transitions without mutating real queue items."
            "Safety level: GREEN (read-only smoke test, relay-only)."
            "Intended worker: Claude (analysis / plan, read-only)."
            "Expected output: relay/outbox (preview only)."
            ""
            "Relay-only task. Take no version-control action. Do not change files outside relay. Do not schedule tasks or start background services. No financial or sensitive data."
        ) | Set-Content -LiteralPath $smokeGoalPath -Encoding UTF8

        $output = (& powershell -NoProfile -ExecutionPolicy Bypass -File $runnerPath) 2>&1 | Out-String
        Write-Host ""
        Write-Host "Runner output:"
        Write-Host $output

        foreach ($token in @("[INFO] Relay start", "[GOAL] goal-intake", "[PKT] packetize", "[OK] DONE", "TIER_0_AUTO", "DryRun=True")) {
            if (-not $output.Contains($token)) {
                Add-Failure "Missing expected token: $token"
            }
        }

        foreach ($transition in @("handoffs\", "inbox\", "worker=claude")) {
            if (-not $output.Contains($transition)) {
                Add-Failure "Missing expected transition preview: $transition"
            }
        }

        if (-not $output.Contains("Commit performed: NO") -or -not $output.Contains("Push performed: NO")) {
            Add-Failure "Runner did not confirm no commit/no push."
        }
    }
}
finally {
    if (Test-Path -LiteralPath $smokeGoalPath -PathType Leaf) {
        Remove-Item -LiteralPath $smokeGoalPath -Force
    }
}

$after = Get-FileSnapshot -Paths $watchedDirs
$changedDirs = @(Compare-FileSnapshot -Before $before -After $after)
if ($changedDirs.Count -gt 0) {
    foreach ($changedDir in $changedDirs) {
        Add-Failure "Unexpected real relay queue mutation detected: $changedDir"
    }
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "SMOKE-TEST RESULT: PASS" -ForegroundColor Green
    Write-Host "Reason: expected DRY_RUN relay tokens and transition previews were observed; real relay queue directories were unchanged."
    exit 0
}

Write-Host "SMOKE-TEST RESULT: FAIL" -ForegroundColor Red
Write-Host "Reasons:"
foreach ($failure in $failures) {
    Write-Host "- $failure"
}
exit 1
