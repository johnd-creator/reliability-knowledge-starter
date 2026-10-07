-- Preserve PI source quality/type evidence in the local collector store.
-- Apply after 001_init.sql, 002_collect_runs.sql and 003_backfill_progress.sql.
-- This migration is for pi-collector only and is
-- deliberately separate from the Reliability Mart mapping migrations.

BEGIN;

ALTER TABLE pi_snapshot
    ADD COLUMN IF NOT EXISTS source_value JSON,
    ADD COLUMN IF NOT EXISTS value_type VARCHAR(40),
    ADD COLUMN IF NOT EXISTS value_questionable BOOLEAN,
    ADD COLUMN IF NOT EXISTS value_substituted BOOLEAN,
    ADD COLUMN IF NOT EXISTS value_annotated BOOLEAN;

ALTER TABLE pi_timeseries
    ADD COLUMN IF NOT EXISTS units VARCHAR(40),
    ADD COLUMN IF NOT EXISTS source_value JSON,
    ADD COLUMN IF NOT EXISTS value_type VARCHAR(40),
    ADD COLUMN IF NOT EXISTS value_questionable BOOLEAN,
    ADD COLUMN IF NOT EXISTS value_substituted BOOLEAN,
    ADD COLUMN IF NOT EXISTS value_annotated BOOLEAN;

COMMIT;
