[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-AiOsSection {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ("-" * $Title.Length) -ForegroundColor DarkGray
}

function Write-AiOsLine {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [AllowNull()][string]$Value = ""
    )

    Write-Host ("{0,-28} {1}" -f $Label, $Value)
}

function Invoke-AiOsTextCommand {
    param([Parameter(Mandatory = $true)][scriptblock]$Command)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & $Command 2>&1
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            Output = @($output | ForEach-Object { [string]$_ })
        }
    }
    catch {
        return [pscustomobject]@{
            ExitCode = 1
            Output = @($_.Exception.Message)
        }
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Resolve-AiOsMorningBriefRepoRoot {
    $resolverPath = Join-Path $PSScriptRoot "Resolve-AiOsRepoRoot.ps1"
    if (Test-Path -LiteralPath $resolverPath -PathType Leaf) {
        . $resolverPath
        return Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
    }

    $gitRoot = Invoke-AiOsTextCommand -Command { git rev-parse --show-toplevel }
    if ($gitRoot.ExitCode -eq 0 -and $gitRoot.Output.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($gitRoot.Output[0])) {
        return $gitRoot.Output[0].Trim()
    }

    throw "Unable to resolve AI_OS repo root."
}

function Invoke-AiOsHelperJson {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [string[]]$Arguments = @()
    )

    $helperPath = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $helperPath -PathType Leaf)) {
        return [pscustomobject]@{
            Available = $false
            Data = $null
            Summary = "Helper not found: $RelativePath"
        }
    }

    $result = Invoke-AiOsTextCommand -Command {
        powershell -NoProfile -ExecutionPolicy Bypass -File $helperPath @Arguments
    }

    if ($result.ExitCode -ne 0) {
        return [pscustomobject]@{
            Available = $true
            Data = $null
            Summary = "Helper returned exit code $($result.ExitCode)."
        }
    }

    try {
        $jsonText = ($result.Output -join [Environment]::NewLine).Trim()
        return [pscustomobject]@{
            Available = $true
            Data = ($jsonText | ConvertFrom-Json -ErrorAction Stop)
            Summary = "Loaded."
        }
    }
    catch {
        return [pscustomobject]@{
            Available = $true
            Data = $null
            Summary = "Helper output was not parseable JSON."
        }
    }
}

function Get-AiOsCount {
    param([AllowNull()]$Value)

    if ($null -eq $Value) { return 0 }
    return @($Value).Count
}

function Get-AiOsPropertyValue {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = "UNKNOWN"
    )

    if ($null -eq $Object) { return $Default }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        $value = $Object.$Name
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            return [string]$value
        }
    }

    return $Default
}

function Get-AiOsPropertyCount {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if ($null -eq $Object) { return 0 }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        return Get-AiOsCount $Object.$Name
    }

    return 0
}

$repoRoot = Resolve-AiOsMorningBriefRepoRoot
Push-Location -LiteralPath $repoRoot
try {
    $branchResult = Invoke-AiOsTextCommand -Command { git branch --show-current }
    $statusResult = Invoke-AiOsTextCommand -Command { git status --short --branch }
    $lastCommitResult = Invoke-AiOsTextCommand -Command { git log -1 --oneline }

    $branch = if ($branchResult.ExitCode -eq 0 -and $branchResult.Output.Count -gt 0) { $branchResult.Output[0] } else { "UNKNOWN" }
    $statusLines = @($statusResult.Output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $changedLines = @($statusLines | Where-Object { $_ -notlike "##*" })
    $lastCommit = if ($lastCommitResult.ExitCode -eq 0 -and $lastCommitResult.Output.Count -gt 0) { $lastCommitResult.Output[0] } else { "UNKNOWN" }

    Write-Host "AI_OS Morning Brief" -ForegroundColor Yellow
    Write-Host "Mode: READ_ONLY"
    Write-Host "Repo: $repoRoot"

    Write-AiOsSection "Repo State"
    Write-AiOsLine "Current branch:" $branch
    if ($changedLines.Count -eq 0) {
        Write-AiOsLine "Working tree:" "CLEAN"
    }
    else {
        Write-AiOsLine "Working tree:" ("DIRTY - {0} changed or untracked item(s)" -f $changedLines.Count)
    }
    Write-AiOsLine "Last commit:" $lastCommit

    Write-AiOsSection "Approval Inbox"
    $approval = Invoke-AiOsHelperJson -RepoRoot $repoRoot -RelativePath "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1" -Arguments @("-QuietJson")
    if (-not $approval.Available -or $null -eq $approval.Data) {
        Write-AiOsLine "Status:" $approval.Summary
    }
    else {
        Write-AiOsLine "Pending approvals:" (Get-AiOsPropertyCount -Object $approval.Data -Name "pending_approvals")
        Write-AiOsLine "Approved actions:" (Get-AiOsPropertyCount -Object $approval.Data -Name "approved_actions")
        Write-AiOsLine "Blocked actions:" (Get-AiOsPropertyCount -Object $approval.Data -Name "blocked_actions")
    }

    Write-AiOsSection "Work Packets"
    $packetRecommendation = Invoke-AiOsHelperJson -RepoRoot $repoRoot -RelativePath "automation/orchestration/work_packets/Get-AiOsPacketStateRecommendation.DRY_RUN.ps1" -Arguments @("-QuietJson")
    if (-not $packetRecommendation.Available -or $null -eq $packetRecommendation.Data) {
        Write-AiOsLine "Status:" $packetRecommendation.Summary
    }
    else {
        Write-AiOsLine "Packet:" (Get-AiOsPropertyValue -Object $packetRecommendation.Data -Name "packet_id")
        Write-AiOsLine "Current state:" (Get-AiOsPropertyValue -Object $packetRecommendation.Data -Name "current_state")
        Write-AiOsLine "Recommended state:" (Get-AiOsPropertyValue -Object $packetRecommendation.Data -Name "recommended_next_state")
        Write-AiOsLine "Transition allowed:" (Get-AiOsPropertyValue -Object $packetRecommendation.Data -Name "transition_allowed")
    }

    Write-AiOsSection "Validator Recommendation"
    $validator = Invoke-AiOsHelperJson -RepoRoot $repoRoot -RelativePath "automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1" -Arguments @("-OutputJson")
    if (-not $validator.Available -or $null -eq $validator.Data) {
        Write-AiOsLine "Status:" $validator.Summary
    }
    else {
        Write-AiOsLine "Approval required:" (Get-AiOsPropertyValue -Object $validator.Data -Name "approval_required")
        Write-AiOsLine "Changed paths:" (Get-AiOsPropertyCount -Object $validator.Data -Name "changed_paths")
        Write-AiOsLine "Recommendations:" (Get-AiOsPropertyCount -Object $validator.Data -Name "recommendations")
    }

    Write-AiOsSection "Commit Package"
    $commitPackage = Invoke-AiOsHelperJson -RepoRoot $repoRoot -RelativePath "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1" -Arguments @("-OutputJson")
    if (-not $commitPackage.Available -or $null -eq $commitPackage.Data) {
        Write-AiOsLine "Status:" $commitPackage.Summary
    }
    else {
        Write-AiOsLine "Recommended files:" (Get-AiOsPropertyCount -Object $commitPackage.Data -Name "recommended_files")
        Write-AiOsLine "Excluded files:" (Get-AiOsPropertyCount -Object $commitPackage.Data -Name "excluded_files")
        Write-AiOsLine "Risk count:" (Get-AiOsPropertyCount -Object $commitPackage.Data -Name "risks")
        Write-AiOsLine "Suggested message:" (Get-AiOsPropertyValue -Object $commitPackage.Data -Name "commit_message_suggestion")
    }

    Write-AiOsSection "Clean-State Check"
    Write-AiOsLine "Suggested command:" "powershell -NoProfile -File scripts/validation/Invoke-AIOSCleanStateCheck.ps1"
    Write-AiOsLine "Run automatically:" "NO"

    Write-AiOsSection "Next Safe Action"
    $nextSafeAction = "Review the sections above and continue with a scoped AI_OS packet."
    if ($changedLines.Count -gt 0) {
        $nextSafeAction = "Classify the dirty working tree before starting unrelated APPLY work."
    }
    elseif ($approval.Available -and $null -ne $approval.Data -and (Get-AiOsPropertyCount -Object $approval.Data -Name "blocked_actions") -gt 0) {
        $nextSafeAction = "Resolve blocked approval inbox items before APPLY."
    }
    elseif ($approval.Available -and $null -ne $approval.Data -and (Get-AiOsPropertyCount -Object $approval.Data -Name "pending_approvals") -gt 0) {
        $nextSafeAction = "Review pending approval inbox items before APPLY."
    }
    elseif ($packetRecommendation.Available -and $null -ne $packetRecommendation.Data) {
        $requiredOperatorAction = Get-AiOsPropertyValue -Object $packetRecommendation.Data -Name "required_operator_action" -Default ""
        if (-not [string]::IsNullOrWhiteSpace($requiredOperatorAction)) {
            $nextSafeAction = $requiredOperatorAction
        }
    }

    Write-Host $nextSafeAction -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
}
finally {
    Pop-Location
}
