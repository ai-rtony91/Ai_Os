Set-StrictMode -Version Latest

function Get-AiOsCodexPacketContract {
    [CmdletBinding()]
    param()

    [ordered]@{
        schema = "AIOS_CODEX_PACKET_CONTRACT.v2"
        required_fields = @(
            "CODEX-ONLY PROMPT",
            "AI_OS EXECUTION TOKEN",
            "AI_OS BOOTSTRAP REQUIRED",
            "IDENTITY MARKER",
            "SUPERVISOR IDENTITY",
            "WORKER IDENTITY",
            "MISSION ID",
            "MISSION NAME",
            "PROGRAM ID",
            "PROGRAM NAME",
            "EPIC ID",
            "EPIC NAME",
            "BUCKET ID",
            "BUCKET NAME",
            "PACKET ID",
            "PACKET NAME",
            "MODE",
            "ZONE",
            "LANE",
            "WORKTREE",
            "BRANCH",
            "APPROVAL AUTHORITY",
            "PREFLIGHT",
            "BRANCH PLAN",
            "ALLOWED MUTATION FILES ONLY",
            "FORBIDDEN PATHS",
            "VALIDATOR CHAIN",
            "STOP POINT",
            "COMPLETION REPORT FORMAT"
        )
        terminology = [ordered]@{
            preferred = [ordered]@{
                work_item = "engineering work packet"
                change_action = "apply"
                validation_result = "validation evidence"
            }
            compatibility_bound = @(
                "PACKET ID",
                "MODE",
                "ZONE",
                "LANE",
                "MISSION",
                "BRANCH PLAN",
                "VALIDATOR CHAIN",
                "STOP POINT",
                "COMPLETION REPORT FORMAT"
            )
            drift_terms = @("workload pack", "task pack")
        }
        profiles = [ordered]@{
            state_aligned_routine_engineering_controller = [ordered]@{
                identity_marker = "AIOS-STATE-ALIGNED-ROUTINE-ENGINEERING-CONTROLLER-V2"
                mission_id = "MISSION-AIOS-001"
                mission_name = "AI_OS Product Engineering"
                program_id = "PRG-AIOS-AUTONOMY-001"
                program_name = "AI_OS Engineering Automation"
                epic_id = "EPC-ROUTINE-ENGINEERING-CONTROLLER-001"
                epic_name = "State-Aligned Low-Friction Engineering"
                bucket_id = "BKT-ROUTINE-ACTION-BUNDLE-001"
                bucket_name = "Session-Scoped Engineering Actions"
                packet_id = "PKT-STATE-ALIGNED-ROUTINE-CONTROLLER-APPLY-002"
                packet_name = "Implement State-Aligned Owner Command and Routine PR Controller"
                mode = "APPLY"
                zone = "EAST"
                lane = "GOVERNANCE_AUTOMATION"
                supervisor_identity = "ChatGPT Planning Supervisor under Anthony Human Owner"
                worker_identity = "EAST_OCC_01 - Codex Cloud Engineering Worker"
                approval_authority = "Anthony Human Owner explicitly approves this exact packet for scoped APPLY, exact-file staging, one commit, feature-branch publication, and one PR create or update. Merge remains blocked."
                allowed_mutation_files = @(
                    "automation/orchestration/packet_generator/AiOsCodexPacketContract.ps1",
                    "automation/orchestration/packet_generator/New-AiOsCodexPacket.DRY_RUN.ps1",
                    "automation/orchestration/packet_generator/Test-AiOsCodexPacket.DRY_RUN.ps1",
                    "tests/orchestration/test_codex_packet_generator.py"
                )
                forbidden_paths = @(
                    ".env and secret or credential paths",
                    "broker, OANDA, webhook, order, position, and money-movement paths",
                    "paper, demo, practice, and live trading execution",
                    "runtime state, scheduler, daemon, and worker activation",
                    "direct main push, merge, force push, reset, clean, and branch deletion",
                    "all files outside ALLOWED MUTATION FILES ONLY"
                )
                validators = @(
                    "git diff --check",
                    "python -m pytest tests/orchestration/test_codex_packet_generator.py -q -p no:cacheprovider"
                )
                stop_point = "Stop after one feature-branch PR is created or updated and available CI is inspected. Do not merge."
            }
        }
    }
}
