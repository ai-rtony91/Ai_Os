[CmdletBinding()]
param(
    [string]$DeleteBranch = ""
)

$ErrorActionPreference = "Stop"

git checkout main
git pull

if (-not [string]::IsNullOrWhiteSpace($DeleteBranch)) {
    git branch -D $DeleteBranch
}

git status --short --branch