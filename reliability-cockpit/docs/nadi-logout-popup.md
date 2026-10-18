# Logout progress inside confirmation dialog

Root cause: confirming logout closed the dialog and set the entire workspace to checking, displaying the legacy session-check page before navigation.

Keep the same dialog mounted through pending and failed states. Show a spinner and disable repeated submission. Block Escape/dismissal after revocation begins; hide protected workspace content. Focus/visibility/polling responses cannot replace pending progress. On success, use existing direct /login replacement; on failure, show an explicit retry inside the popup, without falsely claiming success. Existing session-bound CSRF logout contract remains unchanged.

Validation: 51 isolated browser assertions include delayed logout, no checking-page flash, single-submit protection, failure/retry and hidden protected content. TypeScript, scoped lint, production build and 16 global-auth checks PASS. Actual trusted HTTPS browser verified own test-session login/logout, pending popup, direct fullscreen login, and subsequent session401. No original user sessions reset. [Live result](evidence/nadi-logout-popup/live-results.json), [synthetic result](evidence/nadi-logout-popup/synthetic-results.json), [screenshot](evidence/nadi-logout-popup/logout-pending.png), [preservation](evidence/nadi-logout-popup/preservation.json).

Only AuthenticatedWorkspace.tsx applied through existing Mode A Fast Refresh. Frontend/QA process identities, controller, unrelated active files and 35 original containers unchanged. No restart, backend source, schema, database cleanup, collector operation or merge. Private exact original-file checkpoint retained for scoped rollback. Product Owner visual review pending.
