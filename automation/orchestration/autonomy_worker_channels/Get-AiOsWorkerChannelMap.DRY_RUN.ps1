param(
    [string]$OutputPath = "Reports/autonomy_worker_channels/channel_map.json"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Get-AiOsRepoRoot {
    $repoRoot = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoRoot)) {
        throw "REVIEW_REQUIRED: Unable to resolve repository root."
    }
    return $repoRoot.Trim()
}

function Resolve-AiOsPath {
    param([string]$PathHint, [string]$RepoRoot)
    if ([string]::IsNullOrWhiteSpace($PathHint)) {
        return [string]::Empty
    }
    if ([System.IO.Path]::IsPathRooted($PathHint)) {
        return [System.IO.Path]::GetFullPath($PathHint)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $PathHint))
}

function Write-TextAtomic {
    param([string]$Path, [string]$Text)
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $tmp = Join-Path $parent ([guid]::NewGuid().ToString("N") + ".tmp")
    [System.IO.File]::WriteAllText($tmp, $Text, [System.Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Force
    }
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

try {
    $repoRoot = Get-AiOsRepoRoot
    $outputPath = Resolve-AiOsPath -PathHint $OutputPath -RepoRoot $repoRoot

    $channels = @(
        [ordered]@{
            name = "Codex CLI local"
            role = "execution"
            command = 'codex run --path . --file automation/orchestration/autonomy_control_plane/Invoke-AiOsAutonomyControlPlane.DRY_RUN.ps1'
            boundary = "workspace executor"
            safety = @("dry_run", "local_read", "local_write_in_allowed_paths")
            blocked_by = @()
            requires_authorization = $false
            supports = @("control_plane", "packet_runner", "autonomy_next_action")
        },
        [ordered]@{
            name = "Codex App worktree"
            role = "execution"
            command = 'codex run --path . --goal "handoff worktree for autonomy lane"'
            boundary = "isolated worktree"
            safety = @("no_merge", "no_force_push", "no_apply", "no_secret_reads")
            blocked_by = @("shared_lock")
            requires_authorization = $false
            supports = @("paper_lab", "autonomy_loop")
        },
        [ordered]@{
            name = "Codex Web/cloud"
            role = "connector"
            command = "codex cloud sync --scope autonomy --dry-run"
            boundary = "remote_orchestrator"
            safety = @("readonly", "no_local_secret")
            blocked_by = @("api_key_missing")
            requires_authorization = $false
            supports = @("pr_workflow", "status_reports")
        },
        [ordered]@{
            name = "ChatGPT desktop/mobile supervisor"
            role = "supervisor"
            command = 'echo "Supervisor review required for protected action"'
            boundary = "human_guidance"
            safety = @("no_code_execution", "human_only")
            blocked_by = @("approval_missing")
            requires_authorization = $false
            supports = @("REQUEST_APPROVAL", "ESCALATE_SOS")
        },
        [ordered]@{
            name = "OpenAI CLI optional"
            role = "optional_tool"
            command = "openai api --help"
            boundary = "local_optional"
            safety = @("graceful_if_unconfigured", "no_state_change")
            blocked_by = @("api_key_missing")
            requires_authorization = $false
            supports = @("summaries", "assisted_checking")
        },
        [ordered]@{
            name = "GitHub PR checks"
            role = "verification"
            command = "gh pr checks"
            boundary = "remote_ci"
            safety = @("no_branch_mutation", "readonly")
            blocked_by = @("network_unavailable")
            requires_authorization = $false
            supports = @("OPEN_PR", "validation_status")
        },
        [ordered]@{
            name = "AI_OS internal router"
            role = "coordinator"
            command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/autonomy_router/Get-AiOsAutonomyNextAction.DRY_RUN.ps1"
            boundary = "internal"
            safety = @("dry_run", "policy_guardrails")
            blocked_by = @()
            requires_authorization = $false
            supports = @("RUN_CODEX_WITH_PACKET", "FIX_VALIDATION", "OPEN_PR", "REQUEST_APPROVAL", "ESCALATE_SOS", "BLOCKED")
        }
    )

    $payload = [ordered]@{
        schema_version = "AIOS-AUTONOMY-WORKER-CHANNEL-MAP-V1"
        created_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        repo_root = $repoRoot
        channels = $channels
    }

    Write-TextAtomic -Path $outputPath -Text ($payload | ConvertTo-Json -Depth 20)
    Write-Output ($payload | ConvertTo-Json -Depth 20)
    exit 0
} catch {
    Write-Error "REVIEW_REQUIRED: $($_.Exception.Message)"
    exit 1
}
