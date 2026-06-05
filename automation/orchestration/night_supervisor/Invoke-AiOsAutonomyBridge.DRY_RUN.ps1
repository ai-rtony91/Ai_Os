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
    $bridgeStatus = [string]$BridgeState.bridge_status
    if ([string]::IsNullOrWhiteSpace($bridgeStatus)) { $bridgeStatus = [string]$BridgeState.night_supervisor_status }
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
    $bridgeRefinesReadyToApproval = ($reportStatus -eq "READY" -and $bridgeStatus -eq "NEEDS_APPROVAL" -and $decisionCards.Count -gt 0)
    if ($reportStatus -and $bridgeStatus -and $reportStatus -ne $bridgeStatus -and -not $bridgeRefinesReadyToApproval) {
        $staleWarnings += "Report status is $reportStatus while bridge status is $bridgeStatus."
    }
    if ($digestState -and ([string]$digestState.generated_at).Substring(0, [Math]::Min(10, ([string]$digestState.generated_at).Length)) -ne ([string]$nightReport.generated_at).Substring(0, 10)) {
        $staleWarnings += "Morning digest state date does not match latest Night Supervisor report date."
    }
    if ($digestMarkdown -match "Morning Digest - 2026-06-02") {
        $staleWarnings += "Morning digest markdown is stale and still dated 2026-06-02."
    }
    if ($decisionCards.Count -ne $bridgeApprovalCount -or $decisionCards.Count -ne $digestApprovalCount) {
        $staleWarnings += "Approval counts differ after noise filtering: active=$($decisionCards.Count) bridge=$bridgeApprovalCount digest=$digestApprovalCount."
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
        status = $bridgeStatus
        supervisor_status = $reportStatus
        execution_result = [string]$nightReport.execution_result.result_classification
        recommendation_only = $true
        generated_at = $generatedAt
        source_report = $NightReportRef.repo_relative
        authority = "recommendation_only_not_approval_authority"
        executive_summary = "AI_OS is safe for continued DRY_RUN and sandbox work. The latest Night Supervisor report is $reportStatus, bridge status is $bridgeStatus, validators pass, and active approvals are filtered to current decision cards."
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
        active_decision_cards = @($BridgeState.active_decision_cards)
        current_blockers = @($BridgeState.current_blockers)
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
        noise_cards = @($noiseCards + @($BridgeState.noise_cards))
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

function New-AiosApprovalIntelligenceV2 {
    param(
        [object]$BridgeState,
        [object]$MorningBriefV2
    )

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $sourceCards = @()
    if ($BridgeState -and $BridgeState.active_decision_cards) {
        $sourceCards += @($BridgeState.active_decision_cards)
    }
    if ($sourceCards.Count -eq 0 -and $MorningBriefV2 -and $MorningBriefV2.json -and $MorningBriefV2.json.active_decision_cards) {
        $sourceCards += @($MorningBriefV2.json.active_decision_cards)
    }

    $decisionCards = @()
    foreach ($card in $sourceCards) {
        $title = if ($card.title) { [string]$card.title } else { Split-Path -Leaf ([string]$card.file) }
        if ([string]::IsNullOrWhiteSpace($title)) { $title = "Approval decision" }
        $packetId = [string]$card.packet_id
        $requestedAction = [string]$card.requested_action
        $status = [string]$card.status
        $risk = [string]$card.risk
        $classification = [string]$card.classification
        if ([string]::IsNullOrWhiteSpace($classification)) { $classification = "ACTIVE_APPROVAL_REQUIRED" }

        $recommendedDisposition = "defer"
        $reason = "Defer until exact scope, intended mutation, validator evidence, affected file list, and stop point are visible."
        $missingEvidence = @(
            "Exact intended mutation.",
            "Exact files to change.",
            "Validator chain proof.",
            "Commit package or explicit no-commit boundary.",
            "Stop point.",
            "Evidence that this approval is not stale or superseded by newer governance changes."
        )
        $allowedPaths = @("unknown_from_active_bridge_evidence")
        $blockedPaths = @(
            "approval mutation",
            "automation/orchestration/approval_inbox/",
            "secrets",
            ".env",
            "broker/API keys",
            "live trading",
            "real orders",
            "real webhooks",
            "production promotion",
            "commit",
            "push"
        )

        if ($title -eq "APPLY_APPROVAL_GATE_001.json" -or ([string]$card.file) -like "*APPLY_APPROVAL_GATE_001.json") {
            $recommendedDisposition = "defer"
            $reason = "Approval record is current, but the underlying packet is old, broad, and missing exact file list, mutation details, validator evidence, and stop point."
            $allowedPaths = @(
                "automation/orchestration/",
                "docs/concepts/",
                "docs/workflows/",
                "docs/architecture/",
                "docs/audits/"
            )
            $blockedPaths = @(
                "automation/operator/",
                "Reports/security/",
                "apps/dashboard/",
                "automation/telemetry/",
                "Reports/telemetry/",
                "README.md",
                "RISK_POLICY.md",
                "SOURCE_LOG.md",
                "ERROR_LOG.md",
                "HALLUCINATION_LOG.md",
                "AAR.md",
                "DAILY_REPORT.md",
                "ARCHITECTURE.md",
                "DEPLOYMENT.md",
                "WHITEPAPER.md",
                "broker/",
                "OANDA/",
                "api_keys/",
                "live_trading/"
            )
        }

        $decisionCards += [ordered]@{
            title = $title
            source_path = [string]$card.source_path
            status = $status
            current_stale_noise_classification = $classification
            requested_action = $requestedAction
            current_allowed_state = "DRY_RUN_ONLY until Human Owner approval is explicit."
            risk = $risk
            blast_radius = "medium: scoped repo mutation request requiring Human Owner review before APPLY."
            affected_allowed_paths = $allowedPaths
            blocked_protected_paths = $blockedPaths
            required_missing_evidence = $missingEvidence
            recommended_disposition = $recommendedDisposition
            reason = $reason
            safest_next_action = "Defer APPLY; run a fresh DRY_RUN review or generate a narrower APPLY packet with exact scope and validation."
            recommendation_only = $true
            approval_mutation = $false
        }
    }

    $json = [ordered]@{
        schema = "AIOS_APPROVAL_INTELLIGENCE_V2.v1"
        mode = "DRY_RUN_SANDBOX_OUTPUT"
        generated_at = $generatedAt
        recommendation_only = $true
        approval_authority = $false
        approval_mutation = $false
        source = "Bridge/Morning Brief active approval evidence."
        active_approval_cards = $decisionCards
        noise_cards_seen = if ($MorningBriefV2 -and $MorningBriefV2.json -and $MorningBriefV2.json.noise_cards) { @($MorningBriefV2.json.noise_cards).Count } else { 0 }
        stale_state_warnings = if ($MorningBriefV2 -and $MorningBriefV2.json -and $MorningBriefV2.json.stale_state_warnings) { @($MorningBriefV2.json.stale_state_warnings) } else { @() }
        validation = [ordered]@{
            no_approval_mutation = $true
            no_external_api_call = $true
            no_secrets = $true
            no_broker_api = $true
            no_live_trading = $true
            no_production_promotion = $true
            no_commit_or_push = $true
        }
    }

    $lines = @(
        "# Approval Intelligence v2 - LATEST",
        "",
        "Status: DRY_RUN sandbox output only",
        "Authority: recommendation-only evidence; not approval authority",
        "Generated: $generatedAt",
        "",
        "## Summary",
        "",
        "Approval Intelligence v2 converts active approval evidence into human decision cards. It does not approve, reject, defer, or mutate approval state.",
        "",
        "## Active Approval Cards",
        ""
    )

    if ($decisionCards.Count -eq 0) {
        $lines += "- No active approval cards found in current Bridge/Morning Brief evidence."
    } else {
        $index = 1
        foreach ($decision in $decisionCards) {
            $lines += @(
                "### $index. $($decision.title)",
                "",
                "- Status: $($decision.status)",
                "- Classification: $($decision.current_stale_noise_classification)",
                "- Requested action: $($decision.requested_action)",
                "- Current allowed state: $($decision.current_allowed_state)",
                "- Risk: $($decision.risk)",
                "- Blast radius: $($decision.blast_radius)",
                "- Recommended disposition: $($decision.recommended_disposition)",
                "- Reason: $($decision.reason)",
                "- Safest next action: $($decision.safest_next_action)",
                "- Recommendation only: true",
                "- No approval mutation: true",
                "",
                "Affected allowed paths:",
                ""
            )
            foreach ($path in @($decision.affected_allowed_paths)) {
                $lines += "- $path"
            }
            $lines += @(
                "",
                "Missing evidence:",
                ""
            )
            foreach ($item in @($decision.required_missing_evidence)) {
                $lines += "- $item"
            }
            $lines += ""
            $index += 1
        }
    }

    $lines += @(
        "## Validation Notes",
        "",
        "- recommendation_only: true",
        "- no approval mutation",
        "- no external API call",
        "- no secrets",
        "- no broker/API",
        "- no live trading",
        "- no production promotion",
        "- no commit or push"
    )

    return [pscustomobject]@{
        markdown = ($lines -join "`n") + "`n"
        json = $json
    }
}

function New-AiosPi5ProgressReport {
    param(
        [object]$BridgeState,
        [object]$MorningBriefV2,
        [object]$ApprovalIntelligenceV2,
        [object]$NightReportRef,
        [object]$ForexProfile,
        [string]$ForexReadme,
        [string]$Branch,
        [string]$GitStatus
    )

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $nightReport = $NightReportRef.report
    $execution = $nightReport.execution_result
    $safety = $nightReport.safety_confirmation
    $supervisorStatus = [string]$nightReport.supervisor_status
    $bridgeStatus = [string]$BridgeState.bridge_status
    if ([string]::IsNullOrWhiteSpace($bridgeStatus)) { $bridgeStatus = [string]$BridgeState.night_supervisor_status }
    if ([string]::IsNullOrWhiteSpace($bridgeStatus)) { $bridgeStatus = [string]$MorningBriefV2.json.status }

    $currentBlockers = @($BridgeState.current_blockers)
    $approvalCards = @()
    if ($ApprovalIntelligenceV2 -and $ApprovalIntelligenceV2.json -and $ApprovalIntelligenceV2.json.active_approval_cards) {
        $approvalCards += @($ApprovalIntelligenceV2.json.active_approval_cards)
    } elseif ($MorningBriefV2 -and $MorningBriefV2.json -and $MorningBriefV2.json.active_decision_cards) {
        $approvalCards += @($MorningBriefV2.json.active_decision_cards)
    } elseif ($BridgeState -and $BridgeState.active_decision_cards) {
        $approvalCards += @($BridgeState.active_decision_cards)
    }

    $blockersCount = $currentBlockers.Count
    $activeApprovalCount = $approvalCards.Count
    $validatorPass = ([string]$execution.validator_status) -eq "PASS"
    $qaPass = ([string]$execution.qa_status) -eq "PASS"
    $forbiddenWriteAttempts = if ($safety -and $safety.forbidden_write_attempts -ne $null) { [int]$safety.forbidden_write_attempts } else { 0 }
    $alertsCount = @($nightReport.alerts).Count

    $nightSupervisorHealthPercent = if ($supervisorStatus -eq "READY" -and $alertsCount -eq 0 -and $forbiddenWriteAttempts -eq 0) { 95 } elseif ($supervisorStatus -eq "NEEDS_APPROVAL") { 80 } elseif ($supervisorStatus -eq "BLOCKED") { 20 } else { 50 }
    $validationHealthPercent = if ($validatorPass -and $qaPass -and $forbiddenWriteAttempts -eq 0) { 100 } elseif ($validatorPass -or $qaPass) { 65 } else { 25 }
    $approvalClearancePercent = if ($activeApprovalCount -eq 0) { 100 } else { [Math]::Max(0, 100 - ($activeApprovalCount * 40)) }
    $workerReadinessPercent = if ($blockersCount -gt 0) { 25 } elseif ($activeApprovalCount -gt 0) { 75 } elseif ($execution.packet_selected -eq $true -and $validatorPass -and $qaPass) { 90 } else { 50 }

    $forexStatus = if ($ForexProfile -and $ForexProfile.status) { [string]$ForexProfile.status } else { "UNKNOWN" }
    $forexMode = if ($ForexProfile -and $ForexProfile.mode) { [string]$ForexProfile.mode } else { "UNKNOWN" }
    $forexHourlyPlanCount = if ($ForexProfile -and $ForexProfile.hourly_plan) { @($ForexProfile.hourly_plan).Count } else { 0 }
    $forexBotBuildPercent = if ($forexStatus -eq "REPORT_ONLY_PROFILE" -and $forexHourlyPlanCount -gt 0) { 15 } elseif ($forexStatus -eq "REPORT_ONLY_PROFILE") { 10 } else { 0 }
    $safetyHealthPercent = if (
        $safety -and
        $safety.no_live_trading -eq $true -and
        $safety.no_broker_execution -eq $true -and
        $safety.no_secrets_exposed -eq $true -and
        $forbiddenWriteAttempts -eq 0
    ) { 100 } else { 25 }
    $overallAiosProgressPercent = [int][Math]::Round(
        ($nightSupervisorHealthPercent * 0.25) +
        ($validationHealthPercent * 0.20) +
        ($approvalClearancePercent * 0.15) +
        ($workerReadinessPercent * 0.15) +
        ($forexBotBuildPercent * 0.10) +
        ($safetyHealthPercent * 0.15),
        0
    )

    $humanInteractionRequired = ($blockersCount -gt 0 -or $activeApprovalCount -gt 0)
    $currentPhase = if ($blockersCount -gt 0) {
        "current blocker review"
    } elseif ($activeApprovalCount -gt 0) {
        "approval decision required"
    } elseif ($supervisorStatus -eq "READY") {
        "ready for DRY_RUN or sandbox work"
    } else {
        "status review"
    }
    $nextSafeAction = if ($MorningBriefV2 -and $MorningBriefV2.json -and $MorningBriefV2.json.active_decision_cards -and $activeApprovalCount -gt 0) {
        "Review Approval Intelligence v2 decision card; defer broad APPLY until exact scope and validator evidence are available."
    } elseif ($BridgeState -and $BridgeState.next_safe_action) {
        [string]$BridgeState.next_safe_action
    } else {
        "Review latest Morning Brief v2 before taking action."
    }

    $displayCards = @(
        [ordered]@{
            title = "Main Status"
            status = $bridgeStatus
            percent = $overallAiosProgressPercent
            summary = "AI_OS is $bridgeStatus with $blockersCount blocker(s) and $activeApprovalCount active approval(s)."
            next_safe_action = $nextSafeAction
        },
        [ordered]@{
            title = "Night Supervisor"
            status = $supervisorStatus
            percent = $nightSupervisorHealthPercent
            summary = "Latest Night Supervisor report is $supervisorStatus; validator=$($execution.validator_status); qa=$($execution.qa_status)."
            source = $NightReportRef.repo_relative
        },
        [ordered]@{
            title = "Approval Intelligence"
            status = if ($activeApprovalCount -gt 0) { "NEEDS_APPROVAL" } else { "CLEAR" }
            percent = $approvalClearancePercent
            summary = "$activeApprovalCount active recommendation-only approval card(s)."
            next_safe_action = "Approve, reject, or defer only through the canonical approval process; Pi5 display has no approval authority."
        },
        [ordered]@{
            title = "Forex Paper Lab"
            status = $forexStatus
            percent = $forexBotBuildPercent
            summary = "REPORT_ONLY_PROFILE / paper simulation planning only. No broker, OANDA, real market data, live bot, or real orders."
            mode = $forexMode
        },
        [ordered]@{
            title = "Worker Readiness"
            status = if ($blockersCount -gt 0) { "BLOCKED" } elseif ($activeApprovalCount -gt 0) { "WAITING_APPROVAL" } else { "READY" }
            percent = $workerReadinessPercent
            summary = "Worker evidence is display-only; worker_launch remains disabled unless a separate approved packet allows it."
        },
        [ordered]@{
            title = "Validation Health"
            status = if ($validatorPass -and $qaPass) { "PASS" } else { "REVIEW" }
            percent = $validationHealthPercent
            summary = "Validator=$($execution.validator_status); QA=$($execution.qa_status); forbidden_write_attempts=$forbiddenWriteAttempts."
        },
        [ordered]@{
            title = "Human Needed"
            status = if ($humanInteractionRequired) { "YES" } else { "NO" }
            percent = if ($humanInteractionRequired) { 100 } else { 0 }
            summary = if ($humanInteractionRequired) { "Anthony action is needed for current approval/blocker review." } else { "No current human action required for read-only display state." }
        },
        [ordered]@{
            title = "Next Safe Action"
            status = "DISPLAY_ONLY"
            percent = 0
            summary = $nextSafeAction
        }
    )

    $json = [ordered]@{
        schema = "AIOS_PI5_PROGRESS_REPORT.v1"
        mode = "DRY_RUN_SANDBOX_OUTPUT"
        authority_boundary = [ordered]@{
            evidence_only = $true
            approval_authority = $false
            trading_authority = $false
            repo_mutation_authority = $false
            pi_service_authority = $false
            scheduler_authority = $false
            gpio_or_motor_authority = $false
        }
        overall_aios_progress_percent = $overallAiosProgressPercent
        forex_bot_build_percent = $forexBotBuildPercent
        night_supervisor_health_percent = $nightSupervisorHealthPercent
        worker_readiness_percent = $workerReadinessPercent
        approval_clearance_percent = $approvalClearancePercent
        validation_health_percent = $validationHealthPercent
        human_interaction_required = $humanInteractionRequired
        current_phase = $currentPhase
        next_safe_action = $nextSafeAction
        blockers_count = $blockersCount
        active_approval_count = $activeApprovalCount
        last_updated = $generatedAt
        source_evidence = [ordered]@{
            morning_brief_v2 = "telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.json"
            approval_intelligence_v2 = "telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.json"
            bridge_state = "telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json"
            night_supervisor_report = $NightReportRef.repo_relative
            forex_profile = "automation/orchestration/night_supervisor/FOREX_PAPER_LAB_12H_PROFILE.json"
        }
        repo_state = [ordered]@{
            branch = $Branch
            status_summary = $GitStatus
        }
        forex_display_rule = "REPORT_ONLY_PROFILE / paper simulation planning only. Do not imply live bot, broker connection, real market data, or real orders."
        stale_state_warnings = if ($MorningBriefV2 -and $MorningBriefV2.json -and $MorningBriefV2.json.stale_state_warnings) { @($MorningBriefV2.json.stale_state_warnings) } else { @() }
        display_cards = $displayCards
        validation = [ordered]@{
            no_pi_deployment = $true
            no_service_created = $true
            no_scheduler_created = $true
            no_gpio_or_motor_controls = $true
            no_approval_mutation = $true
            no_secrets = $true
            no_broker_api = $true
            no_live_trading = $true
            no_real_orders = $true
            no_real_webhooks = $true
            no_commit_or_push = $true
        }
    }

    $lines = @(
        "# Pi5 Progress Report - LATEST",
        "",
        "Status: display-only sandbox output",
        "Authority: evidence only; no approval, trading, repo mutation, Pi service, scheduler, GPIO, or motor authority",
        "Generated: $generatedAt",
        "",
        "## Progress",
        "",
        "- Overall AI_OS progress: $overallAiosProgressPercent%",
        "- Forex bot build progress: $forexBotBuildPercent%",
        "- Night Supervisor health: $nightSupervisorHealthPercent%",
        "- Worker readiness: $workerReadinessPercent%",
        "- Approval clearance: $approvalClearancePercent%",
        "- Validation health: $validationHealthPercent%",
        "- Human interaction required: $humanInteractionRequired",
        "- Current phase: $currentPhase",
        "- Blockers: $blockersCount",
        "- Active approvals: $activeApprovalCount",
        "",
        "## Next Safe Action",
        "",
        $nextSafeAction,
        "",
        "## Display Cards",
        ""
    )

    foreach ($card in $displayCards) {
        $lines += @(
            "### $($card.title)",
            "",
            "- Status: $($card.status)",
            "- Percent: $($card.percent)%",
            "- Summary: $($card.summary)",
            ""
        )
    }

    $lines += @(
        "## Forex Bot Display Rule",
        "",
        "- Show Forex as: REPORT_ONLY_PROFILE / paper simulation planning only.",
        "- Do not imply the bot is live.",
        "- Do not imply broker/OANDA is connected.",
        "- Do not imply real market data is active.",
        "- Do not imply real orders are possible.",
        "",
        "## Source Evidence",
        "",
        "- Morning Brief v2: telemetry/morning_digest/MORNING_BRIEF_V2_LATEST.json",
        "- Approval Intelligence v2: telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.json",
        "- Bridge state: telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json",
        "- Night Supervisor report: $($NightReportRef.repo_relative)",
        "- Forex profile: automation/orchestration/night_supervisor/FOREX_PAPER_LAB_12H_PROFILE.json",
        "",
        "## Validation Notes",
        "",
        "- evidence_only: true",
        "- no approval mutation",
        "- no Pi deployment",
        "- no service or scheduler",
        "- no GPIO or motor controls",
        "- no secrets",
        "- no broker/API",
        "- no live trading",
        "- no real orders or webhooks",
        "- no commit or push"
    )

    return [pscustomobject]@{
        markdown = ($lines -join "`n") + "`n"
        json = $json
    }
}

function New-AiosOpenAiSanitizedSummary {
    param(
        [object]$BridgeState,
        [object]$MorningBriefV2,
        [object]$ApprovalIntelligenceV2,
        [object]$Pi5ProgressReport,
        [object]$NightReportRef
    )

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $nightReport = $NightReportRef.report
    $execution = $nightReport.execution_result
    $briefJson = $MorningBriefV2.json
    $approvalJson = $ApprovalIntelligenceV2.json
    $pi5Json = $Pi5ProgressReport.json

    $approvalCards = @()
    foreach ($card in @($approvalJson.active_approval_cards)) {
        $approvalCards += [pscustomobject]@{
            title = [string]$card.title
            status = [string]$card.status
            classification = [string]$card.current_stale_noise_classification
            requested_action = [string]$card.requested_action
            risk = [string]$card.risk
            recommended_disposition = [string]$card.recommended_disposition
            reason = [string]$card.reason
            safest_next_action = [string]$card.safest_next_action
            recommendation_only = $true
        }
    }

    $currentBlockersCount = @($BridgeState.current_blockers).Count
    $activeApprovalCount = $approvalCards.Count
    $noiseCount = if ($approvalJson.noise_cards_seen -ne $null) {
        [int]$approvalJson.noise_cards_seen
    } elseif ($briefJson.noise_cards) {
        @($briefJson.noise_cards).Count
    } else {
        0
    }
    $staleWarnings = @($briefJson.stale_state_warnings) | Select-Object -First 5

    $nextSafeActionCandidates = @()
    if ($approvalCards.Count -gt 0) {
        foreach ($card in $approvalCards) {
            if (-not [string]::IsNullOrWhiteSpace([string]$card.safest_next_action)) {
                $nextSafeActionCandidates += [string]$card.safest_next_action
            }
        }
    }
    if ($pi5Json.next_safe_action) { $nextSafeActionCandidates += [string]$pi5Json.next_safe_action }
    if ($briefJson.aios_recommendation) { $nextSafeActionCandidates += [string]$briefJson.aios_recommendation }
    $nextSafeActionCandidates = @($nextSafeActionCandidates | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Select-Object -Unique -First 5)

    $json = [pscustomobject]@{
        schema = "AIOS_OPENAI_SANITIZED_SUMMARY.v1"
        mode = "DRY_RUN_SANDBOX_OUTPUT"
        generated_at = $generatedAt
        recommendation_only = $true
        no_approval_authority = $true
        no_execution_authority = $true
        source_contracts_used = @(
            "AIOS_MORNING_BRIEF_V2.v1",
            "AIOS_APPROVAL_INTELLIGENCE_V2.v1",
            "AIOS_PI5_PROGRESS_REPORT.v1",
            "AIOS_AUTONOMY_BRIDGE_STATE.v1",
            "AIOS_NIGHT_SUPERVISOR_REPORT.v1"
        )
        current_status = [string]$briefJson.status
        night_supervisor_status = [string]$nightReport.supervisor_status
        bridge_status = [string]$BridgeState.bridge_status
        validator_status = [string]$execution.validator_status
        qa_status = [string]$execution.qa_status
        current_blockers_count = $currentBlockersCount
        active_approval_count = $activeApprovalCount
        active_approval_decision_cards = $approvalCards
        stale_warnings_summary = [pscustomobject]@{
            count = $staleWarnings.Count
            first_items = $staleWarnings
        }
        noise_summary = [pscustomobject]@{
            noise_count = $noiseCount
            detail = "Noise, examples, completed records, and raw evidence remain excluded from this summary."
        }
        next_safe_action_candidates = $nextSafeActionCandidates
        explicit_forbidden_boundaries = [pscustomobject]@{
            no_raw_file_contents = $true
            no_raw_conversations = $true
            no_credentials = $true
            no_external_calls = $true
            no_approval_mutation = $true
            no_protected_repo_action = $true
            no_runtime_promotion = $true
            no_market_execution = $true
        }
        excluded_content = @(
            "raw file contents",
            "raw conversations",
            "credentials",
            "private telemetry",
            "raw evidence dumps",
            "approval mutation authority",
            "execution authority"
        )
        validation = [pscustomobject]@{
            recommendation_only = $true
            no_approval_authority = $true
            no_execution_authority = $true
            no_external_calls = $true
            no_raw_output = $true
            no_approval_mutation = $true
        }
    }

    $lines = @(
        "# OpenAI Sanitized Summary",
        "",
        "Status: recommendation-only sanitized input package.",
        "",
        "## Current Status",
        "",
        "- Current status: $($json.current_status)",
        "- Night Supervisor status: $($json.night_supervisor_status)",
        "- Bridge status: $($json.bridge_status)",
        "- Validator status: $($json.validator_status)",
        "- QA status: $($json.qa_status)",
        "- Current blockers count: $($json.current_blockers_count)",
        "- Active approval count: $($json.active_approval_count)",
        "",
        "## Active Approval Decision Cards",
        ""
    )

    if ($approvalCards.Count -eq 0) {
        $lines += "- None."
    } else {
        foreach ($card in $approvalCards) {
            $lines += "- $($card.title): $($card.recommended_disposition) - $($card.reason)"
        }
    }

    $lines += @(
        "",
        "## Stale Warnings",
        "",
        "- Count: $($json.stale_warnings_summary.count)"
    )
    foreach ($warning in @($json.stale_warnings_summary.first_items)) {
        $lines += "- $warning"
    }

    $lines += @(
        "",
        "## Noise Summary",
        "",
        "- Noise count: $($json.noise_summary.noise_count)",
        "- Detail: $($json.noise_summary.detail)",
        "",
        "## Next Safe Action Candidates",
        ""
    )
    foreach ($action in @($json.next_safe_action_candidates)) {
        $lines += "- $action"
    }

    $lines += @(
        "",
        "## Boundaries",
        "",
        "- recommendation_only: true",
        "- no_approval_authority: true",
        "- no_execution_authority: true",
        "- no raw file contents",
        "- no raw conversations",
        "- no credentials",
        "- no external calls",
        "- no approval mutation",
        "- no protected repo action",
        "- no runtime promotion",
        "- no market execution"
    )

    return [pscustomobject]@{
        markdown = ($lines -join "`n") + "`n"
        json = $json
    }
}

function New-AiosOpenAiCliInputReadyContract {
    param(
        [object]$OpenAiSanitizedSummary,
        [object]$ProtectedActionReadiness,
        [string]$InputPath,
        [string]$OutputTargetPath
    )

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $inputReady = (
        $OpenAiSanitizedSummary -and
        $OpenAiSanitizedSummary.json -and
        $OpenAiSanitizedSummary.json.recommendation_only -eq $true -and
        $OpenAiSanitizedSummary.json.no_approval_authority -eq $true -and
        $OpenAiSanitizedSummary.json.no_execution_authority -eq $true -and
        $OpenAiSanitizedSummary.json.validation.no_raw_output -eq $true -and
        $OpenAiSanitizedSummary.json.validation.no_external_calls -eq $true
    )

    $json = [pscustomobject]@{
        schema = "AIOS_OPENAI_CLI_INPUT_READY.v1"
        mode = "DRY_RUN_SANDBOX_OUTPUT"
        generated_at = $generatedAt
        input_ready = [bool]$inputReady
        input_path = $InputPath
        output_target_path = $OutputTargetPath
        api_call_permitted = $false
        recommendation_only = $true
        approval_authority = $false
        execution_authority = $false
        blocked_until_explicit_api_approval = $true
        required_approval_fields_before_live_api_call = @(
            "exact input file",
            "exact output file",
            "model or CLI command boundary",
            "cost or usage boundary",
            "credential-exclusion and no-raw-output validation",
            "recommendation-only output contract",
            "stop point",
            "human approval for the API call"
        )
        allowed_input = [pscustomobject]@{
            sanitized_summary_only = $true
            source_path = $InputPath
            raw_repo_dump = $false
            raw_chats = $false
            credential_material = $false
            approval_authority = $false
            execution_authority = $false
        }
        forbidden_input = @(
            "raw repo dumps",
            "raw conversations",
            "credentials",
            "private telemetry",
            "approval mutation state",
            "execution authority",
            "broker/OANDA/live trading data",
            "real orders or webhooks",
            "GPIO or motor control",
            "production state"
        )
        allowed_output = @(
            "recommendation-only reasoning",
            "ranked next safe actions",
            "risk summary",
            "stale/noise notes",
            "approval decision explanation",
            "candidate Codex packet draft for human review"
        )
        forbidden_output = @(
            "approval decisions",
            "execution commands treated as authority",
            "approval mutation",
            "worker launch",
            "scheduler creation",
            "external API calls",
            "protected repo actions",
            "credential handling",
            "market execution",
            "production promotion"
        )
        protected_action_readiness = [pscustomobject]@{
            recommendation_only = [bool]$ProtectedActionReadiness.json.recommendation_only
            approval_authority = [bool]$ProtectedActionReadiness.json.approval_authority
            execution_authority = [bool]$ProtectedActionReadiness.json.execution_authority
        }
    }

    $lines = @(
        "# OpenAI CLI Input Ready Contract",
        "",
        "Generated: $generatedAt",
        "",
        "## Contract",
        "",
        "- input_ready: $($json.input_ready)",
        "- input_path: $InputPath",
        "- output_target_path: $OutputTargetPath",
        "- api_call_permitted: false",
        "- recommendation_only: true",
        "- approval_authority: false",
        "- execution_authority: false",
        "- blocked_until_explicit_api_approval: true",
        "",
        "## Allowed Input",
        "",
        "- OPENAI_SANITIZED_SUMMARY_LATEST.json only.",
        "- No raw repo dump.",
        "- No raw chats.",
        "- No credentials.",
        "- No approval or execution authority.",
        "",
        "## Required Approval Before Live API Call",
        ""
    )

    foreach ($field in @($json.required_approval_fields_before_live_api_call)) {
        $lines += "- $field"
    }

    $lines += @(
        "",
        "## Boundary",
        "",
        "- This output prepares a future CLI/API lane only.",
        "- It does not call OpenAI.",
        "- It does not read credential material.",
        "- It does not approve or execute work."
    )

    return [pscustomobject]@{
        markdown = ($lines -join "`n") + "`n"
        json = $json
    }
}

function New-AiosOpenAiNoCallRecommendation {
    param(
        [object]$OpenAiSanitizedSummary,
        [object]$OpenAiCliInputReady,
        [string]$SourceInputPath
    )

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $inputReady = (
        $OpenAiCliInputReady -and
        $OpenAiCliInputReady.json -and
        $OpenAiCliInputReady.json.input_ready -eq $true -and
        $OpenAiCliInputReady.json.api_call_permitted -eq $false -and
        $OpenAiCliInputReady.json.recommendation_only -eq $true -and
        $OpenAiCliInputReady.json.approval_authority -eq $false -and
        $OpenAiCliInputReady.json.execution_authority -eq $false -and
        $OpenAiCliInputReady.json.blocked_until_explicit_api_approval -eq $true
    )

    $nextSafeActions = @()
    if ($OpenAiSanitizedSummary -and $OpenAiSanitizedSummary.json -and $OpenAiSanitizedSummary.json.next_safe_action_candidates) {
        $nextSafeActions += @($OpenAiSanitizedSummary.json.next_safe_action_candidates)
    }
    $nextSafeActions += "Request explicit API approval if Anthony wants the first live recommendation call."

    $json = [pscustomobject]@{
        schema = "AIOS_OPENAI_RECOMMENDATION.v1"
        generated_at = $generatedAt
        source_input_path = $SourceInputPath
        adapter_mode = "NO_CALL_FIXTURE"
        input_contract_valid = [bool]$inputReady
        recommendation_only = $true
        approval_authority = $false
        execution_authority = $false
        api_call_made = $false
        human_review_required = $true
        summary = "No-call fixture recommendation generated from sanitized AI_OS evidence. OpenAI API call is still blocked until explicit approval."
        recommended_next_actions = @($nextSafeActions)
        risks = @(
            "Treating recommendation text as authority would violate AI_OS protected-action rules.",
            "A live API call still needs exact approval, model or CLI boundary, cost boundary, and output validation.",
            "Broad APPLY approval remains deferred until exact scope and validator evidence exist."
        )
        missing_evidence = @(
            "Explicit API approval packet.",
            "Approved model or CLI command boundary.",
            "Approved cost or usage boundary.",
            "Post-call output schema validator."
        )
        approval_decision_explanation = "Current active approval evidence recommends deferring APPLY because the old approval record is broad and missing exact file list, mutation details, validator evidence, and stop point."
        protected_action_notes = "OpenAI output is recommendation evidence only. It cannot approve, execute, stage, commit, push, merge, mutate approvals, launch workers, create schedulers, call external services, or touch production."
        do_not_execute = @(
            "Do not call OpenAI from this adapter mode.",
            "Do not treat this output as approval.",
            "Do not execute commands from this output.",
            "Do not mutate approvals.",
            "Do not stage, commit, push, merge, or launch workers.",
            "Do not use broker, OANDA, live trading, real order, webhook, GPIO, motor, or production paths."
        )
        safe_next_packet_candidate = [pscustomobject]@{
            mode = "DRY_RUN"
            lane = "OPENAI_CLI_API_APPROVAL_REVIEW"
            mission = "Review whether Anthony wants to approve the first live OpenAI recommendation call."
            allowed_input = $SourceInputPath
            output_target = "telemetry/morning_digest/OPENAI_RECOMMENDATION_LATEST.json"
            stop_point = "approval decision only; no API call unless explicitly approved"
        }
        validation = [pscustomobject]@{
            input_ready = [bool]$OpenAiCliInputReady.json.input_ready
            api_call_permitted_is_false = ($OpenAiCliInputReady.json.api_call_permitted -eq $false)
            recommendation_only = $true
            approval_authority = $false
            execution_authority = $false
            no_api_call = $true
            no_approval_mutation = $true
        }
    }

    $lines = @(
        "# OpenAI Recommendation Fixture",
        "",
        "Generated: $generatedAt",
        "",
        "## Adapter",
        "",
        "- schema: AIOS_OPENAI_RECOMMENDATION.v1",
        "- adapter_mode: NO_CALL_FIXTURE",
        "- source_input_path: $SourceInputPath",
        "- api_call_made: false",
        "- recommendation_only: true",
        "- approval_authority: false",
        "- execution_authority: false",
        "- human_review_required: true",
        "",
        "## Summary",
        "",
        $json.summary,
        "",
        "## Recommended Next Actions",
        ""
    )

    foreach ($action in @($json.recommended_next_actions)) {
        $lines += "- $action"
    }

    $lines += @(
        "",
        "## Do Not Execute",
        ""
    )

    foreach ($item in @($json.do_not_execute)) {
        $lines += "- $item"
    }

    $lines += @(
        "",
        "## Boundary",
        "",
        "- No command from this output is authority.",
        "- A live API call remains blocked until exact human approval exists."
    )

    return [pscustomobject]@{
        markdown = ($lines -join "`n") + "`n"
        json = $json
    }
}

function New-AiosOpenAiApiApprovalBoundary {
    param(
        [object]$OpenAiCliInputReady,
        [object]$OpenAiSanitizedSummary,
        [object]$OpenAiRecommendation,
        [object]$ProtectedActionReadiness
    )

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $inputPath = "telemetry/morning_digest/OPENAI_SANITIZED_SUMMARY_LATEST.json"
    if ($OpenAiCliInputReady -and $OpenAiCliInputReady.json -and $OpenAiCliInputReady.json.input_path) {
        $inputPath = [string]$OpenAiCliInputReady.json.input_path
    }

    $outputPath = "telemetry/morning_digest/OPENAI_RECOMMENDATION_LATEST.json"
    if ($OpenAiCliInputReady -and $OpenAiCliInputReady.json -and $OpenAiCliInputReady.json.output_target_path) {
        $outputPath = [string]$OpenAiCliInputReady.json.output_target_path
    }

    $json = [pscustomobject]@{
        schema = "AIOS_OPENAI_API_APPROVAL_BOUNDARY.v1"
        generated_at = $generatedAt
        api_call_permitted = $false
        blocked_until_explicit_api_approval = $true
        recommendation_only = $true
        approval_authority = $false
        execution_authority = $false
        exact_input_file = $inputPath
        exact_output_file = $outputPath
        approved_model = "[REQUIRES_EXPLICIT_HUMAN_APPROVAL]"
        approved_command_or_adapter_path = "[REQUIRES_EXPLICIT_HUMAN_APPROVAL]"
        maximum_input_size = "[REQUIRES_EXPLICIT_HUMAN_APPROVAL]"
        maximum_output_size = "[REQUIRES_EXPLICIT_HUMAN_APPROVAL]"
        maximum_cost_per_run = "[REQUIRES_EXPLICIT_HUMAN_APPROVAL]"
        maximum_runs_per_cycle = 1
        duplicate_run_suppression_rule = "Hash exact input file plus approved adapter version; skip a live call when the same hash already produced a valid recommendation in the same cycle."
        pre_call_credential_raw_exclusion_scan = [pscustomobject]@{
            required = $true
            target = $inputPath
            scan_scope = "credential markers and raw conversation identifiers"
            must_return_no_matches = $true
        }
        post_call_schema_raw_exclusion_scan = [pscustomobject]@{
            required = $true
            target = $outputPath
            required_schema = "AIOS_OPENAI_RECOMMENDATION.v1"
            scan_scope = "credential markers and raw conversation identifiers"
            must_return_no_matches = $true
        }
        stop_point = "Write recommendation-only output, validate schema and scans, then stop before any protected action."
        explicit_human_approval_statement = "[REQUIRED] Anthony explicitly approves exactly one OpenAI recommendation-only API call with the input, output, model, command, cost, run limit, validators, and stop point named in this boundary."
        required_approval_fields = @(
            "exact input file",
            "exact output file",
            "approved model",
            "approved command/adapter path",
            "maximum input size",
            "maximum output size",
            "maximum cost per run",
            "maximum runs per cycle",
            "duplicate-run suppression rule",
            "pre-call credential/raw exclusion scan",
            "post-call schema/raw exclusion scan",
            "stop point",
            "explicit human approval statement"
        )
        integration_boundary = [pscustomobject]@{
            may_feed_morning_brief = "recommendation evidence only"
            may_feed_pi5 = "display-only recommendation status"
            may_feed_approval_intelligence = "supporting evidence only"
            never_authority = $true
        }
        current_contract_state = [pscustomobject]@{
            input_ready = [bool]$OpenAiCliInputReady.json.input_ready
            cli_api_call_permitted = [bool]$OpenAiCliInputReady.json.api_call_permitted
            sanitized_summary_schema = [string]$OpenAiSanitizedSummary.json.schema
            no_call_recommendation_schema = [string]$OpenAiRecommendation.json.schema
            no_call_adapter_mode = [string]$OpenAiRecommendation.json.adapter_mode
            protected_action_recommendation_only = [bool]$ProtectedActionReadiness.json.recommendation_only
            protected_action_approval_authority = [bool]$ProtectedActionReadiness.json.approval_authority
            protected_action_execution_authority = [bool]$ProtectedActionReadiness.json.execution_authority
        }
        validation = [pscustomobject]@{
            no_api_call = $true
            no_external_call = $true
            no_approval_mutation = $true
            api_call_remains_blocked = $true
            recommendation_only = $true
            approval_authority = $false
            execution_authority = $false
        }
    }

    $lines = @(
        "# OpenAI API Approval Boundary",
        "",
        "Generated: $generatedAt",
        "",
        "## Boundary Flags",
        "",
        "- schema: AIOS_OPENAI_API_APPROVAL_BOUNDARY.v1",
        "- api_call_permitted: false",
        "- blocked_until_explicit_api_approval: true",
        "- recommendation_only: true",
        "- approval_authority: false",
        "- execution_authority: false",
        "",
        "## Required Approval Fields",
        ""
    )

    foreach ($field in @($json.required_approval_fields)) {
        $lines += "- $field"
    }

    $lines += @(
        "",
        "## Exact Paths",
        "",
        "- exact_input_file: $inputPath",
        "- exact_output_file: $outputPath",
        "",
        "## Limits",
        "",
        "- approved_model: [REQUIRES_EXPLICIT_HUMAN_APPROVAL]",
        "- approved_command_or_adapter_path: [REQUIRES_EXPLICIT_HUMAN_APPROVAL]",
        "- maximum_input_size: [REQUIRES_EXPLICIT_HUMAN_APPROVAL]",
        "- maximum_output_size: [REQUIRES_EXPLICIT_HUMAN_APPROVAL]",
        "- maximum_cost_per_run: [REQUIRES_EXPLICIT_HUMAN_APPROVAL]",
        "- maximum_runs_per_cycle: 1",
        "",
        "## Duplicate Run Suppression",
        "",
        $json.duplicate_run_suppression_rule,
        "",
        "## Integration Boundary",
        "",
        "- Morning Brief: recommendation evidence only.",
        "- Pi5: display-only recommendation status.",
        "- Approval Intelligence: supporting evidence only.",
        "- Never approval or execution authority.",
        "",
        "## Explicit Human Approval Statement",
        "",
        $json.explicit_human_approval_statement
    )

    return [pscustomobject]@{
        markdown = ($lines -join "`n") + "`n"
        json = $json
    }
}

function New-AiosProtectedActionReadiness {
    param(
        [object]$BridgeState,
        [object]$MorningBriefV2,
        [object]$ApprovalIntelligenceV2,
        [object]$Pi5ProgressReport,
        [object]$OpenAiSanitizedSummary,
        [object]$NightReportRef
    )

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

    $samples = @(
        [pscustomobject]@{
            action = "read latest Night Supervisor report"
            action_type = "read"
            classification = "ALLOWED_READ_ONLY"
            status = "PASS"
            reason = "Reads existing report evidence only."
            safest_next_action = "Read and summarize the latest report without writing files."
            required_human_approval = $false
            allowed_path_check = "PASS"
            forbidden_path_check = "PASS"
            confidence = "HIGH"
            audit_log_hint = "Record report path and generated_at if surfaced in a brief."
        },
        [pscustomobject]@{
            action = "generate sanitized summary"
            action_type = "prepare"
            classification = "PREPARE_ONLY"
            status = "PASS"
            reason = "Creates recommendation-only sandbox evidence for later reasoning."
            safest_next_action = "Generate sanitized output only; do not call external services."
            required_human_approval = $false
            allowed_path_check = "PASS"
            forbidden_path_check = "PASS"
            confidence = "HIGH"
            audit_log_hint = "Record source contracts and excluded-content boundary."
        },
        [pscustomobject]@{
            action = "draft Codex packet"
            action_type = "prepare"
            classification = "PREPARE_ONLY"
            status = "PASS"
            reason = "Drafting a packet is preparation, not execution."
            safest_next_action = "Draft complete packet fields and wait for Anthony before execution."
            required_human_approval = $false
            allowed_path_check = "PASS"
            forbidden_path_check = "PASS"
            confidence = "HIGH"
            audit_log_hint = "Record packet ID, lane, allowed paths, forbidden paths, and stop point."
        },
        [pscustomobject]@{
            action = "stage files"
            action_type = "stage"
            classification = "NEEDS_EXPLICIT_APPROVAL"
            status = "REVIEW_REQUIRED"
            reason = "Staging is a protected repo action and requires exact-file approval."
            safest_next_action = "Request exact current approval with named files and cached-diff review."
            required_human_approval = $true
            allowed_path_check = "UNKNOWN"
            forbidden_path_check = "UNKNOWN"
            confidence = "HIGH"
            audit_log_hint = "Use the Protected Action Gate and Commit/Push Gate before staging."
        },
        [pscustomobject]@{
            action = "commit changes"
            action_type = "commit"
            classification = "NEEDS_EXPLICIT_APPROVAL"
            status = "REVIEW_REQUIRED"
            reason = "Commit requires explicit approval, reviewed diff, exact files, and message."
            safest_next_action = "Run cached diff review and request explicit commit approval."
            required_human_approval = $true
            allowed_path_check = "UNKNOWN"
            forbidden_path_check = "UNKNOWN"
            confidence = "HIGH"
            audit_log_hint = "Record exact files, validation, cached diff, and commit message."
        },
        [pscustomobject]@{
            action = "push branch"
            action_type = "push"
            classification = "NEEDS_EXPLICIT_APPROVAL"
            status = "REVIEW_REQUIRED"
            reason = "Push is a protected repo action and must name branch and remote target."
            safest_next_action = "Request explicit push approval for one branch and one remote target."
            required_human_approval = $true
            allowed_path_check = "PASS"
            forbidden_path_check = "UNKNOWN"
            confidence = "HIGH"
            audit_log_hint = "Record branch, remote, commits intended for push, and ruleset warnings."
        },
        [pscustomobject]@{
            action = "merge PR"
            action_type = "merge"
            classification = "NEEDS_EXPLICIT_APPROVAL"
            status = "REVIEW_REQUIRED"
            reason = "Merge requires separate explicit approval after checks and mergeability are known."
            safest_next_action = "Prepare merge readiness evidence and wait for explicit merge approval."
            required_human_approval = $true
            allowed_path_check = "UNKNOWN"
            forbidden_path_check = "UNKNOWN"
            confidence = "HIGH"
            audit_log_hint = "Record PR number, checks, mergeability, and review state."
        },
        [pscustomobject]@{
            action = "mutate approval inbox"
            action_type = "approval_state_change"
            classification = "NEEDS_EXPLICIT_APPROVAL"
            status = "REVIEW_REQUIRED"
            reason = "Approval state changes are protected and Anthony-owned."
            safest_next_action = "Produce a recommendation card; do not change approval state."
            required_human_approval = $true
            allowed_path_check = "UNKNOWN"
            forbidden_path_check = "UNKNOWN"
            confidence = "HIGH"
            audit_log_hint = "Record target approval record and requested state transition."
        },
        [pscustomobject]@{
            action = "create scheduler"
            action_type = "scheduler"
            classification = "NEEDS_EXPLICIT_APPROVAL"
            status = "REVIEW_REQUIRED"
            reason = "Scheduler creation starts background behavior and requires explicit approval."
            safest_next_action = "Prepare a schedule design and stop before registration."
            required_human_approval = $true
            allowed_path_check = "UNKNOWN"
            forbidden_path_check = "UNKNOWN"
            confidence = "HIGH"
            audit_log_hint = "Record schedule name, trigger, stop control, and rollback plan."
        },
        [pscustomobject]@{
            action = "launch worker"
            action_type = "worker_launch"
            classification = "NEEDS_EXPLICIT_APPROVAL"
            status = "REVIEW_REQUIRED"
            reason = "Worker launch changes runtime behavior and requires explicit approval."
            safest_next_action = "Prepare worker packet and readiness evidence; do not launch."
            required_human_approval = $true
            allowed_path_check = "UNKNOWN"
            forbidden_path_check = "UNKNOWN"
            confidence = "HIGH"
            audit_log_hint = "Record worker identity, lane, worktree, and stop point."
        },
        [pscustomobject]@{
            action = "call OpenAI API"
            action_type = "api_call"
            classification = "NEEDS_EXPLICIT_APPROVAL"
            status = "REVIEW_REQUIRED"
            reason = "External AI calls require explicit approval and credential boundary review."
            safest_next_action = "Use sanitized summary output only until an API lane is approved."
            required_human_approval = $true
            allowed_path_check = "UNKNOWN"
            forbidden_path_check = "UNKNOWN"
            confidence = "HIGH"
            audit_log_hint = "Record model intent, input contract, cost boundary, and no-credential-output check."
        },
        [pscustomobject]@{
            action = "access .env / credential material"
            action_type = "credential_access"
            classification = "BLOCKED_FOR_SAFETY"
            status = "BLOCKED"
            reason = "Credential material is outside evidence-only readiness scope."
            safest_next_action = "Stop and request a separate credential-boundary review if ever needed."
            required_human_approval = $true
            allowed_path_check = "FAIL"
            forbidden_path_check = "FAIL"
            confidence = "HIGH"
            audit_log_hint = "Do not print, copy, store, or summarize credential values."
        },
        [pscustomobject]@{
            action = "market-provider / O-connector / live-trading boundary"
            action_type = "market_execution"
            classification = "BLOCKED_FOR_SAFETY"
            status = "BLOCKED"
            reason = "Market execution paths remain blocked outside a separately approved safety lane."
            safest_next_action = "Keep Forex work report-only and paper-simulation planning only."
            required_human_approval = $true
            allowed_path_check = "FAIL"
            forbidden_path_check = "FAIL"
            confidence = "HIGH"
            audit_log_hint = "Record that no market provider, live execution, or order routing was used."
        },
        [pscustomobject]@{
            action = "GPIO / motor control"
            action_type = "hardware_control"
            classification = "BLOCKED_FOR_SAFETY"
            status = "BLOCKED"
            reason = "Physical control is outside this repo-readiness lane."
            safest_next_action = "Stop until a future isolated hardware lane defines safety controls."
            required_human_approval = $true
            allowed_path_check = "FAIL"
            forbidden_path_check = "FAIL"
            confidence = "HIGH"
            audit_log_hint = "Record that no hardware control path was touched."
        }
    )

    $counts = [ordered]@{}
    foreach ($sample in $samples) {
        $classification = [string]$sample.classification
        if (-not $counts.Contains($classification)) {
            $counts[$classification] = 0
        }
        $counts[$classification] = [int]$counts[$classification] + 1
    }

    $json = [pscustomobject]@{
        schema = "AIOS_PROTECTED_ACTION_READINESS_OUTPUT.v1"
        mode = "DRY_RUN_SANDBOX_OUTPUT"
        generated_at = $generatedAt
        recommendation_only = $true
        approval_authority = $false
        execution_authority = $false
        source_contracts_used = @(
            "AIOS_MORNING_BRIEF_V2.v1",
            "AIOS_APPROVAL_INTELLIGENCE_V2.v1",
            "AIOS_PI5_PROGRESS_REPORT.v1",
            "AIOS_OPENAI_SANITIZED_SUMMARY.v1",
            "AIOS_AUTONOMY_BRIDGE_STATE.v1"
        )
        current_bridge_status = [string]$BridgeState.bridge_status
        current_blockers_count = @($BridgeState.current_blockers).Count
        active_approval_count = @($BridgeState.active_decision_cards).Count
        classification_counts = [pscustomobject]$counts
        sample_classifications = $samples
        integration = [pscustomobject]@{
            morning_brief = "Show aggregate readiness counts and human-needed items only."
            approval_intelligence = "Attach readiness class to approval cards without changing approval state."
            pi5_progress = "Display blocked/readiness counts without action controls."
            openai_sanitized_summary = "Provide sanitized aggregate context only."
        }
        boundary = [pscustomobject]@{
            recommendation_only = $true
            approval_authority = $false
            execution_authority = $false
            no_approval_mutation = $true
            no_worker_launch = $true
            no_scheduler = $true
            no_external_calls = $true
            no_protected_action_execution = $true
        }
    }

    $lines = @(
        "# Protected Action Readiness Gate v1",
        "",
        "Status: recommendation-only sandbox evidence.",
        "",
        "## Authority Boundary",
        "",
        "- recommendation_only: true",
        "- approval_authority: false",
        "- execution_authority: false",
        "- no approval mutation",
        "- no worker launch",
        "- no scheduler",
        "- no external calls",
        "- no protected action execution",
        "",
        "## Current Evidence",
        "",
        "- Bridge status: $($json.current_bridge_status)",
        "- Current blockers count: $($json.current_blockers_count)",
        "- Active approval count: $($json.active_approval_count)",
        "",
        "## Classification Counts",
        ""
    )

    foreach ($key in $counts.Keys) {
        $lines += "- ${key}: $($counts[$key])"
    }

    $lines += @(
        "",
        "## Sample Classifications",
        ""
    )

    foreach ($sample in $samples) {
        $lines += "- $($sample.action): $($sample.classification) / $($sample.status) - $($sample.reason) Next: $($sample.safest_next_action)"
    }

    $lines += @(
        "",
        "## Integration",
        "",
        "- Morning Brief: aggregate counts and human-needed items only.",
        "- Approval Intelligence: readiness class on cards, no approval mutation.",
        "- Pi5 Progress: display-only readiness counts, no action controls.",
        "- OpenAI sanitized summary: sanitized aggregate context only."
    )

    return [pscustomobject]@{
        markdown = ($lines -join "`n") + "`n"
        json = $json
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
    "telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.md",
    "telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.json",
    "telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.md",
    "telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.json",
    "telemetry/morning_digest/OPENAI_SANITIZED_SUMMARY_LATEST.md",
    "telemetry/morning_digest/OPENAI_SANITIZED_SUMMARY_LATEST.json",
    "telemetry/morning_digest/OPENAI_CLI_INPUT_READY_LATEST.md",
    "telemetry/morning_digest/OPENAI_CLI_INPUT_READY_LATEST.json",
    "telemetry/morning_digest/OPENAI_RECOMMENDATION_LATEST.md",
    "telemetry/morning_digest/OPENAI_RECOMMENDATION_LATEST.json",
    "telemetry/morning_digest/OPENAI_API_APPROVAL_BOUNDARY_LATEST.md",
    "telemetry/morning_digest/OPENAI_API_APPROVAL_BOUNDARY_LATEST.json",
    "telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.md",
    "telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.json",
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
$approvalIntelligenceV2MarkdownOutput = "telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.md"
$approvalIntelligenceV2JsonOutput = "telemetry/morning_digest/APPROVAL_INTELLIGENCE_V2_LATEST.json"
$approvalIntelligenceV2MarkdownPath = Join-Path $repoRoot $approvalIntelligenceV2MarkdownOutput
$approvalIntelligenceV2JsonPath = Join-Path $repoRoot $approvalIntelligenceV2JsonOutput
$pi5ProgressMarkdownOutput = "telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.md"
$pi5ProgressJsonOutput = "telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.json"
$pi5ProgressMarkdownPath = Join-Path $repoRoot $pi5ProgressMarkdownOutput
$pi5ProgressJsonPath = Join-Path $repoRoot $pi5ProgressJsonOutput
$openAiSanitizedSummaryMarkdownOutput = "telemetry/morning_digest/OPENAI_SANITIZED_SUMMARY_LATEST.md"
$openAiSanitizedSummaryJsonOutput = "telemetry/morning_digest/OPENAI_SANITIZED_SUMMARY_LATEST.json"
$openAiSanitizedSummaryMarkdownPath = Join-Path $repoRoot $openAiSanitizedSummaryMarkdownOutput
$openAiSanitizedSummaryJsonPath = Join-Path $repoRoot $openAiSanitizedSummaryJsonOutput
$openAiCliInputReadyMarkdownOutput = "telemetry/morning_digest/OPENAI_CLI_INPUT_READY_LATEST.md"
$openAiCliInputReadyJsonOutput = "telemetry/morning_digest/OPENAI_CLI_INPUT_READY_LATEST.json"
$openAiCliInputReadyMarkdownPath = Join-Path $repoRoot $openAiCliInputReadyMarkdownOutput
$openAiCliInputReadyJsonPath = Join-Path $repoRoot $openAiCliInputReadyJsonOutput
$openAiRecommendationMarkdownOutput = "telemetry/morning_digest/OPENAI_RECOMMENDATION_LATEST.md"
$openAiRecommendationJsonOutput = "telemetry/morning_digest/OPENAI_RECOMMENDATION_LATEST.json"
$openAiRecommendationMarkdownPath = Join-Path $repoRoot $openAiRecommendationMarkdownOutput
$openAiRecommendationJsonPath = Join-Path $repoRoot $openAiRecommendationJsonOutput
$openAiApiApprovalBoundaryMarkdownOutput = "telemetry/morning_digest/OPENAI_API_APPROVAL_BOUNDARY_LATEST.md"
$openAiApiApprovalBoundaryJsonOutput = "telemetry/morning_digest/OPENAI_API_APPROVAL_BOUNDARY_LATEST.json"
$openAiApiApprovalBoundaryMarkdownPath = Join-Path $repoRoot $openAiApiApprovalBoundaryMarkdownOutput
$openAiApiApprovalBoundaryJsonPath = Join-Path $repoRoot $openAiApiApprovalBoundaryJsonOutput
$protectedActionReadinessMarkdownOutput = "telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.md"
$protectedActionReadinessJsonOutput = "telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.json"
$protectedActionReadinessMarkdownPath = Join-Path $repoRoot $protectedActionReadinessMarkdownOutput
$protectedActionReadinessJsonPath = Join-Path $repoRoot $protectedActionReadinessJsonOutput

if (($StateApply -or $MorningBriefV2Apply) -and -not $Apply) {
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

    $approvalIntelligenceV2 = New-AiosApprovalIntelligenceV2 `
        -BridgeState $receipt.bridge_state `
        -MorningBriefV2 $briefV2

    Set-Content -LiteralPath $approvalIntelligenceV2MarkdownPath -Value $approvalIntelligenceV2.markdown -Encoding UTF8
    $approvalIntelligenceV2.json | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $approvalIntelligenceV2JsonPath -Encoding UTF8
    Write-AiosLine "PASS" "approval_intelligence_v2_written=$approvalIntelligenceV2MarkdownOutput,$approvalIntelligenceV2JsonOutput"

    $forexProfilePath = Join-Path $repoRoot "automation\orchestration\night_supervisor\FOREX_PAPER_LAB_12H_PROFILE.json"
    $forexReadmePath = Join-Path $repoRoot "automation\orchestration\night_supervisor\FOREX_PAPER_LAB_12H_PROFILE_README.md"
    $forexProfile = Read-AiosJsonObject -Path $forexProfilePath
    $forexReadme = if (Test-Path -LiteralPath $forexReadmePath -PathType Leaf) {
        Get-Content -LiteralPath $forexReadmePath -Raw
    } else {
        ""
    }

    $pi5ProgressReport = New-AiosPi5ProgressReport `
        -BridgeState $receipt.bridge_state `
        -MorningBriefV2 $briefV2 `
        -ApprovalIntelligenceV2 $approvalIntelligenceV2 `
        -NightReportRef $latestReport `
        -ForexProfile $forexProfile `
        -ForexReadme $forexReadme `
        -Branch $branch `
        -GitStatus $gitStatus

    Set-Content -LiteralPath $pi5ProgressMarkdownPath -Value $pi5ProgressReport.markdown -Encoding UTF8
    $pi5ProgressReport.json | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $pi5ProgressJsonPath -Encoding UTF8
    Write-AiosLine "PASS" "pi5_progress_report_written=$pi5ProgressMarkdownOutput,$pi5ProgressJsonOutput"

    $openAiSanitizedSummary = New-AiosOpenAiSanitizedSummary `
        -BridgeState $receipt.bridge_state `
        -MorningBriefV2 $briefV2 `
        -ApprovalIntelligenceV2 $approvalIntelligenceV2 `
        -Pi5ProgressReport $pi5ProgressReport `
        -NightReportRef $latestReport

    Set-Content -LiteralPath $openAiSanitizedSummaryMarkdownPath -Value $openAiSanitizedSummary.markdown -Encoding UTF8
    $openAiSanitizedSummary.json | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $openAiSanitizedSummaryJsonPath -Encoding UTF8
    Write-AiosLine "PASS" "openai_sanitized_summary_written=$openAiSanitizedSummaryMarkdownOutput,$openAiSanitizedSummaryJsonOutput"

    $protectedActionReadiness = New-AiosProtectedActionReadiness `
        -BridgeState $receipt.bridge_state `
        -MorningBriefV2 $briefV2 `
        -ApprovalIntelligenceV2 $approvalIntelligenceV2 `
        -Pi5ProgressReport $pi5ProgressReport `
        -OpenAiSanitizedSummary $openAiSanitizedSummary `
        -NightReportRef $latestReport

    Set-Content -LiteralPath $protectedActionReadinessMarkdownPath -Value $protectedActionReadiness.markdown -Encoding UTF8
    $protectedActionReadiness.json | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $protectedActionReadinessJsonPath -Encoding UTF8
    Write-AiosLine "PASS" "protected_action_readiness_written=$protectedActionReadinessMarkdownOutput,$protectedActionReadinessJsonOutput"

    $openAiCliInputReady = New-AiosOpenAiCliInputReadyContract `
        -OpenAiSanitizedSummary $openAiSanitizedSummary `
        -ProtectedActionReadiness $protectedActionReadiness `
        -InputPath $openAiSanitizedSummaryJsonOutput `
        -OutputTargetPath "telemetry/morning_digest/OPENAI_RECOMMENDATION_LATEST.json"

    Set-Content -LiteralPath $openAiCliInputReadyMarkdownPath -Value $openAiCliInputReady.markdown -Encoding UTF8
    $openAiCliInputReady.json | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $openAiCliInputReadyJsonPath -Encoding UTF8
    Write-AiosLine "PASS" "openai_cli_input_ready_written=$openAiCliInputReadyMarkdownOutput,$openAiCliInputReadyJsonOutput"

    $openAiRecommendation = New-AiosOpenAiNoCallRecommendation `
        -OpenAiSanitizedSummary $openAiSanitizedSummary `
        -OpenAiCliInputReady $openAiCliInputReady `
        -SourceInputPath $openAiSanitizedSummaryJsonOutput

    Set-Content -LiteralPath $openAiRecommendationMarkdownPath -Value $openAiRecommendation.markdown -Encoding UTF8
    $openAiRecommendation.json | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $openAiRecommendationJsonPath -Encoding UTF8
    Write-AiosLine "PASS" "openai_recommendation_fixture_written=$openAiRecommendationMarkdownOutput,$openAiRecommendationJsonOutput"

    $openAiApiApprovalBoundary = New-AiosOpenAiApiApprovalBoundary `
        -OpenAiCliInputReady $openAiCliInputReady `
        -OpenAiSanitizedSummary $openAiSanitizedSummary `
        -OpenAiRecommendation $openAiRecommendation `
        -ProtectedActionReadiness $protectedActionReadiness

    Set-Content -LiteralPath $openAiApiApprovalBoundaryMarkdownPath -Value $openAiApiApprovalBoundary.markdown -Encoding UTF8
    $openAiApiApprovalBoundary.json | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $openAiApiApprovalBoundaryJsonPath -Encoding UTF8
    Write-AiosLine "PASS" "openai_api_approval_boundary_written=$openAiApiApprovalBoundaryMarkdownOutput,$openAiApiApprovalBoundaryJsonOutput"
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
