# Regression Check — Week 3/4 Features After the Week 5 Extension

Use this to prove your Week 5 `/crm` addition did NOT break the Week 3 order tracker or the Week 4 inventory ledger.

> **Instructions:**
> 1. Complete the "Before" rows at Step 0, before writing any Week 5 code.
> 2. Complete the "After" rows at Step 8, once `/crm` is built.
> 3. If any "After" row does not match its "Before" row, fix the regression before continuing — do not submit a failing row.

## Regression Matrix

| # | Check | Command / URL | Before (Step 0) | After (Step 8) | Pass/Fail |
|---|---|---|---|---|:---:|
| 1 | Week 3 order tracker loads | `http://localhost:5050/` | 2026-10-15 14:42 — heading "Order tracker (Week 3 regression)" under the Phở 65 bar; 10 fixture orders; **3 overdue** (O-001, O-002, O-003), O-004–O-007 waiting, O-008–O-010 picked up; threshold 20 min; reference time 2026-01-15 12:30 | 2026-10-15 14:52 — same heading; same 10 orders; **3 overdue** (O-001, O-002, O-003), O-004–O-007 waiting, O-008–O-010 picked up; 20 min; 2026-01-15 12:30. Only visible change: the nav bar now has a **CRM** link (required by Step 3) | **Pass** |
| 2 | Week 4 inventory page loads | `http://localhost:5050/inventory` | 2026-10-15 14:42 — heading "Items", page says "No items yet." (fresh Week 5 ledger) | 2026-10-15 14:52 — heading "Items" loads (HTTP 200), now listing the one regression item created in row 3 | **Pass** |
| 3 | Week 4 known-answer cost test (fresh item) | receive 10@$2.00, receive 10@$2.50, use 12 on a newly created item | Not run before Step 3 (fresh-item test; done once, in the After column) | 2026-10-15 14:52 — new item "Week 5 regression noodles", `PHO65-INV-000501`, through the real web forms: received 10 @ $2.00, received 10 @ $2.50, used 12 → **On hand 8 · Average cost $2.25 · Stock value $18.00**, exactly 3 ledger rows | **Pass** |
| 4 | Automated inventory test suite | `docker compose exec app python test_inventory.py` | 2026-10-15 14:42 — `inventory known-answer and guard tests passed` | 2026-10-15 14:52 — `inventory known-answer and guard tests passed` (now also checks the double-tap message, see below) | **Pass** |

| 5 | New CRM test suite (added this week) | `docker compose exec app python test_crm_copilot.py` | n/a (did not exist) | 2026-10-15 — `crm co-pilot known-answer, edge-case, and draft-only tests passed` | **Pass** |

## If Something Failed

No Week 3 or Week 4 regression was caused by the Week 5 change. To be confident of that, we checked:

- Every Week 3/4 route still answers with the same content. `test_crm_copilot.py` also requests `/` and `/inventory` after importing the new code.
- `/crm` is read-only: it only reads `/data/pho65-week5-seed.csv` and `/config/phone-crosswalk.csv`, and it never opens the ledger.
- `CRM_AS_OF` is parsed when `/crm` is requested, not when the app starts, so a typo in that setting cannot stop `/` or `/inventory` from loading. A test covers this: a bad `CRM_AS_OF` gives `/crm` a clear 503 page, and the other pages are unaffected.

One **pre-existing** Week 4 bug was found *during* the row 3 test and fixed:

| What we saw | Cause | Fix | Re-test |
|---|---|---|---|
| Re-sending the same "used 12" (same request ID, like a double-tap) was correctly **refused**, but the message said "This would make stock negative" instead of "already recorded". No duplicate row was written. | `add_transaction()` checked stock before checking whether the request ID was already in the ledger. | The request-ID check now runs first. The database's UNIQUE constraint is still the last line of defence. | Repeated the same POST: the message now reads "That button press was already recorded; no duplicate transaction was added." The numbers stay at 8 / $2.25 / $18.00. `test_inventory.py` now asserts this. |
