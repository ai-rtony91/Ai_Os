[CmdletBinding()]
param(
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

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4 -or $Line -like "##*") {
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

function New-AiOsPathPattern {
    param(
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Reason
    )

    return [pscustomobject]@{
        pattern = $Pattern
        reason = $Reason
    }
}

function Test-AiOsPathStartsWith {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Prefix
    )

    $repoPath = (ConvertTo-AiOsRepoPath -Path $Path)
    $repoPrefix = (ConvertTo-AiOsRepoPath -Path $Prefix).TrimEnd("/")

    return ($repoPath -eq $repoPrefix -or $repoPath.StartsWith("$repoPrefix/"))
}

function Test-AiOsAnyPathStartsWith {
    param(
        [string[]]$Paths = @(),
        [Parameter(Mandatory = $true)][string]$Prefix
    )

    if ($Paths.Count -eq 0) {
        return $false
    }

    foreach ($path in $Paths) {
        if (Test-AiOsPathStartsWith -Path $path -Prefix $Prefix) {
            return $true
        }
    }

    return $false
}

function Test-AiOsAnyPathMatches {
    param(
        [string[]]$Paths = @(),
        [Parameter(Mandatory = $true)][string]$Pattern
    )

    if ($Paths.Count -eq 0) {
        return $false
    }

    foreach ($path in $Paths) {
        if ($path -match $Pattern) {
            return $true
        }
    }

    return $false
}

function Add-AiOsRecommendation {
    param(
        [System.Collections.Generic.List[object]]$Recommendations,
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string]$Reason,
        [ValidateSet("INFO", "REVIEW", "BLOCKED")]
        [string]$Severity = "REVIEW"
    )

    if (@($Recommendations | Where-Object { $_.id -eq $Id }).Count -gt 0) {
        return
    }

    $Recommendations.Add([pscustomobject]@{
        id = $Id
        label = $Label
        command = $Command
        reason = $Reason
        severity = $Severity
    }) | Out-Null
}

$repoRoot = Get-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$statusResult = Invoke-AiOsGitText -Arguments @("status", "--short")
$gitWarnings = @($statusResult.output | Where-Object { $_ -match "^warning:" } | Sort-Object -Unique)
$statusLines = @($statusResult.output | Where-Object {
    $_ -notmatch "^warning:" -and -not [string]::IsNullOrWhiteSpace($_)
})

$statusEntries = @($statusLines | ForEach-Object { Convert-AiOsStatusLineToEntry -Line $_ } | Where-Object { $null -ne $_ })
$changedPaths = @($statusEntries | ForEach-Object { $_.path } | Sort-Object -Unique)
$untrackedPaths = @($statusEntries | Where-Object { $_.is_untracked } | ForEach-Object { $_.path } | Sort-Object -Unique)
$trackedChangedPaths = @($statusEntries | Where-Object { -not $_.is_untracked } | ForEach-Object { $_.path } | Sort-Object -Unique)

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
    New-AiOsPathPattern -Pattern "(^|/)secrets?(/|$)" -Reason "Secrets path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)credentials?(/|$)" -Reason "Credential path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)\.env($|\.)" -Reason ".env files are blocked."
    New-AiOsPathPattern -Pattern "(^|/)broker(/|$)" -Reason "Broker path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)oanda(/|$)" -Reason "OANDA path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)webhooks?(/|$)" -Reason "Webhook path is blocked."
    New-AiOsPathPattern -Pattern "(^|/)live[-_]?trading(/|$)" -Reason "Live-trading path is blocked."
    New-AiOsPathPattern -Pattern "api[-_]?key" -Reason "API key reference is blocked."
    New-AiOsPathPattern -Pattern "real[-_]?order" -Reason "Real-order reference is blocked."
)

$reviewPathPatterns = @(
    New-AiOsPathPattern -Pattern "^apps/dashboard/" -Reason "Dashboard path changed; confirm explicit UI scope."
    New-AiOsPathPattern -Pattern "^automation/orchestration/approval" -Reason "Approval orchestration changed; operator review required."
    New-AiOsPathPattern -Pattern "^automation/orchestration/commit_packages/" -Reason "Commit package recommendation logic changed."
    New-AiOsPathPattern -Pattern "^automation/orchestration/compliance/" -Reason "Compliance checker changed."
    New-AiOsPathPattern -Pattern "^automation/orchestration/validators/" -Reason "Validator logic changed."
    New-AiOsPathPattern -Pattern "^Reports/" -Reason "Report path changed; confirm evidence scope."
)

$blockedFindings = @()
$reviewFindings = @()
foreach ($path in $changedPaths) {
    foreach ($pattern in $blockedPathPatterns) {
        if ($path -match $pattern.pattern) {
            $blockedFindings += [pscustomobject]@{
                path = $path
                pattern = $pattern.pattern
                reason = $pattern.reason
            }
        }
    }

    foreach ($pattern in $reviewPathPatterns) {
        if ($path -match $pattern.pattern) {
            $reviewFindings += [pscustomobject]@{
                path = $path
                pattern = $pattern.pattern
                reason = $pattern.reason
            }
        }
    }
}

$recommendations = [System.Collections.Generic.List[object]]::new()
$psPaths = @($changedPaths | Where-Object { $_ -like "*.ps1" })
$jsonPaths = @($changedPaths | Where-Object { $_ -like "*.json" })
$markdownPaths = @($changedPaths | Where-Object { $_ -like "*.md" })

if ($statusResult.exit_code -ne 0) {
    $blockedFindings += [pscustomobject]@{
        path = "WORKTREE"
        pattern = "git_status"
        reason = "git status --short failed."
    }
}

if ($changedPaths.Count -eq 0) {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "optional_health_summary" -Label "Optional orchestration health summary" -Command "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1 -OutputJson" -Reason "No changed files detected; optional health check can confirm orchestration status." -Severity "INFO"
}

if ($psPaths.Count -gt 0) {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "powershell_syntax" -Label "PowerShell syntax validation" -Command "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1" -Reason "Changed PowerShell files should parse before any APPLY, commit, or push." -Severity "REVIEW"
}

if ($jsonPaths.Count -gt 0) {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "json_integrity" -Label "JSON parse validation" -Command "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1" -Reason "Changed JSON files should parse before any APPLY, commit, or push." -Severity "REVIEW"
}

if ($markdownPaths.Count -gt 0) {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "markdown_review" -Label "Markdown scope review" -Command "git diff --check" -Reason "Changed Markdown should be checked for whitespace and scoped review." -Severity "REVIEW"
}

if (Test-AiOsAnyPathStartsWith -Paths $changedPaths -Prefix "automation/orchestration/validators/") {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "validator_chain_config" -Label "Validator chain config check" -Command "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-ValidatorChainConfig.DRY_RUN.ps1" -Reason "Validator-area changes should verify the validator chain configuration." -Severity "REVIEW"
    Add-AiOsRecommendation -Recommendations $recommendations -Id "validator_chain" -Label "Validator chain run" -Command "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1" -Reason "Validator-area changes should run the read-only validator chain." -Severity "REVIEW"
}

if (Test-AiOsAnyPathStartsWith -Paths $changedPaths -Prefix "automation/orchestration/") {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "operator_control_loop" -Label "Operator control loop check" -Command "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1 -OutputJson" -Reason "Orchestration changes should be checked by the operator control loop." -Severity "REVIEW"
}

if (
    $blockedFindings.Count -gt 0 -or
    (Test-AiOsAnyPathStartsWith -Paths $changedPaths -Prefix "automation/orchestration/compliance/") -or
    (Test-AiOsAnyPathMatches -Paths $changedPaths -Pattern "(?i)(secret|credential|token|api[-_]?key|private[-_]?key|\.env|broker|oanda|webhook|live[-_]?trading|real[-_]?order)")
) {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "compliance_check" -Label "Compliance checker" -Command "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/compliance/Test-AiOsCompliance.DRY_RUN.ps1 -Mode DRY_RUN -OutputJson" -Reason "Protected, compliance, or sensitive path changes require compliance review." -Severity "BLOCKED"
}
elseif ($reviewFindings.Count -gt 0 -or $untrackedPaths.Count -gt 0) {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "compliance_check" -Label "Compliance checker" -Command "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/compliance/Test-AiOsCompliance.DRY_RUN.ps1 -Mode DRY_RUN -OutputJson" -Reason "Review findings or untracked files require compliance review." -Severity "REVIEW"
}

if ($changedPaths.Count -gt 0) {
    Add-AiOsRecommendation -Recommendations $recommendations -Id "diff_check" -Label "Git diff whitespace check" -Command "git diff --check" -Reason "Changed files should pass git diff whitespace validation." -Severity "REVIEW"
}

$result = if ($blockedFindings.Count -gt 0 -or @($recommendations | Where-Object { $_.severity -eq "BLOCKED" }).Count -gt 0) {
    "BLOCKED"
}
elseif ($changedPaths.Count -gt 0 -or $reviewFindings.Count -gt 0 -or $gitWarnings.Count -gt 0) {
    "REVIEW"
}
else {
    "PASS"
}

$nextSafeAction = switch ($result) {
    "PASS" { "No changed files require validation. Continue with the next approved DRY_RUN step." }
    "REVIEW" { "Run the recommended validation commands and review results before APPLY, commit, or push." }
    default { "Stop. Run compliance review and resolve blocked findings before APPLY, commit, or push." }
}

$report = [pscustomobject]@{
    schema = "AIOS_VALIDATOR_RECOMMENDATION.v1"
    task = "Recommend AI_OS validators from changed files"
    mode = "DRY_RUN"
    execution_enabled = $false
    generated_at = $generatedAt
    repo_root = $repoRoot
    result = $result
    summary = [pscustomobject]@{
        changed_file_count = $changedPaths.Count
        tracked_changed_file_count = $trackedChangedPaths.Count
        untracked_file_count = $untrackedPaths.Count
        powershell_file_count = $psPaths.Count
        json_file_count = $jsonPaths.Count
        markdown_file_count = $markdownPaths.Count
        recommendation_count = $recommendations.Count
        blocked_finding_count = $blockedFindings.Count
        review_finding_count = $reviewFindings.Count
    }
    changed_paths = @($changedPaths)
    tracked_changed_paths = @($trackedChangedPaths)
    untracked_paths = @($untrackedPaths)
    blocked_findings = @($blockedFindings)
    review_findings = @($reviewFindings)
    recommendations = @($recommendations)
    recommended_commands = @($recommendations | ForEach-Object { $_.command } | Sort-Object -Unique)
    git_warnings = @($gitWarnings)
    safety = [pscustomobject]@{
        writes_performed = 0
        git_add_performed = "NO"
        commit_performed = "NO"
        push_performed = "NO"
        dashboard_edits = "NO"
        broker_oanda_api_webhook_live_trading = "NO"
    }
    commit_performed = $false
    push_performed = $false
    validator_friendly = $true
    next_safe_action = $nextSafeAction
}

if ($OutputJson) {
    $report | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Validator Recommendation"
Write-Host "Mode: DRY_RUN"
Write-Host "Result: $result"
Write-Host ""
Write-Host "Changed files: $($changedPaths.Count)"
Write-Host "Tracked changed files: $($trackedChangedPaths.Count)"
Write-Host "Untracked files: $($untrackedPaths.Count)"
Write-Host "Recommendations: $($recommendations.Count)"
Write-Host "Blocked findings: $($blockedFindings.Count)"
Write-Host "Review findings: $($reviewFindings.Count)"
Write-Host ""

Write-Host "Recommended commands:"
if ($recommendations.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($recommendation in $recommendations) {
        Write-Host "  - $($recommendation.command)"
        Write-Host "    Reason: $($recommendation.reason)"
    }
}
Write-Host ""

Write-Host "Blocked findings:"
if ($blockedFindings.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($finding in $blockedFindings) {
        Write-Host "  - $($finding.path): $($finding.reason)"
    }
}
Write-Host ""

Write-Host "Review findings:"
if ($reviewFindings.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($finding in $reviewFindings) {
        Write-Host "  - $($finding.path): $($finding.reason)"
    }
}
Write-Host ""

Write-Host "Git warnings:"
if ($gitWarnings.Count -eq 0) {
    Write-Host "  NONE"
}
else {
    foreach ($warning in $gitWarnings) {
        Write-Host "  - $warning"
    }
}
Write-Host ""

Write-Host "Next safe action: $nextSafeAction"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
