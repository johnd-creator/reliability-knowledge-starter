"""Fixed read-only local collector API observations, never production source access.

No arbitrary endpoint, source authentication, pagination or value export. Missing
aggregate endpoint in an older collector stays UNKNOWN until reviewed deployment.
"""
from datetime import datetime, timezone
from urllib.parse import urlsplit
import json
import requests
from src.domain.integration_status import CollectorObservation, Availability

MAX_BYTES = 1_048_576

def _time(value):
    if not value: return None
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None: raise ValueError("ambiguous timestamp")
    return dt

class LocalCollectorObservations:
    def __init__(self, maximo_base=None, pi_base=None, *, session=None):
        self.maximo_base, self.pi_base = maximo_base, pi_base
        self.session = session or requests.Session()
        self._owns_session = session is None
        # Credentials from ambient .netrc/proxy configuration are not used here.
        self.session.trust_env = False

    def close(self):
        if self._owns_session: self.session.close()

    def _get(self, base, path):
        parsed = urlsplit(base)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("invalid collector API base")
        with self.session.get(base.rstrip("/")+path, timeout=(2, 5), stream=True, allow_redirects=False) as response:
            response.raise_for_status()
            if 300 <= response.status_code < 400: raise ValueError("collector redirect rejected")
            raw = bytearray()
            for chunk in response.iter_content(65536):
                raw.extend(chunk)
                if len(raw)>MAX_BYTES: raise ValueError("bounded observation exceeded")
            return json.loads(raw)

    def maximo(self):
        if not self.maximo_base: return CollectorObservation(availability=Availability.NOT_CONFIGURED)
        try:
            cursors=self._get(self.maximo_base,"/sync/status")
            runs=self._get(self.maximo_base,"/collect-runs?limit=100")
            if not isinstance(runs,list) or len(runs)>100: raise ValueError("invalid bounded runs")
            wo=[r for r in runs if r.get("object_structure")=="mxwodetail" and r.get("finished_at") and r.get("mode")!="recovery-floor"]
            wo.sort(key=lambda r: _time(r["finished_at"]), reverse=True)
            success=next((r for r in wo if r.get("errors")==0 and r.get("mode") in {"incremental","full"}),None)
            return CollectorObservation(availability=Availability.AVAILABLE,
                cursor_present=bool(cursors.get("mxwodetail",{}).get("watermark")),
                last_successful_activity=_time(success["finished_at"]) if success else None,
                latest_completed_at=_time(wo[0]["finished_at"]) if wo else None,
                errors=(wo[0].get("errors",0)+int(wo[0].get("mode")=="partial")) if wo else None)
        except (requests.RequestException, ValueError, TypeError, KeyError, AttributeError):
            return CollectorObservation(availability=Availability.UNAVAILABLE)

    def pi(self):
        if not self.pi_base: return CollectorObservation(availability=Availability.NOT_CONFIGURED)
        try:
            return CollectorObservation.model_validate(self._get(self.pi_base,"/integration-observation"))
        except (requests.RequestException, ValueError, TypeError):
            return CollectorObservation(availability=Availability.UNKNOWN)
