# AI_OS Dashboard First Deploy Runbook

## Deployment Overview

This runbook covers the first manual deployment of the AI_OS dashboard to Azure App Service `algotradez-aios`.

The deployment is a static Vite dashboard deployment. It is not a Python backend deployment and does not require `app.py`, `server.py`, Flask, FastAPI, Gunicorn, `requirements.txt`, or a Python startup command.

The dashboard source lives in `apps/dashboard/`. The GitHub Actions workflow runs `npm ci` and `npm run build` from that folder. Vite then emits the deployable static output into:

```text
apps/dashboard/dist
```

The workflow deploys that `dist` folder to Azure App Service. It is intentionally manual-only for the first deployment:

```text
workflow_dispatch
```

Manual-only deployment keeps the operator in control while Azure platform settings, publish profile scope, and static file behavior are verified.

## Azure Portal Readiness Checklist

Use the Azure Portal browser UI only. Do not use Azure CLI for this checklist.

Target App Service:

```text
algotradez-aios
```

Before clicking any GitHub Actions Run workflow button:

- Confirm the Azure Portal is using the expected directory and subscription for AI_OS.
- Open App Services and select `algotradez-aios`.
- Confirm the App Service exists.
- Confirm the App Service status is Running.
- Confirm the App Service URL is `https://algotradez-aios.azurewebsites.net`.
- Confirm the platform/runtime settings are compatible with serving static files from a deployed folder.
- Confirm there is no startup command pointing to Python, `app.py`, `main.py`, `server.py`, Flask, FastAPI, Gunicorn, or `requirements.txt`.
- Confirm static file behavior is expected for a Vite build artifact.
- If the setting is visible, confirm default document behavior can serve `index.html`.
- Open the App Service URL before deployment and record the visible result.
- Preserve screenshots or notes from any 403, 404, runtime, or default-document page before changing settings.

## GitHub Readiness Checklist

Use GitHub in the browser. Do not run the workflow until Azure Portal readiness is checked.

- Confirm the workflow named `Azure Deploy AI_OS Dashboard` appears under GitHub Actions.
- Confirm the workflow has a manual Run workflow button.
- Confirm the workflow is not auto-triggered by push.
- Confirm repository secret exists by name only:

```text
AZUREAPPSERVICE_PUBLISHPROFILE_ALGOTRADEZ_AIOS
```

Do not reveal, paste, decode, download, or inspect the secret value or publish profile XML.

## First Deploy Safety Warnings

Expected first-deploy failure modes include:

- 403 or 404 because Azure is serving the wrong folder.
- 403 or 404 because `index.html` is not present at the deployed root.
- Runtime mismatch if the App Service expects a backend process instead of static files.
- Wrong publish profile target if the secret points to another App Service.
- Deploy-before-validation risk if the workflow is run before platform settings are checked.
- Accidental backend assumptions, such as trying to configure Python startup behavior for a static Vite output.

Do not repeatedly redeploy to guess at the fix. Capture the visible Azure result first, then diagnose from evidence.

## Rollback Guidance

If the first deployment fails or produces an unexpected site state:

- Stop and preserve the GitHub Actions run logs.
- Preserve screenshots of the App Service URL result.
- Preserve Azure Portal configuration screenshots before changing settings.
- Do not run repeated panic redeploys.
- Do not add backend startup commands for this static dashboard workflow.
- If necessary, temporarily disable or restrict the workflow through GitHub UI until the operator approves the next recovery step.
- Use a new DRY_RUN recovery packet before changing workflow, Azure settings, publish profiles, or deployment targets.
