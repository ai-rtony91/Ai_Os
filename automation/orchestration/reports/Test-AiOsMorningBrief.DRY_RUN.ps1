$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$scriptPath = Join-Path $repoRoot "automation\orchestration\reports\New-AiOsMorningBrief.ps1"
$date = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
$briefPath = Join-Path $repoRoot ("relay\reports\MORNING_BRIEF_{0}.md" -f $date)

function Get-AiOsFileFingerprint {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{ exists = $false; hash = ""; length = 0; modified_utc = "" }
    }
    $item = Get-Item -LiteralPath $Path
    return [pscustomobject]@{
        exists = $true
        hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
        length = $item.Length
        modified_utc = $item.LastWriteTimeUtc.ToString("o")
    }
}

function Assert-AiOs {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) {
        throw $Message
    }
}

Set-Location $repoRoot

$before = Get-AiOsFileFingerprint -Path $briefPath
$output = @(& pwsh -NoProfile -ExecutionPolicy Bypass -File $scriptPath)
$exitCode = $LASTEXITCODE
$after = Get-AiOsFileFingerprint -Path $briefPath
$text = $output -join "`n"

Assert-AiOs ($exitCode -eq 0) "Morning brief default DRY_RUN exited with $exitCode."
Assert-AiOs ($text -match "MORNING_BRIEF_PREVIEW") "Default run did not identify itself as preview."
Assert-AiOs ($text -notmatch "MORNING_BRIEF_WRITTEN") "Default run wrote a morning brief."
Assert-AiOs ($text -match "morning_evidence_status=") "Output missing morning_evidence_status."
Assert-AiOs ($text -match "digest_path=") "Output missing digest_path."
Assert-AiOs ($text -match "digest_freshness=") "Output missing digest_freshness."
Assert-AiOs ($text -match "next_safe_action=") "Output missing next_safe_action."
Assert-AiOs ($before.exists -eq $after.exists) "Default run changed morning brief existence."
if ($before.exists) {
    Assert-AiOs ($before.hash -eq $after.hash) "Default run changed morning brief content."
    Assert-AiOs ($before.length -eq $after.length) "Default run changed morning brief length."
}
Assert-AiOs ($text -match "morning_digest=.*(WARN|BLOCKED|PASS)") "Digest freshness classification missing."

[pscustomobject]@{
    schema = "AIOS_MORNING_BRIEF_DRY_RUN_VALIDATION.v1"
    mode = "DRY_RUN"
    status = "PASS"
    default_run_mutated_output = $false
    checked_path = $briefPath.Substring($repoRoot.Length + 1)
    assertions = @(
        "default run is preview-only",
        "default run does not write MORNING_BRIEF output",
        "output includes morning_evidence_status",
        "output includes digest_path",
        "output includes digest_freshness",
        "output includes next_safe_action"
    )
} | ConvertTo-Json -Depth 4
