[CmdletBinding()]
param(
    [string[]]$ChangedPaths = @(),
    [string[]]$AllowedPaths = @("automation/dispatcher/runtime/validators")
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

function New-AIOSAllowedPathResult {
    param([string]$Status, [object[]]$Findings, [string[]]$CheckedPaths)
    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "allowed_path"
        stage = "pre_apply"
        status = $Status
        findings = $Findings
        checked_paths = $CheckedPaths
        blocked_actions = @("modify_outside_allowed_paths", "stage_files", "commit", "push")
        next_safe_action = "Keep changes inside the approved allowed paths before APPLY or commit packaging."
    }
}

function Test-AIOSAllowedPath {
    [CmdletBinding()]
    param(
        [string[]]$ChangedPaths = @(),
        [string[]]$AllowedPaths = @("automation/dispatcher/runtime/validators")
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $status = "PASS"

    if ($ChangedPaths.Count -eq 0) {
        return New-AIOSAllowedPathResult -Status "REVIEW_REQUIRED" -Findings @([pscustomobject]@{
            status = "REVIEW_REQUIRED"
            message = "No changed paths were supplied for allowed-path validation."
        }) -CheckedPaths @()
    }

    foreach ($path in $ChangedPaths) {
        if (Test-AIOSPathPrefix -Path $path -Prefixes $AllowedPaths) {
            $findings.Add([pscustomobject]@{ status = "PASS"; message = "Path is allowed: $path" }) | Out-Null
        }
        else {
            $status = "FAIL"
            $findings.Add([pscustomobject]@{ status = "FAIL"; message = "Path is outside allowed paths: $path" }) | Out-Null
        }
    }

    New-AIOSAllowedPathResult -Status $status -Findings $findings.ToArray() -CheckedPaths $ChangedPaths
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSAllowedPath -ChangedPaths $ChangedPaths -AllowedPaths $AllowedPaths | ConvertTo-Json -Depth 8
}
