# AI_OS Sidebar Panel Grouping Rules Draft

## Purpose

This draft defines recommended sidebar panel groups for future AI_OS dashboard planning. It is documentation only and does not edit dashboard code.

## Recommended Panel Groups

### Trading Lab

Read-only review views for signal logs, paper-review artifacts, expectancy notes, and trading laboratory status. No broker execution controls.

### Telemetry

Read-only future views for user telemetry, app telemetry, and business telemetry planning. No telemetry persistence or collectors are approved.

### Reports

Read-only report navigation for daily reports, checkpoints, audits, and evidence summaries. No report writer activation.

### Roadmap

Planning views for stage position, next safe action, and batch approval status.

### Broker/OANDA

Disabled future-only group for Stage 8 broker/OANDA boundary status. Must remain labeled BLOCKED or REVIEW_ONLY until separately approved.

### Admin/Safety

Safety, protected-file status, approval gates, invalid data handling, and blocked action summaries.

## Mobile Drawer Rules

Mobile drawer grouping should keep Admin/Safety, Roadmap, and critical status entries above lower-priority panels. Broker/OANDA must remain disabled and future-only.

## Priority Order

1. Admin/Safety
2. Roadmap
3. Reports
4. Telemetry
5. Trading Lab
6. Broker/OANDA disabled future-only group

## Blocked Controls

Sidebar groups must not include script execution, API calls, telemetry writers, broker orders, credential access, file edits, localStorage/sessionStorage behavior, or hidden automation.

## Safe Default State

Default state should be read-only, validator-first, and show UNKNOWN when evidence is unavailable.

## Read-Only Display Boundary

All sidebar groups are display/navigation concepts only until a separate approved UI implementation batch exists.
