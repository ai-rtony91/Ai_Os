[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$SelfBuildArgs = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Dev\Ai.Os"
$ControllerScript = ".\automation\orchestration\aios_overnight_build_controller.py"
$DefaultArgs = @(
    "--controller-mode", "DRY_RUN",
    "--goal", "forex-paper-bot",
    "--current-mode", "generic",
    "--cycle-budget", "1",
    "--time-budget-minutes", "30",
    "--max-files-changed", "5",
    "--max-repairs", "1"
)

Set-Location -LiteralPath $RepoRoot

$EffectiveArgs = if ($SelfBuildArgs.Count -gt 0) {
    $SelfBuildArgs
} else {
    $DefaultArgs
}

& python $ControllerScript @EffectiveArgs
exit $LASTEXITCODE
