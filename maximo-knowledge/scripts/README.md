# Safe Discovery Scripts

Scripts in this folder must:

- use GET/HEAD/OPTIONS for business resources; the only POST exception is the
  exact authentication handshake at `/j_security_check`
- default to dry-run where possible
- read credentials from environment variables
- never print secrets
- implement request timeout
- implement conservative rate limiting
- save sanitized metadata, not raw sensitive payloads

## Discovery CLI

`discover.py` is intentionally limited to `GET`, `HEAD`, and `OPTIONS` for
business resources. With `--execute` and form/login mode it may perform one
controlled authentication POST to the exact `/j_security_check` endpoint,
then it fetches the documented OAS or selected endpoint samples read-only.

Examples:

```bash
python scripts/discover.py --oas-file /path/to/openapi.json --scope reliability-core
python scripts/discover.py --fetch-oas --execute --scope reliability-core
python scripts/discover.py --fetch-oas --execute --resource workorder
# Bounded one-level detail verification: one BSR-scoped collection record and
# at most one same-origin detail GET per selected resource.
python scripts/discover.py --enumerate-oslc --verify-detail --execute \
  --resource IPFMEA --resource IPRCFA
```

The production Maximo login form uses `POST /j_security_check`. In form/login
mode the CLI submits that authentication handshake once using environment-only
credentials and keeps cookies in memory. It never POSTs to OSLC or another
business resource. Configure an approved read-only bearer token when available,
or use the separately approved browser-assisted authentication flow.

## Browser-session discovery

For the Maximo form-login flow, run the interactive session CLI locally:

```bash
python scripts/session_discover.py run --scope reliability-core --verify-samples
```

The CLI opens Chromium, waits for the operator to complete login manually,
then uses the in-memory browser context for OAS and GET-only sample requests.
It never writes browser storage state. Results are staged under
`discovery/runs/<timestamp>/` and do not overwrite the main catalog.

Install the browser dependency once:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```
