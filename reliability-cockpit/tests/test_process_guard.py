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


class StableCollectionTest(unittest.TestCase):
    setUp = ProcessGuardTest.setUp
    """Each retry starts a complete new capture; no incomplete view is reused."""
    def props(self):
        return dict(MainPID="1", InvocationID="invocation", ControlGroup=GROUP)
    def incomplete(self, pid=2):
        return g.IncompleteObservation("INCOMPLETE_DESCRIPTOR_OBSERVATION", dict(
            pid=pid,descriptor="9",complete=False,identity=copy.deepcopy(self.v["records"][pid])))
    def collect(self, captures, *, properties=None, identities=None, listeners=None, events=None):
        with patch.object(g,"snapshot",side_effect=captures) as capture, \
             patch.object(g,"process_identity",side_effect=identities or (lambda pid,proc:self.v["records"][pid])), \
             patch.object(g,"tcp_listeners",return_value=self.v["listeners"] if listeners is None else listeners), \
             patch.object(g.time,"sleep"):
            result=g.collect_observation(self.guard,Path("/not-used"),properties or self.props,
                                         on_incomplete=(events.append if events is not None else None))
            return result,capture.call_count
    def test_transient_non_listener_descriptor_closure_fresh_capture(self):
        events=[];(v,attr,props),calls=self.collect([self.incomplete(),self.v],events=events)
        self.assertEqual(calls,2);self.assertIs(v,self.v)
        self.assertEqual(attr["collection"]["attempts"],2)
        self.assertTrue(attr["collection"]["complete"])
        self.assertEqual(events,[dict(attempt=1,pid=2,descriptor="9",complete=False)])
    def test_process_fd_enoent_is_incomplete_not_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/"42";folder.mkdir();fds=folder/"fd";fds.mkdir()
            fields=["S","1"]+["0"]*17+["1234"]
            (folder/"stat").write_text("42 (fixture) "+" ".join(fields))
            (folder/"cmdline").write_bytes(b"fixture\0")
            (folder/"exe").symlink_to("/bin/sleep")
            (folder/"comm").write_text("fixture")
            (folder/"cgroup").write_text("0::/isolated\n")
            (fds/"8").symlink_to("socket:[20]");closing=fds/"9";closing.symlink_to("/synthetic/non-listener")
            original=os.readlink
            def readlink(path):
                if Path(path)==closing:closing.unlink()
                return original(path)
            with patch.object(g.os,"readlink",side_effect=readlink),self.assertRaises(g.IncompleteObservation) as error:g.process(42,root)
            self.assertFalse(error.exception.evidence["complete"])
            self.assertEqual(error.exception.evidence["descriptor"],"9")
    def test_listener_disappearance_after_incomplete_is_terminal(self):
        with self.assertRaisesRegex(g.AttributionError,"MISSING_OR_CHANGED_LISTENER"):self.collect([self.incomplete(),self.v],listeners={})
    def test_listener_disappearance_in_fresh_capture_is_terminal(self):
        missing=dict(records=self.v["records"],listeners={})
        with self.assertRaisesRegex(g.AttributionError,"MISSING_OR_AMBIGUOUS_LISTENER"):self.collect([self.incomplete(),missing])
    def test_repeated_failure_bounded_to_three_captures(self):
        events=[]
        with patch.object(g,"snapshot",side_effect=[self.incomplete()]*4) as captures, \
             patch.object(g,"process_identity",side_effect=lambda pid,proc:self.v["records"][pid]), \
             patch.object(g,"tcp_listeners",return_value=self.v["listeners"]),patch.object(g.time,"sleep"), \
             self.assertRaisesRegex(g.AttributionError,"PERSISTENT_INCOMPLETE") as error:
            g.collect_observation(self.guard,Path("/not-used"),self.props,on_incomplete=events.append)
        self.assertEqual(captures.call_count,3);self.assertEqual(len(events),3)
        self.assertFalse(error.exception.evidence["complete"])
    def test_permission_denial_is_not_retried(self):
        failure=g.AttributionError("UNREADABLE_PROCESS_EVIDENCE",dict(error_type="PermissionError"))
        with patch.object(g,"snapshot",side_effect=failure) as capture,self.assertRaises(g.AttributionError):g.collect_observation(self.guard,Path("/not-used"),self.props)
        self.assertEqual(capture.call_count,1)
    def test_pid_replacement_during_incomplete_is_terminal(self):
        changed=copy.deepcopy(self.v["records"][2]);changed["start_ticks"]="replacement"
        with self.assertRaisesRegex(g.AttributionError,"IDENTITY_CHANGED"):self.collect([self.incomplete(),self.v],identities=lambda pid,proc:changed if pid==2 else self.v["records"][pid])
    def test_identity_change_on_fresh_capture(self):
        for key in ["parent","start_ticks","executable","command_sha256","cgroup"]:
            changed=copy.deepcopy(self.v);changed["records"][2][key]="changed"
            with self.subTest(key=key),self.assertRaisesRegex(g.AttributionError,"IDENTITY_CHANGED"):self.collect([self.incomplete(),changed])
    def test_unauthorized_socket_on_fresh_capture(self):
        changed=copy.deepcopy(self.v);changed["records"][1]["sockets"]=["30"]
        changed["listeners"]["30"]=dict(port=9999,address="0100007F")
        with self.assertRaisesRegex(g.AttributionError,"UNAUTHORIZED_LISTENER"):self.collect([self.incomplete(),changed])
    def test_partial_unauthorized_socket_is_terminal(self):
        failure=self.incomplete();failure.evidence["sockets"]=["30"]
        listeners=dict(self.v["listeners"],**{"30":dict(port=9999,address="0100007F")})
        with self.assertRaisesRegex(g.AttributionError,"UNAUTHORIZED_LISTENER"):self.collect([failure,self.v],listeners=listeners)
    def test_missing_process_identity_is_not_retried(self):
        with self.assertRaisesRegex(g.AttributionError,"UNREADABLE_PROCESS"):self.collect([self.incomplete(),self.v],identities=g.AttributionError("UNREADABLE_PROCESS_EVIDENCE"))
    def test_unknown_process_cannot_use_retry(self):
        failure=self.incomplete();failure.evidence["identity"]=row(3,2,"next-server (v15.5.9)")
        self.v["records"][3]=failure.evidence["identity"]
        with self.assertRaisesRegex(g.AttributionError,"UNVERIFIED_AUXILIARY"):self.collect([failure,self.v])
    def test_changed_invocation_after_capture_is_terminal(self):
        calls=iter([self.props(),dict(self.props(),InvocationID="changed")])
        with self.assertRaisesRegex(g.AttributionError,"INVOCATION_CHANGED"):self.collect([self.v],properties=lambda:next(calls))
    def test_time_budget_exhaustion_never_accepts_capture(self):
        with patch.object(g.time,"monotonic",side_effect=[0,0,.3]),self.assertRaisesRegex(g.AttributionError,"PERSISTENT_INCOMPLETE"):self.collect([self.v])

    def test_missing_service_metadata_not_retried(self):
        with patch.object(g,"snapshot") as capture,self.assertRaisesRegex(g.AttributionError,"UNREADABLE_SERVICE"):g.collect_observation(self.guard,Path("/not-used"),lambda:{"MainPID":"1"})
        capture.assert_not_called()
    def test_fd_permission_denial_does_not_become_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);fds=root/"2/fd";fds.mkdir(parents=True);(fds/"9").symlink_to("/synthetic/non-listener")
            with patch.object(g,"process_identity",return_value=self.v["records"][2]),patch.object(g.os,"readlink",side_effect=PermissionError()),self.assertRaisesRegex(g.AttributionError,"UNREADABLE_PROCESS") as error:g.process(2,root)
            self.assertNotIsInstance(error.exception,g.IncompleteObservation)


class LifecycleQualificationTest(unittest.TestCase):
    setUp = ProcessGuardTest.setUp
    def props(self):
        return dict(MainPID="1",InvocationID="invocation",ControlGroup=GROUP)
    def vanished(self,pid=3):
        return g.AttributionError("UNREADABLE_PROCESS_EVIDENCE",dict(pid=pid,stage="identity",error_type="FileNotFoundError",members=[1,2,pid]))
    def test_short_lived_auxiliary_disappears_after_enumeration(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);(folder/"cgroup.procs").write_text("1\n2\n3")
            def read(pid,proc):
                if pid==3:
                    (folder/"cgroup.procs").write_text("1\n2")
                    raise self.vanished()
                return self.v["records"][pid]
            with patch.object(g,"process",side_effect=read),patch.object(g,"tcp_listeners",return_value=self.v["listeners"]),self.assertRaises(g.AttributionError) as error:g.snapshot(folder)
            self.assertEqual(g.diagnostic_category(error.exception,self.guard),"TRANSIENT_MEMBERSHIP_UNVERIFIED")
            self.assertEqual(error.exception.evidence["members"],[1,2,3])
            self.assertNotIn(3,error.exception.evidence["verified_partial"])
    def test_unknown_vanish_then_fresh_stable_is_not_pass(self):
        original_worker=copy.deepcopy(self.guard.worker)
        with patch.object(g,"snapshot",side_effect=[self.vanished(),self.v]) as captures,self.assertRaises(g.AttributionError) as error:g.collect_observation(self.guard,Path("/not-used"),self.props)
        self.assertEqual(captures.call_count,2)
        self.assertEqual(error.exception.evidence["diagnostic"],"TRANSIENT_MEMBERSHIP_UNVERIFIED")
        self.assertFalse(error.exception.evidence["acceptance"])
        fresh=error.exception.evidence["fresh_diagnostic"]
        self.assertEqual(fresh["status"],"CURRENT_PRIMARY_VERIFIED_ONLY")
        self.assertFalse(fresh["membership_gap_closed"])
        self.assertEqual(self.guard.worker,original_worker)
    def test_bounded_fresh_diagnostic_failure_never_loops(self):
        with patch.object(g,"snapshot",side_effect=[self.vanished(),self.vanished()]) as captures,self.assertRaises(g.AttributionError) as error:g.collect_observation(self.guard,Path("/not-used"),self.props)
        self.assertEqual(captures.call_count,2)
        self.assertEqual(error.exception.evidence["fresh_diagnostic"]["status"],"UNVERIFIED")
        self.assertFalse(error.exception.evidence["acceptance"])
    def test_approved_unreadable_has_separate_terminal_diagnostic(self):
        for pid in [1,2]:
            with self.subTest(pid=pid),patch.object(g,"snapshot",side_effect=self.vanished(pid)) as captures,self.assertRaises(g.AttributionError) as error:g.collect_observation(self.guard,Path("/not-used"),self.props)
            self.assertEqual(captures.call_count,1)
            self.assertEqual(error.exception.evidence["diagnostic"],"UNREADABLE_APPROVED_PROCESS")
    def test_changed_membership_has_no_silent_recovery(self):
        gap=g.AttributionError("CGROUP_CHANGED_DURING_READ",dict(members=[1,2,3],members_after=[1,2]))
        with patch.object(g,"snapshot",side_effect=[gap,self.v]),self.assertRaises(g.AttributionError) as error:g.collect_observation(self.guard,Path("/not-used"),self.props)
        self.assertFalse(error.exception.evidence["acceptance"])
        self.assertEqual(error.exception.evidence["diagnostic"],"TRANSIENT_MEMBERSHIP_UNVERIFIED")
    def test_primary_missing_in_membership_is_protection_failure(self):
        failure=g.AttributionError("CGROUP_CHANGED_DURING_READ",dict(members=[1,2],members_after=[1,3]))
        self.assertEqual(g.diagnostic_category(failure,self.guard),"UNAUTHORIZED_OR_REPLACED_WORKER")
    def test_replaced_pid_cannot_be_approved_in_fresh_diagnostic(self):
        changed=copy.deepcopy(self.v);changed["records"][2]["start_ticks"]="reused"
        with patch.object(g,"snapshot",side_effect=[self.vanished(),changed]),self.assertRaises(g.AttributionError) as error:g.collect_observation(self.guard,Path("/not-used"),self.props)
        fresh=error.exception.evidence["fresh_diagnostic"]
        self.assertEqual(fresh["diagnostic"],"UNAUTHORIZED_OR_REPLACED_WORKER")
        self.assertFalse(fresh["acceptance"])
        self.assertEqual(self.guard.worker["start_ticks"],"102")
    def test_foreign_listener_in_fresh_diagnostic_refused(self):
        changed=copy.deepcopy(self.v);changed["records"][3]=row(3,2,"next-server (v15.5.9)",["20"])
        with patch.object(g,"snapshot",side_effect=[self.vanished(),changed]),self.assertRaises(g.AttributionError) as error:g.collect_observation(self.guard,Path("/not-used"),self.props)
        self.assertEqual(error.exception.evidence["fresh_diagnostic"]["diagnostic"],"UNAUTHORIZED_OR_REPLACED_WORKER")
    def test_invocation_changed_in_fresh_diagnostic_refused(self):
        contexts=iter([self.props(),dict(self.props(),InvocationID="changed")])
        with patch.object(g,"snapshot",side_effect=self.vanished()),self.assertRaises(g.AttributionError) as error:g.collect_observation(self.guard,Path("/not-used"),lambda:next(contexts))
        self.assertEqual(error.exception.evidence["fresh_diagnostic"]["diagnostic"],"UNAUTHORIZED_OR_REPLACED_WORKER")
    def test_fresh_diagnostic_has_time_budget(self):
        with patch.object(g,"snapshot",return_value=self.v),patch.object(g.time,"monotonic",side_effect=[0,.3]):
            result=g.fresh_membership_diagnostic(self.guard,Path("/not-used"),self.props,(),Path("/proc"))
        self.assertEqual(result["status"],"BUDGET_EXHAUSTED");self.assertFalse(result["acceptance"])
