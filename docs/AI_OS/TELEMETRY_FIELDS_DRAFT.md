# AI_OS Telemetry Fields Draft

## Purpose

This draft defines future telemetry fields for AI_OS work sessions. It does not implement telemetry automation and does not migrate any existing metrics file.

## Draft Fields

| Field | Purpose | Draft value rule |
|---|---|---|
| date | Calendar date for the work session | `YYYY-MM-DD` |
| stage | AI_OS stage or task label | Human-readable stage name |
| session_start_time | Session start timestamp | Local time, include timezone when available |
| session_end_time | Session end timestamp | Local time, include timezone when available |
| codex_opened | Whether Codex was opened for the session | `true`, `false`, or `UNKNOWN` |
| user_input_char_count | Count of user-entered characters | Integer or `UNKNOWN` if transcript is unavailable |
| ai_output_char_count | Count of assistant output characters | Integer or `UNKNOWN` if transcript is unavailable |
| codex_prompt_char_count | Count of prompt/work-order characters sent to Codex | Integer or `UNKNOWN` |
| codex_output_char_count | Count of Codex-generated output characters | Integer or `UNKNOWN` |
| files_created | Count of files created during the session | Integer |
| files_changed | Count of existing files changed during the session | Integer |
| files_deleted | Count of files deleted during the session | Integer, normally `0` unless separately approved |
| git_commit_hash | Commit hash associated with the session | Full hash, short hash, `NONE`, or `UNKNOWN` |
| git_status_final | Final git status summary | Output summary from `git status --short --branch` |
| progress_percent | Estimated AI_OS progress percentage | Requires a future approved formula |
| screen_recording_used | Whether approved screen recording was used | `true` or `false` |
| screen_recording_path | Path to approved recording evidence | Blank, approved path, or `UNKNOWN` |
| privacy_review_required | Whether privacy review is needed | `true`, `false`, or `UNKNOWN` |

## Notes

- Character counts are draft telemetry only until transcript export and counting rules are approved.
- `progress_percent` must not be automated until a formula is approved.
- Existing `Reports\DAILY_METRICS.csv` must not be edited by this draft.
