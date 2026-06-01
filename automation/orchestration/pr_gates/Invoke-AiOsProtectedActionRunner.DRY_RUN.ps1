<#
.SYNOPSIS
Classifies exact-scope AI_OS protected actions without executing them.

.DESCRIPTION
This runner is DRY_RUN evidence only. It inspects supplied scope, approval,
validator, PR, and Git-state evidence and emits one JSON gate decision. It does
not edit files, stage, commit, push, create PRs, watch checks, merge, switch
branches, reset, clean, delete branches, run schedulers, or touch runtime,
dashboard, trading, broker, OANDA, secret, or API-key paths.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $Action,

    [Parameter(Mandatory = $false)]
    [string] $ApprovalMarker = "",

    [Parameter(Mandatory = $false)]
    [string] $Lane = "",

    [Parameter(Mandatory = $false)]
    [string] $Branch = "",

    [Parameter(Mandatory = $false)]
    [string] $Remote = "",

    [Parameter(Mandatory = $false)]
    [string] $TargetBranch = "",

    [Parameter(Mandatory = $false)]
    [string] $BaseBranch = "",

    [Parameter(Mandatory = $false)]
    [string] $HeadBranch = "",

    [Parameter(Mandatory = $false)]
    [int] $PrNumber = 0,

    [Parameter(Mandatory = $false)]
    [string] $CommitMessage = "",

    [Parameter(Mandatory = $false)]
    [string[]] $ApprovedFiles = @(),

    [Parameter(Mandatory = $false)]
    [string[]] $ChangedFiles = @(),

    [Parameter(Mandatory = $false)]
    [string[]] $CachedDiffFiles = @(),

    [Parameter(Mandatory = $false)]
    [string] $ValidatorStatus = "",

    [Parameter(Mandatory = $false)]
    [string] $MergeabilityStatus = "",

    [Parameter(Mandatory = $false)]
    [string] $ChecksStatus = "",

    [Parameter(Mandatory = $false)]
    [string] $RepoStatus = "",

    [Parameter(Mandatory = $false)]
    [string] $ExpectedHeadSha = "",

    [Parameter(Mandatory = $false)]
    [string] $PushTarget = "",

    [Parameter(Mandatory = $false)]
    [string] $StopCondition = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-AiOsNormalizedAction {
    param([string] $Value)
    return (($Value -replace "-", "_") -replace "\s+", "_").Trim().ToLowerInvariant()
}

function ConvertTo-AiOsNormalizedToken {
    param([string] $Value)
    return (($Value -replace "-", "_") -replace "\s+", "_").Trim().ToUpperInvariant()
}

function ConvertTo-AiOsPath {
    param([string] $Value)
    return (($Value -replace "\\", "/").Trim().Trim("/"))
}

function Test-AiOsPathInside {
    param([string] $Path, [string[]] $Allowed)
    $normalizedPath = ConvertTo-AiOsPath $Path
    foreach ($item in $Allowed) {
        $normalizedAllowed = ConvertTo-AiOsPath $item
        if ([string]::IsNullOrWhiteSpace($normalizedAllowed)) { continue }
        if ($normalizedPath -eq $normalizedAllowed -or $normalizedPath.StartsWith("$normalizedAllowed/")) {
            return $true
        }
    }
    return $false
}

function Add-AiOsFinding {
    param([System.Collections.Generic.List[string]] $List, [string] $Message)
    if (-not [string]::IsNullOrWhiteSpace($Message)) {
        $List.Add($Message) | Out-Null
    }
}

function New-AiOsProtectedActionDecision {
    param(
        [string] $Action,
        [string] $ApprovalMarker,
        [string] $Lane,
        [string] $Branch,
        [string] $Remote,
        [string] $TargetBranch,
        [string] $BaseBranch,
        [string] $HeadBranch,
        [int] $PrNumber,
        [string] $CommitMessage,
        [string[]] $ApprovedFiles,
        [string[]] $ChangedFiles,
        [string[]] $CachedDiffFiles,
        [string] $ValidatorStatus,
        [string] $MergeabilityStatus,
        [string] $ChecksStatus,
        [string] $RepoStatus,
        [string] $ExpectedHeadSha,
        [string] $PushTarget,
        [string] $StopCondition
    )

    $actionKey = ConvertTo-AiOsNormalizedAction $Action
    $marker = ConvertTo-AiOsNormalizedToken $ApprovalMarker
    $validator = ConvertTo-AiOsNormalizedToken $ValidatorStatus
    $checks = ConvertTo-AiOsNormalizedToken $ChecksStatus
    $mergeability = ConvertTo-AiOsNormalizedToken $MergeabilityStatus
    $repo = ConvertTo-AiOsNormalizedToken $RepoStatus

    $requiredMarkers = @{
        stage       = "APPROVE_STAGE_EXACT_FILES"
        commit      = "APPROVE_COMMIT"
        push        = "APPROVE_PUSH"
        pr_create   = "APPROVE_PR_CREATE"
        check_watch = "APPROVE_CHECK_WATCH"
        merge       = "APPROVE_MERGE"
        sync_main   = "APPROVE_SYNC_MAIN"
    }
    $safeStates = @{
        stage       = "SAFE_TO_STAGE"
        commit      = "SAFE_TO_COMMIT"
        push        = "SAFE_TO_PUSH"
        pr_create   = "SAFE_TO_PR_CREATE"
        check_watch = "SAFE_TO_CHECK_WATCH"
        merge       = "SAFE_TO_MERGE"
        sync_main   = "SAFE_TO_SYNC_MAIN"
    }

    $blockers = [System.Collections.Generic.List[string]]::new()
    $warnings = [System.Collections.Generic.List[string]]::new()

    $dangerText = "$Action $PushTarget $StopCondition $($ApprovedFiles -join ' ') $($ChangedFiles -join ' ') $($CachedDiffFiles -join ' ')"
    if ($dangerText -match "(?i)\bgit\s+add\s+\.|\bgit\s+add\s+-A|\bgit\s+add\s+--all") {
        Add-AiOsFinding $blockers "Broad staging command is blocked: git add ., git add -A, and git add --all are forbidden."
    }
    if ($dangerText -match "(?i)\b--force\b|\s-f\s|reset\s+--hard|\bgit\s+clean\b|branch\s+-D|push\s+origin\s+--delete") {
        Add-AiOsFinding $blockers "Force, reset, clean, or branch deletion behavior is blocked by this runner."
    }

    if (-not $requiredMarkers.ContainsKey($actionKey)) {
        Add-AiOsFinding $blockers "Unknown protected action: $Action."
    }
    else {
        $requiredMarker = $requiredMarkers[$actionKey]
        if ($marker -ne $requiredMarker) {
            Add-AiOsFinding $blockers "Missing or mismatched approval marker. Required marker for $actionKey is $requiredMarker."
        }
    }

    if ([string]::IsNullOrWhiteSpace($Lane)) {
        Add-AiOsFinding $warnings "Lane was not supplied."
    }
    if ([string]::IsNullOrWhiteSpace($Branch)) {
        Add-AiOsFinding $blockers "Branch is required for protected action classification."
    }

    if ($validator -in @("FAIL", "FAILED", "BLOCKED", "ERROR")) {
        Add-AiOsFinding $blockers "Validator status blocks protected action: $ValidatorStatus."
    }
    elseif ($validator -in @("", "UNKNOWN", "NOT_RUN", "REVIEW", "WARN", "WARNING")) {
        Add-AiOsFinding $warnings "Validator evidence is incomplete: $ValidatorStatus."
    }

    $normalizedApproved = @($ApprovedFiles | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { ConvertTo-AiOsPath $_ })
    $normalizedChanged = @($ChangedFiles | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { ConvertTo-AiOsPath $_ })
    $normalizedCached = @($CachedDiffFiles | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { ConvertTo-AiOsPath $_ })

    foreach ($path in @($normalizedApproved + $normalizedChanged + $normalizedCached)) {
        if ($path -eq "." -or $path -eq "*" -or $path -match "(?i)^\.codex_backups/|^node_modules/|^\.venv/|/__pycache__/|^dist/|^build/|^apps/dashboard/|\.env($|/)|secret|token|credential|privatekey|broker|oanda|live[_ -]?trading|real[_ -]?order|webhook") {
            Add-AiOsFinding $blockers "Blocked or unsafe path/scope detected: $path."
        }
    }

    switch ($actionKey) {
        "stage" {
            if ($normalizedApproved.Count -eq 0) { Add-AiOsFinding $blockers "Stage requires exact approved files." }
            if ($normalizedChanged.Count -eq 0) { Add-AiOsFinding $blockers "Stage requires changed files evidence." }
            foreach ($path in $normalizedChanged) {
                if (-not (Test-AiOsPathInside -Path $path -Allowed $normalizedApproved)) {
                    Add-AiOsFinding $blockers "Changed file is not approved for staging: $path."
                }
            }
        }
        "commit" {
            if ([string]::IsNullOrWhiteSpace($CommitMessage)) { Add-AiOsFinding $blockers "Commit requires an exact commit message." }
            if ($normalizedApproved.Count -eq 0) { Add-AiOsFinding $blockers "Commit requires exact approved files." }
            if ($normalizedCached.Count -eq 0) { Add-AiOsFinding $blockers "Commit requires cached diff files." }
            foreach ($path in $normalizedCached) {
                if (-not (Test-AiOsPathInside -Path $path -Allowed $normalizedApproved)) {
                    Add-AiOsFinding $blockers "Cached diff file is not approved: $path."
                }
            }
            foreach ($path in $normalizedApproved) {
                if ($normalizedCached -notcontains $path) {
                    Add-AiOsFinding $blockers "Approved file is missing from cached diff: $path."
                }
            }
        }
        "push" {
            if ([string]::IsNullOrWhiteSpace($Remote)) { Add-AiOsFinding $blockers "Push requires an exact remote." }
            if ([string]::IsNullOrWhiteSpace($PushTarget)) { Add-AiOsFinding $blockers "Push requires an exact push target." }
            if ([string]::IsNullOrWhiteSpace($ExpectedHeadSha)) { Add-AiOsFinding $blockers "Push requires expected HEAD SHA evidence." }
            if ($PushTarget -match "(?i)^origin/main$|^main$" -or ($Remote -eq "origin" -and $TargetBranch -eq "main")) {
                Add-AiOsFinding $blockers "Direct main push is blocked for protected work; use PR lane."
            }
        }
        "pr_create" {
            if ([string]::IsNullOrWhiteSpace($BaseBranch)) { Add-AiOsFinding $blockers "PR creation requires base branch." }
            if ([string]::IsNullOrWhiteSpace($HeadBranch)) { Add-AiOsFinding $blockers "PR creation requires head branch." }
            if ($HeadBranch -eq $BaseBranch) { Add-AiOsFinding $blockers "PR creation requires different base and head branches." }
            if ($BaseBranch -ne "main") { Add-AiOsFinding $warnings "PR base branch is not main." }
        }
        "check_watch" {
            if ($PrNumber -le 0) { Add-AiOsFinding $blockers "Check watch requires PR number." }
        }
        "merge" {
            if ($PrNumber -le 0) { Add-AiOsFinding $blockers "Merge requires PR number." }
            if ($mergeability -notin @("CLEAN", "MERGEABLE", "READY")) { Add-AiOsFinding $blockers "Mergeability is not clean: $MergeabilityStatus." }
            if ($checks -notin @("PASS", "PASSED", "SUCCESS", "COMPLETED_SUCCESS")) { Add-AiOsFinding $blockers "Checks must be passing before merge: $ChecksStatus." }
        }
        "sync_main" {
            if ($Branch -ne "main") { Add-AiOsFinding $blockers "sync_main must run from main after approved branch switch/sync flow." }
            if ($TargetBranch -ne "main") { Add-AiOsFinding $blockers "sync_main target branch must be main." }
            if ($repo -notin @("CLEAN", "SYNCED", "CLEAN_SYNCED")) { Add-AiOsFinding $blockers "sync_main requires clean repo evidence: $RepoStatus." }
        }
    }

    $gateState = "HUMAN_APPROVAL_REQUIRED"
    $reason = "Protected action needs human review before mutation."
    if ($blockers.Count -gt 0) {
        $gateState = "BLOCKED"
        $reason = $blockers[0]
    }
    elseif ($warnings.Count -eq 0 -and $safeStates.ContainsKey($actionKey)) {
        $gateState = $safeStates[$actionKey]
        $reason = "Exact-scope evidence satisfies the DRY_RUN gate for $actionKey. This does not execute or approve the protected action by itself."
    }

    $nextSafeAction = if ($gateState -eq "BLOCKED") {
        "Stop. Resolve blockers and rerun the protected-action runner."
    }
    elseif ($gateState -eq "HUMAN_APPROVAL_REQUIRED") {
        "Stop. Complete missing evidence or request exact current-session Human Owner approval."
    }
    else {
        "Use this JSON as evidence in a separate current-session Human Owner approved protected-action packet."
    }

    [pscustomobject]@{
        schema = "AIOS_PROTECTED_ACTION_RUNNER_RESULT.v1"
        generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        mode = "DRY_RUN"
        action = $actionKey
        gate_state = $gateState
        approval_marker = [pscustomobject]@{
            provided = $ApprovalMarker
            required = if ($requiredMarkers.ContainsKey($actionKey)) { $requiredMarkers[$actionKey] } else { "" }
            matched = if ($requiredMarkers.ContainsKey($actionKey)) { $marker -eq $requiredMarkers[$actionKey] } else { $false }
        }
        lane = $Lane
        branch = $Branch
        targets = [pscustomobject]@{
            remote = $Remote
            target_branch = $TargetBranch
            base_branch = $BaseBranch
            head_branch = $HeadBranch
            pr_number = $PrNumber
            expected_head_sha = $ExpectedHeadSha
            push_target = $PushTarget
            commit_message = $CommitMessage
        }
        approved_files = @($normalizedApproved)
        changed_files = @($normalizedChanged)
        cached_diff_files = @($normalizedCached)
        validator_status = $ValidatorStatus
        checks_status = $ChecksStatus
        mergeability_status = $MergeabilityStatus
        repo_status = $RepoStatus
        blockers = @($blockers)
        warnings = @($warnings)
        reason = $reason
        next_safe_action = $nextSafeAction
        stop_condition = if ([string]::IsNullOrWhiteSpace($StopCondition)) { "Stop after DRY_RUN gate decision. Do not mutate repository state." } else { $StopCondition }
        no_mutation_confirmed = [pscustomobject]@{
            files_edited = 0
            files_staged = 0
            commits_performed = 0
            pushes_performed = 0
            prs_created = 0
            check_watch_started = 0
            merges_performed = 0
            branch_switches = 0
            resets_performed = 0
            cleans_performed = 0
            branch_deletions = 0
            backups_performed = 0
            scheduler_changes = 0
            trading_actions = 0
        }
    }
}

$decision = New-AiOsProtectedActionDecision `
    -Action $Action `
    -ApprovalMarker $ApprovalMarker `
    -Lane $Lane `
    -Branch $Branch `
    -Remote $Remote `
    -TargetBranch $TargetBranch `
    -BaseBranch $BaseBranch `
    -HeadBranch $HeadBranch `
    -PrNumber $PrNumber `
    -CommitMessage $CommitMessage `
    -ApprovedFiles $ApprovedFiles `
    -ChangedFiles $ChangedFiles `
    -CachedDiffFiles $CachedDiffFiles `
    -ValidatorStatus $ValidatorStatus `
    -MergeabilityStatus $MergeabilityStatus `
    -ChecksStatus $ChecksStatus `
    -RepoStatus $RepoStatus `
    -ExpectedHeadSha $ExpectedHeadSha `
    -PushTarget $PushTarget `
    -StopCondition $StopCondition

$json = $decision | ConvertTo-Json -Depth 10
$null = $json | ConvertFrom-Json
Write-Output $json
