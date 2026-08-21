-- Reversible companion for 002_reliability_mart.sql.
-- Run only when intentionally removing the v1 Mart tables.

DROP TABLE IF EXISTS overhaul_event;
DROP TABLE IF EXISTS asset_health_assessment;
DROP TABLE IF EXISTS rcfa_analysis;
DROP TABLE IF EXISTS fmea_assessment;
DROP TABLE IF EXISTS maintenance_event;
DROP TABLE IF EXISTS asset_master;
