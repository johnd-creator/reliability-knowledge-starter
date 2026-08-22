"""Deterministic, scope-safe canonical identity helpers."""

from __future__ import annotations

from urllib.parse import quote


def _component(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"canonical identity requires {name}")
    return quote(text, safe="-._~")


def canonical_id(
    namespace: str,
    source_object: str,
    source_record_id: object,
    site: object,
    organization: object,
) -> str:
    """Build a stable identity without Python's process-randomized hash()."""
    return ":".join((
        _component(namespace, "namespace"),
        "MAXIMO",
        _component(source_object, "source_object").upper(),
        _component(site, "site"),
        _component(organization, "organization"),
        _component(source_record_id, "source_record_id"),
    ))


def scoped_reference(
    namespace: str,
    source_object: str,
    source_value: object,
    site: object,
    organization: object,
) -> str | None:
    """Return a scoped canonical reference, or null for an absent relation."""
    if source_value is None or not str(source_value).strip():
        return None
    return canonical_id(namespace, source_object, source_value, site, organization)
