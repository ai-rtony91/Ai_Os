Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$supervisorRulesPath = Join-Path $repoRoot "automation\orchestration\supervisor\aios_supervision_rules.example.json"

function Invoke-Capture {
    param([Parameter(Mandatory = $true)][scriptblock]$Command)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & $Command 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    [pscustomobject]@{
        Output = @($output)
        ExitCode = $exitCode
    }
}

function Invoke-GhCount {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        return [pscustomobject]@{
            Available = $false
            Count = $null
            Reason = "gh CLI not found"
        }
    }

    $result = Invoke-Capture -Command { gh @Arguments }
    if ($result.ExitCode -ne 0) {
        $reason = if ($result.Output.Count -gt 0) {
            ($result.Output | Out-String).Trim().Split([Environment]::NewLine)[0]
        } else {
            "gh command failed"
        }

        return [pscustomobject]@{
            Available = $false
            Count = $null
            Reason = $reason
        }
    }

    $count = 0
    if ($result.Output.Count -gt 0) {
        [int]::TryParse(($result.Output | Select-Object -First 1), [ref]$count) | Out-Null
    }

    [pscustomobject]@{
        Available = $true
        Count = $count
        Reason = $null
    }
}

function Get-FirstTextLine {
    param([object[]]$Lines)

    if ($Lines.Count -eq 0) {
        return $null
    }

    $text = ($Lines | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }

    $text.Split([Environment]::NewLine)[0]
}

function Test-BlockedPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object[]]$Patterns
    )

    $normalized = $Path -replace "\\", "/"
    foreach ($pattern in $Patterns) {
        $patternText = [string]$pattern
        if ($normalized -ieq $patternText -or $normalized -like "*$patternText*") {
            return $true
        }
    }
    return $false
}

if (-not (Test-Path -LiteralPath $repoRoot -PathType Container)) {
    throw "AI_OS repo path not found: $repoRoot"
}

Set-Location -LiteralPath $repoRoot

$rules = if (Test-Path -LiteralPath $supervisorRulesPath -PathType Leaf) {
    Get-Content -Raw -LiteralPath $supervisorRulesPath | ConvertFrom-Json
} else {
    [pscustomobject]@{
        blocked_path_patterns = @()
        blocked_actions = @(
            "commit",
            "push",
            "merge",
            "create branch",
            "create issue",
            "create pull request"
        )
    }
}

$branch = (git branch --show-current)
$statusLines = @(git status --short --untracked-files=all)
$latestCommit = (git log --oneline -1)
$untrackedLines = @($statusLines | Where-Object { $_ -match '^\?\?' })
$changedFiles = @(
    $statusLines |
        ForEach-Object { if ($_.Length -gt 3) { $_.Substring(3).Trim() } } |
        Where-Object { $_ }
)
$blockedFiles = @($changedFiles | Where-Object { Test-BlockedPath -Path $_ -Patterns @($rules.blocked_path_patterns) })
$jsonFiles = @($changedFiles | Where-Object { [System.IO.Path]::GetExtension($_) -ieq ".json" })
$ps1Files = @($changedFiles | Where-Object { [System.IO.Path]::GetExtension($_) -ieq ".ps1" })
$repoClean = $statusLines.Count -eq 0
$validationNeeded = -not $repoClean

$authCheck = if (Get-Command gh -ErrorAction SilentlyContinue) {
    Invoke-Capture -Command { gh auth status }
} else {
    [pscustomobject]@{
        Output = @("gh CLI not found")
        ExitCode = 127
    }
}
$issues = Invoke-GhCount -Arguments @("issue", "list", "--state", "open", "--limit", "100", "--json", "number", "--jq", "length")
$prs = Invoke-GhCount -Arguments @("pr", "list", "--state", "open", "--limit", "100", "--json", "number", "--jq", "length")
$branchPrs = Invoke-GhCount -Arguments @("pr", "list", "--head", $branch, "--state", "open", "--limit", "20", "--json", "number", "--jq", "length")
$ghAvailable = ($authCheck.ExitCode -eq 0) -and $issues.Available -and $prs.Available -and $branchPrs.Available

$risk = "SAFE"
$reason = "No blocking local condition is visible."
if ($blockedFiles.Count -gt 0) {
    $risk = "BLOCKED"
    $reason = "Blocked or protected path changed."
} elseif ($validationNeeded) {
    $risk = "WARNING"
    $reason = "Validation is needed before commit packaging."
} elseif (-not $ghAvailable) {
    $risk = "WATCH"
    $reason = "GitHub checks are unavailable. Local-only mode is active."
}

$recommendedLane = "COMMAND DECK"
$nextSafeAction = "Use Ai_Os COMMAND DECK to choose the next approved phase or PR action."
if ($risk -eq "BLOCKED") {
    $recommendedLane = "COMMAND DECK"
    $nextSafeAction = "Use Ai_Os COMMAND DECK and stop for operator review before any commit, push, merge, or edit."
} elseif ($validationNeeded) {
    $recommendedLane = "VALIDATION DECK"
    $nextSafeAction = "Use Ai_Os VALIDATION DECK and run git diff --check plus file-specific parse checks."
} elseif (-not $ghAvailable -or (($issues.Count -ne $null) -and $issues.Count -gt 0) -or (($prs.Count -ne $null) -and $prs.Count -gt 0)) {
    $recommendedLane = "COMMAND DECK"
    $nextSafeAction = "Use Ai_Os COMMAND DECK to review GitHub issue, PR, approval, or merge state."
} else {
    $recommendedLane = "BUILD ENGINE"
    $nextSafeAction = "Use Ai_Os BUILD ENGINE only after the next APPLY task is explicitly approved."
}

$knownQueueFiles = @(
    "automation/orchestration/packet_queue.example.json",
    "automation/orchestration/packet_queue_ledger.v1.example.json",
    "automation/orchestration/approval_inbox.v1.example.json",
    "automation/orchestration/queue_health_supervisor.v1.example.json"
)
$knownRecoveryFiles = @(
    "automation/orchestration/recovery_bootstrap_supervisor.v1.example.json",
    "automation/orchestration/session_continuity.v1.example.json"
)

$state = [pscustomobject]@{
    system = "AI_OS"
    stack = "Mission Control"
    mode = "READ_ONLY"
    risk = $risk
    recommended_lane = $recommendedLane
    next_safe_action = $nextSafeAction
    reason = $reason
    repo_state = [pscustomobject]@{
        repo_root = $repoRoot
        branch = $branch
        clean = $repoClean
        changed_files = $changedFiles.Count
        untracked_files = $untrackedLines.Count
        latest_commit = $latestCommit
        status_lines = @($statusLines)
    }
    github_state = [pscustomobject]@{
        gh_available = $ghAvailable
        local_only_fallback = -not $ghAvailable
        open_issues = $issues.Count
        open_prs = $prs.Count
        current_branch_prs = $branchPrs.Count
        unavailable_reason = if ($ghAvailable) { $null } else { $reasonText = Get-FirstTextLine -Lines @($authCheck.Output); if ($reasonText) { $reasonText } else { "GitHub checks unavailable" } }
    }
    validation_state = [pscustomobject]@{
        git_diff_needed = -not $repoClean
        json_validation_needed = $jsonFiles.Count -gt 0
        powershell_validation_needed = $ps1Files.Count -gt 0
        repo_clean_check_needed = $true
    }
    stale_state = [pscustomobject]@{
        stale_branch_review_needed = $false
        issue_without_pr_review_needed = $false
        pr_without_merge_review_needed = (($prs.Count -ne $null) -and $prs.Count -gt 0)
    }
    approval_state = [pscustomobject]@{
        approval_needed = (($prs.Count -ne $null) -and $prs.Count -gt 0)
        validation_needed = $validationNeeded
        merge_needed = $false
    }
    routing_state = [pscustomobject]@{
        command_deck_needed = $recommendedLane -eq "COMMAND DECK"
        build_engine_needed = $recommendedLane -eq "BUILD ENGINE"
        validation_deck_needed = $recommendedLane -eq "VALIDATION DECK"
    }
    queue_awareness = [pscustomobject]@{
        known_queue_files = @($knownQueueFiles)
        visible_queue_files = @($knownQueueFiles | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf })
    }
    recovery_awareness = [pscustomobject]@{
        known_recovery_files = @($knownRecoveryFiles)
        visible_recovery_files = @($knownRecoveryFiles | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf })
    }
    blocked_state = [pscustomobject]@{
        blocked = $blockedFiles.Count -gt 0
        blocked_files = @($blockedFiles)
        blocked_actions = @($rules.blocked_actions)
    }
    telemetry_ready = $true
    dashboard_ready = $true
}

$state | ConvertTo-Json -Depth 8
