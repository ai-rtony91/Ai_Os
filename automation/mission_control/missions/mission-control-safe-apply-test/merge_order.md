# Merge Order - Mission Control Safe Apply Test

| Order | Lane | Reason |
|---:|---|---|
| 1 | foundation | Merge config, schemas, or scaffolding PRs first because later implementation depends on stable structure. |
| 2 | implementation | Merge scoped implementation PRs after foundation validation passes. |
| 3 | validation | Merge validator or proof updates after implementation behavior is known. |
| 4 | dashboard | Merge dashboard/status updates last so they reflect the final accepted proof. |

## Merge Rules

- Do not merge PRs without validation proof.
- Merge foundation before implementation.
- Merge implementation before validation/dashboard proof.
- Stop if a PR touches secrets, broker actions, trading actions, startup tasks, scheduled tasks, protected root governance files without approval, or unrelated paths.

Next safe action: replace PR placeholders in the dashboard with real PR links and current check status before merge review.
