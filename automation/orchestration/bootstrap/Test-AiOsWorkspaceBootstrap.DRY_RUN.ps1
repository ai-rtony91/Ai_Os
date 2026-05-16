param(
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
    [string]$SessionExamplePath = "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json",
    [string]$CheckpointExamplePath = "automation/orchestration/terminal_workstations/AIOS_WORKSPACE_CHECKPOINT.example.json",
    [string]$OperatorRulesPath = "automation/orchestration/operator/AIOS_OPERATOR_RULES.json"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Test-PowerShellParse {
    param([Parameter(Mandatory = $true)][string]$Path)

    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count -gt 0) {
        throw "PowerShell parse failed for $Path`: $($errors[0].Message)"
    }
}

function Assert-NoBlockedAutomation {
    param([Parameter(Mandatory = $true)][string]$Path)

    $content = Get-Content -LiteralPath $Path -Raw
    $blockedPatterns = @(
        ("bro" + "ker"),
        ("OAN" + "DA"),
        ("api" + "_key"),
        ("web" + "hook"),
        ("live" + "_order"),
        ("real" + "_order"),
        ("scheduled" + "_task"),
        ("startup" + "_task")
    )

    $blockedPatterns | ForEach-Object {
        $pattern = $_
        if ($content -match [regex]::Escape($pattern)) {
            throw "Blocked automation pattern found in $Path`: $pattern"
        }
    }
}

function Assert-NoAssistantAutoStart {
    param([Parameter(Mandatory = $true)][string]$Path)

    $content = Get-Content -LiteralPath $Path -Raw
    $autoStartPatterns = @(
        ("(^|[\s;&])cod" + "ex\.exe(\s|$)"),
        ("(^|[\s;&])cod" + "ex\s+-"),
        ("Start-Process\s+cod" + "ex"),
        ("&\s+cod" + "ex(\s|$)")
    )

    $autoStartPatterns | ForEach-Object {
        $pattern = $_
        if ($content -match $pattern) {
            throw "Assistant auto-start pattern found in $Path`: $pattern"
        }
    }
}

function Assert-NoScheduledOrStartupMutation {
    param([Parameter(Mandatory = $true)][string]$Path)

    $content = Get-Content -LiteralPath $Path -Raw
    $blockedPatterns = @(
        "Register-ScheduledTask",
        "New-ScheduledTask",
        "schtasks.exe",
        "schtasks ",
        "\Startup\",
        "Start Menu\Programs\Startup"
    )

    $blockedPatterns | ForEach-Object {
        $pattern = $_
        if ($content.IndexOf($pattern, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            throw "Scheduled/startup mutation pattern found in $Path`: $pattern"
        }
    }
}

function Assert-NoBrokerLiveTradingMutation {
    param([Parameter(Mandatory = $true)][string]$Path)

    $content = Get-Content -LiteralPath $Path -Raw
    $blockedPatterns = @(
        "Invoke-RestMethod",
        "Invoke-WebRequest",
        "New-WebServiceProxy",
        "Send-AiOsLiveOrder",
        "Submit-LiveOrder",
        "Place-LiveOrder",
        "Connect-Oanda",
        "Connect-Broker"
    )

    $blockedPatterns | ForEach-Object {
        $pattern = $_
        if ($content.IndexOf($pattern, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            throw "Broker/API/live trading mutation pattern found in $Path`: $pattern"
        }
    }
}

$requiredFiles = @(
    "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
    "automation/orchestration/bootstrap/Resolve-AiOsWorkspaceIntent.ps1",
    "automation/orchestration/bootstrap/Set-AiOsTerminalIdentity.ps1",
    "automation/orchestration/bootstrap/Start-AiOsWorkspace.ps1",
    "automation/orchestration/bootstrap/Start-AiOsDay.ps1",
    "automation/orchestration/bootstrap/Open-AiOsLane.ps1",
    "automation/orchestration/bootstrap/Save-AiOsSession.ps1",
    "automation/orchestration/bootstrap/Restore-AiOsSession.ps1",
    "automation/orchestration/bootstrap/Save-AiOsWorkspaceCheckpoint.ps1",
    "automation/orchestration/bootstrap/Restore-AiOsWorkspaceCheckpoint.ps1",
    "automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1",
    "automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1",
    "automation/orchestration/work_packets/New-AiOsWorkPacket.ps1",
    "automation/orchestration/work_packets/Get-AiOsWorkPacketState.ps1",
    "automation/orchestration/work_packets/Route-AiOsWorkPacket.DRY_RUN.ps1",
    "automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json",
    "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json",
    "automation/orchestration/terminal_workstations/AIOS_WORKSPACE_CHECKPOINT.example.json",
    "automation/orchestration/operator/AIOS_OPERATOR_RULES.json",
    "docs/AI_OS/orchestration/AIOS_WORKSPACE_BOOTSTRAP.md",
    "docs/AI_OS/orchestration/AIOS_OPERATOR_RULEBOOK.md",
    "docs/AI_OS/orchestration/AIOS_DAILY_START.md",
    "docs/AI_OS/orchestration/AIOS_WORK_PACKETS.md"
)

$requiredDirectories = @(
    "automation/orchestration/work_packets",
    "automation/orchestration/work_packets/active",
    "automation/orchestration/work_packets/blocked",
    "automation/orchestration/work_packets/complete",
    "automation/orchestration/work_packets/templates"
)

$requiredPacketFields = @(
    "packet_id",
    "title",
    "intent",
    "owner_lane",
    "assigned_worker",
    "repo",
    "branch",
    "status",
    "priority",
    "created_utc",
    "updated_utc",
    "validator",
    "next_action",
    "blocked_by",
    "related_files",
    "related_packets",
    "notes"
)

$scriptName = Split-Path -Leaf $PSCommandPath
Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Workspace Bootstrap Validator" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no destructive cleanup, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: trust prompt path and Git branch, not stale terminal/tab title after cd."

Write-Host ""
Write-Host "== Required Files ==" -ForegroundColor Yellow
$requiredFiles | ForEach-Object {
    $requiredFile = $_
    $fullPath = Resolve-AiOsPath -Path $requiredFile
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        throw "Missing required file: $requiredFile"
    }
    Write-Host "FOUND: $requiredFile"
}

Write-Host ""
Write-Host "== Required Directories ==" -ForegroundColor Yellow
$requiredDirectories | ForEach-Object {
    $requiredDirectory = $_
    $fullPath = Resolve-AiOsPath -Path $requiredDirectory
    if (-not (Test-Path -LiteralPath $fullPath -PathType Container)) {
        throw "Missing required directory: $requiredDirectory"
    }
    Write-Host "FOUND: $requiredDirectory"
}

Write-Host ""
Write-Host "== PowerShell Parse ==" -ForegroundColor Yellow
$requiredFiles | Where-Object { $_ -like "*.ps1" } | ForEach-Object {
    $scriptFile = $_
    $fullPath = Resolve-AiOsPath -Path $scriptFile
    Test-PowerShellParse -Path $fullPath
    if ((Split-Path -Leaf $fullPath) -ne "Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1") {
        Assert-NoBlockedAutomation -Path $fullPath
        Assert-NoAssistantAutoStart -Path $fullPath
        Assert-NoScheduledOrStartupMutation -Path $fullPath
        Assert-NoBrokerLiveTradingMutation -Path $fullPath
    }
    Write-Host "PASS: $scriptFile"
}

Write-Host ""
Write-Host "== JSON Parse ==" -ForegroundColor Yellow
$registryFullPath = Resolve-AiOsPath -Path $RegistryPath
$sessionExampleFullPath = Resolve-AiOsPath -Path $SessionExamplePath
$checkpointExampleFullPath = Resolve-AiOsPath -Path $CheckpointExamplePath
$operatorRulesFullPath = Resolve-AiOsPath -Path $OperatorRulesPath
$registry = Get-Content -LiteralPath $registryFullPath -Raw | ConvertFrom-Json
$sessionExample = Get-Content -LiteralPath $sessionExampleFullPath -Raw | ConvertFrom-Json
$checkpointExample = Get-Content -LiteralPath $checkpointExampleFullPath -Raw | ConvertFrom-Json
$operatorRules = Get-Content -LiteralPath $operatorRulesFullPath -Raw | ConvertFrom-Json
Write-Host "PASS: $RegistryPath"
Write-Host "PASS: $SessionExamplePath"
Write-Host "PASS: $CheckpointExamplePath"
Write-Host "PASS: $OperatorRulesPath"
Assert-NoBlockedAutomation -Path $registryFullPath
Assert-NoBlockedAutomation -Path $sessionExampleFullPath
Assert-NoBlockedAutomation -Path $checkpointExampleFullPath
Assert-NoAssistantAutoStart -Path $registryFullPath
Assert-NoAssistantAutoStart -Path $sessionExampleFullPath
Assert-NoAssistantAutoStart -Path $checkpointExampleFullPath

Write-Host ""
Write-Host "== Work Packet Template ==" -ForegroundColor Yellow
$packetTemplatePath = Resolve-AiOsPath -Path "automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json"
$packetTemplate = Get-Content -LiteralPath $packetTemplatePath -Raw | ConvertFrom-Json
$requiredPacketFields | ForEach-Object {
    $field = $_
    if (-not ($packetTemplate.PSObject.Properties.Name -contains $field)) {
        throw "Packet template missing field: $field"
    }
    Write-Host "PASS: template field $field"
}

Write-Host ""
Write-Host "== Work Packet Examples ==" -ForegroundColor Yellow
$packetExampleFiles = @()
@("active", "blocked", "complete") | ForEach-Object {
    $state = $_
    $statePath = Resolve-AiOsPath -Path "automation/orchestration/work_packets/$state"
    $files = @(Get-ChildItem -LiteralPath $statePath -Filter "*.json" -File)
    if ($files.Count -lt 1) {
        if ($state -eq "active") {
            Write-Host "PASS: no active packet JSON files"
        } else {
            throw "Missing example packet in state folder: $state"
        }
    } else {
        $packetExampleFiles += $files
    }
}

$packetExampleFiles | ForEach-Object {
    $packetFile = $_
    if ($packetFile.Name -notmatch "^\d{8}-\d{6}-[a-z0-9-]+\.json$") {
        throw "Packet filename does not match YYYYMMDD-HHMMSS-packet-id.json: $($packetFile.Name)"
    }

    $packet = Get-Content -LiteralPath $packetFile.FullName -Raw | ConvertFrom-Json
    $requiredPacketFields | ForEach-Object {
        $field = $_
        if (-not ($packet.PSObject.Properties.Name -contains $field)) {
            throw "Packet $($packetFile.Name) missing field: $field"
        }
    }

    if ([string]::IsNullOrWhiteSpace($packet.repo) -or [string]::IsNullOrWhiteSpace($packet.branch)) {
        throw "Packet must tie to repo and branch: $($packetFile.Name)"
    }

    if (@("active", "blocked", "complete") -notcontains $packet.status) {
        throw "Packet has invalid status: $($packetFile.Name)"
    }

    Write-Host "PASS: $($packetFile.Name)"
}

if (-not $registry.lanes -or @($registry.lanes).Count -lt 1) {
    throw "Lane registry has no lanes."
}

if (-not $sessionExample.lanes -or @($sessionExample.lanes).Count -lt 1) {
    throw "Session example has no lanes."
}

if (-not $checkpointExample.lanes -or @($checkpointExample.lanes).Count -lt 1) {
    throw "Checkpoint example has no lanes."
}

if (@($registry.lanes)[0].lane_id -ne "main_control") {
    throw "CONTROL lane must be leftmost in registry."
}

if (@($registry.lanes)[0].path -ne "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN") {
    throw "CONTROL lane path must remain fixed root."
}

if (@($registry.lanes)[0].branch -ne "main") {
    throw "CONTROL lane branch must remain main."
}

if (@($checkpointExample.lanes)[0].lane_id -ne "main_control") {
    throw "CONTROL lane must be leftmost in checkpoint example."
}

if (-not $operatorRules.lane_identity) {
    throw "Operator rules missing lane_identity."
}

if ($operatorRules.lane_identity.lane_id -ne "rulebook_codex") {
    throw "Operator rules lane_identity must be rulebook_codex."
}

$titleSeparator = " " + [char]0x00b7 + " "

if ($operatorRules.lane_identity.display_title -ne ("RULEBOOK" + $titleSeparator + "codex")) {
    throw "Operator rules display_title must be RULEBOOK · codex."
}

if ($operatorRules.lane_identity.truth_source -ne "path_and_branch") {
    throw "Operator rules lane_identity truth_source must be path_and_branch."
}

$requiredRuleTexts = @(
    "Always say WHERE before commands.",
    "Always name the visible tab/window first.",
    "Always include the path before commands.",
    "Codex worker vs Git/PowerShell save tab must be distinct.",
    "CONTROL is permanent root.",
    "Path + branch are the truth source.",
    "No Codex auto-launch.",
    "Preview before launch.",
    "No commits/pushes without explicit command.",
    "No scheduled/startup tasks.",
    "No broker/API/live trading.",
    "Single-writer brainstem rule: only one Codex worker may edit overlapping orchestration/brainstem files at a time. If files under automation/orchestration/bootstrap, automation/orchestration/supervisor, automation/orchestration/operator, automation/orchestration/work_packets, or docs/AI_OS/orchestration overlap, stop extra Codex workers before continuing.",
    "Any newly discovered operator workflow rule must be added to the operator rulebook or validator before continuing major work."
)

Write-Host ""
Write-Host "== Operator Rulebook Rules ==" -ForegroundColor Yellow
$operatorRuleStrings = @($operatorRules.rules)
$requiredRuleTexts | ForEach-Object {
    $ruleText = $_
    if ($operatorRuleStrings -notcontains $ruleText) {
        throw "Operator rules missing required rule: $ruleText"
    }
    Write-Host "PASS: $ruleText"
}

$requiredLaneIds = @(
    "main_control",
    "create_codex",
    "save_git",
    "route_dispatch",
    "check_audit",
    "watch_state",
    "rulebook_codex"
)

$actualLaneOrder = @($registry.lanes | ForEach-Object { $_.lane_id })
for ($index = 0; $index -lt ($requiredLaneIds.Count - 1); $index += 1) {
    if ($actualLaneOrder[$index] -ne $requiredLaneIds[$index]) {
        throw "Registry lane order mismatch at index $index`: expected $($requiredLaneIds[$index]), found $($actualLaneOrder[$index])"
    }
}

$requiredDisplayTitles = @(
    ("CONTROL" + $titleSeparator + "main"),
    ("CREATE" + $titleSeparator + "codex"),
    ("SAVE" + $titleSeparator + "git"),
    ("ROUTE" + $titleSeparator + "dispatch"),
    ("CHECK" + $titleSeparator + "audit"),
    ("WATCH" + $titleSeparator + "state"),
    ("RULEBOOK" + $titleSeparator + "codex")
)

Write-Host ""
Write-Host "== Required Lane IDs ==" -ForegroundColor Yellow
$actualLaneIds = @($registry.lanes | ForEach-Object { $_.lane_id })
$requiredLaneIds | ForEach-Object {
    $laneId = $_
    if ($actualLaneIds -notcontains $laneId) {
        throw "Missing required lane_id: $laneId"
    }
    Write-Host "PASS: $laneId"
}

Write-Host ""
Write-Host "== Launch Policy ==" -ForegroundColor Yellow
if ($registry.launch_policy -ne "windows_terminal_tab_only") {
    throw "Registry launch_policy must be windows_terminal_tab_only."
}
if ($registry.fallback_policy -ne "print_manual_command") {
    throw "Registry fallback_policy must be print_manual_command."
}
if ($checkpointExample.launch_policy -ne "windows_terminal_tab_only") {
    throw "Checkpoint launch_policy must be windows_terminal_tab_only."
}
if ($checkpointExample.fallback_policy -ne "print_manual_command") {
    throw "Checkpoint fallback_policy must be print_manual_command."
}
Write-Host "PASS: launch_policy windows_terminal_tab_only"
Write-Host "PASS: fallback_policy print_manual_command"

Write-Host ""
Write-Host "== Codex Lanes Manual Only ==" -ForegroundColor Yellow
@($registry.lanes | Where-Object { $_.lane_id -like "*codex*" -or $_.display_title -like "*codex*" }) | ForEach-Object {
    $lane = $_
    if ($lane.lane_id -eq "create_codex" -and $lane.role.IndexOf("Manual", [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw "Codex lane must state manual use: $($lane.lane_id)"
    }
    Write-Host "PASS: $($lane.lane_id) manual lane"
}

Write-Host ""
Write-Host "== Required Display Titles ==" -ForegroundColor Yellow
$actualDisplayTitles = @($registry.lanes | ForEach-Object { $_.display_title })
$requiredDisplayTitles | ForEach-Object {
    $displayTitle = $_
    if ($actualDisplayTitles -notcontains $displayTitle) {
        throw "Missing required display_title: $displayTitle"
    }
    Write-Host "PASS: $displayTitle"
}

$requiredSessionFields = @(
    "active_workspace",
    "active_worktree",
    "active_branch",
    "truth_rule",
    "open_lanes",
    "last_known_roles",
    "last_commands",
    "pending_workorders",
    "last_validator_status",
    "next_safe_action"
)

$requiredCheckpointFields = @(
    "checkpoint_id",
    "created_at",
    "active_workspace",
    "active_worktree",
    "active_branch",
    "launch_policy",
    "fallback_policy",
    "lanes",
    "last_commands",
    "pending_workorders",
    "last_validator_status",
    "next_safe_action"
)

Write-Host ""
Write-Host "== Session State Fields ==" -ForegroundColor Yellow
$requiredSessionFields | ForEach-Object {
    $field = $_
    if (-not ($sessionExample.PSObject.Properties.Name -contains $field)) {
        throw "Session example missing field: $field"
    }
    Write-Host "PASS: $field"
}

Write-Host ""
Write-Host "== Workspace Checkpoint Fields ==" -ForegroundColor Yellow
$requiredCheckpointFields | ForEach-Object {
    $field = $_
    if (-not ($checkpointExample.PSObject.Properties.Name -contains $field)) {
        throw "Checkpoint example missing field: $field"
    }
    Write-Host "PASS: $field"
}

Write-Host ""
Write-Host "== Lane Naming Fields ==" -ForegroundColor Yellow
@($registry.lanes) | ForEach-Object {
    $lane = $_
    @("lane_id", "display_title", "window_title", "tab_title", "path", "branch", "role", "emoji_marker", "truth_source") | ForEach-Object {
        $field = $_
        if (-not ($lane.PSObject.Properties.Name -contains $field)) {
            throw "Lane $($lane.lane_id) missing field: $field"
        }
    }

    if ($lane.truth_source -ne "path_and_branch") {
        throw "Lane $($lane.lane_id) has invalid truth_source: $($lane.truth_source)"
    }

    if ($lane.display_title -match "AI_OS") {
        throw "Lane $($lane.lane_id) still has old AI_OS-prefixed display title."
    }

    if ($lane.display_title.IndexOf("filter", [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
        throw "Lane $($lane.lane_id) has blocked user-facing word: filter"
    }

    @("display_title", "window_title", "tab_title") | ForEach-Object {
        $titleField = $_
        $titleValue = [string]$lane.PSObject.Properties[$titleField].Value
        if ($titleValue -match "Windows PowerShell|PowerShell|aios-worker-|phase-") {
            throw "Lane $($lane.lane_id) has generic or filesystem/branch title in $titleField`: $titleValue"
        }
    }

    Write-Host "lane_id: $($lane.lane_id)" -ForegroundColor Cyan
    Write-Host "display_title: $($lane.display_title)"
    Write-Host "window_title: $($lane.window_title)"
    Write-Host "tab_title: $($lane.tab_title)"
    Write-Host "emoji_marker: $($lane.emoji_marker)"
    Write-Host "truth_source: $($lane.truth_source)"
    Write-Host "path: $($lane.path)"
    Write-Host "branch: $($lane.branch)"
    Write-Host "role: $($lane.role)"
    Write-Host ""
}

Write-Host "== Checkpoint Lane Fields ==" -ForegroundColor Yellow
@($checkpointExample.lanes) | ForEach-Object {
    $lane = $_
    @("lane_id", "display_title", "window_title", "tab_title", "emoji_marker", "role", "path", "branch", "truth_source") | ForEach-Object {
        $field = $_
        if (-not ($lane.PSObject.Properties.Name -contains $field)) {
            throw "Checkpoint lane $($lane.lane_id) missing field: $field"
        }
    }

    if ($actualLaneIds -notcontains $lane.lane_id) {
        throw "Checkpoint lane_id is not in registry: $($lane.lane_id)"
    }

    if ($lane.truth_source -ne "path_and_branch") {
        throw "Checkpoint lane $($lane.lane_id) has invalid truth_source: $($lane.truth_source)"
    }

    Write-Host "PASS: $($lane.lane_id)"
}

Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

Write-Host ""
Write-Host "== Bootstrap Preview Smoke Test ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1" -Preview

Write-Host ""
Write-Host "== Intent Preview Smoke Tests ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1" -Preview -Intent "queue dispatcher automation"
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1" -Preview -Intent "validation cleanup audit"
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1" -Preview -Intent "edit feature with codex"
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1" -Preview -Intent "operator rulebook memory"
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1" -Preview -Intent "complete brainstem daily start route"

Write-Host ""
Write-Host "== Supervisor Planner Smoke Test ==" -ForegroundColor Yellow
$supervisorOutput = powershell -ExecutionPolicy Bypass -File "automation\orchestration\supervisor\Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1" -Intent "complete brainstem daily start route"
$supervisorText = ($supervisorOutput -join [Environment]::NewLine)
if ($supervisorText -notmatch "COPY START" -or $supervisorText -notmatch "COPY END") {
    throw "Supervisor planner copy markers missing."
}
if ($supervisorText -notmatch "What workers are needed" -or $supervisorText -notmatch "Exact next safe action") {
    throw "Supervisor planner required output blocks missing."
}
$supervisorOutput | ForEach-Object { Write-Host $_ }

Write-Host ""
Write-Host "== Daily Start Smoke Test ==" -ForegroundColor Yellow
$dailyStartOutput = powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsDay.ps1" -Intent "complete brainstem daily start route" -MaxTabs 3
$dailyStartText = ($dailyStartOutput -join [Environment]::NewLine)
if ($dailyStartText -notmatch "COPY START" -or $dailyStartText -notmatch "COPY END") {
    throw "Daily Start copy markers missing."
}
if ($dailyStartText -notmatch "WHERE TO RUN NEXT") {
    throw "Daily Start WHERE TO RUN NEXT block missing."
}
if ($dailyStartText -notmatch "Codex auto-launch performed: NO") {
    throw "Daily Start must report no Codex auto-launch."
}
$dailyStartOutput | ForEach-Object { Write-Host $_ }

Write-Host ""
Write-Host "== Lane Preview Smoke Test ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Open-AiOsLane.ps1" -LaneId save_git -Preview
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Open-AiOsLane.ps1" -LaneId rulebook_codex -Preview

Write-Host ""
Write-Host "== Restore Preview Smoke Test ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Restore-AiOsSession.ps1" -Preview

Write-Host ""
Write-Host "== Workspace Checkpoint Preview Smoke Tests ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Save-AiOsWorkspaceCheckpoint.ps1" -Preview
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Restore-AiOsWorkspaceCheckpoint.ps1" -Preview

Write-Host ""
Write-Host "Workspace bootstrap DRY_RUN validation passed." -ForegroundColor Green
Write-Host "Files staged: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
