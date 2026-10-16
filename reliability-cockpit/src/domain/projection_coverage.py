"""Internal B4 v1 evidence only. Never a public DTO or authorization boundary."""
from dataclasses import dataclass
from datetime import datetime

DOMAINS = ('asset_master','maintenance_event')
MANIFEST_FIELDS = ('captured','acknowledged','projected','unchanged','excluded','deferred','failed','unprocessed')
DEBT_FIELDS = ('outstanding','open','eligible','blocked','resolved','superseded','unlinked')
REPLAY_FIELDS = ('PENDING','CLAIMED','CAPTURED','WRITING','FAILED','PROJECTED','DONE','BLOCKED',
                 'expired_claims','stale_claims','policy_mismatch')

@dataclass(frozen=True)
class Activity:
    run_id: str
    state: str
    started_at: datetime
    completed_at: datetime | None
    capture_mode: str
    sealed: bool
    continuation: int

@dataclass(frozen=True)
class DomainCoverage:
    domain: str
    latest: Activity | None = None
    last_complete: Activity | None = None
    manifest: dict | None = None
    debt: dict | None = None
    replay: dict | None = None
    reconciliation: str = 'UNKNOWN'
    last_complete_verified: bool = False
    reasons: tuple[str,...] = ()
    scope_key: str = 'BSR:IP:WO_BSR'
    mapper_epoch: str = 'contract1.0-local-mapper-b1-v1'
    source_freshness: str = 'NOT_EVALUATED'
    policy_epoch: str = 'deferred-v1-BSR-IP-WO-BSR'
    replay_epoch: str = 'replay-v1-exact-id'
    proof_complete: bool = False

@dataclass(frozen=True)
class CoverageSnapshot:
    observed_at: datetime
    capability: str
    domains: tuple[DomainCoverage,...]
    version: str = 'projection-coverage-internal-v1'

    @classmethod
    def unknown(cls,now,reason,capability='UNKNOWN'):
        return cls(now,capability,tuple(DomainCoverage(d,reasons=(reason,)) for d in DOMAINS))
