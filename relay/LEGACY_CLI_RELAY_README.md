# CLI Relay Legacy Fallback

Status: LEGACY_FALLBACK_ONLY

CLI relay is deprecated from the active AI_OS automation path.

The main active automation path is:

```text
AI_OS packet queue -> worker assignment -> Codex/APPLY lane -> validator -> approval inbox -> commit package -> dashboard status
```

CLI relay is preserved only as an Emergency Bridge / Manual Fallback / Copy-Paste Relief Tool.

Allowed uses:

- ChatGPT/Codex/Claude handoff breaks.
- Terminal output is too long to paste.
- Codex logs need to be captured into files.
- Mobile approval/status needs a simple file/message bridge.
- Supervisor queue fails and manual recovery evidence is needed.

Blocked uses:

- Main task routing.
- APPLY authority.
- Approval authority.
- Commits.
- Worker control.
- Main automation ownership.

Relay approval evidence is historical evidence only unless a current approved packet explicitly promotes it.

Do not delete relay until the replacement queue/approval bridge is proven.
