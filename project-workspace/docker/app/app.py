"""Pho65 Week 4: a deliberately small, inspectable inventory ledger."""
import csv
import io
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

import qrcode
from PIL import Image, ImageDraw
from flask import Flask, abort, flash, jsonify, redirect, render_template_string, request, send_file, url_for

import crm_copilot

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "week4-local-demo-only")

ORDERS_CSV = os.environ.get("ORDERS_CSV", "/data/pho65-orders-valid.csv")
DB_PATH = os.environ.get("INVENTORY_DB", "/inventory-data/pho65-inventory.db")
CRM_SEED_CSV = os.environ.get("CRM_SEED_CSV", "/data/pho65-week5-seed.csv")
CRM_AS_OF = os.environ.get("CRM_AS_OF", "2026-02-15")


def db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS items (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          scan_code TEXT NOT NULL UNIQUE,
          code_kind TEXT NOT NULL CHECK(code_kind IN ('manufacturer', 'internal')),
          base_unit TEXT NOT NULL,
          reorder_point INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS inventory_transactions (
          id INTEGER PRIMARY KEY,
          item_id INTEGER NOT NULL REFERENCES items(id),
          action TEXT NOT NULL CHECK(action IN ('starting', 'received', 'used', 'wasted', 'counted', 'correction')),
          quantity_delta INTEGER NOT NULL,
          unit_cost_cents INTEGER,
          occurred_at TEXT NOT NULL,
          recorded_by TEXT NOT NULL,
          note TEXT NOT NULL DEFAULT '',
          request_id TEXT NOT NULL UNIQUE
        );
        """)


def money(cents):
    return f"${Decimal(cents or 0) / 100:.2f}"


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def inventory_state(item_id):
    """Replay one item's ledger. Receipts reset the moving weighted average.

    Quantities and costs are integer base units/cents: no binary float surprises.
    """
    with db() as con:
        rows = con.execute("""SELECT * FROM inventory_transactions
                            WHERE item_id=? ORDER BY occurred_at, id""", (item_id,)).fetchall()
    quantity, average_cents = 0, 0
    for row in rows:
        delta = row["quantity_delta"]
        if delta > 0 and row["unit_cost_cents"] is not None:
            total_value = quantity * average_cents + delta * row["unit_cost_cents"]
            quantity += delta
            average_cents = int((Decimal(total_value) / quantity).quantize(Decimal("1"), ROUND_HALF_UP))
        else:
            quantity += delta
    return {"quantity": quantity, "average_cents": average_cents,
            "value_cents": quantity * average_cents, "transactions": rows}


def all_items():
    with db() as con:
        rows = con.execute("SELECT * FROM items ORDER BY name").fetchall()
    result = []
    for row in rows:
        state = inventory_state(row["id"])
        result.append({**dict(row), **state, "low": state["quantity"] <= row["reorder_point"]})
    return result


def add_transaction(item_id, action, quantity_delta, unit_cost_cents, recorded_by, note, request_id):
    if not request_id:
        raise ValueError("Missing request ID. Refresh and try again.")
    state = inventory_state(item_id)
    if action in {"used", "wasted"} and state["quantity"] + quantity_delta < 0:
        raise ValueError("This would make stock negative. Count what is present or record a correction with an explanation.")
    if action in {"received", "starting"} and (quantity_delta <= 0 or unit_cost_cents is None or unit_cost_cents < 0):
        raise ValueError("A receipt needs a positive quantity and a non-negative unit purchase cost.")
    with db() as con:
        try:
            con.execute("""INSERT INTO inventory_transactions
                (item_id, action, quantity_delta, unit_cost_cents, occurred_at, recorded_by, note, request_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (item_id, action, quantity_delta, unit_cost_cents, utc_now(), recorded_by, note, request_id))
        except sqlite3.IntegrityError as error:
            if "request_id" in str(error):
                raise ValueError("That button press was already recorded; no duplicate transaction was added.") from error
            raise


def code_for_new_item():
    with db() as con:
        last = con.execute("SELECT scan_code FROM items WHERE scan_code LIKE 'PHO65-INV-%' ORDER BY scan_code DESC LIMIT 1").fetchone()
    number = int(last["scan_code"].rsplit("-", 1)[1]) + 1 if last else 101
    return f"PHO65-INV-{number:06d}"


BASE = """
<!doctype html><html><head><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Pho65 Inventory</title><style>
body{font-family:system-ui,sans-serif;max-width:980px;margin:1.2rem auto;padding:0 1rem;color:#17251f}nav{display:flex;gap:1rem;flex-wrap:wrap;border-bottom:2px solid #e5b95c;padding-bottom:.7rem}a{color:#075d51}table{border-collapse:collapse;width:100%}th,td{padding:.55rem;border-bottom:1px solid #ddd;text-align:left}.low{background:#fff0ed}.card{border:1px solid #d8ddd9;border-radius:8px;padding:1rem;margin:1rem 0}label{display:block;margin:.6rem 0}input,select,button{font:inherit;padding:.45rem}button{background:#075d51;color:white;border:0;border-radius:4px}.flash{padding:.65rem;background:#fff5cf}.hint{color:#52625b}.code{font-family:ui-monospace,monospace}</style></head>
<body><nav><a href='/inventory'>Inventory</a><a href='/inventory/scan'>Scan / look up</a><a href='/inventory/new'>New item + label</a><a href='/'>Week 3 orders</a></nav>
<!-- Week 5 Step 3: add <a href='/crm'>CRM co-pilot</a> to this nav bar once your /crm route exists below. -->
{% with messages=get_flashed_messages() %}{% for m in messages %}<p class=flash>{{m}}</p>{% endfor %}{% endwith %}{{ body|safe }}</body></html>
"""


def page(body, **context):
    return render_template_string(BASE, body=render_template_string(body, **context))


@app.route("/inventory")
def inventory():
    return page("""<h1>Pho65 mobile inventory</h1><p>Each number comes from replaying the transaction ledger. It is not an editable stock box.</p>
    <table><tr><th>Item</th><th>Scan code</th><th>On hand</th><th>Average cost</th><th>Value</th><th>Status</th></tr>
    {% for i in items %}<tr class='{{ "low" if i.low else "" }}'><td><a href='/inventory/item/{{i.id}}'>{{i.name}}</a></td><td class=code>{{i.scan_code}}</td><td>{{i.quantity}} {{i.base_unit}}</td><td>{{money(i.average_cents)}}</td><td>{{money(i.value_cents)}}</td><td>{{"LOW — review" if i.low else "OK"}}</td></tr>{% endfor %}</table>
    <p class=hint>Reference costing: receive 10 at $2.00, receive 10 at $2.50, then use 12. The remaining 8 have a moving average cost of $2.25 each and value $18.00.</p>""", items=all_items(), money=money)


@app.route("/inventory/lookup")
def lookup():
    code = request.args.get("code", "").strip().upper()
    with db() as con:
        item = con.execute("SELECT id FROM items WHERE scan_code=?", (code,)).fetchone()
    if item:
        return redirect(url_for("item_detail", item_id=item["id"]))
    return page("""<h1>Unknown code</h1><p><span class=code>{{code}}</span> is not in Pho65 inventory. Check the label, enter it manually, or create an internal item.</p><p><a href='/inventory/new?code={{code}}'>Create internal item safely</a></p>""", code=code or "(blank)")


@app.route("/inventory/scan")
def scan():
    return page("""<h1>Scan or type a code</h1><p>Use this page on the phone’s <strong>HTTPS ngrok URL</strong> for camera access. If permission is denied, scan an image file or type the code.</p>
    <div id=reader class=card></div><form action='/inventory/lookup'><label>Manual code <input name=code required autofocus></label><button>Look up</button></form>
    <p class=hint>Camera needs permission. This page never needs your ngrok authtoken.</p>
    <script src='https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'></script><script>
    function found(text){ location.assign('/inventory/lookup?code='+encodeURIComponent(text)); }
    if(window.Html5QrcodeScanner){new Html5QrcodeScanner('reader',{fps:10,qrbox:{width:240,height:240},formatsToSupport:[Html5QrcodeSupportedFormats.QR_CODE,Html5QrcodeSupportedFormats.UPC_A,Html5QrcodeSupportedFormats.EAN_13,Html5QrcodeSupportedFormats.CODE_128]},false).render(found,()=>{});}
    else { document.getElementById('reader').innerHTML='<p>Scanner library did not load. Use manual entry or try again with internet access.</p>'; }
    </script>""")


@app.route("/inventory/new", methods=["GET", "POST"])
def new_item():
    suggested = request.args.get("code", "") or code_for_new_item()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("scan_code", "").strip().upper()
        unit = request.form.get("base_unit", "each").strip().lower()
        try: point = int(request.form.get("reorder_point", "0"))
        except ValueError: point = -1
        if not name or not code.startswith("PHO65-INV-") or point < 0 or not unit:
            flash("Use a name, non-negative reorder point, unit, and a PHO65-INV internal code.")
        else:
            try:
                with db() as con: con.execute("INSERT INTO items (name,scan_code,code_kind,base_unit,reorder_point,created_at) VALUES (?,?,?,?,?,?)", (name, code, "internal", unit, point, utc_now()))
                flash("Internal item created. Print its label; it is not a retail UPC/EAN.")
                return redirect(url_for("item_detail", item_id=con.execute("SELECT id FROM items WHERE scan_code=?", (code,)).fetchone()["id"]))
            except sqlite3.IntegrityError: flash("That code already exists. Do not make a duplicate label.")
    return page("""<h1>New internal item</h1><p>For an item without a manufacturer code, Pho65 assigns an internal QR label. This is not a UPC/EAN and must say <strong>internal use only</strong>.</p><form method=post class=card><label>Name <input name=name required></label><label>Internal code <input class=code name=scan_code value='{{suggested}}' required></label><label>Base unit <input name=base_unit value=each required></label><label>Low-stock point <input type=number min=0 name=reorder_point value=0 required></label><button>Create and print label</button></form>""", suggested=suggested)


@app.route("/inventory/item/<int:item_id>")
def item_detail(item_id):
    with db() as con: item = con.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    if not item: abort(404)
    state = inventory_state(item_id)
    return page("""<h1>{{item.name}}</h1><p><span class=code>{{item.scan_code}}</span> · {{item.code_kind}} code · {{state.quantity}} {{item.base_unit}} on hand · average {{money(state.average_cents)}} · value {{money(state.value_cents)}}</p>
    {% if item.code_kind == 'internal' %}<p><a href='/inventory/label/{{item.id}}'>Print internal QR label</a></p>{% endif %}
    <form action='/inventory/transaction' method=post class=card><input type=hidden name=item_id value='{{item.id}}'><input type=hidden name=request_id value='{{request_id}}'><label>Action <select name=action><option value=received>Received (adds stock + cost)</option><option value=used>Used (removes stock)</option><option value=wasted>Wasted (removes stock)</option><option value=counted>Counted adjustment (+ or −)</option><option value=correction>Correction (+ or −, explain)</option></select></label><label>Quantity <input type=number name=quantity required> <span class=hint>Use a positive number for Received/Used/Wasted; signed adjustment for Counted/Correction.</span></label><label>Unit purchase cost (USD; receipt only) <input name=unit_cost placeholder='2.50'></label><label>Recorded by <input name=recorded_by required></label><label>Note / reason <input name=note></label><button>Record one ledger event</button></form>
    <h2>History</h2><table><tr><th>When</th><th>Action</th><th>Change</th><th>Cost</th><th>Who / note</th></tr>{% for t in state.transactions %}<tr><td>{{t.occurred_at}}</td><td>{{t.action}}</td><td>{{t.quantity_delta}}</td><td>{{money(t.unit_cost_cents) if t.unit_cost_cents is not none else '—'}}</td><td>{{t.recorded_by}} {{t.note}}</td></tr>{% endfor %}</table>""", item=item, state=state, money=money, request_id=str(uuid.uuid4()))


@app.post("/inventory/transaction")
def transaction():
    item_id, action = int(request.form["item_id"]), request.form["action"]
    raw_quantity = int(request.form["quantity"])
    quantity = -abs(raw_quantity) if action in {"used", "wasted"} else raw_quantity
    raw_cost = request.form.get("unit_cost", "").strip()
    try: cost = int((Decimal(raw_cost) * 100).quantize(Decimal("1"), ROUND_HALF_UP)) if raw_cost else None
    except Exception: cost = -1
    try:
        add_transaction(item_id, action, quantity, cost, request.form.get("recorded_by", "").strip(), request.form.get("note", "").strip(), request.form.get("request_id", ""))
        flash("Ledger event recorded once. Recheck the quantity and value below.")
    except (ValueError, sqlite3.Error) as error: flash(str(error))
    return redirect(url_for("item_detail", item_id=item_id))


@app.route("/inventory/label/<int:item_id>")
def label(item_id):
    with db() as con: item = con.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    if not item or item["code_kind"] != "internal": abort(404)
    qr = qrcode.make(item["scan_code"]).convert("RGB")
    label_height = 76
    image = Image.new("RGB", (qr.width, qr.height + label_height), "white")
    image.paste(qr, (0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((10, qr.height + 8), "PHO65 INTERNAL USE ONLY", fill="black")
    draw.text((10, qr.height + 30), item["scan_code"], fill="black")
    draw.text((10, qr.height + 52), "Not a retail UPC/EAN/GTIN", fill="black")
    output = io.BytesIO(); image.save(output, "PNG"); output.seek(0)
    return send_file(output, mimetype="image/png", download_name=f"{item['scan_code']}.png")


# Week 5 Step 3: add your own @app.route("/crm") here.
#
# It should call crm_copilot.run(CRM_SEED_CSV, as_of) (parse CRM_AS_OF into a
# datetime first) and render, at minimum: the narrative brief, the regulars
# table with the excluded-non-opted-in count, the capacity view with an
# over-capacity flag per bucket, the follow-up queue, and any draft messages
# (each one must read "DRAFT -- NOT SENT" -- never wire this to anything that
# actually sends). Don't forget to add the nav-bar link above once this route
# exists. Handle the case where the seed file can't be found (FileNotFoundError)
# with a clear message instead of a stack trace.


# A minimal Week 3 regression route is retained deliberately.
@app.route("/")
def orders():
    orders = []
    try:
        with open(ORDERS_CSV, newline="", encoding="utf-8") as source: orders = list(csv.DictReader(source))
    except FileNotFoundError: pass
    return page("""<h1>Pho65 order tracker (Week 3 regression)</h1><p>{{orders|length}} fixture orders still load. Week 4 adds inventory; it does not erase the earlier workflow.</p><p><a href='/inventory'>Open mobile inventory</a></p>""", orders=orders)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "inventory_db": DB_PATH})


init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
