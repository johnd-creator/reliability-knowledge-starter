"""Additive latest-only Mart storage; never part of the legacy Base."""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from src.repositories.mart_models import MartBase, _json

CONDITION_TABLES = ("condition_signal_selection", "condition_evidence_latest", "condition_projection_state")

class ConditionSignalSelectionMart(MartBase):
    __tablename__ = "condition_signal_selection"
    __table_args__ = (
        CheckConstraint("approval_status IN ('APPROVED','RETIRED')", name="ck_condition_signal_status"),
        Index("ix_condition_signal_mapping", "mapping_id", "approval_status"),
    )
    signal_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    mapping_id: Mapped[str] = mapped_column(String(200), ForeignKey("asset_af_mapping.id", ondelete="RESTRICT"), nullable=False)
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False)
    definition: Mapped[dict] = mapped_column(_json, nullable=False)

class ConditionEvidenceLatestMart(MartBase):
    __tablename__ = "condition_evidence_latest"
    __table_args__ = (Index("ix_condition_evidence_asset", "canonical_asset_id", "mapping_id"),)
    signal_id: Mapped[str] = mapped_column(String(200), ForeignKey("condition_signal_selection.signal_id", ondelete="RESTRICT"), primary_key=True)
    canonical_asset_id: Mapped[str] = mapped_column(String(200), ForeignKey("asset_master.canonical_id", ondelete="RESTRICT"), nullable=False)
    mapping_id: Mapped[str] = mapped_column(String(200), ForeignKey("asset_af_mapping.id", ondelete="RESTRICT"), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    projected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence: Mapped[dict] = mapped_column(_json, nullable=False)

class ConditionProjectionStateMart(MartBase):
    __tablename__ = "condition_projection_state"
    canonical_asset_id: Mapped[str] = mapped_column(String(200), ForeignKey("asset_master.canonical_id", ondelete="RESTRICT"), primary_key=True)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state: Mapped[dict] = mapped_column(_json, nullable=False)
