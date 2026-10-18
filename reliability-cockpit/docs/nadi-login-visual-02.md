# Login visual refresh and existing topbar logout

Product Owner reference: NADI Industrial Analytics Login Interface.png, supplied18October2026.
Local implementation on codex/nadi-login-visual-02, from reviewed PR101 foundation
bf7f5d366ad941b1e527e24e96fc286757cbc3c5. PR101 remains unchanged; no merge/deployment.

- Standalone navy/light login follows the supplied composition. Exact tagline: **Data Andal Keputusan Terarah**.
- Generated fictional power-plant illustration is saved as [power-plant-night.png](../web/public/login/power-plant-night.png).
  Built-in image_gen was used; [prompt/provenance/hash](evidence/nadi-login-visual-02/asset-provenance.json).
  The illustration is labeled digital and is not accepted factual plant evidence.
- Original transparent logo_nadi.png remains byte-identical. CSS displays its white reverse
  presentation without a white panel. No generated replacement logo was adopted.
- Username and logout now use the existing application topbar beside theme controls;
  no additional session-account navigation row. Canonical identity/roles remain available.
- Native modal confirmation asks “Keluar dari NADI?”; Batal and Escape keep the session,
  focus begins on Batal, and Ya, keluar invokes the existing session/CSRF logout endpoint.
  Existing fail-closed session checking, RBAC and all server authorization remain.
- Only /login/power-plant-night.png is public to support pre-auth login rendering. The
  folder is not exempted; anonymous neighboring routes redirect and factual API returns401.

## Validation

[Summary](evidence/nadi-login-visual-02/validation.json): TypeScript, changed-file lint,
final isolated production build and existing login/global-auth/factual policy checks PASS.
35 isolated synthetic Chromium checks plus10 actual trusted-HTTPS checks PASS.
Desktop1440/tablet768/mobile390, light/dark, no horizontal page overflow, aligned topbar,
Cancel/Escape, one confirmed CSRF logout and subsequent protected-API401 verified.
Synthetic results are separate from actual live evidence; no TLS bypass.
A pre-existing broader EngineeringWorkspace hook warning remains outside this UI change.
GitHub CI was not rerun for this local follow-up; PR101's successful CI is foundation evidence.

[Desktop](evidence/nadi-login-visual-02/login-light-1440.png) ·
[Dark](evidence/nadi-login-visual-02/login-dark-1440.png) ·
[Tablet](evidence/nadi-login-visual-02/login-light-768.png) ·
[Mobile](evidence/nadi-login-visual-02/login-light-390.png) ·
[Logout](evidence/nadi-login-visual-02/logout-dialog-1440.png) ·
[Mobile logout](evidence/nadi-login-visual-02/logout-dialog-390.png).

## Live preview and preservation

Existing https://localhost:3000 uses the same detached7daab3a worktree plus preserved dirty
ModeA source, now including these eight reviewed UI/static-asset files. It is not falsely
relabeled as this clean review branch. UI updates appeared through existing development
refresh with no service restart/handover. Frontend and QA listener identities remain exactly
unchanged, as do private controller and all35 original containers. No backend source, schema,
account policy, collector, factual business data or operational configuration changed.
Only task-owned browser sessions used normal login and CSRF logout; no existing user session
was reset/cleaned/revoked. [Preservation](evidence/nadi-login-visual-02/preservation.json).

Exact previous contents/hashes of edited active files were retained privately under the
existing task checkpoint in /tmp. Recovery must verify current hashes and restore only these
owned files, removing only the new owned CSS/context/illustration after review; never reset
or clean the active dirty worktree. No DB restoration is needed for this presentation change.
Product Owner visual acceptance remains pending. No automatic merge or runtime handover.
