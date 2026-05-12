# Paper Bot Decision Flow

1. Paper Trade Signal
   - Read a Paper Trade Signal from local paper-trade sample data only.
2. Paper Simulation Timing
   - Record Paper Simulation timing and mark unknown timing clearly.
3. Paper Regime Review
   - Add a simple market condition label such as trend, range, volatile, or unknown.
4. Paper Risk Gate
   - Block by default unless paper trade review conditions pass.
5. Paper Decision
   - Create a paper-only decision with no real order route.
6. Paper Trade Result
   - Record a simulated result only.
7. Paper Scorecard
   - Update paper review metrics and confidence.
8. Next Safe Action
   - Tell the user what to review next.

## Default Rule

If any required paper trade review field is missing or unsafe, the result is BLOCKED.
