[CmdletBinding()]
param(
    [ValidateSet("DRY_RUN", "APPLY")]
    [string]$Mode = "DRY_RUN",
    [string]$CommandText = "",
    [string]$PacketPath = "",
    [string]$PolicyPath = "",
    [string]$RepoRoot = "",
    [string]$WorkerId = "",
    [string]$TaskId = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-AiOsJson {
    param([Parameter(Mandatory = $true)]$Value)

    $Value | ConvertTo-Json -Depth 16 -Compress:$false
}

function New-AiOsGateDecision {
    param(
        [string]$Decision = "BLOCKED_ERROR",
        [string]$Tier = "ERROR",
        [string]$Reason = "",
        [string]$BlockedReason = "",
        [bool]$RequiresUserApproval = $true,
        [string]$CommandPreview = "",
        [string]$ResolvedPolicyPath = "",
        [bool]$PolicyLoaded = $false,
        [string]$PolicyId = "",
        [string]$PolicyVersion = "",
        [string[]]$PolicyFieldsConsumed = @(),
        [bool]$HardStopPresent = $false,
        [string]$HardStopDecision = "UNKNOWN",
        [object[]]$MatchedPolicyPatterns = @(),
        [object[]]$MatchedInternalPatterns = @(),
        [object[]]$MatchedScopeGuards = @(),
        [string[]]$MatchedProtectedPaths = @(),
        [string[]]$MatchedForbiddenPatterns = @(),
        [string[]]$MatchedHardExclusions = @()
    )

    [ordered]@{
        decision = $Decision
        tier = $Tier
        mode = $Mode
        worker_id = $WorkerId
        task_id = $TaskId
        command_preview = $CommandPreview
        policy_path = $ResolvedPolicyPath
        policy_loaded = $PolicyLoaded
        policy_id = $PolicyId
        policy_version = $PolicyVersion
        policy_fields_consumed = @($PolicyFieldsConsumed)
        hard_stop_present = $HardStopPresent
        hard_stop_decision = $HardStopDecision
        matched_policy_patterns = @($MatchedPolicyPatterns)
        matched_internal_patterns = @($MatchedInternalPatterns)
        matched_scope_guards = @($MatchedScopeGuards)
        matched_protected_paths = @($MatchedProtectedPaths)
        matched_forbidden_patterns = @($MatchedForbiddenPatterns)
        matched_hard_exclusions = @($MatchedHardExclusions)
        reason = $Reason
        blocked_reason = $BlockedReason
        requires_user_approval = $RequiresUserApproval
        checked_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
}

function Resolve-AiOsRepoRoot {
    param([string]$RequestedRepoRoot)

    if (-not [string]::IsNullOrWhiteSpace($RequestedRepoRoot)) {
        return (Resolve-Path -LiteralPath $RequestedRepoRoot).Path
    }

    $scriptRoot = Split-Path -Parent $PSCommandPath
    return (Resolve-Path -LiteralPath (Join-Path $scriptRoot "..\..\..")).Path
}

function Get-AiOsPropertyValue {
    param(
        [AllowNull()]$InputObject,
        [string]$Name,
        $Default = $null
    )

    if ($null -eq $InputObject) {
        return $Default
    }

    if ($InputObject.PSObject.Properties.Name -contains $Name) {
        return $InputObject.$Name
    }

    return $Default
}

function Get-AiOsPacketCommand {
    param([string]$RequestedPacketPath)

    if ([string]::IsNullOrWhiteSpace($RequestedPacketPath)) {
        return ""
    }

    if (-not (Test-Path -LiteralPath $RequestedPacketPath -PathType Leaf)) {
        return ""
    }

    $packet = Get-Content -LiteralPath $RequestedPacketPath -Raw | ConvertFrom-Json
    foreach ($field in @("command_preview", "command_text", "recommended_command", "validation_command")) {
        $value = [string](Get-AiOsPropertyValue -InputObject $packet -Name $field -Default "")
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            return $value
        }
    }

    return ""
}

function Get-AiOsPolicy {
    param([string]$ResolvedPolicyPath)

    if ([string]::IsNullOrWhiteSpace($ResolvedPolicyPath) -or -not (Test-Path -LiteralPath $ResolvedPolicyPath -PathType Leaf)) {
        return $null
    }

    return Get-Content -LiteralPath $ResolvedPolicyPath -Raw | ConvertFrom-Json
}

function Test-AiOsPatternMatch {
    param(
        [string]$Command,
        [string]$Pattern
    )

    if ([string]::IsNullOrWhiteSpace($Command) -or [string]::IsNullOrWhiteSpace($Pattern)) {
        return $false
    }

    $normalizedCommand = ($Command -replace "\\", "/")
    $normalizedPattern = ([string]$Pattern -replace "\\", "/")

    if ($normalizedCommand -like $normalizedPattern) {
        return $true
    }

    $trimmed = $normalizedPattern.Trim("*")
    if ($trimmed.Length -gt 0 -and $normalizedCommand.IndexOf($trimmed, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
        return $true
    }

    if ($normalizedPattern.EndsWith("/") -and $normalizedCommand.IndexOf($normalizedPattern, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
        return $true
    }

    return $false
}

function Find-AiOsPatternMatches {
    param(
        [string]$Command,
        [string[]]$Patterns
    )

    $foundMatches = [System.Collections.Generic.List[string]]::new()
    foreach ($pattern in @($Patterns)) {
        if (Test-AiOsPatternMatch -Command $Command -Pattern ([string]$pattern)) {
            $foundMatches.Add([string]$pattern) | Out-Null
        }
    }

    return @($foundMatches)
}

function Get-AiOsInternalRiskMatches {
    param([string]$Command)

    $patterns = @(
        @{ id = "broker"; pattern = "(?i)\bbroker\b" },
        @{ id = "oanda"; pattern = "(?i)\boanda\b" },
        @{ id = "api_key"; pattern = "(?i)\bapi\s*key\b|(?i)\bapi[_-]?key\b" },
        @{ id = "secret"; pattern = "(?i)\bsecrets?\b" },
        @{ id = "credential"; pattern = "(?i)\bcredentials?\b" },
        @{ id = "live_order"; pattern = "(?i)\blive\s*orders?\b|(?i)\blive[_-]?orders?\b" },
        @{ id = "invoke_expression"; pattern = "(?i)\bInvoke-Expression\b" },
        @{ id = "remove_item"; pattern = "(?i)\bRemove-Item\b" },
        @{ id = "git_reset_hard"; pattern = "(?i)^git\s+reset\s+--hard\b" },
        @{ id = "git_clean"; pattern = "(?i)^git\s+clean\b" },
        @{ id = "git_push"; pattern = "(?i)^git\s+push\b" },
        @{ id = "git_merge"; pattern = "(?i)^git\s+merge\b" },
        @{ id = "git_rebase"; pattern = "(?i)^git\s+rebase\b" },
        @{ id = "git_commit"; pattern = "(?i)^git\s+commit\b" },
        @{ id = "delete_alias"; pattern = "(?i)\b(del|erase|rmdir|rm)\b" }
    )

    $foundMatches = [System.Collections.Generic.List[object]]::new()
    foreach ($entry in $patterns) {
        if ($Command -match $entry.pattern) {
            $foundMatches.Add([pscustomobject]@{
                id = $entry.id
                pattern = $entry.pattern
                tier = "TIER_2"
            }) | Out-Null
        }
    }

    return @($foundMatches)
}

function Get-AiOsReadOnlyMatches {
    param([string]$Command)

    $patterns = @(
        @{ id = "git_status"; pattern = "(?i)^git\s+status(\s|$)" },
        @{ id = "git_diff"; pattern = "(?i)^git\s+diff(\s|$)" },
        @{ id = "get_child_item"; pattern = "(?i)^Get-ChildItem(\s|$)" },
        @{ id = "get_content"; pattern = "(?i)^Get-Content(\s|$)" },
        @{ id = "test_path"; pattern = "(?i)^Test-Path(\s|$)" },
        @{ id = "select_string"; pattern = "(?i)^Select-String(\s|$)" }
    )

    $foundMatches = [System.Collections.Generic.List[object]]::new()
    foreach ($entry in $patterns) {
        if ($Command -match $entry.pattern) {
            $foundMatches.Add([pscustomobject]@{
                id = $entry.id
                pattern = $entry.pattern
                tier = "TIER_0"
            }) | Out-Null
        }
    }

    return @($foundMatches)
}

function Get-AiOsPolicyCommandPatternMatches {
    param(
        [string]$Command,
        [AllowNull()]$Policy,
        [string]$TierName
    )

    $foundMatches = [System.Collections.Generic.List[object]]::new()
    $tiers = Get-AiOsPropertyValue -InputObject $Policy -Name "tiers" -Default $null
    $tier = Get-AiOsPropertyValue -InputObject $tiers -Name $TierName -Default $null
    $commandPatterns = Get-AiOsPropertyValue -InputObject $tier -Name "command_patterns" -Default $null

    if ($null -eq $commandPatterns) {
        return @()
    }

    foreach ($group in $commandPatterns.PSObject.Properties) {
        foreach ($pattern in @($group.Value)) {
            if (Test-AiOsPatternMatch -Command $Command -Pattern ([string]$pattern)) {
                $foundMatches.Add([pscustomobject]@{
                    tier = $TierName
                    group = $group.Name
                    pattern = [string]$pattern
                }) | Out-Null
            }
        }
    }

    return @($foundMatches)
}

function Get-AiOsScopeGuardMatches {
    param(
        [string]$Command,
        [AllowNull()]$Policy
    )

    $foundMatches = [System.Collections.Generic.List[object]]::new()
    $scopeGuards = Get-AiOsPropertyValue -InputObject $Policy -Name "scope_guards" -Default $null
    foreach ($guard in @((Get-AiOsPropertyValue -InputObject $scopeGuards -Name "guards" -Default @()))) {
        foreach ($trigger in @((Get-AiOsPropertyValue -InputObject $guard -Name "triggers_on" -Default @()))) {
            if (Test-AiOsPatternMatch -Command $Command -Pattern ([string]$trigger)) {
                $foundMatches.Add([pscustomobject]@{
                    guard_id = [string](Get-AiOsPropertyValue -InputObject $guard -Name "guard_id" -Default "UNKNOWN")
                    trigger = [string]$trigger
                    action = [string](Get-AiOsPropertyValue -InputObject $guard -Name "action" -Default "REVIEW_REQUIRED")
                    reason = [string](Get-AiOsPropertyValue -InputObject $guard -Name "reason" -Default "Scope guard matched.")
                }) | Out-Null
            }
        }
    }

    return @($foundMatches)
}

function Get-AiOsProtectedPathMatches {
    param(
        [string]$Command,
        [AllowNull()]$Policy
    )

    return @(Find-AiOsPatternMatches -Command $Command -Patterns @((Get-AiOsPropertyValue -InputObject $Policy -Name "protected_paths" -Default @())))
}

function Get-AiOsHardExclusionMatches {
    param(
        [string]$Command,
        [AllowNull()]$Policy
    )

    $foundMatches = [System.Collections.Generic.List[string]]::new()
    $tiers = Get-AiOsPropertyValue -InputObject $Policy -Name "tiers" -Default $null
    $tier1 = Get-AiOsPropertyValue -InputObject $tiers -Name "TIER_1_LOW_RISK" -Default $null
    foreach ($pattern in @((Get-AiOsPropertyValue -InputObject $tier1 -Name "hard_exclusions" -Default @()))) {
        if (Test-AiOsPatternMatch -Command $Command -Pattern ([string]$pattern)) {
            $foundMatches.Add([string]$pattern) | Out-Null
        }
    }

    return @($foundMatches)
}

function Get-AiOsRollbackProtectionMatches {
    param(
        [string]$Command,
        [AllowNull()]$Policy
    )

    $foundMatches = [System.Collections.Generic.List[string]]::new()
    foreach ($protection in @((Get-AiOsPropertyValue -InputObject $Policy -Name "rollback_protections" -Default @()))) {
        $rule = [string](Get-AiOsPropertyValue -InputObject $protection -Name "rule" -Default "")
        foreach ($quoted in @([regex]::Matches($rule, "git\s+[a-zA-Z0-9 ._-]+|Remove-Item|file writes|file deletes|credential-path reads") | ForEach-Object { $_.Value.Trim() })) {
            if (-not [string]::IsNullOrWhiteSpace($quoted) -and (Test-AiOsPatternMatch -Command $Command -Pattern $quoted)) {
                $foundMatches.Add($quoted) | Out-Null
            }
        }
    }

    return @($foundMatches | Sort-Object -Unique)
}

try {
    $resolvedRepoRoot = Resolve-AiOsRepoRoot -RequestedRepoRoot $RepoRoot
    $resolvedPolicyPath = if ([string]::IsNullOrWhiteSpace($PolicyPath)) {
        Join-Path $resolvedRepoRoot "automation/orchestration/policy/AIOS_APPROVAL_TIER_POLICY.json"
    } elseif ([System.IO.Path]::IsPathRooted($PolicyPath)) {
        $PolicyPath
    } else {
        Join-Path $resolvedRepoRoot $PolicyPath
    }

    $commandPreview = if ([string]::IsNullOrWhiteSpace($CommandText)) {
        Get-AiOsPacketCommand -RequestedPacketPath $PacketPath
    } else {
        $CommandText
    }
    $commandPreview = ([string]$commandPreview).Trim()

    $policy = Get-AiOsPolicy -ResolvedPolicyPath $resolvedPolicyPath
    $policyLoaded = $null -ne $policy
    $policyId = [string](Get-AiOsPropertyValue -InputObject $policy -Name "policy_id" -Default "")
    $policyVersion = [string](Get-AiOsPropertyValue -InputObject $policy -Name "schema_version" -Default "")
    $policyFieldsConsumed = @(
        "schema_version",
        "policy_id",
        "tiers.TIER_0_AUTO.command_patterns",
        "tiers.TIER_1_LOW_RISK.command_patterns",
        "tiers.TIER_1_LOW_RISK.hard_exclusions",
        "tiers.TIER_2_HUMAN_REQUIRED.command_patterns",
        "scope_guards.guards.triggers_on",
        "scope_guards.guards.action",
        "scope_guards.guards.reason",
        "protected_paths",
        "forbidden_patterns",
        "rollback_protections",
        "audit_schema.schema_id"
    )

    $hardStopScript = Join-Path $resolvedRepoRoot "automation/orchestration/safety/Test-AiOsHardStop.ps1"
    $hardStop = & $hardStopScript -RepoRoot $resolvedRepoRoot
    $hardStopPresent = [bool](Get-AiOsPropertyValue -InputObject $hardStop -Name "hard_stop_present" -Default $false)
    $hardStopDecision = [string](Get-AiOsPropertyValue -InputObject $hardStop -Name "decision" -Default "UNKNOWN")

    $internalRiskMatches = @(Get-AiOsInternalRiskMatches -Command $commandPreview)
    $internalReadOnlyMatches = @(Get-AiOsReadOnlyMatches -Command $commandPreview)
    $policyTier2Matches = @(Get-AiOsPolicyCommandPatternMatches -Command $commandPreview -Policy $policy -TierName "TIER_2_HUMAN_REQUIRED")
    $policyTier0Matches = @(Get-AiOsPolicyCommandPatternMatches -Command $commandPreview -Policy $policy -TierName "TIER_0_AUTO")
    $policyTier1Matches = @(Get-AiOsPolicyCommandPatternMatches -Command $commandPreview -Policy $policy -TierName "TIER_1_LOW_RISK")
    $scopeGuardMatches = @(Get-AiOsScopeGuardMatches -Command $commandPreview -Policy $policy)
    $protectedPathMatches = @(Get-AiOsProtectedPathMatches -Command $commandPreview -Policy $policy)
    $forbiddenPatternMatches = @(Find-AiOsPatternMatches -Command $commandPreview -Patterns @((Get-AiOsPropertyValue -InputObject $policy -Name "forbidden_patterns" -Default @())))
    $hardExclusionMatches = @(Get-AiOsHardExclusionMatches -Command $commandPreview -Policy $policy)
    $rollbackMatches = @(Get-AiOsRollbackProtectionMatches -Command $commandPreview -Policy $policy)
    $matchedPolicyPatterns = @($policyTier2Matches + $policyTier0Matches + $policyTier1Matches)
    $matchedInternalPatterns = @($internalRiskMatches + $internalReadOnlyMatches)

    $decision = "REVIEW_REQUIRED"
    $tier = "TIER_1"
    $reason = "Command requires review before execution."
    $blockedReason = ""
    $requiresUserApproval = $true

    if ([string]::IsNullOrWhiteSpace($commandPreview)) {
        $decision = "BLOCKED"
        $tier = "UNKNOWN"
        $reason = "Empty command cannot be approved."
        $blockedReason = "CommandText and PacketPath did not provide a command."
    }
    elseif (@($internalRiskMatches).Count -gt 0) {
        $decision = "BLOCKED"
        $tier = "TIER_2"
        $reason = "Critical internal risk matched before policy allow rules."
        $blockedReason = "Critical internal risk: " + (($internalRiskMatches | ForEach-Object { $_.id }) -join ", ")
    }
    elseif (@($forbiddenPatternMatches).Count -gt 0 -or @($policyTier2Matches).Count -gt 0) {
        $decision = "BLOCKED"
        $tier = "TIER_2"
        $reason = "Policy Tier 2 or forbidden pattern matched."
        $blockedReason = "Policy blocked pattern matched."
    }
    elseif (@($scopeGuardMatches | Where-Object { $_.action -eq "TIER_2" }).Count -gt 0) {
        $decision = "BLOCKED"
        $tier = "TIER_2"
        $reason = "Policy scope guard requires block."
        $blockedReason = (($scopeGuardMatches | Where-Object { $_.action -eq "TIER_2" } | ForEach-Object { $_.reason }) -join "; ")
    }
    elseif (@($scopeGuardMatches).Count -gt 0) {
        $decision = "REVIEW_REQUIRED"
        $tier = "TIER_1"
        $reason = "Policy scope guard requires review."
        $blockedReason = (($scopeGuardMatches | ForEach-Object { $_.reason }) -join "; ")
    }
    elseif (@($protectedPathMatches).Count -gt 0) {
        $decision = "REVIEW_REQUIRED"
        $tier = "TIER_1"
        $reason = "Command touches a protected path."
        $blockedReason = "Protected path matched: " + ($protectedPathMatches -join ", ")
    }
    elseif (@($hardExclusionMatches).Count -gt 0 -or @($rollbackMatches).Count -gt 0) {
        $decision = "BLOCKED"
        $tier = "TIER_2"
        $reason = "Hard exclusion or rollback protection matched."
        $blockedReason = "Hard exclusion matched."
    }
    elseif (@($policyTier0Matches).Count -gt 0 -or @($internalReadOnlyMatches).Count -gt 0) {
        $decision = "AUTO_PROCEED"
        $tier = "TIER_0"
        $reason = "Command classified as safe read-only inspection with no conflicts."
        $blockedReason = ""
        $requiresUserApproval = $false
    }
    elseif (@($policyTier1Matches).Count -gt 0) {
        $decision = "REVIEW_REQUIRED"
        $tier = "TIER_1"
        $reason = "Policy Tier 1 command requires review."
    }

    if ($hardStopPresent) {
        if ($Mode -eq "APPLY" -or $decision -ne "AUTO_PROCEED") {
            $decision = "BLOCKED_HARD_STOP"
            $tier = "TIER_2"
            $reason = "Global hard stop is active."
            $blockedReason = "HARD_STOP.flag is present. Only clear read-only DRY_RUN inspection may proceed."
            $requiresUserApproval = $true
        }
        else {
            $reason = "Global hard stop is active, but command is clear read-only DRY_RUN inspection."
        }
    }

    ConvertTo-AiOsJson -Value (New-AiOsGateDecision `
        -Decision $decision `
        -Tier $tier `
        -Reason $reason `
        -BlockedReason $blockedReason `
        -RequiresUserApproval $requiresUserApproval `
        -CommandPreview $commandPreview `
        -ResolvedPolicyPath $resolvedPolicyPath `
        -PolicyLoaded $policyLoaded `
        -PolicyId $policyId `
        -PolicyVersion $policyVersion `
        -PolicyFieldsConsumed $policyFieldsConsumed `
        -HardStopPresent $hardStopPresent `
        -HardStopDecision $hardStopDecision `
        -MatchedPolicyPatterns $matchedPolicyPatterns `
        -MatchedInternalPatterns $matchedInternalPatterns `
        -MatchedScopeGuards $scopeGuardMatches `
        -MatchedProtectedPaths $protectedPathMatches `
        -MatchedForbiddenPatterns $forbiddenPatternMatches `
        -MatchedHardExclusions @($hardExclusionMatches + $rollbackMatches))
}
catch {
    $safePolicyPath = if ([string]::IsNullOrWhiteSpace($PolicyPath)) {
        "automation/orchestration/policy/AIOS_APPROVAL_TIER_POLICY.json"
    } else {
        $PolicyPath
    }

    ConvertTo-AiOsJson -Value (New-AiOsGateDecision `
        -Decision "BLOCKED_ERROR" `
        -Tier "ERROR" `
        -Reason "Gate runner failed closed." `
        -BlockedReason $_.Exception.Message `
        -RequiresUserApproval $true `
        -CommandPreview $CommandText `
        -ResolvedPolicyPath $safePolicyPath `
        -PolicyLoaded $false `
        -HardStopPresent $false `
        -HardStopDecision "UNKNOWN")
}
