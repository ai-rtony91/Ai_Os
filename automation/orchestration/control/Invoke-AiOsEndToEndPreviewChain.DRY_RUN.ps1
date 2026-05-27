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

function Invoke-AiOsPreviewHelper {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Path,
        [string[]]$Arguments = @()
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            name = $Name
            path = $Path
            status = "MISSING"
            exit_code = $null
            schema = "UNKNOWN"
            payload = $null
            error = "Helper file not found."
            output = ""
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
    $text = ($lines -join "`n").Trim()
    $payload = $null
    $schema = "UNKNOWN"
    $errorText = ""

    try {
        $jsonText = Get-AiOsJsonTextFromLines -Lines $lines
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            $errorText = "No JSON object found in helper output."
        }
        else {
            $payload = $jsonText | ConvertFrom-Json
            if ($payload.PSObject.Properties.Name -contains "schema") {
                $schema = $payload.schema
            }
        }
    }
    catch {
        $errorText = "JSON parse failed: $($_.Exception.Message)"
    }

    return [pscustomobject]@{
        name = $Name
        path = $Path
        status = if ($exitCode -eq 0 -and $null -ne $payload) { "PASS" } else { "BLOCKED" }
        exit_code = $exitCode
        schema = $schema
        payload = $payload
        error = $errorText
        output = $text
    }
}

$helperResults = @(
    Invoke-AiOsPreviewHelper -Name "brief_preview" -Path "automation/orchestration/control/Get-AiOsMorningBriefPacketPreview.DRY_RUN.ps1" -Arguments @("-BriefPath", $BriefPath, "-OutputJson")
    Invoke-AiOsPreviewHelper -Name "planner_adapter_preview" -Path "automation/orchestration/control/Get-AiOsApiPlannerAdapter.DRY_RUN.ps1" -Arguments @("-FixturePath", $BriefPath, "-OutputJson")
    Invoke-AiOsPreviewHelper -Name "approval_handoff_preview" -Path "automation/orchestration/control/Get-AiOsApprovalGatedHandoff.DRY_RUN.ps1" -Arguments @("-OutputJson")
    Invoke-AiOsPreviewHelper -Name "loop_engine_preview" -Path "automation/orchestration/control/Get-AiOsLoopEnginePreview.DRY_RUN.ps1" -Arguments @("-BriefPath", $BriefPath, "-OutputJson")
    Invoke-AiOsPreviewHelper -Name "commit_push_pr_controller_preview" -Path "automation/orchestration/control/Get-AiOsCommitPushPrController.DRY_RUN.ps1" -Arguments @("-OutputJson")
)

$failedHelpers = @($helperResults | Where-Object { $_.status -ne "PASS" })
$chainState = if ($failedHelpers.Count -gt 0) { "BLOCKED" } else { "PREVIEW_READY" }
$briefPreviewResult = $helperResults | Where-Object { $_.name -eq "brief_preview" } | Select-Object -First 1
$plannerAdapterPreviewResult = $helperResults | Where-Object { $_.name -eq "planner_adapter_preview" } | Select-Object -First 1
$approvalHandoffPreviewResult = $helperResults | Where-Object { $_.name -eq "approval_handoff_preview" } | Select-Object -First 1
$loopEnginePreviewResult = $helperResults | Where-Object { $_.name -eq "loop_engine_preview" } | Select-Object -First 1
$commitPushPrControllerPreviewResult = $helperResults | Where-Object { $_.name -eq "commit_push_pr_controller_preview" } | Select-Object -First 1

$blockedActions = @(
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

$packet = [pscustomobject]@{
    schema = "AIOS_ENDTOEND_PREVIEW_CHAIN.v1"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        single_pass = $true
        preview_only = $true
        no_api_calls = $true
        no_network = $true
        no_codex_subprocess = $true
        no_worker_launch = $true
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
    autonomy_levels_referenced = @("Level 1 - AUTO READ-ONLY", "Level 2 - AUTO REPORT / PREVIEW FILES")
    execution_enabled = $false
    chain_state = $chainState
    helper_evidence = @($helperResults | ForEach-Object {
        [pscustomobject]@{
            name = $_.name
            path = $_.path
            status = $_.status
            exit_code = $_.exit_code
            schema = $_.schema
            error = $_.error
        }
    })
    brief_preview = $briefPreviewResult.payload
    planner_adapter_preview = $plannerAdapterPreviewResult.payload
    approval_handoff_preview = $approvalHandoffPreviewResult.payload
    loop_engine_preview = $loopEnginePreviewResult.payload
    commit_push_pr_controller_preview = $commitPushPrControllerPreviewResult.payload
    blocked_actions = $blockedActions
    stop_conditions = @(
        "Any helper failure marks chain_state BLOCKED.",
        "Any request for API keys, .env files, external model calls, or network execution stops this chain.",
        "Any request for Codex subprocess execution, scheduled/background loops, worker launch, queue mutation, or approval mutation stops this chain.",
        "Any request for APPLY, staging, commit, push, PR creation, or merge stops this chain.",
        "Any broker/OANDA/live trading/webhook/secrets/dashboard scope requires a separate explicit human-approved packet."
    )
    next_safe_action = if ($chainState -eq "BLOCKED") {
        "Stop and review helper_evidence before any next packet."
    }
    else {
        "Review the unified preview output. Execution remains disabled and protected actions require separate approval."
    }
}

if ($OutputJson) {
    $packet | ConvertTo-Json -Depth 18
    exit 0
}

Write-Host "AI_OS End-to-End Preview Chain"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($packet.schema)"
Write-Host "Chain state: $($packet.chain_state)"
Write-Host "Execution enabled: $($packet.execution_enabled)"
Write-Host "Helpers:"
foreach ($helper in $packet.helper_evidence) {
    Write-Host "  $($helper.name): $($helper.status) / $($helper.schema)"
}
Write-Host "Next safe action: $($packet.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
