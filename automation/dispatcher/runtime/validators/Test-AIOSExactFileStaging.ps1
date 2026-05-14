[CmdletBinding()]
param(
    [string[]]$ApprovedFiles = @(),
    [string[]]$ProposedStagingCommands = @()
)

$ErrorActionPreference = "Stop"

function Test-AIOSExactFileStaging {
    [CmdletBinding()]
    param(
        [string[]]$ApprovedFiles = @(),
        [string[]]$ProposedStagingCommands = @()
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $checked = New-Object System.Collections.Generic.List[string]
    $status = "PASS"
    $unsafePatterns = @("git add .", "git add -A", "git add --all")

    if ($ApprovedFiles.Count -eq 0) {
        $status = "REVIEW_REQUIRED"
        $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "No approved exact file list was supplied." }) | Out-Null
    }

    foreach ($command in $ProposedStagingCommands) {
        $checked.Add($command) | Out-Null
        foreach ($pattern in $unsafePatterns) {
            if ($command.Trim().ToLowerInvariant() -eq $pattern.ToLowerInvariant()) {
                $status = "BLOCKED"
                $findings.Add([pscustomobject]@{ status = "BLOCKED"; message = "Unsafe broad staging command is not allowed: $command" }) | Out-Null
            }
        }

        if ($command -match "\*") {
            $status = "BLOCKED"
            $findings.Add([pscustomobject]@{ status = "BLOCKED"; message = "Wildcard staging is not allowed: $command" }) | Out-Null
        }
    }

    if ($ProposedStagingCommands.Count -eq 0) {
        if ($status -eq "PASS") { $status = "REVIEW_REQUIRED" }
        $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "No proposed staging commands were supplied. Validator is report-only." }) | Out-Null
    }

    if ($status -eq "PASS") {
        $findings.Add([pscustomobject]@{ status = "PASS"; message = "No broad staging command was detected." }) | Out-Null
    }

    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "exact_file_staging"
        stage = "pre_commit"
        status = $status
        findings = $findings.ToArray()
        checked_paths = $ApprovedFiles
        checked_commands = $checked.ToArray()
        blocked_actions = @("git_add_dot", "git_add_all", "wildcard_staging", "commit", "push")
        next_safe_action = "Use exact approved file paths only after human commit approval."
    }
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSExactFileStaging -ApprovedFiles $ApprovedFiles -ProposedStagingCommands $ProposedStagingCommands | ConvertTo-Json -Depth 8
}
