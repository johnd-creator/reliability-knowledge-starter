# Bundle C — login visual readiness evidence

2026-10-10. Functional source `64eb1f73152267d454056abf798aed5bf89f9b27` on the existing single
https://localhost:3000 frontend. Evidence is a reviewed presentation candidate,
not final Product Owner approval or global authentication activation.

All 14 screenshots use **DEMO / synthetic browser states**, mocked authentication
failures and a sanitized fixture identity. They contain no actual credentials,
account names, session cookies or plant measurements. Actual assigned-account
login and retained-record checks run separately without screenshots.
The unchanged original NADI logo and implemented Design System V1 are the visual
inputs; no supplied official login reference image exists.

| State | Desktop 1440 px | Tablet 768 px | Mobile 390 px |
|---|---|---|---|
| Default | [PNG](login-default-1440.png) | [PNG](login-default-768.png) | [PNG](login-default-390.png) |
| Loading | [PNG](login-loading-1440.png) | [PNG](login-loading-768.png) | [PNG](login-loading-390.png) |
| Error | [PNG](login-error-1440.png) | [PNG](login-error-768.png) | [PNG](login-error-390.png) |
| Expired | [PNG](login-expired-1440.png) | [PNG](login-expired-768.png) | [PNG](login-expired-390.png) |

Additional evidence: [existing password-change state](login-password-change-390.png),
[dark theme](login-dark-1440.png), [96 login browser checks](login-browser-report.json),
[21 merged-main synchronization checks](stage-a-report.json),
[105 Bundle A regressions](bundle-a-regression.json) and
[129 Bundle B regressions](bundle-b-regression.json).

Desktop uses paired navy identity / white form panels. Tablet/mobile prioritize
credentials with compact brand context; the existing development status banner
remains visible and may require scrolling. Native Next.js development controls
are retained. Controls are 48 px, with keyboard focus, explicit disabled guidance,
announced generic feedback and color-independent labels. Computed form boundaries
meet 3:1 and error text 4.5:1 in the tested states; this is bounded evidence, not
an exhaustive accessibility certification. Dark form text/boundaries are checked.

PO decisions pending: wording/language, logo scale/white surround, compact mobile
brand layout, Engineering navigation placement and final spacing/density.
Final visual review is Monday, 12 October 2026. UX-09 is preparation.
See [implementation and review](../../../reliability-cockpit/docs/nadi-ux-bundle-c.md),
[UI specification](../NADI-UI-SPEC.md), [Design System](../../../DESIGN-SYSTEM.md)
and [official roadmap](../../../plans/NADI-ROADMAP.md).
