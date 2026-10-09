-- Application-owned local authentication. Explicit migration only; never startup/Mart.
CREATE TABLE nadi_local_account (
 user_id varchar(160) PRIMARY KEY,
 username varchar(64) NOT NULL UNIQUE CHECK (username ~ '^[a-z0-9][a-z0-9_.-]{2,63}$'),
 password_hash text NOT NULL CHECK (left(password_hash, 10) = '$argon2id$'),
 active boolean NOT NULL,
 password_change_required boolean NOT NULL,
 grant_version integer NOT NULL CHECK (grant_version >= 1),
 roles json NOT NULL, asset_ids json NOT NULL,
 failed_attempts integer NOT NULL CHECK (failed_attempts >= 0),
 locked_until timestamptz,
 created_at timestamptz NOT NULL, updated_at timestamptz NOT NULL
);
CREATE TABLE nadi_local_login_budget (
 budget_id varchar(40) PRIMARY KEY CHECK (budget_id = 'global'),
 window_start timestamptz NOT NULL,
 attempts integer NOT NULL CHECK (attempts >= 0)
);
CREATE TABLE nadi_local_security_event (
 event_id varchar(100) PRIMARY KEY,
 actor_id varchar(160), target_id varchar(160),
 action varchar(40) NOT NULL, outcome varchar(40) NOT NULL,
 occurred_at timestamptz NOT NULL
);
-- Runtime SELECT/INSERT/UPDATE account/budget; immutable event SELECT/INSERT only.
