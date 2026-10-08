# ADR 007 — source facts and NADI-owned human records

Status: Bundle B candidate; 9 October 2026. Baseline main/PR29 merge
`02e887c56057611f112b7b652ba9a9aee8b382ea`.

Maximo business objects and PI are strictly READ ONLY. NADI cannot create,
update, approve, assign, schedule, close or cancel any Maximo Work Order.
An informational existing-WO reference is never a command or maintenance approval.
No source write credentials or privilege may be introduced. The existing controlled
Maximo authentication handshake is not a business-data write and is not run here.

Collectors retain source acquisition, normalization, cursors and projections.
The existing Reliability Mart remains collector-owned in the Maximo database.
Engineering Cases, manual inspections, review decisions and recommendations belong
only to the EXISTING separate Cockpit application store, with deliberately
provisioned least-privilege writer authority. No new operational database.
Application services use injected repositories and local SELECT-only catalogs;
no source clients, credentials, arbitrary remote URLs or implicit Mart writer.

Trusted identity must be server-derived, asset scoped, revocable and audited.
ADMIN is a bounded application-security capability, not source/Mart authority,
not an independent reviewer override. Enterprise integration and writer/migration
provisioning are separately reviewed activation gates. Production router remains
unmounted; development fixtures are not authentication.

Inspection measurements, human interpretations and review decisions are separate.
Unknown values/units/times remain explicit. Good quality does not mean freshness
or equipment health. Canonical asset resolution is exact; no fuzzy crosswalk.
Reviewed local records retain append-only revisions and compare-and-swap updates.

Rollback: do not activate candidate bootstraps. Future approved deployment must
back up the existing application store, validate its identity/ledger, apply only
reviewed additive application migrations, and revoke mounting/writer authority
before rollback. Retain audit and approved records; no table drop/truncate or
source recollection. Mart migrations and Phase-1 journals are outside this path.
