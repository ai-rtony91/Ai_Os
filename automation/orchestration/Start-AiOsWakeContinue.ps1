[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$WakeArgs = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Dev\Ai.Os"
$WakeScript = ".\automation\orchestration\aios_wake_continue.py"
$DefaultArgs = @(
    "--goal", "forex-paper-bot",
    "--apply",
    "--max-cycles", "3",
    "--max-repairs", "1",
    "--write-resume-state",
    "--write-control-plane-status",
    "--emit-continuation-controller"
)

Set-Location -LiteralPath $RepoRoot

$EffectiveArgs = if ($WakeArgs.Count -gt 0) {
    $WakeArgs
} else {
    $DefaultArgs
}

& python $WakeScript @EffectiveArgs
exit $LASTEXITCODE
