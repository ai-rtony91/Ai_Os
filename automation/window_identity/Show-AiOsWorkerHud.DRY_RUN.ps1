param(
    [string]$Worker = "ALL",
    [ValidateSet("DRY_RUN", "APPLY", "READ_ONLY", "REPORT")]
    [string]$Mode = "DRY_RUN"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch {
    # Rendering falls back to plain text if the host rejects UTF-8 output.
}

function Get-AiOsPropertyValue {
    param(
        [Parameter(Mandatory = $true)]
        $Object,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $property = $Object.PSObject.Properties[$Name]
    if ($property) {
        return $property.Value
    }

    return $null
}

function Get-AiOsEmoji {
    param([Parameter(Mandatory = $true)]$Identity)

    $emojiCodePoint = "$(Get-AiOsPropertyValue -Object $Identity -Name 'emojiCodePoint')".Trim()
    if ([string]::IsNullOrWhiteSpace($emojiCodePoint)) {
        return ""
    }

    try {
        $codePoint = if ($emojiCodePoint.StartsWith("0x", [System.StringComparison]::OrdinalIgnoreCase)) {
            [Convert]::ToInt32($emojiCodePoint.Substring(2), 16)
        } else {
            [Convert]::ToInt32($emojiCodePoint, 10)
        }

        return [System.Char]::ConvertFromUtf32($codePoint)
    } catch {
        return ""
    }
}

function Get-AiOsDisplayTitle {
    param([Parameter(Mandatory = $true)]$Identity)

    $title = "$($Identity.title)".Trim()
    $fallbackTitle = "$(Get-AiOsPropertyValue -Object $Identity -Name 'fallbackTitle')".Trim()
    $emoji = Get-AiOsEmoji -Identity $Identity

    if (-not [string]::IsNullOrWhiteSpace($emoji)) {
        return "$emoji $title"
    }

    if (-not [string]::IsNullOrWhiteSpace($fallbackTitle)) {
        return $fallbackTitle
    }

    return $title
}

function Get-AiOsShortRole {
    param([Parameter(Mandatory = $true)]$Identity)

    $role = "$($Identity.role)".Trim()
    if ($role.Length -le 72) {
        return $role
    }

    return ($role.Substring(0, 69) + "...")
}

function Get-AiOsStopRule {
    param([Parameter(Mandatory = $true)]$Identity)

    $blocked = @($Identity.blockedActions)
    if ($blocked.Count -eq 0) {
        return "Visual identity only. No execution behavior."
    }

    return [string]$blocked[0]
}

function Write-AiOsHudRow {
    param(
        [string]$Label,
        [string]$Value
    )

    $safeValue = if ([string]::IsNullOrWhiteSpace($Value)) { "UNKNOWN" } else { $Value }
    Write-Host ("  {0,-8} {1}" -f $Label, $safeValue)
}

function Write-AiOsWorkerHud {
    param(
        [Parameter(Mandatory = $true)]
        $Identity,

        [Parameter(Mandatory = $true)]
        [string]$DisplayMode
    )

    $color = "$($Identity.color)"
    if ([string]::IsNullOrWhiteSpace($color)) {
        $color = "White"
    }

    $title = Get-AiOsDisplayTitle -Identity $Identity
    $fallbackTitle = "$(Get-AiOsPropertyValue -Object $Identity -Name 'fallbackTitle')".Trim()
    $theme = "$(Get-AiOsPropertyValue -Object $Identity -Name 'theme')".Trim()
    $divider = "+" * 64

    Write-Host $divider -ForegroundColor $color
    Write-Host ("  {0}" -f $title) -ForegroundColor $color
    if (-not [string]::IsNullOrWhiteSpace($fallbackTitle)) {
        Write-AiOsHudRow -Label "FALLBACK" -Value $fallbackTitle
    }
    Write-AiOsHudRow -Label "ROLE" -Value (Get-AiOsShortRole -Identity $Identity)
    Write-AiOsHudRow -Label "COLOR" -Value $color
    Write-AiOsHudRow -Label "THEME" -Value $theme
    Write-AiOsHudRow -Label "LANE" -Value "$($Identity.marker)"
    Write-AiOsHudRow -Label "MODE" -Value $DisplayMode
    Write-AiOsHudRow -Label "STOP" -Value (Get-AiOsStopRule -Identity $Identity)
    Write-Host $divider -ForegroundColor $color
    Write-Host ""
}

$registryPath = Join-Path $PSScriptRoot "AIOS_WORKER_REGISTRY.json"
if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    throw "AI_OS worker registry not found: $registryPath"
}

$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$enabledWorkers = @($registry.workers | Where-Object { $_.enabled -eq $true })

$shortCodeMap = @{
    "MAIN"      = "AI_OS MAIN CONTROL"
    "ORCH"      = "CLAUDE REVIEWER"
    "CLAUDE"    = "CLAUDE REVIEWER"
    "EAST"      = "CODEX BUILD LANE"
    "WEST"      = "CLAUDE REVIEWER"
    "VALIDATOR" = "VALIDATOR WORKER"
    "GATE"      = "APPROVAL INBOX"
    "PACKET"    = "PACKET QUEUE"
    "HANDOFF"   = "APPROVAL INBOX"
    "NIGHT"     = "STANDBY WORKER"
    "CLEAN"     = "RECOVERY HEALTH"
}

$targetWorker = $Worker.Trim()
if ([string]::IsNullOrWhiteSpace($targetWorker) -or $targetWorker -eq "ALL") {
    $selectedWorkers = $enabledWorkers
} else {
    $lookupKey = $targetWorker.ToUpperInvariant()
    if ($shortCodeMap.ContainsKey($lookupKey)) {
        $targetWorker = $shortCodeMap[$lookupKey]
    }

    $selectedWorkers = @($enabledWorkers | Where-Object {
        $_.marker -eq $targetWorker -or $_.title -eq $targetWorker
    })
}

if ($selectedWorkers.Count -eq 0) {
    $knownMarkers = @($enabledWorkers | ForEach-Object { $_.marker })
    throw "Unknown AI_OS worker '$Worker'. Known workers: $($knownMarkers -join ', ')"
}

Write-Host "AI_OS WORKER HUD PREVIEW" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN visual-only. No execution behavior changed."
Write-Host ""

foreach ($identity in $selectedWorkers) {
    Write-AiOsWorkerHud -Identity $identity -DisplayMode $Mode
}

Write-Host "Visual-only confirmation: no dispatch, queue, approval, git, API, secret, or trading behavior changed."
