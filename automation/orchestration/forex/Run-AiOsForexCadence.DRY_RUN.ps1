Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptPath "..\..\..")
$Python = Get-Command python -ErrorAction Stop
$Runner = Join-Path $RepoRoot "automation\forex_engine\forex_demo_cadence_runner_v1.py"

$BlockedTerms = @("git commit", "git push", "scheduler", "broker", "secret")
foreach ($Term in $BlockedTerms) {
    if ($env:AIOS_FOREX_CADENCE_ACTION -like "*$Term*") {
        throw "BLOCKED_FORBIDDEN_CADENCE_ACTION"
    }
}

& $Python.Source $Runner --repo-root $RepoRoot --cycles 3 --pretty
if ($LASTEXITCODE -ne 0) {
    throw "AIOS_FOREX_CADENCE_DRY_RUN_FAILED"
}
