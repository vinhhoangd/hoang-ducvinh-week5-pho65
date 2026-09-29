# Pho65 Week 5 Team Project Workspace — CRM Co-Pilot

> **Instructions for Student Teams:** Complete this README as your team extends the Pho65 app with the CRM co-pilot. Write it so a reviewer with no prior context could run and test your extension without asking you a question. Replace every *italicized example* with your team's real content; do not delete the section headers.

## 1. Purpose & Intended User

- **System name:** *e.g., "Pho65 CRM Co-Pilot"*
- **Intended user:** *(who reads the weekly narrative brief and follow-up drafts — e.g., "the café owner, checked once a week between the lunch and dinner rush")*
- **Core problem solved:** *(e.g., "surfaces which regulars may be drifting away and which catering slots are overbooked, without a membership program and without sending anything automatically")*

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

Then open:
- `http://localhost:5050/` — Week 3 order tracker (regression)
- `http://localhost:5050/inventory` — Week 4 inventory ledger (regression)
- `http://localhost:5050/crm` — Week 5 CRM co-pilot (new)

> Port is **5050**, not 5000 — macOS AirPlay Receiver claims 5000 by default on many machines.

## 5. Automated Verification

```bash
docker compose exec app python test_inventory.py
docker compose exec app python test_crm_copilot.py
```

*Expected: both print a "passed" line with no assertion errors.* Record your team's actual output in `evidence/known-answer-test.md` and `evidence/regression-check.md`.

## 6. Testing Fixture Matrix

| Fixture | Location | Used for |
|---|---|---|
| `pho65-week5-seed.csv` | `sample-data/` | CRM co-pilot known-answer test |
| `pho65-orders-valid.csv` | `sample-data/` | Week 3 regression |
| Fresh inventory item (create your own) | `/inventory/new` | Week 4 regression cost test |

## 7. Common Troubleshooting Scenarios

1. **Port conflict on 5050:** *(e.g., "another team's stack was still running — `docker compose down` in the other project first")*
2. **`/crm` shows "Seed file not found":** check the volume mount in `docker-compose.yml` points `../sample-data` to `/data`, and that `pho65-week5-seed.csv` is actually present there.
3. **Host binding:** confirm the compose file binds `0.0.0.0` inside the container (already configured) — a `127.0.0.1`-only bind would block access from another device on your network.

## 8. Known Limitations

*(e.g., "phone-number matching fails when a family shares one phone number across multiple household members" — state your team's actual limitation here, matching your manager README)*
