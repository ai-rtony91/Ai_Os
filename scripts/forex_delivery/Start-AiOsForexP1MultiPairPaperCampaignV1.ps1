param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os',
    [int]$Cycles = 288
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot '.git'))) { throw 'REPO_ROOT_INVALID' }
$branch = (& git -C $RepoRoot branch --show-current).Trim()
if ($branch -ne 'codex/forex-all-pairs-paper-total-closure-v1' -and $branch -ne 'main') {
    throw "NORMALIZED_MULTI_PAIR_BRANCH_REQUIRED: $branch"
}
if ($Cycles -lt 1 -or $Cycles -gt 288) { throw 'CYCLES_OUT_OF_RANGE' }
$runner = Join-Path $RepoRoot 'scripts\forex_delivery\run_forex_p1_multipair_normalized_paper_campaign_v1.py'
if (-not (Test-Path -LiteralPath $runner)) { throw 'NORMALIZED_MULTIPAIR_RUNNER_MISSING' }
$runtimeRoot = Join-Path $RepoRoot '.aios\runtime\forex_p1_multipair_normalized_paper_campaign_v1'
if (Test-Path -LiteralPath $runtimeRoot) {
    $state = Join-Path $runtimeRoot 'AIOS_FOREX_MULTIPAIR_NORMALIZED_PAPER_CAMPAIGN_STATE.json'
    if (Test-Path -LiteralPath $state) {
        $existing = Get-Content -LiteralPath $state -Raw | ConvertFrom-Json
        if ($existing.campaign_status -in @('RUNNING','WAITING_FOR_NEXT_RUN')) {
            throw 'CAMPAIGN_ALREADY_ACTIVE'
        }
    }
}
& python $runner --repo-root $RepoRoot --runtime-root $runtimeRoot --cycles $Cycles --reviewer 'Human Owner Anthony'
if ($LASTEXITCODE -ne 0) { throw "NORMALIZED_MULTIPAIR_CAMPAIGN_FAILED: $LASTEXITCODE" }
