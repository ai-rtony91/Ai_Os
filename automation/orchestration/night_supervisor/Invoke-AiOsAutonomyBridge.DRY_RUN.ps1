param(
    [switch]$Apply,
    [switch]$AllowNonMain,
    [switch]$AlertApply,
    [switch]$StateApply,
    [switch]$AlertSelfTest
)

$ErrorActionPreference = "Stop"

function Write-AiosLine {
    param([string]$Status, [string]$Message)
    Write-Host "$Status`t$Message"
}

function ConvertTo-AiosAlertMarkdown {
    param([object]$BridgeState)

    $status = [string]$BridgeState.night_supervisor_status
    if ([string]::IsNullOrWhiteSpace($status)) { $status = [string]$BridgeState.supervisor_status }
    if ([string]::IsNullOrWhiteSpace($status)) { $status = "UNKNOWN" }

    $summary = [string]$BridgeState.plain_summary
    if ([string]::IsNullOrWhiteSpace($summary)) { $summary = "No summary available." }

    $approvalCount = [string]$BridgeState.approval_needed_count
    if ([string]::IsNullOrWhiteSpace($approvalCount)) { $approvalCount = "UNKNOWN" }

    $nextAction = [string]$BridgeState.next_safe_action
    if ([string]::IsNullOrWhiteSpace($nextAction)) { $nextAction = "Review bridge state before taking action." }

    $generatedAt = [string]$BridgeState.generated_at
    if ([string]::IsNullOrWhiteSpace($generatedAt)) {
        $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
    $mustSeeItems = @($BridgeState.must_see)
    $statusUpper = $status.ToUpperInvariant()

    if ($statusUpper -in @("BLOCKED", "NEEDS_APPROVAL")) {
        $lines = @(
            "# AI_OS ALERT - $statusUpper",
            "",
            "- Plain summary: $summary",
            "- Waiting approvals: $approvalCount",
            "- Must see:"
        )

        if ($mustSeeItems.Count -gt 0) {
            foreach ($item in $mustSeeItems) {
                $lines += "  - $item"
            }
        } else {
            $lines += "  - No must-see items reported."
        }

        $lines += @(
            "- Next safe action: $nextAction",
            "- Generated: $generatedAt"
        )

        return ($lines -join "`r`n") + "`r`n"
    }

    return "No blockers - $summary`r`n"
}

function Test-AiosAlertRenderer {
    $samples = @(
        [pscustomobject]@{
            name = "blocked"
            state = [pscustomobject]@{
                night_supervisor_status = "BLOCKED"
                plain_summary = "1 item blocked."
                approval_needed_count = 0
                must_see = @("Blocked sample item.")
                next_safe_action = "Review blocker."
                generated_at = "2026-05-31T00:00:00Z"
            }
        },
        [pscustomobject]@{
            name = "needs_approval"
            state = [pscustomobject]@{
                night_supervisor_status = "NEEDS_APPROVAL"
                plain_summary = "1 approval waiting."
                approval_needed_count = 1
                must_see = @("Approval sample item.")
                next_safe_action = "Approve or reject."
                generated_at = "2026-05-31T00:00:00Z"
            }
        },
        [pscustomobject]@{
            name = "pass"
            state = [pscustomobject]@{
                night_supervisor_status = "PASS"
                plain_summary = "No blockers found."
                approval_needed_count = 0
                must_see = @()
                next_safe_action = "Continue."
                generated_at = "2026-05-31T00:00:00Z"
            }
        }
    )

    foreach ($sample in $samples) {
        $alert = ConvertTo-AiosAlertMarkdown -BridgeState $sample.state
        $fires = $alert.StartsWith("# AI_OS ALERT")
        Write-AiosLine "SELFTEST" "$($sample.name): fires=$fires first_line=$($alert.Split("`n")[0].Trim())"
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$forbiddenOutputTerms = @(".env", "secrets", "credentials", "broker", "OANDA", "live webhook", "real order")
$pythonModule = Join-Path $repoRoot "services\python_supervisor\autonomy_bridge.py"
$alertOutput = "relay/reports/ALERT_LATEST.md"

if ($AlertSelfTest) {
    Test-AiosAlertRenderer
    exit 0
}

Set-Location $repoRoot
$branch = (& git branch --show-current).Trim()
$gitStatus = (& git status --short --branch) -join "`n"

Write-AiosLine "INFO" "repo_path=$repoRoot"
Write-AiosLine "INFO" "branch=$branch"
Write-AiosLine "INFO" "mode=$(if ($Apply) { 'APPLY' } elseif ($AlertApply -or $StateApply) { 'PARTIAL_APPLY' } else { 'DRY_RUN' })"

if ($branch -ne "main" -and -not $AllowNonMain) {
    Write-AiosLine "BLOCKED" "Autonomy Bridge only runs on main unless -AllowNonMain is explicitly passed."
    exit 2
}

if (-not (Test-Path $pythonModule)) {
    Write-AiosLine "BLOCKED" "Missing Python bridge module: $pythonModule"
    exit 2
}

$plannedOutputs = @(
    "telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json",
    "telemetry/morning_digest/MORNING_DIGEST_STATE.json",
    "telemetry/morning_digest/MORNING_DIGEST_LATEST.md",
    $alertOutput
)

foreach ($output in $plannedOutputs) {
    foreach ($term in $forbiddenOutputTerms) {
        if ($output.ToLowerInvariant().Contains($term.ToLowerInvariant())) {
            Write-AiosLine "BLOCKED" "Forbidden output path term detected: $term in $output"
            exit 2
        }
    }
}

Write-AiosLine "INFO" "planned_outputs=$($plannedOutputs -join ', ')"

$argsList = @(
    $pythonModule,
    "--repo-root", $repoRoot,
    "--repo-branch", $branch,
    "--git-status", $gitStatus,
    "--pretty"
)

if ($Apply) {
    $argsList += "--apply"
}

$outputJson = & python @argsList
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-AiosLine "BLOCKED" "Python bridge returned exit code $exitCode"
    Write-Output $outputJson
    exit $exitCode
}

$receipt = $outputJson | ConvertFrom-Json
if (-not $receipt.bridge_state.dashboard_cards -or $receipt.bridge_state.dashboard_cards.Count -lt 1) {
    Write-AiosLine "BLOCKED" "Bridge output did not include dashboard_cards."
    exit 2
}

$alertMarkdown = ConvertTo-AiosAlertMarkdown -BridgeState $receipt.bridge_state
$alertPath = Join-Path $repoRoot $alertOutput
$bridgeStateOutput = "telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json"
$bridgeStatePath = Join-Path $repoRoot $bridgeStateOutput

if ($StateApply -and -not $Apply) {
    $stateDir = Split-Path -Parent $bridgeStatePath
    if (-not (Test-Path $stateDir)) {
        New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
    }
    $receipt.bridge_state | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $bridgeStatePath -Encoding UTF8
    Write-AiosLine "PASS" "bridge_state_written=$bridgeStateOutput"
}

if ($Apply -or $AlertApply) {
    $alertDir = Split-Path -Parent $alertPath
    if (-not (Test-Path $alertDir)) {
        New-Item -ItemType Directory -Path $alertDir -Force | Out-Null
    }
    Set-Content -LiteralPath $alertPath -Value $alertMarkdown -Encoding UTF8
    Write-AiosLine "PASS" "alert_written=$alertOutput"
} else {
    Write-AiosLine "PASS" "alert_preview=$alertOutput"
}

Write-AiosLine "PASS" "autonomy_bridge_status=$($receipt.status)"
Write-AiosLine "PASS" "planned_output_paths=$($receipt.planned_output_paths -join ', ')"
if ($Apply) {
    Write-AiosLine "PASS" "written_output_paths=$($receipt.written_output_paths -join ', ')"
} elseif ($AlertApply -or $StateApply) {
    Write-AiosLine "PASS" "bridge DRY_RUN only; partial local outputs written."
} else {
    Write-AiosLine "PASS" "DRY_RUN only; no files written."
}

$outputJson
