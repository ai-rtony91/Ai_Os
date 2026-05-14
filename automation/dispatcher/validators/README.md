# Dispatcher Validators

Validators check whether the dispatcher scaffold is present and whether the repo is safe enough for the next controlled step.

The validators in this folder are DRY_RUN helpers. They must not modify files.

Current validator:

- `Test-AIOSDispatcherDryRun.ps1`

Validator duties:

- Run from repo root.
- Print dispatcher folder status.
- Check required dispatcher folders exist.
- Check required dispatcher docs exist.
- Check required `Reports/dispatcher` example JSON files exist.
- Parse `Reports/dispatcher/*.json`.
- Run `git status --short --branch`.
- Run `git diff --check`.
- Scan dispatcher files for blocked safety terms.
- Report `PASS` or `FAIL`.

