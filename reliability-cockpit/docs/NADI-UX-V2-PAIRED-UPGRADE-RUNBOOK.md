# Future local paired V2 upgrade — NOT EXECUTED

Requires separate explicit controller-delivery approval and paired activation
approval. This task permits neither. Run as the established owner, stopping on
any failed command or changed identity. Never reset source, delete journals,
apply migrations, restore data or retry startup automatically.

## Review and baseline

Review exact controller PR HEAD with backend/frontend CI, PR102 and the recovery
report. Fill the reviewed controller SHA and clean checkout path below. The
application SHA is current PR102; any replacement needs a new explicit review.

    set -euo pipefail
    REPO=/home/john-d/Music/reliability-knowledge-starter
    CONTROLLER_SHA=REPLACE_WITH_REVIEWED_40_CHARACTER_CONTROLLER_SHA
    REVIEWED_CONTROLLER=/absolute/path/to/clean/reviewed/controller/worktree
    APP_SHA=260c4f9f5f9a17aea3b36476ca4a0e202069e19d
    OLD_SHA=7daab3a62866f19b30fb45462a94bafff8795dc5
    OLD_CONTROLLER=fef7bccd61d3d6a5dd184f2fff94453242ff2056
    BASE="$REPO/.nadi-dev"
    CONTROL="$BASE/nadi-dev"
    QUAL="$BASE/ux-v2-upgrade-$(date +%Y%m%d-%H%M%S)"
    umask 077
    mkdir -m 700 "$QUAL"
    git -C "$REPO" cat-file -e "$CONTROLLER_SHA^{commit}"
    git -C "$REPO" cat-file -e "$APP_SHA^{commit}"
    "$CONTROL" local-status > "$QUAL/status-before.json"
    docker ps -a --no-trunc --format '{{json .}}' > "$QUAL/containers-before.jsonl"
    systemctl --user show nadi-primary-web.service nadi-live-api.service \
      -p MainPID -p ExecMainStartTimestamp -p WorkingDirectory -p InvocationID \
      -p NRestarts > "$QUAL/units-before.txt"

Independently verify frontend/API roots/HEAD are OLD_SHA, unit/cgroup/socket
ownership, installed wrapper/four-file release OLD_CONTROLLER, current existing
retained database/account/config and original bootstrap. Preserve private
metadata hashes and source scan as in qualification evidence. Inventory existing
containers and competing workers. Stop for a new review if any baseline moved.

Obtain an owner-only existing-session proof through the approved operator workflow,
without automated login/logout/account creation. Private JSON contains only cookie
using the existing session cookie; mode 600, outside source. Never print it.

    SESSION_PROOF=/absolute/private/path/to/existing-session-proof.json
    test -f "$SESSION_PROOF"
    "$CONTROL" local-status --session-file "$SESSION_PROOF" > "$QUAL/session-before.json"

Require authorized_session VERIFIED, correct asset/role policy and account hashes.
Record the same session's subject/roles/asset IDs privately. Record retained QA
IDs/counts/content digests through SELECT-only existing-store queries or authorized
read-only APIs, scoped to that account. HTTP 200 alone is not preservation proof.

## Controller installation — explicit delivery approval required

    test "$(git -C "$REVIEWED_CONTROLLER" rev-parse HEAD)" = "$CONTROLLER_SHA"
    test -z "$(git -C "$REVIEWED_CONTROLLER" status --porcelain)"
    /usr/bin/python3 "$REVIEWED_CONTROLLER/deploy/development/install_auth03_controller.py" \
      --repository "$REPO" --candidate-sha "$CONTROLLER_SHA" \
      --expected-release-sha "$OLD_CONTROLLER" --expected-serving-sha "$OLD_SHA" \
      --session-file "$SESSION_PROOF" --acknowledge-local-controller-update \
      > "$QUAL/controller-install.json"
    "$CONTROL" local-status --session-file "$SESSION_PROOF" > "$QUAL/status-installed.json"

Require exact release acceptance and unchanged source/process/container/account
identities. Installation updates controller metadata only; failure means stop.

## Prepare clean D and sealed R without service changes

Choose unused direct children of BASE, preserving original source/PR102 checkout:

    TARGET="$BASE/ux-v2-candidate-$(date +%Y%m%d-%H%M%S)"
    RECOVERY="$BASE/ux-v2-recovery-$(date +%Y%m%d-%H%M%S)"
    git -C "$REPO" worktree add --detach "$TARGET" "$APP_SHA"
    test -z "$(git -C "$TARGET" status --porcelain)"
    "$CONTROL" local-preserve "$QUAL/source-seal" > "$QUAL/seal-approval.json"
    MANIFEST=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["manifest"])' "$QUAL/seal-approval.json")
    MANIFEST_SHA=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["digest"])' "$QUAL/seal-approval.json")
    test "$(sha256sum "$MANIFEST" | cut -d' ' -f1)" = "$MANIFEST_SHA"
    "$CONTROL" local-prepare-recovery "$RECOVERY" \
      --preservation "$MANIFEST" --preservation-sha256 "$MANIFEST_SHA" \
      > "$QUAL/recovery-approval.json"
    RECEIPT=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["receipt"])' "$QUAL/recovery-approval.json")
    RECEIPT_SHA=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["receipt_sha256"])' "$QUAL/recovery-approval.json")
    test "$(sha256sum "$RECEIPT" | cut -d' ' -f1)" = "$RECEIPT_SHA"

Review fresh manifest/receipt digests, original provenance, file tree/modes, private
R SHA, disabled pushing and config/account bindings. Do not reuse the offline seal
from this task. Retain original base Git objects for the read-only alternate.

Use the pinned Node executable from existing frontend-runtime.json and verify
its hash/version. Use the already qualified npm CLI with that Node, not a globally
selected replacement. Set NPM_CLI to its verified absolute npm-cli.js path:

    PINNED_NODE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["node_path"])' "$BASE/state/frontend-runtime.json")
    NPM_CLI=/absolute/path/to/previously/qualified/npm-cli.js
    "$PINNED_NODE" --version
    (cd "$TARGET/reliability-cockpit/web" && "$PINNED_NODE" "$NPM_CLI" ci --ignore-scripts --no-audit --no-fund)
    (cd "$RECOVERY/reliability-cockpit/web" && "$PINNED_NODE" "$NPM_CLI" ci --ignore-scripts --no-audit --no-fund)
    cmp "$TARGET/reliability-cockpit/web/node_modules/.package-lock.json" \
        "$RECOVERY/reliability-cockpit/web/node_modules/.package-lock.json"
    "$CONTROL" local-preflight "$TARGET" --preview-ref "$APP_SHA" \
      --recovery-receipt "$RECEIPT" --recovery-receipt-sha256 "$RECEIPT_SHA" \
      > "$QUAL/paired-preflight.json"
    "$CONTROL" local-status --session-file "$SESSION_PROOF" > "$QUAL/status-prepared.json"

Require exact 20-surface/dependency compatibility, same database/container/account,
no schema/ledger drift, correct TLS/owners/source and existing verified session.
Check no dotenv or tracked source changes; R verification must remain exact.
Recompare protected files, original source, process and container identities.
Preparation must not restart anything. Do not copy serving node_modules.

## STOP for separate explicit paired-activation approval

Approval must name APP_SHA, CONTROLLER_SHA, manifest/receipt digests and R SHA,
the existing retained store, permission to restart only nadi-live-api.service and
nadi-primary-web.service and one bounded recovery. Exclude collectors and database/
schema/account changes. Controller delivery approval alone is insufficient.

Only after that separate approval:

    "$CONTROL" local-select "$TARGET" --preview-ref "$APP_SHA" \
      --recovery-receipt "$RECEIPT" --recovery-receipt-sha256 "$RECEIPT_SHA" \
      --acceptance-session-file "$SESSION_PROOF" > "$QUAL/selection.json"
    "$CONTROL" local-status --session-file "$SESSION_PROOF" > "$QUAL/status-after.json"
    docker ps -a --no-trunc --format '{{json .}}' > "$QUAL/containers-after.jsonl"

The controller validates a fresh readable private backup, double preflight and
last-moment owners/source before stopping, then starts only the development pair.
Require frontend/backend/launched SHAs APP_SHA, trusted HTTPS, existing session/
factual gateway, unchanged account hashes, same store/ledger and retained QA
records/session subject/roles/assets. Compare container IDs/states/ports. Perform
read-only Mode A/V2 page checks and PO visual acceptance. Do not write records to
test preservation. No migration or database restore occurs.

## Failure or deliberate rollback

Candidate failure triggers one bounded automatic recovery to R against the same
store. A nonzero selection is still failure even if recovery succeeds.
Inspect private requested/prepared/stopping/failed/recovered journals, actual units/
listeners and authenticated status. R reports its own SHA and original-source
provenance; do not expect clean OLD_SHA. Original dirty source stays untouched.

If V2 was accepted and rollback is explicitly authorized, active metadata already
contains approved previous R; rollback obtains a fresh backup and rechecks gates:

    "$CONTROL" local-rollback --acceptance-session-file "$SESSION_PROOF" > "$QUAL/rollback.json"
    "$CONTROL" local-status --session-file "$SESSION_PROOF" > "$QUAL/status-recovered.json"

On failed recovery or unresolved stopping journal, STOP and preserve everything.
Record actual PIDs/roots/socket owners/SHA privately; a pointer is not proof of
health. Request a separately reviewed recovery action. Never delete journals,
use frontend-only selection/old bootstrap, destructive checkout/stash/reset,
restore the database or blindly start the candidate again.
