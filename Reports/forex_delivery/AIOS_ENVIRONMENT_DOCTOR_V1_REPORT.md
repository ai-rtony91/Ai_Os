ENVIRONMENT_DOCTOR_STATUS: BLOCKED
POWERSHELL_VERSION: 7.6.3
REPO_PATH: C:/Dev/Ai.Os
CURRENT_BRANCH: main
CURRENT_HEAD: ff74df3f
MAIN_SYNC_STATUS: FETCH_FAILED: error: cannot open '.git/FETCH_HEAD': Permission denied
WORKTREE_STATUS: warning: unable to access 'C:\Users\mylab\.config\git\ignore': Permission denied
warning: unable to access 'C:\Users\mylab\.config\git\ignore': Permission denied
## main...origin/main
?? Reports/forex_delivery/AIOS_ENVIRONMENT_DOCTOR_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_NEXT_CODEX_PACKET_V1.md
?? Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_CHECKPOINT.md
?? Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_OWNER_APPROVAL_CARD.md
?? Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_STATE.json
?? automation/forex_engine/forex_promotion_pipeline_v1.py
?? scripts/forex_delivery/Invoke-ForexPromotionPipeline.V1.ps1
?? tests/forex_engine/test_forex_promotion_pipeline_v1.py
GIT_INDEX_WRITABLE: NO
GIT_REFS_WRITABLE: NO
GIT_BRANCH_CREATE_OK: NO
GIT_ADD_OK: NO_IGNORED_FILE
GIT_COMMIT_OK: NO
GITHUB_CONNECTIVITY: NETWORK_BLOCKED
GH_AUTH_STATUS: UNAUTHENTICATED
GH_REPO_ACCESS: FAILED: Post "https://api.github.com/graphql": dial tcp 140.82.112.6:443: connectex: An attempt was made to access a socket in a way forbidden by its access permissions.
PUSH_CAPABILITY: SKIPPED_BRANCH_FAIL
PR_CAPABILITY: BLOCKED
MERGE_CAPABILITY: BLOCKED
ACL_DENIES_FOUND: 2
USER_GIT_IGNORE_ACCESS: ACCESS_DENIED
CODEX_NETWORK_ACCESS: NETWORK_BLOCKED
BLOCKERS: Cannot stat ~/.config/git/ignore; Cannot write .git/refs/heads; Cannot write to .git directory; gh auth status failed: github.com   X Failed to log in to github.com account ai-rtony91 (default)   - Active account: true   - The token in default is invalid.   - To re-authenticate, run: gh auth login -h github.com   - To forget about this account, run: gh auth logout -h github.com -u ai-rtony91; gh repo view failed: Post "https://api.github.com/graphql": dial tcp 140.82.112.6:443: connectex: An attempt was made to access a socket in a way forbidden by its access permissions.; git branch create failed: fatal: cannot lock ref 'refs/heads/doctor-temp-97ce5d56c01b4d26a00b7295b562733d': Unable to create 'C:/Dev/Ai.Os/.git/refs/heads/doctor-temp-97ce5d56c01b4d26a00b7295b562733d.lock': Permission denied; git commit --dry-run failed; git fetch origin main failed; github.com network blocked; No ignored temp file candidate available for write test; Unable to create/remove .git/index.lock
SAFE_REPAIRS_ATTEMPTED: create branch doctor-temp-97ce5d56c01b4d26a00b7295b562733d
SAFE_REPAIRS_SUCCEEDED: NONE
SAFE_REPAIRS_FAILED: .git write probe; .git/refs/heads write probe; create branch doctor-temp-97ce5d56c01b4d26a00b7295b562733d; index.lock create/remove
READINESS_SCORE_PERCENT: 10
OVERNIGHT_READY: NO
NEXT_REQUIRED_HUMAN_ACTION: Fix blocker list and rerun AIOS_ENVIRONMENT_DOCTOR_V1.
STOP_REASON: Readiness blockers detected; commit/push/PR path is unsafe.
