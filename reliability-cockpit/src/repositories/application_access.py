"""Read-only PostgreSQL privilege audit. Never creates roles, grants or connects sources."""
from sqlalchemy import text
from src.domain.engineering import EngineeringError


def assert_writer_capability(connection, role):
    row = connection.execute(text(
        "SELECT oid,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolbypassrls "
        "FROM pg_roles WHERE rolname=:role"), {"role": role}).first()
    if row is None or any(row[1:]):
        raise EngineeringError("APPLICATION_WRITER_ROLE_UNSAFE", 503)
    oid = row[0]
    if connection.scalar(text("SELECT count(*) FROM pg_auth_members WHERE member=:oid"), {"oid": oid}):
        raise EngineeringError("APPLICATION_WRITER_ROLE_UNSAFE", 503)
    if connection.scalar(text(
        "SELECT (SELECT count(*) FROM pg_namespace WHERE nspowner=:oid)"
        "+(SELECT count(*) FROM pg_database WHERE datdba=:oid)"
        "+(SELECT count(*) FROM pg_class WHERE relowner=:oid)"), {"oid": oid}):
        raise EngineeringError("APPLICATION_WRITER_OWNERSHIP_FORBIDDEN", 503)
    if connection.scalar(text(
        "SELECT has_schema_privilege(:role,'public','CREATE')"), {"role": role}):
        raise EngineeringError("APPLICATION_WRITER_DDL_FORBIDDEN", 503)


def assert_no_public_application_grants(connection, tables):
    for name in sorted(tables):
        # Expanded ACL avoids interpreting role names or assuming default PUBLIC safety.
        if connection.scalar(text(
            "SELECT count(*) FROM pg_class c CROSS JOIN LATERAL "
            "aclexplode(coalesce(c.relacl,acldefault('r',c.relowner))) a "
            "WHERE c.oid=to_regclass(:name) AND a.grantee=0"), {"name": name}):
            raise EngineeringError("APPLICATION_PUBLIC_PRIVILEGES_UNSAFE", 503)
    if connection.scalar(text(
        "SELECT count(*) FROM pg_default_acl d CROSS JOIN LATERAL aclexplode(d.defaclacl) a "
        "WHERE a.grantee=0 AND d.defaclobjtype IN ('r','S','f') AND "
        "(d.defaclnamespace=0 OR d.defaclnamespace=(SELECT oid FROM pg_namespace WHERE nspname='public'))")):
        raise EngineeringError("APPLICATION_DEFAULT_PRIVILEGES_UNSAFE", 503)


def audit_runtime_access(engine, *, expected_database, owner, capability, runtime):
    """Return reason codes only. Caller supplies an explicitly approved engine."""
    from src.repositories.application_migrations import MIGRATIONS, CURRENT, LEDGER
    from src.repositories.application_boundary import ApplicationStore
    ApplicationStore(engine, expected_database=expected_database, dedicated=True)
    tables = set().union(*MIGRATIONS.values())
    with engine.connect() as c:
        assert_writer_capability(c, capability)
        assert_no_public_application_grants(c, tables)
        rows = {r[0]: r for r in c.execute(text(
            "SELECT rolname,oid,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolbypassrls "
            "FROM pg_roles WHERE rolname IN (:owner,:cap,:runtime)"),
            {"owner": owner, "cap": capability, "runtime": runtime})}
        if len({owner, capability, runtime}) != 3 or set(rows) != {owner, capability, runtime}:
            raise EngineeringError("APPLICATION_ROLE_SEPARATION_REQUIRED", 503)
        r = rows[runtime]
        if not r[2] or any(r[3:]):
            raise EngineeringError("APPLICATION_RUNTIME_ROLE_UNSAFE", 503)
        ancestors = set(c.scalars(text(
            "WITH RECURSIVE memberships(oid) AS (SELECT roleid FROM pg_auth_members WHERE member=:oid "
            "UNION SELECT m.roleid FROM pg_auth_members m JOIN memberships p ON m.member=p.oid) "
            "SELECT r.rolname FROM memberships p JOIN pg_roles r ON r.oid=p.oid"), {"oid": r[1]}))
        if ancestors != {capability}:
            raise EngineeringError("APPLICATION_MEMBERSHIP_UNSAFE", 503)
        if c.scalar(text(
            "SELECT (SELECT count(*) FROM pg_namespace WHERE nspowner=:oid)"
            "+(SELECT count(*) FROM pg_database WHERE datdba=:oid)"
            "+(SELECT count(*) FROM pg_class WHERE relowner=:oid)"), {"oid": r[1]}):
            raise EngineeringError("APPLICATION_RUNTIME_OWNERSHIP_FORBIDDEN", 503)
        if (c.scalar(text("SELECT has_schema_privilege(:role,'public','CREATE')"), {"role": runtime})
                or c.scalar(text("SELECT has_database_privilege(:role,current_database(),'CREATE')"), {"role": runtime})
                or c.scalar(text("SELECT has_database_privilege(:role,current_database(),'TEMP')"), {"role": runtime})):
            raise EngineeringError("APPLICATION_RUNTIME_DDL_FORBIDDEN", 503)
        if not c.scalar(text("SELECT has_database_privilege(:role,current_database(),'CONNECT')"), {"role": runtime}):
            raise EngineeringError("APPLICATION_CONNECT_REQUIRED", 503)
        for table in tables | {LEDGER}:
            actual_owner = c.scalar(text(
                "SELECT pg_get_userbyid(relowner) FROM pg_class WHERE oid=to_regclass(:name)"), {"name": table})
            if actual_owner != owner:
                raise EngineeringError("APPLICATION_MIGRATION_OWNER_MISMATCH", 503)
            allowed = {"SELECT", "INSERT", "UPDATE"} if table in CURRENT else {"SELECT", "INSERT"}
            if table == LEDGER:
                allowed = {"SELECT"}
            for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"):
                actual = c.scalar(text("SELECT has_table_privilege(:role,:name,:privilege)"),
                                  {"role": runtime, "name": table, "privilege": privilege})
                if bool(actual) != (privilege in allowed):
                    raise EngineeringError("APPLICATION_RUNTIME_PRIVILEGE_DRIFT", 503)
        other_writes = c.scalar(text(
            "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m') AND "
            "c.relname<>ALL(:tables) AND has_table_privilege(:role,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE')"),
            {"tables": list(tables | {LEDGER}), "role": runtime})
        if other_writes:
            raise EngineeringError("APPLICATION_NONAPPLICATION_WRITE_FORBIDDEN", 503)
    return {"database_identity": "PASS", "owner_separation": "PASS", "writer_privileges": "PASS",
            "public_and_default_privileges": "PASS", "membership": "PASS",
            "immutable_history": "PASS", "runtime_ddl": "DENIED"}
