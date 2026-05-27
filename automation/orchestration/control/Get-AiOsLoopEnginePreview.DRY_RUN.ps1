[CmdletBinding()]
param(
    [string]$BriefPath = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-AiOsGit {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        exit_code = $exitCode
        lines = @($output | ForEach-Object { [string]$_ })
        text = (@($output | ForEach-Object { [string]$_ }) -join "`n").Trim()
    }
}

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

function Invoke-AiOsControllerPreview {
    param([Parameter(Mandatory = $true)][string]$ControllerPath)

    if (-not (Test-Path -LiteralPath $ControllerPath -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            exit_code = $null
            json = $null
            error = "Controller helper not found."
        }
    }

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $ControllerPath -OutputJson 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    $lines = @($output | ForEach-Object { [string]$_ })
    $json = $null
    $errorText = ""

    try {
        $jsonText = Get-AiOsJsonTextFromLines -Lines $lines
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            $errorText = "No JSON object found in controller output."
        }
        else {
            $json = $jsonText | ConvertFrom-Json
        }
    }
    catch {
        $errorText = "Controller JSON parse failed: $($_.Exception.Message)"
    }

    return [pscustomobject]@{
        status = if ($exitCode -eq 0 -and $null -ne $json) { "PASS" } else { "REVIEW" }
        exit_code = $exitCode
        json = $json
        error = $errorText
    }
}

function Get-AiOsBriefState {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = ""
            exists = $false
            read_as_evidence_only = $true
            length = 0
            line_count = 0
            preview = @()
        }
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = $Path
            exists = $false
            read_as_evidence_only = $true
            length = 0
            line_count = 0
            preview = @()
        }
    }

    $content = Get-Content -LiteralPath $Path -Raw
    $lines = @($content -split "`r?`n")
    return [pscustomobject]@{
        status = "FOUND"
        path = $Path
        exists = $true
        read_as_evidence_only = $true
        length = $content.Length
        line_count = $lines.Count
        preview = @($lines | Select-Object -First 20)
    }
}

$repoRootResult = Invoke-AiOsGit -Arguments @("rev-parse", "--show-toplevel")
if ($repoRootResult.exit_code -ne 0 -or [string]::IsNullOrWhiteSpace($repoRootResult.text)) {
    throw "Unable to resolve git repository root."
}

$repoRoot = $repoRootResult.text.Trim()
Set-Location -LiteralPath $repoRoot

$controllerPath = "automation/orchestration/control/Get-AiOsCommitPushPrController.DRY_RUN.ps1"
$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$branchResult = Invoke-AiOsGit -Arguments @("branch", "--show-current")
$statusResult = Invoke-AiOsGit -Arguments @("status", "--short", "--branch")
$briefState = Get-AiOsBriefState -Path $BriefPath
$controllerPreview = Invoke-AiOsControllerPreview -ControllerPath $controllerPath

$packet = [pscustomobject]@{
    schema = "AIOS_LOOP_ENGINE_PREVIEW.v1"
    mode = "DRY_RUN"
    generated_at = $generatedAt
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        loop_mode = "single_pass"
        allowed_autonomy_levels = @(
            "Level 1 - AUTO READ-ONLY",
            "Level 2 - AUTO REPORT / PREVIEW FILES"
        )
        blocked_autonomy_levels = @(
            "Level 3 - AUTO PREP",
            "Level 4 - APPROVED EXECUTION",
            "Level 5 - HARD GATE"
        )
        governance_reference = "docs/governance/AI_OS_AUTONOMY_LEVELS.md"
        controller_reference = $controllerPath
        no_bypass = "Does not override AGENTS.md, README.md, security policy, branch protection, trading safety, packet scope, or human approval gates."
    }
    autonomy_levels_referenced = @(
        [pscustomobject]@{
            level = "Level 1 - AUTO READ-ONLY"
            use = "Read repo/controller/brief evidence only."
        }
        [pscustomobject]@{
            level = "Level 2 - AUTO REPORT / PREVIEW FILES"
            use = "Emit preview JSON to stdout only in this implementation; no files are written."
        }
    )
    execution_enabled = $false
    loop_mode = "single_pass"
    repo_state = [pscustomobject]@{
        repo_root = $repoRoot
        branch = if ($branchResult.exit_code -eq 0) { $branchResult.text } else { "UNKNOWN" }
        status = if ($statusResult.exit_code -eq 0) { $statusResult.lines } else { @("UNKNOWN") }
    }
    brief_state = $briefState
    controller_preview = [pscustomobject]@{
        status = $controllerPreview.status
        exit_code = $controllerPreview.exit_code
        schema = if ($controllerPreview.json) { $controllerPreview.json.schema } else { "UNKNOWN" }
        result = if ($controllerPreview.json -and $controllerPreview.json.dry_run_result) { $controllerPreview.json.dry_run_result.result } else { "UNKNOWN" }
        payload = $controllerPreview.json
        error = $controllerPreview.error
    }
    approval_requirements = @(
        "Human approval required before APPLY.",
        "APPROVE_COMMIT required before staging or commit.",
        "APPROVE_PUSH required before push.",
        "APPROVE_PR_CREATE required before PR creation.",
        "Merge requires separate explicit human approval and is not part of this wrapper."
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
        "Controller preview helper missing or non-JSON.",
        "Brief evidence missing is allowed and marked MISSING.",
        "Any requested Level 3, Level 4, or Level 5 action stops this wrapper.",
        "Any request to loop, schedule, launch workers, call model APIs, mutate approvals, stage, commit, push, create PRs, merge, or touch protected scope stops this wrapper."
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
    next_safe_action = if ($controllerPreview.status -eq "PASS") {
        "Review this single-pass preview. Protected actions still require separate explicit approval."
    }
    else {
        "Stop and review controller preview status before considering any next packet."
    }
}

if ($OutputJson) {
    $packet | ConvertTo-Json -Depth 16
    exit 0
}

Write-Host "AI_OS Loop Engine Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($packet.schema)"
Write-Host "Loop mode: $($packet.loop_mode)"
Write-Host "Execution enabled: $($packet.execution_enabled)"
Write-Host "Brief state: $($packet.brief_state.status)"
Write-Host "Controller preview: $($packet.controller_preview.status) / $($packet.controller_preview.result)"
Write-Host "Next safe action: $($packet.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
