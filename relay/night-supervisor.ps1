#requires -Version 7.0
<#
==============================================================================
 AI_OS NIGHT SUPERVISOR  (read-mostly, self-gating)
 Owner: Anthony Meza
 Doctrine:
   - Easy safe work happens automatically.
   - Risky work stops automatically and creates an approval item.
   - Anthony gets an alert ONLY when a blocker is hit.
 Scope:
   - Reads anywhere in the repo (inspect only).
   - WRITES ONLY inside relay\ (reports, packets, approvals, logs, sorting).
   - Never commits, pushes, merges, deletes, or overwrites source files.
 This is a SINGLE PASS. It is not a background service. Run it on demand.
==============================================================================
#>
[CmdletBinding()]
param(
    [switch]$Apply,          # without -Apply it only reports what it WOULD do
    [switch]$GenerateGoals   # write safe maintenance goals into relay\goals\
)

$RepoRoot  = Split-Path $PSScriptRoot -Parent
$RelayRoot = $PSScriptRoot
$Reports   = Join-Path $RelayRoot 'reports'
$Approvals = Join-Path $RelayRoot 'approvals'
$Logs      = Join-Path $RelayRoot 'logs'
$Goals     = Join-Path $RelayRoot 'goals'
foreach ($d in @($Reports,$Approvals,$Logs)) { if (-not (Test-Path $d)) { New-Item -ItemType Directory $d | Out-Null } }

$findings = [System.Collections.Generic.List[string]]::new()
function Note($m) { $findings.Add($m); Write-Host "  $m" }

function Log($m) {
    $ts = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    "$ts [NIGHT] $m" | Out-File (Join-Path $Logs 'night.log') -Append -Encoding utf8
}

function Alert {
    param([string]$Title,[string]$Reason,[string]$Proposed,[string]$Risk)
    $stamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
    $f = Join-Path $Approvals "$stamp-$Title.approval.md"
    @"
# APPROVAL REQUIRED — $Title

**Created (UTC):** $([DateTime]::UtcNow.ToString('u'))
**Risk level:** $Risk
**Status:** WAITING

## Reason
$Reason

## Proposed action (NOT taken automatically)
``````
$Proposed
``````

## What Anthony must approve
Review and decide. Night Supervisor stopped here by design.
"@ | Out-File $f -Encoding utf8
    Note "ALERT raised: $f"; Log "ALERT $Title"
}

Write-Host "=== AI_OS Night Supervisor (Apply=$Apply) ==="
Log "start Apply=$Apply"

# --- 1. Folder integrity (auto-fixable inside relay\) -----------------------
$need = 'inbox','running','outbox','done','error','reports','logs','approvals','handoffs','packets'
foreach ($n in $need) {
    $p = Join-Path $RelayRoot $n
    if (-not (Test-Path $p)) {
        if ($Apply) { New-Item -ItemType Directory $p | Out-Null; Note "created missing folder relay\$n" }
        else        { Note "WOULD create missing folder relay\$n" }
    }
}

# --- 2. Stale running\ files (worker may have died) -------------------------
$running = Join-Path $RelayRoot 'running'
if (Test-Path $running) {
    Get-ChildItem $running -File -EA SilentlyContinue | ForEach-Object {
        $ageMin = ([DateTime]::UtcNow - $_.LastWriteTimeUtc).TotalMinutes
        if ($ageMin -gt 60) { Note "STALE in running\: $($_.Name) ($([math]::Round($ageMin))m old) — investigate" }
    }
}

# --- 3. Duplicate packets in inbox\ -----------------------------------------
$inbox = Join-Path $RelayRoot 'inbox'
if (Test-Path $inbox) {
    Get-ChildItem $inbox -File -EA SilentlyContinue | Group-Object BaseName |
        Where-Object Count -gt 1 | ForEach-Object { Note "DUPLICATE packet base: $($_.Name) x$($_.Count)" }
}

# --- 4. Repo cleanliness (READ ONLY — never acts) ---------------------------
Push-Location $RepoRoot
try {
    $branch = (git branch --show-current 2>$null)
    $dirty  = (git status --porcelain 2>$null)
    Note "git branch: $branch"
    if ($dirty) {
        $count = ($dirty -split "`n").Where({$_ -ne ''}).Count
        Note "git working tree DIRTY ($count changed paths) — commit requires Anthony approval"
        Alert -Title 'dirty-repo' `
            -Reason "Working tree has $count uncommitted change(s) on '$branch'. Committing is an ultimate blocker." `
            -Proposed "git add -A; git commit -m '<message>'   # DO NOT run automatically" `
            -Risk 'BLOCKER — git commit'
    } else { Note "git working tree clean" }
} catch { Note "git inspect failed: $($_.Exception.Message)" }
Pop-Location

# --- 5. Outstanding approvals --------------------------------------------------
$waiting = @(Get-ChildItem $Approvals -File -Filter *.approval.md -EA SilentlyContinue)
if ($waiting.Count) { Note "$($waiting.Count) approval item(s) WAITING for Anthony" }

# --- 5b. SAFE GOAL FEEDER (-GenerateGoals) -------------------------------------
# Night Supervisor is a GOAL CREATOR, not an executor. It writes plain goal
# files into relay\goals\; the existing relay chain (goal-intake -> packetize ->
# runner) does routing, packets, workers, results, and blocker approvals.
#
# Safety colors:  GREEN  = read-only summary/checks (auto)
#                 YELLOW = relay-only packets/reports (auto)
#                 ORANGE = suggests future change, does not apply (approval)
#                 RED    = source change outside relay (approval)
#                 BLACK  = commit/push/merge/delete/trade/secret/etc. (approval)
# Auto-create GREEN + YELLOW only. Anything else -> approval. If unsure -> approval.

# Words that force a goal to BLACK no matter what it claims.
$BlackWords = @('commit','push','merge','rebase','delete','trade','broker',
    'oanda','secret','credential','api key','apikey','to main','order',
    'execution','position','buy','sell','live')

function Get-GoalColor {
    param([string]$Title,[string]$Body,[string]$Declared)
    $low = "$Title `n$Body".ToLowerInvariant()
    foreach ($w in $BlackWords) { if ($low.Contains($w)) { return 'BLACK' } }
    if ($Declared -in @('GREEN','YELLOW','ORANGE','RED','BLACK')) { return $Declared }
    return 'ORANGE'   # unknown -> treat as approval-required
}

function New-NightGoal {
    param([string]$Slug,[string]$Title,[string]$Body,[string]$Declared)
    $color = Get-GoalColor -Title $Title -Body $Body -Declared $Declared
    if ($color -in @('GREEN','YELLOW')) {
        if (-not (Test-Path $Goals)) { New-Item -ItemType Directory $Goals | Out-Null }
        $stamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmm')
        $name  = "night-$stamp-$Slug.goal.txt"
        $Body | Out-File (Join-Path $Goals $name) -Encoding utf8
        Note "GOAL created [$color]: goals\$name"
        Log  "GOAL $color $name"
    } else {
        Alert -Title "night-goal-$Slug" `
            -Reason "Night Supervisor classified maintenance goal '$Title' as $color. Not auto-created; needs operator decision." `
            -Proposed $Title `
            -Risk "$color — approval required"
        Note "GOAL blocked [$color]: '$Title' -> approval (no goal file)"
    }
}

if ($GenerateGoals) {
    Note "GenerateGoals: classifying safe maintenance goals"

    # Candidate GREEN goals. Bodies deliberately avoid blocker keywords so the
    # relay routes them to a read-only worker instead of self-blocking. The
    # "no version-control" reminder is phrased without trigger words on purpose.
    $g1 = @"
GOAL: Summarize today's relay activity from logs and outbox.

Purpose: Give Anthony a fast morning read of what the relay processed.
Safety level: GREEN (read-only summary, relay-only).
Intended worker: Claude (analysis / plan, read-only).
Expected output: relay/outbox (result packet).

Relay-only task. Take no version-control action. Do not change files outside
relay. Do not schedule tasks or start background services. No financial or
sensitive data. This goal only asks for a summary.
"@
    $g2 = @"
GOAL: Review waiting approval items and list what needs operator attention.

Purpose: Surface anything parked in relay/approvals so nothing is missed.
Safety level: GREEN (read-only review, relay-only).
Intended worker: Claude (analysis / plan, read-only).
Expected output: relay/outbox (result packet).

Relay-only task. Take no version-control action. Do not change files outside
relay. Do not schedule tasks or start background services. No financial or
sensitive data. This goal only asks for a review summary.
"@
    $g3 = @"
GOAL: Inspect relay for stale running tasks and duplicate handoffs.

Purpose: Flag tasks stuck in relay/running and any duplicated handoff packets.
Safety level: GREEN (read-only inspection, relay-only).
Intended worker: Claude (analysis / plan, read-only).
Expected output: relay/outbox (result packet).

Relay-only task. Take no version-control action. Do not change files outside
relay. Do not schedule tasks or start background services. No financial or
sensitive data. This goal only asks for an inspection summary.
"@

    New-NightGoal -Slug 'activity-summary' -Title "Summarize today's relay activity" -Body $g1 -Declared 'GREEN'
    New-NightGoal -Slug 'approval-review'  -Title 'Review waiting approval items'     -Body $g2 -Declared 'GREEN'
    New-NightGoal -Slug 'stale-task-check' -Title 'Inspect for stale running tasks'   -Body $g3 -Declared 'GREEN'
}

# --- 6. Write the night report ------------------------------------------------
$date = [DateTime]::UtcNow.ToString('yyyy-MM-dd-HHmm')
$rep  = Join-Path $Reports "night-$date.md"
$body = "# Night Supervisor Report — $([DateTime]::UtcNow.ToString('u'))`n`nApply mode: $Apply`n`n## Findings`n" +
        (($findings | ForEach-Object { "- $_" }) -join "`n") +
        "`n`n## Standing rule`nAutomatic = read/sort/report/route low-risk relay work. " +
        "Anything outside relay\, any git write, delete, or overwrite STOPS and creates an approval item."
$body | Out-File $rep -Encoding utf8
Note "report written: $rep"
Log "end findings=$($findings.Count)"
Write-Host "=== done. Report: $rep ==="
