#!/usr/bin/env python3
"""Verify stream health for ALL BSR1 AF attributes (read-only GET /streams/{id}/value).

Classifies each attribute:
  ok       - stream responds 200
  gone     - 410 Gone (referenced PI Point deleted / no data reference)
  error    - other HTTP error
Writes pi-knowledge/discovery/stream-verification.json.
"""
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
RATE = 0.5
_last = 0.0


def check(web_id):
    global _last
    wait = RATE - (time.monotonic() - _last)
    if wait > 0:
        time.sleep(wait)
    r = requests.get(f"{BASE}/streams/{web_id}/value", auth=AUTH, timeout=30, verify=True)
    _last = time.monotonic()
    if r.status_code == 200:
        return "ok", None
    if r.status_code == 410:
        try:
            err = r.json().get("Errors", [""])[0]
        except Exception:
            err = r.text[:120]
        return "gone", err
    return "error", f"HTTP {r.status_code}: {r.text[:120]}"


records = json.load(open("/tmp/bsr1_walk_v2.json"))
results = []
counts = {"ok": 0, "gone": 0, "error": 0}
for i, r in enumerate(records, 1):
    status, detail = check(r["web_id"])
    counts[status] += 1
    results.append({
        "equipment": r["equipment"],
        "sub_element": r.get("sub_element"),
        "attribute": r["attribute"],
        "units": r["units"],
        "web_id": r["web_id"],
        "stream_status": status,
        "detail": detail,
    })
    if i % 50 == 0:
        print(f"  progress: {i}/{len(records)} ({counts})")

now = datetime.now(timezone.utc).isoformat(timespec="seconds")
out = {
    "system": "pi",
    "scope": "BSR > BSR1 all systems - stream health verification",
    "verified_at": now,
    "method": "GET /streams/{webId}/value per attribute (read-only)",
    "summary": counts,
    "attributes": results,
}
path = Path("discovery/stream-verification.json")
path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print(f"\nDONE {counts}")
print(f"wrote {path}")
