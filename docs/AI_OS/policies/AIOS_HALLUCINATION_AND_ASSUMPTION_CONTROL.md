# AIOS Hallucination and Assumption Control

Purpose:
Prevent AI\_OS reports, prompts, worker outputs, and trading workflow notes from claiming unverified facts.

Rules:

* Mark unknown items as UNKNOWN.
* Do not invent file paths, repo status, commits, trade results, broker status, or validation results.
* Verify files before referencing them.
* Verify git status before claiming clean or dirty state.
* Keep live trading, broker execution, OANDA, API keys, and real orders blocked unless explicitly approved in a later validated phase.
* Use HALLUCINATION\_LOG.md to record mistakes after they happen.
* Use this file to prevent mistakes before they happen.

Startup Check:

* Confirm repo path.
* Confirm branch.
* Confirm git status.
* Confirm required policy files exist.
* Confirm no missing file paths are opened by AM startup scripts.

