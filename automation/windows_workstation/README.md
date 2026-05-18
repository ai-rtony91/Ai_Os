# AI_OS Windows Workstation Setup

Status: baseline scaffold.

Purpose:
Standardize the local Windows operator workstation so AI_OS worker windows open predictably every morning.

## Recommended Tooling

- Windows Terminal
- PowerToys FancyZones
- PowerShell
- GitHub CLI

## Morning Layout Goal

Expected operator lanes:

1. AI_OS MAIN CONTROL
2. CODEX BUILD LANE
3. VALIDATOR WORKER
4. APPROVAL INBOX

## PowerToys / FancyZones Role

FancyZones should own screen snapping and zone layout.

AI_OS scripts should own:
- launching worker windows
- naming windows
- setting working directory
- applying worker identity markers

AI_OS should not depend on cloud automation for basic local layout.

## Rule

PowerToys handles placement.
AI_OS handles process launch and identity.
