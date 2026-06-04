# Phase 16.4-16.10 OpenAI Planner Pipeline Design

Status: DRY_RUN docs/fixtures design

## Purpose

This design describes the local-only planner pipeline that turns one fake goal into a full AI_OS repo-work packet lifecycle preview.

No OpenAI API call, API key, package install, network call, runtime autonomy, approval inbox write, telemetry write, broker action, OANDA action, live trading action, commit, push, or merge is enabled.

## 16.4 Planner -> Packet Generator

The planner reads a fixture goal and classifies safety. It produces a deterministic planner result and recommends a packet ID.

## 16.5 Packet Generator -> Worker Assignment

The packet generator creates a Codex-ready draft packet marked `DRAFT_ONLY`, `NO_APPLY_AUTHORITY`, `NO_COMMIT`, `NO_PUSH`, `NO_MERGE`, and `NO_LIVE_API_CALL`.

The worker assignment preview recommends a DRY_RUN Codex lane with bounded allowed and forbidden paths.

## 16.6 Worker Assignment -> Validator Chain

The validator chain preview lists the checks needed before a worker can safely continue:

- git clean-state check.
- allowed path check.
- forbidden path check.
- validate-only runner check.
- JSON integrity check.
- no-secret check.
- no-network check.
- trading safety check.
- final git status.

## 16.7 Validator Chain -> Approval Inbox Preview

The approval preview is inert evidence only. It does not write to `automation/orchestration/approval_inbox/` and cannot approve APPLY.

## 16.8 Approval Inbox -> Commit Package Preview

The commit package preview shows what a future commit package might contain, but `commit_allowed` and `push_allowed` stay false.

## 16.9 Commit Package -> Clean-State Verifier Preview

The clean-state verifier preview defines pass/fail logic for dirty files, untracked files, forbidden paths, and final sync.

## 16.10 Real OpenAI API Adapter Boundary

The real adapter remains documentation-only in this pack. A future adapter requires separate human approval and must start with dry-run and no-write validation modes.

## Copy-Paste Reduction

This pipeline reduces relay work by producing the planner result, Codex packet draft, worker assignment, validator chain, approval preview, commit package preview, and clean-state verifier preview from one goal fixture.
