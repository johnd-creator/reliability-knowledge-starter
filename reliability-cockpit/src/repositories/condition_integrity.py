"""Read-only checks binding stored JSON evidence to canonical row identities.

A partial restore or inconsistent stored document cannot supply replacement
identity, provenance or successful projection state. No records are repaired here.
"""
from datetime import datetime, timezone
from src.domain.condition_evidence import ConditionEvidence, SignalSelection


def utc_timestamp(value):
    # SQLite drops timezone metadata for DateTime columns; canonical PostgreSQL
    # stores aware times. Preserve the instant of any supplied aware timestamp.
    if not isinstance(value, datetime):
        raise ValueError('stored timestamp required')
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def stored_selection(row, mapping_id):
    signal = SignalSelection.model_validate(row.definition)
    if (row.mapping_id != mapping_id or signal.mapping_id != mapping_id
            or signal.signal_id != row.signal_id
            or row.approval_status != 'APPROVED' or signal.approval_status != 'APPROVED'):
        raise ValueError('stored selection identity differs')
    return signal


def stored_evidence(row, asset_id, mapping_id, signal, lineage):
    evidence = ConditionEvidence.model_validate(row.evidence)
    if (row.canonical_asset_id != asset_id or evidence.canonical_asset_id != asset_id
            or row.mapping_id != mapping_id or evidence.mapping_id != mapping_id
            or row.signal_id != signal.signal_id or evidence.signal_id != row.signal_id
            or utc_timestamp(row.collected_at) != evidence.collected_at
            or evidence.sources.pi.model_dump(exclude={'attribute_ref', 'attribute_name'}) != lineage.model_dump()
            or evidence.attribute_ref != signal.attribute_ref or evidence.semantic_name != signal.semantic_name
            or evidence.provenance.selection_evidence_ref != signal.evidence_ref
            or evidence.provenance.selection_approved_by != signal.approved_by
            or evidence.provenance.selection_approved_at != signal.approved_at):
        raise ValueError('stored evidence identity or provenance differs')
    return evidence


def stored_projection_state(row, mapping_id, evidence_rows=()):
    state = row.state if row is not None else None
    if not isinstance(state, dict) or state.get('mapping_id') != mapping_id:
        return None
    statuses = state.get('statuses')
    supported = {'PROJECTED', 'PARTIAL_SIGNAL_SET', 'SOURCE_UNAVAILABLE', 'PROJECTION_ERROR'}
    if not isinstance(statuses, list) or not statuses or any(not isinstance(x, str) or x not in supported for x in statuses):
        return None
    try:
        attempt = utc_timestamp(row.attempted_at)
        if any(utc_timestamp(e.collected_at) > attempt for e in evidence_rows):
            return None
    except (ValueError, TypeError):
        return None
    return state
