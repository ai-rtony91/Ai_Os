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
Write-Host "  Temporary OCC workers may stay visible while WORKING."
Write-Host "  Temporary OCC workers close after completed APPLY/commit workflow or park on BLOCKED."
Write-Host "  Anti-pileup: do not stack unlimited completed worker windows."
Write-Host "  No Codex auto-launch. No startup tasks. No scheduled tasks."
Write-Host $border -ForegroundColor $color

if ($TemporaryWorker -and $CloseOnComplete -and ($State -in @("COMPLETE", "CLOSED"))) {
    Write-Host "Temporary worker close mode active. Closing this terminal without keepalive prompt." -ForegroundColor Green
    exit 0
}

Read-Host "Press Enter to close this AI_OS terminal"
