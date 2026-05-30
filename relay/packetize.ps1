#requires -Version 7.0
<#
==============================================================================
 AI_OS RELAY PACKETIZER  (handoff -> inbox task)
 The missing connection: a Claude-produced handoff packet becomes a Codex
 task with NO manual copy/paste. Can run standalone OR be dot-sourced by
 relay-runner.ps1 (which calls Invoke-Packetize before each inbox pass).
 Scope: reads relay\handoffs\, writes relay\inbox\, moves processed handoffs
        to relay\handoffs\processed\. Nothing outside relay\.
==============================================================================
#>
[CmdletBinding()]
param([switch]$Apply)   # standalone: without -Apply, preview only

function Invoke-Packetize {
    param(
        [string]$Root = $PSScriptRoot,
        [switch]$Apply,
        [scriptblock]$Logger
    )
    $Handoffs  = Join-Path $Root 'handoffs'
    $Inbox     = Join-Path $Root 'inbox'
    $Processed = Join-Path $Handoffs 'processed'
    foreach ($d in @($Handoffs,$Inbox,$Processed)) {
        if (-not (Test-Path $d)) { New-Item -ItemType Directory $d | Out-Null }
    }
    function emit($m) { if ($Logger) { & $Logger $m } else { Write-Host $m } }

    $packets = Get-ChildItem $Handoffs -File -Filter *.handoff.json -EA SilentlyContinue
    if (-not $packets) { emit "packetize: no pending handoffs"; return 0 }

    $count = 0
    foreach ($p in $packets) {
        try { $h = Get-Content $p.FullName -Raw | ConvertFrom-Json }
        catch { emit "packetize SKIP (bad JSON): $($p.Name)"; continue }

        if ($h.packet -ne 'handoff' -or [string]::IsNullOrWhiteSpace($h.prompt)) {
            emit "packetize SKIP (not a valid handoff): $($p.Name)"; continue
        }

        $task = [ordered]@{
            id      = $h.id
            worker  = if ($h.to) { $h.to } else { 'codex' }
            mode    = if ($h.mode) { $h.mode } else { 'exec' }
            prompt  = $h.prompt
            context = if ($h.context) { @($h.context) } else { @() }
            output  = 'json'
        }
        $dest = Join-Path $Inbox ("$($h.id).task.json")
        if (Test-Path $dest) { emit "packetize EXISTS (skip): inbox\$($h.id).task.json"; continue }

        if ($Apply) {
            ($task | ConvertTo-Json -Depth 6) | Out-File $dest -Encoding utf8
            # move handoff aside so it is not re-packetized next pass
            Move-Item $p.FullName (Join-Path $Processed $p.Name) -Force
            emit "packetize: $($p.Name) -> inbox\$($h.id).task.json (worker=$($task.worker))"
            $count++
        } else {
            emit "packetize WOULD: $($p.Name) -> inbox\$($h.id).task.json (worker=$($task.worker))"
        }
    }
    return $count
}

# Standalone execution (not dot-sourced)
if ($MyInvocation.InvocationName -ne '.') {
    $n = Invoke-Packetize -Root $PSScriptRoot -Apply:$Apply
    Write-Host "Done. Packetized=$n (Apply=$Apply)"
}
