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
| *e.g., 09/22 14:05* | *e.g., Priya (data/schema owner) / Claude Code* | *e.g., "Propose a plan to add a /crm route to app.py that computes regular_status from the seed CSV."* | *e.g., Proposed crm_copilot.py with load/compute/route functions, including a draft_and_send_email() helper "for convenience."* | *e.g., Accepted the module structure and the consent-gate design.* | *e.g., Rejected draft_and_send_email() entirely — replaced with draft_message() that only returns a labeled string, no transport call.* | *e.g., Read the generated function line by line; confirmed no smtplib/requests import exists anywhere in crm_copilot.py.* | *e.g., Safety boundary: no code path may send a real message without a human explicitly choosing to.* |
| *e.g., 09/22 14:40* | *e.g., Marco (capacity owner) / Claude Code* | *e.g., "Implement the 2-hour capacity bucket logic."* | *e.g., Proposed slot_bucket() rounding by hour // 2 * 2.* | *e.g., Accepted the bucketing math.* | *e.g., None — verified against hand-computed buckets first.* | *e.g., Hand-computed which bucket 18:45 belongs to (18:00-20:00), then confirmed the function returned the same bucket.* | *e.g., Trusting a hand-verified calculation over the agent's claim that "the logic is correct."* |
| | | | | | | | |
| | | | | | | | |

## Command/Action Decision Checkpoint

For any agent-proposed command or file change beyond ordinary code edits, log it here before running it.

| Command/Action | Target | Purpose | Risk | Recovery | Decision |
|---|---|---|---|---|---|
| *e.g., `docker compose up -d --build app`* | *e.g., app container* | *e.g., rebuild with new /crm route* | *e.g., low — isolated to app image, no data loss* | *e.g., `docker compose down` reverts to no running container* | *e.g., Approved by whole team before running* |
| | | | | | |

## Safety Checklist (Stop Signs)

Before considering this project done, confirm:

1. **Does any file contain a function that sends an email, SMS, or push notification?** *(Answer: No — verified by searching for `send_`, `smtplib`, `requests.post` across `docker/app/`.)*
2. **Were Week 3 and Week 4 routes (`/`, `/inventory`) preserved without modification?** *(Answer: Yes — see `evidence/regression-check.md`.)*
3. **Is every `opted_in = false` record excluded from `regular_status`?** *(Answer: Yes — see `evidence/consent-and-capacity.md`.)*
4. **Did the team log at least one rejected agent proposal?** *(Answer: Yes — see row above.)*
