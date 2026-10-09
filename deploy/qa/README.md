# Governed QA templates — default off


**NADI-E-INTEGRATION-02 selection:** local username/password is initial QA auth.
Enterprise SSO/Entra/OIDC registration is an optional future path, not an initial
activation prerequisite. Local account custody/onboarding and existing host/DB/
TLS/storage/PdM/UAT/explicit deployment gates remain. See local-authentication-v1
and the final integration report; historical enterprise-specific evidence below
remains reusable, not initial-QA authorization.

These templates belong to Bundle E and are not a deployed environment.
Use a separately approved project/network/host and QA-only credentials.
No collector, source connection or production override belongs here.

The template service only runs the source-free preflight; it cannot activate
Engineering endpoints. A future separately reviewed activation entrypoint must
inject the reviewed local account provider/durable directory, approved dedicated QA store,
SELECT-only factual reader and private storage/scanner. The existing public
cockpit serve command and disposable test server are NOT substitutes.

Copy qa-config.example.json to a private, owner-only location, fill operator
decisions and retain approved manifests outside Git. Validate source-free:
`python -m src.qa.preflight --config <private-config.json>` from cockpit source.
Placeholder input yields NO-GO, not a successful deployment.

Do not execute Docker Compose, host start/stop, DB provisioning, migrations,
account provisioning or secret acquisition here without explicit environment-bound
operator approval. E6 runbook contains the gated sequence.
