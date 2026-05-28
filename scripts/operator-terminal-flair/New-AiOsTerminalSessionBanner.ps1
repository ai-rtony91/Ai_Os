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

function Format-AiOsPanelLine {
    param(
        [string]$Label,
        [string]$Text,
        [string]$Code = "48;5;24;97"
    )

    $line = ("  {0,-12} {1}" -f $Label, $Text)
    return Format-AiOsAnsi -Text $line -Code $Code
}

function Format-AiOsBadge {
    param(
        [string]$Text,
        [string]$Code
    )

    return Format-AiOsAnsi -Text ("[{0}]" -f $Text) -Code $Code
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
$panelCode = "48;5;24;97"
$panelAccentCode = "48;5;17;96"
$panelWarningCode = "48;5;236;93"

Write-Host $primaryBorder
Write-Host (Format-AiOsAnsi -Text $title -Code $profile.ansi_accent)
Write-Host (Format-AiOsPanelLine -Label "PROFILE" -Text $status -Code $panelCode)
Write-Host (Format-AiOsPanelLine -Label "MODE" -Text $modeLine -Code $panelAccentCode)
Write-Host (Format-AiOsPanelLine -Label "SAFE" -Text $profile.safe_command_hint -Code $panelCode)
Write-Host (Format-AiOsPanelLine -Label "BLOCKED" -Text $profile.forbidden_action_hint -Code $panelWarningCode)
Write-Host ("  STATUS     {0} {1} {2} {3} {4}" -f (Format-AiOsBadge -Text "CI" -Code "96"), (Format-AiOsBadge -Text "PASS" -Code "92"), (Format-AiOsBadge -Text "WORKING" -Code "38;5;208"), (Format-AiOsBadge -Text "COMPLETE" -Code "92"), (Format-AiOsBadge -Text "BLOCKED" -Code "91"))
Write-Host (Format-AiOsPanelLine -Label "WORKERS" -Text "persistent decks stay open; OCC workers complete once per task lifecycle" -Code $panelCode)
Write-Host ("REPO: {0}" -f $repoRoot.Path)
Write-Host "RULE: NO COMMIT / NO PUSH unless approved"
Write-Host $primaryBorder
