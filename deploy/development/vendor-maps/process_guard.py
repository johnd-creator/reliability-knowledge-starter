"""Fail-closed Linux listener attribution for disposable experiments only.

No title-substring worker counting; no implicit approval of children. Snapshots
are bounded consistency checks, not atomic kernel traces. Unreadable/vanished
members reject the observation. Only descriptor ENOENT permits a bounded fresh
collection; an incomplete read is never verified or reused.
"""
import hashlib
import os
import time
from pathlib import Path

class AttributionError(RuntimeError):
    def __init__(self, code, evidence=None):
        super().__init__(code)
        self.evidence = evidence or {}

IDENTITY = ("pid", "parent", "start_ticks", "executable", "exe_device", "exe_inode",
            "command_sha256", "comm", "cgroup")

def identity(record):
    return tuple(record[key] for key in IDENTITY)

class IncompleteObservation(AttributionError):
    """A closed descriptor invalidates this read; it is never a verified view."""


def process_identity(pid, proc=Path("/proc")):
    folder = proc / str(pid)
    try:
        before = (folder / "stat").read_text().rsplit(") ", 1)[1].split()
        raw = (folder / "cmdline").read_bytes()
        executable = os.readlink(folder / "exe")
        exe = (folder / "exe").stat()
        group = (folder / "cgroup").read_text()
        comm = (folder / "comm").read_text().strip()
        after = (folder / "stat").read_text().rsplit(") ", 1)[1].split()
        if before[1] != after[1] or before[19] != after[19] or raw != (folder / "cmdline").read_bytes() or executable != os.readlink(folder / "exe"):
            raise AttributionError("PROCESS_CHANGED_DURING_READ")
        argv = tuple(x.decode("utf-8", "strict") for x in raw.rstrip(b"\0").split(b"\0"))
        if not raw or not argv[0]:
            raise AttributionError("EMPTY_COMMAND")
        return dict(pid=int(pid), parent=int(after[1]), start_ticks=after[19],
                    executable=executable, exe_device=exe.st_dev, exe_inode=exe.st_ino,
                    command_sha256=hashlib.sha256(raw).hexdigest(), comm=comm,
                    cgroup=group, argv=argv)
    except (OSError, ValueError, IndexError, UnicodeError) as error:
        raise AttributionError("UNREADABLE_PROCESS_EVIDENCE", dict(pid=int(pid), stage="identity", error_type=type(error).__name__)) from error


def process(pid, proc=Path("/proc")):
    record = process_identity(pid, proc)
    sockets = set()
    folder = proc / str(pid)
    try:
        for fd in (folder / "fd").iterdir():
            try:
                target = os.readlink(fd)
            except FileNotFoundError as error:
                # No skipped descriptor, stale view or assumed socket type.
                raise IncompleteObservation("INCOMPLETE_DESCRIPTOR_OBSERVATION",
                    dict(pid=int(pid), descriptor=fd.name, complete=False, identity=record, sockets=sorted(sockets))) from error
            if target.startswith("socket:["):
                sockets.add(target[8:-1])
    except OSError as error:
        raise AttributionError("UNREADABLE_PROCESS_EVIDENCE", dict(pid=int(pid), stage="file_descriptors", error_type=type(error).__name__)) from error
    if identity(record) != identity(process_identity(pid, proc)):
        raise AttributionError("PROCESS_CHANGED_DURING_READ")
    return dict(record, sockets=sorted(sockets))

def tcp_listeners(proc=Path("/proc")):
    listeners = {}
    try:
        for name in ("tcp", "tcp6"):
            for line in (proc / "net" / name).read_text().splitlines()[1:]:
                fields = line.split()
                if fields[3] == "0A":
                    address, port = fields[1].split(":")
                    listeners[fields[9]] = dict(port=int(port, 16), address=address)
    except (OSError, ValueError, IndexError) as error:
        raise AttributionError("UNREADABLE_LISTENER_EVIDENCE") from error
    return listeners

def snapshot(group, proc=Path("/proc"), port=None):
    try:
        members = sorted(int(x) for x in (group / "cgroup.procs").read_text().split())
        if not members or len(members) > 128:
            raise AttributionError("INVALID_CGROUP_MEMBERSHIP")
        records = {}
        try:
            for pid in members:
                records[pid] = process(pid, proc)
        except AttributionError as error:
            error.evidence.update(dict(members=members, verified_partial=sanitized(dict(records=records))))
            raise
        listeners = tcp_listeners(proc)
        after = sorted(int(x) for x in (group / "cgroup.procs").read_text().split())
        if members != after:
            raise AttributionError("CGROUP_CHANGED_DURING_READ")
        second = {pid: process(pid, proc) for pid in members}
        for pid, old in records.items():
            if identity(old) != identity(second[pid]):
                raise AttributionError("PROCESS_CHANGED_DURING_SNAPSHOT")
            if set(old["sockets"]) & set(listeners) != set(second[pid]["sockets"]) & set(listeners):
                raise AttributionError("LISTENER_OWNERSHIP_CHANGED_DURING_SNAPSHOT")
        owned = {inode for row in [*records.values(), *second.values()] for inode in row["sockets"]}
        relevant = lambda items: {inode: item for inode, item in items.items() if inode in owned or item["port"] == port}
        if relevant(listeners) != relevant(tcp_listeners(proc)):
            raise AttributionError("LISTENERS_CHANGED_DURING_SNAPSHOT")
        return dict(records=records, listeners=listeners)
    except (OSError, ValueError) as error:
        raise AttributionError("UNREADABLE_CGROUP_EVIDENCE") from error

def listener_owner(view, port):
    targets = {inode for inode, item in view["listeners"].items() if item["port"] == port}
    if len(targets) != 1:
        raise AttributionError("MISSING_OR_AMBIGUOUS_LISTENER")
    inode = next(iter(targets))
    owners = [pid for pid, row in view["records"].items() if inode in row["sockets"]]
    if len(owners) != 1:
        raise AttributionError("UNAUTHORIZED_OR_SHARED_LISTENER")
    return owners[0], inode

class Guard:
    def __init__(self, view, parent_pid, port, invocation, node, cgroup):
        worker_pid, inode = listener_owner(view, port)
        if view["listeners"][inode]["address"] != "0100007F":
            raise AttributionError("NON_LOOPBACK_LISTENER")
        self.parent = view["records"][parent_pid]
        self.worker = view["records"][worker_pid]
        self.port, self.inode, self.invocation = port, inode, invocation
        self.node, self.cgroup = node, cgroup
        self.auxiliary_identities = {}
        if worker_pid == parent_pid or self.worker["parent"] != parent_pid:
            raise AttributionError("UNEXPECTED_WORKER_ANCESTRY")
        if not self.worker["argv"][0].startswith("next-server ("):
            raise AttributionError("UNEXPECTED_WORKER_COMMAND")
        self.validate(view, parent_pid, invocation)

    def validate(self, view, main_pid, invocation, auxiliaries=()):
        if main_pid != self.parent["pid"] or invocation != self.invocation:
            raise AttributionError("PARENT_OR_INVOCATION_CHANGED")
        for expected in (self.parent, self.worker):
            actual = view["records"].get(expected["pid"])
            if actual is None or identity(actual) != identity(expected):
                raise AttributionError("APPROVED_PROCESS_IDENTITY_CHANGED")
            if actual["executable"] != self.node or actual["cgroup"] != "0::" + self.cgroup + "\n":
                raise AttributionError("EXECUTABLE_OR_CGROUP_MISMATCH")
        owner, inode = listener_owner(view, self.port)
        if owner != self.worker["pid"] or inode != self.inode:
            raise AttributionError("LISTENER_WORKER_CHANGED")
        classified = []
        for pid, row in view["records"].items():
            owned = set(row["sockets"]) & set(view["listeners"])
            if pid == self.worker["pid"]:
                if owned != {self.inode}:
                    raise AttributionError("UNAUTHORIZED_LISTENER")
                continue
            if owned:
                raise AttributionError("UNAUTHORIZED_LISTENER")
            if pid == self.parent["pid"]:
                continue
            # Exact reviewed command, executable and direct parent only. Empty
            # by default. No rule permits a next-server title, even without FD.
            if row["argv"][0].startswith("next-server"):
                raise AttributionError("UNVERIFIED_ADDITIONAL_NEXT_PROCESS")
            if row["parent"] != self.worker["pid"] or row["executable"] != self.node or row["cgroup"] != "0::" + self.cgroup + "\n" or row["argv"] not in auxiliaries:
                raise AttributionError("UNVERIFIED_AUXILIARY_PROCESS")
            if pid in self.auxiliary_identities and self.auxiliary_identities[pid] != identity(row):
                raise AttributionError("AUXILIARY_PID_REUSE_OR_IDENTITY_CHANGED")
            self.auxiliary_identities[pid] = identity(row)
            classified.append(dict(pid=pid, role="EXACT_REVIEWED_AUXILIARY", start_ticks=row["start_ticks"]))
        return dict(worker=self.worker["pid"], parent=self.parent["pid"], inode=self.inode,
                    invocation=self.invocation, auxiliaries=classified)

# Fixed acquisition budget. This retries evidence only, never a process/application.
COLLECTION_ATTEMPTS = 3
COLLECTION_BUDGET_SECONDS = 0.25
COLLECTION_PAUSE_SECONDS = 0.01


def collect_observation(guard, group, properties, auxiliaries=(), proc=Path("/proc"), on_incomplete=None):
    deadline = time.monotonic() + COLLECTION_BUDGET_SECONDS
    incomplete = []
    keys = ("MainPID", "InvocationID", "ControlGroup")
    expected = (str(guard.parent["pid"]), guard.invocation, guard.cgroup)
    for attempt in range(1, COLLECTION_ATTEMPTS + 1):
        if time.monotonic() >= deadline:
            break
        before = properties()
        if not all(isinstance(before.get(key),str) for key in keys):
            raise AttributionError("UNREADABLE_SERVICE_EVIDENCE")
        if tuple(before[key] for key in keys) != expected:
            raise AttributionError("PARENT_OR_INVOCATION_CHANGED")
        try:
            view = snapshot(group, proc=proc, port=guard.port)
        except IncompleteObservation as error:
            # Only descriptor ENOENT can reach here. A missing PID, denied FD,
            # changed membership/identity or invalid listener is not retryable.
            row = error.evidence["identity"]
            pid = row["pid"]
            for approved in (guard.parent, guard.worker):
                if identity(process_identity(approved["pid"], proc)) != identity(approved):
                    raise AttributionError("APPROVED_PROCESS_IDENTITY_CHANGED")
            current = process_identity(pid, proc)
            if identity(current) != identity(row):
                raise AttributionError("PROCESS_CHANGED_DURING_READ")
            approved = next((r for r in (guard.parent, guard.worker) if r["pid"] == pid), None)
            if approved is not None:
                if identity(row) != identity(approved):
                    raise AttributionError("APPROVED_PROCESS_IDENTITY_CHANGED")
            elif row["argv"][0].startswith("next-server") or row["parent"] != guard.worker["pid"] or row["executable"] != guard.node or row["cgroup"] != "0::" + guard.cgroup + "\n" or row["argv"] not in auxiliaries:
                raise AttributionError("UNVERIFIED_AUXILIARY_PROCESS")
            if pid in guard.auxiliary_identities and guard.auxiliary_identities[pid] != identity(row):
                raise AttributionError("AUXILIARY_PID_REUSE_OR_IDENTITY_CHANGED")
            listeners = tcp_listeners(proc)
            observed_listeners = set(error.evidence.get("sockets", ())) & set(listeners)
            allowed_listeners = {guard.inode} if pid == guard.worker["pid"] else set()
            if observed_listeners - allowed_listeners:
                raise AttributionError("UNAUTHORIZED_LISTENER")
            targets = {inode for inode, item in listeners.items() if item["port"] == guard.port}
            if targets != {guard.inode}:
                raise AttributionError("MISSING_OR_CHANGED_LISTENER")
            observation = dict(attempt=attempt, pid=pid, descriptor=error.evidence["descriptor"], complete=False)
            incomplete.append(observation)
            if on_incomplete is not None:
                on_incomplete(observation)
            if attempt < COLLECTION_ATTEMPTS and time.monotonic() + COLLECTION_PAUSE_SECONDS < deadline:
                time.sleep(COLLECTION_PAUSE_SECONDS)
                continue
            break
        after = properties()
        if not all(isinstance(after.get(key),str) for key in keys):
            raise AttributionError("UNREADABLE_SERVICE_EVIDENCE")
        if tuple(after[key] for key in keys) != expected:
            raise AttributionError("PARENT_OR_INVOCATION_CHANGED")
        if time.monotonic() >= deadline:
            break
        attribution = guard.validate(view, int(after["MainPID"]), after["InvocationID"], auxiliaries)
        if time.monotonic() >= deadline:
            break
        attribution["collection"] = dict(complete=True, attempts=attempt, incomplete_observations=incomplete)
        return view, attribution, after
    raise AttributionError("PERSISTENT_INCOMPLETE_LISTENER_EVIDENCE", dict(complete=False, observations=incomplete))


def sanitized(view):
    # Full argv never enters published evidence. Socket ownership is numeric.
    return {pid: {key: value for key, value in row.items() if key != "argv"}
            for pid, row in view["records"].items()}

NEXT_AUXILIARY_HASHES = {
    "compiled/jest-worker/processChild.js": "46f2e1a165a1ec49ce067d00d16af4ce737e92b08b7a24e23db3e9336159d9c9",
    "server/dev/next-dev-server.js": "28885e2e63208c753a3402517323f402bd6681489380c720de5e08127dcdb7f9",
    "server/dev/static-paths-worker.js": "d022b4c5d63a2c968cd577ec475e98635a3c6487dedae10a50cef0a5523a4c24",
}
def reviewed_next_auxiliary(deps, node):
    """Source-reviewed process role, never a discovered-PID allowlist.

Locked Next DevServer creates a Jest child for static paths. The processChild
bootstrap accepts an IPC module: its actual job remains UNKNOWN without IPC
capture. Only this exact helper command can be classified, with the parent,
executable, cgroup, non-listener and identity checks in Guard.validate.
"""
    base = deps.resolve() / "next/dist"
    try:
        for relative, digest in NEXT_AUXILIARY_HASHES.items():
            if hashlib.sha256((base / relative).read_bytes()).hexdigest() != digest:
                raise AttributionError("AUXILIARY_SOURCE_HASH_MISMATCH")
    except OSError as error:
        raise AttributionError("UNREADABLE_AUXILIARY_SOURCE") from error
    return ((node, str(base / "compiled/jest-worker/processChild.js")),)
