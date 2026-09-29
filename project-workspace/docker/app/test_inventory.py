"""Run inside the app image: python test_inventory.py."""
import os
import tempfile

temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
temp.close()
os.environ["INVENTORY_DB"] = temp.name

import app  # noqa: E402

app.init_db()
with app.db() as con:
    con.execute("INSERT INTO items (name,scan_code,code_kind,base_unit,reorder_point,created_at) VALUES (?,?,?,?,?,?)", ("Test noodles", "PHO65-INV-999999", "internal", "bag", 2, app.utc_now()))
    item_id = con.execute("SELECT id FROM items").fetchone()["id"]

app.add_transaction(item_id, "received", 10, 200, "test", "first receipt", "r1")
app.add_transaction(item_id, "received", 10, 250, "test", "second receipt", "r2")
app.add_transaction(item_id, "used", -12, None, "test", "service", "r3")
state = app.inventory_state(item_id)
assert (state["quantity"], state["average_cents"], state["value_cents"]) == (8, 225, 1800), state
label = app.app.test_client().get(f"/inventory/label/{item_id}")
assert label.status_code == 200 and label.mimetype == "image/png" and len(label.data) > 1000
try:
    app.add_transaction(item_id, "used", -1, None, "test", "duplicate", "r3")
except ValueError as error:
    assert "already recorded" in str(error)
else:
    raise AssertionError("duplicate request was accepted")
try:
    app.add_transaction(item_id, "used", -100, None, "test", "negative", "r4")
except ValueError as error:
    assert "negative" in str(error)
else:
    raise AssertionError("negative stock was accepted")
print("inventory known-answer and guard tests passed")
