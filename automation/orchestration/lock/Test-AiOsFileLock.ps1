[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string[]]$AllowedPaths,
    [int]$RecentWindowSec = 300,
    [string]$RepoRoot = "C:\Dev\Ai.Os"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolved = (Resolve-Path -LiteralPath $RepoRoot).Path
$cutoff = (Get-Date).AddSeconds(-1 * $RecentWindowSec)
$locked = New-Object System.Collections.Generic.List[string]

foreach ($pattern in $AllowedPaths) {
    $clean = ([string]$pattern).Replace("/", "\").TrimStart(".\")
    if ([string]::IsNullOrWhiteSpace($clean)) { continue }
    $root = Join-Path $repoRootResolved $clean
    $files = if (Test-Path -LiteralPath $root -PathType Leaf) {
        @(Get-Item -LiteralPath $root)
    } elseif (Test-Path -LiteralPath $root -PathType Container) {
        @(Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue)
    } else {
        @(Get-ChildItem -Path (Join-Path $repoRootResolved $clean) -File -ErrorAction SilentlyContinue)
    }

    foreach ($file in $files) {
        $relative = $file.FullName.Substring($repoRootResolved.Length + 1).Replace("\", "/")
        if ($file.LastWriteTime -gt $cutoff -and $relative -notmatch "^relay/") {
            $locked.Add($relative)
        }
    }
}

$deferUntil = (Get-Date).ToUniversalTime().AddSeconds($RecentWindowSec).ToString("yyyy-MM-ddTHH:mm:ssZ")
return [pscustomobject]@{ defer = ($locked.Count -gt 0); locked_files = @($locked); defer_until_utc = $deferUntil; reason = if ($locked.Count -gt 0) { "RECENT_EXTERNAL_WRITE" } else { "" } }
