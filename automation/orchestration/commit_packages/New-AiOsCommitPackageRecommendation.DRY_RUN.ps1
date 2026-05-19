param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-GitText {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $ErrorActionPreference = $previousErrorActionPreference

    return @($output | ForEach-Object { [string]$_ })
}

function ConvertTo-RepoPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $repoPath = $Path.Replace("\", "/").Trim()
    while ($repoPath.StartsWith("./")) {
        $repoPath = $repoPath.Substring(2)
    }
    return $repoPath
}

function Test-PathStartsWith {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Prefix
    )

    $normalizedPath = ConvertTo-RepoPath -Path $Path
    $normalizedPrefix = (ConvertTo-RepoPath -Path $Prefix).TrimEnd("/")

    return ($normalizedPath -eq $normalizedPrefix -or $normalizedPath.StartsWith("$normalizedPrefix/"))
}

function Expand-StatusPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $repoPath = ConvertTo-RepoPath -Path $Path
    if ($repoPath.EndsWith("/") -and (Test-Path -LiteralPath $repoPath -PathType Container)) {
        return @(Get-ChildItem -LiteralPath $repoPath -Recurse -File | ForEach-Object {
            ConvertTo-RepoPath -Path (Resolve-Path -LiteralPath $_.FullName -Relative)
        })
    }

    return @($repoPath)
}

function Get-WorkerLaneFromBranch {
    param([Parameter(Mandatory = $true)][string]$Branch)

    switch -Regex ($Branch) {
        "^codex/worker-0?1$" { return "CODEX_01" }
        "^codex/worker-0?2$" { return "CODEX_02" }
        "^claude/worker-0?1$" { return "CLAUDE_01" }
        "^(main|master|release/.+)$" { return "MAIN_CONTROL" }
        default { return "UNKNOWN" }
    }
}

function Get-CommitMessageSuggestion {
    param([Parameter(Mandatory = $true)][object[]]$RecommendedFiles)

    $paths = @($RecommendedFiles | ForEach-Object { $_.path })
    $scopes = @($paths | ForEach-Object {
        $parts = $_ -split "/"
        if ($parts.Count -ge 3) {
            "$($parts[0])/$($parts[1])/$($parts[2])"
        } else {
            $_
        }
    } | Sort-Object -Unique)

    if ($paths.Count -eq 0) {
        return "No commit package recommended"
    }

    if ($scopes.Count -gt 1) {
        return "Add AI_OS orchestration DRY_RUN scaffolds"
    }

    if (@($paths | Where-Object { Test-PathStartsWith -Path $_ -Prefix "automation/orchestration/worker_lanes/" }).Count -gt 0) {
        return "Add worker lane status DRY_RUN scaffold"
    }

    if (@($paths | Where-Object { Test-PathStartsWith -Path $_ -Prefix "automation/orchestration/adapters/" }).Count -gt 0) {
        return "Add packet normalization adapter DRY_RUN scaffold"
    }

    if (@($paths | Where-Object { Test-PathStartsWith -Path $_ -Prefix "automation/orchestration/locks/" }).Count -gt 0) {
        return "Add file lock registry DRY_RUN scaffold"
    }

    if (@($paths | Where-Object { Test-PathStartsWith -Path $_ -Prefix "automation/orchestration/commit_packages/" }).Count -gt 0) {
        return "Add commit package recommendation DRY_RUN scaffold"
    }

    return "Add AI_OS orchestration DRY_RUN scaffold"
}

$protectedPaths = @(
    ".codex_backups/",
    ".git/",
    "approval_runner/",
    "apps/dashboard/",
    "apps/dashboard/assets/",
    "broker/",
    "compliance/",
    "live_trading/",
    "oanda/",
    "schemas/",
    "secrets/",
    "webhooks/",
    ".env"
)

$protectedRootFiles = @(
    "README.md",
    "RISK_POLICY.md",
    "SOURCE_LOG.md",
    "ERROR_LOG.md",
    "HALLUCINATION_LOG.md",
    "AAR.md",
    "DAILY_REPORT.md",
    "ARCHITECTURE.md",
    "DEPLOYMENT.md",
    "WHITEPAPER.md",
    "AGENTS.md"
)

$branchOutputLines = @(Invoke-GitText -Arguments @("branch", "--show-current"))
$branchWarnings = @($branchOutputLines | Where-Object { $_ -match "^warning:" })
$branchLines = @($branchOutputLines | Where-Object { $_ -notmatch "^warning:" })
$currentBranch = if ($branchLines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($branchLines[0])) { $branchLines[0] } else { "UNKNOWN" }

$statusOutputLines = @(Invoke-GitText -Arguments @("status", "--short"))
$statusWarnings = @($statusOutputLines | Where-Object { $_ -match "^warning:" })
$statusLines = @($statusOutputLines | Where-Object { $_ -notmatch "^warning:" -and -not [string]::IsNullOrWhiteSpace($_) })
$gitWarnings = @($branchWarnings + $statusWarnings | Sort-Object -Unique)

$changedFiles = @()
$newFiles = @()
$recommendedFiles = @()
$excludedFiles = @()
$risks = @()
$generatedOrExampleFiles = @()

foreach ($line in $statusLines) {
    $statusCode = $line.Substring(0, 2)
    $rawPath = ConvertTo-RepoPath -Path ($line.Substring(3))
    $isNew = $statusCode -eq "??"
    $expandedPaths = @(Expand-StatusPath -Path $rawPath)

    foreach ($path in $expandedPaths) {
        if ($isNew) {
            $newFiles += $path
        } else {
            $changedFiles += $path
        }

        $pathRisks = @()
        foreach ($protectedPath in $protectedPaths) {
            if (Test-PathStartsWith -Path $path -Prefix $protectedPath) {
                $pathRisks += "Protected or blocked path: $protectedPath"
            }
        }

        if ($protectedRootFiles -contains $path) {
            $pathRisks += "Protected root governance file."
        }

        if ($path -match "(\.example\.|README\.md$|\.DRY_RUN\.ps1$)") {
            $generatedOrExampleFiles += $path
        }

        if ($pathRisks.Count -gt 0) {
            foreach ($risk in $pathRisks) {
                $risks += [pscustomobject]@{
                    path = $path
                    risk = $risk
                }
            }

            $excludedFiles += [pscustomobject]@{
                path = $path
                reason = ($pathRisks -join "; ")
            }
        } else {
            $recommendedFiles += [pscustomobject]@{
                path = $path
                reason = if ($isNew) { "New non-protected file from current worktree." } else { "Changed non-protected file from current worktree." }
                git_add_command = "git add -- $path"
            }
        }
    }
}

$workerLane = Get-WorkerLaneFromBranch -Branch $currentBranch
$laneOwnershipStatus = "WARN"
$laneOwnershipReason = "Branch does not map to a known worker lane."
if ($workerLane -ne "UNKNOWN") {
    $laneOwnershipStatus = "PASS"
    $laneOwnershipReason = "Current branch maps to $workerLane."
}

if ($recommendedFiles.Count -eq 0) {
    $risks += [pscustomobject]@{
        path = "WORKTREE"
        risk = "No files are recommended for selective staging."
    }
}

if ($excludedFiles.Count -gt 0) {
    $risks += [pscustomobject]@{
        path = "WORKTREE"
        risk = "Some files were excluded because they match protected or blocked paths."
    }
}

$recommendedTopScopes = @($recommendedFiles | ForEach-Object {
    $parts = $_.path -split "/"
    if ($parts.Count -ge 3) {
        "$($parts[0])/$($parts[1])/$($parts[2])"
    } else {
        $_.path
    }
} | Sort-Object -Unique)

if ($recommendedTopScopes.Count -gt 1) {
    $risks += [pscustomobject]@{
        path = "WORKTREE"
        risk = "Recommended files span multiple work areas: $($recommendedTopScopes -join ', '). Consider separate selective commits."
    }
}

$commitMessage = Get-CommitMessageSuggestion -RecommendedFiles $recommendedFiles
$gitStatus = if ($statusLines.Count -eq 0) { "clean" } else { "dirty" }

$result = [pscustomobject]@{
    task = "Recommend AI_OS selective commit package"
    mode = "DRY_RUN"
    current_branch = $currentBranch
    git_status = $gitStatus
    worker_lane = [pscustomobject]@{
        lane_id = $workerLane
        ownership_status = $laneOwnershipStatus
        reason = $laneOwnershipReason
    }
    summary = [pscustomobject]@{
        changed_file_count = $changedFiles.Count
        new_file_count = $newFiles.Count
        recommended_file_count = $recommendedFiles.Count
        excluded_file_count = $excludedFiles.Count
        risk_count = $risks.Count
        generated_or_example_file_count = @($generatedOrExampleFiles | Sort-Object -Unique).Count
    }
    changed_files = $changedFiles
    new_files = $newFiles
    generated_or_example_files = @($generatedOrExampleFiles | Sort-Object -Unique)
    recommended_files = $recommendedFiles
    recommended_git_add_commands = @($recommendedFiles | ForEach-Object { $_.git_add_command })
    excluded_files = $excludedFiles
    risks = $risks
    git_warnings = $gitWarnings
    commit_message_suggestion = $commitMessage
    safety = [pscustomobject]@{
        git_add_dot_used = "NO"
        files_staged = 0
        commits_performed = 0
        pushes_performed = 0
        dispatcher_edits = "NO"
        runtime_integration = "NO"
        dashboard_edits = "NO"
    }
    validator_friendly = $true
    next_safe_action = "Review recommended git add commands. Stage only selected files after explicit approval; never use git add ."
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Commit Package Recommendation"
Write-Host "Mode: DRY_RUN"
Write-Host "Current branch: $currentBranch"
Write-Host "Worker lane: $workerLane ($laneOwnershipStatus)"
Write-Host "Git status: $gitStatus"
Write-Host ""
Write-Host "Summary:"
Write-Host "  Changed files: $($result.summary.changed_file_count)"
Write-Host "  New files: $($result.summary.new_file_count)"
Write-Host "  Recommended files: $($result.summary.recommended_file_count)"
Write-Host "  Excluded files: $($result.summary.excluded_file_count)"
Write-Host "  Risks: $($result.summary.risk_count)"
Write-Host ""

Write-Host "Recommended git add commands:"
if ($result.recommended_git_add_commands.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($command in $result.recommended_git_add_commands) {
        Write-Host "  $command"
    }
}
Write-Host ""

Write-Host "Excluded files:"
if ($excludedFiles.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($file in $excludedFiles) {
        Write-Host "  - $($file.path)"
        Write-Host "    Reason: $($file.reason)"
    }
}
Write-Host ""

Write-Host "Risks:"
if ($risks.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($risk in $risks) {
        Write-Host "  - $($risk.path): $($risk.risk)"
    }
}
Write-Host ""

Write-Host "Generated/example files:"
if ($generatedOrExampleFiles.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($file in ($generatedOrExampleFiles | Sort-Object -Unique)) {
        Write-Host "  - $file"
    }
}
Write-Host ""

Write-Host "Suggested commit message:"
Write-Host "  $commitMessage"
Write-Host ""

Write-Host "Git warnings:"
if ($gitWarnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($warning in $gitWarnings) {
        Write-Host "  - $warning"
    }
}
Write-Host ""

Write-Host "Validator note: no files were staged. No git add, commit, or push was run."
Write-Host "Next safe action: $($result.next_safe_action)"
