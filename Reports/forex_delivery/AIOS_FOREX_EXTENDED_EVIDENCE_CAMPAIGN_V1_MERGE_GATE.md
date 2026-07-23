# AIOS Forex Extended Evidence Campaign V1 Merge Gate

Merge only when:

- the branch diff contains only the intended campaign files and daily-orchestrator integration;
- targeted tests pass;
- repository CI passes;
- the full Forex suite passes or an explicit evidence-backed exception is approved;
- no credential, account ID, `.env`, broker payload, or private identifier is present;
- live trading and automatic order authority remain false.

Until those conditions are met, the branch remains a draft production-candidate evidence improvement only.
