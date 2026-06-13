param(
    [switch]$OutputJson,
    [string]$RepoRoot = "",
    [string]$CampaignTaskScript = "",
    [string]$ForexRecommenderScript = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    param([string]$CandidateRoot)

    if (-not [string]::IsNullOrWhiteSpace($CandidateRoot)) {
        try {
            return (Resolve-Path -LiteralPath $CandidateRoot -ErrorAction Stop).Path
        }
        catch {
            throw "Invalid RepoRoot provided: $CandidateRoot"
        }
    }

    try {
        $gitRoot = git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($gitRoot)) {
            return $gitRoot.Trim()
        }
    }
    catch {
        # Ignore and fall back to script location.
    }

    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Read-JsonSafe {
    param([string]$Text, [string]$Source)
    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $null
    }
    try {
        $textValue = [string]$Text
        $startIndex = $textValue.IndexOf("{")
        if ($startIndex -lt 0) {
            throw "No JSON object found in text."
        }

        $endIndex = $textValue.LastIndexOf("}")
        if ($endIndex -lt $startIndex) {
            throw "JSON object boundaries are incomplete."
        }

        $jsonPayload = $textValue.Substring($startIndex, $endIndex - $startIndex + 1)
        $obj = $jsonPayload | ConvertFrom-Json
        $obj | Add-Member -NotePropertyName _aios_source -NotePropertyValue $Source -Force
        return $obj
    }
    catch {
        return [pscustomobject]@{
            _aios_parse_error = $_.Exception.Message
            _aios_source = $Source
        }
    }
}

function Invoke-JsonCommand {
    param([string]$Path, [string[]]$Arguments)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $Path @Arguments 2>$null
        if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
        return Read-JsonSafe -Text ($raw | Out-String) -Source $Path
    }
    catch {
        return [pscustomobject]@{
            _aios_parse_error = $_.Exception.Message
            _aios_source = $Path
        }
    }
}

function Has-MemberValue {
    param($Object, [string]$Name)
    if ($null -eq $Object) { return $false }
    return ($Object.PSObject.Properties.Name -contains $Name)
}

function Get-ActivePacketId {
    param([string]$RepoRootPath)

    $packetDir = Join-Path $RepoRootPath "automation/orchestration/work_packets/active"
    if (-not (Test-Path -LiteralPath $packetDir -PathType Container)) {
        return ""
    }

    $packetFiles = @(Get-ChildItem -LiteralPath $packetDir -File -Filter "*.json" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending)
    if ($packetFiles.Count -eq 0) { return "" }

    $packet = Read-JsonSafe -Text ((Get-Content -LiteralPath $packetFiles[0].FullName -Raw) 2>$null) -Source $packetFiles[0].FullName
    if (-not $packet -or (Has-MemberValue -Object $packet -Name "_aios_parse_error")) {
        return ""
    }
    return [string]$packet.packet_id
}

$repoRoot = Resolve-RepoRoot -CandidateRoot $RepoRoot

$gitStatusRaw = @(git -C $repoRoot status --short --untracked-files=all 2>$null)
$dirtyOrUntrackedCount = $gitStatusRaw.Count
$branch = (git -C $repoRoot branch --show-current 2>$null).Trim()
if ([string]::IsNullOrWhiteSpace($branch)) { $branch = "UNKNOWN" }

$activePacketId = Get-ActivePacketId -RepoRootPath $repoRoot

$registryPath = Join-Path $repoRoot "automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json"
$campaignNextPath = Join-Path $repoRoot "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1"
if (-not [string]::IsNullOrWhiteSpace($CampaignTaskScript)) {
    $campaignNextPath = $CampaignTaskScript
}

$forexDefaultScript = Join-Path $repoRoot "automation/orchestration/recommendations/Get-AiOsForexNextBuildPacket.DRY_RUN.ps1"
if ([string]::IsNullOrWhiteSpace($ForexRecommenderScript)) {
    $ForexRecommenderScript = $forexDefaultScript
}

$campaignReadiness = "NOT_AVAILABLE"
$campaignNextTask = Invoke-JsonCommand -Path $campaignNextPath -Arguments @("-OutputJson")
if ($campaignNextTask -and -not (Has-MemberValue -Object $campaignNextTask -Name "_aios_parse_error")) {
    $campaignNextTask | Add-Member -NotePropertyName _aios_parse_error -NotePropertyValue $null -Force
}
if ($campaignNextTask -and (Has-MemberValue -Object $campaignNextTask -Name "_aios_parse_error") -and -not $campaignNextTask._aios_parse_error) {
    $campaignReadiness = [string]$campaignNextTask.overall_readiness
}
elseif (Test-Path -LiteralPath $campaignNextPath -PathType Leaf) {
    $campaignReadiness = "AVAILABLE_BUT_PARSE_ERROR"
}

$forexPlan = Invoke-JsonCommand -Path $ForexRecommenderScript -Arguments @("-OutputJson")
$safeToApprove = $false
$domain = "FOREX_ENGINE"
$domainRecommender = "Get-AiOsForexNextBuildPacket.DRY_RUN.ps1"
$recommendedNextPacketId = ""
$recommendedNextPacketTitle = ""
$recommendedLane = ""
$recommendedFiles = @()
$requiredValidators = @()
$continuationStatus = "BLOCKED"
$reason = "No valid recommender evidence was available to produce a safe continuation recommendation."
$exactNextAction = "Resolve recommender dependency and rerun this continuation plan."

if ($forexPlan -and (Has-MemberValue -Object $forexPlan -Name "_aios_parse_error") -and -not $forexPlan._aios_parse_error -and $forexPlan.recommended_next_packet_id) {
    $safeToApprove = $true
    $recommendedNextPacketId = [string]$forexPlan.recommended_next_packet_id
    $recommendedNextPacketTitle = [string]$forexPlan.recommended_next_packet_title
    $recommendedLane = [string]$forexPlan.recommended_lane
    $recommendedFiles = @($forexPlan.recommended_files)
    $requiredValidators = @($forexPlan.required_validators)
    $reason = [string]$forexPlan.reason
    $exactNextAction = "Anthony review the proposed packet $recommendedNextPacketId, then approve Codex APPLY packet generation."
    $continuationStatus = "READY_FOR_APPROVAL"
}
elseif ($forexPlan -and (Has-MemberValue -Object $forexPlan -Name "_aios_parse_error") -and $forexPlan._aios_parse_error) {
    $reason = "Forex recommender output was not valid JSON in this environment."
    $continuationStatus = "BLOCKED"
}

if ($dirtyOrUntrackedCount -gt 0) {
    $continuationStatus = "REVIEW_REQUIRED"
    if ($safeToApprove) {
        $reason = "Repository is not clean. Review dirty/untracked changes before proposing or executing next packet work."
        $safeToApprove = $false
    }
    else {
        $reason = "Repository is not clean and no clean-domain recommendation is currently applicable."
    }
}

if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    $campaignReadiness = "NO_REGISTRY"
}

$validatorScripts = @(
    "Test-WorkerClaimCollision.DRY_RUN.ps1",
    "Test-LockRegistryIntegrity.DRY_RUN.ps1",
    "Test-AiOsIdentitySpine.DRY_RUN.ps1",
    "Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
)
$requiredValidatorsWithPath = @(
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
)
$validatorAvailable = @()
foreach ($entry in $validatorScripts) {
    $fullPath = Join-Path $repoRoot ("automation/orchestration/validators/{0}" -f $entry)
    $validatorAvailable += [string](Test-Path -LiteralPath $fullPath -PathType Leaf)
}

$requiredValidators = if ($requiredValidators.Count -gt 0) { @($requiredValidators) } else { @(
    "git diff --check",
    "python -m pytest tests/forex_engine -q -p no:cacheprovider",
    "python automation/forex_engine/run_readiness_demo.py",
    "python automation/forex_engine/run_paper_signal_intake_demo.py",
    "python automation/forex_engine/run_paper_risk_decision_demo.py",
    "python automation/forex_engine/run_paper_continuity_review_demo.py",
    "python automation/forex_engine/run_paper_study_journal_demo.py",
    ".\\aios.ps1 -Mode status"
) + @($requiredValidatorsWithPath) }

$blockedActions = @(
    "live trading",
    "broker/OANDA",
    "real orders",
    "real webhooks",
    "real market data",
    "API keys/secrets",
    "scheduler/daemon",
    "worker launch",
    "runtime mutation",
    "telemetry mutation",
    "dashboard mutation",
    "Cloudflare",
    "backup sync",
    "push/PR/merge automation"
)

$result = [pscustomobject]@{
    schema = "AIOS_SUPERVISED_CONTINUATION_PLAN.v1"
    mode = "DRY_RUN_READ_ONLY"
    repo_root = $repoRoot
    branch = $branch
    dirty_or_untracked_count = $dirtyOrUntrackedCount
    active_packet_id = $activePacketId
    campaign_readiness = $campaignReadiness
    domain = $domain
    domain_recommender = $domainRecommender
    recommended_next_packet_id = $recommendedNextPacketId
    recommended_next_packet_title = $recommendedNextPacketTitle
    recommended_lane = $recommendedLane
    recommended_files = @($recommendedFiles)
    required_validators = @($requiredValidators)
    blocked_actions = @($blockedActions)
    human_approval_required = $true
    execution_allowed = $false
    can_continue_without_anthony = $false
    continuation_status = $continuationStatus
    reason = $reason
    exact_next_safe_action = if ($safeToApprove) { $exactNextAction } else { "Resolve repository state and required safety gates before proposing next packet." }
    codex_handoff_summary = if ($safeToApprove) {
        [string]("Proposed next packet: {0}. Approve only after validator checklist and blocked-action review." -f $recommendedNextPacketId)
    } else {
        "No safe next packet can be proposed until repo cleanliness and recommender evidence are validated."
    }
    approval_requirement = [pscustomobject]@{
        active = $true
        validator_gates_required = $requiredValidators
        validator_scripts_exist = @($validatorAvailable)
    }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($result | ConvertTo-Json -Depth 20)
