<#
.SYNOPSIS
Runs safe DRY_RUN tests for the protected action runner.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$runner = Join-Path $PSScriptRoot "Invoke-AiOsProtectedActionRunner.DRY_RUN.ps1"
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    throw "Runner not found: $runner"
}

function Invoke-RunnerCase {
    param([hashtable] $Arguments)
    $json = & powershell -NoProfile -ExecutionPolicy Bypass -File $runner @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Runner exited with $LASTEXITCODE for action $($Arguments.Action)"
    }
    return ($json | ConvertFrom-Json)
}

function Assert-Gate {
    param(
        [string] $Name,
        [hashtable] $Arguments,
        [string] $ExpectedGate
    )
    $result = Invoke-RunnerCase -Arguments $Arguments
    if ($result.gate_state -ne $ExpectedGate) {
        throw "[$Name] expected $ExpectedGate, got $($result.gate_state): $($result.reason)"
    }
    if ($result.mode -ne "DRY_RUN") {
        throw "[$Name] expected DRY_RUN mode."
    }
    if ($result.no_mutation_confirmed.files_staged -ne 0 -or $result.no_mutation_confirmed.commits_performed -ne 0 -or $result.no_mutation_confirmed.pushes_performed -ne 0 -or $result.no_mutation_confirmed.merges_performed -ne 0) {
        throw "[$Name] mutation counters are not zero."
    }
    return [pscustomobject]@{
        name = $Name
        expected = $ExpectedGate
        actual = $result.gate_state
        passed = $true
    }
}

function Merge-Args {
    param([hashtable] $Base, [hashtable] $Override)
    $merged = @{}
    foreach ($key in $Base.Keys) {
        $merged[$key] = $Base[$key]
    }
    foreach ($key in $Override.Keys) {
        $merged[$key] = $Override[$key]
    }
    return $merged
}

$common = @{
    Lane = "Protected Action Runner Test Lane"
    Branch = "lane/protected-action-runner"
    ValidatorStatus = "PASS"
    RepoStatus = "CLEAN"
    StopCondition = "Test only. No mutation."
}

$cases = @(
    @{
        Name = "SAFE_TO_STAGE"
        Expected = "SAFE_TO_STAGE"
        Args = Merge-Args -Base $common -Override @{
            Action = "stage"
            ApprovalMarker = "APPROVE_STAGE_EXACT_FILES"
            ApprovedFiles = @("docs/workflows/AI_OS_COMMIT_PUSH_GATE.md")
            ChangedFiles = @("docs/workflows/AI_OS_COMMIT_PUSH_GATE.md")
        }
    },
    @{
        Name = "SAFE_TO_COMMIT"
        Expected = "SAFE_TO_COMMIT"
        Args = Merge-Args -Base $common -Override @{
            Action = "commit"
            ApprovalMarker = "APPROVE_COMMIT"
            CommitMessage = "test: protected action runner"
            ApprovedFiles = @("automation/orchestration/pr_gates/Invoke-AiOsProtectedActionRunner.DRY_RUN.ps1")
            CachedDiffFiles = @("automation/orchestration/pr_gates/Invoke-AiOsProtectedActionRunner.DRY_RUN.ps1")
        }
    },
    @{
        Name = "SAFE_TO_PUSH"
        Expected = "SAFE_TO_PUSH"
        Args = Merge-Args -Base $common -Override @{
            Action = "push"
            ApprovalMarker = "APPROVE_PUSH"
            Remote = "origin"
            TargetBranch = "lane/protected-action-runner"
            PushTarget = "origin/lane/protected-action-runner"
            ExpectedHeadSha = "abc123"
        }
    },
    @{
        Name = "SAFE_TO_PR_CREATE"
        Expected = "SAFE_TO_PR_CREATE"
        Args = Merge-Args -Base $common -Override @{
            Action = "pr_create"
            ApprovalMarker = "APPROVE_PR_CREATE"
            BaseBranch = "main"
            HeadBranch = "lane/protected-action-runner"
        }
    },
    @{
        Name = "SAFE_TO_CHECK_WATCH"
        Expected = "SAFE_TO_CHECK_WATCH"
        Args = Merge-Args -Base $common -Override @{
            Action = "check_watch"
            ApprovalMarker = "APPROVE_CHECK_WATCH"
            PrNumber = 343
        }
    },
    @{
        Name = "SAFE_TO_MERGE"
        Expected = "SAFE_TO_MERGE"
        Args = Merge-Args -Base $common -Override @{
            Action = "merge"
            ApprovalMarker = "APPROVE_MERGE"
            PrNumber = 343
            MergeabilityStatus = "CLEAN"
            ChecksStatus = "SUCCESS"
        }
    },
    @{
        Name = "SAFE_TO_SYNC_MAIN"
        Expected = "SAFE_TO_SYNC_MAIN"
        Args = @{
            Action = "sync_main"
            ApprovalMarker = "APPROVE_SYNC_MAIN"
            Lane = "Protected Action Runner Test Lane"
            Branch = "main"
            TargetBranch = "main"
            ValidatorStatus = "PASS"
            RepoStatus = "CLEAN"
            StopCondition = "Test only. No mutation."
        }
    },
    @{
        Name = "HUMAN_APPROVAL_REQUIRED"
        Expected = "HUMAN_APPROVAL_REQUIRED"
        Args = Merge-Args -Base $common -Override @{
            Action = "stage"
            ApprovalMarker = "APPROVE_STAGE_EXACT_FILES"
            ApprovedFiles = @("docs/workflows/AI_OS_COMMIT_PUSH_GATE.md")
            ChangedFiles = @("docs/workflows/AI_OS_COMMIT_PUSH_GATE.md")
            ValidatorStatus = "REVIEW"
        }
    },
    @{
        Name = "BLOCKED_GIT_ADD_DOT"
        Expected = "BLOCKED"
        Args = Merge-Args -Base $common -Override @{
            Action = "git add ."
            ApprovalMarker = "APPROVE_STAGE_EXACT_FILES"
            ApprovedFiles = @(".")
            ChangedFiles = @(".")
        }
    },
    @{
        Name = "BLOCKED_CACHED_DIFF_MISMATCH"
        Expected = "BLOCKED"
        Args = Merge-Args -Base $common -Override @{
            Action = "commit"
            ApprovalMarker = "APPROVE_COMMIT"
            CommitMessage = "test: mismatch"
            ApprovedFiles = @("docs/workflows/AI_OS_COMMIT_PUSH_GATE.md")
            CachedDiffFiles = @("automation/orchestration/pr_gates/Invoke-AiOsProtectedActionRunner.DRY_RUN.ps1")
        }
    },
    @{
        Name = "BLOCKED_FAILED_CHECKS"
        Expected = "BLOCKED"
        Args = Merge-Args -Base $common -Override @{
            Action = "merge"
            ApprovalMarker = "APPROVE_MERGE"
            PrNumber = 343
            MergeabilityStatus = "CLEAN"
            ChecksStatus = "FAIL"
        }
    },
    @{
        Name = "BLOCKED_DIRTY_SYNC_MAIN"
        Expected = "BLOCKED"
        Args = @{
            Action = "sync_main"
            ApprovalMarker = "APPROVE_SYNC_MAIN"
            Lane = "Protected Action Runner Test Lane"
            Branch = "main"
            TargetBranch = "main"
            ValidatorStatus = "PASS"
            RepoStatus = "DIRTY"
            StopCondition = "Test only. No mutation."
        }
    },
    @{
        Name = "BLOCKED_UNKNOWN_ACTION"
        Expected = "BLOCKED"
        Args = Merge-Args -Base $common -Override @{
            Action = "teleport"
            ApprovalMarker = "APPROVE_TELEPORT"
        }
    }
)

$results = @()
foreach ($case in $cases) {
    $results += Assert-Gate -Name $case.Name -Arguments $case.Args -ExpectedGate $case.Expected
}

$summary = [pscustomobject]@{
    schema = "AIOS_PROTECTED_ACTION_RUNNER_TEST_RESULT.v1"
    mode = "DRY_RUN"
    tests_run = $results.Count
    tests_passed = @($results | Where-Object { $_.passed }).Count
    tests_failed = 0
    mutation_performed = $false
    results = $results
}

$json = $summary | ConvertTo-Json -Depth 6
$null = $json | ConvertFrom-Json
Write-Output $json
