# NADI-PR101-LOGIN-CI-FIX-01

Baseline: b70700d1aec087c9a3cf7a47db03d9f4f7f987ef, PR101 remains draft.

The login submit spinner assertion used a generic aria-hidden selector which also selected the approved password-eye SVG. Scope it to button[type="submit"] .spinner[aria-hidden="true"] inside the named login form. Preserve busy, disabled username/password/submit, generic error, cleared password and focused-feedback assertions.

The localization-only browser entry lacked the real authenticated workspace provider after the approved logout control moved into the existing topbar. Wrap its synthetic Engineering-local route with the actual provider and exact fixture identity. Require confirmation without revocation, explicit consent and CSRF before direct /login navigation; keep later anonymous/revoked redirects and bounded return-path checks. Include actual login stylesheet and exact image fixtures to test the approved design instead of stale presentation. No production component or auth implementation changed.

The separate login/logout suite now additionally dispatches focus/visibility events before consent, while pending and after failure. It preserves cancel/Escape, spinner, disabled submission, hidden protected workspace, failure, explicit retry and CSRF-success tests.

Local results: full localization browser396 PASS; login/logout browser56 PASS (existing51 plus5 focus/visibility assertions). All15 frontend check groups PASS, TypeScript PASS, full lint0errors/one pre-existing EngineeringWorkspace dependency warning, isolated production build PASS. All browser traffic fulfilled by synthetic fixtures; no active-runtime browser login/session operations. Exact-head hosted CI must separately qualify the final commit; the final PR receipt reports that result.

Preservation: no active source edits, controller changes, service restart or handover. Existing private checkpoint attests exact source hashes, frontend/QA listener identities and35 original container identities unchanged. No database/schema/session access, collector/source operation, PR100 mutation or merge. Senior review and Product Owner acceptance pending.
