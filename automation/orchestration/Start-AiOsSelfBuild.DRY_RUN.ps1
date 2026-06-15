[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$SelfBuildArgs = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Dev\Ai.Os"
$DriverScript = ".\automation\orchestration\aios_self_build_dry_run_driver.py"
$DefaultArgs = @(
    "--driver-mode", "DRY_RUN"
)

Set-Location -LiteralPath $RepoRoot

$EffectiveArgs = if ($SelfBuildArgs.Count -gt 0) {
    $SelfBuildArgs
} else {
    $DefaultArgs
}

& python $DriverScript @EffectiveArgs
exit $LASTEXITCODE
