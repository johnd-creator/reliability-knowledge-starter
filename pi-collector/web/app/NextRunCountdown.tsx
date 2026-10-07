"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { collectorApi, ScheduleView } from "@/lib/api";

function fmt(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
}

export function NextRunCountdown({ onRefresh }: { onRefresh: () => void }) {
  const [schedule, setSchedule] = useState<ScheduleView | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const refreshing = useRef(false);

  const fetchSchedule = useCallback(async () => {
    try {
      setSchedule(await collectorApi.getSchedule());
    } catch {
      setSchedule(null);
    }
  }, []);

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([fetchSchedule(), onRefresh()]);
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  useEffect(() => {
    fetchSchedule();
    const poll = setInterval(fetchSchedule, 15_000);
    return () => clearInterval(poll);
  }, [fetchSchedule]);

  // stable primitives only — `schedule` is a new object on every 15s poll and
  // would keep resetting these timers if used as a dependency
  const stateKey = schedule?.state ?? "unknown";
  const nextRunKey = schedule?.state === "scheduled" ? schedule.next_run_at : null;

  useEffect(() => {
    if (!nextRunKey) {
      setRemaining(null);
      return;
    }
    const next = new Date(nextRunKey).getTime();
    const tick = () => {
      const left = (next - Date.now()) / 1000;
      if (left <= 0) {
        if (!refreshing.current) {
          refreshing.current = true;
          onRefresh();
          fetchSchedule().finally(() => {
            setTimeout(() => (refreshing.current = false), 10_000);
          });
        }
        setRemaining(0);
        return;
      }
      setRemaining(left);
    };
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, [nextRunKey, onRefresh, fetchSchedule]);

  // while a cycle is writing snapshots, stream the fresh data in gradually
  useEffect(() => {
    if (stateKey !== "running") return;
    const t = setInterval(onRefresh, 30_000);
    return () => clearInterval(t);
  }, [stateKey, onRefresh]);

  if (!schedule) {
    return (
      <div className="countdown-box">
        <span className="dot dot-gray" />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600 }}>Jadwal Collector</div>
          <div className="sub-muted">Menghubungkan ke service collector...</div>
        </div>
        <button
          type="button"
          onClick={handleManualRefresh}
          className="btn btn-ghost"
          style={{ padding: "4px 8px", fontSize: "0.8rem" }}
          title="Refresh Data"
        >
          {isRefreshing ? "⏳" : "🔄 Refresh"}
        </button>
      </div>
    );
  }

  if (schedule.state === "running") {
    return (
      <div className="countdown-box countdown-ok">
        <span className="dot dot-green dot-pulse" />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, color: "#34d399" }}>
            Aktivitas Koleksi Terdeteksi
          </div>
          <div className="sub-muted">
            Snapshot sedang diperbarui • Jeda setelah siklus {Math.round((schedule.pause_seconds ?? schedule.interval_seconds) / 60)} mnt
            <br />Kesegaran sinyal mengikuti timestamp sumber.
          </div>
        </div>
        <button
          type="button"
          onClick={handleManualRefresh}
          className="btn btn-ghost"
          style={{ padding: "6px 10px", fontSize: "0.8rem" }}
          title="Refresh Data"
        >
          {isRefreshing ? "⏳" : "🔄 Refresh"}
        </button>
      </div>
    );
  }

  if (schedule.state === "idle") {
    return (
      <div className="countdown-box countdown-warn">
        <span className="dot dot-red" />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, color: "#fb7185" }}>
            Belum Ada Aktivitas Koleksi Terbaru
          </div>
          <div className="sub-muted">
            {schedule.last_run_at
              ? `Siklus terakhir selesai: ${new Date(schedule.last_run_at).toLocaleTimeString("id-ID")} — periksa pemilik worker yang ada`
              : "Belum ada siklus tercatat — periksa pemilik worker yang ada"}
          </div>
        </div>
        <button
          type="button"
          onClick={handleManualRefresh}
          className="btn btn-ghost"
          style={{ padding: "6px 10px", fontSize: "0.8rem" }}
          title="Refresh Status"
        >
          {isRefreshing ? "⏳" : "🔄 Refresh"}
        </button>
      </div>
    );
  }

  return (
    <div className="countdown-box countdown-ok">
      <span className="dot dot-green" />
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 8 }}>
          <span>Perkiraan Mulai Siklus Berikutnya</span>
          <span className="mono" style={{ color: "#34d399", fontWeight: 700, fontSize: "1.1rem" }}>
            {remaining != null ? fmt(remaining) : "--:--"}
          </span>
        </div>
        <div className="sub-muted">
          {remaining === 0 ? "Perkiraan mulai telah lewat; menunggu aktivitas koleksi." :
            `Jeda setelah siklus selesai: ${Math.round((schedule.pause_seconds ?? schedule.interval_seconds) / 60)} menit.`}
          {schedule.last_cycle_duration_seconds != null && <>
            <br />Durasi siklus terakhir: {fmt(schedule.last_cycle_duration_seconds)}.
          </>}
          {schedule.effective_start_to_start_seconds != null && <>
            <br />Perkiraan antar mulai siklus: {fmt(schedule.effective_start_to_start_seconds)}.
          </>}
          <br />Hitungan mundur memperkirakan awal koleksi; data sumber dapat tetap usang.
        </div>
      </div>
      <button
        type="button"
        onClick={handleManualRefresh}
        className="btn btn-ghost"
        style={{ padding: "6px 10px", fontSize: "0.8rem" }}
        title="Refresh Data Sekarang"
      >
        {isRefreshing ? "⏳" : "🔄 Refresh"}
      </button>
    </div>
  );
}
