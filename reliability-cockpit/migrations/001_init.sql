-- Cockpit local store (NOT production). Matches src/repositories/models.py
-- and reliability-data-contracts field names.

CREATE TABLE IF NOT EXISTS equipment (
    id                   VARCHAR(80)  PRIMARY KEY,          -- assetnum
    name                 VARCHAR(200),
    description          TEXT,
    location_id          VARCHAR(80),
    equipment_class      VARCHAR(40),
    unit                 VARCHAR(40),
    status               VARCHAR(40),
    status_description   VARCHAR(80),
    is_running           BOOLEAN,
    priority             INTEGER,
    parent_id            VARCHAR(80),
    ancestor_id          VARCHAR(80),
    has_children         BOOLEAN,
    failure_code         VARCHAR(40),
    is_safety_critical   BOOLEAN,
    is_calibration       BOOLEAN,
    installed_at         TIMESTAMPTZ,
    status_changed_at    TIMESTAMPTZ,
    source_changed_at    TIMESTAMPTZ,
    purchase_price       NUMERIC(18,2),
    replacement_cost     NUMERIC(18,2),
    total_cost           NUMERIC(18,2),
    downtime_total_hours DOUBLE PRECISION,
    manufacturer         VARCHAR(120),
    vendor               VARCHAR(120),
    src_assetid          INTEGER,
    src_siteid           VARCHAR(20),
    src_orgid            VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS work_order (
    id                      VARCHAR(80) PRIMARY KEY,        -- wonum
    equipment_id            VARCHAR(80),
    location_id             VARCHAR(80),
    status                  VARCHAR(40),
    status_description      VARCHAR(80),
    work_type               VARCHAR(40),
    work_class              VARCHAR(40),
    description             TEXT,
    reported_at             TIMESTAMPTZ,
    source_changed_at       TIMESTAMPTZ,
    status_changed_at       TIMESTAMPTZ,
    scheduled_start         TIMESTAMPTZ,
    scheduled_finish        TIMESTAMPTZ,
    target_completion       TIMESTAMPTZ,
    estimated_duration_hours DOUBLE PRECISION,
    downtime_hours          DOUBLE PRECISION,
    priority                VARCHAR(20),
    priority_description    VARCHAR(80),
    reported_by             VARCHAR(40),
    supervisor              VARCHAR(40),
    lead                    VARCHAR(40),
    failure_code            VARCHAR(40),
    is_task                 BOOLEAN,
    parent_wo               VARCHAR(80),
    has_children            BOOLEAN,
    estimated_labor_cost    NUMERIC(18,2),
    estimated_material_cost NUMERIC(18,2),
    actual_labor_cost       NUMERIC(18,2),
    actual_material_cost    NUMERIC(18,2),
    actual_labor_hours      DOUBLE PRECISION,
    src_workorderid         INTEGER
);
CREATE INDEX IF NOT EXISTS ix_work_order_equipment_id ON work_order (equipment_id);
CREATE INDEX IF NOT EXISTS ix_work_order_source_changed_at ON work_order (source_changed_at);

CREATE TABLE IF NOT EXISTS service_request (
    id                    VARCHAR(80) PRIMARY KEY,          -- ticketid
    description           TEXT,
    status                VARCHAR(40),
    status_description    VARCHAR(80),
    work_type             VARCHAR(40),
    equipment_id          VARCHAR(80),
    location_id           VARCHAR(80),
    reported_by           VARCHAR(40),
    reported_by_name      VARCHAR(120),
    reported_at           TIMESTAMPTZ,
    source_changed_at     TIMESTAMPTZ,
    affected_at           TIMESTAMPTZ,
    actual_start          TIMESTAMPTZ,
    actual_finish         TIMESTAMPTZ,
    target_start          TIMESTAMPTZ,
    target_finish         TIMESTAMPTZ,
    internal_priority     VARCHAR(20),
    reported_priority     VARCHAR(20),
    actual_labor_hours    DOUBLE PRECISION,
    actual_labor_cost     NUMERIC(18,2),
    risk_area_environment VARCHAR(80),
    risk_area_process     VARCHAR(80),
    risk_area_human       VARCHAR(80),
    risk_area_reputation  VARCHAR(80),
    class_label           VARCHAR(40),
    src_ticketuid         INTEGER
);
CREATE INDEX IF NOT EXISTS ix_service_request_equipment_id ON service_request (equipment_id);
CREATE INDEX IF NOT EXISTS ix_service_request_source_changed_at ON service_request (source_changed_at);

CREATE TABLE IF NOT EXISTS person (
    id                 VARCHAR(40) PRIMARY KEY,             -- personid
    display_name       VARCHAR(160),
    first_name         VARCHAR(120),
    status             VARCHAR(40),
    status_changed_at  TIMESTAMPTZ,
    location_org       VARCHAR(80)
);

CREATE TABLE IF NOT EXISTS item (
    id                  VARCHAR(80) PRIMARY KEY,            -- itemnum
    description         TEXT,
    status              VARCHAR(40),
    item_type           VARCHAR(40),
    lot_type            VARCHAR(40),
    issue_unit          VARCHAR(20),
    order_unit          VARCHAR(20),
    is_rotating         BOOLEAN,
    is_kit              BOOLEAN,
    is_crew             BOOLEAN,
    inspection_required BOOLEAN,
    meter_name          VARCHAR(40),
    item_set_id         VARCHAR(40),
    status_changed_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS labor (
    id                        VARCHAR(40) PRIMARY KEY,      -- laborcode
    person_id                 VARCHAR(40),
    status                    VARCHAR(40),
    status_description        VARCHAR(80),
    work_site                 VARCHAR(80),
    is_assigned               BOOLEAN,
    availability_factor       DOUBLE PRECISION,
    reported_hours            DOUBLE PRECISION,
    year_to_date_other_hours  DOUBLE PRECISION,
    year_to_date_refused_hours DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS reliability_kpi (
    id           VARCHAR(120) PRIMARY KEY,
    equipment_id VARCHAR(80),
    metric       VARCHAR(40),
    value        DOUBLE PRECISION,
    unit         VARCHAR(20),
    period_start DATE,
    period_end   DATE,
    computed_at  TIMESTAMPTZ,
    inputs_json  TEXT,
    CONSTRAINT uq_kpi_scope UNIQUE (equipment_id, metric, period_start, period_end)
);
CREATE INDEX IF NOT EXISTS ix_reliability_kpi_equipment_id ON reliability_kpi (equipment_id);

CREATE TABLE IF NOT EXISTS sync_cursor (
    object_structure VARCHAR(60) PRIMARY KEY,
    last_changedate  TIMESTAMPTZ,
    last_synced_at   TIMESTAMPTZ,
    rows_seen        INTEGER
);