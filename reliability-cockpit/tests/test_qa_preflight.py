import json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from src.qa.preflight import assess_configuration, read_private_config, ROOT


class QaPreflightTest(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads((ROOT/"deploy/qa/qa-config.example.json").read_text())
        self.sha = "a"*40

    def complete(self):
        r = dict(self.raw)
        r.update(release_sha=self.sha, origin="https://qa.corp.example",
            application_database="nadi_qa_application", migration_owner="nadi_qa_owner",
            writer_capability="nadi_qa_writer", runtime_role="nadi_qa_runtime",
            storage_root="/private/qa", identity_provider="oidc", issuer="https://id.corp.example/tenant",
            client_id="client-id", redirect_uri="https://qa.corp.example/auth/callback",
            logout_uri="https://qa.corp.example/auth/logout", algorithms=["RS256"],
            session_idle_seconds=300,session_absolute_seconds=3600,provider_timeout_seconds=5,
            pool_size=4,pool_timeout_seconds=5,lease_capacity=8,attachment_max_bytes=100,
            attachment_asset_quota_bytes=1000,orphan_grace_seconds=60,retention_days=30,
            operator_approval_ref="fixture-approval",database_secret_ref="secret://qa/db",
            identity_secret_ref="secret://qa/idp",scanner_approval_ref="fixture-scanner",
            directory_approval_ref="fixture-directory",infrastructure_approval_ref="fixture-infra",
            backup_recovery_approval_ref="fixture-recovery")
        return r

    def test_template_is_no_go_no_sources_writes(self):
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            result=assess_configuration(self.raw,actual_sha=self.sha,clean=True)
        self.assertEqual(result["preparation"],"BLOCKED")
        self.assertEqual(result["real_qa_readiness"],"NO_GO")
        self.assertEqual((result["source_gets"],result["writes"]),(0,0))

    def test_complete_contract_is_not_actual_activation_authority(self):
        result=assess_configuration(self.complete(),actual_sha=self.sha,clean=True)
        self.assertEqual(result["preparation"],"PASS")
        self.assertEqual(result["real_qa_readiness"],"NO_GO")
        self.assertEqual(result["attestations"],"DECLARED_NOT_VERIFIED")

    def test_forged_release_dirty_tree_activation_collection_denied(self):
        for change,clean in [({"release_sha":"b"*40},True),({},False),
                             ({"engineering_enabled":True},True),({"source_collection_enabled":True},True)]:
            r=self.complete();r.update(change)
            self.assertEqual(assess_configuration(r,actual_sha=self.sha,clean=clean)["preparation"],"BLOCKED")

    def test_no_unknown_source_credentials_or_coercion(self):
        for key,value in [("PI_PASSWORD","do-not-expose-fixture"),("MAXIMO_TOKEN","fixture"),
                          ("pool_size","4"),("engineering_enabled",0)]:
            r=self.complete();r[key]=value
            output=assess_configuration(r,actual_sha=self.sha,clean=True)
            self.assertEqual(output["preparation"],"BLOCKED")
            if key in {"PI_PASSWORD","MAXIMO_TOKEN"}:
                self.assertNotIn(str(value),json.dumps(output))

    def test_missing_scanner_approval_and_unsafe_origin_fail(self):
        for change in [{"scanner_approval_ref":None},{"origin":"http://qa.corp.example"},
                       {"redirect_uri":"https://attacker.example/callback"},
                       {"runtime_role":"nadi_qa_owner"},{"pool_size":100}]:
            r=self.complete();r.update(change)
            self.assertEqual(assess_configuration(r,actual_sha=self.sha,clean=True)["preparation"],"BLOCKED")

    def test_private_file_limits_permissions_and_symlink(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"config.json";p.write_text(json.dumps(self.raw));p.chmod(0o600)
            self.assertEqual(read_private_config(p),self.raw)
            p.chmod(0o644)
            with self.assertRaises(ValueError):read_private_config(p)
            p.chmod(0o600);p.write_bytes(b"x"*32769)
            with self.assertRaises(ValueError):read_private_config(p)
            link=Path(root)/"link";link.symlink_to(p)
            with self.assertRaises(OSError):read_private_config(link)

    def test_local_auth_selected_without_enterprise_registration(self):
        r=self.complete();r.update(identity_provider="local",issuer="",client_id="",redirect_uri="",logout_uri="",
            algorithms=[],provider_timeout_seconds=None,identity_secret_ref=None,
            local_auth_approval_ref="fixture-account-policy")
        result=assess_configuration(r,actual_sha=self.sha,clean=True)
        self.assertEqual(result["preparation"],"PASS")
        self.assertEqual(result["real_qa_readiness"],"NO_GO")
        self.assertNotIn("ENTERPRISE",str(result))
        for field,value in (("local_password_minimum",11),("local_login_attempts",0),("local_auth_approval_ref",None)):
            changed={**r,field:value}
            self.assertEqual(assess_configuration(changed,actual_sha=self.sha,clean=True)["preparation"],"BLOCKED")

    def test_compose_command_extends_image_entrypoint_and_cli_remains_source_free(self):
        import ast, re, subprocess, sys
        docker=(ROOT/"deploy/qa/Dockerfile.preflight").read_text()
        compose=(ROOT/"deploy/qa/compose.preflight.yaml").read_text()
        entrypoint=json.loads(re.search(r"^ENTRYPOINT (.+)$",docker,re.M).group(1))
        command=ast.literal_eval(re.search(r"^    command: (.+)$",compose,re.M).group(1))
        self.assertEqual(entrypoint,["python","-m","src.qa.preflight"])
        with tempfile.TemporaryDirectory() as private:
            config=Path(private)/"config.json";config.write_text(json.dumps(self.raw));config.chmod(0o600)
            manifest=Path(private)/"release.json";manifest.write_text("{}");manifest.chmod(0o600)
            args=[str(config) if v=="/run/qa/config.json" else str(manifest) if v=="/app/.qa-release.json" else v for v in command]
            result=subprocess.run([sys.executable,*entrypoint[1:],*args],cwd=ROOT/"reliability-cockpit",
                env={"PATH":os.environ.get("PATH","/usr/bin:/bin"),"PYTHONPATH":"."},capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2)
        output=json.loads(result.stdout)  # argparse duplication produces no JSON, so fails here.
        self.assertEqual(output["real_qa_readiness"],"NO_GO")
        self.assertEqual((output["source_gets"],output["writes"]),(0,0))
