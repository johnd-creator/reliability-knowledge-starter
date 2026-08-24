-- NADI-MAP-002: verification and retirement provenance for governed mappings.
--
-- Apply after 002_asset_af_mapping.sql to the Reliability Mart configured by
-- RELIABILITY_MART_DATABASE_URL. This migration is schema-only and contains no
-- production mapping rows.

ALTER TABLE asset_af_mapping
    ADD COLUMN IF NOT EXISTS verified_by VARCHAR(160),
    ADD COLUMN IF NOT EXISTS verification_note TEXT,
    ADD COLUMN IF NOT EXISTS evidence_ref VARCHAR(500),
    ADD COLUMN IF NOT EXISTS retired_by VARCHAR(160),
    ADD COLUMN IF NOT EXISTS retirement_note TEXT;

ALTER TABLE asset_af_mapping
    ADD CONSTRAINT ck_asset_af_mapping_verified_provenance
    CHECK (
        mapping_status <> 'VERIFIED'
        OR (
            verified_at IS NOT NULL
            AND NULLIF(BTRIM(verified_by), '') IS NOT NULL
            AND (
                NULLIF(BTRIM(verification_note), '') IS NOT NULL
                OR NULLIF(BTRIM(evidence_ref), '') IS NOT NULL
            )
        )
    ),
    ADD CONSTRAINT ck_asset_af_mapping_proposed_provenance
    CHECK (
        mapping_status <> 'PROPOSED'
        OR (verified_at IS NULL AND verified_by IS NULL)
    ),
    ADD CONSTRAINT ck_asset_af_mapping_retired_provenance
    CHECK (
        mapping_status <> 'RETIRED'
        OR (
            retired_at IS NOT NULL
            AND NULLIF(BTRIM(retired_by), '') IS NOT NULL
            AND NULLIF(BTRIM(retirement_note), '') IS NOT NULL
        )
    );
