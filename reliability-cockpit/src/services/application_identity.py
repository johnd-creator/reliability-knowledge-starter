"""Injected trusted-provider + shared SQL session foundation; no runtime mounting.

Provider implementations MUST verify authentication externally and serialize grant
changes through guard(). No production IdP, anonymous fallback or browser roles.
"""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from hashlib import sha256
from hmac import compare_digest
import secrets
from typing import Protocol
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import HTTPException, Request
from pydantic import Field, StrictInt
from sqlalchemy import Column, String, Integer, JSON, select, update
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import Principal, Role, EngineeringError


class SecurityAction(StrEnum):
    SESSION_ESTABLISHED = "SESSION_ESTABLISHED"
    SESSION_REVOKED = "SESSION_REVOKED"
    ACCESS_GRANTED = "ACCESS_GRANTED"
    ACCESS_DENIED = "ACCESS_DENIED"


class IdentityGrant(EvidenceModel):
    principal: Principal
    version: StrictInt = Field(ge=1)
    valid_until: datetime


class TrustedIdentityProvider(Protocol):
    def verify_assertion(self, assertion: str) -> IdentityGrant: ...
    def current_grant(self, subject: str) -> IdentityGrant | None: ...
    # Held across the authorized command commit. Directory revocation/changes
    # must use the same serialization boundary; a no-op guard is not production-ready.
    def guard(self, subject: str, version: int): ...


class IdentityBase(DeclarativeBase):
    pass


class SessionRow(IdentityBase):
    __tablename__ = "nadi_application_session"
    token_hash = Column(String(64), primary_key=True)
    csrf_hash = Column(String(64), nullable=False)
    subject = Column(String(160), nullable=False)
    grant_version = Column(Integer, nullable=False)
    created_at = Column(String(40), nullable=False)
    last_seen_at = Column(String(40), nullable=False)
    expires_at = Column(String(40), nullable=False)
    revoked_at = Column(String(40), nullable=True)


class SecurityRow(IdentityBase):
    __tablename__ = "nadi_security_activity"
    activity_id = Column(String(100), primary_key=True)
    subject = Column(String(160), nullable=True)
    action = Column(String(40), nullable=False)
    outcome = Column(String(40), nullable=False)
    occurred_at = Column(String(40), nullable=False)
    asset_ids = Column(JSON, nullable=False)


def _hash(token):
    return sha256(token.encode()).hexdigest()


class SessionAuthority:
    COOKIE = "__Host-nadi_session"

    def __init__(self, store, provider: TrustedIdentityProvider, *, origins, idle_seconds, absolute_seconds, clock=None):
        if type(idle_seconds) is not int or type(absolute_seconds) is not int or not 0 < idle_seconds <= absolute_seconds:
            raise ValueError("explicit session policy required")
        if not origins or any(urlsplit(o).scheme != "https" or not urlsplit(o).netloc or
                              urlsplit(o).path or urlsplit(o).query or urlsplit(o).fragment or
                              urlsplit(o).username or urlsplit(o).password or "*" in o for o in origins):
            raise ValueError("exact HTTPS browser origins required")
        self.engine, self.provider = store.engine, provider
        self.origins, self.idle, self.absolute = frozenset(origins), idle_seconds, absolute_seconds
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def audit(self, c, grant, action, outcome):
        c.execute(SecurityRow.__table__.insert().values(activity_id="activity:"+str(uuid4()),
            subject=grant.principal.principal_id if grant else None, action=action.value,
            outcome=outcome, occurred_at=self.clock().isoformat(),
            asset_ids=sorted(grant.principal.asset_ids) if grant else []))

    def establish(self, assertion):
        # Only a verified trusted adapter may interpret the opaque assertion.
        try:
            grant = self.provider.verify_assertion(assertion)
            if not isinstance(grant, IdentityGrant):
                raise EngineeringError("AUTHENTICATION_REQUIRED", 401)
            grant = IdentityGrant.model_validate(grant.model_dump())
            now = self.clock()
            if grant.valid_until <= now or not grant.principal.roles or len(grant.principal.asset_ids) > 1000:
                raise EngineeringError("AUTHENTICATION_REQUIRED", 401)
            token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            with self.provider.guard(grant.principal.principal_id, grant.version), self.engine.begin() as c:
                current = self.provider.current_grant(grant.principal.principal_id)
                if current != grant:
                    raise EngineeringError("IDENTITY_REVOKED", 401)
                c.execute(SessionRow.__table__.insert().values(token_hash=_hash(token), csrf_hash=_hash(csrf),
                    subject=grant.principal.principal_id, grant_version=grant.version, created_at=now.isoformat(),
                    last_seen_at=now.isoformat(), expires_at=min(now+timedelta(seconds=self.absolute),grant.valid_until).isoformat()))
                self.audit(c, grant, SecurityAction.SESSION_ESTABLISHED, "PASS")
            return token, csrf
        except EngineeringError:
            raise
        except Exception:
            raise EngineeringError("AUTHENTICATION_UNAVAILABLE", 503) from None

    def denial(self, code):
        allowed={"AUTHENTICATION_REQUIRED","SESSION_INVALID","IDENTITY_REVOKED","ORIGIN_DENIED","CSRF_DENIED","CONTENT_TYPE_DENIED"}
        try:
            with self.engine.begin() as c:
                self.audit(c,None,SecurityAction.ACCESS_DENIED,code if code in allowed else "DENIED")
        except SQLAlchemyError:
            raise EngineeringError("IDENTITY_STORE_UNAVAILABLE",503) from None

    @contextmanager
    def lease(self, token, *, method="GET", origin=None, csrf=None, content_type=None):
        if not isinstance(token, str) or not 40 <= len(token) <= 128:
            self.denial("AUTHENTICATION_REQUIRED")
            raise EngineeringError("AUTHENTICATION_REQUIRED", 401)
        try:
            with self.engine.begin() as c:
                row = c.execute(select(SessionRow.__table__).where(SessionRow.token_hash == _hash(token)).with_for_update()).mappings().first()
                now = self.clock()
                if row is None or row["revoked_at"] or datetime.fromisoformat(row["expires_at"]) <= now or                         datetime.fromisoformat(row["last_seen_at"])+timedelta(seconds=self.idle) <= now:
                    raise EngineeringError("SESSION_INVALID", 401)
                with self.provider.guard(row["subject"], row["grant_version"]):
                    grant = self.provider.current_grant(row["subject"])
                    if not isinstance(grant, IdentityGrant) or grant.version != row["grant_version"] or grant.valid_until <= now or not grant.principal.roles:
                        raise EngineeringError("IDENTITY_REVOKED", 401)
                    if method not in {"GET", "HEAD", "OPTIONS"}:
                        if origin not in self.origins:
                            raise EngineeringError("ORIGIN_DENIED", 403)
                        if not isinstance(csrf,str) or not 40 <= len(csrf) <= 128 or not compare_digest(row["csrf_hash"], _hash(csrf)):
                            raise EngineeringError("CSRF_DENIED", 403)
                        if content_type != "application/json":
                            raise EngineeringError("CONTENT_TYPE_DENIED", 415)
                    c.execute(update(SessionRow).where(SessionRow.token_hash == row["token_hash"]).values(last_seen_at=now.isoformat()))
                    self.audit(c, grant, SecurityAction.ACCESS_GRANTED, "PASS")
                    yield grant.principal
        except EngineeringError as error:
            self.denial(error.code)
            raise
        except SQLAlchemyError:
            raise EngineeringError("IDENTITY_STORE_UNAVAILABLE", 503) from None

    def dependency(self):
        async def trusted(request: Request):
            try:
                with self.lease(request.cookies.get(self.COOKIE), method=request.method,
                        origin=request.headers.get("origin"), csrf=request.headers.get("x-csrf-token"),
                        content_type=request.headers.get("content-type")) as principal:
                    yield principal
            except EngineeringError as error:
                raise HTTPException(error.status, detail={"code":error.code}) from None
        return trusted

    def set_cookie(self, response, token):
        response.set_cookie(self.COOKIE, token, secure=True, httponly=True, samesite="strict", path="/", max_age=self.absolute)
        response.headers["Cache-Control"] = "no-store"

    def revoke(self, actor: Principal, token):
        if not isinstance(actor, Principal) or not isinstance(token,str) or len(token) > 128:
            raise EngineeringError("FORBIDDEN",403)
        with self.engine.begin() as c:
            row=c.execute(select(SessionRow.__table__).where(SessionRow.token_hash==_hash(token)).with_for_update()).mappings().first()
            if not row:
                raise EngineeringError("NOT_FOUND",404)
            current=self.provider.current_grant(actor.principal_id)
            target=self.provider.current_grant(row["subject"])
            if not isinstance(current,IdentityGrant) or current.principal != actor or current.valid_until<=self.clock():
                raise EngineeringError("IDENTITY_REVOKED",401)
            own=actor.principal_id==row["subject"]
            if not own and (Role.ADMIN not in actor.roles or not isinstance(target,IdentityGrant) or not target.principal.asset_ids <= actor.asset_ids):
                raise EngineeringError("FORBIDDEN",403)
            with self.provider.guard(actor.principal_id,current.version):
                c.execute(update(SessionRow).where(SessionRow.token_hash==row["token_hash"]).values(revoked_at=self.clock().isoformat()))
                self.audit(c,current,SecurityAction.SESSION_REVOKED,"PASS")

    def activities(self, actor: Principal, *, offset=0, limit=50):
        if not isinstance(actor,Principal) or Role.ADMIN not in actor.roles or not 0<=offset<=10000 or not 1<=limit<=100:
            raise EngineeringError("FORBIDDEN",403)
        current=self.provider.current_grant(actor.principal_id)
        if not isinstance(current,IdentityGrant) or current.principal != actor or current.valid_until<=self.clock():
            raise EngineeringError("IDENTITY_REVOKED",401)
        # Denials/anonymous records are restricted to a future security custodian,
        # not exposed across scopes. SQL prefilter precedes bounded pagination.
        with self.provider.guard(actor.principal_id,current.version),self.engine.connect() as c:
            rows=c.execute(select(SecurityRow.__table__).where(SecurityRow.subject==actor.principal_id)
                .order_by(SecurityRow.occurred_at,SecurityRow.activity_id).offset(offset).limit(limit)).mappings()
            return [dict(row) for row in rows if set(row["asset_ids"])<=actor.asset_ids]
