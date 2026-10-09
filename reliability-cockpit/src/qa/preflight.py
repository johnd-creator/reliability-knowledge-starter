"""Read-only/source-free QA preflight. No dotenv, source HTTP, DDL or activation."""
import argparse, json, os, re, stat, subprocess
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, StrictBool, StrictInt, StrictStr
from src.services.identity_configuration import OidcTrustConfiguration, SessionRuntimePolicy

REQUIRED = "REQUIRED_OPERATOR_INPUT"
ROOT = Path(__file__).resolve().parents[3]


class QaConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    environment: Literal["qa"]
    release_sha: StrictStr
    origin: StrictStr
    application_database: StrictStr
    migration_owner: StrictStr
    writer_capability: StrictStr
    runtime_role: StrictStr
    storage_root: StrictStr
    identity_provider: StrictStr
    issuer: StrictStr
    client_id: StrictStr
    redirect_uri: StrictStr
    logout_uri: StrictStr
    algorithms: list[StrictStr]
    session_idle_seconds: StrictInt | None
    session_absolute_seconds: StrictInt | None
    provider_timeout_seconds: StrictInt | None
    pool_size: StrictInt | None
    pool_timeout_seconds: StrictInt | None
    lease_capacity: StrictInt | None
    attachment_max_bytes: StrictInt | None
    attachment_asset_quota_bytes: StrictInt | None
    orphan_grace_seconds: StrictInt | None
    retention_days: StrictInt | None
    operator_approval_ref: StrictStr | None
    engineering_enabled: StrictBool
    source_collection_enabled: StrictBool
    factual_data_mode: Literal["fixtures", "approved_select_only"]
    database_secret_ref: StrictStr | None = None
    identity_secret_ref: StrictStr | None = None
    scanner_approval_ref: StrictStr | None = None
    directory_approval_ref: StrictStr | None = None
    infrastructure_approval_ref: StrictStr | None = None
    backup_recovery_approval_ref: StrictStr | None = None


def assess_configuration(raw, *, actual_sha, clean):
    """No private values echoed. References are declared, never approval proof."""
    gates = []
    def gate(name, passed, reason):
        gates.append({"gate": name, "status": "PASS" if passed else "BLOCKED", "reason": reason})
    try:
        config = QaConfiguration.model_validate(raw)
    except Exception:
        return {"preparation": "BLOCKED", "real_qa_readiness": "NO_GO",
                "gates": [{"gate":"CONFIGURATION","status":"BLOCKED","reason":"INVALID_OR_UNKNOWN_CONFIG_FIELDS"}],
                "source_gets": 0, "writes": 0}
    gate("EXACT_RELEASE", bool(re.fullmatch("[a-f0-9]{40}", config.release_sha))
         and config.release_sha == actual_sha and clean, "PINNED_CLEAN_RELEASE_REQUIRED")
    gate("FEATURE_GATES", not config.engineering_enabled and not config.source_collection_enabled,
         "ACTIVATION_AND_COLLECTION_MUST_REMAIN_OFF")
    names = (config.application_database, config.migration_owner, config.writer_capability, config.runtime_role)
    gate("DATABASE_NAMES", len(set(names)) == 4 and all(re.fullmatch(r"[a-z][a-z0-9_]{2,62}", n) for n in names),
         "EXPLICIT_DISTINCT_QA_DATABASE_ROLES_REQUIRED")
    try:
        OidcTrustConfiguration(config.issuer, config.client_id, config.redirect_uri,
            config.logout_uri, config.origin, tuple(config.algorithms), config.provider_timeout_seconds)
        valid_identity = config.identity_provider in {"oidc", "gateway"}
        # Placeholder DNS is intentionally not a real approved origin/issuer.
        valid_identity = valid_identity and ".invalid" not in config.origin and ".invalid" not in config.issuer
    except Exception:
        valid_identity = False
    gate("IDENTITY_TRUST", valid_identity, "ENTERPRISE_TRUST_AND_REAL_HTTPS_ORIGIN_REQUIRED")
    try:
        SessionRuntimePolicy(config.session_idle_seconds, config.session_absolute_seconds,
            config.pool_size, config.pool_timeout_seconds, config.lease_capacity)
        session = True
    except Exception:
        session = False
    gate("SESSION_POOL_POLICY", session, "APPROVED_EXPLICIT_BOUNDED_POLICY_REQUIRED")
    a, q = config.attachment_max_bytes, config.attachment_asset_quota_bytes
    storage = (type(a) is int and 1 <= a <= 20*1024*1024 and type(q) is int and q >= a
               and config.storage_root.startswith("/") and REQUIRED not in config.storage_root
               and type(config.orphan_grace_seconds) is int and config.orphan_grace_seconds > 0
               and type(config.retention_days) is int and config.retention_days > 0)
    gate("PRIVATE_STORAGE_POLICY", storage, "STORAGE_QUOTA_RETENTION_INPUT_REQUIRED")
    refs = (config.operator_approval_ref, config.database_secret_ref, config.identity_secret_ref,
            config.scanner_approval_ref, config.directory_approval_ref,
            config.infrastructure_approval_ref, config.backup_recovery_approval_ref)
    gate("DECLARED_APPROVAL_REFERENCES", all(isinstance(v,str) and v.strip() and REQUIRED not in v for v in refs),
         "ACCOUNTABLE_OPERATOR_APPROVAL_REFERENCES_REQUIRED")
    return {"preparation": "PASS" if all(g["status"]=="PASS" for g in gates) else "BLOCKED",
            "real_qa_readiness": "NO_GO", "gates": gates,
            "attestations": "DECLARED_NOT_VERIFIED",
            "remaining": ["ONHOST_IDENTITY_PRIVILEGE_STORAGE_TLS_UAT_AUDIT",
                          "REVIEWED_ENTERPRISE_AND_FRONTEND_STARTUP_INTEGRATION"],
            "source_gets": 0, "writes": 0}


def read_private_config(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as f:
        info = os.fstat(f.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                or info.st_mode & 0o077 or info.st_size > 32768):
            raise ValueError("PRIVATE_CONFIGURATION_REQUIRED")
        data = f.read(32769)
        if len(data) > 32768:
            raise ValueError("CONFIGURATION_TOO_LARGE")
    return json.loads(data)


def audit_disposable_database(engine, config):
    """Optional local fixture audit only; no migrations/grants executed."""
    from src.repositories.application_access import audit_runtime_access
    from src.repositories.application_migrations import ApplicationMigrator
    url = engine.url
    if url.host not in {"127.0.0.1", "localhost"} or not (url.database or "").endswith("_test"):
        raise ValueError("DISPOSABLE_DATABASE_ONLY")
    states = ApplicationMigrator(engine, expected_database=config.application_database, isolated=True).status()
    if any(row["status"] != "APPLIED" for row in states):
        raise ValueError("APPLICATION_SCHEMA_NOT_READY")
    return audit_runtime_access(engine, expected_database=config.application_database,
        owner=config.migration_owner, capability=config.writer_capability, runtime=config.runtime_role)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="private owner-only JSON; never dotenv")
    parser.add_argument("--audit-disposable-db", action="store_true",
                        help="explicit loopback *_test read-only audit using NADI_APPLICATION_TEST_DSN")
    args = parser.parse_args(argv)
    try:
        raw = read_private_config(args.config)
        sha = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        clean = not subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"], text=True).strip()
        result = assess_configuration(raw, actual_sha=sha, clean=clean)
        if args.audit_disposable_db:
            from sqlalchemy import create_engine
            config = QaConfiguration.model_validate(raw)
            engine = create_engine(os.environ.get("NADI_APPLICATION_TEST_DSN", ""), connect_args={"connect_timeout":5})
            try:
                result["disposable_database"] = audit_disposable_database(engine, config)
            finally:
                engine.dispose()
    except Exception:
        result = {"preparation": "BLOCKED", "real_qa_readiness":"NO_GO",
                  "reason":"PRIVATE_CONFIG_RELEASE_OR_DISPOSABLE_AUDIT_INVALID", "source_gets":0,"writes":0}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["preparation"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
