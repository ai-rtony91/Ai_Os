param(
    [ValidateSet("IDLE", "WORKING", "COMPLETE", "BLOCKED", "CLOSED")]
    [string]$State = "IDLE",

    [string]$Message = "Persistent AI_OS terminal is visible. Press Enter to close when finished.",

    [switch]$TemporaryWorker,

    [switch]$CloseOnComplete
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$stateColors = @{
    IDLE = "Cyan"
    WORKING = "Green"
    COMPLETE = "Green"
    BLOCKED = "Red"
    CLOSED = "DarkGray"
}

$color = $stateColors[$State]
$border = "#" * 100

Write-Host ""
Write-Host $border -ForegroundColor $color
Write-Host ("  AI_OS VISIBLE TERMINAL STATE: {0}" -f $State) -ForegroundColor $color
Write-Host ("  {0}" -f $Message) -ForegroundColor $color
Write-Host "  Persistent decks stay open in IDLE for the operator session."
Write-Host "  Temporary OCC workers stay open for one assigned task lifecycle."
Write-Host "  OCC lifecycle covers APPLY, validation, commit, push, PR/merge if used, and final sync/status."
Write-Host "  OCC workers close only after final COMPLETE, or park visibly on BLOCKED."
Write-Host "  Anti-pileup: reuse the active worker lane; do not spawn unlimited new windows."
Write-Host "  No Codex auto-launch. No startup tasks. No scheduled tasks."
Write-Host $border -ForegroundColor $color

if ($TemporaryWorker -and $CloseOnComplete -and ($State -in @("COMPLETE", "CLOSED"))) {
    Write-Host "Temporary worker close mode active. Closing this terminal without keepalive prompt." -ForegroundColor Green
    exit 0
}

Read-Host "Press Enter to close this AI_OS terminal"
