# Known-Answer Test — Seeded Failure (Steps 4-6)

> **Instructions:**
> 1. Fill "Prediction" before you ever run the co-pilot (Step 4).
> 2. Fill "Observed (before fix)" from your first real run.
> 3. Diagnose the type (data / logic / interface) with your reasoning — do not just guess and check.
> 4. Apply the smallest correction, then fill "Observed (after fix)."
> 5. This table is your verification evidence. "It ran with no errors" is not acceptable on its own.

> **Note:** the "e.g." examples below use a fictional Tuesday-lunch scenario that does not match your actual seed file, on purpose — copying these values instead of your own real output will not pass grading, and will not match what your team actually observes.

## Capacity Prediction (made BEFORE first run)

| Field | Your answer |
|---|---|
| Predicted over-capacity day/slot | *e.g. (fictional, not your real answer), "Tuesday lunch — the seed file looked catering-heavy around midday"* |
| Predicted booking count in that slot | *e.g., "3 or more"* |

## Full Known-Answer Table

| Stage | Regular-status result | Follow-up queue result | Capacity result |
|---|---|---|---|
| **Observed (before fix)** | *e.g. (fictional), "only one customer flagged regular"* | *e.g., "empty — nobody appeared, which seemed suspicious"* | *e.g., "one Tuesday slot flagged, count over your threshold"* |
| **Diagnosis** | *State: data / logic / interface, and your specific reasoning — e.g. (fictional), "data issue: found two records for the same customer name under two slightly different phone numbers; neither alone reaches your visit threshold"* | | |
| **Fix applied** | *e.g., "added a phone-number crosswalk mapping the typo'd number to the correct one before grouping by phone"* | | |
| **Observed (after fix)** | *e.g., "that customer now shows the correct combined visit_count and is_regular=True"* | *e.g., "that customer now appears in the follow-up queue with a real days_since_visit value"* | *(unchanged — the fix does not touch catering data)* |

## Confirm

Does the after-fix result match what you would now expect, given the corrected data? Explain any remaining gap.

*(your answer here)*
