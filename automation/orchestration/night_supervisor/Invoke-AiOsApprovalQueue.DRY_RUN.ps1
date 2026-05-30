param(
    [switch]$Apply,
    [switch]$InspectionOnly,
    [switch]$OutputJson
)

$ErrorActionPreference = "Stop"

function Write-AiosLine {
    param([string]$Status, [string]$Message)
    Write-Host "$Status`t$Message"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$pythonModule = Join-Path $repoRoot "services\python_supervisor\approval_queue.py"

Set-Location $repoRoot
$branch = (& git branch --show-current).Trim()
$gitStatus = (& git status --short --branch) -join "`n"
$gitStatusEncoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($gitStatus))
$statusLines = @($gitStatus -split "`n" | Where-Object { $_ -and -not $_.StartsWith("## ") })
$sourceDirty = @($statusLines | Where-Object {
    $_ -match "^\s*(M|A|D|R|C|UU|AA|DD|AM|MM)\s+" -or $_ -match "^\s*\?\?\s+(schemas|services|automation|docs|apps)/"
})

Write-AiosLine "INFO" "repo_path=$repoRoot"
Write-AiosLine "INFO" "branch=$branch"
Write-AiosLine "INFO" "mode=$(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

if ($branch -ne "main") {
    Write-AiosLine "BLOCKED" "Approval Queue runs on main only."
    exit 2
}

if (-not (Test-Path $pythonModule)) {
    Write-AiosLine "BLOCKED" "Missing Python approval queue module: $pythonModule"
    exit 2
}

if ($Apply -and $sourceDirty.Count -gt 0 -and -not $InspectionOnly) {
    Write-AiosLine "BLOCKED" "Source tree has changed files. Re-run with -InspectionOnly for evidence-only output."
    $sourceDirty | ForEach-Object { Write-AiosLine "DIRTY" $_ }
    exit 2
}

if ($Apply) {
    $pythonOutput = & python $pythonModule "--repo-root" $repoRoot "--repo-branch" $branch "--git-status-base64" $gitStatusEncoded "--pretty" "--apply"
} else {
    $pythonOutput = & python $pythonModule "--repo-root" $repoRoot "--repo-branch" $branch "--git-status-base64" $gitStatusEncoded "--pretty"
}
if ($LASTEXITCODE -ne 0) {
    Write-AiosLine "BLOCKED" "Python approval queue returned exit code $LASTEXITCODE"
    Write-Output $pythonOutput
    exit $LASTEXITCODE
}

$receipt = $pythonOutput | ConvertFrom-Json
$state = $receipt.queue_state
$counts = $state.approval_counts

Write-AiosLine "PASS" "approval_queue_status=$($receipt.status)"
Write-AiosLine "PASS" "waiting=$($counts.waiting_review) approved=$($counts.approved) rejected=$($counts.rejected)"
Write-AiosLine "PASS" "stale=$($counts.stale) unsafe_blocked=$($counts.unsafe_blocked) already_handled=$($counts.already_handled)"
Write-AiosLine "PASS" "next_safe_action=$($state.next_safe_action)"
if ($Apply) {
    Write-AiosLine "PASS" "written_output_paths=$($receipt.written_output_paths -join ', ')"
} else {
    Write-AiosLine "PASS" "DRY_RUN only; no files written."
}

if ($OutputJson) {
    $pythonOutput
}
