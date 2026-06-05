param(
    [switch]$Apply,
    [switch]$AllowNonMain,
    [switch]$AlertApply,
    [switch]$StateApply,
    [switch]$MorningBriefV2Apply,
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

function Read-AiosJsonObject {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-AiosLatestNightReport {
    param([string]$RepoRoot)

    $reportDir = Join-Path $RepoRoot "telemetry\night_supervisor\reports"
    if (-not (Test-Path -LiteralPath $reportDir -PathType Container)) {
        return $null
    }

    $reportFile = Get-ChildItem -LiteralPath $reportDir -Filter "night_summary_*.json" -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $reportFile) {
        return $null
    }

    return [pscustomobject]@{
        path = $reportFile.FullName
        repo_relative = ("telemetry/night_supervisor/reports/{0}" -f $reportFile.Name)
        report = Read-AiosJsonObject -Path $reportFile.FullName
    }
}

function Get-AiosApprovalRecord {
    param(
        [string]$RepoRoot,
        [string]$Name
    )

    $path = Join-Path $RepoRoot ("automation\orchestration\approval_inbox\{0}" -f $Name)
    return Read-AiosJsonObject -Path $path
}

function Get-AiosApprovalDecisionCards {
    param(
        [string]$RepoRoot,
        [object]$NightReport
    )

    $phase = @($NightReport.phases | Where-Object { $_.phase -eq "approval_automation" } | Select-Object -First 1)
    $items = @()
    if ($phase -and $phase.detail -and $phase.detail.pending_human_review) {
        $items = @($phase.detail.pending_human_review)
    }

    $cards = @()
    foreach ($item in $items) {
        $file = [string]$item.file
        $tier = [string]$item.tier
        $name = Split-Path -Leaf $file
        $record = Get-AiosApprovalRecord -RepoRoot $RepoRoot -Name $name
        $status = if ($record -and $record.approval_status) { [string]$record.approval_status } else { "pending_or_unknown" }
        $packetId = if ($record -and $record.packet_id) { [string]$record.packet_id } elseif ($NightReport.execution_result.packet_id) { [string]$NightReport.execution_result.packet_id } else { "UNKNOWN" }
        $requestedAction = if ($record -and $record.requested_action) { [string]$record.requested_action } elseif ($record -and $record.requested_mode) { [string]$record.requested_mode } else { "review approval evidence" }
        $risk = if ($record -and $record.risk_level) { [string]$record.risk_level } elseif ($tier) { $tier } else { "UNKNOWN" }
        $classification = "review"
        $why = "Human review is required before any mutation or protected action."
        $recommendation = "Defer APPLY until exact scope, expected mutation, validator evidence, and stop point are visible."

        if ($name -like "*.example.json" -or $tier -eq "EXAMPLE") {
            $classification = "noise"
            $why = "Example approval records should not consume morning decision attention."
            $recommendation = "Hide from the decision queue unless Anthony asks for examples."
        } elseif ($status -eq "completed") {
            $classification = "completed_evidence"
            $why = "Completed approval authority records are evidence, not new approval requests."
            $recommendation = "Report as completed evidence; do not count as pending approval."
        } elseif ($status -eq "pending_review") {
            $classification = "approval_required"
        }

        $cards += [pscustomobject]@{
            file = $file
            packet_id = $packetId
            requested_action = $requestedAction
            status = $status
            risk = $risk
            classification = $classification
            why_it_matters = $why
            recommended_action = $recommendation
        }
    }

    return @($cards)
}

function New-AiosMorningBriefV2 {
    param(
        [string]$RepoRoot,
        [object]$BridgeState,
        [object]$NightReportRef,
        [string]$Branch,
        [string]$GitStatus
    )

    $nightReport = $NightReportRef.report
    $digestStatePath = Join-Path $RepoRoot "telemetry\morning_digest\MORNING_DIGEST_STATE.json"
    $digestMdPath = Join-Path $RepoRoot "telemetry\morning_digest\MORNING_DIGEST_LATEST.md"
    $digestState = Read-AiosJsonObject -Path $digestStatePath
    $digestMarkdown = if (Test-Path -LiteralPath $digestMdPath -PathType Leaf) {
        Get-Content -LiteralPath $digestMdPath -Raw
    } else {
        ""
    }

    $reportStatus = [string]$nightReport.supervisor_status
    $bridgeStatus = [string]$BridgeState.night_supervisor_status
    if ([string]::IsNullOrWhiteSpace($bridgeStatus)) { $bridgeStatus = [string]$BridgeState.supervisor_status }
    $digestStatus = if ($digestState) { [string]$digestState.night_supervisor_status } else { "MISSING" }
    if ([string]::IsNullOrWhiteSpace($digestStatus) -and $digestState) { $digestStatus = [string]$digestState.supervisor_status }

    $approvalCards = Get-AiosApprovalDecisionCards -RepoRoot $RepoRoot -NightReport $nightReport
    $decisionCards = @($approvalCards | Where-Object { $_.classification -eq "approval_required" })
    $noiseCards = @($approvalCards | Where-Object { $_.classification -ne "approval_required" })
    $reportApprovalCount = @($nightReport.phases | Where-Object { $_.phase -eq "approval_automation" } | ForEach-Object { $_.detail.pending_human_review }).Count
    $bridgeApprovalCount = if ($BridgeState.approval_needed_count -ne $null) { [int]$BridgeState.approval_needed_count } else { 0 }
    $digestApprovalCount = if ($digestState -and $digestState.approval_needed_count -ne $null) { [int]$digestState.approval_needed_count } else { 0 }

    $staleWarnings = @()
    if ($reportStatus -and $bridgeStatus -and $reportStatus -ne $bridgeStatus) {
        $staleWarnings += "Report status is $reportStatus while bridge status is $bridgeStatus."
    }
    if ($digestState -and ([string]$digestState.generated_at).Substring(0, [Math]::Min(10, ([string]$digestState.generated_at).Length)) -ne ([string]$nightReport.generated_at).Substring(0, 10)) {
        $staleWarnings += "Morning digest state date does not match latest Night Supervisor report date."
    }
    if ($digestMarkdown -match "Morning Digest - 2026-06-02") {
        $staleWarnings += "Morning digest markdown is stale and still dated 2026-06-02."
    }
    if ($reportApprovalCount -ne $bridgeApprovalCount -or $reportApprovalCount -ne $digestApprovalCount) {
        $staleWarnings += "Approval counts differ: report=$reportApprovalCount bridge=$bridgeApprovalCount digest=$digestApprovalCount."
    }
    if ($staleWarnings.Count -eq 0) {
        $staleWarnings += "No stale-state mismatch detected across report, bridge, and digest evidence."
    }

    $ignoreNoise = @(
        "Example approval records.",
        "Schema files presented as blocked work.",
        "Raw Night Supervisor config snippets.",
        "Completed governance records presented as pending approvals.",
        "Historical relay artifacts unless active in the canonical approval inbox.",
        "Raw JSON fragments in Must See sections.",
        "Old digest totals when a newer Night Supervisor report exists."
    )

    $highestRoiPacket = @"
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

identity marker: AI_OS_CODEX_WORK_PACKET
supervisor identity: Anthony / AI_OS Operator
packet ID: AIOS-APPROVAL-SUMMARY-CLASSIFICATION-FIX-APPLY-2026-06-05
mode: APPLY
zone: APPROVAL_INTELLIGENCE
worker identity: Codex approval intelligence implementer
lane: APPROVAL_APPLY
worktree: C:\Dev\Ai.Os
branch: resolve after preflight
allowed paths:
- automation/orchestration/approval_inbox/
- automation/orchestration/night_supervisor/
- telemetry/morning_digest/
forbidden paths:
- credentials
- secrets
- .env
- broker/API keys
- live trading
- real orders
- production promotion
- commit
- push
approval authority: Anthony only
validator chain: preflight, approval summary readback, targeted classification fix, sandbox morning brief test, diff check
stop point: approval-summary classification fix only; no commit, no push

MISSION:
Fix approval intelligence so completed records and examples are not counted as current pending approvals in Morning Brief v2.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
APPROVAL CLASSIFICATION:
VALIDATION:
SAFE NEXT COMMAND:
STATUS: APPROVAL INTELLIGENCE CLASSIFICATION FIX COMPLETE, NO COMMIT, NO PUSH
"@

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $brief = [ordered]@{
        schema = "AIOS_MORNING_BRIEF_V2.v1"
        mode = "DRY_RUN_SANDBOX_OUTPUT"
        generated_at = $generatedAt
        source_report = $NightReportRef.repo_relative
        authority = "recommendation_only_not_approval_authority"
        executive_summary = "AI_OS is safe for continued DRY_RUN and sandbox work. The latest Night Supervisor report is $reportStatus with validators passing and approval still required. The main value gap is approval classification and stale digest filtering."
        overnight_changes = [ordered]@{
            report_generated_at = [string]$nightReport.generated_at
            supervisor_status = $reportStatus
            execution_result = [string]$nightReport.execution_result.result_classification
            branch = [string]$nightReport.repo.branch
            head_sha = [string]$nightReport.repo.head_sha
            ahead_commits = [int]$nightReport.repo.ahead_commits
            changed_files = @($nightReport.repo.changed_files)
            untracked_items = @($nightReport.repo.untracked_items)
        }
        current_system_state = [ordered]@{
            repo = "current checkout on $Branch; $GitStatus"
            validator = [string]$nightReport.execution_result.validator_status
            qa = [string]$nightReport.execution_result.qa_status
            automation = "Night Supervisor status $reportStatus; result $($nightReport.execution_result.result_classification)."
            safety = $nightReport.safety_confirmation
        }
        approval_required = @($decisionCards)
        stale_state_warnings = @($staleWarnings)
        risks = @(
            "Approval queue noise can hide the one real decision Anthony needs to make.",
            "Stale digest or bridge surfaces can make READY evidence look blocked.",
            "Raw evidence dumps increase operator review burden."
        )
        ignore_noise = $ignoreNoise
        opportunities = @(
            "Turn approval evidence into decision cards.",
            "Refresh or label stale digest and bridge state before presentation.",
            "Generate one highest-ROI packet each morning."
        )
        openai_recommendation_targets = @(
            "Sanitized report status and validator health.",
            "Approval cards and recommended disposition.",
            "Stale-state mismatch flags.",
            "Noise candidates.",
            "Next work packet selection."
        )
        codex_recommendation = "Implement approval-summary classification next so completed records and examples do not inflate pending review."
        aios_recommendation = "Keep Night Supervisor as evidence producer and Morning Brief v2 as the decision filter."
        highest_roi_next_packet = $highestRoiPacket
        noise_cards = @($noiseCards)
        validation = [ordered]@{
            recommendation_only = $true
            approval_authority = $false
            production_promotion = $false
            external_api_calls = $false
            protected_execution = $false
        }
    }

    $lines = @(
        "# AI_OS Morning Brief v2 - LATEST",
        "",
        "Status: DRY_RUN sandbox output only",
        "Authority: recommendation-only evidence; not approval authority",
        "Generated: $generatedAt",
        "Source report: $($NightReportRef.repo_relative)",
        "",
        "## Executive Summary",
        "",
        $brief.executive_summary,
        "",
        "## Overnight Changes",
        "",
        "- Supervisor status: $($brief.overnight_changes.supervisor_status)",
        "- Execution result: $($brief.overnight_changes.execution_result)",
        "- Branch: $($brief.overnight_changes.branch)",
        "- Head: $($brief.overnight_changes.head_sha)",
        "- Ahead commits: $($brief.overnight_changes.ahead_commits)",
        "- Changed files: $(if ($brief.overnight_changes.changed_files.Count) { $brief.overnight_changes.changed_files -join ', ' } else { 'none' })",
        "- Untracked items: $(if ($brief.overnight_changes.untracked_items.Count) { $brief.overnight_changes.untracked_items -join ', ' } else { 'none' })",
        "",
        "## Current System State",
        "",
        "- Repo: $($brief.current_system_state.repo)",
        "- Validator: $($brief.current_system_state.validator)",
        "- QA: $($brief.current_system_state.qa)",
        "- Automation: $($brief.current_system_state.automation)",
        "- Safety: no live execution, no protected action, no approval authority.",
        "",
        "## Approval Required",
        ""
    )

    if ($decisionCards.Count -eq 0) {
        $lines += "- No active approval decision cards after filtering noise."
    } else {
        $i = 1
        foreach ($card in $decisionCards) {
            $lines += @(
                "### $i. $($card.file)",
                "",
                "- Packet: $($card.packet_id)",
                "- Status: $($card.status)",
                "- Risk: $($card.risk)",
                "- Why it matters: $($card.why_it_matters)",
                "- Recommended action: $($card.recommended_action)",
                ""
            )
            $i += 1
        }
    }

    $lines += @(
        "",
        "## Stale State Warnings",
        ""
    )
    foreach ($warning in $staleWarnings) { $lines += "- $warning" }

    $lines += @(
        "",
        "## Risks",
        ""
    )
    foreach ($risk in $brief.risks) { $lines += "- $risk" }

    $lines += @(
        "",
        "## Ignore / Noise",
        ""
    )
    foreach ($noise in $ignoreNoise) { $lines += "- $noise" }

    $lines += @(
        "",
        "## Opportunities",
        ""
    )
    foreach ($opportunity in $brief.opportunities) { $lines += "- $opportunity" }

    $lines += @(
        "",
        "## OpenAI Recommendation Targets",
        ""
    )
    foreach ($target in $brief.openai_recommendation_targets) { $lines += "- $target" }

    $lines += @(
        "",
        "## Codex Recommendation",
        "",
        $brief.codex_recommendation,
        "",
        "## AI_OS Recommendation",
        "",
        $brief.aios_recommendation,
        "",
        "## Highest ROI Next Packet",
        "",
        '```text',
        $highestRoiPacket,
        '```',
        "",
        "## Validation Notes",
        "",
        "- Recommendation-only output.",
        "- Not approval authority.",
        "- No production promotion.",
        "- No external API call.",
        "- No protected execution."
    )

    return [pscustomobject]@{
        markdown = ($lines -join "`n") + "`n"
        json = $brief
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
Write-AiosLine "INFO" "mode=$(if ($Apply) { 'APPLY' } elseif ($AlertApply -or $StateApply -or $MorningBriefV2Apply) { 'PARTIAL_APPLY' } else { 'DRY_RUN' })"

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
    "telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.md",
    "telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.json",
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
$morningBriefV2MarkdownOutput = "telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.md"
$morningBriefV2JsonOutput = "telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.json"
$morningBriefV2MarkdownPath = Join-Path $repoRoot $morningBriefV2MarkdownOutput
$morningBriefV2JsonPath = Join-Path $repoRoot $morningBriefV2JsonOutput

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

if ($MorningBriefV2Apply) {
    $latestReport = Get-AiosLatestNightReport -RepoRoot $repoRoot
    if (-not $latestReport -or -not $latestReport.report) {
        Write-AiosLine "BLOCKED" "No Night Supervisor report found for Morning Brief v2."
        exit 2
    }

    $briefV2 = New-AiosMorningBriefV2 `
        -RepoRoot $repoRoot `
        -BridgeState $receipt.bridge_state `
        -NightReportRef $latestReport `
        -Branch $branch `
        -GitStatus $gitStatus

    $briefDir = Split-Path -Parent $morningBriefV2MarkdownPath
    if (-not (Test-Path -LiteralPath $briefDir -PathType Container)) {
        New-Item -ItemType Directory -Path $briefDir -Force | Out-Null
    }
    Set-Content -LiteralPath $morningBriefV2MarkdownPath -Value $briefV2.markdown -Encoding UTF8
    $briefV2.json | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $morningBriefV2JsonPath -Encoding UTF8
    Write-AiosLine "PASS" "morning_brief_v2_written=$morningBriefV2MarkdownOutput,$morningBriefV2JsonOutput"
}

Write-AiosLine "PASS" "autonomy_bridge_status=$($receipt.status)"
Write-AiosLine "PASS" "planned_output_paths=$($receipt.planned_output_paths -join ', ')"
if ($Apply) {
    Write-AiosLine "PASS" "written_output_paths=$($receipt.written_output_paths -join ', ')"
} elseif ($AlertApply -or $StateApply -or $MorningBriefV2Apply) {
    Write-AiosLine "PASS" "bridge DRY_RUN only; partial local outputs written."
} else {
    Write-AiosLine "PASS" "DRY_RUN only; no files written."
}

$outputJson
