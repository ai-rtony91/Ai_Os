[CmdletBinding()]
param(
    [string[]]$ChangedPaths = @(),
    [string[]]$BlockedPaths = @(
        "automation/operator",
        "Reports/security",
        "apps/dashboard",
        "automation/telemetry",
        "Reports/telemetry"
    )
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

function Test-AIOSBlockedPath {
    [CmdletBinding()]
    param(
        [string[]]$ChangedPaths = @(),
        [string[]]$BlockedPaths = @(
            "automation/operator",
            "Reports/security",
            "apps/dashboard",
            "automation/telemetry",
            "Reports/telemetry"
        )
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $status = "PASS"

    if ($ChangedPaths.Count -eq 0) {
        $status = "REVIEW_REQUIRED"
        $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "No changed paths were supplied for blocked-path validation." }) | Out-Null
    }

    foreach ($path in $ChangedPaths) {
        if (Test-AIOSPathPrefix -Path $path -Prefixes $BlockedPaths) {
            $status = "BLOCKED"
            $findings.Add([pscustomobject]@{ status = "BLOCKED"; message = "Path matches a blocked path: $path" }) | Out-Null
        }
        else {
            $findings.Add([pscustomobject]@{ status = "PASS"; message = "Path does not match blocked paths: $path" }) | Out-Null
        }
    }

    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "blocked_path"
        stage = "pre_apply"
        status = $status
        findings = $findings.ToArray()
        checked_paths = $ChangedPaths
        blocked_actions = @("modify_blocked_paths", "stage_files", "commit", "push")
        next_safe_action = "Remove blocked paths from the package before continuing."
    }
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSBlockedPath -ChangedPaths $ChangedPaths -BlockedPaths $BlockedPaths | ConvertTo-Json -Depth 8
}
