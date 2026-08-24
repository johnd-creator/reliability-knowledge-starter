-- NADI-MAP-001: NADI-owned governed Maximo Asset to PI AF identity registry.
--
-- Apply this migration to the existing Reliability Mart database configured by
-- RELIABILITY_MART_DATABASE_URL. It is not a migration for the legacy
-- Cockpit DATABASE_URL and it intentionally contains no production seed rows.

CREATE TABLE IF NOT EXISTS asset_af_mapping (
    id                         VARCHAR(200) PRIMARY KEY,
    canonical_asset_id         VARCHAR(200) NOT NULL,
    pi_source_id               VARCHAR(80) NOT NULL,
    af_server_ref               VARCHAR(200) NOT NULL,
    af_database_ref             VARCHAR(200) NOT NULL,
    af_element_ref              VARCHAR(200) NOT NULL,
    mapping_role                VARCHAR(40) NOT NULL,
    mapping_status              VARCHAR(20) NOT NULL,
    evidence_method             VARCHAR(40) NOT NULL,
    created_at                  TIMESTAMPTZ NOT NULL,
    updated_at                  TIMESTAMPTZ NOT NULL,
    verified_at                 TIMESTAMPTZ,
    retired_at                  TIMESTAMPTZ,
    source_assetnum_snapshot    VARCHAR(160),
    source_siteid_snapshot      VARCHAR(40),
    source_orgid_snapshot       VARCHAR(40),
    af_path_snapshot            VARCHAR(500),
    af_element_name_snapshot    VARCHAR(240),
    CONSTRAINT fk_asset_af_mapping_asset
        FOREIGN KEY (canonical_asset_id)
        REFERENCES asset_master (canonical_id)
        ON DELETE RESTRICT,
    CONSTRAINT ck_asset_af_mapping_status
        CHECK (mapping_status IN ('PROPOSED', 'VERIFIED', 'RETIRED')),
    CONSTRAINT ck_asset_af_mapping_role
        CHECK (mapping_role = 'PRIMARY_EQUIPMENT'),
    CONSTRAINT ck_asset_af_mapping_evidence
        CHECK (evidence_method IN (
            'NATIVE_IDENTIFIER',
            'GOVERNED_LOOKUP',
            'MANUAL_VERIFICATION',
            'MIGRATED_VERIFIED'
        ))
);

CREATE INDEX IF NOT EXISTS ix_asset_af_mapping_asset_status
    ON asset_af_mapping (canonical_asset_id, mapping_status);
CREATE INDEX IF NOT EXISTS ix_asset_af_mapping_af_element
    ON asset_af_mapping (af_element_ref);

-- Retired rows remain historical. Active proposals and verified mappings may
-- not duplicate the same Asset, AF Element, and role combination.
CREATE UNIQUE INDEX IF NOT EXISTS uq_asset_af_mapping_active_exact
    ON asset_af_mapping (canonical_asset_id, af_element_ref, mapping_role)
    WHERE mapping_status IN ('PROPOSED', 'VERIFIED');
