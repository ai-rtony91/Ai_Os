param(
    [string]$OrchestrationRegistryPath = "",
    [string]$WindowRegistryPath = "",
    [string]$WindowLayoutsPath = "",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$PrimaryVisibleMarkers = @(
    "AI_OS MAIN CONTROL",
    "CODEX BUILD LANE",
    "VALIDATOR WORKER",
    "APPROVAL INBOX"
)

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

function ConvertTo-AddressBookKey {
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

function Get-PropertyValue {
    param(
        [AllowNull()]
        $Object,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($property) {
        return $property.Value
    }

    return $null
}

function Get-StringList {
    param([AllowNull()]$Value)

    if ($null -eq $Value) {
        return @()
    }

    return @($Value | ForEach-Object { "$_".Trim() } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Join-StringList {
    param([string[]]$Value)

    if (@($Value).Count -eq 0) {
        return ""
    }

    return (@($Value) -join "; ")
}

function Compare-StringList {
    param(
        [string[]]$Left,
        [string[]]$Right
    )

    $leftKeys = @{}
    foreach ($item in @($Left)) {
        $key = ConvertTo-AddressBookKey -Value $item
        if (-not [string]::IsNullOrWhiteSpace($key)) {
            $leftKeys[$key] = $item
        }
    }

    $rightKeys = @{}
    foreach ($item in @($Right)) {
        $key = ConvertTo-AddressBookKey -Value $item
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

function Add-Issue {
    param(
        [System.Collections.Generic.List[object]]$Target,

        [Parameter(Mandatory = $true)]
        [string]$Severity,

        [Parameter(Mandatory = $true)]
        [string]$Type,

        [Parameter(Mandatory = $true)]
        [string]$Marker,

        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $Target.Add([pscustomobject]@{
        severity = $Severity
        type = $Type
        marker = $Marker
        message = $Message
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
$issues = [System.Collections.Generic.List[object]]::new()

$windowByKey = @{}
foreach ($worker in $windowWorkers) {
    $marker = "$($worker.marker)"
    $markerKey = ConvertTo-AddressBookKey -Value $marker
    if (-not [string]::IsNullOrWhiteSpace($markerKey)) {
        $windowByKey[$markerKey] = $worker
    }

    $title = "$($worker.title)"
    $titleKey = ConvertTo-AddressBookKey -Value $title
    if (-not [string]::IsNullOrWhiteSpace($titleKey) -and -not $windowByKey.ContainsKey($titleKey)) {
        $windowByKey[$titleKey] = $worker
    }
}

$layoutMembershipByMarker = @{}
$presetProperties = @($windowLayouts.presets.PSObject.Properties)
foreach ($preset in $presetProperties) {
    foreach ($marker in @($preset.Value)) {
        $markerText = "$marker"
        $markerKey = ConvertTo-AddressBookKey -Value $markerText
        if ([string]::IsNullOrWhiteSpace($markerKey)) {
            continue
        }

        if (-not $layoutMembershipByMarker.ContainsKey($markerKey)) {
            $layoutMembershipByMarker[$markerKey] = @()
        }

        if ($layoutMembershipByMarker[$markerKey] -notcontains $preset.Name) {
            $layoutMembershipByMarker[$markerKey] += $preset.Name
        }
    }
}

$entries = @()
$matchedWindowKeys = @{}
foreach ($worker in $orchestrationWorkers) {
    $workerId = "$($worker.worker_id)"
    $windowMarker = "$($worker.window_marker)"
    $matchSource = "worker_id"
    $matchValue = $workerId
    if (-not [string]::IsNullOrWhiteSpace($windowMarker)) {
        $matchSource = "window_marker"
        $matchValue = $windowMarker
    }

    $matchKey = ConvertTo-AddressBookKey -Value $matchValue
    $windowWorker = $null
    if (-not [string]::IsNullOrWhiteSpace($matchKey) -and $windowByKey.ContainsKey($matchKey)) {
        $windowWorker = $windowByKey[$matchKey]
        $matchedWindowKeys[(ConvertTo-AddressBookKey -Value "$($windowWorker.marker)")] = $true
    }

    $marker = "$($worker.window_marker)"
    if ([string]::IsNullOrWhiteSpace($marker) -and $null -ne $windowWorker) {
        $marker = "$($windowWorker.marker)"
    }
    if ([string]::IsNullOrWhiteSpace($marker)) {
        $marker = $workerId
    }

    $markerKey = ConvertTo-AddressBookKey -Value $marker
    $layoutMembership = @()
    if ($layoutMembershipByMarker.ContainsKey($markerKey)) {
        $layoutMembership = @($layoutMembershipByMarker[$markerKey])
    }

    $orchestrationAllowed = Get-StringList -Value $worker.allowed_actions
    $windowAllowed = Get-StringList -Value (Get-PropertyValue -Object $windowWorker -Name "allowedActions")
    $orchestrationBlocked = Get-StringList -Value $worker.blocked_actions
    $windowBlocked = Get-StringList -Value (Get-PropertyValue -Object $windowWorker -Name "blockedActions")
    $nextCommand = Get-PropertyValue -Object $windowWorker -Name "nextCommand"
    if ($null -eq $nextCommand) {
        $nextCommand = Get-PropertyValue -Object $worker -Name "next_command"
    }

    $enabled = Get-PropertyValue -Object $windowWorker -Name "enabled"
    if ($null -eq $enabled) {
        $enabled = Get-PropertyValue -Object $worker -Name "enabled"
    }
    if ($null -eq $enabled) {
        $disabled = Get-PropertyValue -Object $worker -Name "disabled"
        if ($null -ne $disabled) {
            $enabled = -not [bool]$disabled
        }
    }

    $group = "Registered support workers"
    if ($PrimaryVisibleMarkers -contains $marker) {
        $group = "Primary visible crew"
    }

    $entryIssues = @()
    if ($null -eq $windowWorker) {
        $entryIssues += "missing_window_mapping"
        $severity = "WARN"
        if ($PrimaryVisibleMarkers -contains $marker) {
            $severity = "BLOCKED"
        }
        Add-Issue -Target $issues -Severity $severity -Type "missing_window_mapping" -Marker $marker -Message "No matching window identity worker found."
    }
    if ([string]::IsNullOrWhiteSpace("$nextCommand") -and $group -eq "Registered support workers") {
        $entryIssues += "missing_next_command"
        Add-Issue -Target $issues -Severity "WARN" -Type "missing_optional_field" -Marker $marker -Message "Support worker has no nextCommand value."
    }
    if ($null -eq $enabled -and $group -eq "Registered support workers") {
        $entryIssues += "missing_enabled"
        Add-Issue -Target $issues -Severity "WARN" -Type "missing_optional_field" -Marker $marker -Message "Support worker has no enabled value."
    }
    if (@($layoutMembership).Count -eq 0 -and $group -eq "Registered support workers") {
        $entryIssues += "missing_layout_membership"
        Add-Issue -Target $issues -Severity "WARN" -Type "missing_optional_field" -Marker $marker -Message "Support worker is not listed in any layout preset."
    }

    $rolePurpose = "$($worker.type) :: $($worker.purpose)"
    $windowRole = Get-PropertyValue -Object $windowWorker -Name "role"
    if ($null -ne $windowRole -and (ConvertTo-AddressBookKey -Value $rolePurpose) -ne (ConvertTo-AddressBookKey -Value "$windowRole") -and $group -eq "Registered support workers") {
        $entryIssues += "role_purpose_drift"
        Add-Issue -Target $issues -Severity "WARN" -Type "support_drift" -Marker $marker -Message "Support worker orchestration purpose differs from window role."
    }

    $blockedCompare = Compare-StringList -Left $orchestrationBlocked -Right $windowBlocked
    if ((@($blockedCompare.left_only).Count -gt 0 -or @($blockedCompare.right_only).Count -gt 0) -and $group -eq "Registered support workers") {
        $entryIssues += "blocked_action_drift"
        Add-Issue -Target $issues -Severity "WARN" -Type "support_drift" -Marker $marker -Message "Support worker blocked action lists differ."
    }

    $entries += [pscustomobject]@{
        group = $group
        worker_id = $workerId
        marker = $marker
        title = "$(Get-PropertyValue -Object $windowWorker -Name "title")"
        role_purpose = $rolePurpose
        window_role = "$windowRole"
        nextCommand = "$nextCommand"
        allowed_action_summary = Join-StringList -Value ($(if (@($orchestrationAllowed).Count -gt 0) { $orchestrationAllowed } else { $windowAllowed }))
        blocked_action_summary = Join-StringList -Value ($(if (@($orchestrationBlocked).Count -gt 0) { $orchestrationBlocked } else { $windowBlocked }))
        enabled = $enabled
        layout_presets = @($layoutMembership)
        match_key = $matchKey
        match_key_source = $matchSource
        mapped = ($null -ne $windowWorker)
        issues = @($entryIssues)
    }
}

foreach ($windowWorker in $windowWorkers) {
    $marker = "$($windowWorker.marker)"
    $markerKey = ConvertTo-AddressBookKey -Value $marker
    if ([string]::IsNullOrWhiteSpace($markerKey) -or $matchedWindowKeys.ContainsKey($markerKey)) {
        continue
    }

    $layoutMembership = @()
    if ($layoutMembershipByMarker.ContainsKey($markerKey)) {
        $layoutMembership = @($layoutMembershipByMarker[$markerKey])
    }

    $group = "Registered support workers"
    if ($PrimaryVisibleMarkers -contains $marker) {
        $group = "Primary visible crew"
        Add-Issue -Target $issues -Severity "BLOCKED" -Type "missing_orchestration_mapping" -Marker $marker -Message "Primary visible window worker has no orchestration worker mapping."
    } else {
        Add-Issue -Target $issues -Severity "WARN" -Type "window_only_support_worker" -Marker $marker -Message "Window worker has no orchestration worker mapping."
    }

    $entries += [pscustomobject]@{
        group = $group
        worker_id = ""
        marker = $marker
        title = "$($windowWorker.title)"
        role_purpose = ""
        window_role = "$($windowWorker.role)"
        nextCommand = "$($windowWorker.nextCommand)"
        allowed_action_summary = Join-StringList -Value (Get-StringList -Value $windowWorker.allowedActions)
        blocked_action_summary = Join-StringList -Value (Get-StringList -Value $windowWorker.blockedActions)
        enabled = (Get-PropertyValue -Object $windowWorker -Name "enabled")
        layout_presets = @($layoutMembership)
        match_key = $markerKey
        match_key_source = "window_registry_only"
        mapped = $false
        issues = @("missing_orchestration_mapping")
    }
}

$primaryEntries = @($entries | Where-Object { $_.group -eq "Primary visible crew" } | Sort-Object { [array]::IndexOf($PrimaryVisibleMarkers, $_.marker) })
$supportEntries = @($entries | Where-Object { $_.group -eq "Registered support workers" } | Sort-Object marker)
$mappedPrimaryMarkers = @($primaryEntries | Where-Object { $_.mapped } | ForEach-Object { $_.marker })

foreach ($marker in $PrimaryVisibleMarkers) {
    if ($mappedPrimaryMarkers -notcontains $marker) {
        Add-Issue -Target $issues -Severity "BLOCKED" -Type "primary_visible_worker_unmapped" -Marker $marker -Message "Primary visible worker is not fully mapped."
    }
}

$status = "PASS"
if (@($issues | Where-Object { $_.severity -eq "BLOCKED" }).Count -gt 0) {
    $status = "BLOCKED"
} elseif (@($issues | Where-Object { $_.severity -eq "WARN" }).Count -gt 0) {
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
        primary_visible_workers = $PrimaryVisibleMarkers.Count
        primary_visible_mapped = @($mappedPrimaryMarkers).Count
        registered_support_workers = $supportEntries.Count
        total_entries = $entries.Count
        issues = $issues.Count
        blockers = @($issues | Where-Object { $_.severity -eq "BLOCKED" }).Count
        warnings = @($issues | Where-Object { $_.severity -eq "WARN" }).Count
    }
    primary_visible_crew = @($primaryEntries)
    registered_support_workers = @($supportEntries)
    issues = @($issues)
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 10
} else {
    Write-Host "AI_OS Worker Address Book"
    Write-Host "Mode: READ_ONLY"
    Write-Host "Status: $status"
    Write-Host "Primary visible mapped: $(@($mappedPrimaryMarkers).Count)/$($PrimaryVisibleMarkers.Count)"
    Write-Host "Registered support workers: $($supportEntries.Count)"
    Write-Host ""

    Write-Host "Primary visible crew:"
    foreach ($entry in $primaryEntries) {
        Write-Host "  - $($entry.marker)"
        Write-Host "    worker_id: $($entry.worker_id)"
        Write-Host "    title: $($entry.title)"
        Write-Host "    role/purpose: $($entry.role_purpose)"
        Write-Host "    nextCommand: $($entry.nextCommand)"
        Write-Host "    allowed: $($entry.allowed_action_summary)"
        Write-Host "    blocked: $($entry.blocked_action_summary)"
        Write-Host "    enabled: $($entry.enabled)"
        Write-Host "    layout presets: $(@($entry.layout_presets) -join ', ')"
    }
    Write-Host ""

    Write-Host "Registered support workers:"
    if ($supportEntries.Count -eq 0) {
        Write-Host "  none"
    } else {
        foreach ($entry in $supportEntries) {
            Write-Host "  - $($entry.marker)"
            Write-Host "    worker_id: $($entry.worker_id)"
            Write-Host "    title: $($entry.title)"
            Write-Host "    role/purpose: $($entry.role_purpose)"
            Write-Host "    nextCommand: $($entry.nextCommand)"
            Write-Host "    allowed: $($entry.allowed_action_summary)"
            Write-Host "    blocked: $($entry.blocked_action_summary)"
            Write-Host "    enabled: $($entry.enabled)"
            Write-Host "    layout presets: $(@($entry.layout_presets) -join ', ')"
        }
    }
    Write-Host ""

    Write-Host "Issues:"
    if ($issues.Count -eq 0) {
        Write-Host "  none"
    } else {
        foreach ($issue in $issues) {
            Write-Host "  - $($issue.severity): $($issue.marker) :: $($issue.type) :: $($issue.message)"
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
