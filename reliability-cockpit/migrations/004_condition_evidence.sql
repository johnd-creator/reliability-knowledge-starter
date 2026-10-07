-- NADI-ING-PI-001A: latest selected evidence in the existing Collector-owned Mart.
-- Apply ONLY through cockpit mart-migrate --apply with explicit owner DB preflight.
CREATE TABLE condition_signal_selection (
 signal_id varchar(200) PRIMARY KEY,
 mapping_id varchar(200) NOT NULL REFERENCES asset_af_mapping(id) ON DELETE RESTRICT,
 approval_status varchar(20) NOT NULL,
 definition jsonb NOT NULL,
 CONSTRAINT ck_condition_signal_status CHECK (approval_status IN ('APPROVED','RETIRED'))
);
CREATE INDEX ix_condition_signal_mapping ON condition_signal_selection(mapping_id,approval_status);
CREATE TABLE condition_evidence_latest (
 signal_id varchar(200) PRIMARY KEY REFERENCES condition_signal_selection(signal_id) ON DELETE RESTRICT,
 canonical_asset_id varchar(200) NOT NULL REFERENCES asset_master(canonical_id) ON DELETE RESTRICT,
 mapping_id varchar(200) NOT NULL REFERENCES asset_af_mapping(id) ON DELETE RESTRICT,
 collected_at timestamptz NOT NULL,
 projected_at timestamptz NOT NULL,
 evidence jsonb NOT NULL
);
CREATE INDEX ix_condition_evidence_asset ON condition_evidence_latest(canonical_asset_id,mapping_id);
CREATE TABLE condition_projection_state (
 canonical_asset_id varchar(200) PRIMARY KEY REFERENCES asset_master(canonical_id) ON DELETE RESTRICT,
 attempted_at timestamptz NOT NULL,
 state jsonb NOT NULL
);
