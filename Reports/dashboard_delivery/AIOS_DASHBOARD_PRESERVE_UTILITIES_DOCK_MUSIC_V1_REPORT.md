# AIOS Dashboard Preserve Utilities Dock Music V1 Report

## Summary

The new React dashboard page now mounts the legacy Utilities, Dock, and Music Player modules. The build output keeps the React `dist/index.html` entrypoint and still copies the legacy static preview as a separate artifact, so the old page remains available but not deleted.

## Preserved Modules

- Utilities
  - Legacy source: `apps/dashboard/AIOS_STATIC_PREVIEW.html`
  - Legacy behavior: `apps/dashboard/js/aios-static-preview.js` (`runSoftRefresh`)
  - New destination: `apps/dashboard/src/PreservedLegacyModules.jsx`
- Dock
  - Legacy source: `apps/dashboard/AIOS_STATIC_PREVIEW.html`
  - Legacy behavior: `apps/dashboard/js/aios-static-preview.js` (`setYouTubeDockCollapsed`, `handleYouTubeRadioControl`, `handleYouTubeRadioVolume`)
  - New destination: `apps/dashboard/src/PreservedLegacyModules.jsx`
- Music Player
  - Legacy source: `apps/dashboard/AIOS_MUSIC_COMPANION.html`
  - Legacy behavior: `apps/dashboard/AIOS_MUSIC_COMPANION.html` inline player script (`runCommand`, `applyRestoreState`, `retrySingleVideo`, `window.onYouTubeIframeAPIReady`)
  - New destination: `apps/dashboard/src/PreservedLegacyModules.jsx`

## What Changed

- Added `apps/dashboard/src/PreservedLegacyModules.jsx` to rehydrate the legacy utilities drawer, dock controls, and YouTube player behavior in React.
- Added `apps/dashboard/src/PreservedLegacyModules.css` to style the preserved modules without changing the old static preview files.
- Mounted the preserved modules in `apps/dashboard/src/MinimalOperatorDashboard.jsx`.
- Updated `apps/dashboard/vite.config.js` so `dist/index.html` stays the React deployment entry instead of being overwritten by `AIOS_STATIC_PREVIEW.html`.

## What Remains Deletion-Candidate

These files were preserved and left in place:

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/js/aios-static-preview.js`
- `apps/dashboard/css/aios-static-preview.css`
- `apps/dashboard/AIOS_MUSIC_COMPANION.html`

## Validation Commands

- `cd C:\Dev\Ai.Os\apps\dashboard`
- `npm run build`
- `cd C:\Dev\Ai.Os`
- `git status --short --branch`

## Validation Result

- Build passed successfully.
- Git status shows only the intended source changes in the feature branch.
