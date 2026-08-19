"""Snapshot schedule computation for the web countdown.

The snapshot collector runs on a repeating cycle (cron ``*/5`` or
``picollector run --interval-seconds 300``). One cycle takes minutes — the
client is rate-limited to 1 req/s across 433 attributes — so a daemon's real
period is ``cycle_duration + interval``, not the bare interval. This module
turns the last recorded run into an honest schedule state:

* ``running``  — snapshots are being written right now (latest activity < 90s)
* ``scheduled``— collector alive; next cycle expected at ``last_run_at + interval``
* ``idle``     — collector has not reported for longer than one full period
                 plus grace; the UI should show a red "not running" warning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

DEFAULT_SNAPSHOT_INTERVAL_SECONDS = 300
# a snapshot row lands every ~1s during a run; 90s of silence = not writing
RUNNING_ACTIVITY_WINDOW_SECONDS = 90

STATE_RUNNING = "running"
STATE_SCHEDULED = "scheduled"
STATE_IDLE = "idle"


@dataclass(frozen=True)
class ScheduleInfo:
    interval_seconds: int
    state: str
    last_run_at: datetime | None
    next_run_at: datetime | None
    active: bool  # anything other than idle
    last_cycle_duration_seconds: float | None = field(default=None)


def _aware(dt: datetime | None) -> datetime | None:
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def compute_schedule(
    last_run_at: datetime | None,
    now: datetime,
    interval_seconds: int = DEFAULT_SNAPSHOT_INTERVAL_SECONDS,
    *,
    last_cycle_duration_seconds: float | None = None,
    latest_activity_at: datetime | None = None,
) -> ScheduleInfo:
    """Compute collector schedule state.

    Args:
        last_run_at: when the last snapshot cycle COMPLETED (cursor/run log).
        now: current time.
        interval_seconds: configured cycle interval (seconds).
        last_cycle_duration_seconds: how long the last cycle took; sizes the
            idle deadline honestly (daemon period = duration + interval).
        latest_activity_at: most recent snapshot write time; within
            RUNNING_ACTIVITY_WINDOW_SECONDS it means a cycle is in progress.
    """
    if interval_seconds <= 0:
        interval_seconds = DEFAULT_SNAPSHOT_INTERVAL_SECONDS
    now = _aware(now) or now
    last_run_at = _aware(last_run_at)
    latest_activity_at = _aware(latest_activity_at)

    now_ts = now.timestamp()

    # --- running: fresh snapshot writes ---
    if (
        latest_activity_at is not None
        and now_ts - latest_activity_at.timestamp() <= RUNNING_ACTIVITY_WINDOW_SECONDS
    ):
        return ScheduleInfo(
            interval_seconds=interval_seconds,
            state=STATE_RUNNING,
            last_run_at=last_run_at,
            next_run_at=None,
            active=True,
            last_cycle_duration_seconds=last_cycle_duration_seconds,
        )

    # --- no history at all ---
    if last_run_at is None:
        return ScheduleInfo(
            interval_seconds=interval_seconds,
            state=STATE_IDLE,
            last_run_at=None,
            next_run_at=None,
            active=False,
            last_cycle_duration_seconds=last_cycle_duration_seconds,
        )

    last_ts = last_run_at.timestamp()
    # daemon: sleep(interval) starts when the cycle ENDS; cycle N+1 starts at
    # last_ts + interval. (Cron */5 fires at least this often too.)
    next_ts = last_ts + interval_seconds

    # idle deadline: one full period (duration + interval) + grace. Without a
    # known duration, assume duration ~= interval (2x total).
    duration = (
        last_cycle_duration_seconds
        if last_cycle_duration_seconds and last_cycle_duration_seconds > 0
        else float(interval_seconds)
    )
    deadline = last_ts + interval_seconds + duration + 120.0

    if now_ts > deadline:
        state, active = STATE_IDLE, False
    else:
        state, active = STATE_SCHEDULED, True

    return ScheduleInfo(
        interval_seconds=interval_seconds,
        state=state,
        last_run_at=last_run_at,
        next_run_at=datetime.fromtimestamp(next_ts, tz=timezone.utc)
        if state == STATE_SCHEDULED
        else None,
        active=active,
        last_cycle_duration_seconds=last_cycle_duration_seconds,
    )
