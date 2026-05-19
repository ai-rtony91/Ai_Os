[CmdletBinding()]
param(
    [string[]]$EvidencePath = @(),
    [string]$OutputJsonPath = ""
)

$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }

    return $root.Trim()
}

function Add-AiOsCheck {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$CheckId,
        [ValidateSet("PASS", "WARN", "FAIL")][string]$Result,
        [string]$Message,
        [string[]]$Evidence = @(),
        [string]$NextSafeAction = "Review this compliance result before approving APPLY, commit, or push."
    )

    $Checks.Add([pscustomobject]@{
        check_id = $CheckId
        result = $Result
        message = $Message
        evidence = @($Evidence)
        next_safe_action = $NextSafeAction
    }) | Out-Null
}

function Get-AiOsEvidenceFiles {
    param([string[]]$Paths)

    $files = New-Object System.Collections.Generic.List[string]

    foreach ($path in $Paths) {
        if ([string]::IsNullOrWhiteSpace($path)) {
            continue
        }

        $resolved = Resolve-Path -LiteralPath $path -ErrorAction SilentlyContinue
        if ($null -eq $resolved) {
            continue
        }

        foreach ($item in @($resolved)) {
            if (Test-Path -LiteralPath $item.Path -PathType Leaf) {
                $files.Add($item.Path) | Out-Null
                continue
            }

            if (Test-Path -LiteralPath $item.Path -PathType Container) {
                Get-ChildItem -LiteralPath $item.Path -Recurse -File -Include *.md,*.txt,*.json,*.log |
                    ForEach-Object { $files.Add($_.FullName) | Out-Null }
            }
        }
    }

    return @($files | Select-Object -Unique)
}

function Test-AiOsContentPattern {
    param(
        [string[]]$Files,
        [string]$Pattern
    )

    if ($Files.Count -eq 0) {
        return @()
    }

    return @(
        Select-String -LiteralPath $Files -Pattern $Pattern -CaseSensitive:$false -ErrorAction SilentlyContinue |
            ForEach-Object { "{0}:{1}: {2}" -f $_.Path, $_.LineNumber, $_.Line.Trim() }
    )
}

$repoRoot = Get-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$checks = [System.Collections.Generic.List[object]]::new()
$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$evidenceFiles = Get-AiOsEvidenceFiles -Paths $EvidencePath

Write-Host "AI_OS Agent Compliance Checker"
Write-Host "Mode: DRY_RUN"
Write-Host "Repo: $repoRoot"
Write-Host "Evidence files inspected: $($evidenceFiles.Count)"
Write-Host ""

if ($EvidencePath.Count -eq 0) {
    Add-AiOsCheck -Checks $checks -CheckId "evidence_path_supplied" -Result "WARN" -Message "No evidence path was supplied. Content checks are limited." -NextSafeAction "Run again with -EvidencePath pointing to worker reports, command logs, or packet output."
}
elseif ($evidenceFiles.Count -eq 0) {
    Add-AiOsCheck -Checks $checks -CheckId "evidence_files_found" -Result "WARN" -Message "Evidence paths were supplied, but no readable evidence files were found." -Evidence $EvidencePath -NextSafeAction "Confirm the worker report or log path, then rerun this DRY_RUN checker."
}
else {
    Add-AiOsCheck -Checks $checks -CheckId "evidence_files_found" -Result "PASS" -Message "Evidence files were found for compliance scanning." -Evidence $evidenceFiles -NextSafeAction "Review individual compliance checks below."
}

$gitAddDotMatches = Test-AiOsContentPattern -Files $evidenceFiles -Pattern "(^|\s)git\s+add\s+\.(\s|$)"
if ($gitAddDotMatches.Count -gt 0) {
    Add-AiOsCheck -Checks $checks -CheckId "git_add_dot_detection" -Result "FAIL" -Message "Evidence contains git add . usage or instruction." -Evidence $gitAddDotMatches -NextSafeAction "Stop commit preparation and replace with exact-file staging only after approval."
}
else {
    Add-AiOsCheck -Checks $checks -CheckId "git_add_dot_detection" -Result "PASS" -Message "No git add . usage was detected in supplied evidence."
}

$pushMatches = Test-AiOsContentPattern -Files $evidenceFiles -Pattern "git\s+push"
$approvedPushMatches = @($pushMatches | Where-Object { $_ -match "(?i)(approved|approval|explicit)" })
if ($pushMatches.Count -gt 0 -and $approvedPushMatches.Count -eq 0) {
    Add-AiOsCheck -Checks $checks -CheckId "unauthorized_push_detection" -Result "FAIL" -Message "Evidence mentions git push without nearby approval language." -Evidence $pushMatches -NextSafeAction "Do not push. Request explicit push approval with exact branch and commit details."
}
elseif ($pushMatches.Count -gt 0) {
    Add-AiOsCheck -Checks $checks -CheckId "unauthorized_push_detection" -Result "WARN" -Message "Evidence mentions git push. Approval language was present, but human review is still required." -Evidence $pushMatches -NextSafeAction "Confirm the push was explicitly approved before proceeding."
}
else {
    Add-AiOsCheck -Checks $checks -CheckId "unauthorized_push_detection" -Result "PASS" -Message "No git push usage was detected in supplied evidence."
}

$modeReportMatches = Test-AiOsContentPattern -Files $evidenceFiles -Pattern "(DRY_RUN|APPLY)"
$requiredReportMatches = Test-AiOsContentPattern -Files $evidenceFiles -Pattern "(Files inspected|Files created|Files changed|Validation result|Dry-run|APPLY result|Errors|Unknowns)"
if ($evidenceFiles.Count -gt 0 -and ($modeReportMatches.Count -eq 0 -or $requiredReportMatches.Count -eq 0)) {
    Add-AiOsCheck -Checks $checks -CheckId "missing_dry_run_apply_report" -Result "FAIL" -Message "Evidence does not show a complete DRY_RUN/APPLY report structure." -NextSafeAction "Ask the worker to provide the required AGENTS.md report fields before approval."
}
else {
    Add-AiOsCheck -Checks $checks -CheckId "missing_dry_run_apply_report" -Result "PASS" -Message "Evidence includes DRY_RUN/APPLY language and report-field language, or no evidence was supplied."
}

$protectedPathPatterns = @(
    "README\.md",
    "RISK_POLICY\.md",
    "SOURCE_LOG\.md",
    "ERROR_LOG\.md",
    "HALLUCINATION_LOG\.md",
    "AAR\.md",
    "DAILY_REPORT\.md",
    "ARCHITECTURE\.md",
    "DEPLOYMENT\.md",
    "WHITEPAPER\.md",
    "\.codex_backups/",
    "apps/dashboard/assets/"
)
$protectedMatches = @()
foreach ($pattern in $protectedPathPatterns) {
    $protectedMatches += Test-AiOsContentPattern -Files $evidenceFiles -Pattern $pattern
}

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$gitStatusLines = @(git status --short 2>$null)
$ErrorActionPreference = $previousErrorActionPreference

$changedFiles = @($gitStatusLines | ForEach-Object {
    if ($_ -match "^\s*$") { return }
    $path = $_.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }
    $path -replace "\\", "/"
})

$protectedChanged = @($changedFiles | Where-Object {
    $_ -match "^(README\.md|RISK_POLICY\.md|SOURCE_LOG\.md|ERROR_LOG\.md|HALLUCINATION_LOG\.md|AAR\.md|DAILY_REPORT\.md|ARCHITECTURE\.md|DEPLOYMENT\.md|WHITEPAPER\.md)$" -or
    $_ -like ".codex_backups/*" -or
    $_ -like "apps/dashboard/assets/*"
})

if ($protectedChanged.Count -gt 0) {
    Add-AiOsCheck -Checks $checks -CheckId "protected_path_violations" -Result "FAIL" -Message "Git status shows protected paths changed." -Evidence $protectedChanged -NextSafeAction "Stop and request explicit protected-path approval before any further action."
}
elseif ($protectedMatches.Count -gt 0) {
    Add-AiOsCheck -Checks $checks -CheckId "protected_path_violations" -Result "WARN" -Message "Evidence mentions protected paths. This may be allowed if it is report-only." -Evidence $protectedMatches -NextSafeAction "Confirm no protected path was edited without explicit approval."
}
else {
    Add-AiOsCheck -Checks $checks -CheckId "protected_path_violations" -Result "PASS" -Message "No protected path violation was detected."
}

$liveViolationMatches = @()
foreach ($pattern in @("OANDA", "broker", "live[_ -]?trading", "API key", "secret", "webhook", "real order")) {
    $liveViolationMatches += Test-AiOsContentPattern -Files $evidenceFiles -Pattern $pattern
}

$liveChanged = @($changedFiles | Where-Object { $_ -match "(?i)(broker|oanda|live[_-]?trading|api[_-]?key|secret|webhook|real[_-]?order|\.env)" })
if ($liveChanged.Count -gt 0) {
    Add-AiOsCheck -Checks $checks -CheckId "broker_live_api_violations" -Result "FAIL" -Message "Git status shows broker/live/API/secret-related paths changed." -Evidence $liveChanged -NextSafeAction "Stop and review the safety boundary before any APPLY, commit, or push."
}
elseif ($liveViolationMatches.Count -gt 0) {
    Add-AiOsCheck -Checks $checks -CheckId "broker_live_api_violations" -Result "WARN" -Message "Evidence mentions broker/live/API/secret terms. This may be safe if it is blocking language only." -Evidence $liveViolationMatches -NextSafeAction "Confirm the evidence is policy/report text only and did not enable execution."
}
else {
    Add-AiOsCheck -Checks $checks -CheckId "broker_live_api_violations" -Result "PASS" -Message "No broker/live/API violation was detected."
}

$validationMatches = Test-AiOsContentPattern -Files $evidenceFiles -Pattern "(Validation result|git diff --check|PASS JSON|validator|validated)"
if ($evidenceFiles.Count -gt 0 -and $validationMatches.Count -eq 0) {
    Add-AiOsCheck -Checks $checks -CheckId "missing_validation_output" -Result "FAIL" -Message "Evidence does not include validation output." -NextSafeAction "Ask the worker to run and report required validators before approval."
}
else {
    Add-AiOsCheck -Checks $checks -CheckId "missing_validation_output" -Result "PASS" -Message "Validation output was found, or no evidence was supplied."
}

$nextSafeActionMatches = Test-AiOsContentPattern -Files $evidenceFiles -Pattern "next safe action"
if ($evidenceFiles.Count -gt 0 -and $nextSafeActionMatches.Count -eq 0) {
    Add-AiOsCheck -Checks $checks -CheckId "missing_next_safe_action" -Result "FAIL" -Message "Evidence does not include next safe action output." -NextSafeAction "Ask the worker to provide the exact next safe action."
}
else {
    Add-AiOsCheck -Checks $checks -CheckId "missing_next_safe_action" -Result "PASS" -Message "Next safe action output was found, or no evidence was supplied."
}

$failCount = @($checks | Where-Object { $_.result -eq "FAIL" }).Count
$warnCount = @($checks | Where-Object { $_.result -eq "WARN" }).Count
$passCount = @($checks | Where-Object { $_.result -eq "PASS" }).Count
$overall = if ($failCount -gt 0) { "FAIL" } elseif ($warnCount -gt 0) { "WARN" } else { "PASS" }

$report = [pscustomobject]@{
    schema = "AIOS_AGENT_COMPLIANCE_REPORT.v1"
    mode = "DRY_RUN"
    generated_at = $generatedAt
    repo_root = $repoRoot
    evidence_paths = @($EvidencePath)
    evidence_files_inspected = @($evidenceFiles)
    overall_result = $overall
    pass_count = $passCount
    warn_count = $warnCount
    fail_count = $failCount
    checks = @($checks)
    files_changed_by_checker = @()
    commit_performed = $false
    push_performed = $false
    next_safe_action = if ($overall -eq "PASS") { "Review compliance output before approving APPLY, commit, or push." } else { "Resolve WARN/FAIL compliance findings before approving APPLY, commit, or push." }
}

Write-Host "Compliance result: $overall"
Write-Host "PASS: $passCount WARN: $warnCount FAIL: $failCount"
Write-Host "Next safe action: $($report.next_safe_action)"
Write-Host ""

$json = $report | ConvertTo-Json -Depth 12

if (-not [string]::IsNullOrWhiteSpace($OutputJsonPath)) {
    Write-Host "OutputJsonPath was supplied, but this scaffold is DRY_RUN only and does not write report files."
    Write-Host "Copy the JSON output only after an approved APPLY workflow exists."
}

$json

if ($overall -eq "FAIL") {
    exit 1
}

exit 0
