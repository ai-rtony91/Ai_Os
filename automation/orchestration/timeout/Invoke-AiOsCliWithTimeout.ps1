[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [string[]]$ArgumentList = @(),
    [int]$TimeoutSec = 600,
    [AllowNull()][string]$StdIn = $null,
    [AllowNull()][string]$WorkingDirectory = $null
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$started = (Get-Date).ToUniversalTime()

function Quote-AiOsCliArg {
    param([AllowNull()][string]$Arg)
    if ($null -eq $Arg) { return '""' }
    if ($Arg -notmatch '[\s"]') { return $Arg }
    return '"' + ($Arg -replace '"', '\"') + '"'
}

try {
    $resolved = Get-Command $FilePath -ErrorAction SilentlyContinue
    $resolvedPath = if ($null -ne $resolved) { $resolved.Source } else { $FilePath }
    $ext = [System.IO.Path]::GetExtension($resolvedPath).ToLowerInvariant()
    $effectiveFile = $resolvedPath
    $effectiveArgs = @($ArgumentList)

    if ($ext -eq ".ps1") {
        $effectiveFile = (Get-Command powershell -ErrorAction Stop).Source
        $effectiveArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $resolvedPath) + @($ArgumentList)
    } elseif ($ext -eq ".cmd" -or $ext -eq ".bat") {
        $effectiveFile = (Get-Command cmd.exe -ErrorAction Stop).Source
        $effectiveArgs = @("/c", $resolvedPath) + @($ArgumentList)
    }

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $effectiveFile
    $psi.Arguments = ($effectiveArgs | ForEach-Object { Quote-AiOsCliArg -Arg $_ }) -join " "
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.RedirectStandardInput = $true
    $psi.UseShellExecute = $false
    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
        $psi.WorkingDirectory = $WorkingDirectory
    }

    $proc = [System.Diagnostics.Process]::new()
    $proc.StartInfo = $psi
    [void]$proc.Start()

    if ($null -ne $StdIn) {
        $proc.StandardInput.Write($StdIn)
    }
    $proc.StandardInput.Close()

    $completed = $proc.WaitForExit([Math]::Max(1, $TimeoutSec) * 1000)
    if (-not $completed) {
        $stdout = $proc.StandardOutput.ReadToEndAsync()
        $stderr = $proc.StandardError.ReadToEndAsync()
        & taskkill /T /F /PID $proc.Id | Out-Null
        [void]$proc.WaitForExit(5000)
        return [pscustomobject]@{
            exit_code = "TIMEOUT_EXCEEDED"
            stdout = $stdout.GetAwaiter().GetResult()
            stderr = $stderr.GetAwaiter().GetResult()
            timed_out_at_utc = (Get-Date).ToUniversalTime()
            pid = $proc.Id
        }
    }

    $outText = $proc.StandardOutput.ReadToEnd()
    $errText = $proc.StandardError.ReadToEnd()
    return [pscustomobject]@{
        exit_code = [int]$proc.ExitCode
        stdout = $outText
        stderr = $errText
        duration_sec = [Math]::Round(((Get-Date).ToUniversalTime() - $started).TotalSeconds, 3)
    }
}
catch {
    return [pscustomobject]@{
        exit_code = 127
        stdout = ""
        stderr = $_.Exception.Message
        duration_sec = [Math]::Round(((Get-Date).ToUniversalTime() - $started).TotalSeconds, 3)
    }
}
