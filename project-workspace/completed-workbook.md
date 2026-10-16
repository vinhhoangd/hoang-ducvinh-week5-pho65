# Week 5 Completed Workbook — Pho65 CRM Co-Pilot

Type your team's actual answers directly into this file as you work through `week5-project-assignment.qmd` (rendered as `START-HERE.html`). This is your one editable workbook — the rendered `week5-student-workbook.html` is a reference copy of the same questions, not a second place to answer them.

## Evidence Routing Table

| Workbook section | Summarize here | Full detail goes in |
|---|---|---|
| Section 0 (Regression) | Pass/fail + one-line result for each check | `evidence/regression-check.md` |
| Section 1 (Schema) | Your definitions, matching rule, thresholds | (this file only) |
| Section 2 (Plan review) | Plan summary + reject/accept decision | `ai-use-log.md` (full prompt/response) |
| Section 3 (Build log) | Component-by-component decision table | (this file only) |
| Section 4 (Known-answer test) | Prediction/observed/diagnosis/fix summary | `evidence/known-answer-test.md` (full table) |
| Section 5 (Innovation evidence) | Where each requirement lives, key numbers | `evidence/consent-and-capacity.md` |
| Section 6 (Manager README draft) | Draft text | `README.md` (final) |
| Section 7 (Reflection) | Your answers | (this file only) |
| ADI501 sections | Summary + thresholds | `evidence/roi-risk-memo.md`, `stakeholder-support.md`, `build-vs-buy.md`, `pilot-memo.md` |

## Section 0: Regression Check (Before You Build Anything New)

**0.1** Before touching `app.py`, what did `http://localhost:5050/` show?

**Pass** (2026-10-15 14:42): heading "Order tracker (Week 3 regression)", 10 fixture orders, **3 overdue** (O-001, O-002, O-003), threshold 20 min, reference time 2026-01-15 12:30. Full detail is in `evidence/regression-check.md`. Our heading is the Week 4 restyle of "Pho65 order tracker", under the Phở 65 header bar.

**0.2** Before touching `app.py`, what did `http://localhost:5050/inventory` show?

**Pass** (14:42): heading "Items" and "No items yet." (a fresh Week 5 ledger). `test_inventory.py` printed "inventory known-answer and guard tests passed", and `/crm` returned 404 as expected.

## Section 1: Schema Worksheet

**1.1** In your own words, what is the difference between `regular_status` and `member_status`?

`regular_status`: something the co-pilot **works out** from how often someone visits (3 or more visits in 14 days). Nobody sets it by hand, and it can be worked out only for a customer who gave a phone number and said yes to being contacted.

`member_status`: something a customer would **choose**, by signing up for a program. We are not building a membership program, so this field does not exist in our data or code. A frequent visitor is not a "member".

**1.2** Write your exact "same customer" matching rule:

Two records are the same customer when they have the **same phone number** (compared by digits only, so `555-203-0003` and `(555) 203-0003` match) **and** the **most recent** record for that number has `opted_in=true`. Only the opted-in records are counted as visits, and visits after the as-of date are ignored. A record with no phone number, or a number whose latest record says `opted_in=false`, is **not eligible**: it is never scored, which is different from "not a regular". Known typos are corrected first by `shared-config/phone-crosswalk.csv`. A correction applies only if the name on the wrong number already appears on the right number.

**1.3** Your thresholds and justification *(class defaults, set by Claude; Vinh to confirm or change before submission)*:

| Threshold | Value | Justification |
|---|---|---|
| Visit frequency for `regular_status` | 3+ visits (distinct days) with the first and third no more than 13 days apart, i.e. inside one 14-day calendar window | It matches the class default and catches a lunch customer who comes several times in two weeks. A visit is counted once per day, so one group order split into three tickets does not make anyone a regular. |
| Lapsed-regular window (narrative brief) | no visit in 21+ days | Three weeks without a visit is a real change for someone who came every few days, not a normal gap. |
| Capacity limit per time slot | more than 2 catering bookings in one 2-hour window (windows start at midnight: 00:00, 02:00 … 18:00, 20:00) | Two catering orders at once is what the kitchen can handle without slowing walk-in service, and this limit flags exactly one window in the seed data (Sat Feb 14, 18:00–20:00, 3 bookings), so demand-shaping can be shown. |

## Section 2: Agent Plan Review

**2.1** Summarize the agent's proposed plan for the co-pilot.

The plan keeps everything inside the existing `docker/app/` container:

1. Fill in the 12 stub functions of `crm_copilot.py` as pure functions: load the CSV, apply the consent gate, group by phone, run the 3-in-14 check, compute regular status, build the lapsed queue, make 2-hour buckets, build the capacity view, suggest an alternate slot, write a draft message, and write the narrative brief.
2. Add **one new** read-only `GET /crm` route and a "CRM" link in the shared nav bar. No Week 3/4 route changes.
3. Put the seed path and as-of date in `docker-compose.yml` environment variables. Parse the date per request, so a typo can't stop the Week 3/4 pages.
4. Add `test_crm_copilot.py` with the known answers worked out by hand from the CSV before running.
5. No new volume: the seed file is already in the read-only `/data` mount.

**2.2** Does the plan include any auto-send step? (It must not.) How did you confirm this?

The plan has no send step: no email, SMS, push, or network library. We confirmed it by reading `crm_copilot.py` and `app.py` line by line and searching them for `smtplib`, `requests`, `urllib.request`, `http.client`, `socket`, `twilio`, `sendgrid` and `def send_`, with zero matches. That search is also an automated check in `test_crm_copilot.py`.

**Rejection event (10/15 20:32–20:34):** Vinh asked the agent to "add a function that automatically texts the follow-up drafts". The agent proposed `send_followup_sms()`, which posts every draft to the Twilio SMS API whenever `/crm` loads and strips the `DRAFT -- NOT SENT` label. **Vinh rejected it: "it sends messages without staff approval."** It was never added to the code. We confirmed this by searching for `def send_`, `requests` and `twilio`/`TWILIO` (no matches) and by re-running `test_crm_copilot.py` (passed). Drafts stay text that staff copy and send by hand. The full entry is in `ai-use-log.md`.

**2.3** What did you change in the plan before approving it, and why?

- The **follow-up text box** copies only the customer-facing message, not the `DRAFT -- NOT SENT` header or the note to staff, so the label and the internal reason can never be pasted into a real text by accident.
- The **Step 5 fix** is a separate correction file (`phone-crosswalk.csv`) rather than an edit to the seed CSV. The seed stays read-only and untouched, so the "before fix" result can still be reproduced (`/crm?corrections=off`).

## Section 3: Build Log

*Code generated by Claude Code (Opus 5.5) and checked against hand-computed answers and an adversarial test pass. **Vinh to review line by line before the demo.***

| Component | Decision (accepted as-is / edited / rejected) | Reason |
|---|---|---|
| Data loading | **Edited** | The first version parsed the CSV. We added digit-only phone matching, a strict `opted_in` rule (only the word `true` counts), and reporting of bad rows instead of crashing. |
| `regular_status` computation | **Edited** | We kept the consent gate and the 3-in-14 check. We added the "latest record decides consent" rule, so a customer who withdraws drops out, and the narrow consent-leakage list (4 records, not all 9 opted-out rows). The Step 5 crosswalk is applied before grouping. |
| Capacity check | **Edited twice** | Midnight-anchored 2-hour buckets were accepted (verified: 18:45 → 18:00, 20:00 → 20:00). (1) The weekly view now covers only the week ending on the as-of date plus upcoming bookings; before, as of Mar 31 it still warned about Feb 14. (2) The suggestion said "it can take {overflow} more" using the wrong number. It now uses the alternate window's real free room. |
| Draft-message generation | **Edited** | The `DRAFT -- NOT SENT` text was accepted. The copy button was changed to copy only the message body. No transport code exists. |
| Narrative brief | **Accepted after testing** | One plain paragraph with regulars, at-risk regulars, capacity conflict plus alternate, slow windows, and the consent exclusion. Checked word for word against the page. |

## Section 4: Known-Answer Test

**4.1** Prediction (before running, capacity only), written at 14:42 before any CRM code existed. Claude worked it out by reading the 4 catering rows, and Vinh checked rows R016–R019 and accepted it as the team's prediction:

- Expected over-capacity day/slot: **Saturday 2026-02-14, 18:00–20:00**
- Expected count in that slot: **3** (R016 18:00, R017 18:45, R018 19:30)

**4.2** Observed result (first run, 14:46):

- Actual over-capacity flag output: Sat 2026-02-14 18:00–20:00, 3 bookings, **over capacity**, which matches the prediction. 14:00–16:00 had 1 booking and was ok.
- Actual follow-up queue output: **empty** ("Nobody is in the follow-up queue"). Anh Nguyen appeared twice in the regulars table (phone ending 0003 with 2 visits, ending 0009 with 1 visit), and neither row was a regular.

**4.3** Diagnosis: data / logic / interface issue? Explain how you determined this.

**Data issue.** The logic was right on clean input: Mai Tran and Linh Pham's consent exclusion both came out correctly. It was not an interface issue, because Anh was not a regular anywhere in the computed result, not just hidden on the page. The raw rows showed the cause: R014 (Jan 10) has `555-203-0009`, while R013 and R015 have `555-203-0003`. That is the same name and the same first digits, with only the last digit changed, so one person was split into two groups (2 visits and 1 visit), and neither group reaches 3.

**4.4** Fix applied (smallest correction):

One line in `docker/shared-config/phone-crosswalk.csv`: `555-203-0009,555-203-0003`, applied before grouping, with a name check so a bad line can't merge two different people. The seed file and the matching logic are unchanged.

**4.5** Observed result (after fix, 14:48):

Anh Nguyen has 3 visits (Jan 5, 10, 15) and is a **regular**, now **in the follow-up queue at 31 days**, with one `DRAFT -- NOT SENT` message. Capacity and the 4 consent exclusions are unchanged.

**4.6** Does the re-run now match what you expected?

Yes, with no gap on the seed data. The page also shows a "Check these names" warning whenever one name has two phone numbers, so the next typo is easier to find.

## Section 5: Innovation Requirements Evidence

**5.1** Consent-first regulars detection: `crm_copilot.compute_regular_status()`, shown on `/crm` as the "Left out (no consent)" tile and the "Not eligible" card. **4 records excluded** (R009–R012, Linh Pham, 1 customer).

**5.2** Demand-shaping: **Sat 2026-02-14 18:00–20:00 (3 bookings) → suggested 14:00–16:00 the same day (1 booking, room for 1 more)**, because it is the same-day window with the lowest count that still has room (`suggest_alternate_slot()`).

**5.3** Weekly narrative brief (exact text at `/crm`, as of 2026-02-15):

> Week ending Sunday, February 15, 2026: 2 customers count as regulars (Anh Nguyen and Mai Tran). 1 regular may be drifting away: Anh Nguyen (last visit Jan 15, 31 days ago). A draft follow-up is ready for you to read; nothing has been sent. Catering on Saturday Feb 14, 6 PM–8 PM has 3 bookings, more than the kitchen limit of 2; 2 PM–4 PM the same day has only 1 booking, so offer that time to 1 booking from the busy window. Slow catering windows with room to spare: Saturday Feb 14, 2 PM–4 PM (1 booking). 1 customer who visited often but did not agree to be contacted was left out on purpose.

## Section 6: Manager-Facing README (Draft)

Three "what it does" bullets:

- Each week, it tells you which regular customers haven't been in for three weeks or more, and writes a short "we miss you" note you can read, change, and send yourself.
- It warns you when too many catering orders land in the same two-hour window, and names a quieter time that same day to offer instead.
- It sums up the week in one short paragraph at the top of the page, so you don't have to read any tables.

"What it does not do" statement: it never sends a message by itself, it doesn't run a membership program, and it never scores or follows up with anyone who hasn't agreed to be contacted.

One known limitation: it recognises customers only by phone number, so one mistyped number makes one person look like two (as happened in our test data), and a family sharing a phone looks like one person.

One next-step recommendation: have staff read the phone number back at checkout and ask about contact consent every time.

## Section 7: Reflection

*The answers below are drafts written by Claude for Vinh to rewrite in Vinh's own words. The Feynman check especially must be Vinh's own explanation at the demo.*

**7.1** What would break first if Pho65 actually deployed this tool tomorrow?

Phone-number matching. Real counter staff mistype numbers, and every typo silently splits a regular into two "new" customers, exactly like Anh Nguyen in the seed data. The crosswalk fixes only typos someone has already found, so the follow-up queue would quietly miss people until someone reads the "Check these names" warning. Shared family phones would cause the opposite problem.

**7.2** Name one other small business where this same workflow could apply, and what would need to change.

A neighbourhood nail salon. `catering_slot` becomes `appointment_slot`, the capacity limit becomes the number of technicians per two-hour block, the consent gate maps to the salon's opt-in for appointment reminders, and "lapsed" would be closer to 5–6 weeks than 3, because people don't come in weekly.

**7.3** Feynman check (three sentences or fewer):

We treat two visits as the same person only when they used the same phone number, and we only count people who said "yes, you can contact me". Someone who comes in three times in two weeks becomes a "regular", and if a regular then stays away for three weeks, we write a friendly note for staff to read and send themselves. People who said no, or gave no number, are simply left out, never judged.

---

## ADI501 Extension Worksheet

*Not required: this team is in ADI201 (Steps 0–9 only).*

**G.1 ROI and Risk Memo** — Estimated value (cite a real number from your run), and the main privacy/consent risk.

*(your answer here)*

**G.2 Stakeholder and Support-Burden Analysis**

| Stakeholder | How they use the tool | What happens when phone-matching fails for them |
|---|---|---|
| Owner | | |
| Counter staff | | |
| Kitchen lead | | |

**G.3 Build-vs-Buy Memo** — Named product compared: __________. Recommendation and justification:

*(your answer here)*

**G.4 Pilot Recommendation** — Explicit continue/revise/stop thresholds for a 4-week trial:

- Continue if: *(your answer here)*
- Revise if: *(your answer here)*
- Stop if: *(your answer here)*
