#!/usr/bin/env python3
"""Re-walk BSR1 AF hierarchy and collect fresh WebIds (read-only, rate-limited)."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

for line in Path(".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

BASE = os.environ["PI_WEB_API_BASE_URL"].rstrip("/")
AUTH = (os.environ["PI_USERNAME"], os.environ["PI_PASSWORD"])
RATE = 0.7
_last = 0.0


def get(path, **params):
    global _last
    wait = RATE - (time.monotonic() - _last)
    if wait > 0:
        time.sleep(wait)
    r = requests.get(BASE + path, auth=AUTH, params=params, timeout=30, verify=True)
    _last = time.monotonic()
    r.raise_for_status()
    return r.json()


def get_elements(wid, maxc=200):
    return get(f"/elements/{wid}/elements", maxCount=str(maxc)).get("Items", [])


def get_attributes(wid, maxc=200):
    return get(f"/elements/{wid}/attributes", maxCount=str(maxc)).get("Items", [])


now = datetime.now(timezone.utc).isoformat(timespec="seconds")
srv = get("/assetservers")["Items"][0]
db = next(d for d in get(f"/assetservers/{srv['WebId']}/assetdatabases")["Items"] if d["Name"] == "Indonesia Power Corporate")
els = get(f"/assetdatabases/{db['WebId']}/elements", maxCount="100")["Items"]
bsr = next(e for e in els if e["Name"] == "BSR")
bsr1 = get_elements(bsr["WebId"])[0]
print("BSR1:", bsr1["Name"])
systems = get_elements(bsr1["WebId"])
print("systems:", [s["Name"] for s in systems])

all_records = []


def record(sys_el, equipment, a, sub_element=None):
    all_records.append({
        "system_name": sys_el["Name"],
        "equipment": equipment,
        "sub_element": sub_element,
        "attribute": a.get("Name"),
        "units": a.get("DefaultUnitsName"),
        "type": a.get("Type"),
        "web_id": a.get("WebId"),
    })


for sys_el in systems:
    print(f"--- {sys_el['Name']} ---")
    for a in get_attributes(sys_el["WebId"]):
        record(sys_el, sys_el["Name"], a)
    for kid in get_elements(sys_el["WebId"]):
        for a in get_attributes(kid["WebId"]):
            record(sys_el, kid["Name"], a)
        for sub in get_elements(kid["WebId"]):
            for a in get_attributes(sub["WebId"]):
                record(sys_el, kid["Name"], a, sub_element=sub["Name"])

print(f"\nTOTAL: {len(all_records)} attributes under BSR1")
out = Path("/tmp/bsr1_walk_v2.json")
out.write_text(json.dumps(all_records, indent=2, ensure_ascii=False))
print(f"wrote {out}")
