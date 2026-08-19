"""Programmatic Maximo login (authentication, not data mutation).

Recipe: maximo-knowledge/docs/authentication.md — the downstream app may POST
/j_security_check ONCE to obtain a session cookie, then issue GET-only OSLC
requests. Cookies live in the requests.Session (memory only); they are never
logged or persisted.

Safety:
  * Only ever POSTs to the exact login path — never to /oslc/*.
  * Rate-limited like every other request.
  * On failure: one clear error, no retry loop (anti brute-force).
"""

from __future__ import annotations

import logging
import time
from urllib.parse import urljoin

import requests

from src.config import MaximoConfig

LOG = logging.getLogger(__name__)

LOGIN_PATH = "/j_security_check"
_LOGIN_MARKER = "j_security_check"
_LOGIN_PAGE_MARKERS = ("login.jsp", "loginerror.jsp", "j_security_check")


class MaximoAuthError(RuntimeError):
    """Login failed (bad credentials, server unavailable, or login page loop)."""


class MaximoAuth:
    """Obtains and transparently refreshes a Maximo web session."""

    def __init__(self, config: MaximoConfig, session: requests.Session | None = None):
        self._config = config
        self._session = session or requests.Session()
        self._last_request = 0.0
        self._logged_in = False

    @property
    def logged_in(self) -> bool:
        return self._logged_in

    @property
    def session(self) -> requests.Session:
        """The in-memory session that owns the authentication cookies."""
        return self._session

    @property
    def last_request_at(self) -> float:
        """Monotonic timestamp of the last login/auth request."""
        return self._last_request

    # -- login -------------------------------------------------------------
    def ensure_logged_in(self, *, force: bool = False) -> None:
        """Log in if needed (or forced). Idempotent within a session."""
        if self._logged_in and not force:
            return
        if self._config.auth_mode == "cookie" or self._config.session_cookie:
            if not self._config.session_cookie:
                raise MaximoAuthError(
                    "MAXIMO_AUTH_MODE=cookie requires MAXIMO_SESSION_COOKIE"
                )
            # Out-of-band session cookies are runtime-only and never logged.
            self._session.headers["Cookie"] = self._config.session_cookie
            self._logged_in = True
            return
        if self._config.auth_mode == "token":
            # bearer mode: no login handshake at all
            if not self._config.token:
                raise MaximoAuthError("MAXIMO_AUTH_MODE=token but MAXIMO_READ_ONLY_TOKEN is empty")
            self._session.headers["Authorization"] = f"Bearer {self._config.token}"
            self._logged_in = True
            return
        if not self._config.username or not self._config.password:
            raise MaximoAuthError(
                "MAXIMO_AUTH_MODE=login requires MAXIMO_USERNAME and MAXIMO_PASSWORD in the environment"
            )
        self._post_login()

    def _post_login(self) -> None:
        self._rate_limit()
        url = urljoin(self._config.base_url + "/", LOGIN_PATH.lstrip("/"))
        try:
            resp = self._session.post(
                url,
                data={
                    "j_username": self._config.username,
                    "j_password": self._config.password,
                },
                headers={"Accept": "text/html"},
                timeout=self._config.timeout_seconds,
                allow_redirects=True,
            )
        except requests.RequestException as error:
            raise MaximoAuthError(f"Maximo login request failed: {error}") from error
        self._last_request = time.monotonic()

        if len(resp.content) > self._config.max_response_bytes:
            raise MaximoAuthError(
                "Maximo login response exceeded the 1 MiB safety cap"
            )

        if not self._has_session_cookie():
            raise MaximoAuthError(
                "Maximo login did not return a session cookie — check credentials "
                "(HTTP %s)" % resp.status_code
            )
        if self._is_login_page(resp):
            # server re-served the login form: credentials rejected
            raise MaximoAuthError(
                "Maximo login rejected — check MAXIMO_USERNAME / MAXIMO_PASSWORD "
                "(read-only account)"
            )
        self._logged_in = True
        LOG.info("Maximo programmatic login OK (session cookie in memory)")

    def _has_session_cookie(self) -> bool:
        return any(
            c.name in ("JSESSIONID", "LtpaToken2")
            for c in self._session.cookies
        )

    @staticmethod
    def _is_login_page(resp: requests.Response) -> bool:
        if resp.status_code in (401, 403):
            return True
        response_url = str(getattr(resp, "url", "")).lower()
        location = resp.headers.get("Location", "").lower()
        if any(marker in response_url or marker in location for marker in _LOGIN_PAGE_MARKERS):
            return True
        content_type = resp.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            return False
        body = resp.text[:4096].lower()
        return any(marker in body for marker in _LOGIN_PAGE_MARKERS)

    # -- expiry detection ----------------------------------------------------
    @staticmethod
    def looks_expired(resp: requests.Response) -> bool:
        """Heuristic: response indicates the session is no longer valid."""
        if resp.status_code in (401, 403):
            return True
        if resp.status_code in (301, 302):
            location = resp.headers.get("Location", "")
            return "login" in location.lower()
        content_type = resp.headers.get("Content-Type", "")
        if "html" in content_type.lower():
            return "login" in resp.text[:4096].lower()
        return False

    def handle_expiry(self) -> None:
        """Called when a data request looked expired: force a fresh login."""
        LOG.warning("Maximo session looked expired — re-login (once)")
        self._session.cookies.clear()
        if self._session.headers.get("Authorization"):
            del self._session.headers["Authorization"]
        if self._session.headers.get("Cookie"):
            del self._session.headers["Cookie"]
        self._logged_in = False
        self.ensure_logged_in(force=True)

    # -- shared guardrails -----------------------------------------------------
    def _rate_limit(self) -> None:
        delay = self._config.rate_limit_seconds - (time.monotonic() - self._last_request)
        if delay > 0:
            time.sleep(delay)
