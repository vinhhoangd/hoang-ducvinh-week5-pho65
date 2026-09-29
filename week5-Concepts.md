# Week 5 Concepts — Pho65 CRM Co-Pilot

Read this before Step 0 if any of these terms are new. Each entry explains what the term is, why it matters this week, how it shows up in your actual build, and gives you a prompt you can ask your AI agent to explore further on your own.

## `regular_status` vs `member_status`

**What it is:** `regular_status` is a flag your code *computes* from how often a customer visits. `member_status` is a flag that would only be set if a customer explicitly signed up for something — a membership program this project does not build.

**Why it matters:** Confusing these two is the single most common Week 5 mistake. If you treat `member_status` as something to compute, you've built the wrong feature.

**How it appears in your work:** The seed CSV has no `member_status` column at all — it's deliberately absent so you can't accidentally implement logic for it. `regular_status` is a value you will compute in `crm_copilot.py` and display on `/crm`.

**Ask your agent:** "Explain the difference between a computed behavioral flag and an explicit enrollment flag in a CRM system, with one example of each from a business you know."

## Consent gating

**What it is:** A rule that a customer's data can only be used for a certain purpose (here: being flagged as a regular) if they've explicitly agreed (`opted_in = true`).

**Why it matters:** A naive frequency-only rule would flag *any* frequent visitor as a regular, opted in or not — that's a privacy violation, even with fabricated data. Consent gating is the difference between "we noticed you visit a lot" and "we noticed you visit a lot, and you told us it's okay to track that."

**How it appears in your work:** you'll implement `eligible_records()` in `crm_copilot.py` (already stubbed) to filter to `phone_number` present AND `opted_in = true` before anything else runs. Your `/crm` page should report exactly how many records were excluded for this reason.

**Ask your agent:** "What's the difference between anonymized data and consent-gated data, and why might a business need both?"

## Lapsed-regular window

**What it is:** A threshold (e.g., 21+ days) that turns "someone who used to visit often" into "someone worth a follow-up."

**Why it matters:** Without a lapsed window, every regular customer would be in the follow-up queue forever, which makes the queue useless. The window is a business judgment call, not a fact — you justify your own number.

**How it appears in your work:** you'll implement `lapsed_followup_queue()` so it only includes customers who were flagged regular AND haven't visited in your chosen window.

**Ask your agent:** "How would you choose a 'customer at risk of churning' threshold for a business that sees repeat customers roughly weekly, versus one that sees them roughly monthly?"

## Capacity bucketing

**What it is:** Dividing a day into fixed time windows (here, 2-hour buckets anchored at midnight) so you can count how many catering bookings land in the same window.

**Why it matters:** "Over capacity" only means something relative to a specific window. Get the bucket boundaries wrong (e.g., counting per-day instead of per-window) and every capacity warning is meaningless.

**How it appears in your work:** you'll implement `slot_bucket()` to round a booking's start time down to its 2-hour window, and `capacity_view()` to count bookings per bucket and flag any bucket over your threshold.

**Ask your agent:** "If a booking starts at 17:59 and another starts at 18:01, should a 2-hour-bucket system anchored at midnight treat them as the same slot? Why or why not?"

## Demand-shaping suggestion

**What it is:** Instead of only warning "this slot is full," naming a specific, less-busy slot as an alternative.

**Why it matters:** A warning without a suggestion pushes the decision-making work back onto a busy owner. A named alternative is a decision they can act on immediately.

**How it appears in your work:** you'll implement `suggest_alternate_slot()` to look at same-day buckets and pick the one with the fewest historical bookings.

**Ask your agent:** "What data would a real restaurant CRM need to suggest alternate slots more intelligently than 'lowest historical count'?"

## Draft-only / never-sent pattern

**What it is:** A design rule that a system may *generate* message text but must never *transmit* it without a human explicitly choosing to send it.

**Why it matters:** This is the project's hard safety boundary. An agent that "helpfully" adds a send function has crossed a line that must be caught and rejected, every time.

**How it appears in your work:** you'll implement `draft_message()` to return a string labeled `DRAFT -- NOT SENT`. Do not add a `send_*` function anywhere in `crm_copilot.py` — and check the finished file yourself to confirm one never crept in.

**Ask your agent:** "Why might a business deliberately choose not to automate the 'send' step of a customer follow-up workflow, even if the drafting step is automated?"

## Build-vs-buy (ADI501)

**What it is:** The decision a manager makes between building a custom tool in-house versus purchasing an existing commercial product.

**Why it matters:** A working prototype doesn't automatically mean "build it." Named commercial CRMs (Toast Loyalty, Square Loyalty, SevenRooms) already solve parts of this problem — sometimes better, sometimes worse, for a specific business's needs.

**How it appears in your work:** Your ADI501 build-vs-buy memo names one specific product and compares it to your prototype on cost, data ownership, and workflow fit.

**Ask your agent:** "What are three questions a small-business owner should ask before choosing between a custom-built internal tool and an off-the-shelf CRM product?"
