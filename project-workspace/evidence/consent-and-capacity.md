# Innovation Requirements Evidence — Step 7

> **Instructions:** For each requirement, state the exact number or slot your build produced (not an estimate), and name the file/function/URL where it's visible.

## 1. Consent-First Regulars Detection

- Number of records excluded as non-opted-in: **4 records (R009, R010, R011, R012), all from 1 customer (Linh Pham, phone ending 0002).** The work: Linh's visits on Feb 3, 6, 10 and 13 contain 3 visits within 14 days (Feb 3–13), so they would meet the regular rule, but every one of Linh's rows has `opted_in=false`. The other opted-out customers would not have qualified anyway, so they are not counted here. Ben Tran (R026–R028) has 3 visits, but they are spread over Jan 1, Jan 20 and Feb 10. Tom Ng (R023) and Trang Bui (R018) have 1 visit each. In total, 9 rows are opted out and 1 row has no phone (R029 "Guest"). All 10 are shown as **not eligible**, never as "not a regular".
- Where this is visible: on the `/crm` page, the **"Left out (no consent)" tile (4)** and the **"Not eligible (never scored)" card**, which lists R009–R012. In code: `crm_copilot.compute_regular_status()` returns `excluded_non_opted_in`, and `run()` returns `excluded_non_opted_in_count`. The narrative brief ends with "1 customer who visited often but did not agree to be contacted was left out on purpose."
- Verification: Linh Pham's number is absent from the regulars table and from `regular_status`. `test_crm_copilot.py` asserts that each excluded record's phone is not in `regular_status`. It also checks two harder cases: a customer who opted in and then said no on the latest visit drops out completely, and consent counts only when the CSV says exactly `true` (`yes` does not count).

## 2. Demand-Shaping Catering Suggestion

- Over-capacity request: **Saturday 2026-02-14, 18:00–20:00, 3 bookings** (R016 at 18:00, R017 at 18:45, R018 at 19:30), over the limit of 2.
- Suggested alternate slot: **Saturday 2026-02-14, 14:00–16:00, 1 booking** (R019 at 14:30). It has room for 1 more, which is exactly the 1 extra booking.
- Why this slot was chosen: `crm_copilot.suggest_alternate_slot()` picks the same-day window with the **lowest booking count that still has room**, with ties going to the window closest in time. It only offers windows that already took a catering booking that day, because the seed data has no opening hours, so an empty 02:00 window would not be a real option. If no window has room, the page says so and suggests calling customers instead of naming a bad slot. On the page, the amber "Suggestion for Sat Feb 14…" box sits under the capacity table, and the brief carries the same advice.

## 3. Weekly Narrative Brief

Paste the exact paragraph your co-pilot generated at `/crm` (as of 2026-02-15, phone fix on):

> Week ending Sunday, February 15, 2026: 2 customers count as regulars (Anh Nguyen and Mai Tran). 1 regular may be drifting away: Anh Nguyen (last visit Jan 15, 31 days ago). A draft follow-up is ready for you to read; nothing has been sent. Catering on Saturday Feb 14, 6 PM–8 PM has 3 bookings, more than the kitchen limit of 2; 2 PM–4 PM the same day has only 1 booking, so offer that time to 1 booking from the busy window. Slow catering windows with room to spare: Saturday Feb 14, 2 PM–4 PM (1 booking). 1 customer who visited often but did not agree to be contacted was left out on purpose.

Is it a plain-language paragraph (not a chart/table)? **Yes.** It is the first card on `/crm`, above every table, and it uses 12-hour times ("6 PM–8 PM") rather than database values. One change was needed to meet the "weekly" requirement. Early versions still warned about Feb 14 when viewed as of March 31. The brief now covers catering from the week ending on the as-of date plus anything upcoming, and older bookings are counted in a note instead.
