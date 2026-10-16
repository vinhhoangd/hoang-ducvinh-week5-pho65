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
| Predicted over-capacity day/slot | **Saturday 2026-02-14, 18:00–20:00.** Written 2026-10-15 14:42, before any CRM code existed. Only 4 of the 29 seed rows are catering (R016–R019), all on Feb 14. Three start between 18:00 and 20:00 (18:00, 18:45, 19:30), and the fourth is 14:30. With 2-hour windows anchored at midnight, 18:45 and 19:30 belong to the 18:00 window, even though they are not "on the hour". |
| Predicted booking count in that slot | **3** (R016 Duc Le, R017 Kim Vo, R018 Trang Bui). That is more than the limit of 2, so the slot is flagged. The only other bucket is Feb 14 14:00–16:00 with 1 booking (R019). |

## Full Known-Answer Table

| Stage | Regular-status result | Follow-up queue result | Capacity result |
|---|---|---|---|
| **Observed (before fix)** — first run of `/crm`, 2026-10-15 14:46 | 1 regular: Mai Tran (8 visit days). Anh Nguyen is listed **twice**: phone ending 0003 with 2 visits (last 2026-01-15) and phone ending 0009 with 1 visit (2026-01-10). Neither is a regular. | **Empty.** The page says "Nobody is in the follow-up queue." | Sat 2026-02-14 18:00–20:00: **3 bookings, over capacity** (R016 18:00, R017 18:45, R018 19:30). 14:00–16:00: 1 booking (R019), ok. **Matches the prediction.** |
| **Diagnosis** | **Data issue.** First I checked the logic on clean input. Mai Tran (8 visits) and Linh Pham (4 opted-out visits) both scored correctly, so the grouping and the 3-in-14-days rule work. Next I checked the output for a hidden answer. Anh is not marked regular anywhere in the computed result, so this is not an interface issue. Then I read Anh's raw rows. R013 (Jan 5) and R015 (Jan 15) use 555-203-0003, but R014 (Jan 10) uses 555-203-0009: the same name and the same first seven digits, with only the last digit changed. Grouping by phone splits one person into two groups (2 visits + 1 visit), and neither group reaches 3. Combined, the visits are Jan 5, 10 and 15: 3 visits in 11 days, so Anh is a regular. The last visit, Jan 15, is 31 days before Feb 15, which is 21+ days, so she belongs in the follow-up queue. | (same cause) | Not affected: catering rows R016–R019 have consistent keys. |
| **Fix applied** | Smallest correction, on the data side and with no logic rewrite. A one-line phone crosswalk in `docker/shared-config/phone-crosswalk.csv` (`555-203-0009 → 555-203-0003`) re-keys R014 before grouping. The raw seed file stays untouched and read-only. The crosswalk is applied only when the name on the wrong number matches a name already on the right number, so a bad line can't merge two different people (for example Rosa Kim, whose number also ends in 0009). | (same fix) | None needed. |
| **Observed (after fix)** — re-run of `/crm`, 2026-10-15 14:48 | **2 regulars:** Anh Nguyen (one row, phone ending 0003, **3 visits**, last 2026-01-15, regular) and Mai Tran (8 visits, last 2026-02-12). The "Phone fixes applied" card shows `R014 Anh Nguyen: 555-203-0009 counted as 555-203-0003`. The "Check these names" warning is gone. | **Anh Nguyen, 31 days since the last visit**, with one draft that starts `DRAFT -- NOT SENT`. Mai Tran is not in the queue (3 days since the last visit, under 21). | Unchanged: Sat 2026-02-14 18:00–20:00, 3 bookings, over capacity. Suggested alternate: 14:00–16:00 the same day (1 booking). |

## Confirm

Does the after-fix result match what you would now expect, given the corrected data? Explain any remaining gap.

Yes. After the fix, Anh Nguyen's three visits (Jan 5, 10 and 15) are grouped under one number. That is 3 visits in an 11-day span, so Anh is a regular, and Jan 15 is 31 days before Feb 15, which puts Anh in the follow-up queue. Nothing else moved. Mai Tran is still the only other regular. The no-consent count is still 4 records (R009–R012, Linh Pham), and the capacity result still matches the prediction exactly.

No gap remains on this seed file. The general limit stays: the fix corrects only the typo we found. A different mistyped number would split another customer the same way. To make the next one easy to spot, the page shows a **"Check these names"** warning whenever one name appears under two phone numbers. It never merges them by itself, because two people can share a name.

**How to see before and after yourself:** open `http://localhost:5050/crm?corrections=off` (the raw data: 0 follow-ups) and `http://localhost:5050/crm` (fixed: Anh Nguyen in the queue). The automated version is `docker compose exec app python test_crm_copilot.py`, which asserts both states.
