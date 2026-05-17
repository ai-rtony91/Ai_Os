param(
    [Parameter(Mandatory = $true)]
    [string]$Marker,

    [switch]$EndOfChat
)

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch {
    # Older hosts may reject output encoding changes; the marker still works.
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

function Get-AiOsDisplayTitle {
    param([Parameter(Mandatory = $true)]$Identity)

    $emoji = "$($Identity.emoji)".Trim()
    $title = "$($Identity.title)".Trim()

    if ([string]::IsNullOrWhiteSpace($emoji)) {
        return $title
    }

    if ($title.StartsWith($emoji, [System.StringComparison]::Ordinal)) {
        return $title
    }

    return "$emoji $title"
}

function Get-AiOsMarkerWidth {
    param($Identity)

    $width = Get-AiOsPropertyValue -Object $Identity -Name 'endMarkerWidth'
    if ($null -ne $width) {
        try {
            return [Math]::Max(60, [Math]::Min(240, [int]$width))
        } catch {
            return 120
        }
    }

    try {
        if ($Host.UI.RawUI.WindowSize.Width -gt 0) {
            return [Math]::Max(60, [Math]::Min(160, $Host.UI.RawUI.WindowSize.Width))
        }
    } catch {
        return 100
    }

    return 100
}

function Write-AiOsFilledMarker {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,

        [Parameter(Mandatory = $true)]
        [string]$Fill,

        [Parameter(Mandatory = $true)]
        [int]$Width,

        [Parameter(Mandatory = $true)]
        [string]$Color
    )

    if ([string]::IsNullOrWhiteSpace($Fill)) {
        $Fill = '='
    }

    $fillChar = $Fill.Substring(0, 1)
    $safeText = $Text.Trim()
    $line = " $safeText "
    if ($line.Length -lt $Width) {
        $rightFill = $fillChar * ($Width - $line.Length)
        $line = $line + $rightFill
    }

    Write-Host $line -ForegroundColor $Color
}

$repoPath = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$registryPath = Join-Path $PSScriptRoot 'AIOS_WORKER_REGISTRY.json'

if (-not (Test-Path -LiteralPath $registryPath)) {
    throw "Worker registry not found: $registryPath"
}

$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$identity = $registry.workers | Where-Object { $_.marker -eq $Marker -and $_.enabled -eq $true } | Select-Object -First 1

if (-not $identity) {
    $enabledMarkers = @($registry.workers | Where-Object { $_.enabled -eq $true } | ForEach-Object { $_.marker })
    throw "Unknown or disabled AI_OS worker marker '$Marker'. Enabled markers: $($enabledMarkers -join ', ')"
}

$windowTitle = Get-AiOsDisplayTitle -Identity $identity
$Host.UI.RawUI.WindowTitle = $windowTitle

$bannerWidth = Get-AiOsMarkerWidth -Identity $identity
$divider = '=' * $bannerWidth
$color = "$($identity.color)"

$identityBanner = Get-AiOsPropertyValue -Object $identity -Name 'identityBanner'
$beginMarker = Get-AiOsPropertyValue -Object $identity -Name 'beginMarker'
$endMarker = Get-AiOsPropertyValue -Object $identity -Name 'endMarker'
$endMarkerFill = Get-AiOsPropertyValue -Object $identity -Name 'endMarkerFill'

if ($EndOfChat) {
    if ([string]::IsNullOrWhiteSpace("$endMarker")) {
        $endMarker = "$windowTitle :: END OF CHAT"
    }

    Write-Host ''
    Write-AiOsFilledMarker -Text "$endMarker" -Fill "$endMarkerFill" -Width $bannerWidth -Color $color
    Write-Host ''
    exit 0
}

if ([string]::IsNullOrWhiteSpace("$identityBanner")) {
    $identityBanner = "$windowTitle :: ONLINE"
}

if ([string]::IsNullOrWhiteSpace("$beginMarker")) {
    $beginMarker = "$windowTitle :: BEGIN"
}

Write-Host ''
Write-Host $divider -ForegroundColor $color
Write-Host $identityBanner -ForegroundColor $color
Write-Host $beginMarker -ForegroundColor $color
Write-Host $divider -ForegroundColor $color
Write-Host "Role: $($identity.role)"
Write-Host "Repo path: $repoPath"
Write-Host ''
Write-Host 'Allowed actions:' -ForegroundColor $color
foreach ($item in $identity.allowedActions) {
    Write-Host "  - $item"
}
Write-Host ''
Write-Host 'Blocked actions:' -ForegroundColor $color
foreach ($item in $identity.blockedActions) {
    Write-Host "  - $item"
}
Write-Host ''
Write-Host 'Next command hint:' -ForegroundColor $color
Write-Host "  $($identity.nextCommand)"
Write-Host ''
Write-Host 'Safety: repo-scoped marker only. No files, tasks, apps, brokers, keys, or trades are touched.'
Write-Host ''
