-- PI Collector local store (TimescaleDB hypertable for time-series).
-- Matches src/repositories/models.py and vendor-neutral parameter contracts.

-- Registry of attributes to collect (loaded from pi-knowledge mappings).
CREATE TABLE IF NOT EXISTS pi_attribute_registry (
    attribute_id      VARCHAR(200) PRIMARY KEY,
    site              VARCHAR(20),
    unit              VARCHAR(20),
    equipment         VARCHAR(120),
    parameter         VARCHAR(60),
    business_name     TEXT,
    position          VARCHAR(120),
    unit_of_measure   VARCHAR(40),
    web_id            TEXT,
    af_path           TEXT,
    is_active         BOOLEAN DEFAULT TRUE,
    registered_at     TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_registry_equipment ON pi_attribute_registry (equipment);
CREATE INDEX IF NOT EXISTS ix_registry_parameter ON pi_attribute_registry (parameter);

-- Latest snapshot (one row per active attribute, upserted on each snapshot run).
CREATE TABLE IF NOT EXISTS pi_snapshot (
    attribute_id      VARCHAR(200) PRIMARY KEY,
    value             DOUBLE PRECISION,
    value_good        BOOLEAN,
    units             VARCHAR(40),
    source_timestamp  TIMESTAMPTZ,
    collected_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Time-series history (hypertable if TimescaleDB is available).
CREATE TABLE IF NOT EXISTS pi_timeseries (
    attribute_id      VARCHAR(200)  NOT NULL,
    timestamp         TIMESTAMPTZ   NOT NULL,
    value             DOUBLE PRECISION,
    value_good        BOOLEAN,
    collected_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (attribute_id, timestamp)
);

-- Create hypertable if TimescaleDB extension is present; skip silently otherwise.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable('pi_timeseries', 'timestamp', if_not_exists => TRUE);
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'TimescaleDB hypertable creation skipped: %', SQLERRM;
END $$;

CREATE INDEX IF NOT EXISTS ix_ts_attr_time ON pi_timeseries (attribute_id, timestamp DESC);

-- Collection cursor for incremental backfill tracking.
CREATE TABLE IF NOT EXISTS pi_collect_cursor (
    scope              VARCHAR(80) PRIMARY KEY,
    last_collected_at  TIMESTAMPTZ,
    rows_seen          INTEGER DEFAULT 0,
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);
