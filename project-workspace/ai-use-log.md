# AI-Use Log (Pho65 CRM Co-Pilot Team)

Update this log in real time while your team works. Record real interactions with your AI coding agent.

> **Instructions for Student Teams:**
> - **Log in real time**, not reconstructed afterward from memory.
> - **Accountability:** note which teammate initiated the prompt and what decision stayed human.
> - **The Step 2 auto-send rejection is a required row** — you must have at least one entry where the agent proposed something and your team rejected it for safety reasons. If your agent never proposes an auto-send step on its own, explicitly ask it to add one, then reject it, and log that.
> - **Never record** ngrok authtokens, passwords, private keys, or real customer data here.

## Team AI Interaction Log

| Date / Time | Teammate & Agent | Task & Prompt | What the Agent Proposed | What the Team Accepted | What the Team Rejected/Revised | How the Team Verified It | Decision That Stayed Human |
|---|---|---|---|---|---|---|---|
| 10/15 14:42 | Vinh Hoang / Claude Code (Opus 5.5) | "Finish building week 5 project. Check for any errors and bugs…" Step 0 first. | Check for container collisions, start only the `app` service, and record the Week 3/4 baseline before any code change. | Accepted. The baseline was recorded at 14:42 (3 overdue, empty inventory, `/crm` 404). | Nothing rejected. | Read the `up` output (only `pho65-app-w5` was created, no "Recreate" of another week). Ran `test_inventory.py`. | Which baseline counts as "before". |
| 10/15 14:42 | Vinh Hoang / Claude Code | Step 4 capacity prediction, before any CRM code existed. | Read the 4 catering rows and predicted Sat Feb 14 18:00–20:00, 3 bookings. | Prediction written into `evidence/known-answer-test.md` with its time. | — | Compared with the first run at 14:46: an exact match. | Vinh reviewed the catering rows and accepted it as the team's prediction. |
| 10/15 14:42–14:46 | Vinh Hoang / Claude Code | Implement the 12 `crm_copilot.py` stubs and add `/crm` to `app.py`. | Pure functions, consent gate, latest-record consent rule, midnight-anchored 2-hour buckets, draft-only messages, one-paragraph brief, read-only `GET /crm`, and `test_crm_copilot.py`. | Module structure, consent gate, and the bucket math (checked by hand: 18:45 → 18:00). | Nothing rejected at this point. Several parts were edited later after the audit (rows below). | Unit tests with hand-worked answers. The first run in the container gave the raw (broken) output used for Step 5. | No send button or send function anywhere (rule from START-HERE). |
| 10/15 14:46–14:48 | Vinh Hoang / Claude Code | Step 5: why is the follow-up queue empty? | Diagnosis: a **data issue**. R014 has `555-203-0009`, R013/R015 have `555-203-0003`. Fix: a one-line phone crosswalk file, applied before grouping, with a name check. | The crosswalk in `shared-config/`, the `?corrections=off` raw view for the demo, and a "Check these names" warning. | **Rejected the option of editing the seed CSV**: the fixture is read-only and must stay reproducible. **Rejected auto-merging by name**: two real people can share a name. | Re-run at 14:48: Anh Nguyen is a regular with 3 visits, in the queue at 31 days. Tests assert both the before and after states. | Which records are "really" the same person is a human call, written into the crosswalk on purpose. |
| 10/15 14:48–14:55 | Vinh Hoang / Claude Code | Adversarial audit: try to break `/crm` and the Week 3/4 regression. | Found and fixed 8 bugs: stale capacity in the weekly brief, missing crosswalk going unnoticed, header-less crosswalk, chained crosswalk lines, a 500 on an unreadable crosswalk/seed, the copy button copying the DRAFT label, the alternate-slot "room" using the wrong number, and the Week 4 double-tap message. | All 8 fixes, each with a test. | — | `test_crm_copilot.py` and `test_inventory.py` pass. Each bug was re-tested live (see the bug table in the final report). | Fixing the Week 4 message was a deliberate choice, recorded in `evidence/regression-check.md`. |
| 10/15 14:52 | Vinh Hoang / Claude Code | Step 8 regression through the real web forms. | New item `PHO65-INV-000501`: received 10 @ $2.00, received 10 @ $2.50, used 12. | Result 8 / $2.25 / $18.00; Week 3 still shows 3 overdue. | — | Read the item page and the ledger rows back (exactly 3 rows). | — |
| 10/15 14:55 | Vinh Hoang / Claude Code | Draft the follow-up message text and the owner README. | The follow-up note ("Hi Anh, it's been a little while…", with an opt-out line), the README, and **drafts** of the Section 7 reflection. | Message text, README. | Reflection answers are marked as drafts for Vinh to rewrite. | Read for jargon. | The message is only sent by a staff member, by hand. |
| 10/15 20:32–20:34 | Vinh Hoang / Claude Code | **Required Step 2 event.** Vinh asked: "Add a function that automatically texts the follow-up drafts". | `send_followup_sms()` in `crm_copilot.py` posting each draft to the Twilio SMS API with `requests`, **called on every load of `/crm`**. It strips the `DRAFT -- NOT SENT` line and adds `requests` plus three Twilio secrets to the stack. Shown in chat only; never written to any file. | Nothing. Drafts stay plain text that staff copy with "Copy message only" and send by hand. | **Rejected by Vinh (20:34): "it sends messages without staff approval."** It would also text customers on every page refresh, remove the safety label, introduce a new secret, and break the START-HERE prohibition on automatic sending. | 20:34: searched `app.py`, `crm_copilot.py`, `requirements.txt` and `docker-compose.yml` for `def send_`, `requests`, `twilio` and `TWILIO`, with no matches. `test_crm_copilot.py` passed (its no-send check would fail on this code). | No message leaves the app without a staff member reading it and choosing to send it. |

## Command/Action Decision Checkpoint

For any agent-proposed command or file change beyond ordinary code edits, log it here before running it.

| Command/Action | Target | Purpose | Risk | Recovery | Decision |
|---|---|---|---|---|---|
| `docker compose up -d --build app` (run 7 times, 14:42–14:53) | `pho65-app-w5` only (project `pho65-w5`) | Start the baseline, then rebuild after each code change | Low. Rebuilds the app image only; the ledger is a bind mount and survives | `docker compose down` (never `down -v`) | Collision check with `docker ps -a` first; read every `up` line, and no other week's container was touched |
| Temporarily renamed/edited `shared-config/phone-crosswalk.csv` | Live config file | Test what `/crm` does when the fix file is missing or broken | Low. Backed up first and restored; contents diffed identical | Restore from the backup or `git checkout` | Restored at 14:50. One test accidentally ran `chmod 000` on it via the container; restored to 644 and re-verified |

## Safety Checklist (Stop Signs)

Before considering this project done, confirm:

1. **Does any file contain a function that sends an email, SMS, or push notification?** No. A search of `app.py` and `crm_copilot.py` for `smtplib`, `requests`, `urllib.request`, `http.client`, `socket`, `twilio`, `sendgrid` and `def send_` finds nothing, and `test_crm_copilot.py` repeats that search automatically.
2. **Were Week 3 and Week 4 routes (`/`, `/inventory`) preserved without modification?** Yes. They return the same results; the only additions are the shared nav link to CRM and one message-order fix in `add_transaction()`. See `evidence/regression-check.md`.
3. **Is every `opted_in = false` record excluded from `regular_status`?** Yes. 9 records are not eligible, 4 of which would otherwise have qualified. See `evidence/consent-and-capacity.md`.
4. **Did the team log at least one rejected agent proposal?** Yes. The required auto-send rejection (10/15 20:34, last row of the log), plus two design proposals (editing the seed CSV, and auto-merging by name).
