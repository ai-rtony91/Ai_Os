[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$GhJsonPath = "",
    [string]$ApprovalsPath = "relay/approvals"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$resolvedApprovals = if ([System.IO.Path]::IsPathRooted($ApprovalsPath)) { $ApprovalsPath } else { Join-Path $repoRoot $ApprovalsPath }

try {
    if ([string]::IsNullOrWhiteSpace($GhJsonPath)) {
        $raw = gh pr list --json number,title,headRefName,statusCheckRollup --state open
    } else {
        $raw = Get-Content -Raw -LiteralPath $GhJsonPath
    }
    $prs = $raw | ConvertFrom-Json
} catch {
    Write-Host "PR_WATCH_SKIPPED_NO_GH"
    exit 0
}

$written = @()
foreach ($pr in @($prs)) {
    $failed = @()
    foreach ($check in @($pr.statusCheckRollup)) {
        $conclusion = ""
        if ($null -ne $check.conclusion) { $conclusion = [string]$check.conclusion }
        if (@("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED") -contains $conclusion.ToUpperInvariant()) {
            $name = if ($null -ne $check.name) { [string]$check.name } elseif ($null -ne $check.context) { [string]$check.context } else { "unknown-check" }
            $failed += $name
        }
    }
    if ($failed.Count -eq 0) {
        continue
    }

    $advisoryPath = Join-Path $resolvedApprovals ("pr-{0}-check-failed.advisory.md" -f $pr.number)
    $body = @(
        "# PR Check Failed Advisory",
        "",
        "- Advisory type: non-blocking visibility",
        "- PR: #$($pr.number) $($pr.title)",
        "- Branch: $($pr.headRefName)",
        "- Detected at UTC: $((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))",
        "- Failing checks: $($failed -join ', ')",
        "",
        "This is not an approval gate and does not authorize commit, push, merge, or retry."
    ) -join "`n"

    $compareBody = ($body -replace "Detected at UTC: .*", "Detected at UTC: <timestamp>") -replace "`r`n", "`n"
    $existingCompare = ""
    if (Test-Path -LiteralPath $advisoryPath -PathType Leaf) {
        $existingCompare = ((Get-Content -Raw -LiteralPath $advisoryPath) -replace "Detected at UTC: .*", "Detected at UTC: <timestamp>") -replace "`r`n", "`n"
    }
    if ($existingCompare.TrimEnd() -ne $compareBody.TrimEnd()) {
        if ($Apply) {
            if (-not (Test-Path -LiteralPath $resolvedApprovals -PathType Container)) {
                New-Item -ItemType Directory -Path $resolvedApprovals -Force | Out-Null
            }
            Set-Content -LiteralPath $advisoryPath -Value $body -Encoding UTF8
        } else {
            Write-Host ("DRY_RUN would_write={0}" -f $advisoryPath)
        }
        $written += $advisoryPath
    }
}

Write-Output ([ordered]@{ apply = [bool]$Apply; advisories_changed = @($written).Count; paths = @($written) } | ConvertTo-Json -Depth 5)
