# AIOS Forex Validation Acceleration Plan V1

## 1. Status
`PARTIAL`

## 2. Current validators
- `python -m compileall -q -j 0 automation tests scripts`
- `python -m pytest tests/forex_engine/ -q`
- `python -m pytest tests/security/test_aios_bitwarden_local_credential_broker_v1.py -q`
- `git diff --check`
- Optional if `xdist` is available: `python -m pytest tests/forex_engine/ -q -n auto`

## 3. Safe CPU-heavy validators
- `compileall` is the cheapest broad syntax sweep and can use all available workers.
- The Forex engine test suite is the main local logic validator.
- The local security credential broker test stays in the plan because it is a repository-local safety check, not a broker call.
- `git diff --check` remains the final whitespace and patch-shape guard.

## 4. xdist detection plan
Use a local import check before attempting the parallel pytest path:

```powershell
python -c "import importlib.util; print('installed' if importlib.util.find_spec('xdist') else 'missing')"
```

If `xdist` is installed, run the Forex suite with `-n auto`. If it is missing, skip the parallel form and keep the baseline pytest run.

## 5. compileall parallel plan
- Run `python -m compileall -q -j 0 automation tests scripts`.
- Use the whole-tree pass first so syntax errors surface before slower test work.
- Do not narrow the syntax sweep unless a later packet introduces a reason to do so.

## 6. read-only rg scan plan
- Re-run targeted `rg -n` searches after any future code change to confirm the proof, drawdown, receipt, dashboard, and repeatability surfaces still match the reports.
- Keep the scans read-only and side-effect free.
- Use the scan as evidence, not as approval.

## 7. validators that must remain serialized
- `git diff --check`
- `gh pr checks --watch`
- `gh pr merge --squash --delete-branch`
- Any validator that writes to a shared temporary path, a shared cache, or the git index
- Any validator whose output must be read before the next gate is safe

## 8. validators that must not run because they need network or secrets
- Broker API tests.
- Live execution checks.
- Demo or live order placement checks.
- Credential or account-ID fetches.
- `.env` reads or secret extraction checks.
- Any validator that depends on external broker connectivity.

## 9. recommended command chain

```powershell
python -m compileall -q -j 0 automation tests scripts
python -m pytest tests/forex_engine/ -q
python -c "import importlib.util; print('installed' if importlib.util.find_spec('xdist') else 'missing')"
python -m pytest tests/forex_engine/ -q -n auto
python -m pytest tests/security/test_aios_bitwarden_local_credential_broker_v1.py -q
git diff --check
```

If `xdist` is missing, skip the `-n auto` line and keep the rest of the chain.
