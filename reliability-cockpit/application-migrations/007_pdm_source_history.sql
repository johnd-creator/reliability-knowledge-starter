-- Additive owning-store source history. No automatic startup migration or grants.
-- Proof/event/alias/receipt rows are append-only; only batch cursor/state updates.

CREATE TABLE nadi_history_batch (
	batch_id VARCHAR(64) NOT NULL,
	owner_id VARCHAR(160) NOT NULL,
	access_asset_id VARCHAR(200) NOT NULL,
	manifest JSON NOT NULL,
	cursor INTEGER NOT NULL,
	state VARCHAR(20) NOT NULL,
	PRIMARY KEY (batch_id)
)

;

CREATE TABLE nadi_history_profile (
	profile_hash VARCHAR(64) NOT NULL,
	document JSON NOT NULL,
	PRIMARY KEY (profile_hash)
)

;

CREATE TABLE nadi_history_source (
	source_sha VARCHAR(64) NOT NULL,
	document JSON NOT NULL,
	PRIMARY KEY (source_sha)
)

;

CREATE TABLE nadi_history_cell (
	source_sha VARCHAR(64) NOT NULL,
	sheet_index INTEGER NOT NULL,
	coordinate VARCHAR(20) NOT NULL,
	terminal_role VARCHAR(40) NOT NULL,
	claims JSON NOT NULL,
	document JSON NOT NULL,
	PRIMARY KEY (source_sha, sheet_index, coordinate),
	FOREIGN KEY(source_sha) REFERENCES nadi_history_source (source_sha)
)

;

CREATE TABLE nadi_history_event (
	event_key VARCHAR(64) NOT NULL,
	owner_id VARCHAR(160) NOT NULL,
	access_asset_id VARCHAR(200) NOT NULL,
	source_sha VARCHAR(64) NOT NULL,
	source_ref VARCHAR(80) NOT NULL,
	sheet_index INTEGER NOT NULL,
	profile_id VARCHAR(160) NOT NULL,
	profile_hash VARCHAR(64) NOT NULL,
	axis VARCHAR(8) NOT NULL,
	position INTEGER NOT NULL,
	classification_hash VARCHAR(64) NOT NULL,
	kind VARCHAR(40) NOT NULL,
	classification VARCHAR(40) NOT NULL,
	document JSON NOT NULL,
	PRIMARY KEY (event_key),
	FOREIGN KEY(source_sha) REFERENCES nadi_history_source (source_sha),
	FOREIGN KEY(profile_hash) REFERENCES nadi_history_profile (profile_hash)
)

;

CREATE TABLE nadi_history_receipt (
	batch_id VARCHAR(64) NOT NULL,
	sequence INTEGER NOT NULL,
	actor VARCHAR(160) NOT NULL,
	occurred_at VARCHAR(40) NOT NULL,
	fingerprint VARCHAR(64) NOT NULL,
	document JSON NOT NULL,
	PRIMARY KEY (batch_id, sequence),
	FOREIGN KEY(batch_id) REFERENCES nadi_history_batch (batch_id)
)

;

CREATE TABLE nadi_history_alias (
	event_key VARCHAR(64) NOT NULL,
	record_id VARCHAR(100) NOT NULL,
	revision INTEGER NOT NULL,
	capture_hash VARCHAR(64) NOT NULL,
	relation VARCHAR(40) NOT NULL,
	PRIMARY KEY (event_key, record_id, revision),
	FOREIGN KEY(event_key) REFERENCES nadi_history_event (event_key)
)

;
CREATE INDEX nadi_history_owner_page ON nadi_history_event (owner_id, access_asset_id, event_key);
