# Paper Bot Decision Flow

1. Signal Intake
   - Read a mock signal only.
2. Latency Check
   - Record mock timing and mark unknown timing clearly.
3. Regime Tag
   - Add a simple market condition label such as trend, range, volatile, or unknown.
4. Risk Gate
   - Block by default unless mock conditions pass.
5. Paper Decision
   - Create a paper-only decision with no real order route.
6. Paper Trade Result
   - Record a simulated result only.
7. Scorecard
   - Update review metrics and confidence.
8. Next Safe Action
   - Tell the user what to review next.

## Default Rule

If any required mock field is missing or unsafe, the result is BLOCKED.

