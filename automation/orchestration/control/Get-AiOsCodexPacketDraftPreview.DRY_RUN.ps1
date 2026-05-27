[CmdletBinding()]
param(
    [string]$BriefPath = "inputs/morning_brief_fixture_stage2.txt",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsJsonTextFromLines {
    param([string[]]$Lines)

    $startIndex = -1
    $endIndex = -1

    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i].Trim().StartsWith("{")) {
            $startIndex = $i
            break
        }
    }

    for ($i = $Lines.Count - 1; $i -ge 0; $i--) {
        if ($Lines[$i].Trim().EndsWith("}")) {
            $endIndex = $i
            break
        }
    }

    if ($startIndex -lt 0 -or $endIndex -lt $startIndex) {
        return ""
    }

    return (@($Lines[$startIndex..$endIndex]) -join "`n").Trim()
}

function Invoke-AiOsEndToEndPreview {
    param([string]$Path)

    $helperPath = "automation/orchestration/control/Invoke-AiOsEndToEndPreviewChain.DRY_RUN.ps1"
    if (-not (Test-Path -LiteralPath $helperPath -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            exit_code = $null
            schema = "UNKNOWN"
            payload = $null
            error = "End-to-end preview chain helper missing."
        }
    }

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $helperPath -BriefPath $Path -OutputJson 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    $lines = @($output | ForEach-Object { [string]$_ })
    $payload = $null
    $schema = "UNKNOWN"
    $errorText = ""

    try {
        $jsonText = Get-AiOsJsonTextFromLines -Lines $lines
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            $errorText = "No JSON object found in end-to-end preview output."
        }
        else {
            $payload = $jsonText | ConvertFrom-Json
            if ($payload.PSObject.Properties.Name -contains "schema") {
                $schema = $payload.schema
            }
        }
    }
    catch {
        $errorText = "End-to-end preview JSON parse failed: $($_.Exception.Message)"
    }

    return [pscustomobject]@{
        status = if ($exitCode -eq 0 -and $null -ne $payload) { "PASS" } else { "BLOCKED" }
        exit_code = $exitCode
        schema = $schema
        payload = $payload
        error = $errorText
    }
}

function Format-AiOsBulletList {
    param([object[]]$Items)

    $values = @($Items | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | ForEach-Object { [string]$_ })
    if ($values.Count -eq 0) {
        return "- NONE"
    }

    return (($values | ForEach-Object { "- $_" }) -join "`n")
}

$sourcePreview = Invoke-AiOsEndToEndPreview -Path $BriefPath
$source = $sourcePreview.payload
$briefPreview = if ($source -and $source.brief_preview) { $source.brief_preview } else { $null }
$plannerPreview = if ($source -and $source.planner_adapter_preview -and $source.planner_adapter_preview.planner_preview) { $source.planner_adapter_preview.planner_preview } else { $null }

$recommendedMode = if ($briefPreview -and $briefPreview.recommended_mode) {
    [string]$briefPreview.recommended_mode
}
elseif ($plannerPreview -and $plannerPreview.proposed_mode) {
    [string]$plannerPreview.proposed_mode
}
else {
    "DRY_RUN"
}

$isHardGate = $recommendedMode -eq "HARD_GATE_REQUIRED"
$packetMode = "DRY_RUN"
$packetId = if ($briefPreview -and $briefPreview.proposed_packet_id) { [string]$briefPreview.proposed_packet_id } else { "PKT-EAST-CODEX-PACKET-DRAFT-PREVIEW-001" }
$lane = if ($briefPreview -and $briefPreview.recommended_lane) { [string]$briefPreview.recommended_lane } else { "codex packet draft preview" }
$objective = if ($briefPreview -and $briefPreview.inferred_objective) { [string]$briefPreview.inferred_objective } else { "Review generated AI_OS packet draft evidence." }
$allowedPaths = if ($briefPreview -and $briefPreview.allowed_paths_preview) { @($briefPreview.allowed_paths_preview) } else { @("read-only") }
$forbiddenPaths = if ($briefPreview -and $briefPreview.forbidden_paths_preview) { @($briefPreview.forbidden_paths_preview) } else { @() }
$blockedActions = if ($source -and $source.blocked_actions) { @($source.blocked_actions) } else {
    @(
        "API key usage",
        ".env usage",
        "external model API calls",
        "subprocess Codex execution",
        "scheduled/background loops",
        "auto APPLY",
        "auto commit",
        "auto push",
        "auto PR create",
        "auto merge",
        "broker/OANDA/live trading/webhook/secrets/dashboard scope"
    )
}
$stopConditions = if ($source -and $source.stop_conditions) { @($source.stop_conditions) } else { @("Review draft-only packet before any execution packet.") }

$approvalMarkers = @(
    "APPROVE_COMMIT",
    "APPROVE_PUSH",
    "APPROVE_PR_CREATE"
)

$draftState = if ($sourcePreview.status -ne "PASS") {
    "BLOCKED"
}
elseif ($isHardGate) {
    "HARD_GATE_REVIEW_DRAFT"
}
else {
    "DRAFT_READY"
}

$missionText = if ($isHardGate) {
    "Review the hard-gate request inferred from the morning brief. Do not APPLY or execute protected actions."
}
else {
    "Review the inferred AI_OS objective and decide whether to issue a separate governed work packet."
}

$codexPacketText = @"
DRAFT_ONLY - NOT AUTHORIZED FOR EXECUTION
CODEX-ONLY PROMPT
AI_OS EXECUTION TOKEN

Packet ID: $packetId
Mode: $packetMode
Zone: EAST
Worker: EAST_OCC_01
Lane: $lane
Branch: packet-generator-preview
Worktree: C:\Dev\Ai.Os

MISSION:
$missionText

INFERRED OBJECTIVE:
$objective

RECOMMENDED FUTURE MODE:
$recommendedMode

READ FIRST:
- AGENTS.md
- README.md
- docs/governance/AI_OS_AUTONOMY_LEVELS.md
- docs/workflows/AI_OS_ENDTOEND_PREVIEW_CHAIN_WORKFLOW.md

ALLOWED FILES:
$(Format-AiOsBulletList -Items $allowedPaths)

DO NOT TOUCH:
$(Format-AiOsBulletList -Items (@($forbiddenPaths) + @("apps/", "services/", "pipeline/", "Python files", "package/dependency files", "tests/", "automation/loop_engine.py", "broker/OANDA/live trading/webhook/secrets/.env", "commit/push/PR/merge execution paths")))

RULES:
- This generated packet is draft-only evidence.
- Human review is required before any future execution packet.
- Approval markers are required, not granted.
- Do not call APIs.
- Do not use .env files.
- Do not launch Codex subprocesses.
- Do not mutate queues or approvals.
- Do not stage, commit, push, create PRs, or merge.

APPROVAL MARKERS REQUIRED BUT NOT GRANTED:
- APPROVE_COMMIT
- APPROVE_PUSH
- APPROVE_PR_CREATE

VALIDATION:
- git diff --check
- powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/control/Invoke-AiOsEndToEndPreviewChain.DRY_RUN.ps1 -BriefPath $BriefPath -OutputJson

FINAL REPORT:
Packet draft result:
Source preview result:
Approval marker behavior:
Blocked actions preserved:
Validation result:
Commit performed: NO
Push performed: NO
PR created: NO
Merge performed: NO

STOP POINT:
Stop after report. No edits, staging, commit, push, PR creation, merge, secrets, API calls, broker/OANDA, live trading, webhook, or dashboard work.
"@

$packet = [pscustomobject]@{
    schema = "AIOS_CODEX_PACKET_DRAFT_PREVIEW.v1"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        draft_only = $true
        preview_only = $true
        no_api_calls = $true
        no_network = $true
        no_codex_subprocess = $true
        no_file_writes = $true
        no_queue_mutation = $true
        no_approval_mutation = $true
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
    draft_only = $true
    source_preview_schema = $sourcePreview.schema
    source_preview_status = $sourcePreview.status
    packet_draft_state = $draftState
    codex_packet_text = $codexPacketText
    packet_fields = [pscustomobject]@{
        packet_id = $packetId
        mode = $packetMode
        recommended_future_mode = $recommendedMode
        zone = "EAST"
        worker = "EAST_OCC_01"
        lane = $lane
        branch = "packet-generator-preview"
        worktree = "C:\Dev\Ai.Os"
        mission = $missionText
        inferred_objective = $objective
        allowed_files = @($allowedPaths)
        do_not_touch = @($forbiddenPaths)
        hard_gate_review_only = $isHardGate
    }
    approval_markers_referenced = @($approvalMarkers | ForEach-Object {
        [pscustomobject]@{
            approval_marker = $_
            status = "REQUIRED_NOT_GRANTED"
        }
    })
    blocked_actions = @($blockedActions)
    stop_conditions = @($stopConditions)
    source_error = $sourcePreview.error
    next_safe_action = if ($draftState -eq "BLOCKED") {
        "Stop and review source_error before using this draft."
    }
    elseif ($isHardGate) {
        "Review the hard-gate draft only. A separate explicit human-approved packet is required."
    }
    else {
        "Review codex_packet_text. It is not executable approval."
    }
}

if ($OutputJson) {
    $packet | ConvertTo-Json -Depth 16
    exit 0
}

Write-Host "AI_OS Codex Packet Draft Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($packet.schema)"
Write-Host "Draft state: $($packet.packet_draft_state)"
Write-Host "Source preview: $($packet.source_preview_status) / $($packet.source_preview_schema)"
Write-Host "Execution enabled: $($packet.execution_enabled)"
Write-Host "Draft only: $($packet.draft_only)"
Write-Host "Next safe action: $($packet.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
