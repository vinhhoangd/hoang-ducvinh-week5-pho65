# Innovation Requirements Evidence — Step 7

> **Instructions:** For each requirement, state the exact number or slot your build produced (not an estimate), and name the file/function/URL where it's visible.

## 1. Consent-First Regulars Detection

- Number of records excluded as non-opted-in: *(your build's exact number, computed by your own code — count only the non-opted-in records that would have satisfied your frequency rule anyway, not every opted_in=false row in the file; show your work in the workbook)*
- Where this is visible: *e.g., "the '/crm' page's Regulars card, and `crm_copilot.compute_regular_status()`'s excluded_non_opted_in return value"*
- Verification: how did you confirm no `opted_in=false` record is ever flagged as a regular? *(e.g., "manually inspected the seed CSV's opted_in=false rows and confirmed none appear in the is_regular=True list")*

## 2. Demand-Shaping Catering Suggestion

- Over-capacity request: *(day, time, count from your own run — e.g. fictional illustration only, not your real answer, "Wednesday 20:00, 5 bookings")*
- Suggested alternate slot: *(day, time, count from your own run — e.g. fictional illustration only, "Wednesday 10:00, 0 bookings")*
- Why this slot was chosen: *(e.g., "lowest booking count among same-day buckets, computed by `suggest_alternate_slot()`")*

## 3. Weekly Narrative Brief

Paste the exact paragraph your co-pilot generated at `/crm`:

*(paste here)*

Is it a plain-language paragraph (not a chart/table)? *(confirm yes/no and explain if you had to change anything to meet this requirement)*
