"""Synthetic source only. Real guarded client/boundary, fake HTTP session.

Executable handoff fixture for cross-project E2E without importing conflicting
src packages or contacting any network. Never used by production CLI.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from datetime import datetime, timezone
from dataclasses import replace
from unittest.mock import patch
import requests
from src.adapters.pi.client import PiClient
from src.config import PiApiConfig
from src.services.governed_source import GovernedSourceBoundary
from src.services.condition_evidence import collect_condition_evidence

NOW = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
BASE = "https://pi.synthetic.invalid/piwebapi"

class SyntheticSession:
    def __init__(self, plan, variants):
        self.plan, self.variants, self.calls = plan, variants, []

    def request(self, method, url, **kwargs):
        assert method == "GET" and url.startswith(BASE + "/") and not kwargs.get("auth")
        self.calls.append((method, url, kwargs.get("params")))
        lineage = self.plan["sources"]["pi"]
        element, database, server = [lineage[f] for f in ("af_element_ref", "af_database_ref", "af_server_ref")]
        path = url[len(BASE):]
        attrs = {s["sources"]["pi"]["attribute_ref"]: s for s in self.plan["signals"]}
        if path == "/elements/" + element:
            payload = {"WebId": element, "Links": {"Database": BASE + "/assetdatabases/" + database}}
        elif path == "/assetdatabases/" + database:
            payload = {"WebId": database, "Links": {"AssetServer": BASE + "/assetservers/" + server}}
        elif path == "/elements/" + element + "/attributes":
            payload = {"Items": [{"WebId": ref, "Links": {"Element": BASE + "/elements/" + element}} for ref in attrs] +
                       [{"WebId": "UNSELECTED_SYNTHETIC", "Links": {"Element": BASE + "/elements/" + element}}]}
        elif path.startswith("/attributes/"):
            ref = path.split("/")[-1]
            payload = {"WebId": ref, "Name": "Synthetic attribute " + ref, "DefaultUnitsName": "A",
                       "Links": {"Element": BASE + "/elements/" + element, "Value": BASE + "/streams/" + ref + "/value"}}
        elif path.startswith("/streams/") and path.endswith("/value"):
            ref = path.split("/")[-2]
            variant = self.variants.get(attrs[ref]["semantic_name"], {})
            if variant.get("unavailable"):
                raise requests.exceptions.Timeout("synthetic secret must not escape")
            payload = {"Timestamp": NOW.isoformat(), "Value": 12.5, "Good": True,
                       "Questionable": False, "Substituted": False, "Annotated": False, "UnitsAbbreviation": "A"}
            payload.update(variant)
        else:
            raise AssertionError("unexpected source path " + path)
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps(payload).encode()
        response._content_consumed = True
        return response

class SyntheticBoundary(GovernedSourceBoundary):
    def get_evidence_snapshot(self, target, ref):
        name, snapshot = super().get_evidence_snapshot(target, ref)
        return name, replace(snapshot, collected_at=NOW)

def fixture_batch(plan, variants=None):
    session = SyntheticSession(plan, variants or {})
    boundary = SyntheticBoundary(PiClient(PiApiConfig(base_url=BASE), session=session))
    # Preserve production request floor; only the synthetic test clock skips waiting.
    with patch("src.adapters.pi.client.time.sleep"):
        document = collect_condition_evidence(boundary, plan, collector_last_success_at=NOW)
    return document, session.calls

if __name__ == "__main__":
    request = json.load(sys.stdin)
    batch, calls = fixture_batch(request["plan"], request.get("variants"))
    print(json.dumps({"batch": batch, "synthetic_gets": len(calls), "paths": [c[1] for c in calls]}))
