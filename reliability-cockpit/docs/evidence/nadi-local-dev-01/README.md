# NADI-LOCAL-DEV-01 actual live evidence

[Main report](../../nadi-local-dev-01.md) · [Summary](summary.json) · [Browser stages including failed checks](browser-checks.json) · [Preservation](preservation.json) · [Runtime measurements](runtime-metrics.json).

Actual live screenshots, not intercepted fixtures:

- Input: [1440](desktop-input-1440.png), [1920](desktop-input-1920.png).
- Register: [1440](desktop-register-1440.png), [1920](desktop-register-1920.png).
- [Original-sample history](measurement-history-1440.png).
- [Independent review](inspection-review-1440.png).
- [Engineering Case handoff](engineering-handoff-1440.png).
- [Temporary Fast Refresh text visible](fast-refresh-visible.png); the probe was subsequently reverted.

Only newly generated synthetic fixture records appear. No account/password/session/CSRF data, original DB row dumps, source credentials or private config files are included. Old QA fingerprints and validated dump remain private under `.nadi-dev/state/local-dev-01`. Full-page captures may place fixed sidebar content at the scroll position at capture; final desktop input/register captures start at the top. No page overflow or blocking desktop layout defect was observed.
