# Open PR State Capture After #533

Status: LOW_CONFIDENCE_FALLBACK

The packet requested:

```powershell
gh pr list --state open --limit 100 --json number,title,headRefName,baseRefName,mergeable,updatedAt,url > Reports/autonomy_loop_closure/open_pr_state_after_533.json
```

The command did not execute because the Windows sandbox returned:

```text
windows sandbox: runner error: CreateProcessAsUserW failed: 1312
```

No PR was closed, merged, edited, rebased, retargeted, or deleted. This packet will continue using `Reports/pr_backlog_reconciliation/open_pr_backlog_after_570_reconciliation.json` as stale-but-useful reconciliation evidence and will mark current PR state confidence as `LOW`.
