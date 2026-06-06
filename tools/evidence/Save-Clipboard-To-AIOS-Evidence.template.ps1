param(
    [string]$EvidenceRoot = $env:AIOS_EVIDENCE_ROOT
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($EvidenceRoot)) {
    throw 'Set -EvidenceRoot or AIOS_EVIDENCE_ROOT to a local evidence drop folder before running this template.'
}

$captureFolder = Join-Path $EvidenceRoot 'manual_clipboard_captures'
New-Item -ItemType Directory -Force -Path $captureFolder | Out-Null

function Get-AiosSha256Hex {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        return (($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '').ToUpperInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Get-AiosFileSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)

    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Normalize-AiosClipboardBody {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text)

    $normalized = $Text -replace "`r`n", "`n" -replace "`r", "`n"
    $marker = '--- CLIPBOARD TEXT ---'
    $markerIndex = $normalized.IndexOf($marker, [System.StringComparison]::Ordinal)
    if ($markerIndex -ge 0) {
        $normalized = $normalized.Substring($markerIndex + $marker.Length)
    }

    $normalized = $normalized.Trim()
    $normalized = [regex]::Replace($normalized, "`n{3,}", "`n`n")
    return $normalized
}

function Get-AiosStrongSentences {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text)

    $genericPatterns = @(
        '^\s*$',
        '^\s*(hi|hello|hey|thanks|thank you|ok|okay)\s*[.!?]*\s*$',
        '^\s*(next step|summary|status|timestamp|capturedatlocal|sourcehint|classificationhint)\s*:?\s*.*$',
        '^\s*#+\s+.*$',
        '^\s*[-*_]{3,}\s*$',
        '^\s*ai_os telemetry clipboard evidence\s*$',
        '^\s*--- clipboard text ---\s*$'
    )

    $clean = $Text -replace "`r`n", "`n" -replace "`r", "`n"
    $parts = [regex]::Split($clean, '(?<=[.!?])\s+|`n+')
    $strong = New-Object System.Collections.Generic.List[string]

    foreach ($part in $parts) {
        $sentence = [regex]::Replace($part.Trim(), '\s+', ' ')
        if ([string]::IsNullOrWhiteSpace($sentence)) { continue }

        $isGeneric = $false
        foreach ($pattern in $genericPatterns) {
            if ($sentence -match $pattern) {
                $isGeneric = $true
                break
            }
        }
        if ($isGeneric) { continue }

        $wordCount = ([regex]::Matches($sentence, '\b[\p{L}\p{N}_-]+\b')).Count
        if ($wordCount -ge 8 -or $sentence.Length -ge 50) {
            $strong.Add($sentence.ToLowerInvariant())
        }
    }

    return @($strong | Sort-Object -Unique)
}

function Get-AiosWeakSimilarityTokens {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text)

    $genericWords = @(
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'your', 'you', 'are',
        'was', 'were', 'have', 'has', 'had', 'not', 'but', 'can', 'will', 'would',
        'should', 'next', 'step', 'thank', 'thanks', 'hello', 'status', 'summary',
        'timestamp', 'capturedatlocal', 'sourcehint', 'classificationhint'
    )

    $words = [regex]::Matches($Text.ToLowerInvariant(), '\b[\p{L}\p{N}_-]{3,}\b') |
        ForEach-Object { $_.Value } |
        Where-Object { $genericWords -notcontains $_ } |
        Sort-Object -Unique

    return @($words)
}

function Read-AiosExistingCaptureEvidence {
    param([Parameter(Mandatory = $true)][string]$Folder)

    $records = @()
    $files = @(Get-ChildItem -LiteralPath $Folder -File -Force -Filter 'AIOS_CLIPBOARD_EVIDENCE_*.txt' -ErrorAction SilentlyContinue)
    foreach ($file in $files) {
        try {
            $raw = Get-Content -LiteralPath $file.FullName -Raw
            $body = Normalize-AiosClipboardBody -Text $raw
            $records += [pscustomobject]@{
                saved_filename = $file.Name
                normalized_body_sha256 = Get-AiosSha256Hex -Text $body
                normalized_body_length = $body.Length
                strong_sentences = @(Get-AiosStrongSentences -Text $body)
                weak_similarity_tokens = @(Get-AiosWeakSimilarityTokens -Text $body)
            }
        } catch {
            $records += [pscustomobject]@{
                saved_filename = $file.Name
                normalized_body_sha256 = $null
                normalized_body_length = $null
                strong_sentences = @()
                weak_similarity_tokens = @()
                read_error = $_.Exception.Message
            }
        }
    }

    return @($records)
}

function Get-AiosDuplicateClassification {
    param(
        [Parameter(Mandatory = $true)][string]$NormalizedBodySha256,
        [Parameter(Mandatory = $true)][string[]]$StrongSentences,
        [Parameter(Mandatory = $true)][string[]]$WeakSimilarityTokens,
        [Parameter(Mandatory = $true)][object[]]$ExistingRecords
    )

    $exactMatches = @($ExistingRecords | Where-Object { $_.normalized_body_sha256 -eq $NormalizedBodySha256 })
    if ($exactMatches.Count -gt 0) {
        return [pscustomobject]@{
            duplicate_status = 'EXACT_DUPLICATE'
            count_in_metrics = $false
            reason = 'Same normalized_body_sha256 already exists.'
            duplicate_group_id = 'BODY_' + $NormalizedBodySha256.Substring(0, 12)
            matching_files = @($exactMatches.saved_filename)
            strong_sentence_match_count = 0
        }
    }

    $strongMatches = New-Object System.Collections.Generic.List[string]
    foreach ($record in $ExistingRecords) {
        foreach ($sentence in $StrongSentences) {
            if (@($record.strong_sentences) -contains $sentence) {
                $strongMatches.Add($record.saved_filename)
                break
            }
        }
    }

    $uniqueStrongMatches = @($strongMatches | Sort-Object -Unique)
    if ($uniqueStrongMatches.Count -gt 0) {
        return [pscustomobject]@{
            duplicate_status = 'PARTIAL_OVERLAP_STRONG_SENTENCE'
            count_in_metrics = $false
            reason = 'Full body hash differs, but at least one strong non-generic sentence appears in an existing capture.'
            duplicate_group_id = 'OVERLAP_' + $NormalizedBodySha256.Substring(0, 12)
            matching_files = $uniqueStrongMatches
            strong_sentence_match_count = $uniqueStrongMatches.Count
        }
    }

    $weakMatches = New-Object System.Collections.Generic.List[string]
    foreach ($record in $ExistingRecords) {
        $overlap = @($WeakSimilarityTokens | Where-Object { @($record.weak_similarity_tokens) -contains $_ })
        if ($overlap.Count -ge 2 -and $overlap.Count -le 5) {
            $weakMatches.Add($record.saved_filename)
        }
    }

    $uniqueWeakMatches = @($weakMatches | Sort-Object -Unique)
    if ($uniqueWeakMatches.Count -gt 0) {
        return [pscustomobject]@{
            duplicate_status = 'WEAK_SIMILARITY_IGNORE'
            count_in_metrics = $true
            reason = 'Only a short 2-5 word similarity was found; this is not classified as duplicate content.'
            duplicate_group_id = 'BODY_' + $NormalizedBodySha256.Substring(0, 12)
            matching_files = $uniqueWeakMatches
            strong_sentence_match_count = 0
        }
    }

    return [pscustomobject]@{
        duplicate_status = 'UNIQUE'
        count_in_metrics = $true
        reason = 'No matching normalized body hash or strong sentence overlap found.'
        duplicate_group_id = 'BODY_' + $NormalizedBodySha256.Substring(0, 12)
        matching_files = @()
        strong_sentence_match_count = 0
    }
}

function Write-AiosTextCreateNew {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Value
    )

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        $writer = New-Object System.IO.StreamWriter($stream, $utf8NoBom)
        try {
            $writer.Write($Value)
        } finally {
            $writer.Dispose()
        }
    } finally {
        $stream.Dispose()
    }
}

try {
    $clipboardText = Get-Clipboard -Raw -Format Text
} catch {
    Write-Host 'Clipboard empty. Nothing saved.'
    exit 0
}

if ([string]::IsNullOrWhiteSpace($clipboardText)) {
    Write-Host 'Clipboard empty. Nothing saved.'
    exit 0
}

$capturedAt = Get-Date
$normalizedBody = Normalize-AiosClipboardBody -Text $clipboardText
$normalizedBodySha256 = Get-AiosSha256Hex -Text $normalizedBody
$bodyHashSuffix = $normalizedBodySha256.Substring(0, 10)
$randomSuffix = [System.Guid]::NewGuid().ToString('N').Substring(0, 8).ToUpperInvariant()
$timestamp = $capturedAt.ToString('yyyy-MM-dd_HH-mm-ss-fff')

$outputPath = $null
$fileName = $null
for ($attempt = 0; $attempt -lt 25; $attempt++) {
    $attemptSuffix = if ($attempt -eq 0) { $randomSuffix } else { '{0}_{1:00}' -f $randomSuffix, $attempt }
    $fileName = 'AIOS_CLIPBOARD_EVIDENCE_{0}_{1}_{2}.txt' -f $timestamp, $bodyHashSuffix, $attemptSuffix
    $candidatePath = Join-Path $captureFolder $fileName
    $candidateMetadataPath = $candidatePath + '.metadata.json'
    if (-not (Test-Path -LiteralPath $candidatePath) -and -not (Test-Path -LiteralPath $candidateMetadataPath)) {
        $outputPath = $candidatePath
        break
    }
}

if ([string]::IsNullOrWhiteSpace($outputPath)) {
    throw 'Could not allocate a unique clipboard evidence filename without overwrite risk.'
}

$header = @(
    'AI_OS TELEMETRY CLIPBOARD EVIDENCE',
    ('CapturedAtLocal: {0}' -f $capturedAt.ToString('yyyy-MM-dd HH:mm:ss.fff zzz')),
    'SourceHint: manual clipboard capture',
    'ClassificationHint: user-copied evidence, verify before counting',
    '',
    '--- CLIPBOARD TEXT ---',
    ''
) -join [Environment]::NewLine

$captureText = $header + $clipboardText
Write-AiosTextCreateNew -Path $outputPath -Value $captureText

$rawFileSha256 = Get-AiosFileSha256 -Path $outputPath
$existingRecords = @(Read-AiosExistingCaptureEvidence -Folder $captureFolder | Where-Object { $_.saved_filename -ne $fileName })
$strongSentences = @(Get-AiosStrongSentences -Text $normalizedBody)
$weakSimilarityTokens = @(Get-AiosWeakSimilarityTokens -Text $normalizedBody)
$classification = Get-AiosDuplicateClassification `
    -NormalizedBodySha256 $normalizedBodySha256 `
    -StrongSentences $strongSentences `
    -WeakSimilarityTokens $weakSimilarityTokens `
    -ExistingRecords $existingRecords

$metadata = [ordered]@{
    saved_filename = $fileName
    saved_at = $capturedAt.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    file_size_bytes = (Get-Item -LiteralPath $outputPath).Length
    raw_file_sha256 = $rawFileSha256
    normalized_body_sha256 = $normalizedBodySha256
    normalized_body_length = $normalizedBody.Length
    capture_method = 'manual_clipboard_shortcut'
    duplicate_status = $classification.duplicate_status
    count_in_metrics = [bool]$classification.count_in_metrics
    reason = $classification.reason
    duplicate_group_id = $classification.duplicate_group_id
    matching_files = @($classification.matching_files)
    strong_sentence_match_count = [int]$classification.strong_sentence_match_count
    duplicate_logic = [ordered]@{
        exact_duplicate = 'Same normalized_body_sha256.'
        partial_overlap_strong_sentence = 'Different body hash, but at least one shared non-generic sentence with 8+ words or 50+ characters.'
        weak_similarity_ignore = 'Short phrase or 2-5 matching words only; not treated as duplicate.'
        unique = 'No exact hash match and no strong sentence overlap.'
    }
}

$metadataPath = $outputPath + '.metadata.json'
if (Test-Path -LiteralPath $metadataPath) {
    throw "Metadata path already exists and will not be overwritten: $metadataPath"
}

$metadataJson = ($metadata | ConvertTo-Json -Depth 8)
Write-AiosTextCreateNew -Path $metadataPath -Value ($metadataJson + [Environment]::NewLine)

Write-Host ('Saved clipboard evidence: {0}' -f $outputPath)
Write-Host ('Saved clipboard metadata: {0}' -f $metadataPath)
Write-Host ('duplicate_status: {0}' -f $classification.duplicate_status)
Write-Host ('count_in_metrics: {0}' -f $classification.count_in_metrics)
