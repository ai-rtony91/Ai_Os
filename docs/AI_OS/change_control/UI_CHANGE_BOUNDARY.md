# UI Change Boundary

UI means user interface: labels, buttons, layout, spacing, themes, readability, panels, gallery, radio dock player, and visual behavior.

Allowed in planning:

- Describe UI goals.
- Propose labels and beginner wording.
- Plan gallery or radio dock behavior.
- Plan dashboard panels.
- Review color contrast and mobile readability.
- Identify clutter.

Blocked unless exact files are approved:

- Editing `apps/dashboard/`.
- Editing dashboard HTML, CSS, JavaScript, React, assets, or mock data.
- Adding live controls.
- Adding hidden automation.
- Adding API calls.
- Adding broker controls.
- Adding secret or credential handling.

UI changes must not be mixed with Trading Lab logic, connector activation, API activation, or product documentation commits unless the user explicitly approves a combined package.
