param(
    [string]$BaseBranch = "main",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-AiOsGit {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        Output = @($output | ForEach-Object { [string]$_ })
        ExitCode = $exitCode
    }
}

function Get-CleanGitLines {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -notmatch "^warning:" -and -not [string]::IsNullOrWhiteSpace($_) })
}

function Get-GitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -match "^warning:" })
}

function ConvertTo-AiOsPathKey {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    $key = $Path.Replace("\", "/").Trim()
    while ($key.StartsWith("./")) {
        $key = $key.Substring(2)
    }
    return $key.TrimEnd("/")
}

function Test-AiOsPathStartsWith {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Prefix
    )

    $pathKey = ConvertTo-AiOsPathKey -Path $Path
    $prefixKey = (ConvertTo-AiOsPathKey -Path $Prefix).TrimEnd("/")
    return ($pathKey -eq $prefixKey -or $pathKey.StartsWith("$prefixKey/"))
}

$protectedPaths = @(
    ".codex_backups/",
    ".git/",
    "apps/dashboard/assets/",
    "broker/",
    "live_trading/",
    "oanda/",
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

$branchResult = Invoke-AiOsGit -Arguments @("branch", "--show-current")
$statusResult = Invoke-AiOsGit -Arguments @("status", "--short")
$headResult = Invoke-AiOsGit -Arguments @("rev-parse", "--short", "HEAD")
$baseResult = Invoke-AiOsGit -Arguments @("rev-parse", "--short", $BaseBranch)
$mergeBaseResult = Invoke-AiOsGit -Arguments @("merge-base", "HEAD", $BaseBranch)
$changedAgainstBaseResult = Invoke-AiOsGit -Arguments @("diff", "--name-only", "$BaseBranch...HEAD")
$diffCheckResult = Invoke-AiOsGit -Arguments @("diff", "--check")

$currentBranchLines = @(Get-CleanGitLines -Lines $branchResult.Output)
$currentBranch = if ($currentBranchLines.Count -gt 0) { $currentBranchLines[0] } else { "UNKNOWN" }
$statusLines = @(Get-CleanGitLines -Lines $statusResult.Output)
$headLines = @(Get-CleanGitLines -Lines $headResult.Output)
$baseLines = @(Get-CleanGitLines -Lines $baseResult.Output)
$mergeBaseLines = @(Get-CleanGitLines -Lines $mergeBaseResult.Output)
$changedAgainstBase = @(Get-CleanGitLines -Lines $changedAgainstBaseResult.Output | ForEach-Object { ConvertTo-AiOsPathKey -Path $_ })

$gitWarnings = @(
    @(
        Get-GitWarnings -Lines $branchResult.Output
        Get-GitWarnings -Lines $statusResult.Output
        Get-GitWarnings -Lines $headResult.Output
        Get-GitWarnings -Lines $baseResult.Output
        Get-GitWarnings -Lines $mergeBaseResult.Output
        Get-GitWarnings -Lines $changedAgainstBaseResult.Output
        Get-GitWarnings -Lines $diffCheckResult.Output
    ) | Sort-Object -Unique
)

$dirtyFiles = @()
foreach ($line in $statusLines) {
    if ($line.Length -ge 4) {
        $dirtyFiles += [pscustomobject]@{
            status = $line.Substring(0, 2)
            path = ConvertTo-AiOsPathKey -Path $line.Substring(3)
        }
    }
}

$protectedHits = @()
foreach ($path in @($dirtyFiles.path + $changedAgainstBase | Sort-Object -Unique)) {
    foreach ($protectedPath in $protectedPaths) {
        if (Test-AiOsPathStartsWith -Path $path -Prefix $protectedPath) {
            $protectedHits += [pscustomobject]@{
                path = $path
                reason = "Protected path: $protectedPath"
            }
        }
    }

    if ($protectedRootFiles -contains $path) {
        $protectedHits += [pscustomobject]@{
            path = $path
            reason = "Protected root governance file."
        }
    }
}

$risks = @()
if ($currentBranch -eq $BaseBranch) {
    $risks += "Current branch is the base branch. Do not open or merge a PR from this branch."
}
if ($statusLines.Count -gt 0) {
    $risks += "Worktree has dirty or untracked files."
}
if ($baseResult.ExitCode -ne 0) {
    $risks += "Base branch could not be resolved locally: $BaseBranch."
}
if ($mergeBaseResult.ExitCode -ne 0) {
    $risks += "Merge base could not be calculated against $BaseBranch."
}
if ($diffCheckResult.ExitCode -ne 0) {
    $risks += "git diff --check failed."
}
if ($protectedHits.Count -gt 0) {
    $risks += "Changed or dirty files include protected paths."
}
if ($changedAgainstBase.Count -eq 0 -and $currentBranch -ne $BaseBranch) {
    $risks += "No changed files were found against base. PR may be empty or base comparison may be unavailable."
}

$overallStatus = "READY"
if ($risks.Count -gt 0) {
    $overallStatus = "REVIEW_REQUIRED"
}
if ($currentBranch -eq $BaseBranch -or $diffCheckResult.ExitCode -ne 0 -or $protectedHits.Count -gt 0) {
    $overallStatus = "BLOCKED"
}

$result = [pscustomobject]@{
    task = "AI_OS merge readiness report"
    mode = "READ_ONLY"
    overall_status = $overallStatus
    current_branch = $currentBranch
    base_branch = $BaseBranch
    head_short_sha = if ($headLines.Count -gt 0) { $headLines[0] } else { "UNKNOWN" }
    base_short_sha = if ($baseLines.Count -gt 0) { $baseLines[0] } else { "UNKNOWN" }
    merge_base_sha = if ($mergeBaseLines.Count -gt 0) { $mergeBaseLines[0] } else { "UNKNOWN" }
    git_status = if ($statusLines.Count -eq 0) { "clean" } else { "dirty" }
    dirty_files = $dirtyFiles
    changed_files_against_base = $changedAgainstBase
    protected_hits = $protectedHits
    diff_check = if ($diffCheckResult.ExitCode -eq 0) { "PASS" } else { "FAIL" }
    risks = $risks
    git_warnings = $gitWarnings
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        merge_performed = "NO"
        runtime_edits = "NO"
        dashboard_edits = "NO"
        policy_edits = "NO"
        telemetry_edits = "NO"
    }
    next_safe_action = if ($overallStatus -eq "READY") { "Run project validators, confirm CI, then request explicit PR or merge approval." } elseif ($overallStatus -eq "REVIEW_REQUIRED") { "Review risks before PR or merge approval." } else { "Stop. Resolve blockers before PR or merge approval." }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Merge Readiness"
Write-Host "Mode: READ_ONLY"
Write-Host "Status: $overallStatus"
Write-Host "Branch: $currentBranch"
Write-Host "Base: $BaseBranch"
Write-Host "Git status: $($result.git_status)"
Write-Host "Diff check: $($result.diff_check)"
Write-Host "Changed files against base: $($changedAgainstBase.Count)"
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

Write-Host "Protected hits:"
if ($protectedHits.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($hit in $protectedHits) {
        Write-Host "  - $($hit.path): $($hit.reason)"
    }
}
Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Merge performed: NO"
Write-Host "Next safe action: $($result.next_safe_action)"
