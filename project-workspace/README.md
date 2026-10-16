# Pho65 Week 5 Team Project Workspace — CRM Co-Pilot

## 1. Purpose & Intended User

- **System name:** Pho65 CRM Co-Pilot (the `/crm` page of the Pho65 café app, next to the Week 3 order tracker and the Week 4 inventory ledger)
- **Intended user:** the café owner, who reads the weekly brief once a week between the lunch and dinner rush, and the counter staff, who review and send the follow-up drafts by hand
- **Core problem solved:** shows which regulars may be drifting away and which catering windows are overbooked (with a quieter alternative), without a membership program, without scoring anyone who didn't opt in, and without ever sending anything automatically

### For the owner

**What it does**

- Each week, it tells you which regular customers haven't been in for three weeks or more, and writes a short "we miss you" note you can read, change, and send yourself.
- It warns you when too many catering orders land in the same two-hour window, and names a quieter time that same day to offer instead.
- It sums up the week in one short paragraph at the top of the page, so you don't have to read any tables.

**What it does not do:** it never sends a message by itself; there is no send button anywhere in the app. It doesn't run a membership or points program. It never scores or follows up with anyone who hasn't agreed to be contacted, or anyone who left no phone number.

**One known limitation:** it recognises a returning customer only by phone number. If a number is typed wrong once, the same person looks like two people and can be missed. That is exactly what happened to one regular in our test data. If a family shares one phone, they look like one person.

**One next step:** ask staff to read the phone number back to the customer at checkout, and to ask about contact consent every time. When the page shows a "Check these names" warning, have someone look at it that week.

## 2. Safe-Data Boundary

- **Allowed data:** the provided `sample-data/pho65-week5-seed.csv` only. No real customer names, phone numbers, or visit history.
- **Strictly prohibited:** real customer data of any kind, any automated send capability (email/SMS/push), SSH private keys, ngrok tokens.

## 3. Prerequisites

| Software | Version | Check command |
|---|---|---|
| Docker Desktop | any recent | `docker info` |
| Docker Compose | v2+ | `docker compose version` |
| A web browser | any modern | — |

## 4. Local Setup & Run

**macOS/Linux:**
```bash
cd project-workspace/docker
docker compose up -d --build app
```

**Windows (PowerShell):**
```powershell
cd project-workspace\docker
docker compose up -d --build app
```

Wait about 5 seconds, then open:
- `http://localhost:5050/` — Week 3 order tracker (regression)
- `http://localhost:5050/inventory` — Week 4 inventory ledger (regression)
- `http://localhost:5050/crm` — Week 5 CRM co-pilot (new)
- `http://localhost:5050/crm?corrections=off` — the same page on the raw data, before the Step 5 phone fix (for the known-answer demo)
- `http://localhost:5050/crm?as_of=2026-02-05` — any other "as of" date (YYYY-MM-DD); the date box on the page does the same

On a phone, run `ngrok http 5050` yourself (never give an agent your ngrok token) and open the `https://…ngrok-free.dev` address it prints.

> Port is **5050**, not 5000 — macOS AirPlay Receiver claims 5000 by default on many machines.

## 5. Automated Verification

```bash
docker compose exec app python test_inventory.py
docker compose exec app python test_crm_copilot.py
```

Expected (actual output, 2026-10-15):

```
inventory known-answer and guard tests passed
crm co-pilot known-answer, edge-case, and draft-only tests passed
```

`test_crm_copilot.py` checks the known answers on the seed file both before and after the phone fix. It covers edge cases (the 14-day boundary, 18:45 landing in the 18:00 window, consent withdrawn, bad rows, bad config files), checks that `app.py` and `crm_copilot.py` contain no email, SMS or network-sending code, and renders `/crm`, `/` and `/inventory`. The full results are in `evidence/known-answer-test.md` and `evidence/regression-check.md`.

## 6. Testing Fixture Matrix

| Fixture | Location | Used for |
|---|---|---|
| `pho65-week5-seed.csv` | `sample-data/` | CRM co-pilot known-answer test |
| `pho65-orders-valid.csv` | `sample-data/` | Week 3 regression |
| Fresh inventory item (create your own) | `/inventory/new` | Week 4 regression cost test |
| `phone-crosswalk.csv` | `docker/shared-config/` | Step 5 fix: maps the mistyped `555-203-0009` to `555-203-0003`. Re-read on every request |

## 7. Common Troubleshooting Scenarios

1. **Port conflict on 5050, or another week's container gets replaced:** every week's folder is called `docker`, so this compose file pins `name: pho65-w5`. Before `up`, check what is running with `docker ps -a --format '{{.Names}} {{.Label "com.docker.compose.project"}} {{.Ports}}'`, and stop the other stack with `docker compose down` in *its* folder. Never use `down -v`, which deletes the ledger.
2. **`/crm` shows "Seed file not found":** check the volume mount in `docker-compose.yml` points `../sample-data` to `/data`, and that `pho65-week5-seed.csv` is actually present there.
3. **Host binding:** confirm the compose file binds `0.0.0.0` inside the container (already configured) — a `127.0.0.1`-only bind would block access from another device on your network.
4. **`/crm` shows "Check these names" or "Phone-fix file … was not found":** `docker/shared-config/phone-crosswalk.csv` is missing or broken, so the page is showing raw data. Restore it from git (`git checkout -- docker/shared-config/phone-crosswalk.csv`).

## 8. Known Limitations

- Customers are matched only by phone number. A mistyped number splits one person into two (the seeded failure, fixed here with a one-line crosswalk), and a family sharing one phone looks like one person.
- A "visit" is a calendar day, and "3 in 14 days" means the first and third visits are at most 13 days apart. So a customer who comes exactly once a week on the same weekday does not count as a regular.
- The alternate catering time is chosen only from windows that already have a catering booking that day, because the data has no opening hours.
- The data is a fixed fictional CSV. Nothing here reads a live point-of-sale system.
