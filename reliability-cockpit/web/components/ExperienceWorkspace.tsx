"use client";
import { useId, type ReactNode } from "react";
import { Button } from "./ui";
/** Anchor-page patterns. No transport, authority, persistence or derived engineering state. */
export function WorkspaceToolbar({
  children,
  label,
}: {
  children: ReactNode;
  label: string;
}) {
  return (
    <div className="experience-toolbar" role="group" aria-label={label}>
      {children}
    </div>
  );
}
export function CompactFacts({
  items,
}: {
  items: { label: string; value: ReactNode; detail: string }[];
}) {
  return (
    <dl className="experience-facts">
      {items.map((item) => (
        <div key={item.label}>
          <dt>{item.label}</dt>
          <dd>
            <strong>{item.value}</strong>
            <small>{item.detail}</small>
          </dd>
        </div>
      ))}
    </dl>
  );
}
export function RecordNavigator({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <details className="record-navigator" open>
      <summary>{title}</summary>
      <nav aria-label={title}>{children}</nav>
    </details>
  );
}
export function DetailSection({
  eyebrow,
  title,
  children,
  className = "",
}: {
  eyebrow: string;
  title: string;
  children: ReactNode;
  className?: string;
}) {
  const id = useId();
  return (
    <section
      className={"experience-detail-section " + className}
      aria-labelledby={id}
    >
      <header>
        <p className="eyebrow">{eyebrow}</p>
        <h3 id={id}>{title}</h3>
      </header>
      <div>{children}</div>
    </section>
  );
}
/** Every pane stays mounted. In-page navigation preserves unsaved inputs and their CAS base. */
export function SectionJump({
  items,
}: {
  items: { id: string; label: string }[];
}) {
  return (
    <nav className="section-jump" aria-label="Bagian rekam">
      {items.map((item) => (
        <Button
          variant="ghost"
          key={item.id}
          onClick={() => {
            const target = document.getElementById(item.id);
            target?.scrollIntoView({ block: "start", behavior: "auto" });
            target?.focus({ preventScroll: true });
          }}
        >
          {item.label}
        </Button>
      ))}
    </nav>
  );
}
