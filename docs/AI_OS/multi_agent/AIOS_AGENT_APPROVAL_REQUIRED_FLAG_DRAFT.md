# AIOS Agent Approval Required Flag Draft

Stage: 9.2
Status: Draft planning doc

The approval_required flag should be YES when a workload changes files, touches protected areas, affects credentials, affects Git publishing, or touches trading/broker paths.

Boundary: YES means stop before APPLY unless approval is present.
