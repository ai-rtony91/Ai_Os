#requires -Version 7.0
<#
==============================================================================
 AI_OS GOAL INTAKE  (plain goal -> packets, automatically)
 Anthony writes "Build X" in a goal file. This turns it into:
   goal -> worker handoff packet(s) -> (relay watcher) -> result
 No manual packet authoring, no worker selection, no handoff writing.

 Flow:
   goals\*.goal.txt
     -> classify (worker + approval level)
     -> handoffs\<id>.handoff.json  (Claude plan and/or Codex build)
     -> [if blocker] approvals\<id>.approval.json  (no handoff emitted)
     -> goals\processed\  (original archived)

 Runs standalone OR is dot-sourced by relay-runner.ps1, which calls
 Invoke-GoalIntake at the top of each pass (before packetize).
 Scope: reads relay\goals\, writes relay\handoffs\ + relay\approvals\,
        archives to relay\goals\processed\. Nothing outside relay\.
==============================================================================
#>
[CmdletBinding()]
param([switch]$Apply)   # standalone: without -Apply, preview the routing only

function Invoke-GoalIntake {
    param(
        [string]$Root = $PSScriptRoot,
        [switch]$Apply,
        [scriptblock]$Logger
    )
    $Goals     = Join-Path $Root 'goals'
    $Processed = Join-Path $Goals 'processed'
    $Handoffs  = Join-Path $Root 'handoffs'
    $Approvals = Join-Path $Root 'approvals'
    foreach ($d in @($Goals,$Processed,$Handoffs,$Approvals)) {
        if (-not (Test-Path $d)) { New-Item -ItemType Directory $d | Out-Null }
    }
    function emit($m) { if ($Logger) { & $Logger $m } else { Write-Host $m } }

    # Ultimate blockers: goal must stop and become an approval, not a handoff.
    $BlockerWords = @(
        'trade','order','buy','sell','position','execution','broker','oanda',
        'api key','apikey','secret','credential','push','commit',
        'merge','rebase','delete','to main','live order'
    )
    # Verbs that mean "inspect/think" -> route to Claude (plan, read-only).
    $AnalyzeWords = @('review','inspect','audit','analyze','assess','plan','design',
        'evaluate','compare','investigate','map','summarize','recommend','critique')
    # Verbs that mean "make a change" -> route to Codex (exec).
    $BuildWords   = @('build','create','implement','write','add','fix','refactor',
        'generate','wire','connect','update','scaffold','make','validator')

    function Get-Hit { param($text,$words)
        $low = $text.ToLowerInvariant()
        foreach ($w in $words) { if ($low.Contains($w)) { return $w } }
        return $null
    }
    function New-Slug { param($text)
        $s = ($text -replace '[^a-zA-Z0-9 ]','').Trim().ToLowerInvariant()
        $s = ($s -split '\s+' | Select-Object -First 5) -join '-'
        if (-not $s) { $s = 'goal' }
        return $s
    }

    $files = Get-ChildItem $Goals -File -Filter *.goal.txt -EA SilentlyContinue
    if (-not $files) { emit "goal-intake: no pending goals"; return 0 }

    $count = 0
    foreach ($f in $files) {
        $text = (Get-Content $f.FullName -Raw).Trim()
        if (-not $text) { emit "goal-intake SKIP (empty): $($f.Name)"; continue }

        $slug    = New-Slug $text
        $base    = "g-$slug"
        $blocker = Get-Hit $text $BlockerWords
        $analyze = Get-Hit $text $AnalyzeWords
        $build   = Get-Hit $text $BuildWords

        if ($blocker) {
            $who = 'HUMAN (blocked)'; $level = 'TIER_2_HUMAN_REQUIRED'
        } elseif ($build -or -not $analyze) {
            $who = 'Claude (plan) + Codex (build)'; $level = 'TIER_1_LOW_RISK'
        } else {
            $who = 'Claude (plan only)'; $level = 'TIER_0_AUTO'
        }
        emit "goal-intake GOAL: '$text' -> $who [$level]"

        if (-not $Apply) { continue }

        if ($blocker) {
            $appr = [ordered]@{
                packet='approval'; id=$base; raised_by='goal-intake'; risk='HIGH'
                reason="Goal contains blocker keyword '$blocker'. Not auto-routed to a worker."
                proposed=$text; needs='Anthony to approve scope before any worker runs.'
                status='WAITING'
            }
            $dest = Join-Path $Approvals "$base.approval.json"
            ($appr | ConvertTo-Json -Depth 6) | Out-File $dest -Encoding utf8
            emit "goal-intake -> approvals\$base.approval.json (no worker packet)"
        } else {
            $claude = [ordered]@{
                packet='handoff'; id="$base-plan"; from='goal-intake'; to='claude'; mode='plan'
                lane=$base; allowed_paths=@('relay/'); forbidden_paths=@('anything outside relay/')
                goal=$text
                prompt="Produce a short, scoped implementation plan for this goal: `"$text`". List exact files, steps, risks, and a stop condition. Do not modify anything (read-only plan)."
                context=@(); stop_condition="When the plan result is written."; approval_required=$false
            }
            ($claude | ConvertTo-Json -Depth 6) | Out-File (Join-Path $Handoffs "$base-plan.handoff.json") -Encoding utf8
            emit "goal-intake -> handoffs\$base-plan.handoff.json"

            if ($build -or -not $analyze) {
                $codex = [ordered]@{
                    packet='handoff'; id="$base-build"; from='goal-intake'; to='codex'; mode='exec'
                    lane=$base; allowed_paths=@('relay/'); forbidden_paths=@('anything outside relay/')
                    goal=$text
                    prompt="Implement this goal under AI_OS rules (DRY_RUN before APPLY, smallest safe change): `"$text`". Follow the Claude plan for lane $base if present. Report files created/changed, validation, and next safe action."
                    context=@(); stop_condition="When the build result is written."; approval_required=$true
                }
                ($codex | ConvertTo-Json -Depth 6) | Out-File (Join-Path $Handoffs "$base-build.handoff.json") -Encoding utf8
                emit "goal-intake -> handoffs\$base-build.handoff.json"
            }
        }
        Move-Item $f.FullName (Join-Path $Processed $f.Name) -Force
        $count++
    }
    return $count
}

# Standalone execution (not dot-sourced)
if ($MyInvocation.InvocationName -ne '.') {
    $n = Invoke-GoalIntake -Root $PSScriptRoot -Apply:$Apply
    Write-Host "goal-intake done. Processed=$n (Apply=$Apply)"
}
