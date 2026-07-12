#!/usr/bin/env bash
set -Eeuo pipefail

REPO="ai-rtony91/Ai_Os"
BASE="main"
MODE="dry-run"
MAX_PRS=100

usage() {
  echo "Usage:"
  echo "  $0 --dry-run PR_NUMBER..."
  echo "  $0 --execute PR_NUMBER..."
}

fail() {
  echo "BLOCKED: $1" >&2
  exit 1
}

if [[ "${1:-}" == "--execute" ]]; then
  MODE="execute"
  shift
elif [[ "${1:-}" == "--dry-run" ]]; then
  MODE="dry-run"
  shift
else
  usage
  exit 2
fi

[[ "$#" -ge 1 ]] || fail "No approved PR numbers supplied."
[[ "$#" -le "$MAX_PRS" ]] || fail "Maximum approved PR count is $MAX_PRS."

command -v git >/dev/null || fail "git is unavailable."
command -v gh >/dev/null || fail "GitHub CLI is unavailable."
command -v jq >/dev/null || fail "jq is unavailable."

gh auth status >/dev/null 2>&1 || fail "GitHub CLI is not authenticated."

origin="$(git remote get-url origin)"
[[ "$origin" =~ github\.com[:/]ai-rtony91/Ai_Os(\.git)?$ ]] ||
  fail "Unexpected repository origin: $origin"

[[ -z "$(git status --porcelain)" ]] ||
  fail "Git status is dirty before execution."

git fetch origin --prune
git switch "$BASE"
git pull --ff-only origin "$BASE"

[[ -z "$(git status --porcelain)" ]] ||
  fail "Git status became dirty during synchronization."

audited=0
merged=0

for pr in "$@"; do
  [[ "$pr" =~ ^[0-9]+$ ]] || fail "Invalid PR number: $pr"

  echo
  echo "AUDITING PR #$pr"

  data="$(
    gh pr view "$pr" \
      --repo "$REPO" \
      --json number,title,url,state,isDraft,baseRefName,headRefOid,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
  )"

  state="$(jq -r '.state' <<<"$data")"
  draft="$(jq -r '.isDraft' <<<"$data")"
  base="$(jq -r '.baseRefName' <<<"$data")"
  head="$(jq -r '.headRefOid' <<<"$data")"
  mergeable="$(jq -r '.mergeable' <<<"$data")"
  merge_state="$(jq -r '.mergeStateStatus' <<<"$data")"
  review="$(jq -r '.reviewDecision // ""' <<<"$data")"
  title="$(jq -r '.title' <<<"$data")"

  [[ "$state" == "OPEN" ]] || fail "PR #$pr is not open."
  [[ "$draft" == "false" ]] || fail "PR #$pr is still a draft."
  [[ "$base" == "$BASE" ]] || fail "PR #$pr targets $base instead of $BASE."
  [[ -n "$head" && "$head" != "null" ]] || fail "PR #$pr has no valid head SHA."
  [[ "$mergeable" == "MERGEABLE" ]] || fail "PR #$pr mergeable state is $mergeable."
  [[ "$merge_state" =~ ^(CLEAN|HAS_HOOKS|UNSTABLE)$ ]] ||
    fail "PR #$pr merge state is $merge_state."
  [[ "$review" != "CHANGES_REQUESTED" ]] ||
    fail "PR #$pr has requested changes."

  failed_checks="$(
    jq -r '
      .statusCheckRollup[]? |
      {
        name: (.name // .context // "unnamed"),
        result: (.conclusion // .state // .status // "UNKNOWN")
      } |
      select(
        .result != "SUCCESS" and
        .result != "NEUTRAL" and
        .result != "SKIPPED"
      ) |
      "\(.name)=\(.result)"
    ' <<<"$data"
  )"

  [[ -z "$failed_checks" ]] || {
    echo "$failed_checks"
    fail "PR #$pr has incomplete or failed checks."
  }

  refreshed_head="$(
    gh pr view "$pr" \
      --repo "$REPO" \
      --json headRefOid \
      --jq '.headRefOid'
  )"

  [[ "$refreshed_head" == "$head" ]] ||
    fail "PR #$pr changed during validation."

  audited=$((audited + 1))

  if [[ "$MODE" == "dry-run" ]]; then
    echo "DRY_RUN_PASS: PR #$pr — $title"
    continue
  fi

  echo "MERGING: PR #$pr — $title"

  gh pr merge "$pr" \
    --repo "$REPO" \
    --squash \
    --delete-branch \
    --match-head-commit "$head"

  merged_state="$(
    gh pr view "$pr" \
      --repo "$REPO" \
      --json state \
      --jq '.state'
  )"

  [[ "$merged_state" == "MERGED" ]] ||
    fail "PR #$pr merge was not confirmed."

  git fetch origin --prune
  git switch "$BASE"
  git pull --ff-only origin "$BASE"

  [[ -z "$(git status --porcelain)" ]] ||
    fail "Git status is dirty after merging PR #$pr."

  merged=$((merged + 1))
  echo "MERGED_AND_VERIFIED: PR #$pr"
done

echo
echo "COMPLETE: mode=$MODE audited=$audited merged=$merged"
