-- Candidate only: existing Cockpit APPLICATION store; never Mart or startup.
CREATE TABLE nadi_application_session (
 token_hash varchar(64) PRIMARY KEY, csrf_hash varchar(64) NOT NULL,
 subject varchar(160) NOT NULL, grant_version integer NOT NULL CHECK (grant_version>=1),
 created_at varchar(40) NOT NULL, last_seen_at varchar(40) NOT NULL,
 expires_at varchar(40) NOT NULL, revoked_at varchar(40)
);
CREATE TABLE nadi_security_activity (
 activity_id varchar(100) PRIMARY KEY, subject varchar(160),
 action varchar(40) NOT NULL, outcome varchar(40) NOT NULL,
 occurred_at varchar(40) NOT NULL, asset_ids json NOT NULL
);
-- Runtime session authority needs SELECT/INSERT/UPDATE session;
-- security audit SELECT/INSERT only. No owner/DDL/delete/truncate.
