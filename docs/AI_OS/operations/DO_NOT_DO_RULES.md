# Do Not Do Rules

Status: CURRENT
Mode: Operations documentation

## Purpose

These are hard operating boundaries for MAIN CONTROL and worker lanes.

## Never Do Without Explicit Approval

- Do not edit files before DRY_RUN review.
- Do not edit protected root governance files.
- Do not edit `.codex_backups/`.
- Do not edit `apps/dashboard/assets/`.
- Do not stage files.
- Do not commit.
- Do not push.
- Do not create PRs.
- Do not merge.
- Do not delete, move, rename, reset, clean, or prune files or branches.
- Do not change credentials, secrets, API keys, tokens, private keys, or recovery keys.
- Do not change registry, firewall, VPN, browser policies, BitLocker, BIOS, UEFI, startup tasks, or scheduled tasks.

## Trading Safety Blocks

- No live trading.
- No broker connection.
- No OANDA integration.
- No API keys.
- No real webhooks.
- No real orders.
- No hidden execution paths.
- No LLM directly in live order execution paths.

Paper-only simulation and local validation are allowed only when explicitly scoped.

## Runtime And Automation Blocks

- Do not run infinite background loops without approval.
- Do not resume APPLY automatically after interruption.
- Do not reassign packets automatically.
- Do not release locks automatically.
- Do not retry failed packets automatically.
- Do not treat telemetry replay as approval.
- Do not treat dashboard visibility as execution authority.

## Documentation Blocks

- Do not overwrite existing docs blindly.
- Do not create duplicate docs if a canonical file exists.
- Do not rely on unlabeled draft docs as current policy.
- Do not treat Reports as instructions unless marked CURRENT.
- Mark unverifiable claims as UNKNOWN.
- Mark conflicting evidence as MISMATCH.
- Mark unverifiable conflicting evidence as INVALID DATA.

## Worker Blocks

- Worker lanes must not free-roam.
- Worker lanes must not edit outside approved paths.
- Worker lanes must not overlap another active lane without MAIN CONTROL review.
- Worker lanes must not continue past their stop point.
- Worker lanes must not assume APPLY, commit, push, PR, or merge approval.

## Next Safe Action

If a requested action touches any blocked area, stop and request exact operator approval.
