# AI_OS Repo Line Count Metric

- Timestamp: 2026-06-05T20:12:53Z
- Branch: main
- Repo path: C:\Dev\Ai.Os
- Files counted: 3484
- Total lines: 228946
- Exclusion rule: tracked files excluding telemetry, .git, node_modules, dist, and build path roots.

## Summary

Current AI_OS tracked-file line count is 228946 lines across 3484 tracked files after excluding telemetry, .git, node_modules, dist, and build path roots.

This metric includes code, docs, scripts, schemas, configs, and data files. It is not a pure source-code-only line count.

## Command Used

```powershell
git ls-files | Where-Object { $_ -notmatch '(^|/)(telemetry|\.git|node_modules|dist|build)/' } | ForEach-Object {
  if (Test-Path $_) { Get-Content $_ -ErrorAction SilentlyContinue | Measure-Object -Line }
} | Measure-Object -Property Lines -Sum
```

## Measurement Note

The expected packet observation was 3484 files and 228944 lines. The current measured value from this run was 3484 files and 228946 lines.
