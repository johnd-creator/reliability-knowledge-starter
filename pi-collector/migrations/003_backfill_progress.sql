-- Backfill watermark per (attribute_id, interval).
-- Lets backfill skip ranges already downloaded: effective start is clamped to
-- last_timestamp (minus one interval margin); if the watermark already covers
-- the requested end, the attribute is skipped entirely (0 PI requests).
-- interval is the interpolation interval string ("1m", "1h", ...) or the
-- literal "recorded" for raw backfill-recorded runs.
CREATE TABLE IF NOT EXISTS pi_backfill_progress (
    attribute_id   VARCHAR(200)  NOT NULL,
    interval       VARCHAR(20)   NOT NULL,
    last_timestamp TIMESTAMPTZ   NOT NULL,
    updated_at     TIMESTAMPTZ   DEFAULT NOW(),
    PRIMARY KEY (attribute_id, interval)
);
