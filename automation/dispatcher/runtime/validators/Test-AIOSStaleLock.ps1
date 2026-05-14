[CmdletBinding()]
param(
    [string]$LockTablePath = "Reports/dispatcher/runtime/lock_runtime_table.example.json"
)

$ErrorActionPreference = "Stop"

function Test-AIOSStaleLock {
    [CmdletBinding()]
    param([string]$LockTablePath = "Reports/dispatcher/runtime/lock_runtime_table.example.json")

    $findings = New-Object System.Collections.Generic.List[object]
    $status = "PASS"

    if (-not (Test-Path -LiteralPath $LockTablePath)) {
        return [pscustomobject]@{
            schema = "AIOS_VALIDATOR_RESULT.v1"
            validator = "stale_lock"
            stage = "recovery_review"
            status = "REVIEW_REQUIRED"
            findings = @([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Lock table is missing: $LockTablePath" })
            checked_paths = @($LockTablePath)
            blocked_actions = @("release_lock", "resume_apply", "commit", "push")
            next_safe_action = "Review lock state before release, override, or resume."
        }
    }

    try {
        $data = Get-Content -LiteralPath $LockTablePath -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            schema = "AIOS_VALIDATOR_RESULT.v1"
            validator = "stale_lock"
            stage = "recovery_review"
            status = "FAIL"
            findings = @([pscustomobject]@{ status = "FAIL"; message = "Lock table JSON could not parse."; detail = $_.Exception.Message })
            checked_paths = @($LockTablePath)
            blocked_actions = @("release_lock", "resume_apply", "commit", "push")
            next_safe_action = "Fix lock runtime JSON before recovery review."
        }
    }

    $locks = @($data.locks)
    if ($locks.Count -eq 0) {
        $findings.Add([pscustomobject]@{ status = "PASS"; message = "No locks found in lock table." }) | Out-Null
    }

    foreach ($lock in $locks) {
        if ($lock.status -eq "ACTIVE") {
            try {
                $expires = [datetime]::Parse($lock.expires_at).ToUniversalTime()
                if ([datetime]::UtcNow -gt $expires) {
                    $status = "REVIEW_REQUIRED"
                    $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Active lock is expired and needs review: $($lock.lock_id)" }) | Out-Null
                }
                else {
                    $findings.Add([pscustomobject]@{ status = "PASS"; message = "Active lock is not expired: $($lock.lock_id)" }) | Out-Null
                }
            }
            catch {
                $status = "FAIL"
                $findings.Add([pscustomobject]@{ status = "FAIL"; message = "Lock expiration timestamp is invalid: $($lock.lock_id)" }) | Out-Null
            }
        }
        elseif ($lock.status -eq "REVIEW_REQUIRED" -or $lock.status -eq "EXPIRED") {
            $status = "REVIEW_REQUIRED"
            $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Lock requires review before override: $($lock.lock_id)" }) | Out-Null
        }
        else {
            $findings.Add([pscustomobject]@{ status = "PASS"; message = "Lock is not active: $($lock.lock_id)" }) | Out-Null
        }
    }

    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "stale_lock"
        stage = "recovery_review"
        status = $status
        findings = $findings.ToArray()
        checked_paths = @($LockTablePath)
        blocked_actions = @("release_lock", "resume_apply", "commit", "push")
        next_safe_action = "Review stale locks before release, override, or APPLY resume."
    }
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSStaleLock -LockTablePath $LockTablePath | ConvertTo-Json -Depth 8
}
