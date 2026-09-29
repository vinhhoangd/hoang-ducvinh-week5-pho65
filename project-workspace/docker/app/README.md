# Pho65 App Container

## How to Build

```bash
docker build -t pho65-app .
```

## How to Run Standalone for a Quick Local Check

```bash
docker run -p 5050:5000 -e OVERDUE_MIN=20 -e NOW_OVERRIDE="2026-01-15 12:30" \
  -e CRM_SEED_CSV=/data/pho65-week5-seed.csv -e CRM_AS_OF=2026-02-15 \
  -v $(pwd)/../../sample-data:/data pho65-app
```

(Week 5 note: the shared `docker-compose.yml` publishes host port **5050**, not 5000, to avoid a collision with macOS AirPlay Receiver, which claims 5000 by default.)

## Known-Answer Tests

- **Orders (Week 3):** with `OVERDUE_MIN=20`, the packaged `pho65-orders-valid.csv`, and `NOW_OVERRIDE="2026-01-15 12:30"`, the app must show exactly **3 overdue orders** (O-001, O-002, O-003). Do not change the fixture or this expected count.
- **Inventory (Week 4):** on any fresh item, receive 10 @ $2.00, receive 10 @ $2.50, use 12 → 8 remaining at average cost $2.25, value $18.00. Run `python test_inventory.py` inside the container, or repeat it manually on a new item (the ledger is append-only and per-item, so there is no whole-database reset).
- **CRM co-pilot (Week 5):** this is what you build and verify yourself in Steps 3-6 of the assignment — predict, run, diagnose, fix, re-test. Record your results in `evidence/known-answer-test.md`.

## Environment Variables

- `ORDERS_CSV`: Can point at a different filename inside the mounted `/data` directory if a different fixture is used.
- `OVERDUE_MIN`: Minimum minutes for an order to be considered overdue.
- `NOW_OVERRIDE`: Override the current time for testing purposes.

## Startup Output

The app prints the following to stdout at startup:

```
Pho65 order tracker started. OVERDUE_MIN=<value> ORDERS_CSV=<path>
```

This line is important for later `docker logs` / SSH-based diagnosis exercises.
