[CmdletBinding()]
param(
    [switch]$StrictExit
)

$ErrorActionPreference = "Stop"

$schemaRoot = "schemas/aios/orchestration"
$repoRoot = (Get-Location).Path

$schemaFiles = @(
    "WORKER_REGISTRY_SCHEMA.json",
    "WORKER_PROFILE_SCHEMA.json",
    "WORKER_INBOX_SCHEMA.json",
    "WORK_PACKET_SCHEMA.json",
    "COMMAND_QUEUE_SCHEMA.json",
    "APPROVAL_INBOX_SCHEMA.json",
    "APPLY_APPROVAL_GATE_SCHEMA.json",
    "VALIDATOR_OUTPUT_SCHEMA.json",
    "COMMIT_PACKAGE_SCHEMA.json",
    "LOCK_REGISTRY_SCHEMA.json",
    "RUNTIME_VISIBILITY_SCHEMA.json",
    "ORCHESTRATION_SCHEMA_INDEX.json"
)

$targetMap = @(
    [pscustomobject]@{ Schema = "WORKER_REGISTRY_SCHEMA.json"; Target = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"; Optional = $false },
    [pscustomobject]@{ Schema = "WORKER_PROFILE_SCHEMA.json"; Target = "automation/orchestration/workers/AIOS_WORKER_PROFILES.json"; Optional = $false },
    [pscustomobject]@{ Schema = "WORKER_INBOX_SCHEMA.json"; Target = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"; Optional = $false },
    [pscustomobject]@{ Schema = "COMMAND_QUEUE_SCHEMA.json"; Target = "automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json"; Optional = $false },
    [pscustomobject]@{ Schema = "APPROVAL_INBOX_SCHEMA.json"; Target = "automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json"; Optional = $true },
    [pscustomobject]@{ Schema = "APPLY_APPROVAL_GATE_SCHEMA.json"; Target = "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"; Optional = $false },
    [pscustomobject]@{ Schema = "COMMIT_PACKAGE_SCHEMA.json"; Target = "automation/orchestration/commit_packages/COMMIT_PACKAGE_MANIFEST_001.json"; Optional = $false },
    [pscustomobject]@{ Schema = "LOCK_REGISTRY_SCHEMA.json"; Target = "automation/orchestration/locks/FILE_LOCK_REGISTRY_001.json"; Optional = $false },
    [pscustomobject]@{ Schema = "RUNTIME_VISIBILITY_SCHEMA.json"; Target = "apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json"; Optional = $false }
)

function Read-JsonObject {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    try {
        return [pscustomobject]@{
            Result = "PASS"
            Value = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
            Error = $null
        }
    }
    catch {
        return [pscustomobject]@{
            Result = "FAIL"
            Value = $null
            Error = $_.Exception.Message
        }
    }
}

function Get-RequiredGroups {
    param(
        [Parameter(Mandatory = $true)][object]$Schema
    )

    $groups = New-Object System.Collections.Generic.List[object]

    if ($Schema.PSObject.Properties.Name -contains "required") {
        $rootRequired = @($Schema.required)
        if ($rootRequired.Count -gt 0) {
            $groups.Add([pscustomobject]@{ Kind = "required"; Fields = $rootRequired }) | Out-Null
        }
    }

    foreach ($blockName in @("anyOf", "oneOf")) {
        if (-not ($Schema.PSObject.Properties.Name -contains $blockName)) {
            continue
        }

        $choices = @($Schema.$blockName)
        $choiceIndex = 0
        foreach ($choice in $choices) {
            $choiceIndex += 1
            if ($choice.PSObject.Properties.Name -contains "required") {
                $choiceRequired = @($choice.required)
                if ($choiceRequired.Count -gt 0) {
                    $groups.Add([pscustomobject]@{
                        Kind = $blockName
                        Choice = $choiceIndex
                        Fields = $choiceRequired
                    }) | Out-Null
                }
            }
        }
    }

    return @($groups)
}

function Get-SchemaChoiceRequiredFields {
    param(
        [Parameter(Mandatory = $true)][object]$Schema,
        [Parameter(Mandatory = $true)][object]$Choice
    )

    if ($Choice.PSObject.Properties.Name -contains "required") {
        return @($Choice.required)
    }

    if ($Choice.PSObject.Properties.Name -contains '$ref') {
        $ref = [string]$Choice.'$ref'
        if ($ref -like '#/$defs/*' -and ($Schema.PSObject.Properties.Name -contains '$defs')) {
            $defName = $ref.Substring('#/$defs/'.Length)
            $defs = $Schema.'$defs'
            if ($defs.PSObject.Properties.Name -contains $defName) {
                $definition = $defs.$defName
                if ($definition.PSObject.Properties.Name -contains "required") {
                    return @($definition.required)
                }
            }
        }
    }

    return @()
}

function Test-TopLevelContract {
    param(
        [Parameter(Mandatory = $true)][object]$Schema,
        [Parameter(Mandatory = $true)][object]$Target
    )

    $targetFields = @($Target.PSObject.Properties.Name)
    $notes = New-Object System.Collections.Generic.List[string]
    $result = "PASS"

    $rootRequired = @()
    if ($Schema.PSObject.Properties.Name -contains "required") {
        $rootRequired = @($Schema.required)
    }

    $missingRoot = @($rootRequired | Where-Object { $_ -notin $targetFields })
    if ($missingRoot.Count -gt 0) {
        $result = "PARTIAL"
        $notes.Add("Missing required: $($missingRoot -join ', ')") | Out-Null
    }

    foreach ($blockName in @("anyOf", "oneOf")) {
        if (-not ($Schema.PSObject.Properties.Name -contains $blockName)) {
            continue
        }

        $choices = @($Schema.$blockName)
        if ($choices.Count -eq 0) {
            continue
        }

        $matched = $false
        $choiceNotes = New-Object System.Collections.Generic.List[string]
        foreach ($choice in $choices) {
            $required = @(Get-SchemaChoiceRequiredFields -Schema $Schema -Choice $choice)
            if ($required.Count -eq 0) {
                continue
            }
            $missing = @($required | Where-Object { $_ -notin $targetFields })
            if ($missing.Count -eq 0) {
                $matched = $true
                break
            }
            $choiceNotes.Add("[$($required -join ', ')] missing [$($missing -join ', ')]") | Out-Null
        }

        if (-not $matched) {
            $result = "PARTIAL"
            $notes.Add("$blockName group not satisfied: $($choiceNotes -join '; ')") | Out-Null
        }
    }

    if ($notes.Count -eq 0) {
        $notes.Add("Top-level required fields present.") | Out-Null
    }

    return [pscustomobject]@{
        Result = $result
        Notes = ($notes -join " ")
    }
}

function Test-TargetFile {
    param(
        [Parameter(Mandatory = $true)][string]$SchemaName,
        [Parameter(Mandatory = $true)][string]$TargetPath,
        [bool]$Optional = $false
    )

    $schemaPath = Join-Path $schemaRoot $SchemaName
    if (-not (Test-Path -LiteralPath $schemaPath -PathType Leaf)) {
        return [pscustomobject]@{ Schema = $SchemaName; Target = $TargetPath; Result = "FAIL"; Notes = "Schema file missing." }
    }

    $schemaRead = Read-JsonObject -Path $schemaPath
    if ($schemaRead.Result -eq "FAIL") {
        return [pscustomobject]@{ Schema = $SchemaName; Target = $TargetPath; Result = "FAIL"; Notes = "Schema JSON parse failed: $($schemaRead.Error)" }
    }

    if (-not (Test-Path -LiteralPath $TargetPath -PathType Leaf)) {
        $result = if ($Optional) { "UNKNOWN" } else { "UNKNOWN" }
        $note = if ($Optional) { "Optional target missing; state is UNKNOWN, not PASS." } else { "Target missing; state is UNKNOWN." }
        return [pscustomobject]@{ Schema = $SchemaName; Target = $TargetPath; Result = $result; Notes = $note }
    }

    $targetRead = Read-JsonObject -Path $TargetPath
    if ($targetRead.Result -eq "FAIL") {
        return [pscustomobject]@{ Schema = $SchemaName; Target = $TargetPath; Result = "FAIL"; Notes = "Target JSON parse failed: $($targetRead.Error)" }
    }

    $contract = Test-TopLevelContract -Schema $schemaRead.Value -Target $targetRead.Value
    return [pscustomobject]@{ Schema = $SchemaName; Target = $TargetPath; Result = $contract.Result; Notes = $contract.Notes }
}

function Get-GitValue {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    try {
        $output = & git @Arguments 2>$null
        if ($LASTEXITCODE -ne 0) {
            return "UNKNOWN"
        }
        return (($output | Out-String).Trim())
    }
    catch {
        return "UNKNOWN"
    }
}

function Write-ResultTable {
    param([Parameter(Mandatory = $true)][object[]]$Rows)

    Write-Host "| Schema | Target | Result | Notes |"
    Write-Host "|---|---|---|---|"
    foreach ($row in $Rows) {
        $notes = ([string]$row.Notes).Replace("|", "/")
        Write-Host "| $($row.Schema) | $($row.Target) | $($row.Result) | $notes |"
    }
}

function Get-SampleSummary {
    param(
        [Parameter(Mandatory = $true)][object[]]$Rows
    )

    return [pscustomobject]@{
        inspected = @($Rows).Count
        pass = @($Rows | Where-Object { $_.Result -eq "PASS" }).Count
        partial = @($Rows | Where-Object { $_.Result -eq "PARTIAL" }).Count
        fail = @($Rows | Where-Object { $_.Result -eq "FAIL" }).Count
        unknown = @($Rows | Where-Object { $_.Result -eq "UNKNOWN" }).Count
    }
}

$schemaParseRows = foreach ($schemaName in $schemaFiles) {
    $schemaPath = Join-Path $schemaRoot $schemaName
    if (-not (Test-Path -LiteralPath $schemaPath -PathType Leaf)) {
        [pscustomobject]@{ Schema = $schemaName; Result = "FAIL"; Notes = "Schema file missing." }
        continue
    }

    $read = Read-JsonObject -Path $schemaPath
    [pscustomobject]@{
        Schema = $schemaName
        Result = $read.Result
        Notes = if ($read.Result -eq "PASS") { "JSON parses." } else { $read.Error }
    }
}

$targetRows = foreach ($mapping in $targetMap) {
    Test-TargetFile -SchemaName $mapping.Schema -TargetPath $mapping.Target -Optional $mapping.Optional
}

$workPacketRows = @()
$workPacketSchema = "WORK_PACKET_SCHEMA.json"
$workPacketRoot = "automation/orchestration/work_packets"
if (Test-Path -LiteralPath $workPacketRoot -PathType Container) {
    $workPacketRows = @(Get-ChildItem -LiteralPath $workPacketRoot -Recurse -Filter "*.json" -File |
        Select-Object -First 50 |
        ForEach-Object { Test-TargetFile -SchemaName $workPacketSchema -TargetPath $_.FullName -Optional $false })
}

$validatorRows = @()
$validatorSchema = "VALIDATOR_OUTPUT_SCHEMA.json"
$validatorRoot = "automation/orchestration/validators"
if (Test-Path -LiteralPath $validatorRoot -PathType Container) {
    $validatorRows = @(Get-ChildItem -LiteralPath $validatorRoot -Filter "*.json" -File |
        Select-Object -First 50 |
        ForEach-Object { Test-TargetFile -SchemaName $validatorSchema -TargetPath $_.FullName -Optional $false })
}

$allRows = @($schemaParseRows + $targetRows + $workPacketRows + $validatorRows)
$schemaParseResult = if (@($schemaParseRows | Where-Object { $_.Result -eq "FAIL" }).Count -gt 0) {
    "FAIL"
}
elseif (@($schemaParseRows | Where-Object { $_.Result -ne "PASS" }).Count -gt 0) {
    "PARTIAL"
}
else {
    "PASS"
}

$overallResult = if (@($allRows | Where-Object { $_.Result -eq "FAIL" }).Count -gt 0) {
    "FAIL"
}
elseif (@($allRows | Where-Object { $_.Result -in @("PARTIAL", "UNKNOWN") }).Count -gt 0) {
    "PARTIAL"
}
else {
    "PASS"
}

$workPacketSummary = Get-SampleSummary -Rows $workPacketRows
$validatorSummary = Get-SampleSummary -Rows $validatorRows

Write-Host "AI_OS ORCHESTRATION SCHEMA CONTRACT VALIDATION - DRY_RUN"
Write-Host ""
Write-Host "Repo:"
Write-Host "- $repoRoot"
Write-Host "- branch: $(Get-GitValue -Arguments @('branch', '--show-current'))"
Write-Host "- git status summary: $(Get-GitValue -Arguments @('status', '--short', '--branch'))"
Write-Host ""
Write-Host "Schema parse result:"
Write-Host "- $schemaParseResult"
Write-Host ""
Write-Host "Target validation results:"
Write-ResultTable -Rows $targetRows
Write-Host ""
Write-Host "Work packet sample results:"
Write-Host "- inspected: $($workPacketSummary.inspected)"
Write-Host "- pass: $($workPacketSummary.pass)"
Write-Host "- partial: $($workPacketSummary.partial)"
Write-Host "- fail: $($workPacketSummary.fail)"
Write-Host "- unknown: $($workPacketSummary.unknown)"
Write-Host ""
Write-Host "Validator output sample results:"
Write-Host "- inspected: $($validatorSummary.inspected)"
Write-Host "- pass: $($validatorSummary.pass)"
Write-Host "- partial: $($validatorSummary.partial)"
Write-Host "- fail: $($validatorSummary.fail)"
Write-Host "- unknown: $($validatorSummary.unknown)"
Write-Host ""
Write-Host "Overall result:"
Write-Host "- $overallResult"
Write-Host ""
Write-Host "Safety:"
Write-Host "- Files edited by script: NO"
Write-Host "- Runtime state changed: NO"
Write-Host "- Packets moved: NO"
Write-Host "- Approval state changed: NO"
Write-Host "- Services started: NO"
Write-Host "- Secrets touched: NO"
Write-Host "- Live trading touched: NO"
Write-Host "- Commit performed: NO"
Write-Host "- Push performed: NO"
Write-Host ""
Write-Host "Evidence note: Validator output is evidence only. PASS does not approve APPLY, commit, push, deploy, or protected actions."

if ($StrictExit -and $overallResult -eq "FAIL") {
    exit 1
}

exit 0
