param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-CommandText {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & $Command @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        Output = @($output | ForEach-Object { [string]$_ })
        ExitCode = $exitCode
    }
}

function Invoke-GitText {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    return Invoke-CommandText -Command "git" -Arguments $Arguments
}

function Remove-GitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -notmatch "^warning:" })
}

function Get-GitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -match "^warning:" })
}

function Get-FirstCleanLine {
    param([string[]]$Lines)

    $cleanLines = @(Remove-GitWarnings -Lines $Lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($cleanLines.Count -eq 0) {
        return "UNKNOWN"
    }

    return $cleanLines[0].Trim()
}

function ConvertFrom-GitRemoteUrl {
    param([string]$RemoteUrl)

    if ([string]::IsNullOrWhiteSpace($RemoteUrl) -or $RemoteUrl -eq "UNKNOWN") {
        return [pscustomobject]@{
            owner = "UNKNOWN"
            name = "UNKNOWN"
            remote_url_available = $false
        }
    }

    $clean = $RemoteUrl.Trim()
    if ($clean -match "github\.com[:/](?<owner>[^/]+)/(?<repo>[^/]+?)(\.git)?$") {
        return [pscustomobject]@{
            owner = $Matches.owner
            name = $Matches.repo
            remote_url_available = $true
        }
    }

    return [pscustomobject]@{
        owner = "UNKNOWN"
        name = "UNKNOWN"
        remote_url_available = $true
    }
}

function Convert-CheckRuns {
    param($ApiObject)

    if ($null -eq $ApiObject -or $null -eq $ApiObject.check_runs) {
        return @()
    }

    return @($ApiObject.check_runs | ForEach-Object {
        [pscustomobject]@{
            name = [string]$_.name
            status = [string]$_.status
            conclusion = if ($null -eq $_.conclusion) { "UNKNOWN" } else { [string]$_.conclusion }
            html_url = if ($null -eq $_.html_url) { "" } else { [string]$_.html_url }
        }
    })
}

$branchResult = Invoke-GitText -Arguments @("branch", "--show-current")
$headResult = Invoke-GitText -Arguments @("rev-parse", "HEAD")
$headShortResult = Invoke-GitText -Arguments @("rev-parse", "--short", "HEAD")
$originMainResult = Invoke-GitText -Arguments @("rev-parse", "--short", "origin/main")
$remoteResult = Invoke-GitText -Arguments @("remote", "get-url", "origin")

$gitWarnings = @(
    @(
        Get-GitWarnings -Lines $branchResult.Output
        Get-GitWarnings -Lines $headResult.Output
        Get-GitWarnings -Lines $originMainResult.Output
        Get-GitWarnings -Lines $remoteResult.Output
    ) | Sort-Object -Unique
)

$currentBranch = Get-FirstCleanLine -Lines $branchResult.Output
$currentCommitSha = Get-FirstCleanLine -Lines $headResult.Output
$currentCommitShortSha = Get-FirstCleanLine -Lines $headShortResult.Output
$originMainSha = if ($originMainResult.ExitCode -eq 0) { Get-FirstCleanLine -Lines $originMainResult.Output } else { "UNKNOWN" }
$remoteUrl = if ($remoteResult.ExitCode -eq 0) { Get-FirstCleanLine -Lines $remoteResult.Output } else { "UNKNOWN" }
$repo = ConvertFrom-GitRemoteUrl -RemoteUrl $remoteUrl

$ghCommand = Get-Command gh -ErrorAction SilentlyContinue
$ghExists = $null -ne $ghCommand
$ghAuthStatus = "UNAVAILABLE"
$checksQueryStatus = "SKIPPED"
$checks = @()
$risks = @()
$fallbackMessage = ""

if (-not $ghExists) {
    $risks += "GitHub CLI is not installed or not on PATH."
    $fallbackMessage = "GitHub CLI is unavailable. Confirm checks in GitHub UI."
} elseif (-not $repo.remote_url_available -or $repo.owner -eq "UNKNOWN" -or $repo.name -eq "UNKNOWN") {
    $ghAuthStatus = "NOT_CHECKED"
    $checksQueryStatus = "SKIPPED"
    $risks += "Repository owner/name could not be parsed from origin remote."
    $fallbackMessage = "Repository remote could not be parsed. Confirm checks in GitHub UI."
} else {
    $authResult = Invoke-CommandText -Command "gh" -Arguments @("auth", "status", "--hostname", "github.com")
    if ($authResult.ExitCode -eq 0) {
        $ghAuthStatus = "PASS"
        $apiPath = "repos/$($repo.owner)/$($repo.name)/commits/$currentCommitSha/check-runs"
        $apiResult = Invoke-CommandText -Command "gh" -Arguments @("api", $apiPath)

        if ($apiResult.ExitCode -eq 0) {
            try {
                $apiObject = ($apiResult.Output -join "`n") | ConvertFrom-Json
                $checks = @(Convert-CheckRuns -ApiObject $apiObject)
                $checksQueryStatus = "PASS"
                if ($checks.Count -eq 0) {
                    $risks += "GitHub returned zero check runs for the current commit."
                    $fallbackMessage = "No check runs were returned. Confirm whether this repo uses required status checks."
                }
            } catch {
                $checksQueryStatus = "FAILED"
                $risks += "GitHub check run response could not be parsed as JSON."
                $fallbackMessage = "GitHub check response was unreadable. Confirm checks in GitHub UI."
            }
        } else {
            $checksQueryStatus = "FAILED"
            $risks += "GitHub check run query failed or was unavailable."
            $fallbackMessage = "GitHub checks are unavailable from this machine. Confirm checks in GitHub UI."
        }
    } else {
        $ghAuthStatus = "FAILED"
        $checksQueryStatus = "SKIPPED"
        $risks += "GitHub CLI auth status failed or is unavailable."
        $fallbackMessage = "GitHub CLI auth is unavailable. Run gh auth status manually or confirm checks in GitHub UI."
    }
}

$passCount = @($checks | Where-Object { $_.status -eq "completed" -and $_.conclusion -eq "success" }).Count
$failCount = @($checks | Where-Object { $_.status -eq "completed" -and $_.conclusion -notin @("success", "neutral", "skipped") }).Count
$pendingCount = @($checks | Where-Object { $_.status -ne "completed" }).Count
$unknownCount = @($checks | Where-Object { [string]::IsNullOrWhiteSpace($_.status) -or $_.conclusion -eq "UNKNOWN" }).Count

$resultStatus = "PASS"
if (-not $ghExists -or $ghAuthStatus -eq "FAILED" -or $repo.owner -eq "UNKNOWN") {
    $resultStatus = "BLOCKED"
} elseif ($checksQueryStatus -ne "PASS" -or $failCount -gt 0 -or $pendingCount -gt 0 -or $checks.Count -eq 0) {
    $resultStatus = "REVIEW"
}

$nextSafeAction = "GitHub checks read successfully. Continue only if required checks are passing."
if ($resultStatus -eq "REVIEW") {
    $nextSafeAction = "Review check status in terminal output or GitHub UI before declaring the commit safe."
} elseif ($resultStatus -eq "BLOCKED") {
    $nextSafeAction = "Fix GitHub CLI availability/auth or verify checks manually in GitHub UI."
}

$result = [pscustomobject]@{
    system = "AI_OS"
    task = "Read GitHub status checks for current HEAD"
    mode = "DRY_RUN"
    result = $resultStatus
    current_branch = $currentBranch
    current_commit_sha = $currentCommitSha
    current_commit_short_sha = $currentCommitShortSha
    origin_main_sha = $originMainSha
    repository = [pscustomobject]@{
        remote_url_available = $repo.remote_url_available
        owner = $repo.owner
        name = $repo.name
    }
    github_cli = [pscustomobject]@{
        exists = $ghExists
        auth_status = $ghAuthStatus
        checks_query_status = $checksQueryStatus
    }
    checks = $checks
    summary = [pscustomobject]@{
        check_count = $checks.Count
        pass_count = $passCount
        fail_count = $failCount
        pending_count = $pendingCount
        unknown_count = $unknownCount
    }
    risks = $risks
    fallback_message = $fallbackMessage
    git_warnings = $gitWarnings
    safety = [pscustomobject]@{
        tokens_printed = "NO"
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        dispatcher_edits = "NO"
        runtime_integration = "NO"
        dashboard_edits = "NO"
    }
    validator_friendly = $true
    next_safe_action = $nextSafeAction
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS GitHub Status Check Reader"
Write-Host "Mode: DRY_RUN"
Write-Host "Result: $resultStatus"
Write-Host "Branch: $currentBranch"
Write-Host "Commit: $currentCommitShortSha"
Write-Host "origin/main: $originMainSha"
Write-Host "Repository: $($repo.owner)/$($repo.name)"
Write-Host "gh CLI exists: $ghExists"
Write-Host "gh auth status: $ghAuthStatus"
Write-Host "Checks query: $checksQueryStatus"
Write-Host ""

Write-Host "Checks:"
if ($checks.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($check in $checks) {
        Write-Host "  - $($check.name): status=$($check.status), conclusion=$($check.conclusion)"
    }
}
Write-Host ""

Write-Host "Risks:"
if ($risks.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($risk in $risks) {
        Write-Host "  - $risk"
    }
}
Write-Host ""

Write-Host "Fallback:"
if ([string]::IsNullOrWhiteSpace($fallbackMessage)) {
    Write-Host "  NONE"
} else {
    Write-Host "  $fallbackMessage"
}
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

Write-Host "Validator note: no tokens printed. No files changed. No commit or push was run."
Write-Host "Next safe action: $nextSafeAction"
