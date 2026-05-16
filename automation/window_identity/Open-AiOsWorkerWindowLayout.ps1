param(
    [ValidateSet('compact', 'wide', 'dual-monitor')]
    [string]$Preset = 'compact',

    [switch]$Apply
)

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch {
    # Older hosts may reject output encoding changes; command generation still works.
}

$repoPath = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
$identityScript = Join-Path $repoPath 'automation\window_identity\Set-AiOsWindowIdentity.ps1'

$markers = @(
    'AI_OS MAIN CONTROL',
    'CODEX BUILD LANE',
    'VALIDATOR WORKER',
    'PACKET QUEUE',
    'APPROVAL INBOX',
    'RECOVERY HEALTH',
    'STANDBY WORKER'
)

$emoji = @{
    'AI_OS MAIN CONTROL' = [char]::ConvertFromUtf32(0x1F9ED)
    'CODEX BUILD LANE' = [char]::ConvertFromUtf32(0x1F6E0)
    'VALIDATOR WORKER' = [char]::ConvertFromUtf32(0x2705)
    'PACKET QUEUE' = [char]::ConvertFromUtf32(0x1F4E6)
    'APPROVAL INBOX' = [char]::ConvertFromUtf32(0x1F4E5)
    'RECOVERY HEALTH' = [char]::ConvertFromUtf32(0x1FA7A)
    'STANDBY WORKER' = [char]::ConvertFromUtf32(0x23F8)
}

function New-WorkerCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Marker
    )

    $escapedRepo = $repoPath.Replace("'", "''")
    $escapedScript = $identityScript.Replace("'", "''")
    $escapedMarker = $Marker.Replace("'", "''")
    return "Set-Location -LiteralPath '$escapedRepo'; & '$escapedScript' -Marker '$escapedMarker'"
}

function New-WorkerArgs {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Marker,

        [string[]]$Prefix = @()
    )

    $title = "$($emoji[$Marker]) $Marker"
    return @(
        $Prefix
        '--startingDirectory'
        $repoPath
        '--title'
        $title
        'powershell'
        '-NoExit'
        '-ExecutionPolicy'
        'Bypass'
        '-Command'
        (New-WorkerCommand -Marker $Marker)
    )
}

function Format-WtCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $quoted = foreach ($arg in $Arguments) {
        if ($arg -match '[\s";]') {
            '"' + $arg.Replace('"', '\"') + '"'
        } else {
            $arg
        }
    }

    return "wt.exe $($quoted -join ' ')"
}

function Invoke-Wt {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $printable = Format-WtCommand -Arguments $Arguments
    Write-Host $printable

    if ($Apply) {
        Start-Process -FilePath 'wt.exe' -ArgumentList $Arguments | Out-Null
    }
}

$layoutCommands = @()

switch ($Preset) {
    'compact' {
        $args = @('--window', '0', '--size', '140,40')
        $first = $true
        foreach ($marker in $markers) {
            if ($first) {
                $args += New-WorkerArgs -Marker $marker
                $first = $false
            } else {
                $args += ';'
                $args += New-WorkerArgs -Marker $marker -Prefix @('new-tab')
            }
        }
        $layoutCommands += ,$args
    }
    'wide' {
        $args = @('--window', '0', '--size', '190,48')
        $first = $true
        foreach ($marker in $markers) {
            if ($first) {
                $args += New-WorkerArgs -Marker $marker
                $first = $false
            } else {
                $args += ';'
                $args += New-WorkerArgs -Marker $marker -Prefix @('new-tab')
            }
        }
        $layoutCommands += ,$args
    }
    'dual-monitor' {
        $leftMarkers = @(
            'AI_OS MAIN CONTROL',
            'CODEX BUILD LANE',
            'VALIDATOR WORKER',
            'APPROVAL INBOX'
        )
        $rightMarkers = @(
            'PACKET QUEUE',
            'RECOVERY HEALTH',
            'STANDBY WORKER'
        )

        $leftArgs = @('--window', 'aios-left', '--pos', '0,0', '--size', '145,46')
        $first = $true
        foreach ($marker in $leftMarkers) {
            if ($first) {
                $leftArgs += New-WorkerArgs -Marker $marker
                $first = $false
            } else {
                $leftArgs += ';'
                $leftArgs += New-WorkerArgs -Marker $marker -Prefix @('new-tab')
            }
        }

        $rightArgs = @('--window', 'aios-right', '--pos', '1600,0', '--size', '145,46')
        $first = $true
        foreach ($marker in $rightMarkers) {
            if ($first) {
                $rightArgs += New-WorkerArgs -Marker $marker
                $first = $false
            } else {
                $rightArgs += ';'
                $rightArgs += New-WorkerArgs -Marker $marker -Prefix @('new-tab')
            }
        }

        $layoutCommands += ,$leftArgs
        $layoutCommands += ,$rightArgs
    }
}

Write-Host 'AI_OS Worker Window Layout'
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Preset: $Preset"
Write-Host "Repo path: $repoPath"
Write-Host 'Safety: Windows Terminal only. No startup tasks, scheduled tasks, dashboard edits, Trading Lab edits, protected root edits, commits, or pushes.'
Write-Host ''

$wt = Get-Command 'wt.exe' -ErrorAction SilentlyContinue
if (-not $wt) {
    Write-Host 'WARN: wt.exe was not found on PATH. DRY_RUN commands are still printed; APPLY cannot launch without Windows Terminal.'
    if ($Apply) {
        exit 1
    }
}

Write-Host 'Commands:'
foreach ($commandArgs in $layoutCommands) {
    Invoke-Wt -Arguments $commandArgs
}

Write-Host ''
Write-Host "Launch performed: $(if ($Apply) { 'YES' } else { 'NO' })"
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
