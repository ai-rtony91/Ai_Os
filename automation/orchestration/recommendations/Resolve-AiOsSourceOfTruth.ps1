param(
    [Parameter(Mandatory = $true)][string]$Topic,
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$scriptName = Split-Path -Leaf $PSCommandPath

# Routing data derived from docs/governance/source-of-truth-map.md and docs/audits/active-system-map.md.
# Update this table by reading those canonical authority files first.

$highRiskKeywords = @(
    "trading", "broker", "credentials", "secrets", "runtime",
    "telemetry", "dashboard", "worker registry", "approval gate",
    "protected root", "merge", "push", "oanda", "api key",
    "live order", "webhook execution", "broker execution"
)

$routes = @(
    [ordered]@{
        keywords              = @("work packet", "packet builder", "packet validator", "packet template", "orchestration packet")
        authority_owner       = "automation/orchestration/work_packets/"
        supporting_sources    = @("AGENTS.md", "docs/governance/source-of-truth-map.md", "automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json", "schemas/aios/orchestration/packet.schema.json")
        archive_avoid         = @("archive/", "docs/AI_OS/", "internal/source-artifacts/")
        risk_class            = "medium"
        suggested_lane        = "orchestration_codex"
        blocked_paths         = @("services/runtime/", "apps/trading_lab/trading_lab/execution/", "telemetry/")
        human_approval        = $false
        recommended_next      = "Read automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json and schemas/aios/orchestration/packet.schema.json before editing."
        confidence            = "high"
        reason                = "Canonical packet home confirmed by active-system-map.md and source-of-truth-map.md."
    },
    [ordered]@{
        keywords              = @("dashboard", "runtime visibility", "dashboard visibility", "dashboard bridge", "ui visibility")
        authority_owner       = "apps/dashboard/src/"
        supporting_sources    = @("docs/audits/active-system-map.md", "apps/dashboard/src/runtimeVisibilityClient.js", "apps/dashboard/src/runtimeVisibilityAdapter.js", "services/orchestrator/index.js")
        archive_avoid         = @("archive/", "docs/AI_OS/", "apps/dashboard/mock-data/ (historical fixtures)")
        risk_class            = "medium"
        suggested_lane        = "dashboard_codex"
        blocked_paths         = @("apps/dashboard/assets/", "telemetry/", "services/runtime/")
        human_approval        = $false
        recommended_next      = "Read apps/dashboard/src/App.jsx and runtimeVisibilityClient.js. Do not remove mock fixtures."
        confidence            = "high"
        reason                = "Dashboard chain confirmed by active-system-map.md. Mock fixtures must be preserved as fallback."
    },
    [ordered]@{
        keywords              = @("trading lab", "paper execution", "paper trading", "paper only", "paper route", "paper simulation", "backtest", "trading safety")
        authority_owner       = "apps/trading_lab/ + automation/trading_lab/ + tests/trader/"
        supporting_sources    = @("apps/trading_lab/README.md", "WHITEPAPER.md", "docs/audits/active-system-map.md", "docs/governance/source-of-truth-map.md")
        archive_avoid         = @("docs/AI_OS/brokers/", "docs/AI_OS/execution/", "docs/AI_OS/trading/", "archive/")
        risk_class            = "high"
        suggested_lane        = "trading_lab_codex"
        blocked_paths         = @("apps/trading_lab/trading_lab/execution/ (paper-only boundary)", "aios/modules/trader/ (active dependency until canonical decision)")
        human_approval        = $true
        recommended_next      = "Read apps/trading_lab/README.md and WHITEPAPER.md. Preserve LIVE_BROKER_DISABLED check. All changes require DRY_RUN review."
        confidence            = "high"
        reason                = "Trading Lab is paper-only vertical. Live broker execution is blocked per AGENTS.md and WHITEPAPER.md."
    },
    [ordered]@{
        keywords              = @("broker", "credentials", "api key", "oanda", "live broker", "real order", "live order", "bearer token", "secret", "account id")
        authority_owner       = "BLOCKED"
        supporting_sources    = @("AGENTS.md Trading Safety Rules", "WHITEPAPER.md Trading Safety Boundary", "docs/security/secret-prevention.md")
        archive_avoid         = @("ALL paths")
        risk_class            = "CRITICAL"
        suggested_lane        = "BLOCKED"
        blocked_paths         = @("ENTIRE REPO")
        human_approval        = $true
        recommended_next      = "STOP. Broker credentials, API keys, live orders, and real broker access are blocked in AI_OS. See AGENTS.md Section 5 and docs/security/secret-prevention.md."
        confidence            = "high"
        reason                = "Hard safety rule in AGENTS.md. No live trading. No broker connection. No OANDA integration. No API keys."
    },
    [ordered]@{
        keywords              = @("readme", "readme update", "front door", "project description")
        authority_owner       = "README.md"
        supporting_sources    = @("AGENTS.md Protected Files", "docs/governance/source-of-truth-map.md")
        archive_avoid         = @("archive/", "docs/AI_OS/")
        risk_class            = "high"
        suggested_lane        = "root_doc_codex"
        blocked_paths         = @("README.md edits require explicit operator scope - protected root file")
        human_approval        = $true
        recommended_next      = "README.md is a protected root file. Define exact edit scope before requesting a worker mutation. Read current file first."
        confidence            = "high"
        reason                = "README.md is listed in AGENTS.md Protected Root Files. Edit only when explicitly scoped."
    },
    [ordered]@{
        keywords              = @("worker registry", "worker address book", "worker profile", "worker inbox", "worker assignment")
        authority_owner       = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
        supporting_sources    = @("automation/orchestration/workers/AIOS_WORKER_PROFILES.json", "automation/orchestration/README.md", "docs/audits/active-system-map.md")
        archive_avoid         = @("automation/window_identity/AIOS_WORKER_REGISTRY.json (window presentation only)", "archive/")
        risk_class            = "high"
        suggested_lane        = "orchestration_codex"
        blocked_paths         = @("automation/orchestration/workers/inbox/ (active runtime state)", "automation/orchestration/approval_inbox/")
        human_approval        = $true
        recommended_next      = "Read automation/orchestration/workers/AIOS_WORKER_REGISTRY.json. Confirm with docs/audits/active-system-map.md before any registry edit."
        confidence            = "high"
        reason                = "Orchestration registry is the canonical worker identity per active-system-map.md. Window identity registry is terminal presentation only."
    },
    [ordered]@{
        keywords              = @("source of truth", "source-of-truth", "authority map", "ownership", "canonical", "governance map", "truth cleanup")
        authority_owner       = "docs/governance/source-of-truth-map.md"
        supporting_sources    = @("docs/audits/active-system-map.md", "README.md", "AGENTS.md")
        archive_avoid         = @("docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md (CLEAN-era, not active)", "archive/", "docs/AI_OS/index/")
        risk_class            = "high"
        suggested_lane        = "governance_codex"
        blocked_paths         = @("Protected root files: AGENTS.md, README.md, WHITEPAPER.md, RISK_POLICY.md")
        human_approval        = $true
        recommended_next      = "Read docs/governance/source-of-truth-map.md and docs/audits/active-system-map.md before proposing changes. Changes to governance docs require DRY_RUN review."
        confidence            = "high"
        reason                = "Source-of-truth map is the primary ownership authority per README.md and active-system-map.md."
    }
)

function Get-TopicMatch {
    param([string]$TopicInput, [array]$RouteTable)

    $topicLower = $TopicInput.ToLowerInvariant()
    $bestMatch = $null
    $bestScore = 0

    foreach ($route in $RouteTable) {
        $score = 0
        foreach ($kw in $route.keywords) {
            if ($topicLower -contains $kw -or $topicLower.Contains($kw)) {
                $score++
            }
        }
        if ($score -gt $bestScore) {
            $bestScore = $score
            $bestMatch = $route
        }
    }

    # High-risk keyword override: always flag critical topics
    foreach ($kw in $highRiskKeywords) {
        if ($topicLower.Contains($kw)) {
            # Check if a critical/blocked route covers this keyword
            $criticalRoute = $RouteTable | Where-Object { $_.risk_class -eq "CRITICAL" -and $_.keywords -contains $kw }
            if ($criticalRoute -and ($null -eq $bestMatch -or $bestMatch.risk_class -ne "CRITICAL")) {
                $bestMatch = $criticalRoute
                $bestScore = 99
            }
        }
    }

    if ($null -eq $bestMatch) {
        return [ordered]@{
            topic                 = $TopicInput
            authority_owner       = "UNKNOWN"
            supporting_sources    = @("docs/governance/source-of-truth-map.md", "docs/audits/active-system-map.md")
            archive_avoid         = @()
            risk_class            = "unknown"
            suggested_lane        = "UNKNOWN"
            blocked_paths         = @()
            human_approval        = $true
            recommended_next      = "Read docs/governance/source-of-truth-map.md and docs/audits/active-system-map.md to identify the correct authority file before proceeding."
            confidence            = "low"
            reason                = "No routing match found. Default to canonical governance docs for manual classification."
        }
    }

    $match = [ordered]@{}
    $match["topic"] = $TopicInput
    foreach ($key in $bestMatch.Keys) {
        $match[$key] = $bestMatch[$key]
    }
    return $match
}

$match = Get-TopicMatch -TopicInput $Topic -RouteTable $routes

if ($QuietJson) {
    $match | ConvertTo-Json -Depth 4
    exit 0
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Source-of-Truth Resolver" -ForegroundColor Cyan
Write-Host "Mode: READ_ONLY - does not mutate files"
Write-Host "Topic: $Topic"
Write-Host ""

$riskColor = switch ($match.risk_class) {
    "CRITICAL" { "Red" }
    "high"     { "Yellow" }
    "medium"   { "Cyan" }
    default    { "White" }
}

Write-Host "authority_owner:    $($match.authority_owner)" -ForegroundColor $riskColor
Write-Host "risk_class:         $($match.risk_class)" -ForegroundColor $riskColor
Write-Host "confidence:         $($match.confidence)"
Write-Host "suggested_lane:     $($match.suggested_lane)"
Write-Host "human_approval:     $($match.human_approval)"
Write-Host ""
Write-Host "supporting_sources:"
foreach ($src in $match.supporting_sources) { Write-Host "  - $src" }
Write-Host ""
Write-Host "archive_avoid:"
foreach ($a in $match.archive_avoid) { Write-Host "  - $a" }
Write-Host ""
Write-Host "blocked_paths:"
foreach ($b in $match.blocked_paths) { Write-Host "  - $b" }
Write-Host ""
Write-Host "recommended_next_action:" -ForegroundColor Green
Write-Host "  $($match.recommended_next)"
Write-Host ""
Write-Host "reason: $($match.reason)"
Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")

exit 0
