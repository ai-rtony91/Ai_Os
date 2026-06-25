# AIOS Forex Supervised Demo Broker Snapshot Intake Manual Finalization V1

## Safety Boundary

These commands are for Anthony after review. Codex did not stage, commit, push, create a PR, merge, call a broker, or place a trade.

No broad add-dot staging is allowed.

## Manual Validation Commands

```powershell
python -m py_compile automation/forex_engine/sanitized_broker_snapshot_redaction_guard_v1.py automation/forex_engine/sanitized_broker_snapshot_intake_v1.py automation/forex_engine/demo_broker_snapshot_review_packet_v1.py automation/forex_engine/supervised_demo_broker_snapshot_intake_epic_v1.py scripts/forex_delivery/run_sanitized_broker_snapshot_intake_v1.py scripts/forex_delivery/run_demo_broker_snapshot_review_packet_v1.py scripts/forex_delivery/run_supervised_demo_broker_snapshot_intake_epic_v1.py tests/forex_engine/test_sanitized_broker_snapshot_redaction_guard_v1.py tests/forex_engine/test_sanitized_broker_snapshot_intake_v1.py tests/forex_engine/test_demo_broker_snapshot_review_packet_v1.py tests/forex_engine/test_supervised_demo_broker_snapshot_intake_epic_v1.py
python -m pytest tests/forex_engine/test_sanitized_broker_snapshot_redaction_guard_v1.py tests/forex_engine/test_sanitized_broker_snapshot_intake_v1.py tests/forex_engine/test_demo_broker_snapshot_review_packet_v1.py tests/forex_engine/test_supervised_demo_broker_snapshot_intake_epic_v1.py -q
python scripts/forex_delivery/run_sanitized_broker_snapshot_intake_v1.py --sample-ready
python scripts/forex_delivery/run_sanitized_broker_snapshot_intake_v1.py --sample-blocked
python scripts/forex_delivery/run_sanitized_broker_snapshot_intake_v1.py --sample-ready --json
python scripts/forex_delivery/run_demo_broker_snapshot_review_packet_v1.py --sample-ready --json
python scripts/forex_delivery/run_supervised_demo_broker_snapshot_intake_epic_v1.py --sample-ready --json
python scripts/forex_delivery/run_supervised_demo_broker_snapshot_intake_epic_v1.py --sample-ready --markdown
git diff --check
git status --short --branch
```

## Manual Finalization Commands

Run only after review and explicit protected-action approval.

```powershell
# If needed:
git checkout -b feature/forex-supervised-demo-broker-snapshot-intake-v1
git add automation/forex_engine/sanitized_broker_snapshot_redaction_guard_v1.py
git add automation/forex_engine/sanitized_broker_snapshot_intake_v1.py
git add automation/forex_engine/demo_broker_snapshot_review_packet_v1.py
git add automation/forex_engine/supervised_demo_broker_snapshot_intake_epic_v1.py
git add scripts/forex_delivery/run_sanitized_broker_snapshot_intake_v1.py
git add scripts/forex_delivery/run_demo_broker_snapshot_review_packet_v1.py
git add scripts/forex_delivery/run_supervised_demo_broker_snapshot_intake_epic_v1.py
git add tests/forex_engine/test_sanitized_broker_snapshot_redaction_guard_v1.py
git add tests/forex_engine/test_sanitized_broker_snapshot_intake_v1.py
git add tests/forex_engine/test_demo_broker_snapshot_review_packet_v1.py
git add tests/forex_engine/test_supervised_demo_broker_snapshot_intake_epic_v1.py
git add Reports/forex_delivery/AIOS_FOREX_SANITIZED_BROKER_SNAPSHOT_INTAKE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_DEMO_BROKER_SNAPSHOT_REVIEW_PACKET_V1.md
git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_EPIC_REPORT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_MANUAL_FINALIZATION_V1.md
git diff --cached
git commit -m "Add forex supervised demo broker snapshot intake"
git push -u origin feature/forex-supervised-demo-broker-snapshot-intake-v1
gh pr create --title "Add forex supervised demo broker snapshot intake" --body "Build-only local supervised demo broker snapshot intake V1. No broker call. No trade placed. Broker action remains false." --base main --head feature/forex-supervised-demo-broker-snapshot-intake-v1 --draft
gh pr checks --watch
gh pr ready <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --delete-branch
git switch main
git pull --ff-only
git status --short --branch
git log -1 --oneline
```

## Stop Condition

Stop if validation fails, the diff contains files outside the allowed paths, any protected permission flag becomes true, or any command asks for broker credentials or account identifiers.
