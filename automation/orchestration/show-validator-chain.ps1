Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$chainPath = Join-Path $orchestrationRoot "validator_chain.example.json"

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
        $blockReason = if ([string]::IsNullOrWhiteSpace([string]$validator.block_reason)) { "none" } else { $validator.block_reason }

        Write-Host "  $($validator.order). $($validator.validator_name)"
        Write-Host "    ID: $($validator.validator_id)"
        Write-Host "    Type: $($validator.validator_type)"
        Write-Host "    Status: $($validator.status)"
        Write-Host "    Blocked: $($validator.blocked)"
        Write-Host "    Block reason: $blockReason"
        Write-Host "    Command display: $($validator.command)"
        Write-Host "    Notes: $($validator.notes)"
        Write-Host ""
    }
}

$chain = Read-JsonFile -Path $chainPath
$validators = @($chain.validators)

Write-Host "AI_OS Validator Chain Display"
Write-Host "Mode: $($chain.mode)"
Write-Host "Chain: $($chain.chain_name)"
Write-Host "Purpose: $($chain.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No validators are run. No files are modified. No workers are launched."
Write-Host ""

if ($validators.Count -eq 0) {
    Write-Host "Validators: none found in validator_chain.example.json"
    exit 0
}

$requiredValidators = @($validators | Where-Object { $_.validator_type -eq "required" })
$optionalValidators = @($validators | Where-Object { $_.validator_type -eq "optional" })
$blockedValidators = @($validators | Where-Object { $_.blocked -eq $true -or $_.validator_type -eq "blocked" -or $_.status -eq "blocked" })

Write-Host "Validator summary:"
Write-Host "  Total validators: $($validators.Count)"
Write-Host "  Required validators: $($requiredValidators.Count)"
Write-Host "  Optional validators: $($optionalValidators.Count)"
Write-Host "  Blocked validators: $($blockedValidators.Count)"
Write-Host ""

Write-Host "Validator order:"
foreach ($validator in ($validators | Sort-Object order)) {
    Write-Host "  $($validator.order). $($validator.validator_name) [$($validator.validator_type)] - $($validator.status)"
}
Write-Host ""

Write-ValidatorSection -Title "Required validators:" -Validators $requiredValidators
Write-ValidatorSection -Title "Optional validators:" -Validators $optionalValidators
Write-ValidatorSection -Title "Blocked validator status:" -Validators $blockedValidators

Write-Host "Next safe action: review validator order only; use a separate approved workflow before running validators."
