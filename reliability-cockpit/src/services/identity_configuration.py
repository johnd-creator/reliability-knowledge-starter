"""Source-free enterprise trust configuration. NOT a JWT/OIDC verifier.

Only a reviewed server verifier may call subject_ref after signature, issuer,
audience, time, nonce/state/PKCE and replay validation. This module performs no
discovery, token exchange, registration, secret loading or network access.
"""
from dataclasses import dataclass
from hashlib import sha256
from urllib.parse import urlsplit
import re


def exact_https_url(value, *, origin=False):
    if not isinstance(value, str) or not 1 <= len(value) <= 2048:
        raise ValueError("HTTPS_IDENTITY_URL_REQUIRED")
    p = urlsplit(value)
    if (p.scheme != "https" or not p.hostname or p.username or p.password
            or p.fragment or p.query or "*" in value or re.search(r"[\s\x00-\x1f]", value)
            or (origin and p.path not in ("", "/"))):
        raise ValueError("HTTPS_IDENTITY_URL_REQUIRED")
    try:
        p.port
    except ValueError:
        raise ValueError("HTTPS_IDENTITY_URL_REQUIRED") from None
    return value


@dataclass(frozen=True)
class OidcTrustConfiguration:
    issuer: str
    client_id: str
    redirect_uri: str
    logout_uri: str
    browser_origin: str
    algorithms: tuple[str, ...]
    provider_timeout_seconds: int

    def __post_init__(self):
        exact_https_url(self.issuer)
        exact_https_url(self.browser_origin, origin=True)
        origin = urlsplit(self.browser_origin)
        for uri in (self.redirect_uri, self.logout_uri):
            exact_https_url(uri)
            p = urlsplit(uri)
            if (p.scheme, p.netloc) != (origin.scheme, origin.netloc):
                raise ValueError("IDENTITY_CALLBACK_ORIGIN_MISMATCH")
        if (not isinstance(self.client_id, str) or not self.client_id.strip()
                or len(self.client_id) > 256 or re.search(r"[\s\x00-\x1f]", self.client_id)):
            raise ValueError("IDENTITY_CLIENT_REQUIRED")
        if (not isinstance(self.algorithms, tuple) or not self.algorithms
                or len(set(self.algorithms)) != len(self.algorithms)
                or not set(self.algorithms) <= {"RS256", "PS256", "ES256"}):
            raise ValueError("REVIEWED_ASYMMETRIC_ALGORITHM_REQUIRED")
        if type(self.provider_timeout_seconds) is not int or not 1 <= self.provider_timeout_seconds <= 30:
            raise ValueError("BOUNDED_PROVIDER_TIMEOUT_REQUIRED")

    def subject_ref(self, issuer: str, subject: str) -> str:
        """Derive a namespaced ID from ALREADY verified iss/sub, never email/name."""
        if issuer != self.issuer:
            raise ValueError("IDENTITY_ISSUER_MISMATCH")
        if (not isinstance(subject, str) or not 1 <= len(subject) <= 255
                or subject != subject.strip() or re.search(r"[\x00-\x1f]", subject)):
            raise ValueError("STABLE_SUBJECT_REQUIRED")
        return "oidc:" + sha256((issuer + "\x00" + subject).encode()).hexdigest()


@dataclass(frozen=True)
class SessionRuntimePolicy:
    idle_seconds: int
    absolute_seconds: int
    pool_size: int
    pool_timeout_seconds: int
    lease_capacity: int

    def __post_init__(self):
        if any(type(v) is not int for v in (
                self.idle_seconds, self.absolute_seconds, self.pool_size,
                self.pool_timeout_seconds, self.lease_capacity)):
            raise ValueError("EXPLICIT_SESSION_POLICY_REQUIRED")
        if (not 1 <= self.idle_seconds <= self.absolute_seconds <= 86400
                or not 1 <= self.pool_size <= 64
                or not 1 <= self.pool_timeout_seconds <= 30
                or not 1 <= self.lease_capacity <= 64):
            raise ValueError("BOUNDED_SESSION_POLICY_REQUIRED")

    def engine_options(self):
        return {"pool_size": self.pool_size, "max_overflow": 0,
                "pool_timeout": self.pool_timeout_seconds,
                "connect_args": {"connect_timeout": self.pool_timeout_seconds,
                                 "options": "-c statement_timeout=15000 -c lock_timeout=5000"}}
