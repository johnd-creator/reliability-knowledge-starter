# NADI concept alignment — Bundle B candidate

All five original root PNGs were inspected directly using the local image viewer at original resolution during this bundle; analysis below is visual evidence, not source-system evidence. The existing `web/public/logo_nadi.png`, layout, navigation, theme tokens, factual pages and Engineering Workspace were also inspected. Image hashes identify the exact reference bytes.

| Original image | SHA256 |
|---|---|
| `konsep1.png` | `b204566e4fc9e07512898ceca89d4e75c420cef9defc70755c3a6543d262f666` |
| `konsep2.png` | `1b3686be9700257f9eb53b1c2fe1073215d7dc09dc96487b9b547033d6f2b2ee` |
| `konsep3.png` | `77270507fe975b883b9317a46b0580462fd9e06f248920722bea6f2cc8f17b60` |
| `konsep4.png` | `31082400dc1a501d7924ddd7be4c7865413ae7a9c125290587a979b39f293d57` |
| `konsep5.png` | `a6e57d1ca29400b8e62f372b819c3f9875f7949cae2dde1736e874f32583f1ec` |

## Visual findings and canonical direction

1. **konsep1 — Action Board:** navy left navigation, teal/green active treatment, compact top context, four attention cards and dense ranked tables. Purpose is triage and follow-up, not a source WO editing console.
2. **konsep2 — Recommendations:** status/filter controls, search, summary tiles and a large recommendation table with owner/date/source-WO context. Purpose is human proposal tracking. A recommendation status must not imply source WO status.
3. **konsep3 — PdM Center:** six inspection-method tabs, summary visualization, trend and findings register. Purpose is inspection evidence review. Illustrative totals differ in the concept and are not an authoritative inventory or acceptance model.
4. **konsep4 — Asset detail:** strong equipment identity, health-score tiles, asset facts, method summaries, maintenance trend and recommendations. Purpose is asset context. Health scores/traffic lights require an approved assessment model; this candidate explicitly uses NOT ASSESSED.
5. **konsep5 — executive overview:** portfolio filters, metrics, distribution with gray unknown segment, ranked attention and trend. Purpose is portfolio navigation; no unsupported prediction/risk aggregate is introduced.

Across concepts, typography is compact sans-serif, titles have clear weight hierarchy, spacing groups filters/cards/tables and navy/teal establishes NADI identity. Exact font family, pixel values and original designer interaction intent cannot be proven from flattened images. Canonical implementation reuses current NADI logo, shared spacing/theme tokens, light/dark support, PageHeader, SectionCard, EmptyState and neutral StatusBadge. Teal indicates navigation, not health. No global palette rewrite is necessary.

## Concept-to-screen matrix

| Screen | Reference | Implemented candidate | Missing / activation blocker |
|---|---|---|---|
| Engineering case list/detail | 1/2 workflow hierarchy; existing case implementation | Existing synthetic list, filtering, hypothesis editor, independent-review simulation, history/conflict feedback retained | Trusted provider, reviewed application writer, real per-asset directory |
| PdM Center | 3 | `/engineering/lab` method selection, manual typed value/unit/time/context, observations vs hypotheses, register/status filter, local submit/history | Engineer-approved field definitions, secure attachments, operational persistence |
| Asset Health 360 | 4 | Same lab asset context, per-method evidence availability, NOT ASSESSED, quality/freshness caveat | Approved assessment semantics, integrated authorized read path; no invented health score |
| Recommendations | 2 | Local draft/rationale/date, linked synthetic case, bounded register | Real directory, independent review API integration, existing WO read selector |
| Action Board | 1 | Derived synthetic review queue and local proposal totals, explicit pending reviewer | Enterprise identity/revocation, operational review/follow-up; never source WO mutation |
| Executive overview | 5 | Existing factual Maximo dashboard and Data Trust retained | Portfolio assessment aggregation DEFERRED until approved semantics |

## Component and interaction plan

Reuse shared asset context and evidence cards. Separate SOURCE FACT (immutable, original unit/source time), HUMAN OBSERVATION, HUMAN HYPOTHESIS, REVIEW DECISION and UNKNOWN. Existing Engineering evidence viewer preserves numeric/text/digital/null, quality and distinct timestamps; it never interprets Good as current/healthy. Manual draft editor preserves unsaved input on validation errors, confirms navigation and records local revisions. CAS conflicts must reload authorized history while retaining unsaved text. Review controls later consume a trusted server session and deny creator/PIC/contributors; browser identity is never authority.

The development-only lab is one context-preserving route with four accessible navigation buttons. Saved synthetic drafts remain in memory when switching views, and unsaved forms warn on departure. Panels collapse to one column on narrow desktops/mobile; controls, long canonical IDs, keyboard focus and neutral unknown badges are bounded. Production cannot render the lab even when both candidate flags are true.

PH2-03 implementation order: engineer field sign-off → method form contracts → secure attachment metadata/storage boundaries → trusted frontend/API integration → scoped read-only asset context and WO references → human reviewer UAT → application provisioning review. Operational activation remains separately authorized; no application migration or source collection occurs in this bundle.
