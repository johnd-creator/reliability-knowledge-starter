-- MX-012R: current business Registry relation and local downstream state.
-- Both relations use logical references; they do not add a Contract v1 entity
-- or a hard foreign key to the technical Mart tables.

CREATE TABLE IF NOT EXISTS reliability_asset_registry (
    asset_ref             VARCHAR(200) PRIMARY KEY,
    source_asset_number   VARCHAR(160) NOT NULL,
    site_code             VARCHAR(40) NOT NULL,
    organization_code     VARCHAR(40) NOT NULL,
    registry_source       VARCHAR(120) NOT NULL,
    snapshot_sha256       VARCHAR(64) NOT NULL,
    snapshot_row_count    INTEGER NOT NULL,
    snapshot_imported_at  TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_reliability_asset_registry_source_number
    ON reliability_asset_registry (source_asset_number);
CREATE INDEX IF NOT EXISTS ix_reliability_asset_registry_scope
    ON reliability_asset_registry (site_code, organization_code);

CREATE TABLE IF NOT EXISTS mart_projection_state (
    projection_key   VARCHAR(80) PRIMARY KEY,
    watermark        TIMESTAMPTZ,
    last_status      VARCHAR(30) NOT NULL,
    last_success_at  TIMESTAMPTZ,
    rows_seen        INTEGER NOT NULL DEFAULT 0,
    rows_written     INTEGER NOT NULL DEFAULT 0,
    updated_at       TIMESTAMPTZ NOT NULL
);
