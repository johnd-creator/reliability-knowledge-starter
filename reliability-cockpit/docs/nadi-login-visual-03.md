# Login visual correction — cyan logo and password control

Use the exact transparent white/cyan generated logo selected by the Product Owner, without the previous whitening filter. Preserve the source asset bytes and original logo. Strengthen the navy background overlay and tagline shadow. Replace visible password-toggle text with an accessible, labeled eye icon inside a full-width input matching the username input.

Authentication requests, session, CSRF and authorization behavior are unchanged. Only the exact new decorative logo path is anonymous; adjacent routes remain guarded.

Validation: 47 isolated browser assertions; 10 login-presentation, 16 local-auth and 16 global-auth checks; TypeScript, scoped lint, production build and diff whitespace checks PASS. The initial additional middleware assertion used an out-of-scope test variable; it was corrected and all checks rerun. Initial live image selector assumed a raw src; Next.js image optimization changes the URL. The corrected browser check verified the actual optimized image and byte-equal public source.

Actual HTTPS browser checks at 1440, 768 and 390px PASS in light/dark modes: equal field sizes, inset eye toggle with unchanged input value, no page overflow, full-screen login, selected cyan logo. No credential submission or session write. [Live results](evidence/nadi-login-visual-03/live-results.json), [preservation](evidence/nadi-login-visual-03/preservation.json), [logo provenance](evidence/nadi-login-visual-03/logo-provenance.json).

[Desktop](evidence/nadi-login-visual-03/login-light-1440.png), [tablet](evidence/nadi-login-visual-03/login-light-768.png), [mobile](evidence/nadi-login-visual-03/login-light-390.png).

Applied only five reviewed UI/static files through existing Mode A Fast Refresh. Active detached HEAD remains 7daab3a62866f19b30fb45462a94bafff8795dc5 with explicit dirty UI changes. Frontend/backend process identities, private controller, unrelated active files and original 35 containers unchanged. No restart, handover, database/schema operation, collector action or merge. Exact previous file contents and hashes retained privately for file-specific rollback. Product Owner visual approval pending.
