# AIOS Approved Executor Loop Lite

## Purpose

This lite contract describes the safe shape of an approved executor loop before any runtime activation. It documents the rule that AIOS may run only explicitly approved local packets and must stop before protected Git actions or worker dispatch.

This document does not activate a scheduler, daemon, worker, queue, approval mutation, or command runner.

## Allowed

- Read selected packet evidence.
- Verify the packet has explicit Human Owner approval for the exact scope.
- Verify allowed paths, forbidden paths, validators, and stop point.
- Produce a report-only next safe action.

## Blocked

- worker dispatch without approval
- queue mutation
- approval mutation
- scheduler or daemon activation
- broker, live, credential, order, webhook, or network work
- `git add`, commit, push, merge, reset, clean, or branch deletion

## Stop Point

The loop stops at report-only evidence unless a separate packet authorizes an exact local APPLY runner and the protected-action gates remain closed.
