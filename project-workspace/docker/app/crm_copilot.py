"""Pho65 Week 5: CRM co-pilot -- regulars, capacity, follow-up, narrative brief.

Every function is pure (data in, data out) so it can be tested on its own and
reused from both the CLI and the Flask `/crm` route in app.py.

Consent boundary (load-bearing, do not relax): a record can only ever
contribute to `regular_status` when `opted_in` is true. There is no
send_email / send_sms / auto-dispatch function anywhere in this module --
draft messages are plain strings labeled DRAFT -- NOT SENT and nothing
transmits them.
"""
import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta

# Class defaults, kept as-is (justified in completed-workbook.md Section 1.3).
VISIT_FREQUENCY_THRESHOLD = 3      # visits...
VISIT_FREQUENCY_WINDOW_DAYS = 14   # ...within this many days => regular_status
LAPSED_WINDOW_DAYS = 21            # no visit in this many days => lapsed regular
CAPACITY_THRESHOLD = 2             # more than this many catering bookings...
SLOT_BUCKET_HOURS = 2              # ...in one bucket of this many hours => over capacity
CAPACITY_LOOKBACK_DAYS = 7         # the weekly view covers this week plus anything upcoming

DATE_FMT = "%Y-%m-%d"
SLOT_FMT = "%Y-%m-%d %H:%M"

REQUIRED_COLUMNS = {"record_id", "customer_name", "phone_number", "opted_in",
                    "visit_date", "order_type", "catering_slot"}
# A phone with fewer digits than this cannot identify anyone.
MIN_PHONE_DIGITS = 7


def _note(problems, message):
    if problems is not None:
        problems.append(message)


def normalize_phone(raw):
    """Digits only, so '555-203-0003' and '(555) 203-0003' key the same customer.

    This only fixes formatting. A wrong digit is a different number, on purpose.
    """
    digits = re.sub(r"\D", "", raw or "")
    return digits if len(digits) >= MIN_PHONE_DIGITS else ""


def load_records(csv_path, problems=None):
    """Load the seed CSV into a list of dicts with parsed types.

    Each dict has: record_id, customer_name, phone_number (str, possibly
    empty), phone_key (digits only, "" when there is no usable phone),
    opted_in (bool), visit_date (datetime), order_type (str), catering_slot
    (datetime or None if the row isn't a catering row).

    A row that can't be parsed is skipped and described in `problems`
    instead of crashing the page.
    """
    records = []
    with open(csv_path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"the seed file is missing column(s): {', '.join(sorted(missing))}")
        for line_no, row in enumerate(reader, start=2):
            field = lambda name: (row.get(name) or "").strip()
            record_id = field("record_id") or f"line {line_no}"
            try:
                visit_date = datetime.strptime(field("visit_date"), DATE_FMT)
            except ValueError:
                _note(problems, f"{record_id}: visit_date {field('visit_date')!r} is not YYYY-MM-DD, so the row was skipped.")
                continue
            phone = field("phone_number")
            phone_key = normalize_phone(phone)
            if phone and not phone_key:
                _note(problems, f"{record_id}: phone {phone!r} is too short to identify anyone, so the row counts as having no phone.")
            order_type = field("order_type").lower()
            catering_slot = None
            if order_type == "catering":
                try:
                    catering_slot = datetime.strptime(field("catering_slot"), SLOT_FMT)
                except ValueError:
                    _note(problems, f"{record_id}: catering row has catering_slot {field('catering_slot')!r}, so it is left out of the capacity view.")
            records.append({
                "record_id": record_id,
                "customer_name": field("customer_name"),
                "phone_number": phone,
                "phone_key": phone_key,
                # Consent must be explicit: only the word "true" counts.
                "opted_in": field("opted_in").lower() == "true",
                "visit_date": visit_date,
                "order_type": order_type,
                "catering_slot": catering_slot,
            })
    return records


def load_phone_crosswalk(path, problems=None):
    """Read phone corrections: lines of wrong_phone,correct_phone[,note].

    Blank lines and #comments are ignored. A missing file means "no
    corrections", so the co-pilot still runs on the raw data.
    """
    try:
        with open(path, newline="", encoding="utf-8-sig") as source:
            lines = [line for line in source if line.strip() and not line.lstrip().startswith("#")]
    except FileNotFoundError:
        _note(problems, f"Phone-fix file {path} was not found, so no phone corrections were applied.")
        return {}
    except (OSError, UnicodeDecodeError) as error:
        _note(problems, f"Phone-fix file {path} could not be read ({error.__class__.__name__}), so no phone corrections were applied.")
        return {}
    crosswalk = {}
    reader = csv.DictReader(lines)
    if lines and not {"wrong_phone", "correct_phone"} <= set(reader.fieldnames or []):
        _note(problems, f"Phone-fix file {path} must start with the header line wrong_phone,correct_phone,note; no corrections were applied.")
        return {}
    for row in reader:
        wrong = normalize_phone(row.get("wrong_phone"))
        right = normalize_phone(row.get("correct_phone"))
        if wrong and right and wrong != right:
            crosswalk[wrong] = right
        else:
            _note(problems, f"Phone correction {row.get('wrong_phone')!r} -> {row.get('correct_phone')!r} is not usable and was ignored.")
    # One hop only: a number that is both a "wrong" and a "correct" number
    # would make the result depend on line order, so those lines are dropped.
    chained = {wrong for wrong, right in crosswalk.items() if right in crosswalk}
    for wrong in sorted(chained):
        _note(problems, f"Phone correction for {wrong} points at a number that is itself being corrected; ignored.")
    return {wrong: right for wrong, right in crosswalk.items() if wrong not in chained}


def apply_phone_crosswalk(records, crosswalk):
    """Re-key mistyped phone numbers before grouping (the Week 5 Step 5 fix).

    A row is moved to the correct number only when its customer name already
    appears on that number, so a wrong crosswalk line cannot merge two
    different people. Returns (records, applied, refused).
    """
    names_on, display = defaultdict(set), {}
    for record in records:
        names_on[record["phone_key"]].add(record["customer_name"].casefold())
        display.setdefault(record["phone_key"], record["phone_number"])
    fixed, applied, refused = [], [], []
    for record in records:
        target = crosswalk.get(record["phone_key"])
        if target and record["customer_name"].casefold() in names_on.get(target, set()):
            corrected = {**record, "phone_key": target, "phone_number": display[target],
                         "phone_corrected_from": record["phone_number"]}
            fixed.append(corrected)
            applied.append(corrected)
        else:
            if target:
                refused.append(record)
            fixed.append(record)
    return fixed, applied, refused


def possible_duplicates(records):
    """Names that appear under more than one phone number (after any
    corrections): a hint for staff to check for a typo. Nothing is merged
    automatically -- two different people can share a name."""
    keys, shown, names = defaultdict(set), {}, {}
    for record in records:
        if record["phone_key"] and record["customer_name"]:
            name = record["customer_name"].casefold()
            keys[name].add(record["phone_key"])
            names[name] = record["customer_name"]
            shown.setdefault(record["phone_key"], record["phone_number"])
    return [{"name": names[name], "phones": sorted(shown[key] for key in found)}
            for name, found in sorted(keys.items()) if len(found) > 1]


def eligible_records(records):
    """Return only records that may ever be considered for regular_status.

    Consent-first rule: a record is eligible only if it has a phone number
    AND opted_in is true. Everything else is "not eligible," never "not a
    regular" -- do not silently treat exclusion as a negative computation.
    """
    return [r for r in records if r["phone_key"] and r["opted_in"]]


def group_by_phone(records):
    """Group a list of records into {phone_key: [records]}; rows with no phone are left out."""
    groups = defaultdict(list)
    for record in records:
        if record["phone_key"]:
            groups[record["phone_key"]].append(record)
    return dict(groups)


def has_three_in_window(visit_dates, window_days=VISIT_FREQUENCY_WINDOW_DAYS,
                        threshold=VISIT_FREQUENCY_THRESHOLD):
    """Return True if any window_days-wide window contains >= threshold visits.

    A visit is a distinct calendar day, so lunch and dinner on the same day
    count once. "3 in 14 days" means the first and third visit both fall in
    one 14-day calendar window, e.g. Jan 1 and Jan 14 (13 days apart).
    """
    days = sorted({d.date() if isinstance(d, datetime) else d for d in visit_dates})
    if threshold <= 0:
        return True
    for i in range(len(days) - threshold + 1):
        if (days[i + threshold - 1] - days[i]).days < window_days:
            return True
    return False


def compute_regular_status(records, as_of):
    """Compute regular_status per phone number.

    Returns (result, excluded_non_opted_in) where result is
    {phone_key: {name, phone_number, visit_count, last_visit, is_regular,
    record_ids}} and excluded_non_opted_in is the list of non-opted-in
    records that would have satisfied the frequency rule anyway (the
    consent-leakage check -- deliberately narrower than "every
    opted_in=false record").

    Matching rule: same phone number, and opted_in=true on the most recent
    record for that number. Only opted-in rows are counted as visits.
    Visits after `as_of` are ignored.
    """
    result, excluded = {}, []
    past = [r for r in records if r["visit_date"] <= as_of]
    for key, rows in group_by_phone(past).items():
        rows = sorted(rows, key=lambda r: (r["visit_date"], r["record_id"]))
        latest = rows[-1]
        consented = [r for r in rows if r["opted_in"]] if latest["opted_in"] else []
        would_qualify = has_three_in_window([r["visit_date"] for r in rows])
        qualifies = has_three_in_window([r["visit_date"] for r in consented])
        if would_qualify and not qualifies:
            excluded.extend(r for r in rows if not r["opted_in"])
        if not consented:
            continue  # not eligible -- never recorded as "not a regular"
        result[key] = {
            "name": latest["customer_name"],
            "phone_number": latest["phone_number"],
            "visit_count": len({r["visit_date"].date() for r in consented}),
            "last_visit": consented[-1]["visit_date"],
            "is_regular": qualifies,
            "record_ids": [r["record_id"] for r in consented],
        }
    return result, excluded


def lapsed_followup_queue(regular_status, as_of, lapsed_days=LAPSED_WINDOW_DAYS):
    """Return customers who WERE flagged regular and haven't visited in lapsed_days+."""
    queue = []
    for key, customer in regular_status.items():
        if not customer["is_regular"]:
            continue
        days_since = (as_of.date() - customer["last_visit"].date()).days
        if days_since >= lapsed_days:
            queue.append({**customer, "phone_key": key, "days_since_visit": days_since})
    return sorted(queue, key=lambda c: (-c["days_since_visit"], c["name"]))


def slot_bucket(dt, bucket_hours=SLOT_BUCKET_HOURS):
    """Round a datetime down to its bucket_hours-wide window, anchored at midnight."""
    if not 0 < bucket_hours <= 24 or 24 % bucket_hours:
        raise ValueError("bucket_hours must divide a day evenly (1, 2, 3, 4, 6, 8, 12 or 24)")
    return dt.replace(hour=dt.hour // bucket_hours * bucket_hours, minute=0, second=0, microsecond=0)


def capacity_view(records, threshold=CAPACITY_THRESHOLD):
    """Return a list of {bucket_start, count, over_capacity, records} for catering rows.

    Capacity is about the kitchen, not marketing, so every catering booking
    counts here whether or not that customer opted in.
    """
    buckets = defaultdict(list)
    for record in records:
        if record["order_type"] == "catering" and record["catering_slot"]:
            buckets[slot_bucket(record["catering_slot"])].append(record)
    view = []
    for start in sorted(buckets):
        rows = sorted(buckets[start], key=lambda r: (r["catering_slot"], r["record_id"]))
        view.append({
            "bucket_start": start,
            "bucket_end": start + timedelta(hours=SLOT_BUCKET_HOURS),
            "count": len(rows),
            "over_capacity": len(rows) > threshold,
            "records": rows,
        })
    return view


def suggest_alternate_slot(capacity, over_capacity_bucket, threshold=CAPACITY_THRESHOLD):
    """Return the same-day bucket with the lowest booking count, excluding the overbooked one.

    Only windows that already took a catering booking that day are offered,
    because the seed data has no opening hours: a window nobody has ever
    booked (say 02:00) is not a real option. The suggestion must also have
    room for one more booking. Ties go to the window closest in time.
    Returns None when no same-day window has room.
    """
    start = over_capacity_bucket["bucket_start"]
    candidates = [b for b in capacity
                  if b["bucket_start"].date() == start.date()
                  and b["bucket_start"] != start
                  and b["count"] + 1 <= threshold]
    if not candidates:
        return None
    return min(candidates, key=lambda b: (b["count"], abs(b["bucket_start"] - start)))


DRAFT_LABEL = "DRAFT -- NOT SENT"


def draft_body(draft):
    """The customer-facing part of a draft: everything after the first blank
    line. Used by the Copy button so the label and the internal reason
    never get pasted into a real message."""
    return draft.split("\n\n", 1)[-1]


def draft_message(customer_name, reason):
    """Return a labeled draft string. NEVER send it -- do not add a transport call here."""
    first_name = (customer_name or "").split()[0] if (customer_name or "").split() else "there"
    return (
        f"{DRAFT_LABEL}\n"
        f"For staff to review: {customer_name} ({reason})\n"
        "\n"
        f"Hi {first_name}, it's been a little while since we've seen you at Pho65, "
        "and we hope you're doing well. We'd love to have you back for a bowl soon. "
        "If you'd rather not hear from us, just let us know.\n"
        "- The Pho65 team"
    )


def clock(dt):
    """'18:00' -> '6 PM', '14:30' -> '2:30 PM'."""
    hour = dt.hour % 12 or 12
    suffix = "AM" if dt.hour < 12 else "PM"
    return f"{hour} {suffix}" if dt.minute == 0 else f"{hour}:{dt.minute:02d} {suffix}"


def window_label(bucket):
    start = bucket["bucket_start"]
    return f"{start.strftime('%A %b')} {start.day}, {clock(start)}–{clock(bucket['bucket_end'])}"


def _names(names):
    names = list(names)
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def _plural(count, word, plural=None):
    return f"{count} {word if count == 1 else (plural or word + 's')}"


def narrative_brief(regular_status, followup_queue, capacity, as_of,
                    excluded_non_opted_in=(), threshold=CAPACITY_THRESHOLD):
    """Return one plain-language paragraph summarizing regulars, follow-ups, and capacity."""
    regulars = sorted(c["name"] for c in regular_status.values() if c["is_regular"])
    sentences = [f"Week ending {as_of.strftime('%A, %B')} {as_of.day}, {as_of.year}:"]
    if regulars:
        sentences.append(f"{_plural(len(regulars), 'customer')} {'counts' if len(regulars) == 1 else 'count'} "
                         f"as {'a regular' if len(regulars) == 1 else 'regulars'} ({_names(regulars)}).")
    else:
        sentences.append("No customer counts as a regular yet.")
    if followup_queue:
        who = _names(f"{c['name']} (last visit {c['last_visit'].strftime('%b')} {c['last_visit'].day}, "
                     f"{c['days_since_visit']} days ago)" for c in followup_queue)
        sentences.append(f"{_plural(len(followup_queue), 'regular')} may be drifting away: {who}. "
                         f"A draft follow-up is ready for you to read; nothing has been sent.")
    else:
        sentences.append(f"No regular has gone {LAPSED_WINDOW_DAYS} or more days without a visit.")
    conflicts = [b for b in capacity if b["over_capacity"]]
    for bucket in conflicts:
        alternate = suggest_alternate_slot(capacity, bucket, threshold)
        sentence = (f"Catering on {window_label(bucket)} has {bucket['count']} bookings, "
                    f"more than the kitchen limit of {threshold}")
        if alternate:
            overflow = bucket["count"] - threshold
            move = min(overflow, threshold - alternate["count"])
            sentence += (f"; {clock(alternate['bucket_start'])}–{clock(alternate['bucket_end'])} the same day has only "
                         f"{_plural(alternate['count'], 'booking')}, so offer that time to "
                         f"{_plural(move, 'booking')} from the busy window")
            sentence += "." if move == overflow else f", and call the other {_plural(overflow - move, 'customer')} before accepting more."
        else:
            sentence += "; no other window that day has room, so call the customers before accepting more."
        sentences.append(sentence)
    if not conflicts:
        sentences.append("No catering window is over the limit.")
    quiet = [b for b in capacity if not b["over_capacity"]]
    if quiet:
        sentences.append("Slow catering windows with room to spare: "
                         + _names(f"{window_label(b)} ({_plural(b['count'], 'booking')})" for b in quiet) + ".")
    excluded_people = {r["phone_key"] for r in excluded_non_opted_in}
    if excluded_people:
        sentences.append(f"{_plural(len(excluded_people), 'customer')} who visited often but did not agree to be "
                         f"contacted {'was' if len(excluded_people) == 1 else 'were'} left out on purpose.")
    return " ".join(sentences)


def run(csv_path, as_of, crosswalk_path=None):
    """Wire the pieces above together. Returns a dict with all the fields the
    /crm route needs to render: regular_status, excluded_non_opted_in_count,
    excluded_non_opted_in, followup_queue, capacity, drafts, narrative_brief.

    crosswalk_path=None runs on the raw data (the Step 5 "before fix" view).
    """
    problems = []
    records = load_records(csv_path, problems)
    applied, refused = [], []
    if crosswalk_path:
        crosswalk = load_phone_crosswalk(crosswalk_path, problems)
        records, applied, refused = apply_phone_crosswalk(records, crosswalk)
        for record in refused:
            _note(problems, f"{record['record_id']}: phone correction for {record['customer_name']} was not applied, "
                            "because no record with that name is on the corrected number.")
    duplicates = possible_duplicates(records)
    regular_status, excluded = compute_regular_status(records, as_of)
    queue = lapsed_followup_queue(regular_status, as_of)
    window_start = as_of - timedelta(days=CAPACITY_LOOKBACK_DAYS - 1)
    capacity = capacity_view([r for r in records if r["catering_slot"] and r["catering_slot"].date() >= window_start.date()])
    older_catering = sum(1 for r in records if r["catering_slot"] and r["catering_slot"].date() < window_start.date())
    conflicts = []
    for bucket in capacity:
        if bucket["over_capacity"]:
            alternate = suggest_alternate_slot(capacity, bucket)
            overflow = bucket["count"] - CAPACITY_THRESHOLD
            room = CAPACITY_THRESHOLD - alternate["count"] if alternate else 0
            conflicts.append({"bucket": bucket, "alternate": alternate, "overflow": overflow,
                              "room": room, "move": min(overflow, room)})
    drafts = []
    for c in queue:
        text = draft_message(c["name"], f"regular, last visit {c['last_visit'].strftime(DATE_FMT)}, "
                                        f"{c['days_since_visit']} days ago")
        drafts.append({"name": c["name"], "text": text, "body": draft_body(text)})
    past_with_phone = [r for r in records if r["phone_key"] and r["visit_date"] <= as_of]
    return {
        "as_of": as_of,
        "record_count": len(records),
        "regular_status": regular_status,
        "excluded_non_opted_in": excluded,
        "excluded_non_opted_in_count": len(excluded),
        "excluded_customer_count": len({r["phone_key"] for r in excluded}),
        "not_eligible_no_phone": [r for r in records if not r["phone_key"]],
        # Not opted in, or opted in earlier but withdrew on the latest record.
        "not_eligible_not_opted_in": [r for r in past_with_phone
                                      if not r["opted_in"] or r["phone_key"] not in regular_status],
        "followup_queue": queue,
        "capacity": capacity,
        "capacity_from": window_start,
        "older_catering_count": older_catering,
        "conflicts": conflicts,
        "drafts": drafts,
        "narrative_brief": narrative_brief(regular_status, queue, capacity, as_of, excluded),
        "problems": problems,
        "corrections_on": bool(crosswalk_path),
        "corrections_applied": applied,
        "possible_duplicates": duplicates,
    }


if __name__ == "__main__":
    import sys
    from pprint import pprint
    path = sys.argv[1] if len(sys.argv) > 1 else "/data/pho65-week5-seed.csv"
    as_of = datetime.strptime(sys.argv[2], DATE_FMT) if len(sys.argv) > 2 else datetime(2026, 2, 15)
    crosswalk = sys.argv[3] if len(sys.argv) > 3 else None
    result = run(path, as_of, crosswalk)
    print(result["narrative_brief"], "\n")
    print("Regular status:")
    pprint({c["name"] + " " + c["phone_number"]: (c["visit_count"], c["last_visit"].strftime(DATE_FMT), c["is_regular"])
            for c in result["regular_status"].values()})
    print("Follow-up queue:", [(c["name"], c["days_since_visit"]) for c in result["followup_queue"]])
    print("Excluded (no consent):", [r["record_id"] for r in result["excluded_non_opted_in"]])
    print("Capacity:", [(b["bucket_start"].strftime(SLOT_FMT), b["count"], b["over_capacity"]) for b in result["capacity"]])
    for draft in result["drafts"]:
        print("\n" + draft["text"])
