[CmdletBinding()]
param(
    [string]$InputPacketPath = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsPacketState {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = ""
            exists = $false
            read_as_evidence_only = $true
            json_parse_status = "NOT_ATTEMPTED"
            schema = "UNKNOWN"
            payload = $null
            error = ""
        }
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = $Path
            exists = $false
            read_as_evidence_only = $true
            json_parse_status = "NOT_ATTEMPTED"
            schema = "UNKNOWN"
            payload = $null
            error = "Input packet not found."
        }
    }

    $text = Get-Content -LiteralPath $Path -Raw
    try {
        $payload = $text | ConvertFrom-Json
        $schema = if ($payload.PSObject.Properties.Name -contains "schema") { $payload.schema } else { "UNKNOWN" }
        return [pscustomobject]@{
            status = "FOUND"
            path = $Path
            exists = $true
            read_as_evidence_only = $true
            json_parse_status = "PASS"
            schema = $schema
            payload = $payload
            error = ""
        }
    }
    catch {
        return [pscustomobject]@{
            status = "FOUND"
            path = $Path
            exists = $true
            read_as_evidence_only = $true
            json_parse_status = "REVIEW"
            schema = "UNKNOWN"
            payload = $null
            error = "JSON parse failed: $($_.Exception.Message)"
        }
    }
}

$requiredApprovalMarkers = @(
    "APPROVE_COMMIT",
    "APPROVE_PUSH",
    "APPROVE_PR_CREATE"
)

$packetState = Get-AiOsPacketState -Path $InputPacketPath

$preview = [pscustomobject]@{
    schema = "AIOS_APPROVAL_GATED_HANDOFF_PREVIEW.v1"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        preview_only = $true
        no_approval_mutation = $true
        no_queue_mutation = $true
        no_staging = $true
        no_commit = $true
        no_push = $true
        no_pr_create = $true
        no_merge = $true
        allowed_autonomy_levels = @("Level 1 - AUTO READ-ONLY", "Level 2 - AUTO REPORT / PREVIEW FILES")
        blocked_autonomy_levels = @("Level 3 - AUTO PREP", "Level 4 - APPROVED EXECUTION", "Level 5 - HARD GATE")
        governance_reference = "docs/governance/AI_OS_AUTONOMY_LEVELS.md"
    }
    execution_enabled = $false
    packet_state = [pscustomobject]@{
        status = $packetState.status
        path = $packetState.path
        exists = $packetState.exists
        read_as_evidence_only = $packetState.read_as_evidence_only
        json_parse_status = $packetState.json_parse_status
        schema = $packetState.schema
        error = $packetState.error
    }
    approval_requirements = @(
        [pscustomobject]@{
            approval_marker = "APPROVE_COMMIT"
            required_for = "future exact staging and commit only"
            does_not_authorize = @("push", "PR creation", "merge")
        }
        [pscustomobject]@{
            approval_marker = "APPROVE_PUSH"
            required_for = "future exact push only"
            does_not_authorize = @("commit", "PR creation", "merge")
        }
        [pscustomobject]@{
            approval_marker = "APPROVE_PR_CREATE"
            required_for = "future exact PR creation only"
            does_not_authorize = @("commit", "push", "merge")
        }
    )
    missing_approval_markers = @($requiredApprovalMarkers)
    blocked_actions = @(
        "automation/loop_engine.py",
        "API key usage",
        ".env usage",
        "external model API calls",
        "Codex subprocess execution",
        "scheduled/background loops",
        "auto APPLY",
        "auto commit",
        "auto push",
        "auto PR create",
        "auto merge",
        "approval mutation",
        "queue mutation",
        "staging",
        "commit",
        "push",
        "PR creation",
        "merge",
        "broker/OANDA/live trading/webhook/secrets/dashboard scope"
    )
    stop_conditions = @(
        "Input packet missing is allowed but cannot authorize execution.",
        "Missing approval markers block future protected actions.",
        "This preview must not mutate approvals or queues.",
        "Any request to stage, commit, push, create PRs, or merge stops this preview.",
        "Any Level 5 scope requires a separate explicit human-approved packet."
    )
    next_safe_action = if ($packetState.status -eq "MISSING") {
        "Provide an input packet path for handoff preview, or review this empty gate as evidence only."
    }
    elseif ($packetState.json_parse_status -ne "PASS") {
        "Stop and fix packet JSON before handoff review."
    }
    else {
        "Review approval requirements. Execution remains disabled."
    }
}

if ($OutputJson) {
    $preview | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Approval-Gated Handoff Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($preview.schema)"
Write-Host "Packet state: $($preview.packet_state.status)"
Write-Host "Execution enabled: $($preview.execution_enabled)"
Write-Host "Missing approval markers: $($preview.missing_approval_markers -join ', ')"
Write-Host "Next safe action: $($preview.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
