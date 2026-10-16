"""Run inside the app image: python test_crm_copilot.py.

Known-answer checks for the Week 5 CRM co-pilot against the packaged seed
file, plus edge cases and a no-send guard. Every expected value here was
worked out by hand from pho65-week5-seed.csv before the code ran.
"""
import os
import re
import tempfile
from datetime import datetime

temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
temp.close()
os.environ["INVENTORY_DB"] = temp.name

import crm_copilot as crm  # noqa: E402

SEED = os.environ.get("CRM_SEED_CSV", "/data/pho65-week5-seed.csv")
CROSSWALK = os.environ.get("PHONE_CROSSWALK_PATH", "/config/phone-crosswalk.csv")
AS_OF = datetime(2026, 2, 15)


def write_csv(text):
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    handle.write(text)
    handle.close()
    return handle.name


HEADER = "record_id,customer_name,phone_number,opted_in,visit_date,order_type,catering_slot\n"

# --- Seed file, raw data ------------------------------------------------------
raw = crm.run(SEED, AS_OF)
assert raw["record_count"] == 29, raw["record_count"]
regulars = sorted(c["name"] for c in raw["regular_status"].values() if c["is_regular"])
assert regulars == ["Mai Tran"], regulars
# Consent check: Linh Pham's 4 opted-out visits (R009-R012) would have qualified.
assert [r["record_id"] for r in raw["excluded_non_opted_in"]] == ["R009", "R010", "R011", "R012"]
assert raw["excluded_non_opted_in_count"] == 4 and raw["excluded_customer_count"] == 1
for record in raw["excluded_non_opted_in"]:
    assert record["phone_key"] not in raw["regular_status"], record
# Capacity: Sat Feb 14 18:00-20:00 holds R016 18:00, R017 18:45, R018 19:30.
over = [b for b in raw["capacity"] if b["over_capacity"]]
assert len(over) == 1 and over[0]["bucket_start"] == datetime(2026, 2, 14, 18) and over[0]["count"] == 3
assert [r["record_id"] for r in over[0]["records"]] == ["R016", "R017", "R018"]
alternate = raw["conflicts"][0]["alternate"]
assert alternate["bucket_start"] == datetime(2026, 2, 14, 14) and alternate["count"] == 1
# Guest (R029) has no phone: not eligible, never scored.
assert [r["record_id"] for r in raw["not_eligible_no_phone"]] == ["R029"]
# The seeded failure: Anh Nguyen is split across 0003 (2 visits) and 0009 (1 visit).
assert raw["followup_queue"] == [], raw["followup_queue"]
assert [d["name"] for d in raw["possible_duplicates"]] == ["Anh Nguyen"]

# --- Seed file after the Step 5 fix (phone crosswalk) ------------------------
fixed = crm.run(SEED, AS_OF, CROSSWALK)
assert [r["record_id"] for r in fixed["corrections_applied"]] == ["R014"]
regulars = sorted(c["name"] for c in fixed["regular_status"].values() if c["is_regular"])
assert regulars == ["Anh Nguyen", "Mai Tran"], regulars
anh = fixed["regular_status"]["5552030003"]
assert (anh["visit_count"], anh["last_visit"], anh["is_regular"]) == (3, datetime(2026, 1, 15), True), anh
assert [(c["name"], c["days_since_visit"]) for c in fixed["followup_queue"]] == [("Anh Nguyen", 31)]
assert len(fixed["drafts"]) == 1 and fixed["drafts"][0]["text"].startswith("DRAFT -- NOT SENT")
assert fixed["possible_duplicates"] == [] and fixed["excluded_non_opted_in_count"] == 4
assert [(b["bucket_start"], b["count"]) for b in fixed["capacity"]] == [(b["bucket_start"], b["count"]) for b in raw["capacity"]]

# A crosswalk line can't merge two different people (Rosa Kim -> Mai Tran's number).
wrong = write_csv("wrong_phone,correct_phone,note\n555-209-0009,555-201-0001,bad line\n")
merged = crm.run(SEED, AS_OF, wrong)
assert merged["corrections_applied"] == [] and any("R021" in p for p in merged["problems"])
missing_file = crm.run(SEED, AS_OF, "/nonexistent/crosswalk.csv")
assert missing_file["followup_queue"] == [] and any("not found" in p for p in missing_file["problems"])
# A crosswalk with no header must not silently swallow its first correction.
headerless = crm.run(SEED, AS_OF, write_csv("555-203-0009,555-203-0003,typo\n"))
assert headerless["corrections_applied"] == [] and any("header" in p for p in headerless["problems"])
# An unreadable file (here: a directory) is reported, not a crash.
unreadable = crm.run(SEED, AS_OF, tempfile.mkdtemp())
assert unreadable["corrections_applied"] == [] and any("could not be read" in p for p in unreadable["problems"])
# Chained lines (a->b, b->c) are refused instead of depending on line order.
chain = crm.load_phone_crosswalk(write_csv("wrong_phone,correct_phone\n555-203-0009,555-203-0003\n555-203-0003,555-201-0001\n"), [])
assert chain == {"5552030003": "5552010001"}, chain

# --- Weekly capacity window ---------------------------------------------------
late = crm.run(SEED, datetime(2026, 3, 31), CROSSWALK)
assert late["capacity"] == [] and late["older_catering_count"] == 4
assert "No catering window is over the limit." in late["narrative_brief"]
early = crm.run(SEED, datetime(2026, 1, 14), CROSSWALK)   # Feb 14 is still upcoming
assert [b["count"] for b in early["capacity"]] == [1, 3] and early["older_catering_count"] == 0
assert crm.run(SEED, datetime(2026, 2, 20), CROSSWALK)["capacity"] != []   # week Feb 14-20 includes Feb 14
assert crm.run(SEED, datetime(2026, 2, 21), CROSSWALK)["capacity"] == []   # week Feb 15-21 does not

# --- Edge cases ---------------------------------------------------------------
day = lambda text: datetime.strptime(text, crm.DATE_FMT)
assert crm.has_three_in_window([day("2026-01-01"), day("2026-01-07"), day("2026-01-14")])      # 13 days apart
assert not crm.has_three_in_window([day("2026-01-01"), day("2026-01-07"), day("2026-01-15")])  # 14 days apart
assert not crm.has_three_in_window([day("2026-01-01")] * 3)                                     # same day = 1 visit
assert crm.slot_bucket(datetime(2026, 2, 14, 18, 45)) == datetime(2026, 2, 14, 18)
assert crm.slot_bucket(datetime(2026, 2, 14, 19, 59)) == datetime(2026, 2, 14, 18)
assert crm.slot_bucket(datetime(2026, 2, 14, 20, 0)) == datetime(2026, 2, 14, 20)
assert crm.slot_bucket(datetime(2026, 2, 14, 0, 30)) == datetime(2026, 2, 14, 0)
assert crm.normalize_phone("(555) 203-0003") == crm.normalize_phone("555-203-0003") == "5552030003"
assert crm.normalize_phone("n/a") == ""

# Consent must be the explicit word "true"; "yes" or "TRUE " behave as written.
rows = write_csv(HEADER + "A1,Al,555-300-0001,yes,2026-02-01,dine_in,\n"
                          "A2,Al,555-300-0001,yes,2026-02-03,dine_in,\n"
                          "A3,Al,555-300-0001,yes,2026-02-05,dine_in,\n"
                          "B1,Bo,555-300-0002, TRUE ,2026-02-01,dine_in,\n")
loaded = crm.load_records(rows)
assert [r["opted_in"] for r in loaded] == [False, False, False, True]

# Consent withdrawn on the most recent record: no longer eligible at all.
rows = write_csv(HEADER + "C1,Cy,555-300-0003,true,2026-02-01,dine_in,\n"
                          "C2,Cy,555-300-0003,true,2026-02-03,dine_in,\n"
                          "C3,Cy,555-300-0003,true,2026-02-05,dine_in,\n"
                          "C4,Cy,555-300-0003,false,2026-02-07,dine_in,\n")
status, excluded = crm.compute_regular_status(crm.load_records(rows), AS_OF)
assert status == {} and [r["record_id"] for r in excluded] == ["C4"], (status, excluded)

# Visits after the as-of date are ignored.
rows = write_csv(HEADER + "D1,Di,555-300-0004,true,2026-02-01,dine_in,\n"
                          "D2,Di,555-300-0004,true,2026-02-03,dine_in,\n"
                          "D3,Di,555-300-0004,true,2026-02-20,dine_in,\n")
status, _ = crm.compute_regular_status(crm.load_records(rows), AS_OF)
assert status["5553000004"]["visit_count"] == 2 and not status["5553000004"]["is_regular"]

# Bad rows are reported, not fatal.
problems = []
rows = write_csv(HEADER + "E1,Ed,555-300-0005,true,15/02/2026,dine_in,\n"
                          "E2,Ed,555-300-0005,true,2026-02-14,catering,evening\n")
loaded = crm.load_records(rows, problems)
assert [r["record_id"] for r in loaded] == ["E2"] and loaded[0]["catering_slot"] is None and len(problems) == 2
try:
    crm.load_records(write_csv("record_id,customer_name\nX1,Xu\n"))
except ValueError as error:
    assert "missing column" in str(error)
else:
    raise AssertionError("a file with missing columns was accepted")

# Overflow 2 but room for only 1: the advice must not overfill the quiet window.
busy = write_csv(HEADER + "".join(f"F{i},Fan {i},555-400-000{i},true,2026-02-14,catering,2026-02-14 18:{i}0\n" for i in range(4))
                 + "F9,Fay,555-400-0009,true,2026-02-14,catering,2026-02-14 12:00\n")
crowded = crm.run(busy, AS_OF)
conflict = crowded["conflicts"][0]
assert (conflict["overflow"], conflict["room"], conflict["move"]) == (2, 1, 1), conflict
assert "offer that time to 1 booking" in crowded["narrative_brief"] and "call the other 1 customer" in crowded["narrative_brief"]
# No room anywhere that day: no suggestion rather than a bad one.
full = [{"bucket_start": datetime(2026, 2, 14, h), "count": c, "over_capacity": c > 2} for h, c in ((12, 2), (18, 3))]
assert crm.suggest_alternate_slot(full, full[1]) is None

# --- Draft-only guard ---------------------------------------------------------
draft = crm.draft_message("Anh Nguyen", "test")
assert draft.startswith("DRAFT -- NOT SENT") and "Hi Anh," in draft
body = crm.draft_body(draft)
assert body.startswith("Hi Anh,") and "DRAFT" not in body and "For staff" not in body
here = os.path.dirname(os.path.abspath(__file__))
for name in ("crm_copilot.py", "app.py"):
    source = open(os.path.join(here, name), encoding="utf-8").read()
    for banned in ("smtplib", "import requests", "urllib.request", "http.client", "import socket", "twilio", "sendgrid", "def send_"):
        assert banned not in source, f"{name} contains {banned!r}: no code may transmit a message"

# --- /crm route ---------------------------------------------------------------
import app  # noqa: E402

client = app.app.test_client()
page = client.get("/crm")
assert page.status_code == 200, page.status_code
html = page.get_data(as_text=True)
assert "This week, in plain words" in html and "over capacity" in html
assert "DRAFT -- NOT SENT" in html and "Anh Nguyen (last visit Jan 15, 31 days ago)" in html
copy_source = re.search(r"<textarea[^>]*>(.*?)</textarea>", html, re.S).group(1)
assert copy_source.startswith("Hi Anh,") and "DRAFT" not in copy_source
raw_page = client.get("/crm?corrections=off").get_data(as_text=True)
assert "Raw-data view" in raw_page and "DRAFT -- NOT SENT" not in raw_page
assert not re.search(r"<form[^>]*method=['\"]?post", html, re.I), "the CRM page must not post anything"
assert client.get("/crm?as_of=not-a-date").status_code == 200
assert "Order tracker" in client.get("/").get_data(as_text=True)
assert client.get("/inventory").status_code == 200
saved, app.CRM_SEED_CSV = app.CRM_SEED_CSV, "/data/missing.csv"
missing = client.get("/crm")
assert missing.status_code == 503 and "Seed file not found" in missing.get_data(as_text=True)
app.CRM_SEED_CSV = tempfile.mkdtemp()   # unreadable seed path: friendly 503, not a 500
assert client.get("/crm").status_code == 503
app.CRM_SEED_CSV = saved
saved, app.CRM_AS_OF = app.CRM_AS_OF, "15/02/2026"
bad_default = client.get("/crm")
assert bad_default.status_code == 503 and "CRM_AS_OF" in bad_default.get_data(as_text=True)
app.CRM_AS_OF = saved

print("crm co-pilot known-answer, edge-case, and draft-only tests passed")
