param(
    [string]$RegistryPath = "automation/orchestration/execution_registry/AIOS_EXECUTION_CLASSIFICATION_REGISTRY.json",
    [string[]]$ScanRoots = @(
        "automation/orchestration",
        "automation/startup",
        "automation/operator"
    )
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Add-Finding {
    param(
        [Parameter(Mandatory = $true)]
        [ref]$Findings,

        [Parameter(Mandatory = $true)]
        [string]$Severity,

        [Parameter(Mandatory = $true)]
        [string]$CheckId,

        [Parameter(Mandatory = $true)]
        [string]$Message,

        [string]$Evidence = "UNKNOWN",

        [string]$NextSafeAction = "Review the finding and keep execution blocked until resolved."
    )

    $Findings.Value += [pscustomobject]@{
        Severity = $Severity
        CheckId = $CheckId
        Message = $Message
        Evidence = $Evidence
        NextSafeAction = $NextSafeAction
    }
}

function Resolve-AiOsRepoRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$StartPath
    )

    $candidate = (Resolve-Path -LiteralPath $StartPath).Path
    while (-not [string]::IsNullOrWhiteSpace($candidate)) {
        if ((Test-Path -LiteralPath (Join-Path $candidate "AGENTS.md") -PathType Leaf) -and
            (Test-Path -LiteralPath (Join-Path $candidate "README.md") -PathType Leaf)) {
            return $candidate
        }

        $parent = Split-Path -Parent $candidate
        if ($parent -eq $candidate) {
            break
        }
        $candidate = $parent
    }

    throw "Unable to resolve AI_OS repo root from $StartPath."
}

function Get-RelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BasePath,

        [Parameter(Mandatory = $true)]
        [string]$FullPath
    )

    $baseUri = [System.Uri]::new(($BasePath.TrimEnd("\", "/") + [System.IO.Path]::DirectorySeparatorChar))
    $fileUri = [System.Uri]::new($FullPath)
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($fileUri).ToString()).Replace("/", "\")
}

function Normalize-RegistryPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    return $Path.Replace("\", "/").TrimStart("/", ".")
}

function Test-RequiredRegistryFields {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Registry,

        [Parameter(Mandatory = $true)]
        [ref]$Findings
    )

    $requiredTopLevelFields = @(
        "registry_id",
        "schema_version",
        "status",
        "default_policy",
        "allowed_classifications",
        "required_fields_per_script",
        "scripts"
    )

    foreach ($field in $requiredTopLevelFields) {
        if (-not ($Registry.PSObject.Properties.Name -contains $field)) {
            Add-Finding -Findings $Findings -Severity "STOP" -CheckId "registry_schema_missing_field" -Message "Registry is missing required top-level field." -Evidence $field -NextSafeAction "Repair the registry in a separate approved APPLY task."
        }
    }

    if (($Registry.PSObject.Properties.Name -contains "registry_id") -and $Registry.registry_id -ne "AIOS_EXECUTION_CLASSIFICATION_REGISTRY") {
        Add-Finding -Findings $Findings -Severity "STOP" -CheckId "registry_id_mismatch" -Message "Registry ID is not the expected execution classification registry." -Evidence ([string]$Registry.registry_id) -NextSafeAction "Verify the registry path and stop before execution."
    }

    if (($Registry.PSObject.Properties.Name -contains "schema_version") -and $Registry.schema_version -ne "1.0") {
        Add-Finding -Findings $Findings -Severity "STOP" -CheckId "registry_schema_version_unsupported" -Message "Registry schema version is unsupported." -Evidence ([string]$Registry.schema_version) -NextSafeAction "Review schema compatibility before using this guard."
    }

    if (($Registry.PSObject.Properties.Name -contains "status") -and $Registry.status -ne "canonical_execution_classification_registry") {
        Add-Finding -Findings $Findings -Severity "STOP" -CheckId "registry_status_invalid" -Message "Registry is not marked as canonical execution classification registry." -Evidence ([string]$Registry.status) -NextSafeAction "Review registry authority before execution."
    }
}

function Test-RegistryScriptEntries {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Registry,

        [Parameter(Mandatory = $true)]
        [ref]$Findings
    )

    $allowedClassifications = @($Registry.allowed_classifications)
    $requiredScriptFields = @($Registry.required_fields_per_script)
    $seenPaths = @{}

    foreach ($script in @($Registry.scripts)) {
        $pathValue = "UNKNOWN"
        if ($script.PSObject.Properties.Name -contains "path") {
            $pathValue = [string]$script.path
        }

        foreach ($field in $requiredScriptFields) {
            if (-not ($script.PSObject.Properties.Name -contains $field)) {
                Add-Finding -Findings $Findings -Severity "STOP" -CheckId "script_entry_missing_field" -Message "Registry script entry is missing a required field." -Evidence "$pathValue :: $field" -NextSafeAction "Repair the registry entry before using this script."
            }
        }

        if ($script.PSObject.Properties.Name -contains "classification") {
            if ($allowedClassifications -notcontains $script.classification) {
                Add-Finding -Findings $Findings -Severity "STOP" -CheckId "script_entry_invalid_classification" -Message "Registry script entry uses an unsupported classification." -Evidence "$pathValue :: $($script.classification)" -NextSafeAction "Use only approved classification values."
            }
        }

        $normalizedPath = Normalize-RegistryPath -Path $pathValue
        if ($seenPaths.ContainsKey($normalizedPath)) {
            Add-Finding -Findings $Findings -Severity "STOP" -CheckId "script_entry_duplicate_path" -Message "Registry contains duplicate script path entries." -Evidence $normalizedPath -NextSafeAction "Resolve duplicate entries in a separate approved APPLY task."
        } else {
            $seenPaths[$normalizedPath] = $true
        }
    }
}

function Test-DryRunWriteBehavior {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [Parameter(Mandatory = $true)]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [ref]$Findings
    )

    if ($RelativePath -notmatch "\.DRY_RUN\.ps1$") {
        return
    }

    $writePattern = "(?im)(^|[\s;&|])(?:Set-Content|Add-Content|Out-File|Export-Csv|ConvertTo-Json\s*\|[^`r`n]*Set-Content|New-Item|Remove-Item|Move-Item|Rename-Item|Copy-Item)(?:\s|$)"
    if ($Content -match $writePattern) {
        Add-Finding -Findings $Findings -Severity "STOP" -CheckId "dry_run_script_writes_files" -Message "DRY_RUN script appears to contain file-writing or file-mutating commands." -Evidence $RelativePath -NextSafeAction "Keep the script blocked until behavior is repaired or reclassified through approved APPLY."
    }
}

function Test-BlockedScriptReferences {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [Parameter(Mandatory = $true)]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [object[]]$BlockedEntries,

        [Parameter(Mandatory = $true)]
        [ref]$Findings
    )

    $isLauncherLike = (
        $RelativePath -match "(^|/|\\)(Start|Open)-" -or
        $RelativePath -match "(?i)launcher" -or
        $Content -match "(?i)Start-Process|wt\.exe|conhost\.exe|powershell\s+-|pwsh\s+-"
    )

    if (-not $isLauncherLike) {
        return
    }

    foreach ($entry in $BlockedEntries) {
        $blockedPath = Normalize-RegistryPath -Path ([string]$entry.path)
        $blockedBackslash = $blockedPath.Replace("/", "\")
        $escapedForward = [regex]::Escape($blockedPath)
        $escapedBackslash = [regex]::Escape($blockedBackslash)
        if ($Content -match $escapedForward -or $Content -match $escapedBackslash) {
            Add-Finding -Findings $Findings -Severity "STOP" -CheckId "launcher_references_blocked_script" -Message "Launcher-like script references a BLOCKED script." -Evidence "$RelativePath -> $blockedPath" -NextSafeAction "Keep launcher use blocked until references are removed or explicitly approved."
        }
    }
}

$findings = @()

try {
    $repoRoot = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
} catch {
    Add-Finding -Findings ([ref]$findings) -Severity "STOP" -CheckId "repo_root_resolution_failed" -Message "Could not resolve AI_OS repo root." -Evidence $_.Exception.Message -NextSafeAction "Run from the AI_OS V2 repo and verify AGENTS.md and README.md exist."
    $repoRoot = (Get-Location).Path
}

$resolvedRegistryPath = Join-Path $repoRoot $RegistryPath
if (-not (Test-Path -LiteralPath $resolvedRegistryPath -PathType Leaf)) {
    Add-Finding -Findings ([ref]$findings) -Severity "STOP" -CheckId "registry_not_found" -Message "Execution classification registry was not found." -Evidence $RegistryPath -NextSafeAction "Create or restore the registry through approved APPLY before execution checks."
    $registry = $null
} else {
    try {
        $registry = Get-Content -LiteralPath $resolvedRegistryPath -Raw | ConvertFrom-Json
    } catch {
        Add-Finding -Findings ([ref]$findings) -Severity "STOP" -CheckId "registry_json_parse_failed" -Message "Execution classification registry JSON parse failed." -Evidence $_.Exception.Message -NextSafeAction "Repair registry JSON in a separate approved APPLY task."
        $registry = $null
    }
}

if ($null -ne $registry) {
    Test-RequiredRegistryFields -Registry $registry -Findings ([ref]$findings)
    if (($registry.PSObject.Properties.Name -contains "scripts") -and ($registry.PSObject.Properties.Name -contains "required_fields_per_script")) {
        Test-RegistryScriptEntries -Registry $registry -Findings ([ref]$findings)
    }
}

$registryByPath = @{}
$blockedEntries = @()
if ($null -ne $registry -and ($registry.PSObject.Properties.Name -contains "scripts")) {
    foreach ($entry in @($registry.scripts)) {
        if ($entry.PSObject.Properties.Name -contains "path") {
            $normalizedEntryPath = Normalize-RegistryPath -Path ([string]$entry.path)
            $registryByPath[$normalizedEntryPath] = $entry
            if (($entry.PSObject.Properties.Name -contains "classification") -and $entry.classification -eq "BLOCKED") {
                $blockedEntries += $entry
            }
        }
    }
}

$ps1Files = @()
foreach ($scanRoot in $ScanRoots) {
    $resolvedScanRoot = Join-Path $repoRoot $scanRoot
    if (-not (Test-Path -LiteralPath $resolvedScanRoot -PathType Container)) {
        Add-Finding -Findings ([ref]$findings) -Severity "STOP" -CheckId "scan_root_missing" -Message "Configured scan root does not exist." -Evidence $scanRoot -NextSafeAction "Review scan roots before using this guard."
        continue
    }

    $ps1Files += Get-ChildItem -LiteralPath $resolvedScanRoot -Recurse -File -Filter "*.ps1"
}

foreach ($file in $ps1Files | Sort-Object FullName -Unique) {
    $relativePath = (Get-RelativePath -BasePath $repoRoot -FullPath $file.FullName).Replace("\", "/")
    $normalizedRelativePath = Normalize-RegistryPath -Path $relativePath
    $content = Get-Content -LiteralPath $file.FullName -Raw

    if (-not $registryByPath.ContainsKey($normalizedRelativePath)) {
        Add-Finding -Findings ([ref]$findings) -Severity "STOP" -CheckId "unregistered_executable_script" -Message "Executable PowerShell script is not registered in the execution classification registry." -Evidence $normalizedRelativePath -NextSafeAction "Classify this script in the registry through a separate approved APPLY task or keep it blocked."
    }

    Test-DryRunWriteBehavior -RelativePath $normalizedRelativePath -Content $content -Findings ([ref]$findings)
    Test-BlockedScriptReferences -RelativePath $normalizedRelativePath -Content $content -BlockedEntries $blockedEntries -Findings ([ref]$findings)
}

$stopFindings = @($findings | Where-Object { $_.Severity -eq "STOP" })
$status = if ($stopFindings.Count -gt 0) { "STOP" } else { "PASS" }

Write-Host "AI_OS EXECUTION REGISTRY GUARD: $status"
Write-Host "Mode: report-only validation"
Write-Host "Repo root: $repoRoot"
Write-Host "Registry: $resolvedRegistryPath"
Write-Host "Scan roots: $($ScanRoots -join ', ')"
Write-Host "Scripts scanned: $(@($ps1Files).Count)"
Write-Host "Findings: $($findings.Count)"
Write-Host "No auto-repair, runtime execution, worker launch, startup launch, commit, or push was performed."

if ($findings.Count -gt 0) {
    Write-Host ""
    Write-Host "Findings:"
    foreach ($finding in $findings) {
        Write-Host ("[{0}] {1}: {2}" -f $finding.Severity, $finding.CheckId, $finding.Message)
        Write-Host ("  Evidence: {0}" -f $finding.Evidence)
        Write-Host ("  Next safe action: {0}" -f $finding.NextSafeAction)
    }
}

Write-Host ""
if ($status -eq "PASS") {
    Write-Host "Next safe action: Keep this guard read-only and add it to the validator chain only after registry coverage is reviewed."
    exit 0
}

Write-Host "Next safe action: Review STOP findings and update the registry or scripts only through a separate approved APPLY task."
exit 1
