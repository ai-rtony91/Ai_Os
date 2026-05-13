# AI_OS Worker Task Queue v1

Purpose:
Give governed workers clear task assignments after launch.

Worker Roles:
- AIOS-01-DEVOPS
- AIOS-02-TRADING_LAB
- AIOS-03-VALIDATOR
- AIOS-04-TELEMETRY

Rules:
- Queue is advisory only.
- Workers do not self-commit.
- Workers do not self-push.
- Workers do not deploy.
- Workers do not connect brokers.
- APPLY requires human approval.

Next:
Connect launcher output to this queue so each worker window displays its assigned task.
