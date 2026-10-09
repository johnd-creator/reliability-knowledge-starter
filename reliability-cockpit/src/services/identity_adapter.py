"""Enterprise seam: verified subject from verifier, roles/scopes from directory.
Verifier enforces signature/issuer/audience/expiry/nonce/state/PKCE/replay.
Directory guard serializes revocation with authorized commits. No header trust.
"""
from typing import Protocol
from src.domain.engineering import EngineeringError
from src.services.application_identity import IdentityGrant
class AssertionVerifier(Protocol):
    def subject(self, proof: str) -> str: ...
class GrantDirectory(Protocol):
    def current_grant(self, subject: str) -> IdentityGrant | None: ...
    def guard(self, subject: str, version: int): ...
class EnterpriseIdentityAdapter:
    def __init__(self, verifier: AssertionVerifier, directory: GrantDirectory):
        self.verifier, self.directory = verifier, directory
    def verify_assertion(self, assertion):
        if not isinstance(assertion,str) or not 1<=len(assertion)<=8192:
            raise EngineeringError('AUTHENTICATION_REQUIRED',401)
        try:
            subject=self.verifier.subject(assertion)
            if not isinstance(subject,str) or not 1<=len(subject)<=160:
                raise EngineeringError('AUTHENTICATION_REQUIRED',401)
            grant=self.directory.current_grant(subject)
            if not isinstance(grant,IdentityGrant) or grant.principal.principal_id!=subject:
                raise EngineeringError('AUTHENTICATION_REQUIRED',401)
            return IdentityGrant.model_validate(grant.model_dump())
        except EngineeringError: raise
        except Exception: raise EngineeringError('AUTHENTICATION_UNAVAILABLE',503) from None
    def current_grant(self,subject): return self.directory.current_grant(subject)
    def guard(self,subject,version): return self.directory.guard(subject,version)
