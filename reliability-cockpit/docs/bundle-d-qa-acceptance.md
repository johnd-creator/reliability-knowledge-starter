# Bundle D isolated QA acceptance

D5 real HTTPS socket tests:11 passed. Workflow uses Uvicorn loopback server,
server-issued secure sessions and disposable PostgreSQL records. Checks cover
independent review, frozen inspection/case/recommendation lineage, local follow-up,
unknown/source-quality separation, forged/revoked session, cross-asset denial,
unreviewed evidence rejection, unavailable Mart, replay and stale-revision conflict.
No source client or mutation endpoint exists. Complete source data is synthetic.

Browser acceptance:25 checkpoints passed over HTTPS Next development UI →
loopback proxy → backend → PostgreSQL. Engineer creates/submits inspection;
independent reviewer approves; engineer links frozen evidence to Case; independent
reviewer approves Case/recommendation; internal follow-up appears in recommendation
list. Reload preserves durable records. Width390/768/1365 has no page overflow;
desktop/mobile screenshots visually inspected. This is a QA contract workbench,
not final engineer form UAT. Fixture identities exist only in tests/qa.

Real HTTP exposed a blocking ASGI lease risk: synchronous SQL/directory guard
inside async session dependency can block the event loop under overlapping
requests. Dependency now enters/exits leases on the same dedicated worker, keeping
thread-affine guard and authorized commit boundary. Enterprise provider guard and
service capacity/timeouts remain integration review requirements. Accessible
explicit select labels fixed through browser assertions.

Application fixtures use canonical migration002→003→004→005 and checksum ledger.
Private custom dump/catalog/restore into a second isolated *_test database verified
matching case/event/human revision/session/ledger counts. No operational backup or
restore performed. Private bytes are outside Git and restricted. Migration owner,
writer grants and Mart read-only tests are separate fixture validations.

Engineer UAT: approve each PdM method/version/field/unit and reviewer qualification;
review source/interpretation separation; validate unavailable/null/conflict/unsaved
states; review attachment scanning/storage policy; confirm no WO action; verify
case/recommendation independence and inspect immutable audit. Owner/security must
approve enterprise registration, directory, provisioning and deployment separately.
Phase1 CURRENT/PARTIAL; Phase2 disposable QA candidate only.
