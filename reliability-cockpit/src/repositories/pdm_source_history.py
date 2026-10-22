"""Compact immutable source proof in the existing owning application store."""
from sqlalchemy import (MetaData, Table, Column, String, Integer, JSON, ForeignKeyConstraint, Index)

metadata = MetaData()
Source = Table('nadi_history_source', metadata,
    Column('source_sha', String(64), primary_key=True), Column('document', JSON, nullable=False))
Profile = Table('nadi_history_profile', metadata,
    Column('profile_hash', String(64), primary_key=True), Column('document', JSON, nullable=False))
Cell = Table('nadi_history_cell', metadata,
    Column('source_sha', String(64), primary_key=True), Column('sheet_index', Integer, primary_key=True),
    Column('coordinate', String(20), primary_key=True), Column('terminal_role', String(40), nullable=False),
    Column('claims', JSON, nullable=False), Column('document', JSON, nullable=False),
    ForeignKeyConstraint(['source_sha'], [Source.c.source_sha]))
Event = Table('nadi_history_event', metadata,
    Column('event_key', String(64), primary_key=True), Column('owner_id', String(160), nullable=False),
    Column('access_asset_id', String(200), nullable=False), Column('source_sha', String(64), nullable=False),
    Column('source_ref', String(80), nullable=False), Column('sheet_index', Integer, nullable=False),
    Column('profile_id', String(160), nullable=False), Column('profile_hash', String(64), nullable=False),
    Column('axis', String(8), nullable=False), Column('position', Integer, nullable=False),
    Column('classification_hash', String(64), nullable=False), Column('kind', String(40), nullable=False),
    Column('classification', String(40), nullable=False), Column('document', JSON, nullable=False),
    ForeignKeyConstraint(['source_sha'], [Source.c.source_sha]), ForeignKeyConstraint(['profile_hash'], [Profile.c.profile_hash]))
Index('nadi_history_owner_page', Event.c.owner_id, Event.c.access_asset_id, Event.c.event_key)
Alias = Table('nadi_history_alias', metadata,
    Column('event_key', String(64), primary_key=True), Column('record_id', String(100), primary_key=True),
    Column('revision', Integer, primary_key=True), Column('capture_hash', String(64), nullable=False),
    Column('relation', String(40), nullable=False),
    ForeignKeyConstraint(['event_key'], [Event.c.event_key]))
Batch = Table('nadi_history_batch', metadata,
    Column('batch_id', String(64), primary_key=True), Column('owner_id', String(160), nullable=False),
    Column('access_asset_id', String(200), nullable=False), Column('manifest', JSON, nullable=False),
    Column('cursor', Integer, nullable=False), Column('state', String(20), nullable=False))
Receipt = Table('nadi_history_receipt', metadata,
    Column('batch_id', String(64), primary_key=True), Column('sequence', Integer, primary_key=True),
    Column('actor', String(160), nullable=False), Column('occurred_at', String(40), nullable=False),
    Column('fingerprint', String(64), nullable=False), Column('document', JSON, nullable=False),
    ForeignKeyConstraint(['batch_id'], [Batch.c.batch_id]))
TABLES = {t.name: t for t in (Source, Profile, Cell, Event, Alias, Batch, Receipt)}
KEYS = {t.name: tuple(c.name for c in t.primary_key) for t in TABLES.values()}
