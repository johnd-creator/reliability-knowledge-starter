-- Candidate application-only, explicit migration owner; no operational execution.
CREATE TABLE nadi_attachment(attachment_id varchar(100) PRIMARY KEY,document json NOT NULL);
CREATE TABLE nadi_attachment_event(event_id varchar(100) PRIMARY KEY,attachment_id varchar(100) NOT NULL REFERENCES nadi_attachment(attachment_id),actor varchar(160) NOT NULL,action varchar(40) NOT NULL,occurred_at varchar(40) NOT NULL);
