"""Jejak Kisah posting slots: two per day, 12:00 and 19:00 WIB (Asia/Jakarta).

  python3 brands/jejak-kisah/tools/slot.py next          → the next free slot, e.g. "2026-11-22 12:00"
  python3 brands/jejak-kisah/tools/slot.py log <slug> "<YYYY-MM-DD HH:MM>"   → record a scheduled video

A slot is free when posted.json has no entry for it. "next" skips slots less than 30 minutes from now.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
SLOTS = ["12:00", "19:00"]
POSTED = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posted.json")


def load():
    return json.load(open(POSTED, encoding="utf-8")) if os.path.exists(POSTED) else []


def next_free(now=None):
    now = now or datetime.now(WIB)
    taken = {e["slot"] for e in load()}
    day = now.date()
    for _ in range(60):
        for hm in SLOTS:
            h, m = map(int, hm.split(":"))
            at = datetime(day.year, day.month, day.day, h, m, tzinfo=WIB)
            key = at.strftime("%Y-%m-%d %H:%M")
            if at - now >= timedelta(minutes=30) and key not in taken:
                return key
        day += timedelta(days=1)
    raise SystemExit("no free slot in the next 60 days")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "next"
    if cmd == "next":
        print(next_free())
    elif cmd == "log":
        slug, slot = sys.argv[2], sys.argv[3]
        data = load()
        if any(e["slug"] == slug for e in data):
            raise SystemExit(f"{slug} is already logged")
        if any(e["slot"] == slot for e in data):
            raise SystemExit(f"slot {slot} is already taken")
        data.append({"slot": slot, "slug": slug})
        data.sort(key=lambda e: e["slot"])
        json.dump(data, open(POSTED, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"{len(data)} videos logged")
    else:
        raise SystemExit(__doc__)
