[CmdletBinding()]
param(
    [ValidateSet("DRY_RUN")]
    [string]$Mode = "DRY_RUN",

    [string]$RepoRoot,

    [switch]$OutputJson
)

$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    param([string]$RequestedRoot)

    if (-not [string]::IsNullOrWhiteSpace($RequestedRoot)) {
        return (Resolve-Path -LiteralPath $RequestedRoot).Path
    }

    $current = (Get-Location).Path
    while (-not [string]::IsNullOrWhiteSpace($current)) {
        if ((Test-Path -LiteralPath (Join-Path $current "AGENTS.md") -PathType Leaf) -and
            (Test-Path -LiteralPath (Join-Path $current "README.md") -PathType Leaf)) {
            return $current
        }

        $parent = Split-Path -Parent $current
        if ($parent -eq $current) {
            break
        }
        $current = $parent
    }

    return (Get-Location).Path
}

function Invoke-Git {
    param(
        [string]$Root,
        [string[]]$Arguments
    )

    $output = & git -C $Root @Arguments 2>&1
    return [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Output = @($output)
    }
}

function Add-Message {
    param(
        [System.Collections.Generic.List[string]]$List,
        [string]$Message
    )

    if (-not $List.Contains($Message)) {
        $List.Add($Message) | Out-Null
    }
}

$repoRootResolved = Resolve-AiOsRepoRoot -RequestedRoot $RepoRoot
$currentPath = (Get-Location).Path

$blockers = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()
$nextActions = [System.Collections.Generic.List[string]]::new()

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
$openAiCommand = Get-Command openai -ErrorAction SilentlyContinue
$codexCommand = Get-Command codex -ErrorAction SilentlyContinue

$agentsPath = Join-Path $repoRootResolved "AGENTS.md"
$readmePath = Join-Path $repoRootResolved "README.md"
$onboardingDocPath = Join-Path $repoRootResolved "docs/workflows/OPENAI_CODEX_NIGHT_SUPERVISOR_ONBOARDING.md"
$nightSupervisorDir = Join-Path $repoRootResolved "automation/orchestration/night_supervisor"
$nightSupervisorScript = Join-Path $nightSupervisorDir "Invoke-AiOsNightSupervisor.DRY_RUN.ps1"
$approvalQueueScript = Join-Path $nightSupervisorDir "Invoke-AiOsApprovalQueue.DRY_RUN.ps1"
$telemetryNightSupervisor = Join-Path $repoRootResolved "telemetry/night_supervisor"

$agentsFound = Test-Path -LiteralPath $agentsPath -PathType Leaf
$readmeFound = Test-Path -LiteralPath $readmePath -PathType Leaf
$onboardingDocFound = Test-Path -LiteralPath $onboardingDocPath -PathType Leaf
$nightSupervisorDirFound = Test-Path -LiteralPath $nightSupervisorDir -PathType Container
$nightSupervisorScriptFound = Test-Path -LiteralPath $nightSupervisorScript -PathType Leaf
$approvalQueueScriptFound = Test-Path -LiteralPath $approvalQueueScript -PathType Leaf
$telemetryNightSupervisorFound = Test-Path -LiteralPath $telemetryNightSupervisor -PathType Container

$branch = "UNKNOWN"
$gitStatus = @()
$stagedIndex = @()
$gitAvailable = $null -ne $gitCommand

if (-not $gitAvailable) {
    Add-Message -List $blockers -Message "git command not found on PATH."
} else {
    $branchResult = Invoke-Git -Root $repoRootResolved -Arguments @("branch", "--show-current")
    if ($branchResult.ExitCode -eq 0 -and $branchResult.Output.Count -gt 0) {
        $branch = [string]$branchResult.Output[0]
    } else {
        Add-Message -List $blockers -Message "Unable to determine current Git branch."
    }

    $statusResult = Invoke-Git -Root $repoRootResolved -Arguments @("status", "--short", "--branch")
    if ($statusResult.ExitCode -eq 0) {
        $gitStatus = @($statusResult.Output)
    } else {
        Add-Message -List $blockers -Message "Unable to read Git status."
    }

    $stagedResult = Invoke-Git -Root $repoRootResolved -Arguments @("diff", "--cached", "--name-status")
    if ($stagedResult.ExitCode -eq 0) {
        $stagedIndex = @($stagedResult.Output)
    } else {
        Add-Message -List $blockers -Message "Unable to read staged Git index."
    }
}

$stagedIndexClean = $stagedIndex.Count -eq 0
$dirtyStatus = @($gitStatus | Where-Object { $_ -notmatch "^## " })
$statusHeader = @($gitStatus | Where-Object { $_ -match "^## " } | Select-Object -First 1)
$branchSynced = $true
if ($statusHeader.Count -gt 0 -and ($statusHeader[0] -match "\[ahead|\[behind|\[ahead .*behind")) {
    $branchSynced = $false
}

if (-not $agentsFound) {
    Add-Message -List $blockers -Message "AGENTS.md not found."
}
if (-not $readmeFound) {
    Add-Message -List $blockers -Message "README.md not found."
}
if (-not $onboardingDocFound) {
    Add-Message -List $blockers -Message "Onboarding workflow document not found."
}
if ($branch -ne "main") {
    Add-Message -List $blockers -Message "Current branch is '$branch'; expected 'main' for onboarding closeout."
}
if (-not $stagedIndexClean) {
    Add-Message -List $blockers -Message "Staged index is not empty."
}
if ($dirtyStatus.Count -gt 0) {
    Add-Message -List $warnings -Message "Working tree has dirty files; shared-checkout collision risk exists and must be reviewed before worker launch."
}
if (-not $branchSynced) {
    Add-Message -List $warnings -Message "Branch is ahead or behind upstream; review before shared-checkout work."
}
if ($null -eq $openAiCommand) {
    Add-Message -List $warnings -Message "openai CLI not found on PATH."
}
if ($null -eq $codexCommand) {
    Add-Message -List $warnings -Message "codex CLI not found on PATH."
}
if (-not $nightSupervisorDirFound) {
    Add-Message -List $warnings -Message "Night Supervisor directory not found."
}
if (-not $nightSupervisorScriptFound) {
    Add-Message -List $warnings -Message "Night Supervisor DRY_RUN script not found."
}
if (-not $approvalQueueScriptFound) {
    Add-Message -List $warnings -Message "Night Supervisor approval queue script not found."
}
if (-not $telemetryNightSupervisorFound) {
    Add-Message -List $warnings -Message "telemetry/night_supervisor folder not found."
}

$collisionRisk = (-not $stagedIndexClean) -or ($dirtyStatus.Count -gt 0) -or ($branch -ne "main")

if ($blockers.Count -gt 0) {
    $status = "BLOCKED"
    Add-Message -List $nextActions -Message "Resolve blockers before launching Codex, Claude, or Night Supervisor work."
} elseif ($warnings.Count -gt 0) {
    $status = "REVIEW_REQUIRED"
    Add-Message -List $nextActions -Message "Review warnings; continue only with Human Owner acceptance for read-only work."
} else {
    $status = "READY"
    Add-Message -List $nextActions -Message "Run the next approved onboarding, Codex, or Night Supervisor DRY_RUN packet from clean main."
}

$result = [ordered]@{
    schema = "aios.openai_codex_night_supervisor_readiness.v1"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    repo_root = $repoRootResolved
    current_path = $currentPath
    branch = $branch
    git_status = @($gitStatus)
    staged_index_clean = [bool]$stagedIndexClean
    openai_cli_found = [bool]($null -ne $openAiCommand)
    codex_cli_found = [bool]($null -ne $codexCommand)
    agents_md_found = [bool]$agentsFound
    readme_found = [bool]$readmeFound
    onboarding_doc_found = [bool]$onboardingDocFound
    night_supervisor_paths = [ordered]@{
        directory_found = [bool]$nightSupervisorDirFound
        supervisor_script_found = [bool]$nightSupervisorScriptFound
        approval_queue_script_found = [bool]$approvalQueueScriptFound
        telemetry_night_supervisor_found = [bool]$telemetryNightSupervisorFound
    }
    collision_risk = [bool]$collisionRisk
    status = $status
    blockers = @($blockers)
    warnings = @($warnings)
    next_actions = @($nextActions)
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host "AI_OS_OPENAI_CODEX_NIGHT_SUPERVISOR_ONBOARDING"
    Write-Host "MODE=$Mode"
    Write-Host "STATUS=$status"
    Write-Host "REPO_ROOT=$repoRootResolved"
    Write-Host "CURRENT_PATH=$currentPath"
    Write-Host "BRANCH=$branch"
    Write-Host "STAGED_INDEX_CLEAN=$stagedIndexClean"
    Write-Host "OPENAI_CLI_FOUND=$($null -ne $openAiCommand)"
    Write-Host "CODEX_CLI_FOUND=$($null -ne $codexCommand)"
    Write-Host "AGENTS_MD_FOUND=$agentsFound"
    Write-Host "README_FOUND=$readmeFound"
    Write-Host "ONBOARDING_DOC_FOUND=$onboardingDocFound"
    Write-Host "NIGHT_SUPERVISOR_DIR_FOUND=$nightSupervisorDirFound"
    Write-Host "NIGHT_SUPERVISOR_SCRIPT_FOUND=$nightSupervisorScriptFound"
    Write-Host "APPROVAL_QUEUE_SCRIPT_FOUND=$approvalQueueScriptFound"
    Write-Host "TELEMETRY_NIGHT_SUPERVISOR_FOUND=$telemetryNightSupervisorFound"
    Write-Host "COLLISION_RISK=$collisionRisk"

    if ($blockers.Count -gt 0) {
        Write-Host "BLOCKERS:"
        foreach ($item in $blockers) {
            Write-Host "- $item"
        }
    } else {
        Write-Host "BLOCKERS: none"
    }

    if ($warnings.Count -gt 0) {
        Write-Host "WARNINGS:"
        foreach ($item in $warnings) {
            Write-Host "- $item"
        }
    } else {
        Write-Host "WARNINGS: none"
    }

    Write-Host "NEXT_ACTIONS:"
    foreach ($item in $nextActions) {
        Write-Host "- $item"
    }
}

if ($status -eq "BLOCKED") {
    exit 1
}

exit 0
