param(
    [string]$RepoRoot = "",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Resolve-AiOsRepoRoot {
    param([string]$CandidateRoot)
    if (-not [string]::IsNullOrWhiteSpace($CandidateRoot)) {
        return (Resolve-Path -Path $CandidateRoot).Path
    }

    $candidate = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($candidate)) {
        throw "REVIEW_REQUIRED: Unable to resolve repository root. Set RepoRoot explicitly."
    }
    return $candidate.Trim()
}

function Resolve-PathSafe {
    param(
        [Parameter(Mandatory = $true)][string]$Base,
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    if ([System.IO.Path]::IsPathRooted($RelativePath)) {
        return $RelativePath
    }

    return Join-Path $Base $RelativePath
}

function Collect-Files {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $false)][string[]]$Include
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return @()
    }

    if ($Include -and $Include.Count -gt 0) {
        return Get-ChildItem -LiteralPath $Path -Recurse -File -Include $Include | ForEach-Object { $_.FullName }
    }

    return Get-ChildItem -LiteralPath $Path -Recurse -File | ForEach-Object { $_.FullName }
}

function Write-JsonAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Object
    )

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -Path $directory -ItemType Directory -Force | Out-Null
    }

    $tmp = Join-Path $directory ([guid]::NewGuid().ToString("N") + ".tmp")
    $json = $Object | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($tmp, $json, [Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Force
    }
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

try {
    $resolvedRepoRoot = Resolve-AiOsRepoRoot -CandidateRoot $RepoRoot
    Set-Location -Path $resolvedRepoRoot

    $packetRunnerDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/orchestration/packet_runner"
    $autonomyLoopDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/orchestration/autonomy_loop"
    $coordinationSpineDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/orchestration/coordination_spine"
    $validatorDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/validators"
    $workPacketDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/orchestration/work_packets"
    $tradingDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/trading"
    $reportsTradingDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "Reports/trading_lab"
    $telemetryTradingDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "telemetry/trading_lab"
    $dispatcherDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/dispatcher"
    $locksDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/orchestration/locks"
    $approvalDir = Resolve-PathSafe -Base $resolvedRepoRoot -RelativePath "automation/orchestration/approval_inbox"

    $packetRunnerScripts = Collect-Files -Path $packetRunnerDir -Include "*.ps1"
    $autonomyLoopScripts = Collect-Files -Path $autonomyLoopDir -Include "*.ps1"
    $coordinationSpineScripts = Collect-Files -Path $coordinationSpineDir -Include "*.ps1"
    $validatorScripts = Collect-Files -Path $validatorDir -Include "*.py"
    $dispatcherScripts = Collect-Files -Path $dispatcherDir -Include "*.py","*.ps1"
    $lockScripts = Collect-Files -Path $locksDir -Include "*.ps1","*.py"
    $approvalFiles = Collect-Files -Path $approvalDir -Include "*.md","*.json","*.py","*.ps1"
    $tradingFiles = Collect-Files -Path $tradingDir
    $tradingPaperFiles = Collect-Files -Path $tradingDir -Include "*paper*"

    $reportDir = Join-Path $resolvedRepoRoot "Reports\autonomy_discovery"
    if ([string]::IsNullOrWhiteSpace($OutputPath)) {
        $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
        $OutputPath = Join-Path $reportDir ("autonomy_inventory_{0}.json" -f $stamp)
    } elseif ([System.IO.Path]::IsPathRooted($OutputPath)) {
        $OutputPath = $OutputPath
    } else {
        $OutputPath = Join-Path $resolvedRepoRoot $OutputPath
    }

    $packetFolderStates = @{}
    foreach ($name in @("proposed", "active", "deferred", "blocked", "approved", "rejected")) {
        $folderPath = Join-Path $workPacketDir $name
        if (Test-Path -LiteralPath $folderPath -PathType Container) {
            $files = Get-ChildItem -LiteralPath $folderPath -File | Measure-Object
            $packetFolderStates[$name] = [ordered]@{
                path = $folderPath
                exists = $true
                file_count = $files.Count
            }
        } else {
            $packetFolderStates[$name] = [ordered]@{
                path = $folderPath
                exists = $false
                file_count = 0
            }
        }
    }

    $inventory = [ordered]@{
        schema = "AIOS_AUTONOMY_INVENTORY_V1"
        generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        repo_root = $resolvedRepoRoot
        components = [ordered]@{
            packet_runner = [ordered]@{
                directory = $packetRunnerDir
                exists = (Test-Path -LiteralPath $packetRunnerDir -PathType Container)
                scripts = $packetRunnerScripts
                detection_count = $packetRunnerScripts.Count
            }
            autonomy_loop = [ordered]@{
                directory = $autonomyLoopDir
                exists = (Test-Path -LiteralPath $autonomyLoopDir -PathType Container)
                scripts = $autonomyLoopScripts
                detection_count = $autonomyLoopScripts.Count
            }
            validators = [ordered]@{
                directory = $validatorDir
                exists = (Test-Path -LiteralPath $validatorDir -PathType Container)
                scripts = $validatorScripts
                detection_count = $validatorScripts.Count
            }
            coordination_spine = [ordered]@{
                directory = $coordinationSpineDir
                exists = (Test-Path -LiteralPath $coordinationSpineDir -PathType Container)
                scripts = $coordinationSpineScripts
                detection_count = $coordinationSpineScripts.Count
            }
            work_packets = [ordered]@{
                directory = $workPacketDir
                exists = (Test-Path -LiteralPath $workPacketDir -PathType Container)
                folders = $packetFolderStates
            }
            trading = [ordered]@{
                automation_directory = $tradingDir
                automation_exists = (Test-Path -LiteralPath $tradingDir -PathType Container)
                automation_files = $tradingFiles.Count
                paper_related_files = $tradingPaperFiles.Count
                paper_file_samples = $tradingPaperFiles | Select-Object -First 12
                reports_directory = $reportsTradingDir
                telemetry_directory = $telemetryTradingDir
            }
            approval = [ordered]@{
                directory = $approvalDir
                exists = (Test-Path -LiteralPath $approvalDir -PathType Container)
                files = $approvalFiles
                detection_count = $approvalFiles.Count
            }
            locks = [ordered]@{
                directory = $locksDir
                exists = (Test-Path -LiteralPath $locksDir -PathType Container)
                scripts = $lockScripts
                detection_count = $lockScripts.Count
            }
            dispatch = [ordered]@{
                directory = $dispatcherDir
                exists = (Test-Path -LiteralPath $dispatcherDir -PathType Container)
                scripts = $dispatcherScripts
                detection_count = $dispatcherScripts.Count
            }
        }
        status = "PASS"
    }

    Write-JsonAtomic -Path $OutputPath -Object $inventory
    Write-Output ($inventory | ConvertTo-Json -Depth 20)
    exit 0
} catch {
    Write-Error "REVIEW_REQUIRED: $($_.Exception.Message)"
    exit 1
}
