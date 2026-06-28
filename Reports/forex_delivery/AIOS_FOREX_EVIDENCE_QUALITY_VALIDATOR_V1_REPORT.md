# Forex Evidence Quality Validator V1
Status: SAFETY_REJECT
- Paths: 5

## C:\Dev\Ai.Os\tests\fixtures\forex_delivery\remaining_closure_v1\evidence_bundle_clean.md
- status: OWNER_EVIDENCE_REQUIRED
- sample_size: 120
- missing_sections: []
- repair_instructions:
  - Attach owner review proof.
## C:\Dev\Ai.Os\tests\fixtures\forex_delivery\remaining_closure_v1\evidence_bundle_missing_sections.md
- status: EVIDENCE_REPAIRABLE
- sample_size: 120
- missing_sections: ['risk control', 'expectancy', 'drawdown', 'owner approval']
- repair_instructions:
  - Add all required sections.
## C:\Dev\Ai.Os\tests\fixtures\forex_delivery\remaining_closure_v1\evidence_bundle_broker_command_rejected.md
- status: SAFETY_REJECT
- sample_size: 120
- missing_sections: ['expectancy', 'drawdown', 'owner approval']
- sensitive_hits:
  - (?im)\b(place|send|submit)\s+(an?\s+)?order\b: place order
- repair_instructions:
  - Remove sensitive lines and command text.
## C:\Dev\Ai.Os\tests\fixtures\forex_delivery\remaining_closure_v1\evidence_bundle_insufficient_sample.md
- status: INSUFFICIENT_SAMPLE
- sample_size: 12
- missing_sections: []
- repair_instructions:
  - Collect additional sample rows for review.
## C:\Dev\Ai.Os\tests\fixtures\forex_delivery\remaining_closure_v1\evidence_bundle_sensitive_marker_rejected.md
- status: EVIDENCE_REPAIRABLE
- sample_size: 120
- missing_sections: ['risk control', 'expectancy', 'drawdown', 'owner approval']
- repair_instructions:
  - Add all required sections.