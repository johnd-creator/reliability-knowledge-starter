"""Hermetic identity, ancestry, listener and auxiliary negative regressions."""
import copy
import importlib.util
import os
import subprocess
import time
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("process_guard",ROOT/"deploy/development/vendor-maps/process_guard.py")
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

NODE="/verified/node22";GROUP="/isolated"
def row(pid,parent,title,sockets=()):
    return dict(pid=pid,parent=parent,start_ticks=str(100+pid),executable=NODE,
                exe_device=1,exe_inode=2,command_sha256=str(pid),comm=title,
                cgroup="0::/isolated\n",argv=(title,),sockets=list(sockets))
def view():
    return dict(records={1:row(1,99,"node"),2:row(2,1,"next-server (v15.5.9)",["20"])},
                listeners={"20":dict(port=4444,address="0100007F")})
class ProcessGuardTest(unittest.TestCase):
    def setUp(self):
        self.v=view();self.guard=g.Guard(self.v,1,4444,"invocation",NODE,GROUP)
    def check(self,v=None,main=1,invocation="invocation",auxiliaries=()):
        return self.guard.validate(v or self.v,main,invocation,auxiliaries)
    def test_listener_identity(self):
        self.assertEqual(self.check()["worker"],2)
    def test_pid_reuse(self):
        v=copy.deepcopy(self.v);v["records"][2]["start_ticks"]="999"
        with self.assertRaisesRegex(g.AttributionError,"IDENTITY_CHANGED"):self.check(v)
    def test_parent_change(self):
        v=copy.deepcopy(self.v);v["records"][2]["parent"]=99
        with self.assertRaises(g.AttributionError):self.check(v)
    def test_executable_command_comm_and_cgroup_change(self):
        for key in ["executable","exe_inode","command_sha256","comm","cgroup"]:
            v=copy.deepcopy(self.v);v["records"][2][key]="changed"
            with self.subTest(key=key),self.assertRaises(g.AttributionError):self.check(v)
    def test_parent_identity_change(self):
        v=copy.deepcopy(self.v);v["records"][1]["start_ticks"]="999"
        with self.assertRaises(g.AttributionError):self.check(v)
    def test_invocation_and_mainpid(self):
        for kwargs in [dict(main=3),dict(invocation="replacement")]:
            with self.assertRaises(g.AttributionError):self.check(**kwargs)
    def test_worker_replacement(self):
        v=copy.deepcopy(self.v);v["records"][3]=v["records"].pop(2);v["records"][3]["pid"]=3
        with self.assertRaises(g.AttributionError):self.check(v)
    def test_shared_inherited_listener_refused(self):
        v=copy.deepcopy(self.v);v["records"][3]=row(3,2,"next-server (v15.5.9)",["20"])
        with self.assertRaisesRegex(g.AttributionError,"SHARED_LISTENER"):self.check(v)
    def test_duplicate_next_title_without_listener_unknown(self):
        v=copy.deepcopy(self.v);v["records"][3]=row(3,2,"next-server (v15.5.9)")
        with self.assertRaisesRegex(g.AttributionError,"UNVERIFIED_ADDITIONAL_NEXT_PROCESS"):self.check(v)
    def test_exact_reviewed_auxiliary_not_substring_worker(self):
        v=copy.deepcopy(self.v);v["records"][3]=row(3,2,NODE)
        v["records"][3]["argv"]=(NODE,"/private/reviewed-helper.cjs","next-server argument")
        result=self.check(v,auxiliaries=(v["records"][3]["argv"],))
        self.assertEqual(result["auxiliaries"][0]["role"],"EXACT_REVIEWED_AUXILIARY")
        with self.assertRaises(g.AttributionError):self.check(v)
    def test_auxiliary_bad_parent_executable_or_extra_argument(self):
        v=copy.deepcopy(self.v);v["records"][3]=row(3,2,NODE)
        args=(NODE,"/private/helper.cjs");v["records"][3]["argv"]=args
        for key,value in [("parent",1),("executable","/unknown/node"),("argv",args+("extra",))]:
            changed=copy.deepcopy(v);changed["records"][3][key]=value
            with self.subTest(key=key),self.assertRaises(g.AttributionError):self.check(changed,auxiliaries=(args,))
    def test_auxiliary_unauthorized_listener(self):
        v=copy.deepcopy(self.v);v["records"][3]=row(3,2,NODE,["30"]);v["listeners"]["30"]=dict(port=5555,address="0100007F")
        with self.assertRaisesRegex(g.AttributionError,"UNAUTHORIZED_LISTENER"):self.check(v,auxiliaries=((NODE,),))
    def test_missing_and_foreign_listener(self):
        for v in [dict(records=self.v["records"],listeners={}),dict(records=self.v["records"],listeners={"99":dict(port=4444,address="0100007F")})]:
            with self.assertRaises(g.AttributionError):self.check(v)
    def test_ambiguous_port_and_socket_rebind(self):
        v=copy.deepcopy(self.v);v["listeners"]["30"]=dict(port=4444,address="00000000")
        with self.assertRaises(g.AttributionError):self.check(v)
        v=copy.deepcopy(self.v);v["listeners"]["30"]=v["listeners"].pop("20");v["records"][2]["sockets"]=["30"]
        with self.assertRaisesRegex(g.AttributionError,"LISTENER_WORKER_CHANGED"):self.check(v)
    def test_actual_process_sanitized(self):
        child=subprocess.Popen(["/bin/sleep","5"])
        try:
            time.sleep(.05)
            r=g.process(child.pid);self.assertEqual(r["parent"],os.getpid())
            self.assertNotIn("argv",g.sanitized(dict(records={r["pid"]:r}))[r["pid"]])
        finally:
            child.terminate();child.wait()
    def test_unreadable_process_and_listener(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(g.AttributionError,"UNREADABLE_PROCESS"):g.process(999,Path(tmp))
            with self.assertRaisesRegex(g.AttributionError,"UNREADABLE_LISTENER"):g.tcp_listeners(Path(tmp))
    def test_unreadable_or_empty_cgroup(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            with self.assertRaises(g.AttributionError):g.snapshot(p)
            (p/"cgroup.procs").write_text("")
            with self.assertRaises(g.AttributionError):g.snapshot(p)
    def test_member_changed_during_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"cgroup.procs").write_text("1\n2")
            def capture(pid,proc):
                (p/"cgroup.procs").write_text("1\n2\n3");return self.v["records"][pid]
            with patch.object(g,"process",side_effect=capture),patch.object(g,"tcp_listeners",return_value=self.v["listeners"]),self.assertRaisesRegex(g.AttributionError,"CGROUP_CHANGED"):g.snapshot(p)
    def test_changed_identity_second_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"cgroup.procs").write_text("1\n2")
            records=[self.v["records"][1],self.v["records"][2],row(1,99,"changed"),self.v["records"][2]]
            with patch.object(g,"process",side_effect=records),patch.object(g,"tcp_listeners",return_value=self.v["listeners"]),self.assertRaisesRegex(g.AttributionError,"PROCESS_CHANGED"):g.snapshot(p)

    def test_auxiliary_pid_reuse_refused(self):
        v=copy.deepcopy(self.v);v["records"][3]=row(3,2,NODE)
        self.check(v,auxiliaries=((NODE,),))
        v["records"][3]["start_ticks"]="reused"
        with self.assertRaisesRegex(g.AttributionError,"AUXILIARY_PID_REUSE"):self.check(v,auxiliaries=((NODE,),))
    def test_no_auxiliary_title_whitelist(self):
        v=copy.deepcopy(self.v);v["records"][3]=row(3,2,"next-server (v15.5.9)")
        with self.assertRaises(g.AttributionError):self.check(v,auxiliaries=(("next-server (v15.5.9)",),))

    def test_reviewed_source_hash_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            deps=Path(tmp)
            for relative in g.NEXT_AUXILIARY_HASHES:
                p=deps/"next/dist"/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text("modified")
            with self.assertRaisesRegex(g.AttributionError,"SOURCE_HASH_MISMATCH"):g.reviewed_next_auxiliary(deps,NODE)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(g.AttributionError,"UNREADABLE_AUXILIARY_SOURCE"):g.reviewed_next_auxiliary(Path(tmp),NODE)

    def test_non_loopback_refused(self):
        v=copy.deepcopy(self.v);v["listeners"]["20"]["address"]="00000000"
        with self.assertRaisesRegex(g.AttributionError,"NON_LOOPBACK"):g.Guard(v,1,4444,"invocation",NODE,GROUP)
    def test_listener_ownership_changed_second_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"cgroup.procs").write_text("1\n2")
            changed=copy.deepcopy(self.v["records"][2]);changed["sockets"]=[]
            rows=[self.v["records"][1],self.v["records"][2],self.v["records"][1],changed]
            with patch.object(g,"process",side_effect=rows),patch.object(g,"tcp_listeners",return_value=self.v["listeners"]),self.assertRaisesRegex(g.AttributionError,"LISTENER_OWNERSHIP_CHANGED"):g.snapshot(p)
