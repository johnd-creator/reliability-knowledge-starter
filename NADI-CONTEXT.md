# NADI — project context

Updated: 2026-10-10 · NADI-DOC-FOUNDATION-01. Start here after [AGENTS.md](AGENTS.md).

**NADI — Reliability Data Platform** supports reliability engineering and asset
maintenance decisions at **PLTU Banten 1 Suralaya**. It is the reliability product
within the Power Plant Data Platform. Its vision is to bring factual data and
governed engineering evidence into one Reliability Engineering platform.

## Architecture and ownership

The Shared Data Foundation comprises Maximo Knowledge/Collector, PI
Knowledge/Collector, CEMS Collector and Reliability Data Contracts. Collectors
own guarded source acquisition and their existing stores. Reliability Mart is
inside the existing Maximo Collector database; the NADI FastAPI backend reads it
with SELECT-only authority. The Next.js frontend uses the Cockpit API proxy.
Legacy Cockpit ingestion is a separate path into the existing Cockpit store.

Engineering Cases, inspections, reviews, audit and recommendations belong to
NADI's application store, never to the Mart or source systems. Operational writer
provisioning remains gated; current persisted development workflows use the
existing isolated test fixture. NK is a separate consumer with no application DB.
See [platform ownership](plans/PLATFORM-VISION.md),
[ADR006](reliability-cockpit/docs/adr/006-engineering-workspace.md) and
[ADR007](reliability-cockpit/docs/adr/007-source-read-only-application-boundary.md).

## Development environment

Primary frontend: **https://localhost:3000**. One address serves factual screens
and development-only Engineering. Explicit, controlled branch previews may use
that same address; do not create permanent parallel NADI frontends.

At the audit, merged main is `f54643f3510bf505628a1400024784faab46e496`;
the active, clean preview is PR #62 at
`0bfea1273f97ce96a08ef147b44f804aecb428d1`. PR #62 is OPEN, not merged.
The [audit and development runbook links](docs/NADI-DOC-FOUNDATION-01.md)
record the verified source, secure login boundary and startup authority.
Read the banner's full SHA, dirty state, backend availability and fixture identity
before reviewing changes. A documentation branch is not automatically visible there.

## Modules and current scope

| Module | Verified scope / target |
|---|---|
| Executive Overview | Implemented factual dashboard; visual polish planned |
| Asset Health | Factual register/detail and assessment records exist; integrated asset workspace planned |
| PdM Center | Synthetic concepts and inspection foundation exist; engineer-approved measurement UI planned |
| Engineering Workspace | Merged case/review/audit foundation; persisted isolated QA visible; operational activation partial |
| Recommendations | Merged NADI-owned lifecycle and isolated QA; final operational UI pending |
| Action Board | Synthetic concept and local follow-up foundation; operational board pending |
| Reports | Product module planned; no claim of a complete reporting product |
| System Integration | Data Trust/integration evidence exists; consolidated navigation planned |
| Administration | Private bounded account administration exists; product administration UI planned |

The [official roadmap](plans/NADI-ROADMAP.md) owns Phase 0–5 and the Product UI/UX
track. Factual Phase 0 is complete within its accepted boundary; Phase 1 remains
partial. Engineering foundations are merged, but merging and development tests do
not establish operational activation or engineer UAT. [Repository Status](plans/REPOSITORY-STATUS.md)
and [DEV-LOG](DEV-LOG.md) distinguish those milestones.

## Non-negotiable boundaries

- Maximo and PI source data remain READ-ONLY. NADI never creates, approves,
  updates or closes Maximo Work Orders; existing WO links are informational.
- Preserve stores, accepted evidence, audit/session history and `23496711.xls`.
  A documentation task never changes services, policies, credentials or data.
- No invented condition, score, threshold, risk classification or prediction.
  UNKNOWN, NOT ASSESSED and labeled DEMO have different meanings.
- Source quality, source/collection/projection time, human review and equipment
  condition are independent. Portable PdM is episodic; PD is not assumed DGA.
- Global login is a future requirement. This phase specifies its design only;
  factual development access and existing HTTPS Engineering security remain intact.

## How work continues

Read [PRD](PRD.md), [Design System](DESIGN-SYSTEM.md),
[UI specification](docs/design/NADI-UI-SPEC.md), roadmap/status/log, then scoped
instructions and technical evidence. Use task branches, PRs, relevant tests and
exact-head CI. Verify runtime visibility separately. Record Product Owner decisions
with scope/evidence; proposals are not approvals. Append a development-log entry at
each material milestone. GitHub reviewed documents are the persistent knowledge
source; chat decisions become durable only when their provenance is recorded.
