param(
    [string]$AdbPath = "C:\Android\platform-tools\adb.exe",
    [string]$WirelessTarget = "192.168.1.251:5555",
    [string]$Message = "#AIOS_SOS WAKE",
    [int]$Retries = 3
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Dev\Ai.Os"
$LogDir = Join-Path $RepoRoot "logs\android"
$LogFile = Join-Path $LogDir "adb_sos_wake.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-AiosLog {
    param([string]$Text)
    $Stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Stamp`t$Text" | Tee-Object -FilePath $LogFile -Append
}

function Get-AdbDeviceLines {
    & $AdbPath devices | Where-Object {
        $_ -match "\sdevice$" -and $_ -notmatch "^List of devices"
    }
}

function Test-AdbTargetConnected {
    param([string]$Target)
    $devices = Get-AdbDeviceLines
    return ($devices -match [regex]::Escape($Target))
}

if (-not (Test-Path $AdbPath)) {
    Write-AiosLog "FAIL adb not found at $AdbPath"
    exit 10
}

Write-AiosLog "START AIOS ADB SOS Wake. Target=$WirelessTarget Message=$Message"

if (-not (Test-AdbTargetConnected -Target $WirelessTarget)) {
    Write-AiosLog "Wireless target not connected. Attempting adb connect $WirelessTarget"
    & $AdbPath connect $WirelessTarget | ForEach-Object { Write-AiosLog "adb connect: $_" }
    Start-Sleep -Seconds 2
}

$activeTarget = $null

if (Test-AdbTargetConnected -Target $WirelessTarget) {
    $activeTarget = $WirelessTarget
    Write-AiosLog "Using wireless target $activeTarget"
} else {
    $deviceLines = Get-AdbDeviceLines
    if ($deviceLines.Count -ge 1) {
        $activeTarget = ($deviceLines[0] -split "\s+")[0]
        Write-AiosLog "Wireless unavailable. Falling back to connected target $activeTarget"
    }
}

if (-not $activeTarget) {
    Write-AiosLog "FAIL no ADB device available"
    exit 20
}

for ($i = 1; $i -le $Retries; $i++) {
    try {
        Write-AiosLog "Attempt $i posting SOS notification through $activeTarget"

        & $AdbPath -s $activeTarget shell cmd notification post -S bigtext -t "AIOS SOS" "AIOS_SOS_WAKE" $Message |
            ForEach-Object { Write-AiosLog "post: $_" }

        Start-Sleep -Seconds 1

        $snapshot = & $AdbPath -s $activeTarget shell dumpsys notification --noredact
        $matched = $snapshot | Select-String -Pattern "AIOS_SOS|AIOS_SOS_WAKE|AIOS SOS"

        if ($matched) {
            Write-AiosLog "PASS notification visible in Android notification service"
            exit 0
        }

        Write-AiosLog "WARN notification post command ran, but snapshot match not found"
    }
    catch {
        Write-AiosLog "ERROR attempt $i failed: $($_.Exception.Message)"
    }

    Start-Sleep -Seconds 2
}

Write-AiosLog "FAIL SOS wake did not validate after $Retries attempts"
exit 30
