# AI_OS FancyZones Layout

Status: configured locally in PowerToys.

PowerToys owns the global window layout.

AI_OS owns:
- launching worker lanes
- assigning worker identity markers
- setting repo working directory
- safety banners

Expected zones:
- CREW OPERATOR
- BUILDER
- VALIDATOR
- APPROVALS
- ORCHESTRATOR
- GitHub / browser lane

Restore flow:
1. Start PowerToys.
2. Run .\automation\windows_workstation\Launch-AiOsMorningWorkspace.ps1
3. Windows should return to remembered FancyZones positions.
