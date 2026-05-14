[CmdletBinding()]
param(
    [string[]]$ApprovedPaths = @("automation/dispatcher/runtime/validators"),
    [string[]]$KnownIsolatedPaths = @("automation/operator", "Reports/security")
)

$ErrorActionPreference = "Stop"

function Test-AIOSPathPrefix {
    param([string]$Path, [string[]]$Prefixes)
    $normalized = ($Path -replace "\\", "/").TrimStart("/")
    foreach ($prefix in $Prefixes) {
        $normalizedPrefix = ($prefix -replace "\\", "/").TrimEnd("/")
        if ($normalized -eq $normalizedPrefix -or $normalized.StartsWith("$normalizedPrefix/")) {
            return $true
        }
    }
    return $false
}

function Get-AIOSGitStatusPaths {
    $lines = & git status --short --branch --untracked-files=all
    if ($LASTEXITCODE -ne 0) {
        throw "git status --short --branch failed."
    }

    foreach ($line in $lines) {
        if ($line -like "##*") { continue }
        if ($line.Length -lt 4) { continue }
        [pscustomobject]@{
            raw = $line
            code = $line.Substring(0, 2)
            path = $line.Substring(3).Trim()
        }
    }
}

function Test-AIOSDirtyRepo {
    [CmdletBinding()]
    param(
        [string[]]$ApprovedPaths = @("automation/dispatcher/runtime/validators"),
        [string[]]$KnownIsolatedPaths = @("automation/operator", "Reports/security")
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $checked = New-Object System.Collections.Generic.List[string]
    $status = "PASS"

    try {
        $statusRows = @(Get-AIOSGitStatusPaths)
    }
    catch {
        return [pscustomobject]@{
            schema = "AIOS_VALIDATOR_RESULT.v1"
            validator = "dirty_repo"
            stage = "pre_commit_package"
            status = "FAIL"
            findings = @([pscustomobject]@{ status = "FAIL"; message = $_.Exception.Message })
            checked_paths = @()
            blocked_actions = @("stage_files", "commit", "push")
            next_safe_action = "Fix git status access before commit packaging."
        }
    }

    foreach ($row in $statusRows) {
        $checked.Add($row.path) | Out-Null
        if (Test-AIOSPathPrefix -Path $row.path -Prefixes $ApprovedPaths) {
            if ($status -eq "PASS") { $status = "REVIEW_REQUIRED" }
            $findings.Add([pscustomobject]@{
                status = "REVIEW_REQUIRED"
                message = "Dirty approved-path file must be reviewed before staging: $($row.path)"
            }) | Out-Null
        }
        elseif (Test-AIOSPathPrefix -Path $row.path -Prefixes $KnownIsolatedPaths) {
            if ($status -ne "BLOCKED") { $status = "REVIEW_REQUIRED" }
            $findings.Add([pscustomobject]@{
                status = "REVIEW_REQUIRED"
                message = "Known isolated dirty path must stay out of this package: $($row.path)"
            }) | Out-Null
        }
        else {
            $status = "REVIEW_REQUIRED"
            $findings.Add([pscustomobject]@{
                status = "REVIEW_REQUIRED"
                message = "Unclassified dirty path requires review: $($row.path)"
            }) | Out-Null
        }
    }

    if ($statusRows.Count -eq 0) {
        $findings.Add([pscustomobject]@{ status = "PASS"; message = "Repository has no modified or untracked files." }) | Out-Null
    }

    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "dirty_repo"
        stage = "pre_commit_package"
        status = $status
        findings = $findings.ToArray()
        checked_paths = $checked.ToArray()
        blocked_actions = @("stage_unreviewed_files", "commit", "push")
        next_safe_action = "Review dirty repo state and stage exact approved files only after human approval."
    }
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSDirtyRepo -ApprovedPaths $ApprovedPaths -KnownIsolatedPaths $KnownIsolatedPaths | ConvertTo-Json -Depth 8
}
