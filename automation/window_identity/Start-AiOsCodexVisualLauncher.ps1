#Requires -Version 5.1
param(
    [switch]$PreviewOnly,
    [switch]$NoEmoji
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repo = "C:\Dev\Ai.Os"
$LaunchCommandText = 'codex --cd "C:\Dev\Ai.Os"'

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch {
    # Older hosts can still render the ASCII fallback banner.
}

function Get-AiOsGlyph {
    param(
        [Parameter(Mandatory = $true)]
        [int]$CodePoint,

        [string]$Fallback = ""
    )

    if ($NoEmoji) {
        return $Fallback
    }

    try {
        return [System.Char]::ConvertFromUtf32($CodePoint)
    } catch {
        return $Fallback
    }
}

function Write-AiosDivider {
    param(
        [string]$Color = "Cyan"
    )

    Write-Host ("=" * 78) -ForegroundColor $Color
}

function Write-AiosBlock {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,

        [string]$ForegroundColor = "White",
        [string]$BackgroundColor = "Black"
    )

    Write-Host (" {0} " -f $Text) -ForegroundColor $ForegroundColor -BackgroundColor $BackgroundColor
}

function Write-AiosRow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [string]$Value,

        [string]$ForegroundColor = "White"
    )

    Write-Host ("{0,-16}: {1}" -f $Label, $Value) -ForegroundColor $ForegroundColor
}

function Get-GitBranchSafe {
    if (-not (Test-Path -LiteralPath $Repo -PathType Container)) {
        return "UNKNOWN - repo path missing"
    }

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return "UNKNOWN - git unavailable"
    }

    try {
        $branch = & git -C $Repo branch --show-current 2>$null
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch)) {
            return "UNKNOWN"
        }

        return "$branch".Trim()
    } catch {
        return "UNKNOWN - git branch check failed"
    }
}

function Get-GitStatusSafe {
    if (-not (Test-Path -LiteralPath $Repo -PathType Container)) {
        return @("UNKNOWN - repo path missing")
    }

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return @("UNKNOWN - git unavailable")
    }

    try {
        $status = @(& git -C $Repo status --short --branch 2>$null)
        if ($LASTEXITCODE -ne 0 -or $status.Count -eq 0) {
            return @("UNKNOWN - git status unavailable")
        }

        return $status
    } catch {
        return @("UNKNOWN - git status check failed")
    }
}

function Test-CodexAvailable {
    return [bool](Get-Command codex -ErrorAction SilentlyContinue)
}

function Write-AiosBanner {
    $bolt = Get-AiOsGlyph -CodePoint 0x26A1 -Fallback "*"
    $tool = Get-AiOsGlyph -CodePoint 0x1F6E0 -Fallback "[BUILD]"
    $lock = Get-AiOsGlyph -CodePoint 0x1F512 -Fallback "[LOCKED]"

    $title = "AIOS CODEX"
    if (-not [string]::IsNullOrWhiteSpace($bolt)) {
        $title = "$title $bolt"
    }

    try {
        $Host.UI.RawUI.WindowTitle = $title
        [Console]::Title = $title
    } catch {
        try {
            $Host.UI.RawUI.WindowTitle = "AIOS CODEX"
        } catch {
        }
    }

    Write-Host ""
    Write-AiosDivider -Color Cyan
    Write-AiosBlock -Text " $tool  AIOS CODEX VISUAL LAUNCHER  $lock " -ForegroundColor Black -BackgroundColor Cyan
    Write-AiosDivider -Color Cyan
    Write-Host "Optional repo-local launcher. No profile, terminal settings, broker, or trading state is changed." -ForegroundColor Gray
    Write-Host ""
}

function Write-AiosStatusBlock {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Branch,

        [Parameter(Mandatory = $true)]
        [string[]]$GitStatus,

        [Parameter(Mandatory = $true)]
        [bool]$CodexAvailable
    )

    Write-AiosBlock -Text " CODEX WORKER " -ForegroundColor Black -BackgroundColor Green
    Write-AiosRow -Label "REPO" -Value $Repo -ForegroundColor Cyan
    Write-AiosRow -Label "MODE" -Value "MANUAL" -ForegroundColor Cyan
    Write-AiosRow -Label "BRANCH" -Value $Branch -ForegroundColor Cyan
    Write-AiosRow -Label "CODEX" -Value ($(if ($CodexAvailable) { "AVAILABLE" } else { "NOT FOUND" })) -ForegroundColor ($(if ($CodexAvailable) { "Green" } else { "Yellow" }))
    Write-Host ""

    Write-AiosBlock -Text " SAFETY BOUNDARIES " -ForegroundColor White -BackgroundColor DarkRed
    Write-AiosRow -Label "LIVE TRADING" -Value "LOCKED" -ForegroundColor Red
    Write-AiosRow -Label "BROKER" -Value "BLOCKED" -ForegroundColor Red
    Write-AiosRow -Label "SECRETS" -Value "DO NOT PRINT" -ForegroundColor Yellow
    Write-AiosRow -Label "PROFILE" -Value "NOT MODIFIED" -ForegroundColor Green
    Write-AiosRow -Label "FILES" -Value "NOT MODIFIED BY THIS LAUNCHER" -ForegroundColor Green
    Write-Host ""

    Write-AiosBlock -Text " GIT STATE " -ForegroundColor Black -BackgroundColor DarkCyan
    foreach ($line in $GitStatus) {
        Write-Host "  $line" -ForegroundColor Gray
    }
    Write-Host ""

    Write-AiosBlock -Text " INTENDED COMMAND " -ForegroundColor Black -BackgroundColor Yellow
    Write-Host "  $LaunchCommandText" -ForegroundColor Yellow
    Write-Host ""
}

try {
    Write-AiosBanner

    if (-not (Test-Path -LiteralPath $Repo -PathType Container)) {
        Write-Host "BLOCKED: Repo path not found: $Repo" -ForegroundColor Red
        exit 1
    }

    Set-Location -LiteralPath $Repo

    $branch = Get-GitBranchSafe
    $gitStatus = @(Get-GitStatusSafe)
    $codexAvailable = Test-CodexAvailable

    Write-AiosStatusBlock -Branch $branch -GitStatus $gitStatus -CodexAvailable $codexAvailable

    if (-not $codexAvailable) {
        Write-Host "Codex command was not found on PATH. No launch attempted." -ForegroundColor Yellow
        exit 0
    }

    if ($PreviewOnly) {
        Write-Host "PREVIEW ONLY: Codex was not launched." -ForegroundColor Green
        exit 0
    }

    $response = Read-Host "Launch Codex now? Type YES to continue"
    if ($response -ceq "YES") {
        Write-Host "Launching: $LaunchCommandText" -ForegroundColor Green
        & codex --cd $Repo
        exit $LASTEXITCODE
    }

    Write-Host "Launch cancelled. Codex was not started." -ForegroundColor Yellow
    exit 0
} catch {
    Write-Host "LAUNCHER ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
