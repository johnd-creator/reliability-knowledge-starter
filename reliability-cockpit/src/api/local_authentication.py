"""Local login contract. Explicit isolated QA factory only; never operational mounting."""
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import SecretStr, StrictStr, Field
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import EngineeringError
from src.services.local_authentication import LocalIdentityProvider


class LoginInput(EvidenceModel):
    username: StrictStr = Field(min_length=1, max_length=64)
    password: SecretStr
    new_password: SecretStr | None = None


def build_local_login_router(authority, *, enabled=False):
    router = APIRouter(prefix="/v1/engineering/auth")
    if not enabled:
        return router
    if not isinstance(authority.provider, LocalIdentityProvider):
        raise EngineeringError("LOCAL_DIRECTORY_REQUIRED", 503)

    @router.post("/login")
    def login(body: LoginInput, request: Request, response: Response):
        # Login CSRF: exact trusted HTTPS Origin + JSON, no cross-site form/fallback.
        if request.headers.get("origin") not in authority.origins:
            raise HTTPException(403, detail={"code":"ORIGIN_DENIED"})
        if request.headers.get("content-type") != "application/json":
            raise HTTPException(415, detail={"code":"CONTENT_TYPE_DENIED"})
        try:
            grant = authority.provider.authenticate(body.username, body.password.get_secret_value(),
                new_password=body.new_password.get_secret_value() if body.new_password is not None else None)
            token, csrf = authority.establish_verified(grant)
            authority.set_cookie(response, token)
            return {"csrf_token":csrf}
        except EngineeringError as error:
            raise HTTPException(error.status, detail={"code":error.code}) from None
        except Exception:
            raise HTTPException(503, detail={"code":"AUTHENTICATION_UNAVAILABLE"}) from None
    return router
