-- NADI Reliability Mart Contract v1.
-- Forward migration for PostgreSQL 16. Canonical IDs are the only logical
-- identities; relationship columns intentionally remain soft references.

CREATE TABLE IF NOT EXISTS asset_master (
    canonical_id          VARCHAR(200) PRIMARY KEY,
    contract_version      VARCHAR(10) NOT NULL,
    source_asset_number   VARCHAR(160),
    description           TEXT,
    status                VARCHAR(80),
    location_ref          VARCHAR(200),
    parent_asset_ref      VARCHAR(200),
    site_code             VARCHAR(40),
    organization_code     VARCHAR(40),
    asset_type            VARCHAR(120),
    plant                 VARCHAR(120),
    unit                  VARCHAR(120),
    criticality           JSONB,
    source_updated_at     TIMESTAMPTZ,
    provenance            JSONB NOT NULL,
    relationship_evidence JSONB NOT NULL,
    sources               JSONB,
    mart_created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mart_updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_asset_master_scope
    ON asset_master (site_code, organization_code);
CREATE INDEX IF NOT EXISTS ix_asset_master_source_number
    ON asset_master (source_asset_number);
CREATE INDEX IF NOT EXISTS ix_asset_master_unit
    ON asset_master (unit);

CREATE TABLE IF NOT EXISTS maintenance_event (
    canonical_id          VARCHAR(200) PRIMARY KEY,
    contract_version      VARCHAR(10) NOT NULL,
    id                    VARCHAR(200) NOT NULL,
    equipment_id          VARCHAR(200) NOT NULL,
    work_order_id         VARCHAR(200),
    event_type            VARCHAR(80),
    status                VARCHAR(80),
    actual_start          TIMESTAMPTZ,
    actual_finish         TIMESTAMPTZ,
    duration_hours        DOUBLE PRECISION,
    labor_hours           DOUBLE PRECISION,
    downtime_hours        DOUBLE PRECISION,
    failure_code          VARCHAR(200),
    reported_by           VARCHAR(120),
    lead                  VARCHAR(120),
    source_changed_at     TIMESTAMPTZ,
    site_code             VARCHAR(40),
    organization_code     VARCHAR(40),
    sources               JSONB,
    provenance            JSONB,
    relationship_evidence JSONB,
    mart_created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mart_updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_maintenance_event_scope_work_order
    ON maintenance_event (site_code, organization_code, work_order_id);
CREATE INDEX IF NOT EXISTS ix_maintenance_event_equipment
    ON maintenance_event (equipment_id);
CREATE INDEX IF NOT EXISTS ix_maintenance_event_actual_window
    ON maintenance_event (actual_start, actual_finish);

CREATE TABLE IF NOT EXISTS fmea_assessment (
    canonical_id          VARCHAR(200) PRIMARY KEY,
    contract_version      VARCHAR(10) NOT NULL,
    source_record_id      VARCHAR(160),
    source_number         VARCHAR(160),
    revision              VARCHAR(80),
    lifecycle_status      VARCHAR(80),
    description           TEXT,
    asset_ref             VARCHAR(200),
    failure_code_ref      VARCHAR(200),
    site_code             VARCHAR(40),
    organization_code     VARCHAR(40),
    source_updated_at     TIMESTAMPTZ,
    status_changed_at     TIMESTAMPTZ,
    provenance            JSONB NOT NULL,
    relationship_evidence JSONB NOT NULL,
    sources               JSONB,
    mart_created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mart_updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_fmea_assessment_asset ON fmea_assessment (asset_ref);
CREATE INDEX IF NOT EXISTS ix_fmea_assessment_scope_status
    ON fmea_assessment (site_code, lifecycle_status);
CREATE INDEX IF NOT EXISTS ix_fmea_assessment_source_number ON fmea_assessment (source_number);

CREATE TABLE IF NOT EXISTS rcfa_analysis (
    canonical_id          VARCHAR(200) PRIMARY KEY,
    contract_version      VARCHAR(10) NOT NULL,
    source_record_id      VARCHAR(160),
    source_number         VARCHAR(160),
    revision              VARCHAR(80),
    lifecycle_status      VARCHAR(80),
    category              VARCHAR(160),
    asset_ref             VARCHAR(200),
    location_ref          VARCHAR(200),
    workorder_ref         VARCHAR(200),
    failure_event_ref     VARCHAR(200),
    site_code             VARCHAR(40),
    organization_code     VARCHAR(40),
    source_created_at     TIMESTAMPTZ,
    requested_at          TIMESTAMPTZ,
    provenance            JSONB NOT NULL,
    relationship_evidence JSONB NOT NULL,
    sources               JSONB,
    mart_created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mart_updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_rcfa_analysis_scope_status
    ON rcfa_analysis (site_code, lifecycle_status);
CREATE INDEX IF NOT EXISTS ix_rcfa_analysis_source_number ON rcfa_analysis (source_number);

CREATE TABLE IF NOT EXISTS asset_health_assessment (
    canonical_id          VARCHAR(200) PRIMARY KEY,
    contract_version      VARCHAR(10) NOT NULL,
    source_record_id      VARCHAR(160),
    revision              VARCHAR(80),
    lifecycle_status      VARCHAR(80),
    description           TEXT,
    function_description  TEXT,
    asset_ref             VARCHAR(200),
    site_code             VARCHAR(40),
    organization_code     VARCHAR(40),
    source_created_at     TIMESTAMPTZ,
    source_updated_at     TIMESTAMPTZ,
    status_changed_at     TIMESTAMPTZ,
    provenance            JSONB NOT NULL,
    relationship_evidence JSONB NOT NULL,
    sources               JSONB,
    mart_created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mart_updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_asset_health_assessment_asset ON asset_health_assessment (asset_ref);
CREATE INDEX IF NOT EXISTS ix_asset_health_assessment_scope_status
    ON asset_health_assessment (site_code, lifecycle_status);

CREATE TABLE IF NOT EXISTS overhaul_event (
    canonical_id               VARCHAR(200) PRIMARY KEY,
    contract_version           VARCHAR(10) NOT NULL,
    source_record_id           VARCHAR(160),
    source_number              VARCHAR(160),
    lifecycle_status           VARCHAR(80),
    workorder_ref              VARCHAR(200),
    asset_ref                  VARCHAR(200),
    site_code                  VARCHAR(40),
    organization_code          VARCHAR(40),
    planned_start_at           TIMESTAMPTZ,
    planned_finish_at          TIMESTAMPTZ,
    actual_start_at            TIMESTAMPTZ,
    actual_finish_at           TIMESTAMPTZ,
    progress                   JSONB,
    source_created_at          TIMESTAMPTZ,
    source_updated_at          TIMESTAMPTZ,
    unresolved_source_attributes JSONB,
    provenance                 JSONB NOT NULL,
    relationship_evidence      JSONB NOT NULL,
    sources                    JSONB,
    mart_created_at            TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mart_updated_at            TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_overhaul_event_workorder ON overhaul_event (workorder_ref);
CREATE INDEX IF NOT EXISTS ix_overhaul_event_asset ON overhaul_event (asset_ref);
CREATE INDEX IF NOT EXISTS ix_overhaul_event_scope_status
    ON overhaul_event (site_code, lifecycle_status);
CREATE INDEX IF NOT EXISTS ix_overhaul_event_actual_start ON overhaul_event (actual_start_at);
