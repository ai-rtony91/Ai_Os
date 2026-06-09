param(
    [string]$CommandText = "",
    [string]$LaneType = "READ_ONLY",
    [string]$ScopeHint = "repo",
    [switch]$ShowExamples
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:DEFAULT_PROCEED_POLICY_PATH = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..\orchestration\policy\AIOS_DEFAULT_PROCEED_POLICY.json"
$script:DEFAULT_PROCEED_OPTION = 2
$script:DEFAULT_PROCEED_MEANING = "continue next safe governed DRY_RUN/non-destructive step"
$script:ASK_USER_ONLY_ON_PROTECTED_GATE = $true

function Load-AiOsDefaultProceedPolicy {
    if (-not (Test-Path -LiteralPath $script:DEFAULT_PROCEED_POLICY_PATH -PathType Leaf)) {
        return [pscustomobject]@{
            DEFAULT_PROCEED_OPTION          = $script:DEFAULT_PROCEED_OPTION
            DEFAULT_PROCEED_MEANING         = $script:DEFAULT_PROCEED_MEANING
            ASK_USER_ONLY_ON_PROTECTED_GATE = $script:ASK_USER_ONLY_ON_PROTECTED_GATE
        }
    }

    try {
        $policyText = Get-Content -LiteralPath $script:DEFAULT_PROCEED_POLICY_PATH -Raw
        return ($policyText | ConvertFrom-Json)
    } catch {
        return [pscustomobject]@{
            DEFAULT_PROCEED_OPTION          = $script:DEFAULT_PROCEED_OPTION
            DEFAULT_PROCEED_MEANING         = $script:DEFAULT_PROCEED_MEANING
            ASK_USER_ONLY_ON_PROTECTED_GATE = $script:ASK_USER_ONLY_ON_PROTECTED_GATE
        }
    }
}

$script:DEFAULT_PROCEED_POLICY = Load-AiOsDefaultProceedPolicy

$script:DEFAULT_PROCEED_OPTION = [int]$script:DEFAULT_PROCEED_POLICY.DEFAULT_PROCEED_OPTION
$script:DEFAULT_PROCEED_MEANING = [string]$script:DEFAULT_PROCEED_POLICY.DEFAULT_PROCEED_MEANING
$script:ASK_USER_ONLY_ON_PROTECTED_GATE = [bool]$script:DEFAULT_PROCEED_POLICY.ASK_USER_ONLY_ON_PROTECTED_GATE

if ($script:DEFAULT_PROCEED_OPTION -lt 1) {
    $script:DEFAULT_PROCEED_OPTION = 1
}
if ($script:DEFAULT_PROCEED_OPTION -gt 3) {
    $script:DEFAULT_PROCEED_OPTION = 3
}
if ([string]::IsNullOrWhiteSpace($script:DEFAULT_PROCEED_MEANING)) {
    $script:DEFAULT_PROCEED_MEANING = "continue next safe governed DRY_RUN/non-destructive step"
}

function Get-OptionLabel {
    param([int]$Option)

    if ($Option -eq 1) {
        return "Option 1"
    }
    if ($Option -eq 2) {
        return "Option 2"
    }
    if ($Option -eq 3) {
        return "Option 3 / HARD STOP"
    }
    return "Option $Option"
}

function Normalize-CommandText {
    param([string]$Text)

    return (($Text -replace "\s+", " ").Trim())
}

function Test-IsScopedHint {
    param([string]$Hint)

    return -not [string]::IsNullOrWhiteSpace($Hint)
}

function Test-IsApprovedMutationLane {
    param([string]$Type)

    return $Type -match "(?i)APPLY|APPROVED|COMMIT|PUSH|MERGE|SYNC|BRANCH"
}

function New-Recommendation {
    param(
        [string]$Option,
        [string]$CommandClass,
        [string]$Reason,
        [string]$RiskLevel,
        [string]$ScopeMatch,
        [string]$StateChanging,
        [string]$StopRequired
    )

    [pscustomobject]@{
        RecommendedOption = $Option
        CommandClass = $CommandClass
        Reason = $Reason
        RiskLevel = $RiskLevel
        ScopeMatch = $ScopeMatch
        StateChangingCommand = $StateChanging
        StopRequired = $StopRequired
        DefaultProceedOption = "Option $($script:DEFAULT_PROCEED_OPTION)"
        DefaultProceedMeaning = $script:DEFAULT_PROCEED_MEANING
        AskUserOnlyOnProtectedGate = $script:ASK_USER_ONLY_ON_PROTECTED_GATE
    }
}

function Test-IsHardStopCommand {
    param([string]$Command)

    $hardStopPatterns = @(
        "^(?i)git\s+reset(\s|$)",
        "^(?i)git\s+clean(\s|$)",
        "^(?i)git\s+stash(\s|$)",
        "^(?i)git\s+push\b.*\s--force\b",
        "^(?i)git\s+push\b.*\s-f(\s|$)",
        "^(?i)Remove-Item(\s|$)",
        "^(?i)rm(\s|$)",
        "^(?i)del(\s|$)",
        "^(?i)Move-Item(\s|$)",
        "^(?i)Rename-Item(\s|$)",
        "^(?i)robocopy\b.*\s/MIR(\s|$)",
        "^(?i)Register-ScheduledTask(\s|$)",
        "^(?i)schtasks(\s|$)",
        "^(?i)git\s+branch\s+(-d|-D|--delete)\b",
        "^(?i)git\s+push\b.*\s--delete\b",
        "^(?i)gh\s+pr\s+merge\b.*--delete-branch(?!=false)\b",
        "(?i)\bsecret\b|\bcredential\b|\.env\b|id_rsa|token",
        "(?i)broker",
        "(?i)\boanda\b",
        "(?i)\bwebhook\b",
        "(?i)\blive[-_ ]?trading\b",
        "(?i)\breal[-_ ]?order\b",
        "(?i)\bT9\b|^[A-Z]:\\T9\\|\\T9\\",
        "^(?i)(powershell|pwsh)\b.*\s-File\s+.*\.ps1(\s|$)",
        "^(?i)&\s+.*\.ps1(\s|$)",
        "^(?i)(\./|\.\\|[A-Z]:\\).*\.ps1(\s|$)",
        "(?i)-Recurse\b.*\b(Force|Remove|Move|Copy)\b",
        "(?i)\bremove\b|\brename\b"
    )

    foreach ($pattern in $hardStopPatterns) {
        if ($Command -match $pattern) {
            return $true
        }
    }

    return $false
}

function Test-IsSafeReadOnlyCommand {
    param(
        [string]$Command,
        [string]$Hint
    )

    if (-not (Test-IsScopedHint -Hint $Hint)) {
        return $false
    }

    $safeExactPatterns = @(
        "^git status --short --branch$",
        "^git branch --show-current$",
        "^git rev-parse --short HEAD$",
        "^git diff --name-only$",
        "^git diff --cached --name-only$",
        "^git ls-files(\s|$)",
        "^gh pr view \d+\b",
        "^gh pr checks \d+\b",
        "^gh pr list\b"
    )

    foreach ($pattern in $safeExactPatterns) {
        if ($Command -match $pattern) {
            return $true
        }
    }

    if ($Command -match "^git log\b" -and $Command -match "(-1|-n\s+\d+|--max-count=\d+|--\s+[\w./\\-]+)") {
        return $true
    }

    if ($Command -match "^git show\s+[A-Fa-f0-9]{6,40}(:[\w./\\-]+)?(\s|$)") {
        return $true
    }

    if ($Command -match "^rg\b" -and $Command -match "\b(automation|docs|AGENTS\.md|README\.md)\b") {
        return $true
    }

    if ($Command -match "^(Test-Path|Get-Item|Get-ChildItem)\s+" -and $Command -notmatch "^[A-Za-z]+-[A-Za-z]+\s+[A-Z]:\\" ) {
        return $true
    }

    if ($Command -match "^Get-Content\s+.*-TotalCount\b" -and $Command -notmatch "^Get-Content\s+[A-Z]:\\") {
        return $true
    }

    return $false
}

function Test-IsScopedApprovedMutation {
    param(
        [string]$Command,
        [string]$Type,
        [string]$Hint
    )

    if (-not (Test-IsApprovedMutationLane -Type $Type) -or -not (Test-IsScopedHint -Hint $Hint)) {
        return $false
    }

    $mutationPatterns = @(
        "^git add [\w./\\-]+$",
        "^git commit -m `"[^`"]+`"$",
        "^git switch -c [\w./\\-]+$",
        "^git switch main$",
        "^git pull --ff-only origin main$",
        "^git push -u origin [\w./\\-]+$",
        "^gh pr create\b.*--base\s+\S+.*--head\s+\S+.*--title\s+.+",
        "^gh pr merge \d+\b.*--delete-branch=false\b",
        "^New-Item\b.*-Path\s+[\w./\\:-]+"
    )

    foreach ($pattern in $mutationPatterns) {
        if ($Command -match $pattern) {
            return $true
        }
    }

    return $false
}

function Get-AiOsCommandApprovalRecommendation {
    param(
        [string]$Command,
        [string]$Type,
        [string]$Hint
    )

    $normalized = Normalize-CommandText -Text $Command
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return New-Recommendation `
            -Option "Option 3 / HARD STOP" `
            -CommandClass "UNKNOWN" `
            -Reason "No command text was provided." `
            -RiskLevel "UNKNOWN" `
            -ScopeMatch "NO" `
            -StateChanging "UNKNOWN" `
            -StopRequired "YES"
    }

    if (Test-IsHardStopCommand -Command $normalized) {
        return New-Recommendation `
            -Option "Option 3 / HARD STOP" `
            -CommandClass "HARD_STOP_MUTATION" `
            -Reason "Command matches a destructive, script-execution, secret, scheduled-task, T9, or broad unsafe pattern." `
            -RiskLevel "HIGH" `
            -ScopeMatch "NO" `
            -StateChanging "YES" `
            -StopRequired "YES"
    }

    if (Test-IsSafeReadOnlyCommand -Command $normalized -Hint $Hint) {
        return New-Recommendation `
            -Option (Get-OptionLabel -Option $script:DEFAULT_PROCEED_OPTION) `
            -CommandClass "SAFE_READ_ONLY" `
            -Reason "Command is read-only, scoped, and narrow enough to reuse approval for this command pattern." `
            -RiskLevel "LOW" `
            -ScopeMatch "YES" `
            -StateChanging "NO" `
            -StopRequired "NO"
    }

    if (Test-IsScopedApprovedMutation -Command $normalized -Type $Type -Hint $Hint) {
        return New-Recommendation `
            -Option "Option 1" `
            -CommandClass "SCOPED_APPROVED_MUTATION" `
            -Reason "Command is an exact scoped mutation and should receive one-time approval only." `
            -RiskLevel "MEDIUM" `
            -ScopeMatch "YES" `
            -StateChanging "YES" `
            -StopRequired "NO"
    }

    return New-Recommendation `
        -Option "Option 3 / HARD STOP" `
        -CommandClass "UNKNOWN_OR_OUT_OF_SCOPE" `
        -Reason "Command is not recognized as scoped safe read-only or an exact approved mutation." `
        -RiskLevel "REVIEW" `
        -ScopeMatch "NO" `
        -StateChanging "UNKNOWN" `
        -StopRequired "YES"
}

function Write-Recommendation {
    param(
        [string]$Command,
        [pscustomobject]$Recommendation
    )

    Write-Host "Command: $Command"
    Write-Host "Recommended option: $($Recommendation.RecommendedOption)"
    Write-Host "Command class: $($Recommendation.CommandClass)"
    Write-Host "Reason: $($Recommendation.Reason)"
    Write-Host "Risk level: $($Recommendation.RiskLevel)"
    Write-Host "Scope match: $($Recommendation.ScopeMatch)"
    Write-Host "State-changing command: $($Recommendation.StateChangingCommand)"
    Write-Host "Stop required: $($Recommendation.StopRequired)"
    Write-Host "Default proceed option: $($Recommendation.DefaultProceedOption)"
    Write-Host "Default proceed meaning: $($Recommendation.DefaultProceedMeaning)"
    Write-Host "Ask user only on protected gate: $($Recommendation.AskUserOnlyOnProtectedGate)"
}

if ($ShowExamples) {
    $defaultSafeOption = Get-OptionLabel -Option $script:DEFAULT_PROCEED_OPTION
    $examples = @(
        [pscustomobject]@{ Command = "git status --short --branch"; Lane = "READ_ONLY"; Scope = "repo"; Expected = $defaultSafeOption },
        [pscustomobject]@{ Command = "gh pr view 204 --json number,url,state"; Lane = "READ_ONLY"; Scope = "repo"; Expected = $defaultSafeOption },
        [pscustomobject]@{ Command = "git add AGENTS.md"; Lane = "COMMIT_ONLY"; Scope = "AGENTS.md"; Expected = "Option 1" },
        [pscustomobject]@{ Command = "git commit -m `"docs/agents: add approval friction reduction standard`""; Lane = "COMMIT_ONLY"; Scope = "AGENTS.md"; Expected = "Option 1" },
        [pscustomobject]@{ Command = "gh pr merge 204 --merge --delete-branch=false"; Lane = "MERGE_ONLY"; Scope = "PR 204"; Expected = "Option 1" },
        [pscustomobject]@{ Command = "git push -u origin feature/default-proceed-policy-v1"; Lane = "PUSH_ONLY"; Scope = "repo"; Expected = "Option 1" },
        [pscustomobject]@{ Command = "git clean -fd"; Lane = "READ_ONLY"; Scope = "repo"; Expected = "Option 3 / HARD STOP" },
        [pscustomobject]@{ Command = "python automation/forex_engine/run_live_broker_demo.py --mode=live"; Lane = "READ_ONLY"; Scope = "repo"; Expected = "Option 3 / HARD STOP" },
        [pscustomobject]@{ Command = "robocopy C:\Dev\Ai.Os D:\backup /MIR"; Lane = "READ_ONLY"; Scope = "repo"; Expected = "Option 3 / HARD STOP" }
    )

    foreach ($example in $examples) {
        $recommendation = Get-AiOsCommandApprovalRecommendation -Command $example.Command -Type $example.Lane -Hint $example.Scope
        Write-Recommendation -Command $example.Command -Recommendation $recommendation
        Write-Host "Expected: $($example.Expected)"
        Write-Host ""
    }

    Write-Host "CommandText executed: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    exit 0
}

$result = Get-AiOsCommandApprovalRecommendation -Command $CommandText -Type $LaneType -Hint $ScopeHint
Write-Recommendation -Command (Normalize-CommandText -Text $CommandText) -Recommendation $result
Write-Host "CommandText executed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
