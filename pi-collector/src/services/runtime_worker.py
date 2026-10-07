"""Session lease for one managed PI scheduler; shares exclusion with migrate.

Legacy manual commands are outside this lease. Disable external cron/systemd
and API source triggers before enabling the managed owner or applying DDL.
"""
import signal
import subprocess
from sqlalchemy import text
from src.services.migrations import LOCK_KEY, MigrationError


def run_owned_worker(engine, command):
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        if not connection.scalar(text("SELECT pg_try_advisory_lock(:key)"), {"key": LOCK_KEY}):
            raise MigrationError("PI migration or managed worker already owns the lease")
        child = None
        previous = {}
        try:
            child = subprocess.Popen(command)
            def forward(signum, frame):
                child.send_signal(signum)
            for signum in (signal.SIGTERM, signal.SIGINT):
                previous[signum] = signal.signal(signum, forward)
            while True:
                try:
                    return child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Fail closed if the owning DB session/lease is lost.
                    connection.execute(text("SELECT 1"))
        finally:
            if child is not None and child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            for signum, handler in previous.items():
                signal.signal(signum, handler)
            if not connection.invalidated:
                connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": LOCK_KEY})
