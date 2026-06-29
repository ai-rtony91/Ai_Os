# AIOS Forex Dashboard End User Final UX V1

Forex is not finished for next-project purposes until the Forex 110 gate is merged.

100% means repo-safe Forex completion: required readiness, evidence, candidate, demo-readiness, queue, and broker-boundary artifacts exist in the repo.

The final 10% is dashboard end-user organization and UX clarity. The dashboard must present the operator with critical status, blocker, next safe action, and safety state first.

Bitwarden and Vaultwarden remain locked until after Forex 110 is merged. No secrets migration starts here. No token storage starts here. Broker-facing activity remains protected and separate.

Default display rules:
- Show critical status by default.
- Show active blocker by default.
- Show next safe action by default.
- Show safety state by default.
- Do not show secret values.
- Do not show broker account identifiers.
- Do not show order execution data.
- Do not show demo or live authorization controls.

Hidden detail rules:
- Hide raw broker data behind report/detail windows.
- Hide raw trade data behind report/detail windows.
- Hide raw metadata behind report/detail windows.
- Hide long validator logs behind report/detail windows.
- Hide internal state dumps behind report/detail windows.

Overwhelm prevention rules:
- Use emoji/picture-style clickable button and window labels.
- Keep the first view to critical information only.
- No dashboard chaos.
- No micro-data overload.
- No broker-heavy raw data in the default view.
