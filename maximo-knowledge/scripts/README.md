# Safe Discovery Scripts

Scripts in this folder must:

- use GET/HEAD/OPTIONS only
- default to dry-run where possible
- read credentials from environment variables
- never print secrets
- implement request timeout
- implement conservative rate limiting
- save sanitized metadata, not raw sensitive payloads

## Discovery CLI

`discover.py` is intentionally limited to `GET`, `HEAD`, and `OPTIONS`.
It can parse a local OAS fixture without network access and can fetch the
documented OAS or selected endpoint samples when `--execute` is explicit.

Examples:

```bash
python scripts/discover.py --oas-file /path/to/openapi.json --scope reliability-core
python scripts/discover.py --fetch-oas --execute --scope reliability-core
python scripts/discover.py --fetch-oas --execute --resource workorder
```

The production Maximo login form uses `POST /j_security_check`. The CLI does
not automate that POST because this repository forbids POST requests against
production. Configure an approved read-only bearer token for automated GETs,
or use a separately approved browser-assisted authentication flow.

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
