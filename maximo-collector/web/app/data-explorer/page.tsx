"use client";

import { useEffect, useMemo, useState } from "react";
import {
  collectorApi,
  ExplorerCatalogView,
  ExplorerMappingRow,
  ExplorerRecordDetail,
  ExplorerResourceView,
  ExplorerSourceRecord,
} from "@/lib/api";

type ExplorerTab = "source" | "mart";
type DetailTab = "source" | "canonical" | "provenance" | "evidence" | "mapping";

const iconFor = (value: string) => value.slice(0, 2);

function display(value: unknown): string {
  if (value === null || value === undefined || value === "") return "null";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function evidenceStatus(value: unknown): string {
  if (value && typeof value === "object" && "status" in value) {
    return String((value as { status: unknown }).status);
  }
  return "UNKNOWN";
}

function EvidenceBadge({ value }: { value: unknown }) {
  const status = evidenceStatus(value);
  const neutral = status === "UNRESOLVED" || status === "DEFERRED";
  return <span className={`explorer-badge ${neutral ? "neutral" : "verified"}`}>{status}</span>;
}

function SourceTable({
  rows,
  fields,
  onSelect,
}: {
  rows: ExplorerSourceRecord[];
  fields: string[];
  onSelect: (id: string) => void;
}) {
  return (
    <div className="table-scroll explorer-table-scroll">
      <table>
        <thead>
          <tr>
            <th>Record</th>
            {fields.map((field) => <th key={field}>{field}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.canonical_id} className="explorer-click-row" onClick={() => onSelect(row.canonical_id)}>
              <td><code>{row.canonical_id}</code></td>
              {fields.map((field) => <td key={field}>{display(row.source_data[field])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MartTable({
  rows,
  fields,
  onSelect,
}: {
  rows: Record<string, unknown>[];
  fields: string[];
  onSelect: (id: string) => void;
}) {
  return (
    <div className="table-scroll explorer-table-scroll">
      <table>
        <thead>
          <tr>
            <th>Canonical ID</th>
            {fields.map((field) => <th key={field}>{field}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={String(row.canonical_id)} className="explorer-click-row" onClick={() => onSelect(String(row.canonical_id))}>
              <td><code>{display(row.canonical_id)}</code></td>
              {fields.map((field) => <td key={field}>{display(row[field])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function KeyValueList({ values }: { values: Record<string, unknown> }) {
  const entries = Object.entries(values);
  if (entries.length === 0) return <div className="explorer-null">No approved values available.</div>;
  return (
    <div className="explorer-kv-grid">
      {entries.map(([key, value]) => (
        <div className="explorer-kv" key={key}>
          <span>{key}</span>
          <code>{display(value)}</code>
        </div>
      ))}
    </div>
  );
}

function DetailPanel({ detail, tab, setTab }: { detail: ExplorerRecordDetail; tab: DetailTab; setTab: (tab: DetailTab) => void }) {
  const tabs: Array<[DetailTab, string]> = [
    ["source", "Source Data"],
    ["canonical", "Canonical Mart"],
    ["provenance", "Provenance"],
    ["evidence", "Relationship Evidence"],
    ["mapping", "Field Mapping"],
  ];
  return (
    <aside className="panel explorer-detail-panel">
      <div className="panel-head">
        <div>
          <div className="eyebrow">Record detail</div>
          <h2>{detail.resource.label}</h2>
          <code className="explorer-detail-id">{detail.canonical_id}</code>
        </div>
      </div>
      <div className="explorer-detail-tabs">
        {tabs.map(([key, label]) => (
          <button key={key} className={`quick-chip ${tab === key ? "active" : ""}`} onClick={() => setTab(key)}>{label}</button>
        ))}
      </div>
      {tab === "source" && <><p className="panel-note">Approved Maximo fields retained by the Collector. This is not the complete OSLC response.</p><KeyValueList values={detail.source_data} /></>}
      {tab === "canonical" && <KeyValueList values={detail.canonical} />}
      {tab === "provenance" && <KeyValueList values={detail.provenance} />}
      {tab === "evidence" && (
        <div className="explorer-evidence-list">
          {Object.entries(detail.relationship_evidence).map(([key, value]) => (
            <div key={key} className="explorer-evidence-row"><span>{key}</span><EvidenceBadge value={value} /></div>
          ))}
        </div>
      )}
      {tab === "mapping" && <MappingTable mapping={detail.mapping} />}
    </aside>
  );
}

function MappingTable({ mapping }: { mapping: ExplorerMappingRow[] }) {
  return (
    <div className="table-scroll explorer-mapping-scroll">
      <table>
        <thead><tr><th>Source</th><th>Canonical</th><th>Transform</th><th>Evidence</th></tr></thead>
        <tbody>
          {mapping.map((row, index) => (
            <tr key={`${row.source_field}-${row.canonical_field}-${index}`}>
              <td><code>{row.source_field ?? "null"}</code></td>
              <td><code>{row.canonical_field}</code></td>
              <td>{row.transformation}</td>
              <td><EvidenceBadge value={{ status: row.evidence }} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function DataExplorerPage() {
  const [catalog, setCatalog] = useState<ExplorerCatalogView | null>(null);
  const [selectedObject, setSelectedObject] = useState("MXASSET");
  const [tab, setTab] = useState<ExplorerTab>("source");
  const [detailTab, setDetailTab] = useState<DetailTab>("source");
  const [sourceRows, setSourceRows] = useState<ExplorerSourceRecord[]>([]);
  const [martRows, setMartRows] = useState<Record<string, unknown>[]>([]);
  const [detail, setDetail] = useState<ExplorerRecordDetail | null>(null);
  const [query, setQuery] = useState("");
  const [draftQuery, setDraftQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [limit, setLimit] = useState(25);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const selected = useMemo(
    () => catalog?.resources.find((resource) => resource.resource_key === selectedObject) ?? null,
    [catalog, selectedObject],
  );

  useEffect(() => {
    collectorApi.explorerResources()
      .then((next) => { setCatalog(next); setError(null); })
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Collector API unavailable"));
  }, []);

  useEffect(() => {
    if (!selected) return;
    let cancelled = false;
    setLoading(true);
    setDetail(null);
    const request = tab === "source"
      ? collectorApi.explorerSourceRecords(selected.source_object, { q: query, offset, limit, sort: "updated_desc" })
      : collectorApi.explorerMartRecords(selected.canonical_target, { q: query, offset, limit, sort: "updated_desc" });
    request
      .then((next) => {
        if (cancelled) return;
        if (tab === "source") setSourceRows(next.items as ExplorerSourceRecord[]);
        else setMartRows(next.items as Record<string, unknown>[]);
        setTotal(next.meta.total);
        setHasMore(next.meta.has_more);
        setError(null);
      })
      .catch((reason) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Collector storage unavailable"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [selected, tab, query, offset, limit]);

  function selectResource(sourceObject: string) {
    setSelectedObject(sourceObject);
    setOffset(0);
    setDetail(null);
  }

  function selectTab(nextTab: ExplorerTab) {
    setTab(nextTab);
    setOffset(0);
    setDetail(null);
  }

  async function openDetail(canonicalId: string) {
    if (!selected) return;
    try {
      const next = tab === "source"
        ? await collectorApi.explorerSourceRecord(selected.source_object, canonicalId)
        : await collectorApi.explorerMartRecord(selected.canonical_target, canonicalId);
      setDetail(next);
      setDetailTab(tab === "source" ? "source" : "canonical");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Record detail unavailable");
    }
  }

  const fields = selected ? (tab === "source" ? selected.selected_fields.slice(0, 6) : selected.primary_fields) : [];
  const rowsEmpty = !loading && total === 0;

  return (
    <div>
      <div className="hero">
        <div>
          <div className="eyebrow">Engineering visibility</div>
          <h1>Data Explorer</h1>
          <p className="lede">See what the Collector retained from Maximo and what became a Reliability Mart record.</p>
        </div>
        <div className="hero-meta"><span className="scope-chip">SCOPE <b>BSR / IP</b></span><span className="safe-badge"><i /> READ ONLY</span></div>
      </div>

      {error && <div className="alert"><span>{error}</span><button onClick={() => setError(null)}>Dismiss</button></div>}

      <div className="explorer-switcher" role="tablist" aria-label="Data view">
        <button className={tab === "source" ? "active" : ""} onClick={() => selectTab("source")}><strong>Downloaded Source Data</strong><small>Approved Maximo fields retained by Collector</small></button>
        <button className={tab === "mart" ? "active" : ""} onClick={() => selectTab("mart")}><strong>Reliability Mart</strong><small>Canonical records after mapping</small></button>
      </div>

      <div className="explorer-grid">
        <section className="panel explorer-resource-panel">
          <div className="panel-head"><div><div className="eyebrow">Allowlisted resources</div><h2>Reliability Contract v1</h2></div><span className="count-pill">{catalog?.resources.length ?? 0} sources</span></div>
          <div className="resource-list">
            {(catalog?.resources ?? []).map((resource) => (
              <button key={resource.resource_key} className={`resource-row ${selectedObject === resource.resource_key ? "active" : ""}`} onClick={() => selectResource(resource.resource_key)}>
                <span className="resource-icon">{iconFor(resource.source_object)}</span>
                <span className="resource-name"><strong>{resource.label}</strong><code>{resource.source_object} → {resource.canonical_target}</code></span>
                <span className="resource-count">{resource.records}<small>{resource.status === "READY" ? "records" : "empty"}</small></span>
              </button>
            ))}
          </div>
          <div className="panel-note"><span className="dot" /> Source view is an approved projection, not unrestricted raw OSLC.</div>
          <div className="explorer-deferred"><strong>Deferred / not available</strong>{(catalog?.deferred ?? []).map((item) => <span key={item.source_object}><code>{item.source_object}</code>{item.label}</span>)}</div>
        </section>

        <section className="panel explorer-meta-panel">
          {selected ? <>
            <div className="eyebrow">{tab === "source" ? "Source resource" : "Canonical entity"}</div>
            <h2>{selected.label}</h2>
            <p className="explorer-subtitle"><code>{selected.source_object}</code> → <code>{selected.canonical_target}</code></p>
            <div className="facts explorer-facts">
              <div><dt>System</dt><dd>{selected.source_system}</dd></div>
              <div><dt>Module</dt><dd>{selected.module}</dd></div>
              <div><dt>Scope</dt><dd>{selected.scope.site} / {selected.scope.organization}</dd></div>
              <div><dt>Contract</dt><dd>{selected.contract_version}</dd></div>
              <div><dt>Records</dt><dd>{selected.records}</dd></div>
              <div><dt>Last sync</dt><dd>{selected.last_sync ? new Date(selected.last_sync).toLocaleString() : "—"}</dd></div>
            </div>
            {catalog?.integrity && <div className="explorer-integrity-summary">
              <h3 className="explorer-section-title">Reference integrity</h3>
              <div className="explorer-integrity-grid">
                <span>Asset refs <b>{catalog.integrity.asset_reference_resolved}/{catalog.integrity.asset_reference_total}</b> resolved</span>
                <span>Work Order refs <b>{catalog.integrity.workorder_reference_resolved}/{catalog.integrity.workorder_reference_total}</b> resolved</span>
              </div>
            </div>}
            <h3 className="explorer-section-title">Selected fields ({selected.selected_fields.length})</h3>
            <div className="explorer-field-chips">{selected.selected_fields.map((field) => <code key={field}>{field}</code>)}</div>
          </> : <div className="empty">Loading resource catalog…</div>}
        </section>
      </div>

      <section className="panel data-panel explorer-data-panel">
        <div className="panel-head"><div><div className="eyebrow">{tab === "source" ? "Source projection" : "Canonical preview"}</div><h2>{tab === "source" ? "Downloaded fields" : selected?.canonical_target ?? "Reliability Mart"}</h2></div><span className="count-pill">{total} total</span></div>
        <div className="table-tools-bar"><div className="table-filters"><input className="search-input" value={draftQuery} onChange={(event) => setDraftQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { setOffset(0); setQuery(draftQuery); } }} placeholder="Search approved fields…" /><button className="btn btn-primary" onClick={() => { setOffset(0); setQuery(draftQuery); }}>Search</button>{query && <button className="ghost-button" onClick={() => { setDraftQuery(""); setQuery(""); setOffset(0); }}>Clear</button>}</div><label className="page-size-selector">Rows <select value={limit} onChange={(event) => { setLimit(Number(event.target.value)); setOffset(0); }}><option value={25}>25</option><option value={50}>50</option><option value={100}>100</option><option value={200}>200</option></select></label></div>
        {loading ? <div className="empty">Loading local Collector storage…</div> : rowsEmpty ? <div className="empty"><strong>No records loaded into Reliability Mart yet.</strong><br />The Collector/Contract is configured, but the production initial load has not been executed.</div> : selected && tab === "source" ? <SourceTable rows={sourceRows} fields={fields} onSelect={openDetail} /> : selected ? <MartTable rows={martRows} fields={fields} onSelect={openDetail} /> : <div className="empty">Select a resource.</div>}
        <div className="pagination-bar"><span className="pagination-info">{total === 0 ? "0 records" : `${offset + 1}–${Math.min(offset + limit, total)} of ${total}`}</span><div className="pagination-controls"><button className="page-btn" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - limit))}>←</button><span className="page-btn active">{Math.floor(offset / limit) + 1}</span><button className="page-btn" disabled={!hasMore} onClick={() => setOffset(offset + limit)}>→</button></div></div>
      </section>

      {detail && <DetailPanel detail={detail} tab={detailTab} setTab={setDetailTab} />}
    </div>
  );
}
