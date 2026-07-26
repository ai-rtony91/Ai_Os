Set-StrictMode -Version Latest

function Get-AiOsCodexPacketContract {
    [CmdletBinding()]
    param()

    [ordered]@{
        schema = "AIOS_CODEX_PACKET_CONTRACT.v1"
        required_fields = @(
            "AI_OS BOOTSTRAP REQUIRED",
            "IDENTITY MARKER",
            "SUPERVISOR IDENTITY",
            "WORKER IDENTITY",
            "ZONE",
            "LANE",
            "APPROVAL AUTHORITY",
            "BRANCH PLAN",
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
    }
}
