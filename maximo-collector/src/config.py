"""Configuration loaded from environment / .env (never committed)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # optional; tests may run without python-dotenv installed
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):  # type: ignore[misc]
        return False

_REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class MaximoConfig:
    base_url: str = "http://maximo.plnindonesiapower.co.id/maximo"
    oslc_root: str = "/oslc/os"
    site_id: str = "BSR"
    org_id: str = "IP"
    auth_mode: str = "login"  # "login" | "token" | "cookie"
    username: str | None = None
    password: str | None = None
    token: str | None = None
    session_cookie: str | None = None
    # The BSR Maximo application can take more than five seconds to return an
    # OSLC page/detail response. Keep the response wait bounded, but separate
    # it from the inter-request safety throttle.
    timeout_seconds: int = 30
    rate_limit_seconds: float = 1.0
    page_size: int = 100
    max_response_bytes: int = 1_048_576

    def validate_runtime_safety(self) -> "MaximoConfig":
        """Validate environment-loaded settings before any production request."""
        if self.site_id != "BSR":
            raise ValueError("maximo-collector only permits MAXIMO_SITE_ID=BSR")
        if self.org_id != "IP":
            raise ValueError("maximo-collector only permits MAXIMO_ORG_ID=IP")
        if self.rate_limit_seconds < 1.0:
            raise ValueError("maximo-collector requires MAXIMO_RATE_LIMIT_SECONDS >= 1.0")
        if self.max_response_bytes > 1_048_576:
            raise ValueError("maximo-collector response cap cannot exceed 1 MiB")
        return self

    @classmethod
    def from_environment(cls) -> "MaximoConfig":
        return cls(
            base_url=os.getenv("MAXIMO_BASE_URL", cls.base_url).rstrip("/"),
            oslc_root=os.getenv("MAXIMO_OSLC_ROOT", "/oslc/os"),
            site_id=os.getenv("MAXIMO_SITE_ID", "BSR"),
            org_id=os.getenv("MAXIMO_ORG_ID", "IP"),
            auth_mode=os.getenv("MAXIMO_AUTH_MODE", "login"),
            username=os.getenv("MAXIMO_USERNAME") or None,
            password=os.getenv("MAXIMO_PASSWORD") or None,
            token=os.getenv("MAXIMO_READ_ONLY_TOKEN") or None,
            session_cookie=os.getenv("MAXIMO_SESSION_COOKIE") or None,
            timeout_seconds=int(os.getenv("MAXIMO_TIMEOUT_SECONDS", "30")),
            rate_limit_seconds=float(os.getenv("MAXIMO_RATE_LIMIT_SECONDS", "1.0")),
            page_size=int(os.getenv("MAXIMO_PAGE_SIZE", "100")),
            max_response_bytes=int(os.getenv("MAXIMO_MAX_RESPONSE_BYTES", str(1_048_576))),
        ).validate_runtime_safety()


@dataclass(frozen=True)
class DbConfig:
    dsn: str = "postgresql+psycopg://mxcollector:mxcollector@localhost:5434/mxcollector"
    echo: bool = False

    @classmethod
    def from_environment(cls) -> "DbConfig":
        return cls(
            dsn=os.getenv("DATABASE_URL", cls.dsn),
            echo=os.getenv("DATABASE_ECHO", "0") == "1",
        )


def load_env() -> None:
    """Load .env from the repo root and the user home override, if present."""
    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv(Path.home() / ".maximo-collector.env")
