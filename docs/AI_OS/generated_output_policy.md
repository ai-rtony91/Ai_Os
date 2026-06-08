# AI_OS Generated Output Policy

Status: subordinate policy.

Tracked source authority includes code, schemas, stable fixtures, explicit workflow docs, and operator-approved milestone evidence.

Routine DRY_RUN current projections are generated output. They should write to ignored generated-output roots such as `Reports/generated/` or `Reports/runtime/` and must not overwrite tracked current report files during health checks.

Telemetry current files are runtime/generated telemetry. They should write to ignored telemetry roots such as `telemetry/generated/` or `telemetry/runtime/`, unless a separate operator-approved lane promotes a stable fixture or milestone evidence file.

Dated milestone evidence may remain tracked only when an explicit evidence lane approves that snapshot. Routine commands must not refresh those tracked milestone files.

Validators must not dirty tracked files during routine checks. Validator output can be printed to stdout, written to ignored generated-output roots, or captured as explicitly approved milestone evidence.
