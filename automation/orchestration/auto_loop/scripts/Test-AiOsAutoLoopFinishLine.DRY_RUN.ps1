[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $scriptRoot "..\..\..\..")).Path
Set-Location $repoRoot

$reportsRoot = Join-Path $repoRoot "telemetry\auto_loop\reports"
if (-not (Test-Path -LiteralPath $reportsRoot)) {
    New-Item -ItemType Directory -Path $reportsRoot -Force | Out-Null
}

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$goalPath = Join-Path $repoRoot "telemetry\auto_loop\examples\AUTO_LOOP_DEMO_GOAL.txt"
$goalText = if (Test-Path -LiteralPath $goalPath) {
    (Get-Content -Raw -LiteralPath $goalPath).Trim()
} else {
    "Create a paper-only Trading Lab latency report scaffold without touching broker or live execution paths."
}

$packetPath = "telemetry/auto_loop/reports/AUTO_LOOP_PACKET_CANDIDATE.demo.json"
$approvalPath = "telemetry/auto_loop/reports/AUTO_LOOP_APPROVAL_CANDIDATE.demo.json"

$preflightJson = & (Join-Path $scriptRoot "Test-AiOsAutoLoopPreflight.DRY_RUN.ps1")
$packetJson = & (Join-Path $scriptRoot "New-AiOsAutoLoopPacketCandidate.DRY_RUN.ps1") -GoalText $goalText -OutputPath $packetPath
$validatorJson = & (Join-Path $scriptRoot "Get-AiOsAutoLoopValidatorRoute.DRY_RUN.ps1") -ChangedPath @(
    "automation/orchestration/auto_loop/",
    "telemetry/auto_loop/examples/AUTO_LOOP_DEMO_GOAL.txt"
)
$approvalJson = & (Join-Path $scriptRoot "New-AiOsAutoLoopApprovalCandidate.DRY_RUN.ps1") -PacketCandidatePath $packetPath -OutputPath $approvalPath
$commitPackageJson = & (Join-Path $scriptRoot "New-AiOsAutoLoopCommitPackage.DRY_RUN.ps1")

$preflight = $preflightJson | ConvertFrom-Json
$packet = $packetJson | ConvertFrom-Json
$validatorRoute = $validatorJson | ConvertFrom-Json
$approval = $approvalJson | ConvertFrom-Json
$commitPackage = $commitPackageJson | ConvertFrom-Json

$report = [ordered]@{
    report_id = "AUTO_LOOP_FINISH_LINE_DRY_RUN_$timestamp"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    mode = "DRY_RUN"
    status = if ($preflight.status -eq "BLOCK") { "BLOCK" } else { "PASS" }
    goal_text = $goalText
    preflight = $preflight
    packet_candidate = $packet
    validator_route = $validatorRoute
    approval_candidate = $approval
    commit_package = $commitPackage
    blocked_actions = @(
        "commit",
        "push",
        "merge",
        "live_trading",
        "broker_execution",
        "OANDA_execution",
        "Webull_execution",
        "secret_access",
        "credential_access",
        "active_queue_mutation",
        "active_approval_inbox_mutation",
        "active_worker_registry_mutation",
        "runtime_process_mutation"
    )
    did = @(
        "Ran auto-loop preflight.",
        "Generated a packet candidate.",
        "Generated a validator route recommendation.",
        "Generated an approval candidate.",
        "Generated a commit package recommendation.",
        "Wrote generated evidence under telemetry/auto_loop/reports."
    )
    did_not = @(
        "Did not mutate active queues, active approval inbox, active worker registry, runtime state, broker paths, secrets, commits, pushes, merges, or deployments."
    )
    final_operator_next_action = "Inspect git diff for automation/orchestration/auto_loop and telemetry/auto_loop before approving any focused APPLY/commit package."
}

$reportPath = Join-Path $reportsRoot ("AUTO_LOOP_FINISH_LINE_REPORT_{0}.json" -f $timestamp)
$reportJson = $report | ConvertTo-Json -Depth 20
Set-Content -LiteralPath $reportPath -Value ($reportJson + [Environment]::NewLine) -Encoding UTF8

Write-Output $reportJson
