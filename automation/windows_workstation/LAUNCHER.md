# AI_OS Morning Workspace Launcher

## Purpose

Launch the standard AI_OS operator workstation lanes for morning startup.

## Lanes

- AI_OS MAIN CONTROL
- CODEX BUILD LANE
- VALIDATOR WORKER
- APPROVAL INBOX

## Safety

This launcher only opens PowerShell windows and sets identity markers.

It must not:
- commit
- push
- deploy
- execute broker actions
- create scheduled tasks
- modify dashboards

## Usage

From repo root:

.\automation\windows_workstation\Launch-AiOsMorningWorkspace.ps1

## FancyZones

PowerToys FancyZones should handle placement after windows open.
