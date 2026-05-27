[CmdletBinding()]
param(
    [string]$BriefPath = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsJsonTextFromLines {
    param([string[]]$Lines)

    $startIndex = -1
    $endIndex = -1

    for ($i = 0; $i -lt $Lines.Count; $i++) {
        $trimmed = $Lines[$i].Trim()
        if ($trimmed.StartsWith("{")) {
            $startIndex = $i
            break
        }
    }

    for ($i = $Lines.Count - 1; $i -ge 0; $i--) {
        $trimmed = $Lines[$i].Trim()
        if ($trimmed.EndsWith("}")) {
            $endIndex = $i
            break
        }
    }

    if ($startIndex -lt 0 -or $endIndex -lt $startIndex) {
        return ""
    }

    return (@($Lines[$startIndex..$endIndex]) -join "`n").Trim()
}

function Invoke-AiOsPreviewJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string[]]$Arguments = @()
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = $Path
            exit_code = $null
            json = $null
            error = "Helper not found."
        }
    }

    $commandArguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Path)
    $commandArguments += @($Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & powershell @commandArguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    $lines = @($output | ForEach-Object { [string]$_ })
    $json = $null
    $errorText = ""

    try {
        $jsonText = Get-AiOsJsonTextFromLines -Lines $lines
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            $errorText = "No JSON object found in helper output."
        }
        else {
            $json = $jsonText | ConvertFrom-Json
        }
    }
    catch {
        $errorText = "JSON parse failed: $($_.Exception.Message)"
    }

    return [pscustomobject]@{
        status = if ($exitCode -eq 0 -and $null -ne $json) { "PASS" } else { "REVIEW" }
        path = $Path
        exit_code = $exitCode
        json = $json
        error = $errorText
    }
}

$morningPath = "automation/orchestration/control/Get-AiOsMorningBriefPacketPreview.DRY_RUN.ps1"
$loopPath = "automation/orchestration/control/Get-AiOsLoopEnginePreview.DRY_RUN.ps1"
$controllerPath = "automation/orchestration/control/Get-AiOsCommitPushPrController.DRY_RUN.ps1"

$briefArguments = @("-OutputJson")
if (-not [string]::IsNullOrWhiteSpace($BriefPath)) {
    $briefArguments += @("-BriefPath", $BriefPath)
}

$morningPreview = Invoke-AiOsPreviewJson -Path $morningPath -Arguments $briefArguments
$loopPreview = Invoke-AiOsPreviewJson -Path $loopPath -Arguments $briefArguments
$controllerPreview = Invoke-AiOsPreviewJson -Path $controllerPath -Arguments @("-OutputJson")

$stage = "BLOCKED"
if ($morningPreview.status -ne "PASS" -or $loopPreview.status -ne "PASS" -or $controllerPreview.status -ne "PASS") {
    $stage = "BLOCKED"
}
elseif ($morningPreview.json.recommended_mode -eq "HARD_GATE_REQUIRED") {
    $stage = "HARD_GATE_REQUIRED"
}
elseif ($morningPreview.json.brief_state.status -eq "MISSING") {
    $stage = "NO_BRIEF"
}
elseif ($morningPreview.json.recommended_mode -in @("DRY_RUN", "APPLY_PREVIEW_REQUIRED", "CONTROLLER_PREVIEW_REQUIRED")) {
    $stage = "PACKET_PREVIEW_READY"
}
else {
    $stage = "READY_FOR_HUMAN_REVIEW"
}

$packet = [pscustomobject]@{
    schema = "AIOS_SELF_BUILD_PREVIEW.v1"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        loop_mode = "single_pass"
        local_rule_based_preview_only = $true
        governance_reference = "docs/governance/AI_OS_AUTONOMY_LEVELS.md"
        workflow_reference = "docs/workflows/AI_OS_SELF_BUILD_PREVIEW_WORKFLOW.md"
        no_bypass = "Does not override AGENTS.md, README.md, security policy, branch protection, trading safety, packet scope, or human approval gates."
    }
    autonomy_levels_referenced = @(
        "Level 1 - AUTO READ-ONLY",
        "Level 2 - AUTO REPORT / PREVIEW FILES"
    )
    execution_enabled = $false
    self_build_stage = $stage
    morning_brief_packet_preview = [pscustomobject]@{
        status = $morningPreview.status
        path = $morningPreview.path
        payload = $morningPreview.json
        error = $morningPreview.error
    }
    loop_engine_preview = [pscustomobject]@{
        status = $loopPreview.status
        path = $loopPreview.path
        payload = $loopPreview.json
        error = $loopPreview.error
    }
    commit_push_pr_controller_preview = [pscustomobject]@{
        status = $controllerPreview.status
        path = $controllerPreview.path
        payload = $controllerPreview.json
        error = $controllerPreview.error
    }
    approval_requirements = @(
        "Human approval required before APPLY.",
        "APPROVE_COMMIT required before staging or commit.",
        "APPROVE_PUSH required before push.",
        "APPROVE_PR_CREATE required before PR creation.",
        "Merge requires separate explicit human approval and is not part of this preview."
    )
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
        "worker launch",
        "queue mutation",
        "approval mutation",
        "staging",
        "commit",
        "push",
        "PR creation",
        "merge",
        "broker/OANDA/live trading/webhook/secrets/dashboard scope"
    )
    stop_conditions = @(
        "Any helper missing or non-JSON blocks self-build preview.",
        "Hard-gate brief terms require a separate dedicated packet.",
        "Level 3, Level 4, and Level 5 remain gated.",
        "No API, Codex subprocess, daemon, queue mutation, approval mutation, staging, commit, push, PR creation, merge, or protected-scope action is allowed."
    )
    safety = [pscustomobject]@{
        files_written = 0
        queue_mutations = 0
        approval_mutations = 0
        workers_launched = 0
        api_calls = 0
        codex_subprocesses = 0
        files_staged = 0
        commits_performed = 0
        pushes_performed = 0
        prs_created = 0
        merges_performed = 0
    }
    next_safe_action = switch ($stage) {
        "NO_BRIEF" { "Provide a plain morning brief or review the no-brief preview state." }
        "PACKET_PREVIEW_READY" { "Review the packet preview and decide whether a separate scoped APPLY packet is warranted." }
        "HARD_GATE_REQUIRED" { "Stop and request a dedicated human-approved hard-gate packet." }
        "READY_FOR_HUMAN_REVIEW" { "Review combined preview evidence before any next packet." }
        default { "Stop and resolve blocked preview evidence." }
    }
}

if ($OutputJson) {
    $packet | ConvertTo-Json -Depth 20
    exit 0
}

Write-Host "AI_OS Self-Build Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($packet.schema)"
Write-Host "Self-build stage: $($packet.self_build_stage)"
Write-Host "Execution enabled: $($packet.execution_enabled)"
Write-Host "Morning preview: $($packet.morning_brief_packet_preview.status)"
Write-Host "Loop preview: $($packet.loop_engine_preview.status)"
Write-Host "Controller preview: $($packet.commit_push_pr_controller_preview.status)"
Write-Host "Next safe action: $($packet.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
