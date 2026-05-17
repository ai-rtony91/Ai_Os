param(
    [string]$Preset = 'compact',

    [switch]$Apply
)

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch {
    # Older hosts may reject output encoding changes; command generation still works.
}

$repoPath = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$identityScript = Join-Path $PSScriptRoot 'Set-AiOsWindowIdentity.ps1'
$layoutPath = Join-Path $PSScriptRoot 'AIOS_WINDOW_LAYOUTS.json'

if (-not (Test-Path -LiteralPath $layoutPath)) {
    throw "Window layout registry not found: $layoutPath"
}

$layoutConfig = Get-Content -LiteralPath $layoutPath -Raw | ConvertFrom-Json

function Get-SelectedMarkers {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SelectedPreset
    )

    $presetProperty = $layoutConfig.presets.PSObject.Properties[$SelectedPreset]
    if (-not $presetProperty) {
        $availablePresets = @($layoutConfig.presets.PSObject.Properties.Name)
        throw "Unknown AI_OS window layout preset '$SelectedPreset'. Available presets: $($availablePresets -join ', ')"
    }

    return @($presetProperty.Value)
}

function New-WorkerPowerShellArguments {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Marker
    )

    $escapedScript = $identityScript.Replace("'", "''")
    $escapedMarker = $Marker.Replace("'", "''")
    $command = "& '$escapedScript' -Marker '$escapedMarker'"

    return @(
        '-NoExit',
        '-ExecutionPolicy',
        'Bypass',
        '-Command',
        $command
    )
}

function Format-StartProcessCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Marker,

        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList
    )

    $escapedRepo = $repoPath.Replace("'", "''")
    $escapedArgs = ($ArgumentList | ForEach-Object { "'" + $_.Replace("'", "''") + "'" }) -join ', '

    return "Start-Process -FilePath 'powershell.exe' -WorkingDirectory '$escapedRepo' -ArgumentList @($escapedArgs) # $Marker"
}

function Invoke-WorkerWindow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Marker
    )

    $arguments = New-WorkerPowerShellArguments -Marker $Marker
    Write-Host (Format-StartProcessCommand -Marker $Marker -ArgumentList $arguments)

    if ($Apply) {
        Start-Process -FilePath 'powershell.exe' -WorkingDirectory $repoPath -ArgumentList $arguments | Out-Null
    }
}

$selectedMarkers = Get-SelectedMarkers -SelectedPreset $Preset

Write-Host 'AI_OS Simple Worker Window Launcher'
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Preset: $Preset"
Write-Host "Repo path: $repoPath"
Write-Host "Identity script: $identityScript"
Write-Host 'Safety: powershell.exe only. No startup tasks, scheduled tasks, dashboard edits, Trading Lab edits, commits, or pushes.'
Write-Host ''

Write-Host 'Planned worker windows:'
foreach ($marker in $selectedMarkers) {
    Write-Host "- $marker"
}
Write-Host ''

Write-Host 'Commands:'
foreach ($marker in $selectedMarkers) {
    Invoke-WorkerWindow -Marker $marker
}

Write-Host ''
Write-Host "Launch performed: $(if ($Apply) { 'YES' } else { 'NO' })"
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
