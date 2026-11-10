"""Append a story to posted.json: python engine/log_post.py <slug> <YYYY-MM-DD>"""
import json, os, sys
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "posted.json")
data = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []
slug, day = sys.argv[1], sys.argv[2]
if not any(e["slug"] == slug for e in data):
    data.append({"date": day, "slug": slug})
json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(data)} stories logged")
