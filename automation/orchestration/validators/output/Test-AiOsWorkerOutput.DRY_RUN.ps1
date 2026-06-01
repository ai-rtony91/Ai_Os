[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PacketId,
    [Parameter(Mandatory = $true)][string[]]$AllowedPaths,
    [Parameter(Mandatory = $true)][datetime]$RunStartUtc,
    [string]$RepoRoot = "C:\Dev\Ai.Os"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolved = (Resolve-Path -LiteralPath $RepoRoot).Path
$logPath = Join-Path $repoRootResolved "relay\logs\output_validator.log"
$protectedPaths = @("RISK_POLICY.md", "AGENTS.md", "README.md", "CLAUDE.md", ".git/", ".codex_backups/")

function Convert-ToRelativePath {
    param([string]$Path)
    $base = $repoRootResolved.TrimEnd("\") + "\"
    return $Path.Substring($base.Length).Replace("\", "/")
}

function Test-UnderPattern {
    param([string]$RelativePath, [string[]]$Patterns)
    foreach ($pattern in $Patterns) {
        $clean = ([string]$pattern).Replace("\", "/").TrimStart("./")
        if ([string]::IsNullOrWhiteSpace($clean)) { continue }
        if ($RelativePath.Equals($clean, [StringComparison]::OrdinalIgnoreCase) -or
            $RelativePath.StartsWith($clean.TrimEnd("/") + "/", [StringComparison]::OrdinalIgnoreCase) -or
            ($clean.EndsWith("/") -and $RelativePath.StartsWith($clean, [StringComparison]::OrdinalIgnoreCase))) {
            return $true
        }
    }
    return $false
}

$protectedAllowed = @($AllowedPaths | Where-Object { Test-UnderPattern -RelativePath $_ -Patterns $protectedPaths })
$touched = @(Get-ChildItem -LiteralPath $repoRootResolved -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\.git\\" -and $_.LastWriteTimeUtc -ge $RunStartUtc.ToUniversalTime() } |
    ForEach-Object { Convert-ToRelativePath -Path $_.FullName })

$violations = @($touched | Where-Object { -not (Test-UnderPattern -RelativePath $_ -Patterns $AllowedPaths) })
$protectedViolations = @($touched | Where-Object { Test-UnderPattern -RelativePath $_ -Patterns $protectedPaths })

$payload = [ordered]@{
    pass = ($protectedAllowed.Count -eq 0 -and $violations.Count -eq 0 -and $protectedViolations.Count -eq 0)
    packet_id = $PacketId
    touched = @($touched)
    violations = @($violations)
    protected_violations = @($protectedViolations + $protectedAllowed)
    violation_reason = if (($protectedViolations.Count + $protectedAllowed.Count) -gt 0) { "PROTECTED_PATH_TOUCHED" } elseif ($violations.Count -gt 0) { "OUTPUT_OUTSIDE_ALLOWED_PATHS" } else { "" }
    checked_at_utc = (Get-Date).ToUniversalTime()
}

$logDir = Split-Path -Parent $logPath
if (-not (Test-Path -LiteralPath $logDir -PathType Container)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
Add-Content -LiteralPath $logPath -Value (($payload | ConvertTo-Json -Compress -Depth 8))

return [pscustomobject]$payload
