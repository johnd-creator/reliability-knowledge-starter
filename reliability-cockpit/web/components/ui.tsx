"use client";

import Link from "next/link";
import { type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode } from "react";
import type { PageMeta } from "../lib/api";
import { shortIdentifier } from "../lib/format";

export { AppShell } from "./AppNavigation";

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow: string; title: string; description: string; actions?: ReactNode }) {
  return <div className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="page-description">{description}</p></div>{actions && <div className="page-actions">{actions}</div>}</div>;
}

export function StatCard({ label, value, detail, tone = "default" }: { label: string; value: string | number; detail: string; tone?: "default" | "accent" | "muted" }) {
  return <article className={`stat-card ${tone}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

export function DataMaturity({ state, detail }: { state: string; detail?: string }) {
  return <span className="maturity-badge" title={detail}>{state}</span>;
}

export type StatusBadgeMode = "semantic" | "raw-neutral";

export function StatusBadge({ value, mode = "raw-neutral" }: { value: string | null | undefined; mode?: StatusBadgeMode }) {
  const normalized = value?.toUpperCase() ?? "UNKNOWN";
  const tone = mode === "semantic" && (normalized.includes("CLOSE") || normalized.includes("COMPLETE") || normalized === "ACTIVE" || normalized === "OPERATING") ? "positive" : "neutral";
  return <span className={`status-badge ${tone}`}>{value ?? "—"}</span>;
}

export function Identifier({ value }: { value: string | null | undefined }) {
  return <span className="identifier" title={value ?? undefined}>{shortIdentifier(value)}</span>;
}

export function LoadingState({ label = "Memuat data Reliability Mart…" }: { label?: string }) {
  return <div className="state-card loading-state" role="status" aria-live="polite"><span className="spinner" aria-hidden="true" />{label}</div>;
}

export function EmptyState({ title = "Belum ada data Reliability Mart untuk tampilan ini.", detail }: { title?: string; detail?: string }) {
  return <div className="state-card empty-state"><span className="state-symbol">∅</span><strong>{title}</strong>{detail && <p>{detail}</p>}</div>;
}

export function ErrorState({ message = "Reliability Mart unavailable", onRetry }: { message?: string; onRetry?: () => void }) {
  return <div className="state-card error-state" role="alert"><span className="state-symbol">!</span><strong>{message}</strong><p>Data Reliability Mart belum dapat dibaca. Coba muat ulang beberapa saat lagi.</p>{onRetry && <Button onClick={onRetry}>Try again</Button>}</div>;
}

export function Pagination({ meta, onChange }: { meta: PageMeta; onChange: (offset: number) => void }) {
  const first = meta.total === 0 ? 0 : meta.offset + 1;
  const last = Math.min(meta.offset + meta.limit, meta.total);
  return <div className="pagination"><span>{first}–{last} dari {meta.total.toLocaleString("id-ID")}</span><div><button className="icon-button" type="button" aria-label="Previous page" disabled={meta.offset === 0} onClick={() => onChange(Math.max(0, meta.offset - meta.limit))}>←</button><span className="page-number" aria-live="polite">{Math.floor(meta.offset / meta.limit) + 1}</span><button className="icon-button" type="button" aria-label="Next page" disabled={!meta.has_more} onClick={() => onChange(meta.offset + meta.limit)}>→</button></div></div>;
}

export function TableFrame({ children, minWidth = 900, label = "Data table, scroll horizontally for additional columns" }: { children: ReactNode; minWidth?: number; label?: string }) {
  return <div className="table-frame" role="region" aria-label={label} tabIndex={0}><div className="table-content" style={{ minWidth }}>{children}</div></div>;
}

export function SectionCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`section-card ${className}`}>{children}</section>;
}

export function Button({ variant = "secondary", className = "", type = "button", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "destructive" }) {
  return <button {...props} type={type} className={`button ${variant} ${className}`} />;
}

export function InputControl({ label, id, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string; id: string }) {
  return <label htmlFor={id}>{label}<input {...props} id={id} className="input-control" /></label>;
}

export function Breadcrumbs({ items }: { items: { label: string; href?: string }[] }) {
  return <nav aria-label="Breadcrumb"><ol className="breadcrumbs">{items.map((item, index) => <li key={`${item.label}-${index}`}>{item.href ? <Link href={item.href}>{item.label}</Link> : <span aria-current={index === items.length - 1 ? "page" : undefined}>{item.label}</span>}</li>)}</ol></nav>;
}

export function Feedback({ children, error = false }: { children: ReactNode; error?: boolean }) {
  return <div className={`feedback ${error ? "error" : ""}`} role={error ? "alert" : "status"}>{children}</div>;
}
