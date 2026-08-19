-- cems-collector local store — contract-shaped; mirrors src/repositories/models.py.
-- The ORM (Base.metadata.create_all via `cemscollector init-db`) is the source
-- of truth; this file is a hand-maintained mirror for DBA reference.
-- Core columns are vendor-neutral snake_case; Modbus configuration is
-- quarantined in the sources JSONB under the "cems" key.

CREATE TABLE IF NOT EXISTS stack (
    stack_id          VARCHAR(10) PRIMARY KEY,
    code              VARCHAR(30) NOT NULL,
    name              TEXT NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'active',
    description       TEXT,
    maintenance_from  TIMESTAMPTZ,
    maintenance_to    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS parameter (
    code                        VARCHAR(30) NOT NULL,
    stack_id                    VARCHAR(10) NOT NULL,
    name                        TEXT NOT NULL,
    unit                        VARCHAR(20) NOT NULL,
    status                      VARCHAR(20) NOT NULL DEFAULT 'documented',
    collect_enabled             BOOLEAN NOT NULL DEFAULT TRUE,
    threshold                   FLOAT,
    normalization_enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    maintenance_override_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    o2_reference                FLOAT,
    adjust_factor               FLOAT NOT NULL DEFAULT 1.0,
    adjust_constant             FLOAT NOT NULL DEFAULT 0.0,
    sources                     JSONB,
    PRIMARY KEY (code, stack_id),
    CONSTRAINT uq_parameter_code_stack UNIQUE (code, stack_id)
);

-- Append-only raw + normalized time-series (port of DAZ qdb.data_realtime).
CREATE TABLE IF NOT EXISTS reading_realtime (
    id                     BIGSERIAL PRIMARY KEY,
    parameter_code         VARCHAR(30) NOT NULL,
    stack_id               VARCHAR(10) NOT NULL,
    value_raw              FLOAT,
    value_normalized       FLOAT,
    value_correction       FLOAT,
    value_final            FLOAT,
    transformation_status  VARCHAR(20) NOT NULL DEFAULT 'ok',
    observed_at            TIMESTAMPTZ NOT NULL,
    created_at             TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_reading_realtime_composite
    ON reading_realtime (parameter_code, stack_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS ix_reading_realtime_observed
    ON reading_realtime (observed_at DESC);

-- 5-minute aggregates (port of DAZ sensor_data / qdb.data_5min).
CREATE TABLE IF NOT EXISTS reading_5min (
    id              BIGSERIAL PRIMARY KEY,
    parameter_code  VARCHAR(30) NOT NULL,
    stack_id        VARCHAR(10) NOT NULL,
    avg_value       FLOAT NOT NULL DEFAULT 0,
    min_value       FLOAT NOT NULL DEFAULT 0,
    max_value       FLOAT NOT NULL DEFAULT 0,
    sample_count    INTEGER NOT NULL DEFAULT 0,
    window_start    TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_reading_5min_window UNIQUE (parameter_code, stack_id, window_start)
);

CREATE INDEX IF NOT EXISTS ix_reading_5min_window
    ON reading_5min (window_start DESC);

CREATE TABLE IF NOT EXISTS sync_cursor (
    scope      VARCHAR(80) PRIMARY KEY,
    watermark  TIMESTAMPTZ,
    rows_seen  INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS collect_run (
    id          SERIAL PRIMARY KEY,
    run_type    VARCHAR(20) NOT NULL,
    mode        VARCHAR(20) NOT NULL DEFAULT 'full',
    rows_seen   INTEGER NOT NULL DEFAULT 0,
    upserted    INTEGER NOT NULL DEFAULT 0,
    skipped     INTEGER NOT NULL DEFAULT 0,
    errors      INTEGER NOT NULL DEFAULT 0,
    watermark   TIMESTAMPTZ,
    started_at  TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ
);
