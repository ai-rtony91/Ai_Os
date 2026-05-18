param(
    [string]$OrchestrationRegistryPath = "",
    [string]$WindowRegistryPath = "",
    [string]$WindowLayoutsPath = "",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Resolve-AiOsDefaultPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return (Join-Path (Get-Location).Path $Path)
}

function ConvertTo-BridgeKey {
    param([AllowNull()][string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ""
    }

    $key = $Value.Trim().ToLowerInvariant()
    $key = [regex]::Replace($key, "[^a-z0-9]+", "_")
    return $key.Trim("_")
}

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label missing: $Path"
    }

    try {
        return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
    } catch {
        throw "$Label JSON parse failed: $Path :: $($_.Exception.Message)"
    }
}

function Get-StringList {
    param([AllowNull()]$Value)

    if ($null -eq $Value) {
        return @()
    }

    return @($Value | ForEach-Object { "$_".Trim() } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Compare-StringList {
    param(
        [string[]]$Left,
        [string[]]$Right
    )

    $leftKeys = @{}
    foreach ($item in @($Left)) {
        $key = ConvertTo-BridgeKey -Value $item
        if (-not [string]::IsNullOrWhiteSpace($key)) {
            $leftKeys[$key] = $item
        }
    }

    $rightKeys = @{}
    foreach ($item in @($Right)) {
        $key = ConvertTo-BridgeKey -Value $item
        if (-not [string]::IsNullOrWhiteSpace($key)) {
            $rightKeys[$key] = $item
        }
    }

    $leftOnly = @()
    foreach ($key in @($leftKeys.Keys | Sort-Object)) {
        if (-not $rightKeys.ContainsKey($key)) {
            $leftOnly += $leftKeys[$key]
        }
    }

    $rightOnly = @()
    foreach ($key in @($rightKeys.Keys | Sort-Object)) {
        if (-not $leftKeys.ContainsKey($key)) {
            $rightOnly += $rightKeys[$key]
        }
    }

    return [pscustomobject]@{
        left_only = $leftOnly
        right_only = $rightOnly
    }
}

function Get-PropertyValue {
    param(
        [Parameter(Mandatory = $true)]
        $Object,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $property = $Object.PSObject.Properties[$Name]
    if ($property) {
        return $property.Value
    }

    return $null
}

function Add-Drift {
    param(
        [System.Collections.Generic.List[object]]$Target,

        [Parameter(Mandatory = $true)]
        [string]$Type,

        [Parameter(Mandatory = $true)]
        [string]$WorkerKey,

        [AllowNull()]
        [string]$Orchestration,

        [AllowNull()]
        [string]$Window
    )

    $Target.Add([pscustomobject]@{
        type = $Type
        worker_key = $WorkerKey
        orchestration = $Orchestration
        window = $Window
    }) | Out-Null
}

$scriptName = Split-Path -Leaf $PSCommandPath

if ([string]::IsNullOrWhiteSpace($OrchestrationRegistryPath)) {
    $OrchestrationRegistryPath = Join-Path $PSScriptRoot "AIOS_WORKER_REGISTRY.json"
} else {
    $OrchestrationRegistryPath = Resolve-AiOsDefaultPath -Path $OrchestrationRegistryPath
}

if ([string]::IsNullOrWhiteSpace($WindowRegistryPath)) {
    $WindowRegistryPath = Join-Path $PSScriptRoot "..\..\window_identity\AIOS_WORKER_REGISTRY.json"
} else {
    $WindowRegistryPath = Resolve-AiOsDefaultPath -Path $WindowRegistryPath
}

if ([string]::IsNullOrWhiteSpace($WindowLayoutsPath)) {
    $WindowLayoutsPath = Join-Path $PSScriptRoot "..\..\window_identity\AIOS_WINDOW_LAYOUTS.json"
} else {
    $WindowLayoutsPath = Resolve-AiOsDefaultPath -Path $WindowLayoutsPath
}

$orchestrationRegistry = Read-JsonFile -Path $OrchestrationRegistryPath -Label "Orchestration worker registry"
$windowRegistry = Read-JsonFile -Path $WindowRegistryPath -Label "Window identity worker registry"
$windowLayouts = Read-JsonFile -Path $WindowLayoutsPath -Label "Window layout config"

$orchestrationWorkers = @($orchestrationRegistry.workers)
$windowWorkers = @($windowRegistry.workers)

$blockedReasons = [System.Collections.Generic.List[string]]::new()
$drifts = [System.Collections.Generic.List[object]]::new()

if ($orchestrationWorkers.Count -eq 0) {
    $blockedReasons.Add("Orchestration worker registry has no workers.") | Out-Null
}

if ($windowWorkers.Count -eq 0) {
    $blockedReasons.Add("Window identity worker registry has no workers.") | Out-Null
}

$orchestrationByKey = @{}
$orchestrationMatchSources = @{}
foreach ($worker in $orchestrationWorkers) {
    $workerId = "$($worker.worker_id)"
    $windowMarker = "$($worker.window_marker)"
    $matchSource = "worker_id"
    $matchValue = $workerId
    if (-not [string]::IsNullOrWhiteSpace($windowMarker)) {
        $matchSource = "window_marker"
        $matchValue = $windowMarker
    }

    $key = ConvertTo-BridgeKey -Value $matchValue
    if (-not [string]::IsNullOrWhiteSpace($key)) {
        $orchestrationByKey[$key] = $worker
        $orchestrationMatchSources[$key] = $matchSource
    }
}

$windowByKey = @{}
$windowMarkers = @{}
foreach ($worker in $windowWorkers) {
    $marker = "$($worker.marker)"
    $markerKey = ConvertTo-BridgeKey -Value $marker
    if (-not [string]::IsNullOrWhiteSpace($markerKey)) {
        $windowByKey[$markerKey] = $worker
        $windowMarkers[$marker] = $true
    }

    $title = "$($worker.title)"
    $titleKey = ConvertTo-BridgeKey -Value $title
    if (-not [string]::IsNullOrWhiteSpace($titleKey) -and -not $windowByKey.ContainsKey($titleKey)) {
        $windowByKey[$titleKey] = $worker
    }
}

$orchestrationOnly = @()
foreach ($key in @($orchestrationByKey.Keys | Sort-Object)) {
    if (-not $windowByKey.ContainsKey($key)) {
        $orchestrationOnly += "$($orchestrationByKey[$key].worker_id)"
    }
}

$windowOnly = @()
foreach ($windowWorker in $windowWorkers) {
    $markerKey = ConvertTo-BridgeKey -Value "$($windowWorker.marker)"
    $titleKey = ConvertTo-BridgeKey -Value "$($windowWorker.title)"
    if (([string]::IsNullOrWhiteSpace($markerKey) -or -not $orchestrationByKey.ContainsKey($markerKey)) -and
        ([string]::IsNullOrWhiteSpace($titleKey) -or -not $orchestrationByKey.ContainsKey($titleKey))) {
        $windowName = "$($windowWorker.marker)"
        if ([string]::IsNullOrWhiteSpace($windowName)) {
            $windowName = "$($windowWorker.title)"
        }
        if ($windowOnly -notcontains $windowName) {
            $windowOnly += $windowName
        }
    }
}

$matchedKeys = @($orchestrationByKey.Keys | Where-Object { $windowByKey.ContainsKey($_) } | Sort-Object)
$matchSourceCounts = [ordered]@{
    window_marker = 0
    worker_id = 0
}
$matchedBy = @()
foreach ($key in $matchedKeys) {
    $orchestrationWorker = $orchestrationByKey[$key]
    $windowWorker = $windowByKey[$key]
    $matchSource = "$($orchestrationMatchSources[$key])"
    if ($matchSourceCounts.Contains($matchSource)) {
        $matchSourceCounts[$matchSource]++
    }
    $matchedBy += [pscustomobject]@{
        worker_id = "$($orchestrationWorker.worker_id)"
        window_marker = "$($orchestrationWorker.window_marker)"
        window_registry_marker = "$($windowWorker.marker)"
        match_key = $key
        match_key_source = $matchSource
    }

    $orchestrationName = "$($orchestrationWorker.window_marker)"
    if ([string]::IsNullOrWhiteSpace($orchestrationName)) {
        $orchestrationName = "$($orchestrationWorker.worker_id)"
    }
    $windowTitle = "$($windowWorker.title)"
    $windowMarker = "$($windowWorker.marker)"
    if ((ConvertTo-BridgeKey -Value $orchestrationName) -ne (ConvertTo-BridgeKey -Value $windowTitle) -and
        (ConvertTo-BridgeKey -Value $orchestrationName) -ne (ConvertTo-BridgeKey -Value $windowMarker)) {
        Add-Drift -Target $drifts -Type "title_name_drift" -WorkerKey $key -Orchestration $orchestrationName -Window $windowTitle
    }

    $orchestrationRole = "$($orchestrationWorker.type) :: $($orchestrationWorker.purpose)"
    $windowRole = "$($windowWorker.role)"
    if ((ConvertTo-BridgeKey -Value $orchestrationRole) -ne (ConvertTo-BridgeKey -Value $windowRole)) {
        Add-Drift -Target $drifts -Type "role_type_purpose_drift" -WorkerKey $key -Orchestration $orchestrationRole -Window $windowRole
    }

    $blockedCompare = Compare-StringList -Left (Get-StringList -Value $orchestrationWorker.blocked_actions) -Right (Get-StringList -Value $windowWorker.blockedActions)
    if (@($blockedCompare.left_only).Count -gt 0 -or @($blockedCompare.right_only).Count -gt 0) {
        Add-Drift -Target $drifts -Type "blocked_action_drift" -WorkerKey $key -Orchestration ($blockedCompare.left_only -join "; ") -Window ($blockedCompare.right_only -join "; ")
    }

    $orchestrationNextCommand = Get-PropertyValue -Object $orchestrationWorker -Name "next_command"
    $windowNextCommand = Get-PropertyValue -Object $windowWorker -Name "nextCommand"
    if ($null -ne $orchestrationNextCommand -or $null -ne $windowNextCommand) {
        if ("$orchestrationNextCommand" -ne "$windowNextCommand") {
            Add-Drift -Target $drifts -Type "next_command_drift" -WorkerKey $key -Orchestration "$orchestrationNextCommand" -Window "$windowNextCommand"
        }
    }

    $orchestrationEnabled = Get-PropertyValue -Object $orchestrationWorker -Name "enabled"
    if ($null -eq $orchestrationEnabled) {
        $orchestrationDisabled = Get-PropertyValue -Object $orchestrationWorker -Name "disabled"
        if ($null -ne $orchestrationDisabled) {
            $orchestrationEnabled = -not [bool]$orchestrationDisabled
        }
    }

    $windowEnabled = Get-PropertyValue -Object $windowWorker -Name "enabled"
    if ($null -ne $orchestrationEnabled -or $null -ne $windowEnabled) {
        if ("$orchestrationEnabled" -ne "$windowEnabled") {
            Add-Drift -Target $drifts -Type "enabled_mismatch" -WorkerKey $key -Orchestration "$orchestrationEnabled" -Window "$windowEnabled"
        }
    }
}

$missingLayoutMarkers = @()
$presetProperties = @($windowLayouts.presets.PSObject.Properties)
if ($presetProperties.Count -eq 0) {
    $blockedReasons.Add("Window layout config has no presets.") | Out-Null
} else {
    foreach ($preset in $presetProperties) {
        foreach ($marker in @($preset.Value)) {
            if (-not $windowMarkers.ContainsKey("$marker")) {
                $missingLayoutMarkers += [pscustomobject]@{
                    preset = $preset.Name
                    marker = "$marker"
                }
            }
        }
    }
}

foreach ($missingMarker in $missingLayoutMarkers) {
    $blockedReasons.Add("Layout marker missing from window registry: preset=$($missingMarker.preset), marker=$($missingMarker.marker)") | Out-Null
}

$status = "PASS"
if ($blockedReasons.Count -gt 0) {
    $status = "BLOCKED"
} elseif ($orchestrationOnly.Count -gt 0 -or $windowOnly.Count -gt 0 -or $drifts.Count -gt 0) {
    $status = "WARN"
}

$result = [pscustomobject]@{
    status = $status
    script = $scriptName
    mode = "READ_ONLY"
    files = [pscustomobject]@{
        orchestration_registry = $OrchestrationRegistryPath
        window_registry = $WindowRegistryPath
        window_layouts = $WindowLayoutsPath
    }
    counts = [pscustomobject]@{
        orchestration_workers = $orchestrationWorkers.Count
        window_workers = $windowWorkers.Count
        matched_workers = $matchedKeys.Count
        matched_by_window_marker = $matchSourceCounts["window_marker"]
        matched_by_worker_id = $matchSourceCounts["worker_id"]
        orchestration_only = $orchestrationOnly.Count
        window_only = $windowOnly.Count
        drift_items = $drifts.Count
        missing_layout_markers = $missingLayoutMarkers.Count
        blockers = $blockedReasons.Count
    }
    orchestration_only = $orchestrationOnly
    window_only = $windowOnly
    matched_by = @($matchedBy)
    drift = @($drifts)
    missing_layout_markers = @($missingLayoutMarkers)
    blockers = @($blockedReasons)
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host "AI_OS Worker Registry Bridge"
    Write-Host "Mode: READ_ONLY"
    Write-Host "Status: $status"
    Write-Host "Orchestration workers: $($orchestrationWorkers.Count)"
    Write-Host "Window workers: $($windowWorkers.Count)"
    Write-Host "Matched workers: $($matchedKeys.Count)"
    Write-Host "Matched by window_marker: $($matchSourceCounts["window_marker"])"
    Write-Host "Matched by worker_id fallback: $($matchSourceCounts["worker_id"])"
    Write-Host ""

    Write-Host "Workers only in orchestration registry:"
    if ($orchestrationOnly.Count -eq 0) {
        Write-Host "  none"
    } else {
        foreach ($item in $orchestrationOnly) {
            Write-Host "  - $item"
        }
    }

    Write-Host "Workers only in window registry:"
    if ($windowOnly.Count -eq 0) {
        Write-Host "  none"
    } else {
        foreach ($item in $windowOnly) {
            Write-Host "  - $item"
        }
    }

    Write-Host "Drift:"
    if ($drifts.Count -eq 0) {
        Write-Host "  none"
    } else {
        foreach ($drift in $drifts) {
            Write-Host "  - $($drift.type): $($drift.worker_key)"
            Write-Host "    orchestration: $($drift.orchestration)"
            Write-Host "    window: $($drift.window)"
        }
    }

    Write-Host "Layout markers missing from window registry:"
    if ($missingLayoutMarkers.Count -eq 0) {
        Write-Host "  none"
    } else {
        foreach ($item in $missingLayoutMarkers) {
            Write-Host "  - $($item.preset): $($item.marker)"
        }
    }

    Write-Host "Blockers:"
    if ($blockedReasons.Count -eq 0) {
        Write-Host "  none"
    } else {
        foreach ($item in $blockedReasons) {
            Write-Host "  - $item"
        }
    }

    Write-Host ""
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
}

if ($status -eq "BLOCKED") {
    exit 2
}

exit 0
