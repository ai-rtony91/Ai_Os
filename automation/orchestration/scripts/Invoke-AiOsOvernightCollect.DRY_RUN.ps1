[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$EvidenceRoot = "automation/orchestration/overnight_evidence",
    [string]$ReportRoot = "automation/orchestration/reports",
    [switch]$PlanOnly,
    [switch]$Collect
)

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $gitResult = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($gitResult)) {
        $RepoRoot = $gitResult.Trim()
    } else {
        $RepoRoot = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName
    }
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot -ErrorAction Stop).Path

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$schema = "AIOS_OVERNIGHT_EVIDENCE_COLLECTOR_PLAN.v1"
$dateKey = (Get-Date).ToString("yyyy-MM-dd")
$effectivePlanOnly = -not $Collect

function Resolve-AiOsRepoRoot {
    param([AllowEmptyString()][string]$RequestedRoot)

    if (-not [string]::IsNullOrWhiteSpace($RequestedRoot)) {
        $resolvedOverride = Resolve-Path -LiteralPath $RequestedRoot -ErrorAction Stop
        return $resolvedOverride.ProviderPath
    }

    $gitOutput = & git rev-parse --show-toplevel 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to resolve AI_OS repo root with git rev-parse --show-toplevel. Run this script from inside the active repository or pass -RepoRoot explicitly."
    }

    $resolvedRoot = ($gitOutput | Select-Object -First 1)
    if ([string]::IsNullOrWhiteSpace($resolvedRoot)) {
        throw "Git returned an empty repo root. Pass -RepoRoot explicitly or rerun from inside the active repository."
    }

    return [string]$resolvedRoot
}

function ConvertTo-AiOsRelativePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return ($Path -replace "\\", "/").Trim("/")
}

function Join-AiOsPlanPath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string[]]$Child
    )

    $parts = @((ConvertTo-AiOsRelativePath -Path $Root)) + @($Child | ForEach-Object { ConvertTo-AiOsRelativePath -Path $_ })
    return ($parts | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join "/"
}

function Test-AiOsPathPresent {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = Join-Path -Path $RepoRoot -ChildPath $Path
    return Test-Path -LiteralPath $fullPath
}

$RepoRoot = Resolve-AiOsRepoRoot -RequestedRoot $RepoRoot

$sourceDefinitions = @(
    [ordered]@{
        id = "validator_recommendation"
        command_mode = "future_json_stdout"
        source_path = "automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "validator_recommendation.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "validator_chain"
        command_mode = "future_json_stdout"
        source_path = "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "validator_chain.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "approval_inbox_summary"
        command_mode = "future_json_stdout"
        source_path = "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "approval_inbox_summary.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "commit_package_recommendation"
        command_mode = "future_json_stdout"
        source_path = "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "commit_package_recommendation.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "action_recommendation"
        command_mode = "future_json_stdout"
        source_path = "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "action_recommendation.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "next_packet_recommendation"
        command_mode = "future_json_stdout"
        source_path = "automation/orchestration/recommendations/Get-AiOsNextPacketRecommendation.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "next_packet_recommendation.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "work_packets"
        command_mode = "future_read_only_folder_summary"
        source_path = "automation/orchestration/work_packets"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "work_packets_summary.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "worker_registry"
        command_mode = "future_read_only_folder_summary"
        source_path = "automation/orchestration/workers"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "worker_registry_summary.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "orchestration_health"
        command_mode = "future_json_stdout"
        source_path = "automation/orchestration/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "orchestration_health.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "work_ledger"
        command_mode = "future_read_only_jsonl_summary"
        source_path = "telemetry/work_ledger.jsonl"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "work_ledger_summary.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "github_status"
        command_mode = "future_optional_json_stdout"
        source_path = "automation/orchestration/github_status/Get-AiOsGitHubStatusCheck.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "github_status.json")
        safe_for_future_collection = $true
    },
    [ordered]@{
        id = "operator_status_line"
        command_mode = "future_text_stdout"
        source_path = "automation/orchestration/control_summary/Get-AiOsOperatorStatusLine.DRY_RUN.ps1"
        planned_output_path = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "sources", "operator_status.txt")
        safe_for_future_collection = $true
    }
)

$plannedSources = foreach ($source in $sourceDefinitions) {
    $sourcePresent = Test-AiOsPathPresent -Path $source.source_path
    [ordered]@{
        id = $source.id
        source_path = $source.source_path
        source_present = $sourcePresent
        command_mode = $source.command_mode
        planned_output_path = $source.planned_output_path
        safe_for_future_collection = $source.safe_for_future_collection
        collection_status = if ($sourcePresent) { "PLANNED" } else { "MISSING" }
    }
}

$approvalInboxSeedPresent = Test-AiOsPathPresent -Path "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"
$approvalGatePresent = Test-AiOsPathPresent -Path "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"
$approvalInboxSeedStatus = if ($approvalInboxSeedPresent) { "present" } else { "deferred_missing" }

$plannedDateFolder = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey)
$plannedOutputPaths = [ordered]@{
    date_folder = $plannedDateFolder
    manifest = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "manifest.json")
    collection_summary = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "collection_summary.json")
    morning_brief_input = Join-AiOsPlanPath -Root $EvidenceRoot -Child @($dateKey, "morning_brief_input.json")
    morning_brief_report = Join-AiOsPlanPath -Root $ReportRoot -Child @("morning_brief_$dateKey.json")
    source_outputs = @($plannedSources | ForEach-Object { $_.planned_output_path })
}

# ENFORCEMENT CONTRACT — NOT DECORATIVE:
# The actions listed in $blockedActions are hard stops for this script.
# Any future edit that causes this script to perform a blocked action
# is unauthorized and must be blocked by West review before merging.

# These blocked actions are permanent safety boundaries for this collector.
# Any future Collect implementation must enforce them with explicit guards
# before file writes, child command execution, or network calls. Do not remove
# blocked actions without a separate West safety review.
$blockedActions = @(
    "runtime_start",
    "scheduler_change",
    "backup_execution",
    "packet_state_change",
    "approval_state_change",
    "lock_state_change",
    "worker_lane_mutation",
    "worker_start",
    "webhook_execution",
    "dashboard_edit",
    "repository_stage_commit_or_remote_update",
    "protected_root_edit",
    "live_trading_or_broker_scope",
    "secret_or_credential_access"
)

$collectStatus = "PLAN_ONLY_PREVIEW"
$nextSafeAction = "Review this plan, then approve one future collection packet if the output paths and source list are acceptable."
$collectOutputPaths = @()

if ($Collect) {
    $gateFile = Join-Path -Path $RepoRoot -ChildPath "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"
    if (-not (Test-Path -LiteralPath $gateFile)) {
        $collectStatus = "COLLECT_BLOCKED_NO_APPROVAL_GATE"
        $nextSafeAction = "Approval gate file not found. No evidence files written."
    } else {
        $collectStatus = "COLLECT_IN_PROGRESS"
        $datestamp = (Get-Date -Format "yyyyMMdd_HHmm")
        $evidenceDir = Join-Path -Path $RepoRoot -ChildPath "telemetry/evidence"
        if (-not (Test-Path -LiteralPath $evidenceDir)) {
            New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
        }

        $sourcesAttempted = @()
        $sourcesSucceeded = @()
        $sourcesFailed = @()

        foreach ($source in $sourceDefinitions) {
            # Always skip t9_snapshot_backup unconditionally
            if ($source.id -eq "t9_snapshot_backup") { continue }
            # Only collect sources marked safe_for_unattended_dry_run or safe_for_future_collection
            $safeFlag = $source["safe_for_unattended_dry_run"]
            if ($null -eq $safeFlag) { $safeFlag = $source["safe_for_future_collection"] }
            if (-not $safeFlag) { continue }

            $sourcesAttempted += $source.id
            $sourceScriptPath = Join-Path -Path $RepoRoot -ChildPath $source.source_path

            try {
                if (-not (Test-Path -LiteralPath $sourceScriptPath)) {
                    throw "Source script not found: $sourceScriptPath"
                }
                $stdout = & powershell -ExecutionPolicy Bypass -File $sourceScriptPath 2>&1
                $outFile = Join-Path -Path $evidenceDir -ChildPath "$($source.id)_${datestamp}Z.json"
                $stdout | Out-File -FilePath $outFile -Encoding utf8 -Force
                $collectOutputPaths += $outFile
                $sourcesSucceeded += $source.id
            } catch {
                $sourcesFailed += $source.id
            }
        }

        $manifestPath = Join-Path -Path $evidenceDir -ChildPath "COLLECTION_MANIFEST_${datestamp}.json"
        $manifest = [ordered]@{
            schema             = "AIOS_COLLECTION_MANIFEST.v1"
            collected_at       = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
            source_count       = $sourcesAttempted.Count
            sources_attempted  = $sourcesAttempted
            sources_succeeded  = $sourcesSucceeded
            sources_failed     = $sourcesFailed
            output_paths       = $collectOutputPaths
        }
        $manifest | ConvertTo-Json -Depth 5 | Out-File -FilePath $manifestPath -Encoding utf8 -Force
        $collectOutputPaths += $manifestPath
        $collectStatus = "COLLECT_COMPLETE"
        $nextSafeAction = "Review evidence files in telemetry/evidence/ before any mutation."
    }
}

$report = [ordered]@{
    schema = $schema
    mode = "DRY_RUN"
    repo_root = $RepoRoot
    evidence_root = $EvidenceRoot
    report_root = $ReportRoot
    date_key = $dateKey
    plan_only = $effectivePlanOnly
    collect_enabled = $false
    collect_request_status = $collectStatus
    planned_sources = @($plannedSources)
    planned_output_paths = $plannedOutputPaths
    approval_inbox_001_present = $approvalInboxSeedPresent
    approval_inbox_seed_status = $approvalInboxSeedStatus
    apply_approval_gate_present = $approvalGatePresent
    github_status_optional = $true
    backup_source_rule = "Backup status may be represented by status-line evidence only; backup script execution is out of scope."
    blocked_actions = $blockedActions
    safe_to_collect_later = $false
    next_safe_action = $nextSafeAction
}

$report | ConvertTo-Json -Depth 10
