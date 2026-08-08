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
        operator_delivery = [ordered]@{
            target_operator_pastes = 1
            emit_one_complete_prompt_once = $true
            do_not_repeat_full_prompt_after_delivery = $true
            recovery_uses_smallest_safe_delta = $true
            regenerate_full_prompt_only_when_required_for_safe_execution = $true
            do_not_emit_prompt_and_duplicate_download_copy_unless_requested = $true
            resolve_mutable_repo_state_during_preflight_when_unknown = $true
            inspect_canonical_ownership_before_proposing_new_authority = $true
        }
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
