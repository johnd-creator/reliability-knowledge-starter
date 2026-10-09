# Governed QA templates — default off

These templates belong to Bundle E and are not a deployed environment.
Use a separately approved project/network/host and QA-only credentials.
No collector, source connection or production override belongs here.

The template service only runs the source-free preflight; it cannot activate
Engineering endpoints. A future separately reviewed activation entrypoint must
inject an enterprise verifier/durable directory, approved dedicated QA store,
SELECT-only factual reader and private storage/scanner. The existing public
cockpit serve command and disposable test server are NOT substitutes.

Copy qa-config.example.json to a private, owner-only location, fill operator
decisions and retain approved manifests outside Git. Validate source-free:
`python -m src.qa.preflight --config <private-config.json>` from cockpit source.
Placeholder input yields NO-GO, not a successful deployment.

Do not execute Docker Compose, host start/stop, DB provisioning, migrations,
IdP registration or secret acquisition here without explicit environment-bound
operator approval. E6 runbook contains the gated sequence.
