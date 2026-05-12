# Change Scope Rules

Each change must stay inside one clear package.

Do not mix unrelated work.

Good packages:

- One UI readability patch.
- One dashboard panel mock-data update.
- One Trading Lab mock-data update.
- One validator script.
- One product documentation package.
- One connector planning document.

Bad packages:

- Dashboard styling plus Trading Lab strategy files.
- Product brochure plus executable app code.
- Connector planning plus secrets handling.
- Mock data plus live broker code.
- UI changes plus `gitignore` changes unless explicitly approved.

Every change request must name:

- user goal
- exact allowed files
- exact blocked files
- owner or agent
- DRY_RUN requirement
- APPLY approval requirement
- validation requirement
- commit package
- rollback note

If scope is unclear, stop and ask for a DRY_RUN clarification.
