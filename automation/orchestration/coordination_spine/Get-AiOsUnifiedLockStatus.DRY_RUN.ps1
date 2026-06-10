[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$RepoRoot,
    [string]$LockRegistryPath,
    [string]$ClaimRegistryPath,
    [string]$InstanceLockPath,
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
}

if (-not $PSBoundParameters.ContainsKey('LockRegistryPath')) {
    $LockRegistryPath = Join-Path $RepoRoot 'automation\orchestration\locks\FILE_LOCK_REGISTRY.json'
}

if (-not $PSBoundParameters.ContainsKey('ClaimRegistryPath')) {
    $ClaimRegistryPath = Join-Path $RepoRoot 'automation\orchestration\claims\WORKER_CLAIM_REGISTRY_001.json'
}

if (-not $PSBoundParameters.ContainsKey('InstanceLockPath')) {
    $InstanceLockPath = Join-Path $RepoRoot 'control\cycle\supervisor.lock'
}

if (-not $PSBoundParameters.ContainsKey('OutputPath')) {
    $OutputPath = Join-Path $RepoRoot 'telemetry\coordination_spine\UNIFIED_LOCK_STATUS.json'
}

function Read-JsonDocument {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    $raw = Get-Content -LiteralPath $Path -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }

    return $raw | ConvertFrom-Json
}

function ConvertTo-RecordArray {
    param(
        [object]$InputObject,
        [string]$CollectionName
    )

    if ($null -eq $InputObject) {
        return @()
    }

    if ($InputObject -is [System.Collections.IEnumerable] -and -not ($InputObject -is [string])) {
        return @($InputObject)
    }

    $properties = @()
    if ($InputObject.PSObject.Properties.Name) {
        $properties = @($InputObject.PSObject.Properties.Name)
    }

    if ($properties -contains $CollectionName) {
        $collection = $InputObject.$CollectionName
        if ($null -eq $collection) {
            return @()
        }

        if ($collection -is [System.Collections.IEnumerable] -and -not ($collection -is [string])) {
            return @($collection)
        }

        return @($collection)
    }

    return @($InputObject)
}

function Get-PropertyText {
    param(
        [object]$InputObject,
        [string[]]$Names
    )

    foreach ($name in $Names) {
        if ($null -ne $InputObject -and $InputObject.PSObject.Properties.Name -contains $name) {
            $value = $InputObject.$name
            if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
                return [string]$value
            }
        }
    }

    return $null
}

function Get-LockStateBucket {
    param(
        [object]$Record
    )

    if ($null -eq $Record) {
        return 'UNKNOWN'
    }

    $rawState = (Get-PropertyText -InputObject $Record -Names @('state', 'status', 'lock_state', 'claim_status'))
    if ([string]::IsNullOrWhiteSpace($rawState)) {
        return 'UNKNOWN'
    }

    $rawState = $rawState.ToUpperInvariant()
    switch -Regex ($rawState) {
        '^(HELD|LOCKED|ACTIVE|ACQUIRED|CLAIMED|LOCKED_ACTIVE)$' { return 'HELD' }
        '^(STALE|EXPIRED|STALE_REVIEW_REQUIRED)$' { return 'STALE' }
        '^(RELEASED|FREE|AVAILABLE)$' { return 'RELEASED' }
        default { return 'UNKNOWN' }
    }
}

function Get-RecordPathKey {
    param(
        [object]$Record
    )

    return (Get-PropertyText -InputObject $Record -Names @('path', 'file_path', 'locked_path', 'packet_path', 'target_path'))
}

function Get-RecordOwnerKey {
    param(
        [object]$Record
    )

    return (Get-PropertyText -InputObject $Record -Names @('owner', 'owner_id', 'worker_id', 'claimant', 'lock_owner'))
}

function New-UnknownRecord {
    param(
        [string]$Source,
        [object]$Record,
        [string]$Reason
    )

    [pscustomobject]@{
        source = $Source
        reason = $Reason
        raw_state = (Get-PropertyText -InputObject $Record -Names @('state', 'status', 'lock_state', 'claim_status'))
        record = $Record
    }
}

function Test-IsPlaceholderClaimRecord {
    param(
        [object]$Record
    )

    if ($null -eq $Record) {
        return $false
    }

    foreach ($fieldName in @('worker_id', 'worker_name', 'packet_id', 'claim_timestamp', 'expiration_placeholder')) {
        $fieldValue = Get-PropertyText -InputObject $Record -Names @($fieldName)
        if (-not [string]::IsNullOrWhiteSpace($fieldValue) -and $fieldValue.ToUpperInvariant().Contains('PLACEHOLDER')) {
            return $true
        }
    }

    return $false
}

function Get-ClaimRecordArray {
    param(
        [object]$ClaimDocument
    )

    if ($null -eq $ClaimDocument) {
        return @()
    }

    if ($ClaimDocument.PSObject.Properties.Name -contains 'claims') {
        return @(ConvertTo-RecordArray -InputObject $ClaimDocument -CollectionName 'claims')
    }

    return @($ClaimDocument)
}

$lockDocument = Read-JsonDocument -Path $LockRegistryPath
$claimDocument = Read-JsonDocument -Path $ClaimRegistryPath

$lockRecords = ConvertTo-RecordArray -InputObject $lockDocument -CollectionName 'locks'
$claimRecords = Get-ClaimRecordArray -ClaimDocument $claimDocument

$sourceReaders = @(
    [pscustomobject]@{
        source = 'FILE_LOCK_REGISTRY.json'
        path = $LockRegistryPath
        exists = [bool](Test-Path -LiteralPath $LockRegistryPath)
        records_seen = @($lockRecords).Count
    },
    [pscustomobject]@{
        source = 'WORKER_CLAIM_REGISTRY_001.json'
        path = $ClaimRegistryPath
        exists = [bool](Test-Path -LiteralPath $ClaimRegistryPath)
        records_seen = @($claimRecords).Count
    },
    [pscustomobject]@{
        source = 'supervisor.lock'
        path = $InstanceLockPath
        exists = [bool](Test-Path -LiteralPath $InstanceLockPath)
        records_seen = if (Test-Path -LiteralPath $InstanceLockPath) { 1 } else { 0 }
    }
)

$unknownRecords = [System.Collections.Generic.List[object]]::new()
$claimBoundaryWarnings = [System.Collections.Generic.List[object]]::new()
$heldRecords = [System.Collections.Generic.List[object]]::new()
$staleRecords = [System.Collections.Generic.List[object]]::new()
$collisionCount = 0
$packetLockCount = 0
$workerClaimCount = 0

$pathOwners = @{}

foreach ($record in $lockRecords) {
    $bucket = Get-LockStateBucket -Record $record
    $pathKey = Get-RecordPathKey -Record $record
    $ownerKey = Get-RecordOwnerKey -Record $record

    if ($bucket -eq 'HELD') {
        $heldRecords.Add($record) | Out-Null
    }
    elseif ($bucket -eq 'STALE') {
        $staleRecords.Add($record) | Out-Null
    }
    elseif ($bucket -eq 'UNKNOWN') {
        $unknownRecords.Add((New-UnknownRecord -Source 'locks' -Record $record -Reason 'unmapped_lock_state')) | Out-Null
    }

    if (-not [string]::IsNullOrWhiteSpace((Get-PropertyText -InputObject $record -Names @('packet_id', 'packet', 'packet_reference')))) {
        $packetLockCount++
    }

    if (-not [string]::IsNullOrWhiteSpace($pathKey)) {
    if (-not $pathOwners.ContainsKey($pathKey)) {
            $pathOwners[$pathKey] = [System.Collections.Generic.HashSet[string]]::new()
        }

        if (-not [string]::IsNullOrWhiteSpace($ownerKey)) {
            [void]$pathOwners[$pathKey].Add($ownerKey)
        }
    }
}

foreach ($record in $claimRecords) {
    if (Test-IsPlaceholderClaimRecord -Record $record) {
        $claimBoundaryWarnings.Add((New-UnknownRecord -Source 'claims' -Record $record -Reason 'placeholder_claim_template_excluded')) | Out-Null
        continue
    }

    $workerClaimCount++
    $claimState = Get-PropertyText -InputObject $record -Names @('claim_status', 'status', 'state')
    $packetKey = Get-PropertyText -InputObject $record -Names @('packet_id', 'packet', 'packet_reference')

    if (-not [string]::IsNullOrWhiteSpace($packetKey)) {
        $packetLockCount++
    }

    if ($null -ne $record -and $record.PSObject.Properties.Name -contains 'expiration_placeholder') {
        $unknownRecords.Add((New-UnknownRecord -Source 'claims' -Record $record -Reason 'placeholder_claim_registry')) | Out-Null
    }
    elseif ([string]::IsNullOrWhiteSpace($claimState)) {
        $unknownRecords.Add((New-UnknownRecord -Source 'claims' -Record $record -Reason 'missing_claim_status')) | Out-Null
    }
}

$instanceLockCount = 0
if (Test-Path -LiteralPath $InstanceLockPath) {
    $instanceContent = Get-Content -LiteralPath $InstanceLockPath -Raw
    if (-not [string]::IsNullOrWhiteSpace($instanceContent)) {
        try {
            $instanceDocument = $instanceContent | ConvertFrom-Json
            $instanceState = Get-PropertyText -InputObject $instanceDocument -Names @('status', 'state', 'lock_state')
            if ([string]::IsNullOrWhiteSpace($instanceState) -or $instanceState.ToUpperInvariant() -notin @('RELEASED', 'FREE', 'AVAILABLE')) {
                $instanceLockCount = 1
            }
        }
        catch {
            $instanceLockCount = 1
        }
    }
}

foreach ($pathKey in $pathOwners.Keys) {
    if ($pathOwners[$pathKey].Count -gt 1) {
        $collisionCount++
        $unknownRecords.Add([pscustomobject]@{
            source = 'locks'
            reason = 'duplicate_lock_owner_collision'
            path = $pathKey
            owner_count = $pathOwners[$pathKey].Count
        }) | Out-Null
    }
}

$heldCount = $heldRecords.Count
$staleCount = $staleRecords.Count

$safetyStatus = if ($collisionCount -gt 0 -or $staleCount -gt 0 -or $unknownRecords.Count -gt 0) { 'REVIEW_REQUIRED' } else { 'PASS' }

$result = [ordered]@{
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    repo_root = $RepoRoot
    source_readers = $sourceReaders
    lock_sources_seen = @(
        'FILE_LOCK_REGISTRY.json',
        'WORKER_CLAIM_REGISTRY_001.json',
        'supervisor.lock'
    )
    held_locks_count = $heldCount
    stale_locks_count = $staleCount
    collision_count = $collisionCount
    worker_claim_count = $workerClaimCount
    packet_lock_count = $packetLockCount
    instance_lock_count = $instanceLockCount
    unknown_lock_records = @($unknownRecords)
    claim_registry_boundary_warnings = @($claimBoundaryWarnings)
    safety_status = $safetyStatus
    write_behavior = 'telemetry_only'
}

$json = $result | ConvertTo-Json -Depth 16

if ($Apply) {
    $outputDirectory = Split-Path -Parent $OutputPath
    if (-not (Test-Path -LiteralPath $outputDirectory)) {
        New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
    }

    $tempPath = Join-Path $outputDirectory ('.' + [System.IO.Path]::GetFileName($OutputPath) + '.tmp')
    [System.IO.File]::WriteAllText($tempPath, $json, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tempPath -Destination $OutputPath -Force
}

$json
