# Fullscreen login evidence

See [implementation and review](../../nadi-ux-login-01.md).

Actual before screenshots are privately retained under
`.nadi-dev/state/ux-login-01/before/` at the prior serving SHA 5d8b5c0.
The real HTTPS login displayed AppShell at all three widths.

Candidate component screenshots from the hermetic browser suite are labeled as
network-isolated fixture evidence, separate from actual live HTTPS screenshots.
The suite preserves simulated Case/Recommendation/Advisory/ACK semantics and makes
no requests to operational services or the persistent QA database.

Actual credential-free login images and the exact source/CI/runtime handoff are
added after the official controlled frontend-only preview checks. Engineering
screens with operational data, account names or audit contents remain private.

## Network-isolated component fixtures

395 checks PASS. No live backend/data/persistence claim.

| Width | Light | Dark |
| --- | --- | --- |
| 1440px | [Light](fixture-login-1440.png) | [Dark](fixture-login-dark-1440.png) |
| 768px | [Light](fixture-login-768.png) | [Dark](fixture-login-dark-768.png) |
| 390px | [Light](fixture-login-390.png) | [Dark](fixture-login-dark-390.png) |

## Actual HTTPS3000 before/after

Live captures use the sole official HTTPS preview with no response interception.
Before source: `5d8b5c07531a9b8da9ee5f82a740ee7b519488bd`.
After functional source: `79dda14ccee487f61452aa599f12d9cc3f0d4c09`.
The final release adds only documentation and these captured images; exact final
serving SHA is verified again through the controller and recorded in the PR handoff.
No account credentials, cookies, engineering record contents or operational values
are present in these public login images. Original logo/reference PNGs are unchanged.

| Width | Actual before | Actual fullscreen light | Actual fullscreen dark |
| --- | --- | --- | --- |
| 1440px | [Before](before-login-1440.png) | [After](live-login-1440.png) | [Dark](live-login-dark-1440.png) |
| 768px | [Before](before-login-768.png) | [After](live-login-768.png) | [Dark](live-login-dark-768.png) |
| 390px | [Before](before-login-390.png) | [After](live-login-390.png) | [Dark](live-login-dark-390.png) |

[Expired-session feedback](live-login-expired-390.png) · [sanitized actual report](live-summary.json).

Actual final functional run: 102 checks PASS / 7 screenshots / no browser exceptions.
A separate prior run confirmed generic invalid-credential feedback and cleared
password/error focus before a test-only history-wait assertion failed. Subsequent
run passed all history/logout and route checks. Server expiry/role/review/revision
boundaries are covered in hermetic/CI tests; the live expired-message screenshot
uses `?expired=1` without changing the database's expiry policy.

Three live-harness issues were corrected: Next development has an empty auxiliary
alert (select the login form alert), URL changes precede completed RSC layout renders
(wait for login visibility and shell detachment), and the accepted overview caption
is Ringkasan Eksekutif. Failed attempt logs remain private and are not hidden as
successful runs. No application/authentication change was needed for these issues.
