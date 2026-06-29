# Forex Overnight Repo-Safe Campaign Planner V1

The overnight repo-safe campaign planner defines a finite queue of Forex work units that can be built without broker contact or runtime activation. It is a planner and evidence generator, not an autonomous executor.

The planner is finite and bounded because it returns a fixed list of repo-safe work units. It does not loop, schedule, launch workers, start daemons, open webhooks, or poll external systems.

It is safe to run unattended only inside repo-safe boundaries: local state construction, reports, next-packet drafting, documentation, and validators. It must stop before broker connection proof, credentials, `.env`, account identifiers, account inspection, orders, demo/live action, scheduler, daemon, webhook, worker, watcher, listener, or background loop.

The planner supports larger work packets by making the queue explicit before implementation starts. That reduces branch churn, repeated prompt repair, accidental scope drift, and unclear stop points.

Failure reduction comes from fixed branch expectations, exact allowed paths, exact forbidden paths, deterministic JSON output, focused tests, governance validation, and one-commit stop discipline.
