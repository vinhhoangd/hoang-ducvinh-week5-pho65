"""Pho65 Week 5: CRM co-pilot -- regulars, capacity, follow-up, narrative brief.

Starter skeleton. Your team implements the function bodies below. Keep every
function pure (data in, data out) so it's easy to test and reuse from both
the CLI and the Flask `/crm` route you will add to app.py.

Consent boundary (load-bearing, do not relax): a record can only ever
contribute to `regular_status` when `opted_in` is true. Do not add a
send_email / send_sms / auto-dispatch function anywhere in this module --
draft messages must be plain strings labeled DRAFT -- NOT SENT and nothing
may transmit them.
"""
import csv
from collections import defaultdict
from datetime import datetime, timedelta

# Class defaults -- justify your own values in the workbook if you change these.
VISIT_FREQUENCY_THRESHOLD = 3      # visits...
VISIT_FREQUENCY_WINDOW_DAYS = 14   # ...within this many days => regular_status
LAPSED_WINDOW_DAYS = 21            # no visit in this many days => lapsed regular
CAPACITY_THRESHOLD = 2             # more than this many catering bookings...
SLOT_BUCKET_HOURS = 2              # ...in one bucket of this many hours => over capacity

DATE_FMT = "%Y-%m-%d"
SLOT_FMT = "%Y-%m-%d %H:%M"


def load_records(csv_path):
    """Load the seed CSV into a list of dicts with parsed types.

    Each dict should have: record_id, customer_name, phone_number (str,
    possibly empty), opted_in (bool), visit_date (datetime), order_type
    (str), catering_slot (datetime or None if the row isn't a catering row).
    """
    raise NotImplementedError("Parse the CSV with csv.DictReader and convert types.")


def eligible_records(records):
    """Return only records that may ever be considered for regular_status.

    Consent-first rule: a record is eligible only if it has a phone number
    AND opted_in is true. Everything else is "not eligible," never "not a
    regular" -- do not silently treat exclusion as a negative computation.
    """
    raise NotImplementedError


def group_by_phone(records):
    """Group a list of records into {phone_number: [records]}."""
    raise NotImplementedError


def has_three_in_window(visit_dates, window_days=VISIT_FREQUENCY_WINDOW_DAYS,
                         threshold=VISIT_FREQUENCY_THRESHOLD):
    """Return True if any window_days-wide window contains >= threshold visits."""
    raise NotImplementedError


def compute_regular_status(records, as_of):
    """Compute regular_status per phone number.

    Returns (result, excluded_non_opted_in) where result is
    {phone_number: {name, visit_count, last_visit, is_regular}} and
    excluded_non_opted_in is the list of non-opted-in records that would
    have satisfied the frequency rule anyway (the consent-leakage check --
    this is deliberately narrower than "every opted_in=false record").
    """
    raise NotImplementedError


def lapsed_followup_queue(regular_status, as_of, lapsed_days=LAPSED_WINDOW_DAYS):
    """Return customers who WERE flagged regular and haven't visited in lapsed_days+."""
    raise NotImplementedError


def slot_bucket(dt, bucket_hours=SLOT_BUCKET_HOURS):
    """Round a datetime down to its bucket_hours-wide window, anchored at midnight."""
    raise NotImplementedError


def capacity_view(records, threshold=CAPACITY_THRESHOLD):
    """Return a list of {bucket_start, count, over_capacity, records} for catering rows."""
    raise NotImplementedError


def suggest_alternate_slot(capacity, over_capacity_bucket):
    """Return the same-day bucket with the lowest booking count, excluding the overbooked one."""
    raise NotImplementedError


def draft_message(customer_name, reason):
    """Return a labeled draft string. NEVER send it -- do not add a transport call here."""
    raise NotImplementedError


def narrative_brief(regular_status, followup_queue, capacity, as_of):
    """Return one plain-language paragraph summarizing regulars, follow-ups, and capacity."""
    raise NotImplementedError


def run(csv_path, as_of):
    """Wire the pieces above together. Returns a dict with all the fields the
    /crm route needs to render: regular_status, excluded_non_opted_in_count,
    excluded_non_opted_in, followup_queue, capacity, drafts, narrative_brief.
    """
    raise NotImplementedError


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "/data/pho65-week5-seed.csv"
    as_of = datetime.strptime(sys.argv[2], DATE_FMT) if len(sys.argv) > 2 else datetime(2026, 2, 15)
    result = run(path, as_of)
    print(result)
