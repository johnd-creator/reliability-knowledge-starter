-- Candidate additive migration for the EXISTING application-owned Cockpit store.
-- NOT canonical Mart DDL. Not called by any operational initializer/runner.
-- Test only until writer identity, ownership and migration preflight are reviewed.
CREATE TABLE engineering_case (
    case_id varchar(100) PRIMARY KEY,
    revision integer NOT NULL CHECK (revision >= 1),
    document json NOT NULL
);
CREATE TABLE engineering_case_event (
    case_id varchar(100) NOT NULL REFERENCES engineering_case(case_id) ON DELETE RESTRICT,
    revision integer NOT NULL CHECK (revision >= 1),
    event json NOT NULL,
    snapshot json NOT NULL,
    PRIMARY KEY (case_id, revision)
);
CREATE TABLE engineering_case_receipt (
    actor varchar(160) NOT NULL,
    request_id varchar(100) NOT NULL,
    fingerprint varchar(64) NOT NULL,
    case_id varchar(100) NOT NULL REFERENCES engineering_case(case_id) ON DELETE RESTRICT,
    revision integer NOT NULL CHECK (revision >= 1),
    result json NOT NULL,
    PRIMARY KEY (actor, request_id)
);
-- API users must never own these relations. Future deployment must grant only
-- SELECT/INSERT/UPDATE case, SELECT/INSERT event and receipt; no audit UPDATE/DELETE.
