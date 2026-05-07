# AI_OS Tooltip And Panel Help System Draft

## Purpose

This draft defines future tooltip and panel help behavior for AI_OS dashboard usability. It is DRY_RUN-only and creates no production dashboard UI.

Dashboard production outputs require separate approval.

## Hover Explanations

Tooltips may provide short hover explanations for panel labels, validator states, alert badges, protected-file status, and disabled actions.

## Panel Descriptions

Panel descriptions should explain purpose, data source, validation state, refresh behavior, and safety boundary.

## Validator Help

Validator help should explain PASS, WARN, FAIL, and BLOCKED without hiding the raw validator result.

## Protected-File Warnings

Protected-file warnings should explain why protected root files, DAILY_METRICS, and CHECKPOINT_INDEX require special approval.

## Alert Severity Meanings

Alert severity help should explain FAIL, BLOCKED, WARN, REVIEW REQUIRED, READY, and INFO using concise operator language.

## Operator Quick-Help

Operator quick-help should answer the most common question for each panel: what this means, what changed, and what to do next safely.

## Low-Clutter Behavior

Tooltips should stay brief and avoid covering critical status. Longer explanations should open in a panel help view rather than cluttering the cockpit.

## Future Stage 44

Future Stage 44 may define tooltip fixture content. No dashboard output is approved here.
