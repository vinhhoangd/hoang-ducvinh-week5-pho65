# Regression Check — Week 3/4 Features After the Week 5 Extension

Use this to prove your Week 5 `/crm` addition did NOT break the Week 3 order tracker or the Week 4 inventory ledger.

> **Instructions:**
> 1. Complete the "Before" rows at Step 0, before writing any Week 5 code.
> 2. Complete the "After" rows at Step 8, once `/crm` is built.
> 3. If any "After" row does not match its "Before" row, fix the regression before continuing — do not submit a failing row.

## Regression Matrix

| # | Check | Command / URL | Before (Step 0) | After (Step 8) | Pass/Fail |
|---|---|---|---|---|:---:|
| 1 | Week 3 order tracker loads | `http://localhost:5050/` | *e.g., "Pho65 order tracker (Week 3 regression) heading, 6 fixture orders shown"* | | |
| 2 | Week 4 inventory page loads | `http://localhost:5050/inventory` | *e.g., "Pho65 mobile inventory heading, table empty"* | | |
| 3 | Week 4 known-answer cost test (fresh item) | receive 10@$2.00, receive 10@$2.50, use 12 on a newly created item | *(not applicable before Step 3 — this is a fresh-item test, run once as a baseline sanity check if you like, or skip to After)* | *e.g., "8 bag on hand · average $2.25 · value $18.00"* | |
| 4 | Automated inventory test suite | `docker compose exec app python test_inventory.py` | *e.g., "inventory known-answer and guard tests passed"* | | |

## If Something Failed

*(If any row above is Fail, describe what broke, how you found it, and the fix you applied. If nothing failed, write "No regressions found" and briefly explain what you checked to be confident of that — e.g., "confirmed by diffing app.py's Week 3/4 routes against the original before/after adding /crm.")*
