[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$OutputRoot = "",
    [string]$ConfigPath = "",
    [string]$WorkerId = "NIGHT_SUPERVISOR",
    [ValidateSet("DRY_RUN")]
    [string]$Mode = "DRY_RUN",
    [switch]$QuietJson,
    [switch]$NoMarkdown,
    [switch]$NoTelemetry
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsUtcTimestamp {
    (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function New-AiOsReportId {
    "NSR-" + (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
}

function ConvertTo-AiOsJson {
    param([Parameter(Mandatory = $true)]$Value)
    $Value | ConvertTo-Json -Depth 18 -Compress:$false
}

function Resolve-AiOsRepoRoot {
    param([string]$RequestedRepoRoot)

    if (-not [string]::IsNullOrWhiteSpace($RequestedRepoRoot)) {
        return (Resolve-Path -LiteralPath $RequestedRepoRoot).Path
    }

    $scriptRoot = Split-Path -Parent $PSCommandPath
    return (Resolve-Path -LiteralPath (Join-Path $scriptRoot "..\..\..")).Path
}

function Resolve-AiOsPath {
    param(
        [string]$Root,
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $Root
    }

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return (Join-Path $Root $Path)
}

function Get-AiOsRelativePath {
    param(
        [string]$Root,
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    try {
        $rootPath = (Resolve-Path -LiteralPath $Root).Path.TrimEnd("\") + "\"
        $targetPath = $Path
        if (Test-Path -LiteralPath $Path) {
            $targetPath = (Resolve-Path -LiteralPath $Path).Path
        }
        $rootUri = [System.Uri]::new($rootPath)
        $targetUri = [System.Uri]::new($targetPath)
        return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($targetUri).ToString()).Replace("/", "\")
    }
    catch {
        return $Path
    }
}

function Get-AiOsPropertyValue {
    param(
        [AllowNull()]$InputObject,
        [string[]]$Names,
        $Default = $null
    )

    if ($null -eq $InputObject) {
        return $Default
    }

    foreach ($name in $Names) {
        if ($InputObject.PSObject.Properties.Name -contains $name) {
            $value = $InputObject.$name
            if ($null -ne $value -and [string]$value -ne "") {
                return $value
            }
        }
    }

    return $Default
}

function Protect-AiOsText {
    param([AllowNull()][object]$Value)

    if ($null -eq $Value) {
        return ""
    }

    $text = [string]$Value
    $sensitivePattern = "(?i)(API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|PRIVATE_KEY)\s*[:=]\s*[^,\s;]+"
    return ($text -replace $sensitivePattern, '$1=<REDACTED>')
}

function Get-AiOsJsonFileSafe {
    param(
        [string]$Path,
        [ref]$Warnings
    )

    try {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            return $null
        }

        return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
    }
    catch {
        $Warnings.Value += "JSON parse warning: $Path :: $($_.Exception.Message)"
        return $null
    }
}

function Get-AiOsTextFileSafe {
    param(
        [string]$Path,
        [ref]$Warnings
    )

    try {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            return ""
        }

        return (Get-Content -LiteralPath $Path -Raw)
    }
    catch {
        $Warnings.Value += "Text read warning: $Path :: $($_.Exception.Message)"
        return ""
    }
}

function Get-AiOsConfig {
    param(
        [string]$RepoRootPath,
        [string]$RequestedConfigPath,
        [ref]$Warnings
    )

    $defaultConfig = [ordered]@{
        schema = "AIOS_NIGHT_SUPERVISOR_CONFIG"
        schema_version = "1.0"
        config_id = "AIOS_NIGHT_SUPERVISOR_V1_CONFIG_DEFAULT"
        mode = "DRY_RUN"
        output_root = "telemetry/night_supervisor"
        max_report_files_to_scan = 200
        stale_lock_minutes = 120
        stale_packet_minutes = 240
        stale_worker_minutes = 120
        read_only = $true
        write_reports = $true
        write_markdown_brief = $true
        allow_mutation = $false
        forbidden_actions = @("git add", "git commit", "git push", "git merge", "git rebase", "git reset --hard", "Remove-Item", "Invoke-Expression", "Start-Process", "broker", "OANDA", "live order", "api key", "secret")
        scan_paths = [ordered]@{
            work_packets = @("automation/orchestration/work_packets", "automation/orchestration/packets", "automation/orchestration/queues")
            locks = @("automation/orchestration/locks", "automation/orchestration/file_locks", "automation/orchestration/work_packets/locks", "telemetry/locks")
            approvals = @("automation/orchestration/approval_inbox")
            gate_reports = @("telemetry/gates", "telemetry/night_supervisor", "automation/orchestration/gates")
            workers = @("automation/orchestration/workers", "telemetry/workers")
        }
    }

    $resolvedConfigPath = if ([string]::IsNullOrWhiteSpace($RequestedConfigPath)) {
        Join-Path $RepoRootPath "automation/orchestration/night_supervisor/NIGHT_SUPERVISOR_CONFIG.json"
    } else {
        Resolve-AiOsPath -Root $RepoRootPath -Path $RequestedConfigPath
    }

    if (-not (Test-Path -LiteralPath $resolvedConfigPath -PathType Leaf)) {
        return [pscustomobject]$defaultConfig
    }

    $loaded = Get-AiOsJsonFileSafe -Path $resolvedConfigPath -Warnings $Warnings
    if ($null -eq $loaded) {
        $Warnings.Value += "Config unavailable; default config used."
        return [pscustomobject]$defaultConfig
    }

    return $loaded
}

function Get-AiOsGitSummary {
    param([string]$RepoRootPath)

    $summary = [ordered]@{
        branch = "UNKNOWN"
        status_lines = @()
        changed_files = @()
        untracked_files = @()
        git_available = $false
        warnings = @()
    }

    try {
        $branchOutput = @(& git -C $RepoRootPath branch --show-current 2>&1)
        if ($LASTEXITCODE -eq 0 -and $branchOutput.Count -gt 0) {
            $summary.git_available = $true
            $summary.branch = [string]$branchOutput[0]
        }
        else {
            $summary.warnings += "git branch read failed: $($branchOutput -join ' ')"
        }

        $statusOutput = @(& git -C $RepoRootPath status --short --branch 2>&1)
        if ($LASTEXITCODE -eq 0) {
            $summary.git_available = $true
            $summary.status_lines = @($statusOutput | ForEach-Object { [string]$_ })
            $summary.changed_files = @($statusOutput | Where-Object { $_ -match "^\s*(M|A|D|R|C|U)\s+" } | ForEach-Object { ([string]$_).Substring(3).Trim() })
            $summary.untracked_files = @($statusOutput | Where-Object { $_ -match "^\?\?\s+" } | ForEach-Object { ([string]$_ -replace "^\?\?\s+", "").Trim() })
        }
        else {
            $summary.warnings += "git status read failed: $($statusOutput -join ' ')"
        }
    }
    catch {
        $summary.warnings += "git summary failed: $($_.Exception.Message)"
    }

    [pscustomobject]$summary
}

function Get-AiOsHardStopSummary {
    param(
        [string]$RepoRootPath,
        [ref]$Warnings
    )

    $helperPath = Join-Path $RepoRootPath "automation/orchestration/safety/Test-AiOsHardStop.ps1"
    if (Test-Path -LiteralPath $helperPath -PathType Leaf) {
        try {
            $result = & $helperPath -RepoRoot $RepoRootPath
            return [pscustomobject]@{
                helper_present = $true
                helper_status = "OK"
                hard_stop_present = [bool](Get-AiOsPropertyValue -InputObject $result -Names @("hard_stop_present") -Default $false)
                decision = [string](Get-AiOsPropertyValue -InputObject $result -Names @("decision") -Default "UNKNOWN")
                flag_path = [string](Get-AiOsPropertyValue -InputObject $result -Names @("flag_path") -Default (Join-Path $RepoRootPath "HARD_STOP.flag"))
                checked_at = [string](Get-AiOsPropertyValue -InputObject $result -Names @("checked_at") -Default (Get-AiOsUtcTimestamp))
            }
        }
        catch {
            $Warnings.Value += "Hard stop helper failed: $($_.Exception.Message)"
        }
    }

    $flagPath = Join-Path $RepoRootPath "HARD_STOP.flag"
    $present = Test-Path -LiteralPath $flagPath -PathType Leaf
    [pscustomobject]@{
        helper_present = $false
        helper_status = "MISSING_OR_FAILED"
        hard_stop_present = [bool]$present
        decision = if ($present) { "BLOCKED_HARD_STOP" } else { "CLEAR" }
        flag_path = $flagPath
        checked_at = Get-AiOsUtcTimestamp
    }
}

function Get-AiOsStatusNormalized {
    param(
        [AllowNull()][object]$Status,
        [string]$Kind = "packet"
    )

    $value = ([string]$Status).Trim()
    if ([string]::IsNullOrWhiteSpace($value)) {
        return "UNKNOWN"
    }

    switch -Regex ($value.ToUpperInvariant()) {
        "^(WAITING|QUEUED|PENDING)$" { return "WAITING" }
        "^(ACTIVE|IN_PROGRESS|RUNNING|STARTED)$" { return "IN_PROGRESS" }
        "^(BLOCKED|BLOCK)$" { return "BLOCKED" }
        "^(REVIEW_REQUIRED|NEEDS_REVIEW|HUMAN_REVIEW)$" { return "REVIEW_REQUIRED" }
        "^(COMPLETED|COMPLETE|DONE|CLOSED)$" { return "COMPLETE" }
        "^(FAILED|ERROR|FAIL)$" { return "FAILED" }
        "^(APPROVED|ACCEPTED)$" { return "APPROVED" }
        "^(REJECTED|DENIED)$" { return "REJECTED" }
        "^(EXPIRED)$" { return "EXPIRED" }
        default { return "UNKNOWN" }
    }
}

function Get-AiOsLimitedFiles {
    param(
        [string]$RepoRootPath,
        [object[]]$RelativePaths,
        [int]$Limit,
        [string[]]$Extensions = @("*.json", "*.md", "*.txt")
    )

    $scanPaths = @()
    $missingPaths = @()
    $files = [System.Collections.Generic.List[object]]::new()
    $filesSeen = 0
    $truncated = $false

    foreach ($relativePath in @($RelativePaths)) {
        $resolved = Resolve-AiOsPath -Root $RepoRootPath -Path ([string]$relativePath)
        $scanPaths += [string]$relativePath
        if (-not (Test-Path -LiteralPath $resolved -PathType Container)) {
            $missingPaths += [string]$relativePath
            continue
        }

        foreach ($extension in $Extensions) {
            $found = @(Get-ChildItem -LiteralPath $resolved -Recurse -File -Filter $extension -ErrorAction SilentlyContinue)
            foreach ($file in $found) {
                $filesSeen++
                if ($files.Count -lt $Limit) {
                    $files.Add($file) | Out-Null
                }
                else {
                    $truncated = $true
                }
            }
        }
    }

    [pscustomobject]@{
        scan_paths = $scanPaths
        missing_paths = $missingPaths
        files = @($files)
        files_seen = $filesSeen
        files_scanned = $files.Count
        truncated = $truncated
        scan_limit = $Limit
    }
}

function Test-AiOsStaleCandidate {
    param(
        [datetime]$Timestamp,
        [int]$Minutes
    )

    if ($null -eq $Timestamp) {
        return $false
    }

    return ($Timestamp.ToUniversalTime() -lt (Get-Date).ToUniversalTime().AddMinutes(-1 * $Minutes))
}

function Get-AiOsDateValue {
    param([AllowNull()][object]$Value)

    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) {
        return $null
    }

    try {
        return ([datetime]$Value)
    }
    catch {
        return $null
    }
}

function Get-AiOsPacketSummary {
    param(
        [string]$RepoRootPath,
        [object]$File,
        [int]$StaleMinutes,
        [ref]$Warnings
    )

    $relativePath = Get-AiOsRelativePath -Root $RepoRootPath -Path $File.FullName
    $packet = $null
    $text = ""
    if ($File.Extension -eq ".json") {
        $packet = Get-AiOsJsonFileSafe -Path $File.FullName -Warnings $Warnings
    }
    else {
        $text = Get-AiOsTextFileSafe -Path $File.FullName -Warnings $Warnings
    }

    $statusValue = Get-AiOsPropertyValue -InputObject $packet -Names @("current_status", "status", "packet_state", "state") -Default ""
    if ([string]::IsNullOrWhiteSpace([string]$statusValue) -and -not [string]::IsNullOrWhiteSpace($text)) {
        if ($text -match "(?i)REVIEW_REQUIRED") { $statusValue = "REVIEW_REQUIRED" }
        elseif ($text -match "(?i)IN_PROGRESS|RUNNING") { $statusValue = "IN_PROGRESS" }
        elseif ($text -match "(?i)BLOCKED") { $statusValue = "BLOCKED" }
        elseif ($text -match "(?i)WAITING|QUEUED|PENDING") { $statusValue = "WAITING" }
        elseif ($text -match "(?i)COMPLETE|DONE") { $statusValue = "COMPLETE" }
        elseif ($text -match "(?i)FAILED|ERROR") { $statusValue = "FAILED" }
    }

    $status = Get-AiOsStatusNormalized -Status $statusValue
    $updatedAt = Get-AiOsDateValue -Value (Get-AiOsPropertyValue -InputObject $packet -Names @("updated_at", "completed_at", "created_at") -Default $null)
    $staleBase = if ($null -ne $updatedAt) { $updatedAt } else { $File.LastWriteTimeUtc }
    $isActiveLike = @("WAITING", "IN_PROGRESS", "REVIEW_REQUIRED", "UNKNOWN") -contains $status
    $staleCandidate = $isActiveLike -and (Test-AiOsStaleCandidate -Timestamp $staleBase -Minutes $StaleMinutes)
    $approvalRequired = [bool](Get-AiOsPropertyValue -InputObject $packet -Names @("user_approval_required", "approval_required") -Default $false)
    $approvalStatus = [string](Get-AiOsPropertyValue -InputObject $packet -Names @("approval_status") -Default "")
    if ($text -match "(?i)approval required|user approval") {
        $approvalRequired = $true
    }
    if ($approvalStatus -match "(?i)pending|review|required") {
        $approvalRequired = $true
    }

    [pscustomobject]@{
        path = $relativePath
        packet_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $packet -Names @("packet_id", "id") -Default $File.BaseName)
        task_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $packet -Names @("task_id") -Default "")
        status = $status
        assigned_worker = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $packet -Names @("assigned_worker", "worker_identity", "worker") -Default "")
        next_action = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $packet -Names @("next_action", "next_safe_action") -Default "")
        blocked_reason = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $packet -Names @("blocked_reason", "reason") -Default "")
        approval_required = [bool]$approvalRequired
        validation_required = [bool](Get-AiOsPropertyValue -InputObject $packet -Names @("validation_required") -Default $false)
        validation_status = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $packet -Names @("validation_status") -Default "")
        relay_ready = [bool](Get-AiOsPropertyValue -InputObject $packet -Names @("relay_ready") -Default $false)
        last_write_time = $File.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
        stale_candidate = [bool]$staleCandidate
    }
}

function Add-AiOsSummaryItem {
    param(
        [object]$Summary,
        [string]$Property,
        [object]$Item
    )

    $Summary.$Property = @($Summary.$Property) + @($Item)
}

function Get-AiOsQueueSummary {
    param(
        [string]$RepoRootPath,
        [object]$Config,
        [ref]$Warnings
    )

    $limit = [int](Get-AiOsPropertyValue -InputObject $Config -Names @("max_report_files_to_scan") -Default 200)
    $paths = @(Get-AiOsPropertyValue -InputObject $Config.scan_paths -Names @("work_packets") -Default @())
    $fileSet = Get-AiOsLimitedFiles -RepoRootPath $RepoRootPath -RelativePaths $paths -Limit $limit -Extensions @("*.json", "*.md")
    $summary = [pscustomobject]@{
        scan_paths = @($fileSet.scan_paths)
        missing_paths = @($fileSet.missing_paths)
        total_files_scanned = $fileSet.files_scanned
        packet_files_found = 0
        truncated = [bool]$fileSet.truncated
        scan_limit = $fileSet.scan_limit
        files_seen = $fileSet.files_seen
        counts_by_status = [ordered]@{ WAITING = 0; IN_PROGRESS = 0; BLOCKED = 0; REVIEW_REQUIRED = 0; COMPLETE = 0; FAILED = 0; UNKNOWN = 0 }
        waiting = @()
        in_progress = @()
        blocked = @()
        review_required = @()
        complete = @()
        failed = @()
        unknown = @()
        stale_candidates = @()
        missing_owner = @()
        missing_next_action = @()
        approval_required = @()
        relay_ready = @()
        warnings = @()
    }

    foreach ($file in @($fileSet.files)) {
        $item = Get-AiOsPacketSummary -RepoRootPath $RepoRootPath -File $file -StaleMinutes ([int]$Config.stale_packet_minutes) -Warnings $Warnings
        $summary.packet_files_found++
        $summary.counts_by_status[$item.status] = [int]$summary.counts_by_status[$item.status] + 1
        switch ($item.status) {
            "WAITING" { Add-AiOsSummaryItem -Summary $summary -Property "waiting" -Item $item }
            "IN_PROGRESS" { Add-AiOsSummaryItem -Summary $summary -Property "in_progress" -Item $item }
            "BLOCKED" { Add-AiOsSummaryItem -Summary $summary -Property "blocked" -Item $item }
            "REVIEW_REQUIRED" { Add-AiOsSummaryItem -Summary $summary -Property "review_required" -Item $item }
            "COMPLETE" { Add-AiOsSummaryItem -Summary $summary -Property "complete" -Item $item }
            "FAILED" { Add-AiOsSummaryItem -Summary $summary -Property "failed" -Item $item }
            default { Add-AiOsSummaryItem -Summary $summary -Property "unknown" -Item $item }
        }
        if ($item.stale_candidate) { Add-AiOsSummaryItem -Summary $summary -Property "stale_candidates" -Item $item }
        if ([string]::IsNullOrWhiteSpace($item.assigned_worker)) { Add-AiOsSummaryItem -Summary $summary -Property "missing_owner" -Item $item }
        if ([string]::IsNullOrWhiteSpace($item.next_action)) { Add-AiOsSummaryItem -Summary $summary -Property "missing_next_action" -Item $item }
        if ($item.approval_required) { Add-AiOsSummaryItem -Summary $summary -Property "approval_required" -Item $item }
        if ($item.relay_ready) { Add-AiOsSummaryItem -Summary $summary -Property "relay_ready" -Item $item }
    }

    if ($fileSet.truncated) {
        $summary.warnings += "Queue scan truncated at $($fileSet.scan_limit) files; files seen: $($fileSet.files_seen)."
    }

    $summary
}

function Get-AiOsLockSummary {
    param(
        [string]$RepoRootPath,
        [object]$Config,
        [ref]$Warnings
    )

    $limit = [int](Get-AiOsPropertyValue -InputObject $Config -Names @("max_report_files_to_scan") -Default 200)
    $paths = @(Get-AiOsPropertyValue -InputObject $Config.scan_paths -Names @("locks") -Default @())
    $fileSet = Get-AiOsLimitedFiles -RepoRootPath $RepoRootPath -RelativePaths $paths -Limit $limit -Extensions @("*.json", "*.md", "*.txt")
    $summary = [pscustomobject]@{
        scan_paths = @($fileSet.scan_paths)
        missing_paths = @($fileSet.missing_paths)
        lock_files_found = 0
        truncated = [bool]$fileSet.truncated
        scan_limit = $fileSet.scan_limit
        files_seen = $fileSet.files_seen
        active_locks = @()
        stale_candidates = @()
        expired_candidates = @()
        missing_owner = @()
        missing_path = @()
        missing_timestamp = @()
        target_missing = @()
        warnings = @()
    }

    foreach ($file in @($fileSet.files)) {
        if ($file.Name -notmatch "(?i)lock|registry|ownership|owner") {
            continue
        }

        $lock = if ($file.Extension -eq ".json") { Get-AiOsJsonFileSafe -Path $file.FullName -Warnings $Warnings } else { $null }
        $lockedPath = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $lock -Names @("file_path", "path", "locked_path", "target_path") -Default "")
        $owner = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $lock -Names @("owner", "worker_id", "worker_identity") -Default "")
        $createdAt = Get-AiOsPropertyValue -InputObject $lock -Names @("created_at", "acquired_at") -Default ""
        $updatedAt = Get-AiOsPropertyValue -InputObject $lock -Names @("updated_at", "acquired_at", "created_at") -Default ""
        $expiresAt = Get-AiOsPropertyValue -InputObject $lock -Names @("expires_at") -Default ""
        $timestamp = Get-AiOsDateValue -Value $updatedAt
        $staleBase = if ($null -ne $timestamp) { $timestamp } else { $file.LastWriteTimeUtc }
        $staleCandidate = Test-AiOsStaleCandidate -Timestamp $staleBase -Minutes ([int]$Config.stale_lock_minutes)
        $expiresDate = Get-AiOsDateValue -Value $expiresAt
        $expiredCandidate = $false
        if ($null -ne $expiresDate) {
            $expiredCandidate = ($expiresDate.ToUniversalTime() -lt (Get-Date).ToUniversalTime())
        }
        $targetExists = $null
        if (-not [string]::IsNullOrWhiteSpace($lockedPath)) {
            $targetExists = Test-Path -LiteralPath (Resolve-AiOsPath -Root $RepoRootPath -Path $lockedPath)
        }

        $item = [pscustomobject]@{
            path = Get-AiOsRelativePath -Root $RepoRootPath -Path $file.FullName
            lock_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $lock -Names @("lock_id", "id") -Default $file.BaseName)
            locked_path = $lockedPath
            owner = $owner
            worker_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $lock -Names @("worker_id", "worker_identity") -Default $owner)
            packet_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $lock -Names @("packet_id") -Default "")
            task_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $lock -Names @("task_id") -Default "")
            status = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $lock -Names @("status") -Default "UNKNOWN")
            created_at = [string]$createdAt
            updated_at = [string]$updatedAt
            expires_at = [string]$expiresAt
            last_write_time = $file.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
            stale_candidate = [bool]$staleCandidate
            expired_candidate = [bool]$expiredCandidate
            target_exists = $targetExists
        }

        $summary.lock_files_found++
        Add-AiOsSummaryItem -Summary $summary -Property "active_locks" -Item $item
        if ($staleCandidate) { Add-AiOsSummaryItem -Summary $summary -Property "stale_candidates" -Item $item }
        if ($expiredCandidate) { Add-AiOsSummaryItem -Summary $summary -Property "expired_candidates" -Item $item }
        if ([string]::IsNullOrWhiteSpace($owner)) { Add-AiOsSummaryItem -Summary $summary -Property "missing_owner" -Item $item }
        if ([string]::IsNullOrWhiteSpace($lockedPath)) { Add-AiOsSummaryItem -Summary $summary -Property "missing_path" -Item $item }
        if ([string]::IsNullOrWhiteSpace([string]$updatedAt) -and [string]::IsNullOrWhiteSpace([string]$createdAt)) { Add-AiOsSummaryItem -Summary $summary -Property "missing_timestamp" -Item $item }
        if ($false -eq $targetExists) { Add-AiOsSummaryItem -Summary $summary -Property "target_missing" -Item $item }
    }

    if ($fileSet.truncated) {
        $summary.warnings += "Lock scan truncated at $($fileSet.scan_limit) files; files seen: $($fileSet.files_seen)."
    }

    $summary
}

function Get-AiOsApprovalSummary {
    param(
        [string]$RepoRootPath,
        [object]$Config,
        [ref]$Warnings
    )

    $limit = [int](Get-AiOsPropertyValue -InputObject $Config -Names @("max_report_files_to_scan") -Default 200)
    $paths = @(Get-AiOsPropertyValue -InputObject $Config.scan_paths -Names @("approvals") -Default @())
    $fileSet = Get-AiOsLimitedFiles -RepoRootPath $RepoRootPath -RelativePaths $paths -Limit $limit -Extensions @("*.json", "*.md")
    $summary = [pscustomobject]@{
        scan_paths = @($fileSet.scan_paths)
        missing_paths = @($fileSet.missing_paths)
        approval_files_found = 0
        truncated = [bool]$fileSet.truncated
        scan_limit = $fileSet.scan_limit
        files_seen = $fileSet.files_seen
        counts_by_status = [ordered]@{ PENDING = 0; APPROVED = 0; REJECTED = 0; EXPIRED = 0; UNKNOWN = 0 }
        pending = @()
        approved = @()
        rejected = @()
        expired = @()
        unknown = @()
        stale_candidates = @()
        missing_owner = @()
        missing_reason = @()
        missing_target_action = @()
        requires_user_review = @()
        warnings = @()
    }

    foreach ($file in @($fileSet.files)) {
        $approval = if ($file.Extension -eq ".json") { Get-AiOsJsonFileSafe -Path $file.FullName -Warnings $Warnings } else { $null }
        $text = if ($file.Extension -ne ".json") { Get-AiOsTextFileSafe -Path $file.FullName -Warnings $Warnings } else { "" }
        $statusValue = Get-AiOsPropertyValue -InputObject $approval -Names @("status", "approval_status") -Default ""
        if ([string]::IsNullOrWhiteSpace([string]$statusValue) -and $text -match "(?i)REVIEW_REQUIRED|needs_review|pending") {
            $statusValue = "PENDING"
        }
        $status = Get-AiOsStatusNormalized -Status $statusValue -Kind "approval"
        if ($status -eq "WAITING" -or $status -eq "REVIEW_REQUIRED") { $status = "PENDING" }
        if ($status -eq "FAILED" -or $status -eq "BLOCKED") { $status = "REJECTED" }
        if (@("PENDING", "APPROVED", "REJECTED", "EXPIRED") -notcontains $status) { $status = "UNKNOWN" }

        $expiresAt = Get-AiOsPropertyValue -InputObject $approval -Names @("expires_at") -Default ""
        $expiresDate = Get-AiOsDateValue -Value $expiresAt
        if ($null -ne $expiresDate -and $expiresDate.ToUniversalTime() -lt (Get-Date).ToUniversalTime()) {
            $status = "EXPIRED"
        }

        $updatedAt = Get-AiOsDateValue -Value (Get-AiOsPropertyValue -InputObject $approval -Names @("updated_at", "created_at") -Default $null)
        $staleBase = if ($null -ne $updatedAt) { $updatedAt } else { $file.LastWriteTimeUtc }
        $staleCandidate = (@("PENDING", "UNKNOWN") -contains $status) -and (Test-AiOsStaleCandidate -Timestamp $staleBase -Minutes ([int]$Config.stale_packet_minutes))
        $requiresUserReview = [bool](Get-AiOsPropertyValue -InputObject $approval -Names @("user_approval_required") -Default $false)
        if ($status -eq "PENDING" -or $text -match "(?i)user review|human owner|approval required") {
            $requiresUserReview = $true
        }

        $item = [pscustomobject]@{
            path = Get-AiOsRelativePath -Root $RepoRootPath -Path $file.FullName
            approval_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $approval -Names @("approval_id", "id") -Default $file.BaseName)
            packet_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $approval -Names @("packet_id") -Default "")
            task_id = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $approval -Names @("task_id") -Default "")
            status = $status
            requested_by = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $approval -Names @("requested_by", "requester") -Default "")
            assigned_to = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $approval -Names @("assigned_to", "approver") -Default "")
            requested_action = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $approval -Names @("requested_action", "command", "target_action") -Default "")
            reason = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $approval -Names @("reason", "blocked_reason") -Default "")
            tier = Protect-AiOsText (Get-AiOsPropertyValue -InputObject $approval -Names @("tier") -Default "")
            expires_at = [string]$expiresAt
            last_write_time = $file.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
            stale_candidate = [bool]$staleCandidate
            requires_user_review = [bool]$requiresUserReview
        }

        $summary.approval_files_found++
        $summary.counts_by_status[$status] = [int]$summary.counts_by_status[$status] + 1
        switch ($status) {
            "PENDING" { Add-AiOsSummaryItem -Summary $summary -Property "pending" -Item $item }
            "APPROVED" { Add-AiOsSummaryItem -Summary $summary -Property "approved" -Item $item }
            "REJECTED" { Add-AiOsSummaryItem -Summary $summary -Property "rejected" -Item $item }
            "EXPIRED" { Add-AiOsSummaryItem -Summary $summary -Property "expired" -Item $item }
            default { Add-AiOsSummaryItem -Summary $summary -Property "unknown" -Item $item }
        }
        if ($staleCandidate) { Add-AiOsSummaryItem -Summary $summary -Property "stale_candidates" -Item $item }
        if ([string]::IsNullOrWhiteSpace($item.requested_by) -and [string]::IsNullOrWhiteSpace($item.assigned_to)) { Add-AiOsSummaryItem -Summary $summary -Property "missing_owner" -Item $item }
        if ([string]::IsNullOrWhiteSpace($item.reason)) { Add-AiOsSummaryItem -Summary $summary -Property "missing_reason" -Item $item }
        if ([string]::IsNullOrWhiteSpace($item.requested_action)) { Add-AiOsSummaryItem -Summary $summary -Property "missing_target_action" -Item $item }
        if ($requiresUserReview) { Add-AiOsSummaryItem -Summary $summary -Property "requires_user_review" -Item $item }
    }

    if ($fileSet.truncated) {
        $summary.warnings += "Approval scan truncated at $($fileSet.scan_limit) files; files seen: $($fileSet.files_seen)."
    }

    $summary
}

function Get-AiOsGateSummary {
    param(
        [string]$RepoRootPath,
        [object]$Config,
        [object]$HardStop
    )

    $gateRunner = Join-Path $RepoRootPath "automation/orchestration/gates/gate_runner.ps1"
    $hardStopHelper = Join-Path $RepoRootPath "automation/orchestration/safety/Test-AiOsHardStop.ps1"
    $policyPath = Join-Path $RepoRootPath "automation/orchestration/policy/AIOS_APPROVAL_TIER_POLICY.json"
    $policy = $null
    $policyWarnings = @()
    if (Test-Path -LiteralPath $policyPath -PathType Leaf) {
        $policy = Get-AiOsJsonFileSafe -Path $policyPath -Warnings ([ref]$policyWarnings)
    }
    $paths = @(Get-AiOsPropertyValue -InputObject $Config.scan_paths -Names @("gate_reports") -Default @())
    $fileSet = Get-AiOsLimitedFiles -RepoRootPath $RepoRootPath -RelativePaths $paths -Limit ([int]$Config.max_report_files_to_scan) -Extensions @("*.json")
    $decisions = @{}
    $recentReports = @()

    foreach ($file in @($fileSet.files)) {
        $jsonWarnings = @()
        $gate = Get-AiOsJsonFileSafe -Path $file.FullName -Warnings ([ref]$jsonWarnings)
        $decision = [string](Get-AiOsPropertyValue -InputObject $gate -Names @("decision") -Default "")
        if (-not [string]::IsNullOrWhiteSpace($decision) -and $decision -match "AUTO_PROCEED|REVIEW_REQUIRED|BLOCKED|BLOCKED_HARD_STOP|BLOCKED_ERROR") {
            if (-not $decisions.ContainsKey($decision)) {
                $decisions[$decision] = 0
            }
            $decisions[$decision] = [int]$decisions[$decision] + 1
            $recentReports += [pscustomobject]@{
                path = Get-AiOsRelativePath -Root $RepoRootPath -Path $file.FullName
                decision = $decision
                checked_at = [string](Get-AiOsPropertyValue -InputObject $gate -Names @("checked_at", "generated_at") -Default "")
                last_write_time = $file.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
            }
        }
    }

    [pscustomobject]@{
        gate_runner_present = [bool](Test-Path -LiteralPath $gateRunner -PathType Leaf)
        hard_stop_helper_present = [bool](Test-Path -LiteralPath $hardStopHelper -PathType Leaf)
        policy_present = [bool](Test-Path -LiteralPath $policyPath -PathType Leaf)
        policy_id = [string](Get-AiOsPropertyValue -InputObject $policy -Names @("policy_id") -Default "")
        policy_version = [string](Get-AiOsPropertyValue -InputObject $policy -Names @("schema_version", "policy_version") -Default "")
        hard_stop_present = [bool]$HardStop.hard_stop_present
        decision_telemetry_present = [bool]($recentReports.Count -gt 0)
        decisions_by_type = $decisions
        recent_gate_reports = @($recentReports | Sort-Object last_write_time -Descending | Select-Object -First 10)
        warnings = @($policyWarnings + $(if ($recentReports.Count -eq 0) { "Gate files exist, but gate decision telemetry was not found in configured scan paths." } else { @() }))
    }
}

function Get-AiOsWorkerSummary {
    param(
        [string]$RepoRootPath,
        [object]$Config,
        [ref]$Warnings
    )

    $paths = @(Get-AiOsPropertyValue -InputObject $Config.scan_paths -Names @("workers") -Default @())
    $fileSet = Get-AiOsLimitedFiles -RepoRootPath $RepoRootPath -RelativePaths $paths -Limit ([int]$Config.max_report_files_to_scan) -Extensions @("*.json")
    [pscustomobject]@{
        scan_paths = @($fileSet.scan_paths)
        missing_paths = @($fileSet.missing_paths)
        worker_files_found = @($fileSet.files).Count
        stale_worker_minutes = [int]$Config.stale_worker_minutes
        warnings = @()
    }
}

function Get-AiOsBlockerSummary {
    param(
        [object]$HardStop,
        [object]$QueueSummary,
        [object]$LockSummary,
        [object]$ApprovalSummary,
        [object]$GateSummary
    )

    $critical = @()
    $operator = @()
    $worker = @()

    if ($HardStop.hard_stop_present) {
        $critical += [pscustomobject]@{ type = "HARD_STOP"; summary = "HARD_STOP.flag is present."; source = "repo_root" }
    }
    foreach ($item in @($ApprovalSummary.pending | Where-Object { $_.tier -match "2|TIER_2" })) {
        $operator += [pscustomobject]@{ type = "PENDING_TIER_2_APPROVAL"; summary = $item.path; source = $item.approval_id }
    }
    foreach ($item in @($ApprovalSummary.requires_user_review)) {
        $operator += [pscustomobject]@{ type = "PENDING_APPROVAL"; summary = $item.path; source = $item.approval_id }
    }
    foreach ($item in @($QueueSummary.blocked)) {
        $operator += [pscustomobject]@{ type = "BLOCKED_PACKET"; summary = $item.path; source = $item.packet_id }
    }
    foreach ($item in @($LockSummary.stale_candidates)) {
        $worker += [pscustomobject]@{ type = "STALE_LOCK"; summary = $item.path; source = $item.lock_id }
    }
    foreach ($item in @($QueueSummary.unknown + $ApprovalSummary.unknown)) {
        $worker += [pscustomobject]@{ type = "UNKNOWN_METADATA"; summary = $item.path; source = "metadata" }
    }

    $gateBlocked = 0
    foreach ($key in @($GateSummary.decisions_by_type.Keys)) {
        if ($key -match "BLOCKED") {
            $gateBlocked += [int]$GateSummary.decisions_by_type[$key]
        }
    }
    if ($gateBlocked -gt 0) {
        $operator += [pscustomobject]@{ type = "GATE_BLOCKED_EVENTS"; summary = "$gateBlocked gate blocked events found."; source = "gate_summary" }
    }

    [pscustomobject]@{
        total_blockers = [int]($critical.Count + $operator.Count + $worker.Count)
        blocked_packets = @($QueueSummary.blocked).Count
        pending_approvals = @($ApprovalSummary.pending).Count
        stale_locks = @($LockSummary.stale_candidates).Count
        hard_stop_present = [bool]$HardStop.hard_stop_present
        gate_blocked_events = [int]$gateBlocked
        critical_items = @($critical)
        operator_required_items = @($operator)
        worker_followup_items = @($worker)
    }
}

function Get-AiOsNextSafeAction {
    param(
        [object]$HardStop,
        [object]$QueueSummary,
        [object]$LockSummary,
        [object]$ApprovalSummary,
        [object]$BlockerSummary
    )

    $priority = "LOW"
    $summary = "No critical blockers found. Review packet queue for next prioritized DRY_RUN task."
    $reason = "Night Supervisor found no hard stop, pending approval, blocked packet, stale lock, or stale packet requiring priority attention."
    $sources = @()

    if ($HardStop.hard_stop_present) {
        $priority = "CRITICAL"
        $summary = "Review HARD_STOP.flag condition. Do not run APPLY actions."
        $reason = "Global hard stop is present."
        $sources = @("hard_stop")
    }
    elseif (@($ApprovalSummary.pending | Where-Object { $_.tier -match "2|TIER_2" }).Count -gt 0) {
        $priority = "HIGH"
        $summary = "Review pending Tier 2 approval requests."
        $reason = "Pending Tier 2 approvals require Human Owner review."
        $sources = @("approval_summary.pending")
    }
    elseif (@($QueueSummary.blocked).Count -gt 0) {
        $priority = "HIGH"
        $summary = "Run DRY_RUN review for blocked packets and identify unblock path."
        $reason = "Blocked packets are present."
        $sources = @("queue_summary.blocked")
    }
    elseif (@($LockSummary.stale_candidates).Count -gt 0) {
        $priority = "MEDIUM"
        $summary = "Run DRY_RUN stale lock inspection. Do not unlock automatically."
        $reason = "Stale lock candidates are present."
        $sources = @("lock_summary.stale_candidates")
    }
    elseif (@($QueueSummary.stale_candidates).Count -gt 0) {
        $priority = "MEDIUM"
        $summary = "Run DRY_RUN packet freshness review."
        $reason = "Stale packet candidates are present."
        $sources = @("queue_summary.stale_candidates")
    }
    elseif (@($QueueSummary.unknown + $ApprovalSummary.unknown).Count -gt 0) {
        $priority = "MEDIUM"
        $summary = "Run DRY_RUN metadata repair proposal."
        $reason = "Unknown or malformed metadata is present."
        $sources = @("queue_summary.unknown", "approval_summary.unknown")
    }

    [pscustomobject]@{
        action_id = "NSA-" + (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
        priority = $priority
        summary = $summary
        reason = $reason
        recommended_mode = "DRY_RUN"
        requires_human = $true
        allowed_to_auto_execute = $false
        suggested_codex_prompt = "AI_OS EXECUTION TOKEN`nRun a DRY_RUN review for Night Supervisor finding: $summary`nDo not edit, stage, commit, push, move packets, change approvals, or unlock files."
        source_findings = @($sources)
    }
}

function Write-AiOsJsonFile {
    param(
        [string]$Path,
        [object]$Value
    )

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    ConvertTo-AiOsJson -Value $Value | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Write-AiOsMorningBrief {
    param(
        [string]$Path,
        [object]$Report
    )

    $lines = @(
        "# AI_OS Morning Brief",
        "",
        "## Mission Header",
        "- Report ID: $($Report.report_id)",
        "- Generated At: $($Report.generated_at)",
        "- Branch: $($Report.branch)",
        "- Mode: $($Report.mode)",
        "- Hard Stop: $($Report.hard_stop.decision)",
        "",
        "## Executive Summary",
        "Night Supervisor inspected queues, locks, approvals, gates, worker files, and repo state without mutating operational state. Blockers found: $($Report.blocker_summary.total_blockers).",
        "",
        "## Overnight Status Board",
        "- Workers observed: $($Report.worker_summary.worker_files_found)",
        "- Packets waiting: $($Report.queue_summary.counts_by_status.WAITING)",
        "- Packets blocked: $($Report.queue_summary.counts_by_status.BLOCKED)",
        "- Stale locks: $($Report.lock_summary.stale_candidates.Count)",
        "- Pending approvals: $($Report.approval_summary.pending.Count)",
        "- Gate blocked events: $($Report.blocker_summary.gate_blocked_events)",
        "",
        "## Critical Blockers"
    )

    if ($Report.blocker_summary.critical_items.Count -eq 0) {
        $lines += "- None."
    }
    else {
        foreach ($item in @($Report.blocker_summary.critical_items)) {
            $lines += "- $($item.type): $($item.summary)"
        }
    }

    $lines += @("", "## Operator Required")
    if ($Report.blocker_summary.operator_required_items.Count -eq 0) {
        $lines += "- None."
    }
    else {
        foreach ($item in @($Report.blocker_summary.operator_required_items)) {
            $lines += "- $($item.type): $($item.summary)"
        }
    }

    $lines += @("", "## Worker Follow-Up")
    if ($Report.blocker_summary.worker_followup_items.Count -eq 0) {
        $lines += "- None."
    }
    else {
        foreach ($item in @($Report.blocker_summary.worker_followup_items)) {
            $lines += "- $($item.type): $($item.summary)"
        }
    }

    $lines += @(
        "",
        "## Next Safe Action",
        "$($Report.next_safe_action.summary)",
        "",
        "## Safety Notes",
        "- No mutations performed.",
        "- No approvals changed.",
        "- No locks changed.",
        "- No packets moved.",
        "- No staging, commit, push, merge, rebase, broker, OANDA, secret, scheduler, or dashboard work performed.",
        "",
        "## Report Paths",
        "- JSON report: $($Report.report_paths.json_report)",
        "- Blocker summary: $($Report.report_paths.blocker_summary)",
        "- Next safe action: $($Report.report_paths.next_safe_action)"
    )

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    $lines | Set-Content -LiteralPath $Path -Encoding UTF8
}

$warnings = @()
$errors = @()

try {
    $resolvedRepoRoot = Resolve-AiOsRepoRoot -RequestedRepoRoot $RepoRoot
    $config = Get-AiOsConfig -RepoRootPath $resolvedRepoRoot -RequestedConfigPath $ConfigPath -Warnings ([ref]$warnings)
    $resolvedOutputRoot = if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
        Resolve-AiOsPath -Root $resolvedRepoRoot -Path ([string]$config.output_root)
    } else {
        Resolve-AiOsPath -Root $resolvedRepoRoot -Path $OutputRoot
    }

    $reportId = New-AiOsReportId
    $timestamp = Get-AiOsUtcTimestamp
    $fileStamp = $timestamp -replace "[:-]", "" -replace "Z", "Z"
    $jsonReportPath = Join-Path $resolvedOutputRoot "NIGHT_SUPERVISOR_REPORT_$fileStamp.json"
    $morningBriefPath = Join-Path $resolvedOutputRoot "MORNING_BRIEF_$fileStamp.md"
    $blockerSummaryPath = Join-Path $resolvedOutputRoot "BLOCKER_SUMMARY_$fileStamp.json"
    $nextSafeActionPath = Join-Path $resolvedOutputRoot "NEXT_SAFE_ACTION_$fileStamp.json"

    $gitSummary = Get-AiOsGitSummary -RepoRootPath $resolvedRepoRoot
    $hardStop = Get-AiOsHardStopSummary -RepoRootPath $resolvedRepoRoot -Warnings ([ref]$warnings)
    $queueSummary = Get-AiOsQueueSummary -RepoRootPath $resolvedRepoRoot -Config $config -Warnings ([ref]$warnings)
    $lockSummary = Get-AiOsLockSummary -RepoRootPath $resolvedRepoRoot -Config $config -Warnings ([ref]$warnings)
    $approvalSummary = Get-AiOsApprovalSummary -RepoRootPath $resolvedRepoRoot -Config $config -Warnings ([ref]$warnings)
    $gateSummary = Get-AiOsGateSummary -RepoRootPath $resolvedRepoRoot -Config $config -HardStop $hardStop
    $workerSummary = Get-AiOsWorkerSummary -RepoRootPath $resolvedRepoRoot -Config $config -Warnings ([ref]$warnings)
    $blockerSummary = Get-AiOsBlockerSummary -HardStop $hardStop -QueueSummary $queueSummary -LockSummary $lockSummary -ApprovalSummary $approvalSummary -GateSummary $gateSummary
    $nextSafeAction = Get-AiOsNextSafeAction -HardStop $hardStop -QueueSummary $queueSummary -LockSummary $lockSummary -ApprovalSummary $approvalSummary -BlockerSummary $blockerSummary

    $report = [pscustomobject]@{
        schema = "AIOS_NIGHT_SUPERVISOR_REPORT"
        schema_version = "1.0"
        report_id = $reportId
        generated_at = $timestamp
        generated_by = $WorkerId
        mode = $Mode
        repo_root = $resolvedRepoRoot
        branch = $gitSummary.branch
        git_status_summary = $gitSummary
        hard_stop = $hardStop
        queue_summary = $queueSummary
        lock_summary = $lockSummary
        approval_summary = $approvalSummary
        gate_summary = $gateSummary
        worker_summary = $workerSummary
        blocker_summary = $blockerSummary
        next_safe_action = $nextSafeAction
        report_paths = [pscustomobject]@{
            json_report = if ($NoTelemetry) { "" } else { Get-AiOsRelativePath -Root $resolvedRepoRoot -Path $jsonReportPath }
            morning_brief = if ($NoTelemetry -or $NoMarkdown) { "" } else { Get-AiOsRelativePath -Root $resolvedRepoRoot -Path $morningBriefPath }
            blocker_summary = if ($NoTelemetry) { "" } else { Get-AiOsRelativePath -Root $resolvedRepoRoot -Path $blockerSummaryPath }
            next_safe_action = if ($NoTelemetry) { "" } else { Get-AiOsRelativePath -Root $resolvedRepoRoot -Path $nextSafeActionPath }
        }
        warnings = @($warnings + $gitSummary.warnings + $queueSummary.warnings + $lockSummary.warnings + $approvalSummary.warnings + $gateSummary.warnings + $workerSummary.warnings)
        errors = @($errors)
    }

    if (-not $NoTelemetry) {
        Write-AiOsJsonFile -Path $jsonReportPath -Value $report
        Write-AiOsJsonFile -Path $blockerSummaryPath -Value $blockerSummary
        Write-AiOsJsonFile -Path $nextSafeActionPath -Value $nextSafeAction
        if (-not $NoMarkdown) {
            Write-AiOsMorningBrief -Path $morningBriefPath -Report $report
        }
    }

    if ($QuietJson) {
        ConvertTo-AiOsJson -Value $report
        exit 0
    }

    Write-Host "AI_OS Night Supervisor V1"
    Write-Host "Mode: $Mode"
    Write-Host "Report ID: $reportId"
    Write-Host "Branch: $($report.branch)"
    Write-Host "Hard stop: $($hardStop.decision)"
    Write-Host "Packets scanned: $($queueSummary.packet_files_found)"
    Write-Host "Locks found: $($lockSummary.lock_files_found)"
    Write-Host "Approval files found: $($approvalSummary.approval_files_found)"
    Write-Host "Blockers: $($blockerSummary.total_blockers)"
    Write-Host "Next safe action: $($nextSafeAction.summary)"
    if (-not $NoTelemetry) {
        Write-Host "JSON report: $($report.report_paths.json_report)"
        if (-not $NoMarkdown) {
            Write-Host "Morning brief: $($report.report_paths.morning_brief)"
        }
    }
    Write-Host "Mutation skipped: Night Supervisor is read-only."
}
catch {
    $errors += $_.Exception.Message
    $fallback = [pscustomobject]@{
        schema = "AIOS_NIGHT_SUPERVISOR_REPORT"
        schema_version = "1.0"
        report_id = New-AiOsReportId
        generated_at = Get-AiOsUtcTimestamp
        generated_by = $WorkerId
        mode = $Mode
        repo_root = $RepoRoot
        branch = "UNKNOWN"
        git_status_summary = [pscustomobject]@{}
        hard_stop = [pscustomobject]@{}
        queue_summary = [pscustomobject]@{}
        lock_summary = [pscustomobject]@{}
        approval_summary = [pscustomobject]@{}
        gate_summary = [pscustomobject]@{}
        worker_summary = [pscustomobject]@{}
        blocker_summary = [pscustomobject]@{}
        next_safe_action = [pscustomobject]@{
            action_id = "NSA-ERROR"
            priority = "HIGH"
            summary = "Night Supervisor failed. Review script error before relying on report."
            reason = $_.Exception.Message
            recommended_mode = "DRY_RUN"
            requires_human = $true
            allowed_to_auto_execute = $false
            suggested_codex_prompt = "AI_OS EXECUTION TOKEN`nRun DRY_RUN troubleshooting for Night Supervisor failure. Do not mutate operational state."
            source_findings = @("script_error")
        }
        report_paths = [pscustomobject]@{}
        warnings = @($warnings)
        errors = @($errors)
    }
    ConvertTo-AiOsJson -Value $fallback
    exit 1
}
