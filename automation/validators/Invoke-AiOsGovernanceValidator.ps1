param(
    [string]$InputPath,
    [switch]$SampleCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($SampleCheck) {
    python automation/validators/aios_governance_validator.py --sample-check
    exit $LASTEXITCODE
}

if ([string]::IsNullOrWhiteSpace($InputPath)) {
    throw "InputPath is required unless -SampleCheck is used."
}

python automation/validators/aios_governance_validator.py --input $InputPath
