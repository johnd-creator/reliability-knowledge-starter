#!/usr/bin/env python3
"""Shared configuration for the PI collector.

All secrets come from the environment (or a local .env) — never from source
control. The collector never stores production credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def load_env() -> None:
    """Load .env from the repo root and from the user home, if present."""
    _load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    _load_dotenv(Path.home() / ".pi-collector.env")


@dataclass(frozen=True)
class PiApiConfig:
    base_url: str
    timeout_seconds: int = 30
    rate_limit_seconds: float = 1.0
    max_response_bytes: int = 1_048_576
    verify_tls: bool = True
    username: str | None = None
    password: str | None = None
    token: str | None = None

    @classmethod
    def from_environment(cls) -> "PiApiConfig":
        return cls(
            base_url=os.getenv("PI_WEB_API_BASE_URL", "https://pivision.plnindonesiapower.co.id/piwebapi").rstrip("/"),
            timeout_seconds=int(os.getenv("PI_TIMEOUT_SECONDS", "30")),
            rate_limit_seconds=float(os.getenv("PI_RATE_LIMIT_SECONDS", "1.0")),
            max_response_bytes=int(os.getenv("PI_MAX_RESPONSE_BYTES", str(1_048_576))),
            verify_tls=os.getenv("PI_VERIFY_TLS", "1") == "1",
            username=os.getenv("PI_USERNAME") or None,
            password=os.getenv("PI_PASSWORD") or None,
            token=os.getenv("PI_TOKEN") or None,
        )

    def auth_kwargs(self) -> dict:
        if self.username and self.password is not None:
            return {"auth": (self.username, self.password)}
        if self.token:
            return {"headers": {"Authorization": f"Bearer {self.token}"}}
        return {}


@dataclass(frozen=True)
class DbConfig:
    dsn: str = "postgresql+psycopg://picollector:picollector@localhost:5433/picollector"
    echo: bool = False

    @classmethod
    def from_environment(cls) -> "DbConfig":
        default_dsn = "postgresql+psycopg://picollector:picollector@localhost:5433/picollector"
        return cls(
            dsn=os.getenv("DATABASE_URL", default_dsn),
            echo=os.getenv("DATABASE_ECHO", "0") == "1",
        )


@dataclass(frozen=True)
class CollectSafetyConfig:
    """Safety guardrails for bulk backfill operations against PI.

    These exist to prevent the collector from overwhelming the PI server:
      * max_requests_per_session: hard stop after N API calls (circuit breaker)
      * chunk_days: split long ranges into N-day windows to keep responses small
      * max_consecutive_errors: abort after N errors in a row (server may be down)
      * pause_between_attributes: extra cooldown between attributes
      * off_hours_start / off_hours_end: only allow heavy backfill during these hours
      * off_hours_weekend: allow backfill on Saturday/Sunday anytime
      * snapshot_interval_seconds: expected snapshot cycle (seconds) — drives
        the /schedule countdown in the web UI; aligns with cron */5 or
        ``picollector run --interval-seconds``
    """
    max_requests_per_session: int = 5000
    chunk_days: int = 7
    max_consecutive_errors: int = 10
    pause_between_attributes_seconds: float = 2.0
    off_hours_start: int = 22  # 22:00 local
    off_hours_end: int = 6    # until 06:00 local
    off_hours_weekend: bool = True
    snapshot_interval_seconds: int = 300

    @classmethod
    def from_environment(cls) -> "CollectSafetyConfig":
        return cls(
            max_requests_per_session=int(os.getenv("PI_MAX_REQUESTS_PER_SESSION", "5000")),
            chunk_days=int(os.getenv("PI_BACKFILL_CHUNK_DAYS", "7")),
            max_consecutive_errors=int(os.getenv("PI_MAX_CONSECUTIVE_ERRORS", "10")),
            pause_between_attributes_seconds=float(os.getenv("PI_PAUSE_BETWEEN_ATTRIBUTES", "2.0")),
            off_hours_start=int(os.getenv("PI_OFF_HOURS_START", "22")),
            off_hours_end=int(os.getenv("PI_OFF_HOURS_END", "6")),
            off_hours_weekend=os.getenv("PI_OFF_HOURS_WEEKEND", "1") == "1",
            snapshot_interval_seconds=int(
                os.getenv("PI_SNAPSHOT_INTERVAL_SECONDS", "300")
            ),
        )

    def is_off_hours(self, now: datetime | None = None) -> bool:
        """Check if current time is within the allowed off-hours window."""
        from datetime import datetime as _dt

        moment = now or _dt.now()
        hour = moment.hour
        is_weekend = moment.weekday() >= 5  # Saturday=5, Sunday=6

        if is_weekend and self.off_hours_weekend:
            return True
        if self.off_hours_start > self.off_hours_end:
            # wraps midnight, e.g. 22:00–06:00
            return hour >= self.off_hours_start or hour < self.off_hours_end
        return self.off_hours_start <= hour < self.off_hours_end


@dataclass(frozen=True)
class AppConfig:
    pi: PiApiConfig = field(default_factory=PiApiConfig.from_environment)
    db: DbConfig = field(default_factory=DbConfig.from_environment)
    safety: CollectSafetyConfig = field(default_factory=CollectSafetyConfig.from_environment)
    registry_path: str = "../pi-knowledge/mappings/bsr1-parameters.yaml"

    @classmethod
    def from_environment(cls) -> "AppConfig":
        return cls(
            pi=PiApiConfig.from_environment(),
            db=DbConfig.from_environment(),
            safety=CollectSafetyConfig.from_environment(),
            registry_path=os.getenv(
                "PI_REGISTRY_PATH",
                "../pi-knowledge/mappings/bsr1-parameters.yaml",
            ),
        )
