"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import type { PageMeta } from "../lib/api";
import { shortIdentifier } from "../lib/format";

const navigation = [
  { href: "/", label: "Overview", icon: "◈" },
  { href: "/assets", label: "Asset Reliability", icon: "◌" },
  { href: "/maintenance", label: "Maintenance", icon: "↻" },
  { href: "/fmea", label: "FMEA", icon: "△" },
  { href: "/rcfa", label: "RCFA", icon: "⌁" },
  { href: "/asset-health", label: "Asset Health", icon: "◒" },
  { href: "/overhauls", label: "Overhaul", icon: "◫" },
  { href: "/data-quality", label: "Data Quality", icon: "✓" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="nadi-shell">
      <aside className="nadi-sidebar">
        <Link href="/" className="nadi-brand" aria-label="NADI Overview">
          <span className="brand-mark" aria-hidden="true"><span /></span>
          <span><strong>NADI</strong><small>Navigasi Analitik Data dan Informasi</small></span>
        </Link>
        <div className="sidebar-context"><span className="pulse-dot" /> Platform Analitik Keandalan Aset Pembangkit</div>
        <nav className="nadi-nav" aria-label="NADI navigation">
          <p className="nav-label">Reliability workspace</p>
          {navigation.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return <Link key={item.href} href={item.href} className={active ? "nav-link active" : "nav-link"}><span className="nav-icon">{item.icon}</span>{item.label}</Link>;
          })}
        </nav>
        <div className="sidebar-footer"><span className="scope-label">OPERATING SCOPE</span><strong>BSR / IP</strong><small>Controlled Reliability Mart</small></div>
      </aside>
      <div className="nadi-content">
        <header className="nadi-topbar">
          <div><span className="topbar-kicker">NADI / RELIABILITY INFORMATION</span><span className="topbar-title">Asset reliability workspace</span></div>
          <div className="topbar-status"><span className="pulse-dot" /> Mart read-only <span className="scope-chip">BSR / IP</span></div>
        </header>
        <main className="nadi-main">{children}</main>
      </div>
    </div>
  );
}

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow: string; title: string; description: string; actions?: ReactNode }) {
  return <div className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="page-description">{description}</p></div>{actions && <div className="page-actions">{actions}</div>}</div>;
}

export function StatCard({ label, value, detail, tone = "default" }: { label: string; value: string | number; detail: string; tone?: "default" | "accent" | "muted" }) {
  return <article className={`stat-card ${tone}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

export function StatusBadge({ value }: { value: string | null | undefined }) {
  const normalized = value?.toUpperCase() ?? "UNKNOWN";
  const tone = normalized.includes("CLOSE") || normalized.includes("COMPLETE") || normalized === "ACTIVE" || normalized === "OPERATING" ? "positive" : normalized === "UNRESOLVED" ? "neutral" : "default";
  return <span className={`status-badge ${tone}`}>{value ?? "—"}</span>;
}

export function Identifier({ value }: { value: string | null | undefined }) {
  return <span className="identifier" title={value ?? undefined}>{shortIdentifier(value)}</span>;
}

export function LoadingState({ label = "Memuat data Reliability Mart…" }: { label?: string }) {
  return <div className="state-card loading-state"><span className="spinner" />{label}</div>;
}

export function EmptyState({ title = "Belum ada data pada dataset Reliability Mart saat ini.", detail }: { title?: string; detail?: string }) {
  return <div className="state-card empty-state"><span className="state-symbol">∅</span><strong>{title}</strong>{detail && <p>{detail}</p>}</div>;
}

export function ErrorState({ message = "Reliability Mart unavailable" }: { message?: string }) {
  return <div className="state-card error-state"><span className="state-symbol">!</span><strong>{message}</strong><p>Data canonical belum dapat dibaca. Coba muat ulang beberapa saat lagi.</p></div>;
}

export function Pagination({ meta, onChange }: { meta: PageMeta; onChange: (offset: number) => void }) {
  const first = meta.total === 0 ? 0 : meta.offset + 1;
  const last = Math.min(meta.offset + meta.limit, meta.total);
  return <div className="pagination"><span>{first}–{last} dari {meta.total.toLocaleString("id-ID")}</span><div><button className="icon-button" disabled={meta.offset === 0} onClick={() => onChange(Math.max(0, meta.offset - meta.limit))}>←</button><span className="page-number">{Math.floor(meta.offset / meta.limit) + 1}</span><button className="icon-button" disabled={!meta.has_more} onClick={() => onChange(meta.offset + meta.limit)}>→</button></div></div>;
}

export function TableFrame({ children, minWidth = 900 }: { children: ReactNode; minWidth?: number }) {
  return <div className="table-frame" style={{ minWidth }}>{children}</div>;
}

export function SectionCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`section-card ${className}`}>{children}</section>;
}
