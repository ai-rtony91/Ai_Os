param(
    [string]$PacketId = "",
    [ValidateSet("DRY_RUN", "APPLY")]
    [string]$Mode = "DRY_RUN",
    [string]$Zone = "",
    [string]$Lane = "",
    [string]$Mission = "",
    [string]$Worktree = "C:\Dev\Ai.Os",
    [string]$StartBranch = "main",
    [string]$Branch = "",
    [string]$ApprovalAuthority = "",
    [string[]]$AllowedMutationFiles = @(),
    [string[]]$ForbiddenPaths = @(),
    [string[]]$ReadFirst = @(),
    [string[]]$Validators = @(),
    [string]$StopPoint = "",
    [string]$SupervisorIdentity = "ChatGPT Planning Supervisor under Anthony Human Owner",
    [string]$WorkerIdentity = "Codex CLI local executor inside C:\Dev\Ai.Os",
    [switch]$OutputJson,
    [switch]$AsPromptBlock,
    [switch]$FromContinuationPlan,
    [string]$ContinuationPlanScript = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Format-List {
    param([string[]]$Values, [string]$Fallback)
    if ($null -eq $Values -or $Values.Count -eq 0 -or ($Values.Count -eq 1 -and [string]::IsNullOrWhiteSpace($Values[0]))) {
        return "  - $Fallback"
    }
    $items = @()
    foreach ($value in $Values) {
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            $items += "  - $value"
        }
    }
    if ($items.Count -eq 0) {
        return "  - $Fallback"
    }
    return ($items -join "`r`n")
}

function Ensure-TextValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [object]$Value,
        [string]$Default = ""
    )

    if ($null -eq $Value) {
        return $Default
    }

    if ($Value -is [System.Array]) {
        return $Default
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        if (-not ($Value -is [string])) {
            return $Default
        }
    }

    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $Default
    }

    return $text
}

function Ensure-TextList {
    param(
        [object]$Values,
        [string[]]$Fallback = @()
    )

    $items = @()
    if ($null -eq $Values) {
        return @($Fallback)
    }

    if ($Values -is [string]) {
        if (-not [string]::IsNullOrWhiteSpace($Values)) {
            return @([string]$Values)
        }
        return @($Fallback)
    }

    if ($Values -is [System.Collections.IEnumerable]) {
        foreach ($value in @($Values)) {
            if ($null -eq $value) {
                continue
            }
            if ($value -is [System.Array]) {
                continue
            }
            if ($value -is [System.Collections.IEnumerable]) {
                if (-not ($value -is [string])) {
                    continue
                }
            }
            $normalized = [string]$value
            if (-not [string]::IsNullOrWhiteSpace($normalized)) {
                $items += $normalized
            }
        }
        if ($items.Count -gt 0) {
            return @($items)
        }
    }

    return @($Fallback)
}

function Invoke-ContinuationPlan {
    param([string]$ScriptPath)
    if ([string]::IsNullOrWhiteSpace($ScriptPath) -or -not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        return $null
    }
    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $ScriptPath -OutputJson
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return $null
        }
        return $raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

$fallbackAllowed = @(
    "AGENTS.md",
    "README.md",
    "RISK_POLICY.md",
    "docs/governance/source-of-truth-map.md",
    "automation/forex_engine/paper_study_journal.py",
    "automation/forex_engine/run_paper_study_journal_demo.py",
    "tests/forex_engine/test_paper_study_journal.py",
    "automation/orchestration/continuation/Get-AiOsSupervisedContinuationPlan.DRY_RUN.ps1",
    "automation/orchestration/continuation/Convert-AiOsContinuationPlanToProposedPacket.DRY_RUN.ps1",
    "automation/orchestration/relay_bus",
    "automation/orchestration/review_bridge"
)

$fallbackForbidden = @(
    "broker/OANDA/webhook/order/secrets paths",
    "real market data paths",
    "runtime state",
    "scheduler",
    "daemon",
    "worker launch",
    "queue",
    "locks",
    "approval inbox",
    "campaign registry",
    "telemetry",
    "Reports",
    "dashboard",
    "Cloudflare",
    "backup",
    "work_packets/proposed",
    "work_packets/active",
    "work_packets/complete"
)

$fallbackValidators = @(
    "git diff --check",
    "python -m pytest tests/orchestration/test_codex_packet_generator.py -q -p no:cacheprovider",
    "python -m pytest tests/orchestration/test_actor_relay_bus.py -q -p no:cacheprovider",
    "powershell -NoProfile -ExecutionPolicy Bypass -File .\aios.ps1 -Mode status"
)

$continuation = $null
if ($FromContinuationPlan) {
    $planScript = if (-not [string]::IsNullOrWhiteSpace($ContinuationPlanScript)) {
        $ContinuationPlanScript
    }
    else {
        Join-Path $PSScriptRoot "..\continuation\Get-AiOsSupervisedContinuationPlan.DRY_RUN.ps1"
    }
    $continuation = Invoke-ContinuationPlan -ScriptPath $planScript
}

$resolvedPacketId = Ensure-TextValue -Label "PACKET ID" -Value $PacketId -Default ""
if ([string]::IsNullOrWhiteSpace($resolvedPacketId) -and $continuation -and ($continuation.recommended_next_packet_id)) {
    $resolvedPacketId = [string]$continuation.recommended_next_packet_id
}

$resolvedZone = Ensure-TextValue -Label "ZONE" -Value $Zone -Default ""
if ([string]::IsNullOrWhiteSpace($resolvedZone) -and $continuation -and ($continuation.domain)) {
    $resolvedZone = [string]$continuation.domain
}

$resolvedLane = Ensure-TextValue -Label "LANE" -Value $Lane -Default ""
if ([string]::IsNullOrWhiteSpace($resolvedLane) -and $continuation -and ($continuation.recommended_lane)) {
    $resolvedLane = [string]$continuation.recommended_lane
}

$resolvedMission = Ensure-TextValue -Label "MISSION" -Value $Mission -Default ""
if ([string]::IsNullOrWhiteSpace($resolvedMission) -and $continuation -and ($continuation.recommended_next_packet_title)) {
    $resolvedMission = "build $($continuation.recommended_next_packet_title)"
}

$resolvedWorktree = Ensure-TextValue -Label "WORKTREE" -Value $Worktree -Default "C:\Dev\Ai.Os"
$resolvedStartBranch = Ensure-TextValue -Label "START_BRANCH" -Value $StartBranch -Default "main"
$resolvedApprovalAuthority = Ensure-TextValue -Label "APPROVAL AUTHORITY" -Value $ApprovalAuthority -Default "Anthony approves this scoped packet. No protected action approval beyond this scope is granted."
$resolvedSupervisorIdentity = Ensure-TextValue -Label "SUPERVISOR IDENTITY" -Value $SupervisorIdentity -Default "ChatGPT Planning Supervisor under Anthony Human Owner"
$resolvedWorkerIdentity = Ensure-TextValue -Label "WORKER IDENTITY" -Value $WorkerIdentity -Default "Codex CLI local executor inside C:\Dev\Ai.Os"
$resolvedMode = Ensure-TextValue -Label "MODE" -Value $Mode -Default "DRY_RUN"
$resolvedStopPoint = Ensure-TextValue -Label "STOP POINT" -Value $StopPoint -Default ""
$resolvedBranch = Ensure-TextValue -Label "BRANCH" -Value $Branch -Default ""

$resolvedReadFirst = Ensure-TextList -Values $ReadFirst -Fallback @()
if (@($resolvedReadFirst).Count -eq 0) {
    $resolvedReadFirst = @($fallbackAllowed)
}

$resolvedValidators = Ensure-TextList -Values $Validators -Fallback @()
if (@($resolvedValidators).Count -eq 0) {
    $resolvedValidators = if ($continuation -and $continuation.required_validators) {
        @($continuation.required_validators)
    }
    else {
        @($fallbackValidators)
    }
}

$resolvedAllowed = Ensure-TextList -Values $AllowedMutationFiles -Fallback @()
if (@($resolvedAllowed).Count -eq 0) {
    $resolvedAllowed = if ($continuation -and $continuation.recommended_files) {
        @($continuation.recommended_files)
    }
    else {
        @()
    }
}

$resolvedForbidden = Ensure-TextList -Values $ForbiddenPaths -Fallback $fallbackForbidden
$resolvedStopPoint = if ([string]::IsNullOrWhiteSpace($resolvedStopPoint) -and $continuation -and ($continuation.exact_next_safe_action)) { [string]$continuation.exact_next_safe_action } else { $resolvedStopPoint }

$missing = @()
if ([string]::IsNullOrWhiteSpace($resolvedPacketId)) { $missing += "PACKET ID" }
if ([string]::IsNullOrWhiteSpace($resolvedZone)) { $missing += "ZONE" }
if ([string]::IsNullOrWhiteSpace($resolvedLane)) { $missing += "LANE" }
if ([string]::IsNullOrWhiteSpace($resolvedMission)) { $missing += "MISSION" }
if ([string]::IsNullOrWhiteSpace($resolvedBranch)) { $missing += "BRANCH" }

$packetValid = $missing.Count -eq 0

$schemaText = "AIOS_CODEX_PACKET_GENERATOR.v1"
$generatedPacketText = @"
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED:
Read AGENTS.md first.
Read README.md second.
If unavailable, stop and report missing authority context.

IDENTITY MARKER:
$schemaText

SUPERVISOR IDENTITY:
$resolvedSupervisorIdentity

WORKER IDENTITY:
$resolvedWorkerIdentity

PACKET ID:
$resolvedPacketId

MODE:
$resolvedMode

ZONE:
$resolvedZone

LANE:
$resolvedLane

WORKTREE:
$resolvedWorktree

START_BRANCH:
$resolvedStartBranch

BRANCH:
$resolvedBranch

APPROVAL AUTHORITY:
$resolvedApprovalAuthority

MISSION:
$resolvedMission

PREFLIGHT
1. Confirm branch and state first.
2. Validate packet scope before apply.
3. No runtime/state mutation or secrets usage.

REQUIRED PREFLIGHT STATE:
- path must be $resolvedWorktree
- branch must be $resolvedStartBranch before branch creation
- repository must be clean

BRANCH PLAN:
1. Start on $resolvedStartBranch.
2. Verify branch safety and state.
3. Create/switch to branch $resolvedBranch.
4. Apply only the allowed mutation files.
5. Validate using VALIDATOR CHAIN.
6. Commit exact files only.

READ FIRST:
$(Format-List -Values $resolvedReadFirst -Fallback "None provided")

ALLOWED MUTATION FILES ONLY:
$(Format-List -Values $resolvedAllowed -Fallback "No mutation files provided")

FORBIDDEN PATHS:
$(Format-List -Values $resolvedForbidden -Fallback "No forbidden paths provided")

IMPLEMENTATION:
- generate a deterministic Codex-ready packet text
- no file writes from this DRY_RUN generator
- execution_allowed = false
- can_continue_without_anthony = false
- writes_files = false
- no network/API calls
- no broker/OANDA/secret loading
- no runtime state mutation
- no worker/daemon/scheduler start

VALIDATOR CHAIN:
$(Format-List -Values $resolvedValidators -Fallback "No validators provided")

COMMIT:
If validation passes, commit exact files only.

git add -- $($resolvedAllowed -join ' ')
git diff --cached --name-only
git diff --cached --check

git commit -m "feat(v1): update generated Codex packet"

STOP POINT:
$resolvedStopPoint

COMPLETION REPORT FORMAT:
1. CURRENT STATE
2. FILES CHANGED
3. TESTS
4. VALIDATION
5. COMMIT STATUS
6. SAFE NEXT ACTION

execution_allowed: false
can_continue_without_anthony: false
writes_files: false

STATUS:
PASS / BLOCKED
"@

$result = [ordered]@{
    schema                  = $schemaText
    generated_packet_text    = $generatedPacketText
    packet_valid            = [bool]$packetValid
    missing_required_fields = @($missing)
    writes_files            = $false
    execution_allowed       = $false
    can_continue_without_anthony = $false
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
    exit 0
}

if ($AsPromptBlock) {
    Write-Output $generatedPacketText
}
else {
    Write-Output $generatedPacketText
}
exit 0
