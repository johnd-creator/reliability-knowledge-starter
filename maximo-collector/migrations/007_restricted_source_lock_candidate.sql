-- FIX-01 candidate ONLY: deliberate, transactional installation; no startup DDL.
-- Requires unchanged 001→006 in current trusted source/candidate schema.
-- Installer must verify owning DB/schema and set nadi.lock_projector_role.
-- Pre-create reviewed NOLOGIN nadi_capture_lock_owner with no memberships/admin.
BEGIN;
DO $install$
DECLARE ns text:=pg_catalog.current_schema(); app text:=pg_catalog.current_setting('nadi.lock_projector_role',true);
        own oid; appid oid;
BEGIN
 IF ns IS NULL OR ns IN ('pg_catalog','information_schema') OR ns LIKE 'pg_temp%' OR app IS NULL OR app='' THEN
  RAISE EXCEPTION 'explicit trusted schema and projector required';
 END IF;
 IF pg_catalog.to_regclass(pg_catalog.format('%I.mart_replay_queue',ns)) IS NULL THEN
  RAISE EXCEPTION 'reviewed 006 prerequisite required';
 END IF;
 SELECT oid INTO own FROM pg_catalog.pg_roles WHERE rolname='nadi_capture_lock_owner'
  AND NOT (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls OR rolinherit);
 SELECT oid INTO appid FROM pg_catalog.pg_roles WHERE rolname=app
  AND NOT (rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls OR rolinherit);
 IF own IS NULL OR appid IS NULL OR own=appid OR EXISTS (
  SELECT 1 FROM pg_catalog.pg_auth_members WHERE member IN (own,appid) OR roleid IN (own,appid)) THEN
  RAISE EXCEPTION 'restricted owner/projector roles required';
 END IF;
 IF pg_catalog.has_schema_privilege(app,ns,'CREATE') OR pg_catalog.has_schema_privilege(own,ns,'CREATE')
  OR pg_catalog.has_database_privilege(own,pg_catalog.current_database(),'CREATE,TEMPORARY')
  OR pg_catalog.has_database_privilege(app,pg_catalog.current_database(),'CREATE,TEMPORARY') THEN
  RAISE EXCEPTION 'application/helper creation privilege forbidden';
 END IF;
 IF EXISTS (SELECT 1 FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname=ns AND c.relname IN ('equipment','work_order') AND
   (c.relowner IN (own,appid) OR c.relrowsecurity OR c.relforcerowsecurity OR
    pg_catalog.has_any_column_privilege(app,c.oid,'INSERT,UPDATE,REFERENCES') OR
    pg_catalog.has_table_privilege(app,c.oid,'INSERT,DELETE,TRUNCATE,REFERENCES,TRIGGER'))) THEN
  RAISE EXCEPTION 'source ownership/write/RLS boundary incompatible';
 END IF;
 -- Dynamic identifiers exist ONLY in owner-run migration DDL. The installed
 -- privileged function contains fixed qualified SQL, never EXECUTE or DML.
 EXECUTE pg_catalog.format($ddl$
CREATE FUNCTION %1$I.nadi_lock_source_exact(p_domain text,p_source_id text,p_equipment_id text)
RETURNS void LANGUAGE plpgsql VOLATILE SECURITY DEFINER PARALLEL UNSAFE
SET search_path=pg_catalog,pg_temp
AS $body$
DECLARE eq text; site text; org text;
BEGIN
 IF p_domain IS NULL OR p_domain NOT IN ('asset_master','maintenance_event') OR p_source_id IS NULL
  OR pg_catalog.octet_length(p_source_id)>60 OR p_source_id !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]*$' THEN
  RAISE EXCEPTION 'source lock refused';
 END IF;
 IF p_domain='maintenance_event' THEN
  IF pg_catalog.left(p_source_id,3)<>'BSR' OR p_equipment_id IS NULL OR pg_catalog.octet_length(p_equipment_id)>60
   OR p_equipment_id !~ '^[A-Z0-9][A-Z0-9_.:/-]*$' THEN RAISE EXCEPTION 'source lock refused'; END IF;
  SELECT pg_catalog.upper(pg_catalog.btrim(w.equipment_id)) INTO eq
   FROM %1$I.work_order w WHERE w.id=p_source_id FOR SHARE;
  IF NOT FOUND OR eq IS DISTINCT FROM p_equipment_id THEN RAISE EXCEPTION 'source lock refused'; END IF;
 ELSE
  IF p_equipment_id IS NOT NULL THEN RAISE EXCEPTION 'source lock refused'; END IF;
  eq:=p_source_id;
 END IF;
 SELECT e.sources->'maximo'->>'siteid',e.sources->'maximo'->>'orgid' INTO site,org
  FROM %1$I.equipment e WHERE e.id=eq FOR SHARE;
 IF NOT FOUND OR site IS DISTINCT FROM 'BSR' OR org IS DISTINCT FROM 'IP' THEN
  RAISE EXCEPTION 'source lock refused';
 END IF;
END
$body$;
$ddl$,ns);
 EXECUTE pg_catalog.format('GRANT USAGE ON SCHEMA %I TO nadi_capture_lock_owner',ns);
 EXECUTE pg_catalog.format('GRANT SELECT(id,equipment_id),UPDATE(id) ON %I.work_order TO nadi_capture_lock_owner',ns);
 EXECUTE pg_catalog.format('GRANT SELECT(id,sources),UPDATE(id) ON %I.equipment TO nadi_capture_lock_owner',ns);
 EXECUTE pg_catalog.format('ALTER FUNCTION %I.nadi_lock_source_exact(text,text,text) OWNER TO nadi_capture_lock_owner',ns);
 EXECUTE pg_catalog.format('REVOKE ALL ON FUNCTION %I.nadi_lock_source_exact(text,text,text) FROM PUBLIC',ns);
 EXECUTE pg_catalog.format('GRANT EXECUTE ON FUNCTION %I.nadi_lock_source_exact(text,text,text) TO %I',ns,app);
 IF EXISTS (SELECT 1 FROM pg_catalog.pg_proc p JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace,
  LATERAL pg_catalog.aclexplode(p.proacl) a WHERE n.nspname=ns AND p.proname='nadi_lock_source_exact'
  AND (a.grantee NOT IN (own,appid) OR a.grantor<>own OR a.is_grantable OR a.privilege_type<>'EXECUTE')) THEN
  RAISE EXCEPTION 'unexpected helper default ACL';
 END IF;
END
$install$;
COMMIT;
