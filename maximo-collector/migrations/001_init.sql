-- maximo-collector local store (contract-shaped; mirrors src/repositories/models.py).
-- Column names follow reliability-data-contracts; vendor values quarantined in sources JSONB.

CREATE TABLE IF NOT EXISTS equipment (
    id                   VARCHAR(60) PRIMARY KEY,
    name                 TEXT,
    description          TEXT,
    location_id          VARCHAR(60),
    equipment_class      VARCHAR(40),
    unit                 VARCHAR(40),
    status               VARCHAR(30),
    status_description   TEXT,
    is_running           BOOLEAN,
    priority             INTEGER,
    parent_id            VARCHAR(60),
    ancestor_id          VARCHAR(60),
    has_children         BOOLEAN,
    failure_code         VARCHAR(60),
    is_safety_critical   BOOLEAN,
    is_calibration       BOOLEAN,
    installed_at         TIMESTAMPTZ,
    status_changed_at    TIMESTAMPTZ,
    source_changed_at    TIMESTAMPTZ,
    purchase_price       DOUBLE PRECISION,
    replacement_cost     DOUBLE PRECISION,
    total_cost           DOUBLE PRECISION,
    downtime_total_hours DOUBLE PRECISION,
    manufacturer         TEXT,
    vendor               TEXT,
    sources              JSONB
);
CREATE INDEX IF NOT EXISTS ix_equipment_changed ON equipment (source_changed_at);

CREATE TABLE IF NOT EXISTS equipment_status_history (
    id                 SERIAL PRIMARY KEY,
    equipment_id       VARCHAR(60) NOT NULL,
    status             VARCHAR(30),
    status_description TEXT,
    is_running         BOOLEAN,
    status_changed_at  TIMESTAMPTZ,
    source_changed_at  TIMESTAMPTZ,
    captured_at        TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_equipment_status_history_asset
    ON equipment_status_history (equipment_id, id DESC);

CREATE TABLE IF NOT EXISTS work_order (
    id                        VARCHAR(60) PRIMARY KEY,
    equipment_id              VARCHAR(60),
    location_id               VARCHAR(60),
    status                    VARCHAR(30),
    status_description        TEXT,
    work_type                 VARCHAR(20),
    work_class                VARCHAR(20),
    description               TEXT,
    reported_at               TIMESTAMPTZ,
    source_changed_at         TIMESTAMPTZ,
    status_changed_at         TIMESTAMPTZ,
    scheduled_start           TIMESTAMPTZ,
    scheduled_finish          TIMESTAMPTZ,
    target_completion         TIMESTAMPTZ,
    estimated_duration_hours  DOUBLE PRECISION,
    downtime_hours            DOUBLE PRECISION,
    priority                  VARCHAR(20),
    priority_description      TEXT,
    reported_by               VARCHAR(60),
    supervisor                VARCHAR(60),
    lead                      VARCHAR(60),
    failure_code              VARCHAR(60),
    is_task                   BOOLEAN,
    parent_wo                 VARCHAR(60),
    has_children              BOOLEAN,
    estimated_labor_cost      DOUBLE PRECISION,
    estimated_material_cost   DOUBLE PRECISION,
    actual_labor_cost         DOUBLE PRECISION,
    actual_material_cost      DOUBLE PRECISION,
    actual_labor_hours        DOUBLE PRECISION,
    sources                   JSONB
);
CREATE INDEX IF NOT EXISTS ix_work_order_changed ON work_order (source_changed_at);
CREATE INDEX IF NOT EXISTS ix_work_order_equipment ON work_order (equipment_id);

CREATE TABLE IF NOT EXISTS service_request (
    id                    VARCHAR(60) PRIMARY KEY,
    description           TEXT,
    status                VARCHAR(30),
    status_description    TEXT,
    work_type             VARCHAR(20),
    equipment_id          VARCHAR(60),
    location_id           VARCHAR(60),
    reported_by           VARCHAR(60),
    reported_by_name      TEXT,
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
    actual_labor_cost     DOUBLE PRECISION,
    risk_area_environment TEXT,
    risk_area_process     TEXT,
    risk_area_human       TEXT,
    risk_area_reputation  TEXT,
    class_label           TEXT,
    status_changed_at     TIMESTAMPTZ,
    sources               JSONB
);
CREATE INDEX IF NOT EXISTS ix_service_request_changed ON service_request (source_changed_at);

CREATE TABLE IF NOT EXISTS person (
    id                 VARCHAR(60) PRIMARY KEY,
    display_name       TEXT,
    first_name         TEXT,
    status             VARCHAR(30),
    status_changed_at  TIMESTAMPTZ,
    location_org       VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS item (
    id                   VARCHAR(60) PRIMARY KEY,
    description          TEXT,
    status               VARCHAR(30),
    item_type            VARCHAR(20),
    lot_type             VARCHAR(20),
    issue_unit           VARCHAR(20),
    order_unit           VARCHAR(20),
    is_rotating          BOOLEAN,
    is_kit               BOOLEAN,
    is_crew              BOOLEAN,
    inspection_required  BOOLEAN,
    meter_name           VARCHAR(60),
    item_set_id          VARCHAR(30),
    status_changed_at    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS labor (
    id                          VARCHAR(60) PRIMARY KEY,
    person_id                   VARCHAR(60),
    status                      VARCHAR(30),
    status_description          TEXT,
    work_site                   VARCHAR(20),
    is_assigned                 BOOLEAN,
    availability_factor         DOUBLE PRECISION,
    reported_hours              DOUBLE PRECISION,
    year_to_date_other_hours    DOUBLE PRECISION,
    year_to_date_refused_hours  DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS sync_cursor (
    scope       VARCHAR(80) PRIMARY KEY,
    watermark   TIMESTAMPTZ,
    rows_seen   INTEGER DEFAULT 0,
    updated_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS collect_run (
    id                SERIAL PRIMARY KEY,
    object_structure  VARCHAR(80) NOT NULL,
    mode              VARCHAR(20) DEFAULT 'full',
    rows_seen         INTEGER DEFAULT 0,
    upserted          INTEGER DEFAULT 0,
    skipped           INTEGER DEFAULT 0,
    errors            INTEGER DEFAULT 0,
    watermark         TIMESTAMPTZ,
    started_at        TIMESTAMPTZ NOT NULL,
    finished_at       TIMESTAMPTZ
);
