[CmdletBinding()]
param(
    [string[]]$JsonRoots = @(
        "Reports/dispatcher/runtime",
        "Reports/dispatcher/runtime/validators"
    )
)

$ErrorActionPreference = "Stop"

function New-AIOSValidatorResult {
    param(
        [string]$Status,
        [object[]]$Findings,
        [string[]]$CheckedPaths,
        [string]$NextSafeAction
    )

    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "runtime_json"
        stage = "runtime_json_parse"
        status = $Status
        findings = $Findings
        checked_paths = $CheckedPaths
        blocked_actions = @("modify_files", "stage_files", "commit", "push")
        next_safe_action = $NextSafeAction
    }
}

function Test-AIOSRuntimeJson {
    [CmdletBinding()]
    param(
        [string[]]$JsonRoots = @(
            "Reports/dispatcher/runtime",
            "Reports/dispatcher/runtime/validators"
        )
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $checked = New-Object System.Collections.Generic.List[string]
    $status = "PASS"

    $seen = @{}

    foreach ($root in $JsonRoots) {
        if (-not (Test-Path -LiteralPath $root)) {
            $status = "REVIEW_REQUIRED"
            $findings.Add([pscustomobject]@{
                status = "REVIEW_REQUIRED"
                message = "Runtime JSON root is missing: $root"
            }) | Out-Null
            continue
        }

        Get-ChildItem -LiteralPath $root -Filter "*.json" -File -Recurse | ForEach-Object {
            if ($seen.ContainsKey($_.FullName)) {
                return
            }
            $seen[$_.FullName] = $true
            $checked.Add($_.FullName) | Out-Null
            try {
                Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json | Out-Null
                $findings.Add([pscustomobject]@{
                    status = "PASS"
                    message = "JSON parsed successfully: $($_.FullName)"
                }) | Out-Null
            }
            catch {
                $status = "FAIL"
                $findings.Add([pscustomobject]@{
                    status = "FAIL"
                    message = "JSON parse failed: $($_.FullName)"
                    detail = $_.Exception.Message
                }) | Out-Null
            }
        }
    }

    if ($checked.Count -eq 0 -and $status -eq "PASS") {
        $status = "REVIEW_REQUIRED"
        $findings.Add([pscustomobject]@{
            status = "REVIEW_REQUIRED"
            message = "No runtime JSON files were found to validate."
        }) | Out-Null
    }

    New-AIOSValidatorResult -Status $status -Findings $findings.ToArray() -CheckedPaths $checked.ToArray() -NextSafeAction "Fix JSON parse failures before using runtime status files."
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSRuntimeJson -JsonRoots $JsonRoots | ConvertTo-Json -Depth 8
}
