Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$chainPath = Join-Path $orchestrationRoot "validators\VALIDATOR_CHAIN_CONFIG_001.json"
$legacyChainPath = Join-Path $orchestrationRoot "validator_chain.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Get-JsonValue {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = ""
    )

    if ($null -eq $Object) { return $Default }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        $value = $Object.$Name
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            return $value
        }
    }
    return $Default
}

function Write-ValidatorSection {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [object[]]$Validators
    )

    Write-Host $Title

    if ($Validators.Count -eq 0) {
        Write-Host "  None"
        Write-Host ""
        return
    }

    foreach ($validator in ($Validators | Sort-Object order)) {
        $blockReasonValue = Get-JsonValue -Object $validator -Name "block_reason"
        $blockReason = if ([string]::IsNullOrWhiteSpace([string]$blockReasonValue)) { "none" } else { $blockReasonValue }

        $name = Get-JsonValue -Object $validator -Name "validator_name" -Default (Get-JsonValue -Object $validator -Name "name" -Default "UNKNOWN")
        $type = Get-JsonValue -Object $validator -Name "validator_type" -Default $(if ((Get-JsonValue -Object $validator -Name "required" -Default "false") -eq "True") { "required" } else { "optional" })
        $status = Get-JsonValue -Object $validator -Name "status" -Default "configured"

        Write-Host "  $($validator.order). $name"
        Write-Host "    ID: $(if ($validator.validator_id) { $validator.validator_id } else { $validator.name })"
        Write-Host "    Type: $type"
        Write-Host "    Status: $status"
        Write-Host "    Blocked: $(Get-JsonValue -Object $validator -Name 'blocked' -Default 'False')"
        Write-Host "    Block reason: $blockReason"
        Write-Host "    Command display: $(Get-JsonValue -Object $validator -Name 'command' -Default 'not configured in canonical config')"
        Write-Host "    Notes: $(Get-JsonValue -Object $validator -Name 'notes' -Default (Get-JsonValue -Object $validator -Name 'protects' -Default 'none'))"
        Write-Host ""
    }
}

$chain = if (Test-Path -LiteralPath $chainPath -PathType Leaf) { Read-JsonFile -Path $chainPath } else { Read-JsonFile -Path $legacyChainPath }
$validators = @($chain.validators)

Write-Host "AI_OS Validator Chain Display"
Write-Host "Mode: $($chain.mode)"
Write-Host "Chain: $(Get-JsonValue -Object $chain -Name 'chain_name' -Default (Get-JsonValue -Object $chain -Name 'chain_id' -Default 'UNKNOWN'))"
Write-Host "Purpose: $(Get-JsonValue -Object $chain -Name 'purpose' -Default 'Canonical validator chain config for APPLY, commit, and push gates.')"
Write-Host ""
Write-Host "Safety: display-only. No validators are run. No files are modified. No workers are launched."
Write-Host ""

if ($validators.Count -eq 0) {
    Write-Host "Validators: none found in validator_chain.example.json"
    exit 0
}

$requiredValidators = @($validators | Where-Object { (Get-JsonValue -Object $_ -Name "validator_type") -eq "required" -or (Get-JsonValue -Object $_ -Name "required") -eq "True" })
$optionalValidators = @($validators | Where-Object { (Get-JsonValue -Object $_ -Name "validator_type") -eq "optional" -or (Get-JsonValue -Object $_ -Name "required") -eq "False" })
$blockedValidators = @($validators | Where-Object { (Get-JsonValue -Object $_ -Name "blocked") -eq "True" -or (Get-JsonValue -Object $_ -Name "validator_type") -eq "blocked" -or (Get-JsonValue -Object $_ -Name "status") -eq "blocked" })

Write-Host "Validator summary:"
Write-Host "  Total validators: $($validators.Count)"
Write-Host "  Required validators: $($requiredValidators.Count)"
Write-Host "  Optional validators: $($optionalValidators.Count)"
Write-Host "  Blocked validators: $($blockedValidators.Count)"
Write-Host ""

Write-Host "Validator order:"
foreach ($validator in ($validators | Sort-Object order)) {
    $name = Get-JsonValue -Object $validator -Name "validator_name" -Default (Get-JsonValue -Object $validator -Name "name" -Default "UNKNOWN")
    $type = Get-JsonValue -Object $validator -Name "validator_type" -Default $(if ((Get-JsonValue -Object $validator -Name "required" -Default "false") -eq "True") { "required" } else { "optional" })
    $status = Get-JsonValue -Object $validator -Name "status" -Default "configured"
    Write-Host "  $($validator.order). $name [$type] - $status"
}
Write-Host ""

Write-ValidatorSection -Title "Required validators:" -Validators $requiredValidators
Write-ValidatorSection -Title "Optional validators:" -Validators $optionalValidators
Write-ValidatorSection -Title "Blocked validator status:" -Validators $blockedValidators

Write-Host "Next safe action: review validator order only; use a separate approved workflow before running validators."
