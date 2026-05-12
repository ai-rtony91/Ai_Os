# UI Problem Patterns

UI means what the user sees and clicks.

Dock player problem patterns:

- UI confusion: the player looks clickable but does not clearly show what will happen.
- Playback state mismatch: the button shows pause when playback is stopped, or play when playback is active.
- Mobile readability issue: labels or buttons are too small, crowded, or hidden on phone size.
- Panel spacing issue: the dock player overlaps another panel or leaves too little space.
- Incorrect icon state: icon does not match current state.
- Layout clutter: too many controls compete for attention.
- Wrong placement: the player appears in a place that interrupts the main workflow.
- Mixed unrelated UI changes: the dock player fix also changes unrelated panels or Trading Lab files.

Preferred repair route:

- Labels, spacing, clutter, and mobile readability go to the UI readability role.
- State mismatch and icon state go to the UI Agent.
- Missing checks go to the Validator Gap Agent.
- Mixed unrelated edits go to Cleanup Agent or Architecture Agent before APPLY.
