param(
    [Parameter(Mandatory = $true)]
    [string]$ProfileId,

    [string]$WorkerNumber,

    [ValidateSet("CLEAN", "HYPE", "BOSS")]
    [string]$Mode = "HYPE",

    [switch]$NoEmoji
)

# Builds a readable AI_OS worker-profile terminal banner.
# This script prints preview output only. It does not write files or edit terminal settings.

$ErrorActionPreference = "Stop"

function Test-AiOsAnsiSupport {
    if ($NoColor -or $env:NO_COLOR) {
        return $false
    }

    if ($Host.Name -eq "ConsoleHost" -or $Host.UI.SupportsVirtualTerminal) {
        return $true
    }

    return $false
}

function Format-AiOsAnsi {
    param(
        [string]$Text,
        [string]$Code
    )

    if (-not $script:UseAnsi) {
        return $Text
    }

    $escape = [char]27
    return "$escape[$Code`m$Text$escape[0m"
}

function New-AiOsBorder {
    param(
        [int]$Length,
        [string]$Pattern
    )

    return ($Pattern * $Length).Substring(0, $Length)
}

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDirectory "..\..")
$registryPath = Join-Path $repoRoot "docs\AI_OS\design\terminal-flair\WORKER_PROFILE_THEME_REGISTRY_001.json"

if (-not (Test-Path -LiteralPath $registryPath)) {
    Write-Error "Terminal flair registry not found: $registryPath"
    exit 1
}

$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$normalizedProfileId = $ProfileId.Trim().ToUpperInvariant()
$profile = @($registry.profiles) | Where-Object { $_.profile_id -eq $normalizedProfileId } | Select-Object -First 1

if (-not $profile) {
    Write-Host "Profile not found: $ProfileId" -ForegroundColor Yellow
    Write-Host "Available profiles:" -ForegroundColor Cyan
    @($registry.profiles) | ForEach-Object {
        Write-Host ("- {0}" -f $_.profile_id)
    }
    exit 1
}

$script:UseAnsi = Test-AiOsAnsiSupport
$modeUpper = $Mode.ToUpperInvariant()
$badge = $profile.short_badge
$emojiPrefix = ""

if (-not $NoEmoji -and $profile.emoji) {
    $emojiPrefix = "$($profile.emoji) "
}

$workerLabel = $profile.display_name
if ($WorkerNumber) {
    $workerLabel = "$workerLabel #$WorkerNumber"
}

switch ($modeUpper) {
    "CLEAN" {
        $borderLength = 72
        $borderPattern = "-"
        $modeLine = "MODE CLEAN // readable preview"
    }
    "HYPE" {
        $borderLength = 80
        $borderPattern = "="
        $modeLine = "MODE HYPE // WebDevOps-2026 command deck"
    }
    "BOSS" {
        $borderLength = 88
        $borderPattern = "#"
        $modeLine = "MODE BOSS // mission HUD maximum readable flair"
    }
}

$topBorder = New-AiOsBorder -Length $borderLength -Pattern $borderPattern
$primaryBorder = Format-AiOsAnsi -Text $topBorder -Code $profile.ansi_primary
$title = "$emojiPrefix$($profile.banner_title)"
$status = "[$badge] $workerLabel // $($profile.lane_type)"

Write-Host $primaryBorder
Write-Host (Format-AiOsAnsi -Text $title -Code $profile.ansi_accent)
Write-Host (Format-AiOsAnsi -Text $status -Code $profile.ansi_primary)
Write-Host (Format-AiOsAnsi -Text $modeLine -Code $profile.ansi_accent)
Write-Host (Format-AiOsAnsi -Text ("SAFE: {0}" -f $profile.safe_command_hint) -Code $profile.ansi_primary)
Write-Host (Format-AiOsAnsi -Text ("BLOCKED: {0}" -f $profile.forbidden_action_hint) -Code $profile.ansi_warning)
Write-Host ("REPO: {0}" -f $repoRoot.Path)
Write-Host "RULE: NO COMMIT / NO PUSH unless approved"
Write-Host $primaryBorder
