-- Preserve PI source quality/type evidence in the local collector store.
-- Apply after 001_init.sql. This migration is for pi-collector only and is
-- deliberately separate from the Reliability Mart mapping migrations.

ALTER TABLE IF EXISTS pi_snapshot
    ADD COLUMN IF NOT EXISTS value_type VARCHAR(40),
    ADD COLUMN IF NOT EXISTS value_questionable BOOLEAN,
    ADD COLUMN IF NOT EXISTS value_substituted BOOLEAN,
    ADD COLUMN IF NOT EXISTS value_annotated BOOLEAN;

ALTER TABLE IF EXISTS pi_timeseries
    ADD COLUMN IF NOT EXISTS units VARCHAR(40),
    ADD COLUMN IF NOT EXISTS value_type VARCHAR(40),
    ADD COLUMN IF NOT EXISTS value_questionable BOOLEAN,
    ADD COLUMN IF NOT EXISTS value_substituted BOOLEAN,
    ADD COLUMN IF NOT EXISTS value_annotated BOOLEAN;
