# AIOS GitHub PR State

`aios_github_pr_state.py` parses gh-style JSON or text fixtures into
`AIOS_GITHUB_PR_STATE.v1`.

The contract reports PR number, branch, attached checks, passed and failed
checks, whether the required `validate` check is present, merge eligibility,
merge block reason, and next safe action. It recognizes no-checks-reported,
validate-pass, and validate-fail states.

The module is parser-only. It does not run `gh`, call GitHub, merge PRs, push
branches, or approve protected actions.
