[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Command
)

$ErrorActionPreference = "Stop"

function Block-Command {
    param([string]$Reason)

    Write-Host "BLOCKED: $Reason"
    exit 1
}

function Test-IsRepoScopedPath {
    param(
        [string]$Value,
        [string]$RepoRoot
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $true
    }

    $expanded = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Value)
    $repoPrefix = $RepoRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

    return ($expanded -eq $RepoRoot -or $expanded.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase))
}

$normalizedCommand = $Command.Trim()
if ([string]::IsNullOrWhiteSpace($normalizedCommand)) {
    Block-Command "Recommended command is empty."
}

if ($normalizedCommand -match "[`r`n]") {
    Block-Command "Recommended command must be a single line."
}

if ($normalizedCommand -match "(^|[\s;&|])(?:Remove-Item|rm|del|erase|Invoke-WebRequest|iwr|curl|wget|Start-Process|start|saps|schtasks|Set-ExecutionPolicy|Invoke-Expression|iex|New-Object|Set-Content|Add-Content|Out-File|Move-Item|Copy-Item|Rename-Item|New-Item)(?:$|[\s;&|])") {
    Block-Command "Recommended command contains a blocked command."
}

if ($normalizedCommand -match "(?i)\bgit\s+(?:push|commit|merge|rebase|reset|clean|checkout|switch|branch|tag|remote)\b") {
    Block-Command "Recommended command contains a blocked git action."
}

if ($normalizedCommand -match "(?i)\b(secret|secrets|api[_-]?key|apikey|token|credential|credentials|password|passwd|private[_ -]?key|recovery[_ -]?key)\b") {
    Block-Command "Recommended command appears to reference secrets or credentials."
}

if ($normalizedCommand -match "(?i)(^|[^A-Za-z0-9])(broker|oanda|traderspost|webhook|live[_ -]*trading|real[_ -]*order|place[_ -]*order|submit[_ -]*order|market[_ -]*order|limit[_ -]*order|buy|sell|trade[_ -]*execution|execute[_ -]*trade)([^A-Za-z0-9]|$)") {
    Block-Command "Recommended command appears to reference broker or trading execution actions."
}

$tokens = $null
$parseErrors = $null
$tokens = [System.Management.Automation.PSParser]::Tokenize($normalizedCommand, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) {
    Block-Command "Recommended command is not valid PowerShell syntax."
}

$operatorTokens = @($tokens | Where-Object { $_.Type -eq "Operator" -and $_.Content -in @(";", "|", "&&", "||") })
if ($operatorTokens.Count -gt 0) {
    Block-Command "Recommended command must not chain or pipe commands."
}

$commandTokens = @($tokens | Where-Object { $_.Type -eq "Command" } | ForEach-Object { $_.Content })
if ($commandTokens.Count -ne 1) {
    Block-Command "Recommended command must contain exactly one command."
}

$allowedCommands = @(
    "Get-ChildItem",
    "gci",
    "dir",
    "ls",
    "Get-Content",
    "gc",
    "Select-String",
    "sls",
    "Test-Path",
    "Get-Item",
    "gi",
    "Resolve-Path",
    "git"
)

if ($commandTokens[0] -notin $allowedCommands) {
    Block-Command "Recommended command is not in the safe allowlist."
}

if ($commandTokens[0] -eq "git" -and $normalizedCommand -notmatch "(?i)^git\s+(?:status|diff|log|show)\b") {
    Block-Command "Only read-only git status, diff, log, and show commands are allowed."
}

$repoRoot = (Get-Location).ProviderPath
$pathLikeTokens = @(
    $tokens |
        Where-Object {
            $_.Type -in @("String", "CommandArgument") -and
            $_.Content -notmatch "^-{1,2}" -and
            (
                $_.Content -match "^[A-Za-z]:[\\/]" -or
                $_.Content -match "^\\\\" -or
                $_.Content -match "^[.]{1,2}[\\/]" -or
                $_.Content -match "[\\/]"
            )
        } |
        ForEach-Object { $_.Content.Trim("'`\"") }
)

foreach ($pathToken in $pathLikeTokens) {
    if (-not (Test-IsRepoScopedPath -Value $pathToken -RepoRoot $repoRoot)) {
        Block-Command "Recommended command references a path outside the repo: $pathToken"
    }
}

Write-Host "SAFE: Recommended command is repo-scoped and allowed."
exit 0
