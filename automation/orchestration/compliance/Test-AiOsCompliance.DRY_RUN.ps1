[CmdletBinding()]
param(
    [ValidateSet("DRY_RUN", "APPLY", "UNKNOWN")]
    [string]$Mode = "UNKNOWN",
    [string[]]$WorkerReportPath = @(),
    [string[]]$ValidationEvidencePath = @(),
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }

    return $root.Trim()
}

function Invoke-AiOsGitText {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        output = @($output | ForEach-Object { [string]$_ })
        exit_code = $exitCode
    }
}

function ConvertTo-AiOsRepoPath {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    $repoPath = $Path.Replace("\", "/").Trim()
    while ($repoPath.StartsWith("./")) {
        $repoPath = $repoPath.Substring(2)
    }

    return $repoPath
}

function Convert-AiOsStatusLineToEntry {
    param([Parameter(Mandatory = $true)][string]$Line)

    if ($Line.Length -lt 4) {
        return $null
    }

    $statusCode = $Line.Substring(0, 2)
    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return [pscustomobject]@{
        status = $statusCode
        path = ConvertTo-AiOsRepoPath -Path $path
        is_untracked = $statusCode -eq "??"
    }
}

function Test-AiOsPathPatterns {
    param(
        [Parameter(Mandatory = $true)][object]$Path,
        [Parameter(Mandatory = $true)][object]$Patterns
    )

    $repoPath = [string]$Path
    $matches = New-Object System.Collections.Generic.List[object]
    foreach ($pattern in @($Patterns)) {
        if ($repoPath -match $pattern.pattern) {
            $matches.Add([pscustomobject]@{
                pattern = $pattern.pattern
                reason = $pattern.reason
            }) | Out-Null
        }
    }

    return @($matches)
}

function Test-AiOsExistingPath {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $false
    }

    return Test-Path -LiteralPath $Path
}

function Get-AiOsMissingEvidence {
    param(
        [string[]]$Paths,
        [string]$EvidenceType
    )

    $missing = @()

    if ($Paths.Count -eq 0) {
        $missing += [pscustomobject]@{
            evidence_type = $EvidenceType
            path = ""
            reason = "$EvidenceType path was not supplied."
        }
        return @($missing)
    }

    foreach ($path in $Paths) {
        if (-not (Test-AiOsExistingPath -Path $path)) {
            $missing += [pscustomobject]@{
                evidence_type = $EvidenceType
                path = $path
                reason = "$EvidenceType path does not exist or is not readable."
            }
        }
    }

    return @($missing)
}

function New-AiOsPathPattern {
    param(
        [string]$Pattern,
        [string]$Reason
    )

    return [pscustomobject]@{
        pattern = $Pattern
        reason = $Reason
    }
}

$repoRoot = Get-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$blockedPathPatterns = @(
    New-AiOsPathPattern -Pattern "^README\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^RISK_POLICY\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^SOURCE_LOG\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^ERROR_LOG\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^HALLUCINATION_LOG\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^AAR\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^DAILY_REPORT\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^ARCHITECTURE\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^DEPLOYMENT\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^WHITEPAPER\.md$" -Reason "Protected root governance document."
    New-AiOsPathPattern -Pattern "^AGENTS\.md$" -Reason "Protected root agent governance file."
    New-AiOsPathPattern -Pattern "^\.codex_backups/" -Reason "Backups folder is blocked."
    New-AiOsPathPattern -Pattern "^apps/dashboard/assets/" -Reason "Dashboard assets are blocked unless explicitly approved."
    New-AiOsPathPattern -Pattern "(^|/)secrets(/|$)" -Reason "Secrets path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)credentials?(/|$)" -Reason "Credential path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)\.env($|\.)" -Reason ".env files are blocked."
    New-AiOsPathPattern -Pattern "(^|/)broker(/|$)" -Reason "Broker path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)oanda(/|$)" -Reason "OANDA path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)webhooks?(/|$)" -Reason "Webhook path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)live[-_]?trading(/|$)" -Reason "Live-trading path is blocked."
    New-AiOsPathPattern -Pattern "api[-_]?key" -Reason "API key reference is blocked."
    New-AiOsPathPattern -Pattern "real[-_]?order" -Reason "Real-order reference is blocked."
)

$warningPathPatterns = @(
    New-AiOsPathPattern -Pattern "^apps/dashboard/" -Reason "Dashboard work needs explicit scope review."
    New-AiOsPathPattern -Pattern "^services/" -Reason "Service changes need operator review."
    New-AiOsPathPattern -Pattern "^automation/orchestration/approval" -Reason "Approval orchestration changes need operator review."
    New-AiOsPathPattern -Pattern "^automation/orchestration/commit_packages/" -Reason "Commit package logic changes need operator review."
    New-AiOsPathPattern -Pattern "^automation/orchestration/validators/" -Reason "Validator logic changes need operator review."
    New-AiOsPathPattern -Pattern "^Reports/" -Reason "Report changes should be checked for scope and evidence."
)

$statusResult = Invoke-AiOsGitText -Arguments @("status", "--short")
$cachedResult = Invoke-AiOsGitText -Arguments @("diff", "--cached", "--name-only")
$gitWarnings = @(
    @($statusResult.output + $cachedResult.output) |
        Where-Object { $_ -match "^warning:" } |
        Sort-Object -Unique
)
$statusLines = @($statusResult.output | Where-Object {
    $_ -notmatch "^warning:" -and -not [string]::IsNullOrWhiteSpace($_)
})

$statusEntries = @($statusLines | ForEach-Object { Convert-AiOsStatusLineToEntry -Line $_ } | Where-Object { $null -ne $_ })
$changedFiles = @($statusEntries | ForEach-Object { $_.path } | Sort-Object -Unique)
$untrackedFiles = @($statusEntries | Where-Object { $_.is_untracked } | ForEach-Object { $_.path } | Sort-Object -Unique)
$stagedFiles = @($cachedResult.output | Where-Object {
    $_ -notmatch "^warning:" -and -not [string]::IsNullOrWhiteSpace($_)
} | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Sort-Object -Unique)

$blockedFiles = @()
$warningFiles = @()

foreach ($path in $changedFiles) {
    $repoPath = [string]$path
    foreach ($pattern in @($blockedPathPatterns)) {
        if ($repoPath -match $pattern.pattern) {
            $blockedFiles += [pscustomobject]@{
                path = $repoPath
                pattern = $pattern.pattern
                reason = $pattern.reason
            }
        }
    }

    foreach ($pattern in @($warningPathPatterns)) {
        if ($repoPath -match $pattern.pattern) {
            $warningFiles += [pscustomobject]@{
                path = $repoPath
                pattern = $pattern.pattern
                reason = $pattern.reason
            }
        }
    }
}

foreach ($path in $untrackedFiles) {
    $warningFiles += [pscustomobject]@{
        path = $path
        pattern = "untracked_files"
        reason = "Untracked file requires scope review before APPLY, commit, or push."
    }
}

$missingEvidence = @()
foreach ($item in @(Get-AiOsMissingEvidence -Paths $WorkerReportPath -EvidenceType "worker_report")) {
    $missingEvidence += $item
}
foreach ($item in @(Get-AiOsMissingEvidence -Paths $ValidationEvidencePath -EvidenceType "validation_evidence")) {
    $missingEvidence += $item
}
if ($Mode -eq "UNKNOWN") {
    $missingEvidence += [pscustomobject]@{
        evidence_type = "mode"
        path = ""
        reason = "Mode was not supplied as DRY_RUN or APPLY."
    }
}

$warnings = @()
if ($stagedFiles.Count -gt 0) {
    $warnings += [pscustomobject]@{
        check_id = "staged_files"
        message = "Staged files are present. Confirm exact-file staging was approved."
        evidence = @($stagedFiles)
    }
}
if ($gitWarnings.Count -gt 0) {
    $warnings += [pscustomobject]@{
        check_id = "git_warnings"
        message = "Git returned warnings during compliance checks."
        evidence = @($gitWarnings)
    }
}
if ($warningFiles.Count -gt 0) {
    $warnings += [pscustomobject]@{
        check_id = "warning_files"
        message = "One or more changed files match warning patterns."
        evidence = @($warningFiles | ForEach-Object { $_.path } | Sort-Object -Unique)
    }
}
if ($missingEvidence.Count -gt 0) {
    $warnings += [pscustomobject]@{
        check_id = "missing_evidence"
        message = "Required worker, validation, or mode evidence is missing."
        evidence = @($missingEvidence | ForEach-Object { $_.reason })
    }
}

$result = if ($blockedFiles.Count -gt 0) {
    "BLOCKED"
}
elseif ($warnings.Count -gt 0) {
    "REVIEW"
}
else {
    "PASS"
}

$nextSafeAction = switch ($result) {
    "PASS" { "Compliance check passed. Operator may continue with the next approved DRY_RUN or APPLY step. No commit or push is approved by this checker." }
    "REVIEW" { "Review warnings and missing evidence before APPLY, commit, or push. No commit or push is approved." }
    default { "Stop. Resolve blocked file or safety-path findings before APPLY, commit, or push." }
}

$report = [pscustomobject]@{
    schema = "AIOS_COMPLIANCE_CHECK.v1"
    task = "AI_OS general compliance check"
    mode = $Mode
    checker_mode = "DRY_RUN"
    generated_at = $generatedAt
    repo_root = $repoRoot
    result = $result
    changed_files = @($changedFiles)
    staged_files = @($stagedFiles)
    untracked_files = @($untrackedFiles)
    blocked_files = @($blockedFiles)
    warning_files = @($warningFiles)
    warnings = @($warnings)
    missing_evidence = @($missingEvidence)
    blocked_path_patterns = @($blockedPathPatterns)
    warning_path_patterns = @($warningPathPatterns)
    safety = [pscustomobject]@{
        writes_performed = 0
        git_add_performed = "NO"
        commit_performed = "NO"
        push_performed = "NO"
        broker_or_live_api_work = "NO"
        webhook_execution = "NO"
        dashboard_edits = "NO"
    }
    commit_performed = $false
    push_performed = $false
    next_safe_action = $nextSafeAction
}

if ($OutputJson) {
    $report | ConvertTo-Json -Depth 12
}
else {
    Write-Host "AI_OS Compliance Check"
    Write-Host "Mode: $Mode"
    Write-Host "Checker mode: DRY_RUN"
    Write-Host "Result: $result"
    Write-Host ""
    Write-Host "Changed files: $($changedFiles.Count)"
    Write-Host "Staged files: $($stagedFiles.Count)"
    Write-Host "Untracked files: $($untrackedFiles.Count)"
    Write-Host "Blocked files: $($blockedFiles.Count)"
    Write-Host "Warning files: $($warningFiles.Count)"
    Write-Host "Missing evidence: $($missingEvidence.Count)"
    Write-Host ""
    Write-Host "Next safe action: $nextSafeAction"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ""
    $report | ConvertTo-Json -Depth 12
}

if ($result -eq "BLOCKED") {
    exit 1
}

exit 0
