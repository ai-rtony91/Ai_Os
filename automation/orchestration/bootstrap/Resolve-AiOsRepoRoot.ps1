Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    param(
        [string]$StartPath = $PSScriptRoot
    )

    if ([string]::IsNullOrWhiteSpace($StartPath)) {
        throw "AI_OS repo root discovery failed: StartPath was empty."
    }

    $resolvedStartPath = Resolve-Path -LiteralPath $StartPath -ErrorAction Stop
    $currentPath = $resolvedStartPath.Path

    if (Test-Path -LiteralPath $currentPath -PathType Leaf) {
        $currentPath = Split-Path -Parent $currentPath
    }

    while (-not [string]::IsNullOrWhiteSpace($currentPath)) {
        if (Test-AiOsRepoRoot -Path $currentPath) {
            return $currentPath
        }

        $parentPath = Split-Path -Parent $currentPath
        if ($parentPath -eq $currentPath) {
            break
        }

        $currentPath = $parentPath
    }

    throw "AI_OS repo root discovery failed from StartPath: $StartPath. Required markers not found: .git, AGENTS.md, README.md, project.manifest.json."
}

function Test-AiOsRepoRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $requiredMarkers = @(
        ".git",
        "AGENTS.md",
        "README.md",
        "project.manifest.json"
    )

    foreach ($marker in $requiredMarkers) {
        $markerPath = Join-Path $Path $marker
        if (-not (Test-Path -LiteralPath $markerPath)) {
            return $false
        }
    }

    return $true
}

function Resolve-AiOsRepoPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [string]$StartPath = $PSScriptRoot
    )

    if ([System.IO.Path]::IsPathRooted($RelativePath)) {
        return $RelativePath
    }

    $repoRoot = Resolve-AiOsRepoRoot -StartPath $StartPath
    return Join-Path $repoRoot $RelativePath
}
