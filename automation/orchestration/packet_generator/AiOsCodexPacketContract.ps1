Set-StrictMode -Version Latest

function Get-AiOsCodexPacketContract {
    [CmdletBinding()]
    param()

    [ordered]@{
        schema = "AIOS_CODEX_PACKET_CONTRACT.v2"
        exact_first_line = "CODEX-ONLY PROMPT"
        required_markers = @("AI_OS EXECUTION TOKEN", "AI_OS BOOTSTRAP REQUIRED")
        required_scalar_fields = @(
            "MISSION ID", "MISSION NAME", "PROGRAM ID", "PROGRAM NAME",
            "EPIC ID", "EPIC NAME", "BUCKET ID", "BUCKET NAME",
            "PACKET ID", "PACKET NAME", "IDENTITY MARKER",
            "SUPERVISOR IDENTITY", "WORKER IDENTITY", "LOCK IDENTITY",
            "MODE", "ZONE", "LANE", "WORKTREE", "BRANCH",
            "APPROVAL AUTHORITY", "STOP POINT"
        )
        list_valued_fields = @(
            "ALLOWED PATHS", "FORBIDDEN PATHS", "PREFLIGHT",
            "VALIDATOR CHAIN", "FINAL REPORT FORMAT"
        )
        protected_action_fields = @(
            "STAGING AUTHORITY", "COMMIT AUTHORITY", "PUSH AUTHORITY",
            "PULL REQUEST AUTHORITY", "MERGE AUTHORITY"
        )
        protected_authority_pattern = "^(AUTHORIZED|NOT AUTHORIZED|PREPARE ONLY)(?:\b|\.)"
        required_repository_state_commands = @(
            "pwd", "git status --short --branch", "git branch --show-current",
            "git remote -v", "git rev-parse HEAD", "git diff --name-only"
        )
        unresolved_placeholder_patterns = @(
            "(?i)\bTODO\b", "(?i)\bTBD\b", "(?i)@filename\b",
            "(?i)path/to/file", "(?i)\[REAL-FILENAME\]", "\{[^{}]+\}",
            "(?i)<(?:placeholder|insert|replace)[^>]*>", "(?i)\bplaceholder(?:s|_token)?\b"
        )
        terminology = [ordered]@{
            preferred = [ordered]@{
                work_item = "engineering work packet"
                change_action = "apply"
                validation_result = "validation evidence"
            }
            drift_terms = @("workload pack", "task pack")
        }
    }
}
