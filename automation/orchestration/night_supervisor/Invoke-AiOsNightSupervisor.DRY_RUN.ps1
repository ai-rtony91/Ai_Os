<#
.SYNOPSIS
    AI_OS Night Supervisor orchestrator (DRY_RUN, read-only preview).

.DESCRIPTION
    Previews the full nightly supervision chain in execution order:

        1 bootstrap        2 checkpoint     3 validator       4 lock check
        5 approval plan    6 runtime state  7 resume record   8 cleanup/ledger
        9 summary report   10 safety enforcement

    This script is read-only. It does not write files, mutate active runtime /
    packet / approval / lock state, stage, commit, push, merge, launch workers,
    schedule tasks, touch trading/broker logic, or read/emit secrets.

    The executable sandbox writer lives in night_supervisor_harness.py. This
    .ps1 emits the same shape of plan so operators on Windows can preview the
    chain with the orchestration suite's native tooling. Authority is
    subordinate to RISK_POLICY.md and AGENTS.md; the stricter rule always wins.

.PARAMETER QuietJson
    Emit the plan as JSON only (no human-readable banner).
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [switch]$QuietJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$schema = "AIOS_NIGHT_SUPERVISOR_PLAN.v1"
$approvalAuthority = "Anthony Meza"
$dateKey = (Get-Date).ToString("yyyy-MM-dd")
$runtimeWriteRoot = "telemetry/night_supervisor"

function Resolve-AiOsRepoRoot {
    param([AllowEmptyString()][string]$RequestedRoot)

    if (-not [string]::IsNullOrWhiteSpace($RequestedRoot)) {
        return (Resolve-Path -LiteralPath $RequestedRoot -ErrorAction Stop).ProviderPath
    }

    $gitOutput = & git rev-parse --show-toplevel 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to resolve AI_OS repo root. Run inside the repo or pass -RepoRoot."
    }
    return [string]($gitOutput | Select-Object -First 1)
}

function Test-AiOsPathPresent {
    param([Parameter(Mandatory = $true)][string]$Path)
    return Test-Path -LiteralPath (Join-Path -Path $RepoRoot -ChildPath $Path)
}

$RepoRoot = Resolve-AiOsRepoRoot -RequestedRoot $RepoRoot

$branch = (& git -C $RepoRoot rev-parse --abbrev-ref HEAD 2>$null)
$headSha = (& git -C $RepoRoot rev-parse --short HEAD 2>$null)
$statusLines = @(& git -C $RepoRoot status --porcelain 2>$null | ForEach-Object { [string]$_ })
$changedFiles = @($statusLines | Where-Object { $_ -notmatch '^\?\?' -and $_.Trim() } | ForEach-Object { $_.Substring(3) })
$untrackedItems = @($statusLines | Where-Object { $_ -match '^\?\?' } | ForEach-Object { $_.Substring(3) })

# These boundaries are permanent for night supervision. A future Apply must
# enforce them with explicit guards before any write, child command, or network
# call. Do not remove without a separate West safety review.
$blockedCapabilities = @(
    "APPLY", "commit", "push", "merge",
    "active runtime state mutation",
    "active packet/approval/lock state change",
    "worker launch", "scheduled/background execution",
    "live trading", "broker execution", "secret handling"
)

$phases = @(
    [ordered]@{
        phase = "supervisor_bootstrap"; step = 1; status = "PLANNED"
        summary = "Resolve repo identity and recover the most recent validated runtime snapshot from $runtimeWriteRoot."
        mutations = @()
        next_safe_action = "Confirm branch/head identity before continuing."
    },
    [ordered]@{
        phase = "nightly_telemetry_checkpoint"; step = 2; status = "PLANNED"
        summary = "Capture a read-only runtime snapshot + checkpoint into $runtimeWriteRoot/$dateKey/."
        mutations = @("$runtimeWriteRoot/$dateKey/runtime_snapshot.json", "$runtimeWriteRoot/$dateKey/checkpoint.json")
        next_safe_action = "Run nightly validation against the snapshot."
    },
    [ordered]@{
        phase = "validator_automation"; step = 3; status = "PLANNED"
        summary = "Validate JSON parses (BOM-tolerant), run git diff --check, and repo integrity. Fail-closed creates an alert + stop condition."
        mutations = @()
        next_safe_action = "On any failure: STOP, write alert, hold for human review."
    },
    [ordered]@{
        phase = "lock_enforcement_automation"; step = 4; status = "PLANNED"
        summary = "Inspect locks read-only; produce expired-lock release PLAN only. Locks live outside allowed write paths, so none are released here."
        mutations = @()
        next_safe_action = "Review release plan; release needs a separate approved APPLY packet."
    },
    [ordered]@{
        phase = "approval_automation"; step = 5; status = "PLANNED"
        summary = "Classify approval inbox by risk tier. LOW = auto-eligible (DISABLED in DRY_RUN); MEDIUM/HIGH held for human review. No approval state changes."
        mutations = @()
        next_safe_action = "$approvalAuthority reviews MEDIUM/HIGH items."
    },
    [ordered]@{
        phase = "runtime_state_automation"; step = 6; status = "PLANNED"
        summary = "Write a PROPOSED runtime-state update to sandbox. Active runtime memory is never mutated without validation."
        mutations = @("$runtimeWriteRoot/$dateKey/runtime_state_proposal.json")
        next_safe_action = "Active mutation requires a separate validated APPLY packet."
    },
    [ordered]@{
        phase = "resume_capability_automation"; step = 7; status = "PLANNED"
        summary = "Write a resume record to $runtimeWriteRoot/resume/. Promotion to a canonical runtime path is deferred (outside allowed write paths)."
        mutations = @("$runtimeWriteRoot/resume/resume_$dateKey.json")
        next_safe_action = "Use resume record at morning startup."
    },
    [ordered]@{
        phase = "cleanup_and_ledger"; step = 8; status = "PLANNED"
        summary = "Plan temp cleanup (DRY_RUN, nothing deleted) and append an append-only nightly ledger event."
        mutations = @("$runtimeWriteRoot/night_ledger.jsonl")
        next_safe_action = "Ledger is evidence; deletion needs approval."
    },
    [ordered]@{
        phase = "reporting_and_alerting"; step = 9; status = "PLANNED"
        summary = "Write the nightly summary report; flag CRITICAL alerts for morning review."
        mutations = @("$runtimeWriteRoot/reports/night_summary_$dateKey.json")
        next_safe_action = "Review report; promote outputs only via approved packet."
    },
    [ordered]@{
        phase = "safety_enforcement"; step = 10; status = "PLANNED"
        summary = "Confirm no forbidden writes, no active-state mutation, no secrets, no trading. Fail closed otherwise."
        mutations = @()
        next_safe_action = "Verify safety_confirmation block in the report."
    }
)

$report = [ordered]@{
    schema = $schema
    mode = "DRY_RUN"
    supervisor_status = "READY"
    run_id = "plan_$((Get-Date).ToString('yyyyMMddTHHmmssZ'))"
    generated_at = (Get-Date).ToString("s")
    repo = [ordered]@{
        repo_root = $RepoRoot
        branch = [string]$branch
        head_sha = [string]$headSha
        changed_files = $changedFiles
        untracked_items = $untrackedItems
    }
    runtime_write_root = $runtimeWriteRoot
    executable_engine = "automation/orchestration/night_supervisor/night_supervisor_harness.py"
    phases = $phases
    safety_confirmation = [ordered]@{
        no_live_trading = $true
        no_broker_execution = $true
        no_secrets_exposed = $true
        no_active_state_mutation = $true
        no_commit_or_push = $true
        writes_within_allowed_paths_only = $true
    }
    next_safe_action = "Review this plan, then run night_supervisor_harness.py to execute the DRY_RUN chain into the sandbox."
    authority_boundary = [ordered]@{
        read_only_outside_sandbox = $true
        approval_authority = $approvalAuthority
        blocked_capabilities = $blockedCapabilities
    }
}

if ($QuietJson) {
    $report | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Night Supervisor Plan (DRY_RUN, read-only preview)"
Write-Host ("Branch: {0}  Head: {1}" -f $branch, $headSha)
Write-Host ("Changed files: {0}  Untracked: {1}" -f $changedFiles.Count, $untrackedItems.Count)
Write-Host ""
foreach ($p in $phases) {
    Write-Host ("  [{0,2}] {1,-10} {2}" -f $p.step, $p.status, $p.phase)
}
Write-Host ""
Write-Host ("Executable engine: {0}" -f $report.executable_engine)
Write-Host ("Next safe action: {0}" -f $report.next_safe_action)
Write-Host "Mutation skipped: this orchestrator preview is read-only."
