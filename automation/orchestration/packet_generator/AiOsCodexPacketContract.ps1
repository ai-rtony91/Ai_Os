Set-StrictMode -Version Latest

function Get-AiOsCodexPacketContract {
    [CmdletBinding()]
    param()

    [ordered]@{
        schema = "AIOS_CODEX_PACKET_CONTRACT.v2"
        first_line = "CODEX-ONLY PROMPT"
        required_markers = @(
            "AI_OS EXECUTION TOKEN",
            "AI_OS BOOTSTRAP REQUIRED"
        )
        required_fields = @(
            "IDENTITY MARKER",
            "SUPERVISOR IDENTITY",
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
            "WORKER IDENTITY",
            "LOCK IDENTITY",
            "WORKTREE",
            "BRANCH",
            "APPROVAL AUTHORITY",
            "ALLOWED PATHS",
            "FORBIDDEN PATHS",
            "PREFLIGHT",
            "VALIDATOR CHAIN",
            "STOP POINT",
            "FINAL REPORT FORMAT",
            "STAGING AUTHORITY",
            "COMMIT AUTHORITY",
            "PUSH AUTHORITY",
            "PULL REQUEST AUTHORITY",
            "MERGE AUTHORITY"
        )
        list_fields = @("ALLOWED PATHS", "FORBIDDEN PATHS", "VALIDATOR CHAIN")
        protected_action_fields = @(
            "STAGING AUTHORITY",
            "COMMIT AUTHORITY",
            "PUSH AUTHORITY",
            "PULL REQUEST AUTHORITY",
            "MERGE AUTHORITY"
        )
        unresolved_value_patterns = @(
            '(?im)^\s*(?:TODO|TBD)\s*$',
            '(?i)@filename\b',
            '(?i)path/to/file\b',
            '\{[A-Za-z][A-Za-z0-9_-]*\}',
            '\[(?:REAL-FILENAME|INSERT[^\]]*|PLACEHOLDER)\]'
        )
        state_discovery_commands = @(
            "pwd",
            "git status --short --branch",
            "git branch --show-current",
            "git remote -v",
            "git rev-parse HEAD"
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
