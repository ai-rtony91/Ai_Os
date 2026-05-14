[CmdletBinding()]
param(
    [string[]]$ChangedPaths = @(),
    [string[]]$ProtectedRootFiles = @(
        "README.md",
        "RISK_POLICY.md",
        "SOURCE_LOG.md",
        "ERROR_LOG.md",
        "HALLUCINATION_LOG.md",
        "AAR.md",
        "DAILY_REPORT.md",
        "ARCHITECTURE.md",
        "DEPLOYMENT.md",
        "WHITEPAPER.md"
    )
)

$ErrorActionPreference = "Stop"

function Test-AIOSProtectedRoot {
    [CmdletBinding()]
    param(
        [string[]]$ChangedPaths = @(),
        [string[]]$ProtectedRootFiles = @()
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $status = "PASS"
    $protectedLookup = @{}
    foreach ($file in $ProtectedRootFiles) {
        $protectedLookup[$file.ToLowerInvariant()] = $true
    }

    if ($ChangedPaths.Count -eq 0) {
        $status = "REVIEW_REQUIRED"
        $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "No changed paths were supplied for protected-root validation." }) | Out-Null
    }

    foreach ($path in $ChangedPaths) {
        $normalized = ($path -replace "\\", "/").TrimStart("/")
        if ($normalized -notmatch "/" -and $protectedLookup.ContainsKey($normalized.ToLowerInvariant())) {
            $status = "BLOCKED"
            $findings.Add([pscustomobject]@{ status = "BLOCKED"; message = "Protected root file is in the change set: $path" }) | Out-Null
        }
        else {
            $findings.Add([pscustomobject]@{ status = "PASS"; message = "Path is not a protected root file: $path" }) | Out-Null
        }
    }

    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "protected_root"
        stage = "pre_apply"
        status = $status
        findings = $findings.ToArray()
        checked_paths = $ChangedPaths
        blocked_actions = @("modify_protected_root_files", "stage_files", "commit", "push")
        next_safe_action = "Stop and request explicit protected-file approval if a protected root file appears."
    }
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSProtectedRoot -ChangedPaths $ChangedPaths -ProtectedRootFiles $ProtectedRootFiles | ConvertTo-Json -Depth 8
}
