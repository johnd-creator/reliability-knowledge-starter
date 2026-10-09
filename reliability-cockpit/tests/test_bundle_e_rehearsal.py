"""Real HTTPS, application restart and DB/blob restore on disposable fixtures only."""
import hashlib, json, os, socket, subprocess, tempfile, threading, time, unittest
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
import uvicorn
import test_bundle_d_http as fixture
from src.api.engineering_qa import create_qa_app
from src.services.attachments import AttachmentService, DisposableFileStorage, AttachmentBase
from src.repositories.application_boundary import ApplicationStore
from src.repositories.application_migrations import MIGRATIONS, LEDGER


class BundleERehearsalTest(fixture.RealHttpQaTest):
    def restart_application(self):
        self.client.close();self.server.should_exit=True;self.thread.join(10);self.sock.close()
        self.assertFalse(self.thread.is_alive())
        self.engine.dispose()
        self.sock=socket.socket();self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.bind(("127.0.0.1",0));self.port=self.sock.getsockname()[1]
        self.client=fixture.SocketClient("https://127.0.0.1:"+str(self.port))
        app=create_qa_app(authority=self.authority,cases=self.cases,inspections=self.inspections,
            recommendations=self.recommendations,context=self.context,environment="development")
        root=Path(self.tls.name)
        self.server=uvicorn.Server(uvicorn.Config(app,host="127.0.0.1",port=self.port,
            ssl_keyfile=str(root/"key.pem"),ssl_certfile=str(root/"cert.pem"),log_level="critical",
            proxy_headers=False))
        self.thread=threading.Thread(target=lambda:self.server.run(sockets=[self.sock]),daemon=True)
        self.thread.start()
        for _ in range(200):
            if self.server.started:return
            time.sleep(.01)
        raise RuntimeError("isolated restart failed")

    def fingerprint(self, engine):
        tables=set().union(*MIGRATIONS.values())|{LEDGER}
        result={}
        with engine.connect() as c:
            for table in sorted(tables):
                rows=[dict(r) for r in c.execute(text("SELECT * FROM "+table)).mappings()]
                values=sorted(json.dumps(r,sort_keys=True,default=str,separators=(",",":")) for r in rows)
                result[table]={"rows":len(rows),"sha256":hashlib.sha256("\n".join(values).encode()).hexdigest()}
        return result

    def test_real_http_restart_revocation_and_private_db_blob_restore(self):
        self.test_complete_trusted_http_workflow_preserves_lineage()
        self.restart_application()
        self.assertEqual(self.call("GET","asset-context/"+self.asset)["recommendations"]["total"],1)
        self.assertEqual(self.client.request("GET","/health/ready").status_code,200)
        with tempfile.TemporaryDirectory() as private:
            root=Path(private)
            blobs=DisposableFileStorage(root/"blobs")
            actor=self.directory("author")
            storage_service=AttachmentService(self.store,blobs,lambda a:a==self.asset,
                                              max_bytes=100,asset_quota_bytes=100,scanner=lambda d,t:True)
            attachment=storage_service.upload(actor,self.asset,"fixture.pdf","application/pdf",b"%PDF-fixture")
            storage_service.retrieve(actor,attachment.attachment_id)
            before=self.fingerprint(self.engine)
            url=self.engine.url
            if url.host not in {"127.0.0.1","localhost"} or not url.database.endswith("_test"):
                self.fail("disposable database required")
            clone="nadi_e_restore_"+uuid4().hex[:10]+"_test"
            pg_env={"PATH":os.environ.get("PATH","/usr/bin:/bin"),"LANG":"C.UTF-8"}
            if url.password:pg_env["PGPASSWORD"]=url.password
            dump=root/"application.dump"
            args=["-h",url.host,"-p",str(url.port or 5432),"-U",url.username]
            subprocess.run(["pg_dump",*args,"-d",url.database,"-Fc","-f",str(dump)],
                           check=True,env=pg_env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            dump.chmod(0o600)
            catalog=subprocess.check_output(["pg_restore","--list",str(dump)],env=pg_env,text=True)
            self.assertIn("nadi_application_migration",catalog)
            self.assertGreater(dump.stat().st_size,0)
            digest=hashlib.sha256(dump.read_bytes()).hexdigest()
            self.assertEqual(len(digest),64)
            admin=create_engine(url.set(database="postgres"),isolation_level="AUTOCOMMIT")
            cloned=None
            try:
                with admin.connect() as c:c.exec_driver_sql('CREATE DATABASE "'+clone+'"')
                subprocess.run(["pg_restore",*args,"-d",clone,"--no-owner","--no-privileges",str(dump)],
                               check=True,env=pg_env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                cloned=create_engine(url.set(database=clone))
                self.assertEqual(before,self.fingerprint(cloned))
                restored=DisposableFileStorage(root/"restored")
                import shutil
                shutil.copyfile(blobs.path(attachment.attachment_id),restored.path(attachment.attachment_id))
                restored.path(attachment.attachment_id).chmod(0o600)
                restored_service=AttachmentService(ApplicationStore(cloned,expected_database=clone,isolated=True),
                    restored,lambda a:a==self.asset,max_bytes=100,scanner=lambda d,t:True)
                self.assertEqual(restored_service.retrieve(actor,attachment.attachment_id)[1],b"%PDF-fixture")
                self.assertEqual(before,self.fingerprint(self.engine))
                self.assertEqual(self.inspections.list(actor,asset_id=self.asset)["total"],1)
            finally:
                if cloned:cloned.dispose()
                with admin.connect() as c:c.exec_driver_sql('DROP DATABASE IF EXISTS "'+clone+'" WITH (FORCE)')
                admin.dispose()
        self.authority.revoke(actor,self.credentials["author"][0])
        self.call("GET","asset-context/"+self.asset,expected=401)

    def test_concurrent_quota_only_one_blob_and_audit(self):
        with tempfile.TemporaryDirectory() as private:
            storage=DisposableFileStorage(private)
            service=AttachmentService(self.store,storage,lambda a:a==self.asset,
                max_bytes=100,asset_quota_bytes=100,scanner=lambda d,t:True)
            actor=self.directory("author")
            def upload(i):
                try:return service.upload(actor,self.asset,"file.pdf","application/pdf",b"%PDF-"+b"x"*55)
                except Exception as error:return error
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(upload,range(2)))
            self.assertEqual(sum(hasattr(r,"attachment_id") for r in results),1)
            self.assertEqual(len(list(Path(private).iterdir())),1)
            with self.engine.connect() as c:
                self.assertEqual(c.scalar(text("SELECT count(*) FROM nadi_attachment")),1)
                self.assertEqual(c.scalar(text("SELECT count(*) FROM nadi_attachment_event")),1)

    def test_readonly_preflight_wrong_database_and_provider_failure(self):
        from src.qa.preflight import audit_disposable_database
        from types import SimpleNamespace
        from unittest.mock import patch
        with self.assertRaises(Exception):
            audit_disposable_database(self.engine,SimpleNamespace(application_database="wrong_test"))
        with patch.object(self.authority.provider,"current_grant",side_effect=RuntimeError("private token and URL")):
            result=self.call("GET","asset-context/"+self.asset,expected=503)
        self.assertEqual(result,{"detail":{"code":"IDENTITY_PROVIDER_UNAVAILABLE"}})
        self.assertNotIn("private",json.dumps(result))
        self.assertEqual(self.call("GET","asset-context/"+self.asset)["assessment"],"NOT_ASSESSED")
