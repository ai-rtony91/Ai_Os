param(
    [Parameter(Mandatory = $true)]
    [string]$PacketPath,

    [string]$OutputPath,
    [string]$ReportPath
)

$ErrorActionPreference = "Stop"

function Resolve-TargetPath {
    param(
        [string]$PathHint,
        [string]$DefaultPath
    )

    if ([string]::IsNullOrWhiteSpace($PathHint)) {
        return $DefaultPath
    }

    $candidate = [System.IO.Path]::GetFullPath($PathHint)
    $parentDir = Split-Path -Parent $candidate
    if (-not [string]::IsNullOrWhiteSpace($parentDir) -and -not (Test-Path -Path $parentDir)) {
        New-Item -Path $parentDir -ItemType Directory -Force | Out-Null
    }

    return $candidate
}

function Write-TextAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )

    $targetDirectory = Split-Path -Path $Path -Parent
    if (-not (Test-Path -Path $targetDirectory)) {
        New-Item -Path $targetDirectory -ItemType Directory -Force | Out-Null
    }

    $tmpPath = Join-Path $targetDirectory ("{0}.tmp" -f ([guid]::NewGuid().ToString("N")))
    [System.IO.File]::WriteAllText($tmpPath, $Text, [System.Text.UTF8Encoding]::new($false))
    if (Test-Path -Path $Path) {
        [System.IO.File]::Delete($Path)
    }
    [System.IO.File]::Move($tmpPath, $Path)
}

try {
    $packetItem = Get-Item -Path $PacketPath -ErrorAction Stop
} catch {
    Write-Error "REVIEW_REQUIRED: PacketPath not found: $PacketPath"
    exit 1
}

$packetText = Get-Content -Path $packetItem.FullName -Raw
$packetName = $packetItem.Name
$packetDirectory = Split-Path -Parent $packetItem.FullName

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path -Path (Join-Path $scriptDirectory "..\..\")).Path
$defaultReportDir = Join-Path $repoRoot "Reports\packet_runner"
$defaultOutputPath = Join-Path $defaultReportDir ([IO.Path]::ChangeExtension($packetName, ".full_packet.md"))
$defaultReportPath = Join-Path $defaultReportDir ([IO.Path]::GetFileNameWithoutExtension($packetName) + ".report.json")

$resolvedOutputPath = Resolve-TargetPath -PathHint $OutputPath -DefaultPath $defaultOutputPath
$resolvedReportPath = Resolve-TargetPath -PathHint $ReportPath -DefaultPath $defaultReportPath

$validatorExe = "python"
$validatorArgs = @("automation/validators/aios_governance_validator.py", "--input", $packetItem.FullName)
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $validatorExe
$psi.Arguments = "$($validatorArgs -join ' ')"
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.CreateNoWindow = $true

$validatorProcess = [System.Diagnostics.Process]::Start($psi)
$validatorOutput = $validatorProcess.StandardOutput.ReadToEnd()
$validatorError = $validatorProcess.StandardError.ReadToEnd()
$validatorProcess.WaitForExit()
$validatorExitCode = $validatorProcess.ExitCode

$validatorJson = $null
$validatorPayload = $null
$parsedPayload = $false
if (-not [string]::IsNullOrWhiteSpace($validatorOutput)) {
    try {
        $validatorJson = $validatorOutput
        $validatorPayload = $validatorOutput | ConvertFrom-Json
        $parsedPayload = $true
    } catch {
        $validatorPayload = [ordered]@{
            status = "UNPARSEABLE"
            errors = @(@{
                rule_id = "AIOS-PACKET-RUNNER-OUTPUT"
                message = "Validator output is not valid JSON."
            })
            warnings = @()
        }
        $parsedPayload = $false
    }
}

if (-not $parsedPayload -and [string]::IsNullOrWhiteSpace($validatorError)) {
    $validatorPayload = [ordered]@{
        status = "NO_OUTPUT"
        errors = @(@{
            rule_id = "AIOS-PACKET-RUNNER-OUTPUT"
            message = "Validator produced no JSON output."
        })
        warnings = @()
    }
}

$summary = [ordered]@{
    run_timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
    packet_path = $packetItem.FullName
    packet_name = $packetName
    packet_directory = $packetDirectory
    packet_output_path = $resolvedOutputPath
    report_path = $resolvedReportPath
    packet_size_bytes = $packetText.Length
    validator_command = "$validatorExe $($validatorArgs -join ' ')"
    validator_exit_code = $validatorExitCode
    validator_status = $validatorPayload.status
    validator_errors = $validatorPayload.errors
    validator_warnings = $validatorPayload.warnings
    validator_raw_stdout = $validatorOutput
    validator_raw_stderr = $validatorError
    codex_ready_generated = $true
}

try {
    Write-TextAtomic -Path $resolvedOutputPath -Text $packetText
    Write-TextAtomic -Path $resolvedReportPath -Text ($summary | ConvertTo-Json -Depth 16)
} catch {
    $invocation = $_.InvocationInfo
    $commandName = if ($null -ne $invocation -and $null -ne $invocation.MyCommand) { $invocation.MyCommand.Name } else { "unknown" }
    Write-Error "REVIEW_REQUIRED: Failed writing packet auto-runner outputs: $($_.Exception.Message) | Command=$commandName | Line=$($invocation.ScriptLineNumber)"
    exit 1
}

Write-Output ($summary | ConvertTo-Json -Depth 16)
exit 0
