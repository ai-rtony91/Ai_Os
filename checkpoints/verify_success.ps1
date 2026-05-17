param(
    [switch]$WriteLastVerified
)

$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path "$PSScriptRoot\.."
Set-Location $RootDir

function Read-JsonFile {
    param([string]$Path)

    if (!(Test-Path $Path)) {
        return $null
    }

    try {
        return Get-Content $Path -Raw | ConvertFrom-Json
    }
    catch {
        return "__INVALID__"
    }
}

$Blocked = $false

$validation = Read-JsonFile "validation_result.json"
$approval = Read-JsonFile "approval.json"
$completion = Read-JsonFile "completion_report.json"
$taskLog = Read-JsonFile "task_log.json"

if ($null -eq $validation) {
    Write-Host "FAIL: validation_result.json missing" -ForegroundColor Red
    $Blocked = $true
}
elseif ($validation -eq "__INVALID__") {
    Write-Host "FAIL: validation_result.json invalid JSON" -ForegroundColor Red
    $Blocked = $true
}
elseif ($validation.status -notin @("PASS","passed","pass")) {
    Write-Host "FAIL: validation_result.json status is not PASS" -ForegroundColor Red
    $Blocked = $true
}
else {
    Write-Host "PASS: validation_result.json" -ForegroundColor Green
}

if ($null -eq $approval) {
    Write-Host "FAIL: approval.json missing" -ForegroundColor Red
    $Blocked = $true
}
elseif ($approval.approved -ne $true) {
    Write-Host "FAIL: approval.json approved is not true" -ForegroundColor Red
    $Blocked = $true
}
else {
    Write-Host "PASS: approval.json" -ForegroundColor Green
}

if ($null -eq $completion) {
    Write-Host "FAIL: completion_report.json missing" -ForegroundColor Red
    $Blocked = $true
}
elseif ($completion.complete -ne $true) {
    Write-Host "FAIL: completion_report.json complete is not true" -ForegroundColor Red
    $Blocked = $true
}
else {
    Write-Host "PASS: completion_report.json" -ForegroundColor Green
}

if ($null -eq $taskLog) {
    Write-Host "FAIL: task_log.json missing" -ForegroundColor Red
    $Blocked = $true
}
elseif (
    ($taskLog.PSObject.Properties.Name -contains "updates") -and
    (@($taskLog.updates).Count -lt 1)
) {
    Write-Host "FAIL: task_log.json has no updates" -ForegroundColor Red
    $Blocked = $true
}
else {
    Write-Host "PASS: task_log.json" -ForegroundColor Green
}

if ($Blocked) {
    Write-Host ""
    Write-Host "AIOS VERIFY FAILED" -ForegroundColor Red
    exit 1
}

$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

if ($WriteLastVerified) {
    $timestamp | Set-Content proof\last_verified.txt
    Write-Host "PASS: proof/last_verified.txt updated" -ForegroundColor Green
}
else {
    Write-Host "PASS: read-only verification; proof/last_verified.txt not updated" -ForegroundColor Green
}

Write-Host ""
Write-Host "AIOS VERIFY PASSED" -ForegroundColor Green
exit 0
