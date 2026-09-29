# Run Pho65 Week 3/4/5 locally, then on a phone

From this folder, start the extended stack:

```bash
docker compose up -d --build app
curl http://localhost:5050/health
open http://localhost:5050/inventory
```

Host port is **5050** (not 5000) — macOS AirPlay Receiver claims 5000 by default on many machines.

The app has a persistent SQLite file in `inventory-data/`. To deliberately start over during a class exercise, stop the stack and delete only `inventory-data/pho65-inventory.db`; do not delete the whole project or copy any secrets into it. For the Week 5 regression check specifically, you do not need to do this — create one fresh item instead (see `app/README.md`), so the order tracker and inventory ledger can both stay live while you test.

## New in Week 5: CRM co-pilot (you build this)

`/crm` does not exist yet — it is your Step 3 deliverable. It should be a new, read-only route added to the same `app` container. It will load `../sample-data/pho65-week5-seed.csv` (already mounted at `/data`, same volume Week 3/4 use) and compute regulars, capacity warnings, a follow-up queue, and a narrative brief. It must never send anything — every generated message must be labeled `DRAFT -- NOT SENT`. Start from the function signatures in `app/crm_copilot.py`.

## Phone camera path: use ngrok HTTPS

Phone camera APIs normally require HTTPS. A LAN URL such as `http://192.168...:5050` is not the required path for this course.

1. Register for an ngrok account and obtain **your own** authtoken from its dashboard.
2. Ask a code agent to install ngrok using your operating system’s normal package-manager instructions. The agent may run or explain non-secret installation commands, but **never give it your authtoken**.
3. You personally type this command in your terminal, replacing the placeholder without sharing the value:

   ```bash
   ngrok config add-authtoken <YOUR_TOKEN>
   ```

4. With the local app running, start the temporary HTTPS tunnel:

   ```bash
   ngrok http 5050
   ```

5. Open the displayed `https://...ngrok...` forwarding URL on your phone, choose **Scan / look up**, and allow camera access. Stop ngrok when the test is over.

The token is an account credential. Do not put it in an AI prompt, shell script, `.env`, Git repository, screenshot, evidence file, or ZIP. The public URL is for fictional class data only. If camera permission or the network fails, use the scanner’s image-file or manual-code path and record the failure/recovery result.

## Retained Week 3/4 regression

The app is now at `http://localhost:5050`, and the original SSH practice service remains on port 2222. Test it only with your own public/private keypair; private keys and ngrok tokens never belong in this repository.

```bash
ssh -i <path-to-private-key> pho65user@localhost -p 2222 whoami
```

