-- Candidate APPLICATION-only envelope; no operational runner/startup binding.
CREATE TABLE nadi_human_record (
 kind varchar(40) NOT NULL CHECK(kind IN ('INSPECTION','RECOMMENDATION')),
 record_id varchar(100) NOT NULL, revision integer NOT NULL CHECK(revision>=1),
 document json NOT NULL, PRIMARY KEY(kind,record_id)
);
CREATE TABLE nadi_human_record_revision (
 kind varchar(40) NOT NULL, record_id varchar(100) NOT NULL,
 revision integer NOT NULL CHECK(revision>=1),actor varchar(160) NOT NULL,
 action varchar(40) NOT NULL,occurred_at varchar(40) NOT NULL,
 reason varchar(6000),snapshot json NOT NULL,
 PRIMARY KEY(kind,record_id,revision),
 FOREIGN KEY(kind,record_id) REFERENCES nadi_human_record(kind,record_id)
);
CREATE TABLE nadi_human_record_receipt (
 actor varchar(160) NOT NULL,request_id varchar(100) NOT NULL,
 fingerprint varchar(64) NOT NULL,kind varchar(40) NOT NULL,
 record_id varchar(100) NOT NULL,revision integer NOT NULL CHECK(revision>=1),
 result json NOT NULL,PRIMARY KEY(actor,request_id),
 FOREIGN KEY(kind,record_id) REFERENCES nadi_human_record(kind,record_id)
);
-- Restricted writer: SELECT/INSERT/UPDATE record, SELECT/INSERT revisions/receipts.
-- No UPDATE/DELETE/TRUNCATE audit, ownership or schema privileges.
