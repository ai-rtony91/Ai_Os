param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    $root = git rev-parse --show-toplevel 2>$null | ForEach-Object { $_.Trim() }
    if ([string]::IsNullOrWhiteSpace($root)) {
        return (Get-Location).Path
    }
    return $root
}

$repoRoot = Get-RepoRoot
$gitStatusLines = @(git -C $repoRoot status --short --untracked-files=all 2>$null)
$dirtyCount = $gitStatusLines.Count
$branch = (git -C $repoRoot branch --show-current).Trim()

$sprint14Path = Join-Path $repoRoot "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_14_PAPER_READINESS_GATE.md"
$sprint15Path = Join-Path $repoRoot "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_15_PAPER_SIGNAL_INTAKE_LEDGER.md"

$forexReadinessGatePresent = Test-Path -LiteralPath $sprint14Path -PathType Leaf
$forexSignalIntakeLedgerPresent = Test-Path -LiteralPath $sprint15Path -PathType Leaf

if ($forexReadinessGatePresent -and $forexSignalIntakeLedgerPresent) {
    $latestSprint = "SPRINT_15"
    $recommendedPacketId = "AIOS-FOREX-PAPER-RISK-DECISION-ROUTER-APPLY-V1"
    $recommendedPacketTitle = "feat(forex): add paper risk decision router"
    $recommendedLane = "PAPER_RISK_DECISION_ROUTER"
} else {
    $latestSprint = "UNKNOWN"
    $recommendedPacketId = ""
    $recommendedPacketTitle = "No recommendation yet"
    $recommendedLane = "PAPER_BOUNDARY_REVIEW"
}

$requiredValidators = @(
    "git diff --check",
    "python -m pytest tests/forex_engine -q -p no:cacheprovider",
    "python automation/forex_engine/run_readiness_demo.py",
    "python automation/forex_engine/run_paper_signal_intake_demo.py",
    "python automation/forex_engine/run_paper_risk_decision_demo.py",
    ".\aios.ps1 -Mode status",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
)

$blockedActions = @(
    "live trading",
    "broker APIs",
    "OANDA",
    "real orders",
    "webhooks",
    "real market data",
    "API keys/secrets",
    "scheduler/daemon",
    "worker launch",
    "runtime mutation",
    "telemetry mutation",
    "dashboard mutation",
    "Cloudflare",
    "backup sync",
    "push/PR/merge automation"
)

$recommendedFiles = @(
    "automation/forex_engine/paper_risk_decision.py",
    "automation/forex_engine/run_paper_risk_decision_demo.py",
    "tests/forex_engine/test_paper_risk_decision.py",
    "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_16_PAPER_RISK_DECISION_ROUTER.md"
)

$result = [ordered]@{
    schema = "AIOS_FOREX_CONTINUATION_RECOMMENDATION.v1"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    repo_root = $repoRoot
    branch = $branch
    dirty_or_untracked_count = $dirtyCount
    forex_readiness_gate_present = [bool]$forexReadinessGatePresent
    forex_signal_intake_ledger_present = [bool]$forexSignalIntakeLedgerPresent
    latest_forex_sprint_detected = $latestSprint
    recommended_next_packet_id = $recommendedPacketId
    recommended_next_packet_title = $recommendedPacketTitle
    recommended_lane = $recommendedLane
    recommended_files = @($recommendedFiles)
    required_validators = @($requiredValidators)
    blocked_actions = @($blockedActions)
    human_approval_required = $true
    execution_allowed = $false
    reason = if ($recommendedPacketId) {
        "Sprint 14 and 15 evidence is present; the next safe step is paper risk decision router."
    } else {
        "Sprint 14 and/or Sprint 15 evidence is not fully present; no safe next packet can be recommended."
    }
    next_safe_action = if ($recommendedPacketId) {
        "Create and route APPROVAL packet for '$recommendedPacketId' with required validators only."
    } else {
        "Complete Sprint 14 and Sprint 15 boundary docs/tests first, then rerun this recommender."
    }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS FOREX CONTINUATION RECOMMENDER"
Write-Host "schema: $($result.schema)"
Write-Host "repo_root: $($result.repo_root)"
Write-Host "branch: $($result.branch)"
Write-Host "dirty_or_untracked_count: $($result.dirty_or_untracked_count)"
Write-Host "latest_forex_sprint_detected: $($result.latest_forex_sprint_detected)"
Write-Host "recommended_next_packet_id: $($result.recommended_next_packet_id)"
Write-Host "recommended_next_packet_title: $($result.recommended_next_packet_title)"
Write-Host "recommended_lane: $($result.recommended_lane)"
Write-Host "human_approval_required: $($result.human_approval_required)"
Write-Host "execution_allowed: $($result.execution_allowed)"
Write-Host "reason: $($result.reason)"
Write-Host "next_safe_action: $($result.next_safe_action)"
Write-Host "writes_performed: 0"
Write-Host "worker_execution_performed: NO"
Write-Host "commit_performed: NO"
Write-Host "push_performed: NO"
