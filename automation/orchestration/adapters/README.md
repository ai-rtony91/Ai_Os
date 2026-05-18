# AI_OS Packet Adapter DRY_RUN Scaffold

This folder contains a read-only packet adapter scaffold.

Purpose:

- Detect older AI_OS packet formats.
- Simulate normalization into the canonical work packet shape.
- Report field mapping, warnings, and lossy conversions before any APPLY workflow.

Safety rules:

- DRY_RUN only.
- No dispatcher edits.
- No runtime integration.
- No commits.
- No pushes.
- No broker, live trading, webhook, OANDA, API key, or secret work.
- Do not touch `schemas/aios/orchestration/`.

Files:

- `Normalize-AiOsPacket.DRY_RUN.ps1` reads a packet JSON file and prints a simulated canonical packet.
- `LEGACY_PACKET_MAPPING.example.json` documents known dialects and field mappings.
- `PACKET_ADAPTER_REPORT.example.json` shows validator-friendly output.

Example commands:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\adapters\Normalize-AiOsPacket.DRY_RUN.ps1 -PacketPath work_packets\examples\worker_registry_consolidation.json
```

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\adapters\Normalize-AiOsPacket.DRY_RUN.ps1 -PacketPath automation\orchestration\work_packets\templates\AIOS_WORK_PACKET.template.json -OutputJson
```

Next safe action: run the adapter against one known legacy packet and review warnings before proposing any real canonical schema integration.
