-- Run log: one row per collector run (snapshot cycle, backfill, daemon cycle).
-- Powers the daily activity graph: a day is 'full green' only when runs
-- cover all 24 local hours of that day.
CREATE TABLE IF NOT EXISTS pi_collect_run (
    id                SERIAL PRIMARY KEY,
    scope             VARCHAR(80)  NOT NULL,
    started_at        TIMESTAMPTZ  NOT NULL,
    finished_at       TIMESTAMPTZ,
    attributes_seen   INTEGER      DEFAULT 0,
    rows_collected    INTEGER      DEFAULT 0,
    errors            INTEGER      DEFAULT 0,
    requests_made     INTEGER      DEFAULT 0,
    aborted           BOOLEAN      DEFAULT FALSE,
    abort_reason      TEXT
);
CREATE INDEX IF NOT EXISTS ix_collect_run_finished ON pi_collect_run (finished_at);
