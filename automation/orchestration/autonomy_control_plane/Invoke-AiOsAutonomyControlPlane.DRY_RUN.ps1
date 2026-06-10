param(
    [string]$GoalText,
    [string]$PacketPath,
    [string]$AutonomyLoopScriptPath = "automation/orchestration/autonomy_loop/Invoke-AiOsAutonomyLoop.DRY_RUN.ps1",
    [string]$PacketRunnerScriptPath = "automation/orchestration/packet_runner/Invoke-AiOsPacketAutoRunner.DRY_RUN.ps1",
    [string]$ValidatorScriptPath = "automation/validators/aios_governance_validator.py",
    [string]$OutputEvidencePath = "Reports/autonomy_control_plane/control_plane.evidence.json",
    [string]$OutputReportPath = "Reports/autonomy_control_plane/control_plane.report.md"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Get-AiOsRepoRoot {
    $repoRoot = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoRoot)) {
        throw "REVIEW_REQUIRED: Unable to resolve repository root."
    }
    return $repoRoot.Trim()
}

function Resolve-AiOsPath {
    param(
        [Parameter(Mandatory = $true)][string]$PathHint,
        [Parameter(Mandatory = $true)][string]$RepoRoot
    )

    if ([string]::IsNullOrWhiteSpace($PathHint)) {
        return [string]::Empty
    }
    if ([System.IO.Path]::IsPathRooted($PathHint)) {
        return [System.IO.Path]::GetFullPath($PathHint)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $PathHint))
}

function Write-TextAtomic {
    param([string]$Path, [string]$Text)
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $tmp = Join-Path $parent ([guid]::NewGuid().ToString("N") + ".tmp")
    [System.IO.File]::WriteAllText($tmp, $Text, [System.Text.UTF8Encoding]::new($false))
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Force
    }
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Write-JsonAtomic {
    param([string]$Path, [object]$Object)
    Write-TextAtomic -Path $Path -Text ($Object | ConvertTo-Json -Depth 20)
}

function New-MarkdownReport {
    param([hashtable]$Payload)
    return @"
# Autonomy Control Plane Report

- Created UTC: $($Payload.created_at_utc)
- Workflow: $($Payload.workflow)
- Status: $($Payload.status)
- Packet path: $($Payload.packet_path)
- Packet runner status: $($Payload.packet_runner.status)
- Validator status: $($Payload.validator.status)
- Evidence: $($Payload.evidence_path)
- Report: $($Payload.report_path)
"@
}

function Parse-JsonQuiet {
    param([string]$Text)
    try {
        return $Text | ConvertFrom-Json
    } catch {
        return $null
    }
}

try {
    $repoRoot = Get-AiOsRepoRoot
    Set-Location -Path $repoRoot

    $createdAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $evidencePath = Resolve-AiOsPath -PathHint $OutputEvidencePath -RepoRoot $repoRoot
    $reportPath = Resolve-AiOsPath -PathHint $OutputReportPath -RepoRoot $repoRoot

    if ([string]::IsNullOrWhiteSpace($GoalText) -and [string]::IsNullOrWhiteSpace($PacketPath)) {
        throw "BLOCKED: either -GoalText or -PacketPath is required."
    }
    if (-not [string]::IsNullOrWhiteSpace($GoalText) -and -not [string]::IsNullOrWhiteSpace($PacketPath)) {
        throw "BLOCKED: only one input may be provided."
    }

    $workflow = if ([string]::IsNullOrWhiteSpace($PacketPath)) { "goal" } else { "packet" }
    $resolvedLoopScript = Resolve-AiOsPath -PathHint $AutonomyLoopScriptPath -RepoRoot $repoRoot
    $resolvedRunnerScript = Resolve-AiOsPath -PathHint $PacketRunnerScriptPath -RepoRoot $repoRoot
    $resolvedValidatorScript = Resolve-AiOsPath -PathHint $ValidatorScriptPath -RepoRoot $repoRoot

    $loopStatus = [ordered]@{
        status = "SKIPPED"
        exit_code = 0
        stdout = ""
        stderr = ""
        packet_path = $null
    }

    if ($workflow -eq "goal") {
        $loopPacketOutput = Join-Path (Split-Path -Parent $reportPath) "goal.packet.md"
        $loopPacketReport = Join-Path (Split-Path -Parent $reportPath) "goal.packet_runner.report.json"
        $loopOut = & powershell -NoProfile -ExecutionPolicy Bypass -File $resolvedLoopScript `
            -GoalText $GoalText `
            -PacketRunnerOutputPath $loopPacketOutput `
            -PacketRunnerReportPath $loopPacketReport `
            -PassThrough 2>&1
        $loopExitCode = $LASTEXITCODE
        $loopStatus = [ordered]@{
            status = if ($loopExitCode -eq 0) { "PASS" } else { "FAILED" }
            exit_code = $loopExitCode
            stdout = if ($loopOut -is [array]) { $loopOut -join "`n" } else { $loopOut }
            stderr = ""
            packet_path = $null
        }
        if ($loopExitCode -ne 0) {
            throw "BLOCKED: autonomy loop failed."
        }

        $loopPayload = Parse-JsonQuiet -Text $loopStatus.stdout
        if ($null -eq $loopPayload -or -not $loopPayload.packet_path) {
            throw "SOS_REQUIRED: autonomy loop output missing packet_path."
        }
        $packetPathResolved = [string]$loopPayload.packet_path
        $loopStatus.packet_path = $packetPathResolved
    } else {
        $packetPathResolved = Resolve-AiOsPath -PathHint $PacketPath -RepoRoot $repoRoot
        if (-not (Test-Path -LiteralPath $packetPathResolved)) {
            throw "BLOCKED: packet not found: $packetPathResolved"
        }
    }

    if (-not (Test-Path -LiteralPath $packetPathResolved)) {
        throw "BLOCKED: packet missing at runtime: $packetPathResolved"
    }

    $runnerOutputPath = Join-Path (Split-Path -Parent $reportPath) "control_plane.packet.output.md"
    $runnerReportPath = Join-Path (Split-Path -Parent $reportPath) "control_plane.packet.runner.report.json"
    $runnerOut = & powershell -NoProfile -ExecutionPolicy Bypass -File $resolvedRunnerScript `
        -PacketPath $packetPathResolved `
        -OutputPath $runnerOutputPath `
        -ReportPath $runnerReportPath 2>&1
    $runnerExitCode = $LASTEXITCODE
    if ($runnerExitCode -ne 0) {
        throw "BLOCKED: packet auto-runner failed."
    }

    $validatorOut = & python $resolvedValidatorScript --input $packetPathResolved 2>&1
    $validatorExitCode = $LASTEXITCODE
    $validatorPayload = Parse-JsonQuiet -Text ($validatorOut -join "`n")
    $validatorStatus = "FAILED"
    if ($null -ne $validatorPayload -and $validatorPayload.status -eq "PASS") {
        $validatorStatus = "PASS"
    }
    if ($validatorExitCode -ne 0 -or $validatorStatus -ne "PASS") {
        $status = "VALIDATION_FAILED"
    } else {
        $status = "READY_FOR_CODEX"
    }

    if ($validatorOut -join "`n" -match "REVIEW_REQUIRED|FORBIDDEN|protected") {
        $status = "PROTECTED_ACTION_REQUIRED"
    }

    $evidence = [ordered]@{
        schema_version = "AIOS-AUTONOMY-CONTROL-PLANE-V1"
        created_at_utc = $createdAt
        workflow = $workflow
        status = $status
        goal = $GoalText
        packet_path = $packetPathResolved
        loop = $loopStatus
        packet_runner = [ordered]@{
            status = "PASS"
            exit_code = $runnerExitCode
            stdout = if ($runnerOut -is [array]) { $runnerOut -join "`n" } else { $runnerOut }
            stderr = ""
            packet_output_path = $runnerOutputPath
            report_path = $runnerReportPath
        }
        validator = [ordered]@{
            status = $validatorStatus
            exit_code = $validatorExitCode
            stdout = if ($validatorOut -is [array]) { $validatorOut -join "`n" } else { $validatorOut }
            stderr = ""
            payload = $validatorPayload
        }
        evidence_path = $evidencePath
        report_path = $reportPath
    }

    Write-JsonAtomic -Path $evidencePath -Object $evidence
    Write-TextAtomic -Path $reportPath -Text (New-MarkdownReport -Payload $evidence)
    Write-Output ($evidence | ConvertTo-Json -Depth 20)
    if ($status -eq "READY_FOR_CODEX" -or $status -eq "PROTECTED_ACTION_REQUIRED") {
        exit 0
    }
    exit 1
} catch {
    $errorMessage = $_.Exception.Message
    $status = if ($errorMessage -like "SOS_REQUIRED:*") { "SOS_REQUIRED" } elseif ($errorMessage -like "*REVIEW_REQUIRED*" -or $errorMessage -like "*FORBIDDEN*") { "PROTECTED_ACTION_REQUIRED" } else { "BLOCKED" }
    $workflow = if ([string]::IsNullOrWhiteSpace($PacketPath)) { "goal" } else { "packet" }
    $packetPathResolved = if ($workflow -eq "packet") { Resolve-AiOsPath -PathHint $PacketPath -RepoRoot (Get-AiOsRepoRoot) } else { $null }

    $evidence = [ordered]@{
        schema_version = "AIOS-AUTONOMY-CONTROL-PLANE-V1"
        created_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        workflow = $workflow
        status = $status
        goal = $GoalText
        packet_path = $packetPathResolved
        loop = [ordered]@{
            status = "FAILED"
            exit_code = 1
            stdout = ""
            stderr = $errorMessage
            packet_path = $null
        }
        packet_runner = [ordered]@{
            status = "FAILED"
            exit_code = 1
            stdout = ""
            stderr = $errorMessage
            packet_output_path = $null
            report_path = $null
        }
        validator = [ordered]@{
            status = "FAILED"
            exit_code = 1
            stdout = ""
            stderr = $errorMessage
            payload = $null
        }
        evidence_path = $OutputEvidencePath
        report_path = $OutputReportPath
        error = $errorMessage
    }

    Write-JsonAtomic -Path $evidencePath -Object $evidence
    Write-TextAtomic -Path $reportPath -Text (New-MarkdownReport -Payload $evidence)
    Write-Error "REVIEW_REQUIRED: $errorMessage"
    Write-Output ($evidence | ConvertTo-Json -Depth 20)
    exit 1
}
