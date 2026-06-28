{
  "event_count": 5,
  "events": [
    {
      "blockers": [],
      "metadata": {
        "lane": "forex_owner_evidence_return_orchestration_v1"
      },
      "notes": [
        "lane orchestration started"
      ],
      "route": null,
      "stage": "initialized",
      "status": "STARTED",
      "timestamp": "2026-06-28T00:34:18.683893+00:00"
    },
    {
      "blockers": [],
      "metadata": {
        "missing": 13,
        "requested": 17
      },
      "notes": [
        "intake completed"
      ],
      "route": null,
      "stage": "intake",
      "status": "INTAKE_PARTIAL",
      "timestamp": "2026-06-28T00:34:18.683893+00:00"
    },
    {
      "blockers": [
        "sample_count below minimum 30",
        "sample_count below minimum 30",
        "sample_count below minimum 30",
        "sample_count below minimum 30",
        "strict mode requires explicit owner confirmation",
        "sample_count below minimum 30"
      ],
      "metadata": {
        "path_count": 10
      },
      "notes": [
        "fixture_path_count=10"
      ],
      "route": null,
      "stage": "validator",
      "status": "OWNER_RETURN_REPAIRABLE",
      "timestamp": "2026-06-28T00:34:18.683893+00:00"
    },
    {
      "blockers": [
        "owner evidence missing for owner approval evidence"
      ],
      "metadata": {
        "owner_gaps": 1
      },
      "notes": [
        "route decision completed"
      ],
      "route": "ROUTE_OWNER_EVIDENCE_REQUIRED",
      "stage": "router",
      "status": "ROUTE_OWNER_EVIDENCE_REQUIRED",
      "timestamp": "2026-06-28T00:34:18.683893+00:00"
    },
    {
      "blockers": [],
      "metadata": {
        "local_action_count": 13,
        "owner_action_count": 1
      },
      "notes": [
        "packet composed"
      ],
      "route": null,
      "stage": "packet_composer",
      "status": "FINAL_OWNER_REVIEW_PACKET_PENDING_OWNER_RETURN",
      "timestamp": "2026-06-28T00:34:18.683893+00:00"
    }
  ],
  "generated_at": "2026-06-28T00:34:18.683893+00:00",
  "packet_id": "AIOS-FOREX-OWNER-EVIDENCE-RETURN-ORCHESTRATION-V1",
  "report_type": "checkpoint"
}