#requires -Version 7.0
<#
==============================================================================
 AI_OS RELAY RUNNER  (Mailroom Layer 3.5)
 Owner: Anthony Meza
 Purpose: file-based transport between ChatGPT / Claude / Codex / terminal.
          Drop a task file in inbox\, get a report in outbox\, no copy/paste.
 Safety:  DRY_RUN default TRUE. No model is called until you flip it.
          Scope is confined to relay\. This script never touches the repo
          outside relay\, never commits, never pushes, never deletes source.
==============================================================================
#>
[CmdletBinding()]
param(
    [switch]$Watch,      # follow inbox\ and process files as they land
    [switch]$Report,     # write today's roll-up summary and exit
    [switch]$Live        # turn OFF DryRun for this run (real CLI calls)
)

# ---------------------------------------------------------------------------
# 0. CONFIG  (everything tunable lives here)
# ---------------------------------------------------------------------------
$Config = [ordered]@{
    Root        = $PSScriptRoot
    DryRun      = (-not $Live)          # default TRUE
    TimeoutSec  = 600
    CodexModel  = 'codex'              # CLI name on PATH
    ClaudeModel = 'claude'            # CLI name on PATH
    StableMs    = 1000                # debounce: file size stable this long
}

$Dirs = [ordered]@{
    inbox     = Join-Path $Config.Root 'inbox'
    running   = Join-Path $Config.Root 'running'
    outbox    = Join-Path $Config.Root 'outbox'
    done      = Join-Path $Config.Root 'done'
    error     = Join-Path $Config.Root 'error'
    reports   = Join-Path $Config.Root 'reports'
    logs      = Join-Path $Config.Root 'logs'
    approvals = Join-Path $Config.Root 'approvals'
    handoffs  = Join-Path $Config.Root 'handoffs'
    packets   = Join-Path $Config.Root 'packets'
}

# Bring in the packetizer (handoff -> inbox task) as a function.
. (Join-Path $Config.Root 'packetize.ps1')

# Ultimate blockers: any task containing these stops and creates an approval.
$BlockerWords = @(
    'trade','order','buy','sell','live trade','position','execution',
    'broker','oanda','api key','apikey','secret','credential','merge',
    'rebase','git push','git commit','delete '
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
function Initialize-Tree {
    foreach ($d in $Dirs.Values) {
        if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
    }
}

function Write-Log {
    param([string]$Msg, [string]$Level = 'INFO')
    $ts = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $line = "$ts [$Level] $Msg"
    $line | Out-File -FilePath (Join-Path $Dirs.logs 'runner.log') -Append -Encoding utf8
    Write-Host $line
}

function Test-Stable {
    param([string]$Path)
    try {
        $a = (Get-Item $Path).Length
        Start-Sleep -Milliseconds $Config.StableMs
        $b = (Get-Item $Path).Length
        return ($a -eq $b)
    } catch { return $false }
}

function Get-BlockerHit {
    param([string]$Text)
    $low = $Text.ToLowerInvariant()
    foreach ($w in $BlockerWords) { if ($low.Contains($w)) { return $w } }
    return $null
}

function New-ApprovalItem {
    param([string]$TaskId, [string]$Reason, [string]$Proposed, [string]$Risk)
    $stamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
    $f = Join-Path $Dirs.approvals "$stamp-$TaskId.approval.md"
    @"
# APPROVAL REQUIRED — $TaskId

**Created (UTC):** $([DateTime]::UtcNow.ToString('u'))
**Risk level:** $Risk
**Status:** WAITING

## Reason (plain English)
$Reason

## Proposed command / change
``````
$Proposed
``````

## What Anthony must approve
Review the above. To allow it, move this file to approvals\approved\ and
re-run the relay. To reject, move it to approvals\rejected\.
"@ | Out-File -FilePath $f -Encoding utf8
    Write-Log "APPROVAL created: $f" 'BLOCK'
    return $f
}

# ---------------------------------------------------------------------------
# task parsing
# ---------------------------------------------------------------------------
function Read-Task {
    param([System.IO.FileInfo]$File)
    $id     = $File.BaseName -replace '\.(task)$',''
    $worker = 'codex'; $mode = ''; $output = 'text'; $prompt = ''; $context = @()

    if ($File.Extension -eq '.json' -or $File.Name -like '*.task.json') {
        $j = Get-Content $File.FullName -Raw | ConvertFrom-Json
        if ($j.id)      { $id = $j.id }
        if ($j.worker)  { $worker = $j.worker }
        if ($j.mode)    { $mode = $j.mode }
        if ($j.output)  { $output = $j.output }
        if ($j.prompt)  { $prompt = $j.prompt }
        if ($j.context) { $context = $j.context }
    } else {
        $prompt = Get-Content $File.FullName -Raw
        if ($File.Name -like 'claude-*') { $worker = 'claude' }
    }
    [pscustomobject]@{
        Id=$id; Worker=$worker; Mode=$mode; Output=$output
        Prompt=$prompt; Context=$context; File=$File
    }
}

function Expand-Context {
    param([string]$Prompt, [string[]]$Context)
    if (-not $Context) { return $Prompt }
    $sb = [System.Text.StringBuilder]::new($Prompt)
    foreach ($c in $Context) {
        [void]$sb.AppendLine("`n`n----- CONTEXT FILE: $c -----")
        if (Test-Path $c) { [void]$sb.AppendLine((Get-Content $c -Raw)) }
        else { [void]$sb.AppendLine("[missing: $c]") }
    }
    return $sb.ToString()
}

# ---------------------------------------------------------------------------
# dispatch one task
# ---------------------------------------------------------------------------
function Invoke-Task {
    param([System.IO.FileInfo]$File)

    $task = Read-Task -File $File
    $id   = $task.Id

    # 1. validate
    if ([string]::IsNullOrWhiteSpace($task.Prompt)) {
        $dest = Join-Path $Dirs.error $File.Name
        Move-Item $File.FullName $dest -Force
        "Empty/invalid task." | Out-File (Join-Path $Dirs.error "$id.error.txt") -Encoding utf8
        Write-Log "INVALID task $id -> error\" 'WARN'
        return
    }

    # 2. blocker scan -> approval, do NOT run
    $hit = Get-BlockerHit -Text $task.Prompt
    if ($hit) {
        $dest = Join-Path $Dirs.error $File.Name
        Move-Item $File.FullName $dest -Force
        New-ApprovalItem -TaskId $id `
            -Reason "Task contains blocker keyword '$hit'. Stopped before any execution." `
            -Proposed $task.Prompt -Risk 'HIGH — requires human sign-off' | Out-Null
        Write-Log "BLOCKED task $id ('$hit') -> error\ + approval" 'BLOCK'
        return
    }

    # 3. move to running\
    $running = Join-Path $Dirs.running $File.Name
    Move-Item $File.FullName $running -Force
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $fullPrompt = Expand-Context -Prompt $task.Prompt -Context $task.Context
    $reportPath = Join-Path $Dirs.outbox "$id.report.txt"
    $ok = $false; $err = ''

    try {
        if ($Config.DryRun) {
            @"
[DRY_RUN STUB] task=$id worker=$($task.Worker)
No model was called. Plumbing test only.
Prompt length: $($fullPrompt.Length) chars.
"@ | Out-File $reportPath -Encoding utf8
            $ok = $true
        }
        elseif ($task.Worker -eq 'claude') {
            $out = & $Config.ClaudeModel -p $fullPrompt --output-format text --permission-mode plan 2>&1
            $out | Out-File (Join-Path $Dirs.outbox "$id.claude.txt") -Encoding utf8
            $out | Out-File $reportPath -Encoding utf8
            $ok = ($LASTEXITCODE -eq 0)
        }
        else {
            $out = $fullPrompt | & $Config.CodexModel exec - 2>&1
            $out | Out-File $reportPath -Encoding utf8
            $ok = ($LASTEXITCODE -eq 0)
        }
    } catch {
        $err = $_.Exception.Message; $ok = $false
    }
    $sw.Stop()
    $dur = [math]::Round($sw.Elapsed.TotalSeconds,1)

    $reportOk = (Test-Path $reportPath) -and ((Get-Item $reportPath).Length -gt 0)
    if ($ok -and $reportOk) {
        Move-Item $running (Join-Path $Dirs.done $File.Name) -Force
        Write-Log "DONE $id worker=$($task.Worker) ${dur}s" 'OK'
    } else {
        Move-Item $running (Join-Path $Dirs.error $File.Name) -Force
        "exit/err: $err" | Out-File (Join-Path $Dirs.error "$id.error.txt") -Encoding utf8
        Write-Log "ERROR $id worker=$($task.Worker) ${dur}s" 'ERR'
    }
}

# ---------------------------------------------------------------------------
# daily roll-up
# ---------------------------------------------------------------------------
function Write-Rollup {
    $date = [DateTime]::UtcNow.ToString('yyyy-MM-dd')
    $out  = Join-Path $Dirs.reports "$date-summary.md"
    $done = @(Get-ChildItem $Dirs.done -File -EA SilentlyContinue | Where-Object { $_.LastWriteTimeUtc.Date -eq [DateTime]::UtcNow.Date })
    $errs = @(Get-ChildItem $Dirs.error -File -Filter *.task.* -EA SilentlyContinue | Where-Object { $_.LastWriteTimeUtc.Date -eq [DateTime]::UtcNow.Date })
    $appr = @(Get-ChildItem $Dirs.approvals -File -Filter *.approval.md -EA SilentlyContinue)
    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine("# AI_OS Relay Summary — $date`n")
    [void]$sb.AppendLine("- Done:     $($done.Count)")
    [void]$sb.AppendLine("- Errored:  $($errs.Count)")
    [void]$sb.AppendLine("- Approvals waiting: $($appr.Count)`n")
    [void]$sb.AppendLine("## Completed")
    foreach ($f in $done) { [void]$sb.AppendLine("- $($f.BaseName)") }
    [void]$sb.AppendLine("`n## Errored / blocked")
    foreach ($f in $errs) { [void]$sb.AppendLine("- $($f.BaseName)") }
    [void]$sb.AppendLine("`n## Approval items (action needed)")
    foreach ($f in $appr) { [void]$sb.AppendLine("- $($f.Name)") }
    $sb.ToString() | Out-File $out -Encoding utf8
    Write-Log "ROLLUP -> $out" 'OK'
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
Initialize-Tree
Write-Log "Relay start. DryRun=$($Config.DryRun) Watch=$Watch Report=$Report" 'INFO'

if ($Report) { Write-Rollup; return }

function Invoke-Pass {
    # 1. auto-packetize any pending handoffs so one drop -> one result
    $n = Invoke-Packetize -Root $Config.Root -Apply -Logger { param($m) Write-Log $m 'PKT' }
    if ($n -gt 0) { Write-Log "packetized $n handoff(s) into inbox" 'OK' }

    $files = Get-ChildItem $Dirs.inbox -File -EA SilentlyContinue |
             Where-Object { $_.Name -like '*.task.txt' -or $_.Name -like '*.task.json' } |
             Sort-Object LastWriteTimeUtc
    foreach ($f in $files) {
        if (-not (Test-Stable -Path $f.FullName)) { Write-Log "skip (unstable) $($f.Name)" 'WARN'; continue }
        try { Invoke-Task -File $f } catch { Write-Log "FATAL on $($f.Name): $($_.Exception.Message)" 'ERR' }
    }
}

if ($Watch) {
    Invoke-Pass
    $fsw = [System.IO.FileSystemWatcher]::new($Dirs.inbox, '*.task.*')
    $fsw.EnableRaisingEvents = $true
    Write-Log "WATCH mode on inbox\. Ctrl+C to stop." 'INFO'
    try {
        while ($true) {
            $r = $fsw.WaitForChanged([System.IO.WatcherChangeTypes]::Created, 2000)
            if (-not $r.TimedOut) { Start-Sleep -Milliseconds 200 }
            # Run a pass every tick: catches inbox drops AND handoff drops
            # (handoffs\ is auto-packetized at the top of Invoke-Pass).
            Invoke-Pass
        }
    } finally { $fsw.Dispose() }
} else {
    Invoke-Pass
    Write-Log "Single pass complete." 'INFO'
}
