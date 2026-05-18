#Requires -Version 5.1
<#
.SYNOPSIS
    Prints the AI_OS worker identity banner for a named terminal session.
.EXAMPLE
    powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "AI_OS MAIN CONTROL" -Mode DRY_RUN
#>
param(
    [ValidateSet(
        "AI_OS MAIN CONTROL",
        "CODEX BUILD LANE",
        "CLAUDE REVIEWER",
        "VALIDATOR WORKER",
        "APPROVAL INBOX"
    )]
    [Parameter(Mandatory = $true)]
    [string]$Worker,

    [ValidateSet("DRY_RUN", "APPLY")]
    [string]$Mode = "DRY_RUN",

    [string]$Status = "READY"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Off

$ts   = Get-Date -Format "yyyy-MM-dd HH:mm"
$repo = try { (Resolve-Path ".").Path } catch { "UNKNOWN" }

try { $Host.UI.RawUI.WindowTitle = "AI_OS | $Worker | $Mode | $Status" } catch {}

# Separator for capability lists — built from [char] to avoid UTF-8/codepage mismatch
$d = " $([char]0x00B7) "

# Worker identity table: role, color, scope, next action
$workerMap = @{
    "AI_OS MAIN CONTROL" = @{
        Color      = "Cyan"
        Role       = "orchestrator"
        Allowed    = "display status${d}display packet output${d}report next action"
        Blocked    = "autonomous APPLY${d}commit${d}push${d}broker${d}api_keys${d}secrets"
        NextAction = "Run: .\aios.ps1 packet -- generates operator routing packet"
    }
    "CODEX BUILD LANE"   = @{
        Color      = "Blue"
        Role       = "executor"
        Allowed    = "file edits in approved scope${d}build tasks"
        Blocked    = "autonomous APPLY${d}git commit${d}git push${d}out-of-scope writes"
        NextAction = "No task assigned -- request task from MAIN CONTROL first"
    }
    "CLAUDE REVIEWER"    = @{
        Color      = "Magenta"
        Role       = "reviewer"
        Allowed    = "DRY_RUN inspection${d}audit${d}read docs"
        Blocked    = "file edits${d}git staging${d}git commit${d}git push${d}APPLY"
        NextAction = "No target assigned -- await task packet from MAIN CONTROL"
    }
    "VALIDATOR WORKER"   = @{
        Color      = "Yellow"
        Role       = "validator"
        Allowed    = "run: git diff${d}git status${d}CI checks${d}validation chain"
        Blocked    = "file edits${d}git commit${d}git push${d}APPLY"
        NextAction = "Run: git diff --check${d}then: git status --short"
    }
    "APPROVAL INBOX"     = @{
        Color      = "Green"
        Role       = "approval gate"
        Allowed    = "read inbox${d}accept operator YES/NO${d}display gate"
        Blocked    = "autonomous execution${d}file writes${d}git commit${d}git push"
        NextAction = "No pending approvals -- await operator YES/NO instruction"
    }
}

$p = $workerMap[$Worker]
$c = $p.Color

# Box geometry — total width 80, inner 78
$iw     = 78
$dashes = [string][char]0x2500 * $iw
$TOP    = [string][char]0x250C + $dashes + [string][char]0x2510
$MID    = [string][char]0x251C + $dashes + [string][char]0x2524
$BOT    = [string][char]0x2514 + $dashes + [string][char]0x2518
$PIPE   = [string][char]0x2502

# Label area: 2 + 8 (padded) + 5 ("  :  ") = 15 chars
# Value area: 78 - 15 = 63 chars
$labelWidth = 8
$labelArea  = 2 + $labelWidth + 5   # 15
$valueWidth = $iw - $labelArea       # 63

function Write-BoxTitle([string]$Text) {
    $row = ("  " + $Text)
    if ($row.Length -gt $iw) { $row = $row.Substring(0, $iw) }
    $row = $row.PadRight($iw)
    Write-Host $PIPE -NoNewline -ForegroundColor $c
    Write-Host $row  -NoNewline -ForegroundColor $c
    Write-Host $PIPE -ForegroundColor $c
}

function Write-BoxRow([string]$Label, [string]$Value, [string]$vc = "White") {
    $lbl = "  " + $Label.PadRight($labelWidth) + "  :  "
    if ($Value.Length -gt $valueWidth) { $Value = $Value.Substring(0, $valueWidth - 3) + "..." }
    $row = $lbl + $Value.PadRight($valueWidth)
    Write-Host $PIPE -NoNewline -ForegroundColor $c
    Write-Host $row  -NoNewline -ForegroundColor $vc
    Write-Host $PIPE -ForegroundColor $c
}

# Mode presentation
$modeColor = if ($Mode -eq "APPLY") { "Red" } else { "Cyan" }
$modeText  = if ($Mode -eq "DRY_RUN") {
    "DRY_RUN   [no writes  no commits  no push]"
} else {
    "APPLY     [operator-approved writes only]"
}

# Print banner
Write-Host $TOP -ForegroundColor $c
Write-BoxTitle "AI_OS  //  $Worker"
Write-Host $MID -ForegroundColor $c
Write-BoxRow "MODE"    $modeText     $modeColor
Write-BoxRow "ROLE"    $p.Role       "White"
Write-BoxRow "STATUS"  $Status       "Green"
Write-BoxRow "REPO"    $repo         "DarkGray"
Write-BoxRow "TIME"    $ts           "DarkGray"
Write-Host $MID -ForegroundColor $c
Write-BoxRow "BLOCKED" $p.Blocked    "Red"
Write-BoxRow "ALLOWED" $p.Allowed    "Green"
Write-Host $MID -ForegroundColor $c
Write-BoxRow "NEXT"    $p.NextAction "Yellow"
Write-Host $BOT -ForegroundColor $c
Write-Host ""
