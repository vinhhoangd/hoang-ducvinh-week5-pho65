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

**0.1** Before touching `app.py`, what did `http://localhost:5050/` show? *(e.g., "Pho65 order tracker (Week 3 regression), 6 fixture orders listed")*

*(your answer here)*

**0.2** Before touching `app.py`, what did `http://localhost:5050/inventory` show? *(e.g., "empty table, no items yet")*

*(your answer here)*

## Section 1: Schema Worksheet

**1.1** In your own words, what is the difference between `regular_status` and `member_status`?

`regular_status`: *(your answer here)*

`member_status`: *(your answer here)*

**1.2** Write your exact "same customer" matching rule: *(e.g., "same phone_number AND opted_in=true on the most recent record for that number")*

*(your answer here)*

**1.3** Your thresholds and justification:

| Threshold | Value | Justification |
|---|---|---|
| Visit frequency for `regular_status` | | |
| Lapsed-regular window (narrative brief) | | |
| Capacity limit per time slot | | |

## Section 2: Agent Plan Review

**2.1** Summarize the agent's proposed plan for the co-pilot.

*(your answer here)*

**2.2** Does the plan include any auto-send step? (It must not.) How did you confirm this?

*(your answer here)*

**2.3** What did you change in the plan before approving it, and why?

*(your answer here)*

## Section 3: Build Log

| Component | Decision (accepted as-is / edited / rejected) | Reason |
|---|---|---|
| Data loading | | |
| `regular_status` computation | | |
| Capacity check | | |
| Draft-message generation | | |
| Narrative brief | | |

## Section 4: Known-Answer Test

**4.1** Prediction (before running, capacity only):

- Expected over-capacity day/slot: *(your answer here)*
- Expected count in that slot: *(your answer here)*

**4.2** Observed result (first run):

- Actual over-capacity flag output: *(your answer here)*
- Actual follow-up queue output: *(your answer here)*

**4.3** Diagnosis: data / logic / interface issue? Explain how you determined this.

*(your answer here)*

**4.4** Fix applied (smallest correction):

*(your answer here)*

**4.5** Observed result (after fix):

*(your answer here)*

**4.6** Does the re-run now match what you expected? If not, explain the remaining gap.

*(your answer here)*

## Section 5: Innovation Requirements Evidence

**5.1** Consent-first regulars detection — where does this happen, and how many records were excluded?

*(your answer here)*

**5.2** Demand-shaping catering suggestion — name the request and the suggested alternate slot, and why.

*(your answer here)*

**5.3** Weekly narrative brief — paste your co-pilot's generated paragraph.

*(your answer here)*

## Section 6: Manager-Facing README (Draft)

Three "what it does" bullets:

- *(your answer here)*
- *(your answer here)*
- *(your answer here)*

"What it does not do" statement: *(your answer here)*

One known limitation: *(your answer here)*

One next-step recommendation: *(your answer here)*

## Section 7: Reflection

**7.1** What would break first if Pho65 actually deployed this tool tomorrow?

*(your answer here)*

**7.2** Name one other small business (not Pho65) where this same workflow could apply, and what would need to change.

*(your answer here)*

**7.3** Feynman check: explain your matching rule and consent-first design to someone with no technical background, in three sentences or fewer.

*(your answer here)*

---

## ADI501 Extension Worksheet

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
