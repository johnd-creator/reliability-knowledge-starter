"use client";

import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import Link from "next/link";
import {
  collectorApi,
  EquipmentView,
  WorkOrderView,
  ServiceRequestView,
  GenericView,
  StatsView,
  CollectRunView,
  timeAgo,
} from "@/lib/api";
import { CollectStatusBar } from "./CollectStatusBar";

const resources = [
  { key: "equipment", label: "Equipment", object: "mxapiasset", desc: "Asset master & specifications" },
  { key: "work_order", label: "Work Orders", object: "mxwodetail", desc: "Corrective & preventive maintenance" },
  { key: "service_request", label: "Service Requests", object: "mxapisr", desc: "User tickets & fault reports" },
  { key: "person", label: "Persons", object: "mxperson", desc: "Craft, technicians & personnel" },
  { key: "item", label: "Items", object: "mxitem", desc: "Spare parts & inventory master" },
  { key: "labor", label: "Labor", object: "mxapilabor", desc: "Craft rates & labor qualifications" },
] as const;

type ResourceKey = (typeof resources)[number]["key"];

export default function HomePage() {
  const [stats, setStats] = useState<StatsView | null>(null);
  const [status, setStatus] = useState<Record<string, { watermark: string | null; rows: number }>>({});
  const [runs, setRuns] = useState<CollectRunView[]>([]);

  // Datasets
  const [equipmentList, setEquipmentList] = useState<EquipmentView[]>([]);
  const [workOrdersList, setWorkOrdersList] = useState<WorkOrderView[]>([]);
  const [serviceRequestsList, setServiceRequestsList] = useState<ServiceRequestView[]>([]);
  const [personsList, setPersonsList] = useState<GenericView[]>([]);
  const [itemsList, setItemsList] = useState<GenericView[]>([]);
  const [laborList, setLaborList] = useState<GenericView[]>([]);

  // Selected Resource Tab
  const [selectedResource, setSelectedResource] = useState<ResourceKey>("equipment");

  // Multi-Filter State
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [unitFilter, setUnitFilter] = useState("ALL");
  const [classFilter, setClassFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [quickFilter, setQuickFilter] = useState("ALL");
  const [workSiteFilter, setWorkSiteFilter] = useState("ALL");
  const [assignedFilter, setAssignedFilter] = useState("ALL");
  const [orgFilter, setOrgFilter] = useState("ALL");

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortBy, setSortBy] = useState<string>("id");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const dataSectionRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    try {
      const [nextStats, nextStatus, nextRuns, nextEquipment] = await Promise.all([
        collectorApi.stats(),
        collectorApi.status(),
        collectorApi.runs(),
        collectorApi.equipment(5000),
      ]);
      setStats(nextStats);
      setStatus(nextStatus);
      setRuns(nextRuns);
      setEquipmentList(nextEquipment);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshSelectedData = useCallback(async () => {
    await load();
    if (selectedResource === "work_order") setWorkOrdersList(await collectorApi.workOrders(5000));
    if (selectedResource === "service_request") setServiceRequestsList(await collectorApi.serviceRequests(5000));
    if (selectedResource === "person") setPersonsList(await collectorApi.persons(5000));
    if (selectedResource === "item") setItemsList(await collectorApi.items(5000));
    if (selectedResource === "labor") setLaborList(await collectorApi.labor(5000));
  }, [load, selectedResource]);

  // Lazy load other datasets when selected
  useEffect(() => {
    if (selectedResource === "work_order" && workOrdersList.length === 0) {
      collectorApi.workOrders(5000).then(setWorkOrdersList).catch(() => {});
    } else if (selectedResource === "service_request" && serviceRequestsList.length === 0) {
      collectorApi.serviceRequests(5000).then(setServiceRequestsList).catch(() => {});
    } else if (selectedResource === "person" && personsList.length === 0) {
      collectorApi.persons(5000).then(setPersonsList).catch(() => {});
    } else if (selectedResource === "item" && itemsList.length === 0) {
      collectorApi.items(5000).then(setItemsList).catch(() => {});
    } else if (selectedResource === "labor" && laborList.length === 0) {
      collectorApi.labor(5000).then(setLaborList).catch(() => {});
    }
  }, [selectedResource, workOrdersList.length, serviceRequestsList.length, personsList.length, itemsList.length, laborList.length]);

  useEffect(() => {
    load();
  }, [load]);

  // Reset pagination & filters on tab change
  const handleSelectResource = (key: ResourceKey) => {
    setSelectedResource(key);
    setQuery("");
    setStatusFilter("ALL");
    setTypeFilter("ALL");
    setUnitFilter("ALL");
    setClassFilter("ALL");
    setPriorityFilter("ALL");
    setQuickFilter("ALL");
    setWorkSiteFilter("ALL");
    setAssignedFilter("ALL");
    setOrgFilter("ALL");
    setSortBy("id");
    setSortOrder("asc");
    if (dataSectionRef.current) {
      dataSectionRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [query, statusFilter, typeFilter, unitFilter, classFilter, priorityFilter, quickFilter, workSiteFilter, assignedFilter, orgFilter, selectedResource, pageSize]);

  async function handleSync(object: string, e?: React.MouseEvent) {
    if (e) e.stopPropagation();
    setSyncing(object);
    setError(null);
    try {
      await collectorApi.sync(object);
      await load();
      if (selectedResource === "work_order") {
        setWorkOrdersList(await collectorApi.workOrders(5000));
      } else if (selectedResource === "service_request") {
        setServiceRequestsList(await collectorApi.serviceRequests(5000));
      } else if (selectedResource === "person") {
        setPersonsList(await collectorApi.persons(5000));
      } else if (selectedResource === "item") {
        setItemsList(await collectorApi.items(5000));
      } else if (selectedResource === "labor") {
        setLaborList(await collectorApi.labor(5000));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSyncing(null);
    }
  }

  // Filter options
  const currentStatusOptions = useMemo(() => {
    let list: string[] = [];
    if (selectedResource === "equipment") {
      list = equipmentList.map((e) => e.status).filter(Boolean) as string[];
    } else if (selectedResource === "work_order") {
      list = workOrdersList.map((w) => w.status).filter(Boolean) as string[];
    } else if (selectedResource === "service_request") {
      list = serviceRequestsList.map((s) => s.status).filter(Boolean) as string[];
    } else if (selectedResource === "person") {
      list = personsList.map((row) => row.status).filter(Boolean) as string[];
    } else if (selectedResource === "item") {
      list = itemsList.map((row) => row.status).filter(Boolean) as string[];
    } else if (selectedResource === "labor") {
      list = laborList.map((row) => row.status).filter(Boolean) as string[];
    }
    return Array.from(new Set(list)).sort();
  }, [selectedResource, equipmentList, workOrdersList, serviceRequestsList, personsList, itemsList, laborList]);

  const currentTypeOptions = useMemo(() => {
    const list =
      selectedResource === "work_order"
        ? workOrdersList.map((row) => row.work_type)
        : selectedResource === "service_request"
          ? serviceRequestsList.map((row) => row.work_type)
          : selectedResource === "item"
            ? itemsList.map((row) => row.item_type)
          : [];
    return Array.from(new Set(list.filter(Boolean) as string[])).sort();
  }, [selectedResource, workOrdersList, serviceRequestsList, itemsList]);

  const currentUnitOptions = useMemo(() => {
    if (selectedResource === "equipment") {
      return Array.from(new Set(equipmentList.map((row) => row.unit).filter(Boolean) as string[])).sort();
    }
    if (selectedResource === "item") {
      return Array.from(new Set(itemsList.map((row) => row.issue_unit).filter(Boolean) as string[])).sort();
    }
    return [];
  }, [selectedResource, equipmentList, itemsList]);

  const currentWorkSiteOptions = useMemo(() => (
    selectedResource === "labor"
      ? Array.from(new Set(laborList.map((row) => row.work_site).filter(Boolean) as string[])).sort()
      : []
  ), [selectedResource, laborList]);

  const currentOrgOptions = useMemo(() => (
    selectedResource === "person"
      ? Array.from(new Set(personsList.map((row) => row.location_org).filter(Boolean) as string[])).sort()
      : []
  ), [selectedResource, personsList]);

  const currentClassOptions = useMemo(() => {
    if (selectedResource === "equipment") {
      return Array.from(new Set(equipmentList.map((e) => e.equipment_class).filter(Boolean) as string[])).sort();
    } else if (selectedResource === "work_order") {
      return Array.from(new Set(workOrdersList.map((w) => w.work_class).filter(Boolean) as string[])).sort();
    }
    return [];
  }, [selectedResource, equipmentList, workOrdersList]);

  const currentPriorityOptions = useMemo(() => {
    if (selectedResource === "equipment") {
      const list = equipmentList.map((e) => e.priority).filter((p) => p != null) as number[];
      return Array.from(new Set(list)).sort((a, b) => a - b).map(String);
    } else if (selectedResource === "work_order") {
      return Array.from(new Set(workOrdersList.map((w) => w.priority).filter(Boolean) as string[])).sort();
    } else if (selectedResource === "service_request") {
      return Array.from(new Set(serviceRequestsList.map((s) => s.reported_priority).filter(Boolean) as string[])).sort();
    }
    return [];
  }, [selectedResource, equipmentList, workOrdersList, serviceRequestsList]);

  // Filtered and Sorted Data
  const currentDataset = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list: Array<Record<string, unknown>> = [];

    if (selectedResource === "equipment") {
      list = equipmentList.filter((row) => {
        const matchStatus = statusFilter === "ALL" || row.status === statusFilter;
        const matchUnit = unitFilter === "ALL" || row.unit === unitFilter;
        const matchClass = classFilter === "ALL" || row.equipment_class === classFilter;
        const matchPriority = priorityFilter === "ALL" || (row.priority != null && String(row.priority) === priorityFilter);

        let matchQuick = true;
        if (quickFilter === "RUNNING") {
          matchQuick = row.is_running === true || row.status?.toLowerCase() === "operating";
        } else if (quickFilter === "HIGH_PRIORITY") {
          matchQuick = row.priority != null && row.priority <= 2;
        } else if (quickFilter === "WITH_VENDOR") {
          matchQuick = Boolean(row.manufacturer || row.vendor);
        }

        const matchSearch =
          !q ||
          [row.id, row.name, row.location_id, row.unit, row.equipment_class, row.status, row.manufacturer, row.vendor].some(
            (v) => v?.toLowerCase().includes(q)
          );
        return matchStatus && matchUnit && matchClass && matchPriority && matchQuick && matchSearch;
      }) as unknown as Array<Record<string, unknown>>;
    } else if (selectedResource === "work_order") {
      list = workOrdersList.filter((row) => {
        const matchStatus = statusFilter === "ALL" || row.status === statusFilter;
        const matchType = typeFilter === "ALL" || row.work_type === typeFilter;
        const matchClass = classFilter === "ALL" || row.work_class === classFilter;
        const matchPriority = priorityFilter === "ALL" || row.priority === priorityFilter;

        let matchQuick = true;
        if (quickFilter === "EMERGENCY") {
          matchQuick = ["EM", "CM", "BD", "CORR"].includes((row.work_type || "").toUpperCase());
        } else if (quickFilter === "PREVENTIVE") {
          matchQuick = (row.work_type || "").toUpperCase() === "PM";
        } else if (quickFilter === "DOWNTIME") {
          matchQuick = row.downtime_hours != null && row.downtime_hours > 0;
        }

        const matchSearch =
          !q ||
          [row.id, row.equipment_id, row.location_id, row.status, row.work_type, row.description, row.reported_by, row.supervisor].some(
            (v) => v?.toLowerCase().includes(q)
          );
        return matchStatus && matchType && matchClass && matchPriority && matchQuick && matchSearch;
      }) as unknown as Array<Record<string, unknown>>;
    } else if (selectedResource === "service_request") {
      list = serviceRequestsList.filter((row) => {
        const matchStatus = statusFilter === "ALL" || row.status === statusFilter;
        const matchType = typeFilter === "ALL" || row.work_type === typeFilter;
        const matchPriority = priorityFilter === "ALL" || row.reported_priority === priorityFilter;

        let matchQuick = true;
        if (quickFilter === "HIGH_PRIORITY") {
          matchQuick = ["1", "2", "P1", "P2", "HIGH"].includes((row.reported_priority || "").toUpperCase());
        } else if (quickFilter === "HAS_RISK") {
          matchQuick = Boolean(row.risk_area_process || row.risk_area_human || row.risk_area_environment);
        }

        const matchSearch =
          !q ||
          [row.id, row.equipment_id, row.location_id, row.status, row.description, row.reported_by, row.reported_by_name].some(
            (v) => v?.toLowerCase().includes(q)
          );
        return matchStatus && matchType && matchPriority && matchQuick && matchSearch;
      }) as unknown as Array<Record<string, unknown>>;
    } else if (selectedResource === "person") {
      list = personsList.filter(
        (r) => (statusFilter === "ALL" || r.status === statusFilter) &&
          (orgFilter === "ALL" || r.location_org === orgFilter) &&
          (!q || [r.id, r.display_name, r.first_name, r.status, r.location_org].some((v) => v?.toLowerCase().includes(q)))
      ) as unknown as Array<Record<string, unknown>>;
    } else if (selectedResource === "item") {
      list = itemsList.filter(
        (r) => (statusFilter === "ALL" || r.status === statusFilter) &&
          (typeFilter === "ALL" || r.item_type === typeFilter) &&
          (unitFilter === "ALL" || r.issue_unit === unitFilter) &&
          (!q || [r.id, r.description, r.status, r.item_type, r.issue_unit, r.order_unit].some((v) => v?.toLowerCase().includes(q)))
      ) as unknown as Array<Record<string, unknown>>;
    } else if (selectedResource === "labor") {
      list = laborList.filter(
        (r) => (statusFilter === "ALL" || r.status === statusFilter) &&
          (workSiteFilter === "ALL" || r.work_site === workSiteFilter) &&
          (assignedFilter === "ALL" || String(Boolean(r.is_assigned)) === assignedFilter) &&
          (!q || [r.id, r.person_id, r.status, r.status_description, r.work_site].some((v) => v?.toLowerCase().includes(q)))
      ) as unknown as Array<Record<string, unknown>>;
    }

    // Sort
    list.sort((a, b) => {
      let valA = a[sortBy];
      let valB = b[sortBy];
      if (valA == null) valA = "";
      if (valB == null) valB = "";
      if (typeof valA === "string") {
        const cmp = (valA as string).localeCompare(String(valB));
        return sortOrder === "asc" ? cmp : -cmp;
      }
      const cmp = (valA as number) > (valB as number) ? 1 : -1;
      return sortOrder === "asc" ? cmp : -cmp;
    });

    return list;
  }, [
    selectedResource,
    equipmentList,
    workOrdersList,
    serviceRequestsList,
    personsList,
    itemsList,
    laborList,
    query,
    statusFilter,
    typeFilter,
    unitFilter,
    classFilter,
    priorityFilter,
    quickFilter,
    workSiteFilter,
    assignedFilter,
    orgFilter,
    sortBy,
    sortOrder,
  ]);

  // Pagination calculation
  const totalRows = currentDataset.length;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  const pageSafe = Math.min(Math.max(1, currentPage), totalPages);
  const startIdx = (pageSafe - 1) * pageSize;
  const paginatedRows = currentDataset.slice(startIdx, startIdx + pageSize);

  const toggleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const isFiltered =
    Boolean(query) ||
    statusFilter !== "ALL" ||
    typeFilter !== "ALL" ||
    unitFilter !== "ALL" ||
    classFilter !== "ALL" ||
    priorityFilter !== "ALL" ||
    quickFilter !== "ALL" ||
    workSiteFilter !== "ALL" ||
    assignedFilter !== "ALL" ||
    orgFilter !== "ALL";

  const handleResetFilters = () => {
    setQuery("");
    setStatusFilter("ALL");
    setTypeFilter("ALL");
    setUnitFilter("ALL");
    setClassFilter("ALL");
    setPriorityFilter("ALL");
    setQuickFilter("ALL");
    setWorkSiteFilter("ALL");
    setAssignedFilter("ALL");
    setOrgFilter("ALL");
  };

  const activeResObj = resources.find((r) => r.key === selectedResource)!;

  return (
    <>
      {/* Hero */}
      <section className="hero">
        <div>
          <p className="eyebrow">SOURCE SYSTEM / MAXIMO OSLC</p>
          <h1>BSR Collection Room</h1>
          <p className="lede">
            Pusat sinkronisasi dan penjelajah data transaksi Maximo lokal (Postgres) dengan live state monitoring & filter kaya.
          </p>
        </div>
        <div className="hero-meta">
          <span className="scope-chip">
            SITE <b>BSR</b>
          </span>
          <span className="scope-chip">
            ORG <b>IP</b>
          </span>
          <span className="verified">● verified source</span>
        </div>
      </section>

      {/* Collector Status Bar & Sync Actions (like pi-collector) */}
      <CollectStatusBar onRefresh={refreshSelectedData} />

      {error && (
        <div className="alert">
          <div>
            <strong>Gagal: </strong>
            <span>{error}</span>
          </div>
          <button onClick={load}>Coba lagi</button>
        </div>
      )}

      {/* Metrics */}
      <section className="metrics">
        <div
          className={`metric primary clickable ${selectedResource === "equipment" ? "active" : ""}`}
          onClick={() => handleSelectResource("equipment")}
          title="Klik untuk membuka data Equipment"
        >
          <span>Total Equipment (Klik untuk Buka)</span>
          <strong>{stats?.resources.equipment ?? equipmentList.length ?? "—"}</strong>
          <small>preferred source: MXAPIASSET ↗</small>
        </div>

        <div
          className={`metric clickable ${selectedResource === "work_order" ? "active" : ""}`}
          onClick={() => handleSelectResource("work_order")}
          title="Klik untuk membuka Work Orders"
        >
          <span>Total Work Orders (Klik untuk Buka)</span>
          <strong>{stats?.resources.work_order ?? workOrdersList.length ?? "—"}</strong>
          <small>MXWODETAIL ↗</small>
        </div>

        <div
          className={`metric clickable ${selectedResource === "service_request" ? "active" : ""}`}
          onClick={() => handleSelectResource("service_request")}
          title="Klik untuk membuka Service Requests"
        >
          <span>Total Service Requests</span>
          <strong>{stats?.resources.service_request ?? serviceRequestsList.length ?? "—"}</strong>
          <small>MXAPISR ↗</small>
        </div>

        <div className="metric">
          <span>Safety Boundary</span>
          <strong className="green">GET Only</strong>
          <small>Maximo business data</small>
        </div>
      </section>

      {/* Workspace Grid */}
      <section className="workspace-grid">
        {/* Verified Maximo Objects Panel */}
        <div className="panel">
          <div className="panel-head">
            <div>
              <p className="eyebrow">COLLECTION CATALOG</p>
              <h2>Verified Maximo Objects</h2>
            </div>
            <span className="count-pill">{resources.length} objects</span>
          </div>

          <div className="resource-list">
            {resources.map(({ key, label, object }) => {
              const rowCount = status[object]?.rows ?? stats?.resources[key] ?? 0;
              const isSelected = selectedResource === key;
              return (
                <div
                  className={`resource-row ${isSelected ? "active" : ""}`}
                  key={key}
                  onClick={() => handleSelectResource(key)}
                  title={`Klik untuk melihat tabel ${label} dengan paginasi & link detail`}
                >
                  <div className="resource-icon">{label.slice(0, 1)}</div>
                  <div className="resource-name">
                    <strong>
                      {label} {isSelected && <span style={{ color: "var(--cyan)", fontSize: "0.8rem" }}>● aktif</span>}
                    </strong>
                    <code>{object}</code>
                  </div>
                  <div className="resource-count">
                    {rowCount.toLocaleString()}
                    <small>records</small>
                  </div>
                  <div className="resource-actions">
                    <button
                      className="ghost-button"
                      disabled={!!syncing}
                      onClick={(e) => handleSync(object, e)}
                    >
                      {syncing === object ? "syncing…" : "sync"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="panel-note">
            <span className="dot" /> <strong>Tips:</strong> Klik objek di atas untuk melihat tabel data. Setiap baris record (Equipment, Work Order, Service Request) dapat diklik untuk membuka halaman detail spesifikasinya.
          </div>
        </div>

        {/* Observability Runs Panel */}
        <div className="panel runs-panel">
          <div className="panel-head">
            <div>
              <p className="eyebrow">OBSERVABILITY</p>
              <h2>Recent Sync Runs</h2>
            </div>
            <button className="icon-button" onClick={load} aria-label="Refresh Data">
              ↻ Refresh
            </button>
          </div>

          {runs.length === 0 ? (
            <div className="empty">Belum ada collection run tercatat.</div>
          ) : (
            <div className="run-list">
              {runs.slice(0, 6).map((run) => (
                <div className="run-row" key={run.id}>
                  <span className={`run-state ${run.skipped ? "warn" : "ok"}`}>
                    {run.skipped ? "!" : "✓"}
                  </span>
                  <div>
                    <strong>{run.object_structure}</strong>
                    <small>
                      {run.mode} · {timeAgo(run.finished_at || run.started_at)}
                    </small>
                  </div>
                  <b>
                    +{run.upserted}
                    <small> upserted</small>
                  </b>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Main Data Section (Selected Resource with Multi-Dimensional Filters) */}
      <section className="panel data-panel" ref={dataSectionRef}>
        <div className="panel-head">
          <div>
            <p className="eyebrow">LOCAL POSTGRES STORE · {activeResObj.object.toUpperCase()}</p>
            <h2>
              {activeResObj.label} Explorer
              <span className="count-pill" style={{ marginLeft: 10 }}>
                {totalRows.toLocaleString()} baris ditemukan
              </span>
            </h2>
          </div>

          <div style={{ display: "flex", gap: 8 }}>
            {selectedResource === "equipment" && (
              <Link href="/equipment" className="btn btn-ghost" style={{ fontSize: "0.75rem" }}>
                Buka Dedicated Equipment Explorer ↗
              </Link>
            )}
            {selectedResource === "work_order" && (
              <Link href="/work-orders" className="btn btn-ghost" style={{ fontSize: "0.75rem" }}>
                Buka Dedicated Work Orders Explorer ↗
              </Link>
            )}
            {selectedResource === "service_request" && (
              <Link href="/service-requests" className="btn btn-ghost" style={{ fontSize: "0.75rem" }}>
                Buka Dedicated Service Requests Explorer ↗
              </Link>
            )}
          </div>
        </div>

        {/* Quick Filter Chips (for Equipment / WO / SR) */}
        {selectedResource === "equipment" && (
          <div className="quick-chips-wrapper">
            <span style={{ fontSize: "11px", color: "var(--text-dim)", fontWeight: 700, textTransform: "uppercase", marginRight: 4 }}>
              Quick Filter:
            </span>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "ALL" ? "active" : ""}`}
              onClick={() => setQuickFilter("ALL")}
            >
              Semua
            </button>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "RUNNING" ? "active" : ""}`}
              onClick={() => setQuickFilter(quickFilter === "RUNNING" ? "ALL" : "RUNNING")}
            >
              ⚡ Running (Operating)
            </button>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "HIGH_PRIORITY" ? "active" : ""}`}
              onClick={() => setQuickFilter(quickFilter === "HIGH_PRIORITY" ? "ALL" : "HIGH_PRIORITY")}
            >
              ★ Prioritas Tinggi (P1/P2)
            </button>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "WITH_VENDOR" ? "active" : ""}`}
              onClick={() => setQuickFilter(quickFilter === "WITH_VENDOR" ? "ALL" : "WITH_VENDOR")}
            >
              🏷️ Terdata Vendor
            </button>
          </div>
        )}

        {selectedResource === "work_order" && (
          <div className="quick-chips-wrapper">
            <span style={{ fontSize: "11px", color: "var(--text-dim)", fontWeight: 700, textTransform: "uppercase", marginRight: 4 }}>
              Quick Filter:
            </span>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "ALL" ? "active" : ""}`}
              onClick={() => setQuickFilter("ALL")}
            >
              Semua
            </button>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "EMERGENCY" ? "active" : ""}`}
              onClick={() => setQuickFilter(quickFilter === "EMERGENCY" ? "ALL" : "EMERGENCY")}
            >
              🔴 Emergency / CM
            </button>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "PREVENTIVE" ? "active" : ""}`}
              onClick={() => setQuickFilter(quickFilter === "PREVENTIVE" ? "ALL" : "PREVENTIVE")}
            >
              🛠️ Preventive (PM)
            </button>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "DOWNTIME" ? "active" : ""}`}
              onClick={() => setQuickFilter(quickFilter === "DOWNTIME" ? "ALL" : "DOWNTIME")}
            >
              ⏱️ Ada Downtime
            </button>
          </div>
        )}

        {selectedResource === "service_request" && (
          <div className="quick-chips-wrapper">
            <span style={{ fontSize: "11px", color: "var(--text-dim)", fontWeight: 700, textTransform: "uppercase", marginRight: 4 }}>
              Quick Filter:
            </span>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "ALL" ? "active" : ""}`}
              onClick={() => setQuickFilter("ALL")}
            >
              Semua
            </button>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "HIGH_PRIORITY" ? "active" : ""}`}
              onClick={() => setQuickFilter(quickFilter === "HIGH_PRIORITY" ? "ALL" : "HIGH_PRIORITY")}
            >
              🚨 Prioritas Tinggi (P1/P2)
            </button>
            <button
              type="button"
              className={`quick-chip ${quickFilter === "HAS_RISK" ? "active" : ""}`}
              onClick={() => setQuickFilter(quickFilter === "HAS_RISK" ? "ALL" : "HAS_RISK")}
            >
              ⚠️ Area Risiko Teridentifikasi
            </button>
          </div>
        )}

        {/* Toolbar & Filters */}
        <div className="table-tools-bar">
          <div className="table-filters">
            <input
              className="search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={`Cari di ${activeResObj.label.toLowerCase()}...`}
            />

            {currentStatusOptions.length > 0 && (
              <select
                className="select-filter"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">Semua Status ({currentStatusOptions.length})</option>
                {currentStatusOptions.map((st) => (
                  <option key={st} value={st}>
                    Status: {st}
                  </option>
                ))}
              </select>
            )}

            {currentTypeOptions.length > 0 && (
              <select className="select-filter" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                <option value="ALL">Semua Type ({currentTypeOptions.length})</option>
                {currentTypeOptions.map((type) => <option key={type} value={type}>Type: {type}</option>)}
              </select>
            )}

            {currentUnitOptions.length > 0 && (
              <select className="select-filter" value={unitFilter} onChange={(e) => setUnitFilter(e.target.value)}>
                <option value="ALL">Semua Unit ({currentUnitOptions.length})</option>
                {currentUnitOptions.map((unit) => <option key={unit} value={unit}>Unit: {unit}</option>)}
              </select>
            )}

            {currentClassOptions.length > 0 && (
              <select className="select-filter" value={classFilter} onChange={(e) => setClassFilter(e.target.value)}>
                <option value="ALL">Semua Class ({currentClassOptions.length})</option>
                {currentClassOptions.map((c) => <option key={c} value={c}>Class: {c}</option>)}
              </select>
            )}

            {currentPriorityOptions.length > 0 && (
              <select className="select-filter" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
                <option value="ALL">Semua Prioritas</option>
                {currentPriorityOptions.map((p) => <option key={p} value={p}>Pri: {p}</option>)}
              </select>
            )}

            {currentOrgOptions.length > 0 && (
              <select className="select-filter" value={orgFilter} onChange={(e) => setOrgFilter(e.target.value)}>
                <option value="ALL">Semua Organisasi</option>
                {currentOrgOptions.map((org) => <option key={org} value={org}>{org}</option>)}
              </select>
            )}

            {currentWorkSiteOptions.length > 0 && (
              <select className="select-filter" value={workSiteFilter} onChange={(e) => setWorkSiteFilter(e.target.value)}>
                <option value="ALL">Semua Worksite</option>
                {currentWorkSiteOptions.map((site) => <option key={site} value={site}>{site}</option>)}
              </select>
            )}

            {selectedResource === "labor" && (
              <select className="select-filter" value={assignedFilter} onChange={(e) => setAssignedFilter(e.target.value)}>
                <option value="ALL">Assignment: Semua</option>
                <option value="true">Assigned</option>
                <option value="false">Unassigned</option>
              </select>
            )}

            {isFiltered && (
              <button
                type="button"
                className="btn btn-ghost"
                onClick={handleResetFilters}
              >
                ✕ Reset Filter
              </button>
            )}
          </div>

          <div className="page-size-selector">
            <span>Per halaman:</span>
            <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {/* Table Content */}
        {loading ? (
          <div className="empty">Memuat data dari local Postgres store...</div>
        ) : (
          <div className="table-scroll">
            {selectedResource === "equipment" && (
              <table>
                <thead>
                  <tr>
                    <th className="sortable" onClick={() => toggleSort("id")}>
                      Asset ID {sortBy === "id" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("name")}>
                      Description / Name {sortBy === "name" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("unit")}>
                      Unit / Class {sortBy === "unit" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("location_id")}>
                      Location {sortBy === "location_id" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("status")}>
                      Status {sortBy === "status" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("priority")}>
                      Pri {sortBy === "priority" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th>Manufacturer / Vendor</th>
                    <th className="sortable" onClick={() => toggleSort("source_changed_at")}>
                      Changed {sortBy === "source_changed_at" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th style={{ textAlign: "right" }}>Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {(paginatedRows as unknown as EquipmentView[]).map((row) => (
                    <tr key={row.id}>
                      <td>
                        <Link href={`/equipment/${encodeURIComponent(row.id)}`} className="asset-link">
                          <b>{row.id}</b>
                        </Link>
                      </td>
                      <td>
                        <div style={{ maxWidth: 300, fontWeight: 600 }}>{row.name || "No description"}</div>
                      </td>
                      <td>
                        <span>{row.unit || "—"}</span>
                        {row.equipment_class && (
                          <small style={{ display: "block", color: "var(--text-muted)", fontSize: "11px" }}>
                            {row.equipment_class}
                          </small>
                        )}
                      </td>
                      <td className="mono">{row.location_id || "—"}</td>
                      <td>
                        <span className={`status ${row.status?.toLowerCase() === "operating" ? "good" : ""}`}>
                          {row.status || "—"}
                        </span>
                      </td>
                      <td>{row.priority != null ? <span className="count-pill">P{row.priority}</span> : "—"}</td>
                      <td>{row.manufacturer || row.vendor || "—"}</td>
                      <td className="mono" style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                        {timeAgo(row.source_changed_at)}
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <Link
                          href={`/equipment/${encodeURIComponent(row.id)}`}
                          className="btn btn-ghost"
                          style={{ padding: "3px 8px", fontSize: "0.75rem" }}
                        >
                          Detail ↗
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {selectedResource === "work_order" && (
              <table>
                <thead>
                  <tr>
                    <th className="sortable" onClick={() => toggleSort("id")}>
                      WO # {sortBy === "id" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("equipment_id")}>
                      Equipment {sortBy === "equipment_id" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("work_type")}>
                      Work Type {sortBy === "work_type" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("status")}>
                      Status {sortBy === "status" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("priority")}>
                      Pri {sortBy === "priority" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th>Description</th>
                    <th className="sortable" onClick={() => toggleSort("downtime_hours")}>
                      Downtime {sortBy === "downtime_hours" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("source_changed_at")}>
                      Changed {sortBy === "source_changed_at" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th style={{ textAlign: "right" }}>Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {(paginatedRows as unknown as WorkOrderView[]).map((row) => (
                    <tr key={row.id}>
                      <td>
                        <Link href={`/work-orders/${encodeURIComponent(row.id)}`} className="asset-link">
                          <b>{row.id}</b>
                        </Link>
                      </td>
                      <td>
                        {row.equipment_id ? (
                          <Link href={`/equipment/${encodeURIComponent(row.equipment_id)}`} className="asset-link">
                            <b>{row.equipment_id} ↗</b>
                          </Link>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        <span className="count-pill">{row.work_type || "—"}</span>
                      </td>
                      <td>
                        <span className="status">{row.status || "—"}</span>
                      </td>
                      <td>{row.priority ? <span className="count-pill">{row.priority}</span> : "—"}</td>
                      <td>
                        <div style={{ maxWidth: 280 }}>{row.description || "—"}</div>
                      </td>
                      <td>
                        {row.downtime_hours != null && row.downtime_hours > 0 ? (
                          <span className="mono" style={{ color: "var(--amber)", fontWeight: 600 }}>
                            {row.downtime_hours} jam
                          </span>
                        ) : (
                          <span style={{ color: "var(--text-dim)" }}>0</span>
                        )}
                      </td>
                      <td className="mono">{timeAgo(row.source_changed_at)}</td>
                      <td style={{ textAlign: "right" }}>
                        <Link
                          href={`/work-orders/${encodeURIComponent(row.id)}`}
                          className="btn btn-ghost"
                          style={{ padding: "3px 8px", fontSize: "0.75rem" }}
                        >
                          Detail ↗
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {selectedResource === "service_request" && (
              <table>
                <thead>
                  <tr>
                    <th className="sortable" onClick={() => toggleSort("id")}>
                      SR # {sortBy === "id" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("equipment_id")}>
                      Equipment {sortBy === "equipment_id" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("status")}>
                      Status {sortBy === "status" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("reported_priority")}>
                      Pri {sortBy === "reported_priority" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th>Description</th>
                    <th className="sortable" onClick={() => toggleSort("reported_by")}>
                      Reported By {sortBy === "reported_by" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th className="sortable" onClick={() => toggleSort("source_changed_at")}>
                      Changed {sortBy === "source_changed_at" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th style={{ textAlign: "right" }}>Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {(paginatedRows as unknown as ServiceRequestView[]).map((row) => (
                    <tr key={row.id}>
                      <td>
                        <Link href={`/service-requests/${encodeURIComponent(row.id)}`} className="asset-link">
                          <b>{row.id}</b>
                        </Link>
                      </td>
                      <td>
                        {row.equipment_id ? (
                          <Link href={`/equipment/${encodeURIComponent(row.equipment_id)}`} className="asset-link">
                            <b>{row.equipment_id} ↗</b>
                          </Link>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        <span className="status">{row.status || "—"}</span>
                      </td>
                      <td>
                        {row.reported_priority ? (
                          <span className="count-pill">P{row.reported_priority}</span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        <div style={{ maxWidth: 280 }}>{row.description || "—"}</div>
                      </td>
                      <td>
                        <small style={{ color: "var(--text)", fontWeight: 600 }}>{row.reported_by_name || row.reported_by || "—"}</small>
                      </td>
                      <td className="mono">{timeAgo(row.source_changed_at)}</td>
                      <td style={{ textAlign: "right" }}>
                        <Link
                          href={`/service-requests/${encodeURIComponent(row.id)}`}
                          className="btn btn-ghost"
                          style={{ padding: "3px 8px", fontSize: "0.75rem" }}
                        >
                          Detail ↗
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {["person", "item", "labor"].includes(selectedResource) && (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>{selectedResource === "person" ? "Display Name" : selectedResource === "item" ? "Item Description" : "Person ID"}</th>
                    <th>{selectedResource === "person" ? "Organization" : selectedResource === "item" ? "Item Type / Unit" : "Worksite"}</th>
                    <th>Status</th>
                    {selectedResource === "labor" && <th>Assigned</th>}
                  </tr>
                </thead>
                <tbody>
                  {(paginatedRows as unknown as GenericView[]).map((row) => (
                    <tr key={row.id}>
                      <td className="mono">
                        <b>{row.id}</b>
                      </td>
                      <td>{selectedResource === "person" ? row.display_name || "—" : selectedResource === "item" ? row.description || "—" : row.person_id || "—"}</td>
                      <td>
                        {selectedResource === "person" && (row.location_org || "—")}
                        {selectedResource === "item" && `${row.item_type || "—"} / ${row.issue_unit || "—"}`}
                        {selectedResource === "labor" && (row.work_site || "—")}
                      </td>
                      <td>
                        <span className="status">{row.status || "—"}</span>
                      </td>
                      {selectedResource === "labor" && <td>{row.is_assigned ? "Yes" : "No"}</td>}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {paginatedRows.length === 0 && (
              <div className="empty">
                {(["person", "item", "labor"].includes(selectedResource) &&
                  (selectedResource === "person" ? personsList.length : selectedResource === "item" ? itemsList.length : laborList.length) === 0)
                  ? `Belum ada baseline data ${activeResObj.label}. Klik sync pada object ${activeResObj.object}; untuk Items, jalankan diagnose master-data bila hasil tetap 0.`
                  : "Tidak ada data yang cocok dengan kriteria filter saat ini."}
              </div>
            )}
          </div>
        )}

        {/* Pagination Bar */}
        <div className="pagination-bar">
          <div className="pagination-info">
            Menampilkan <strong>{totalRows === 0 ? 0 : startIdx + 1}</strong> –{" "}
            <strong>{Math.min(startIdx + pageSize, totalRows)}</strong> dari{" "}
            <strong>{totalRows.toLocaleString()}</strong> data
          </div>

          <div className="pagination-controls">
            <button
              type="button"
              className="page-btn"
              disabled={pageSafe <= 1}
              onClick={() => setCurrentPage(1)}
              title="Halaman Pertama"
            >
              «
            </button>
            <button
              type="button"
              className="page-btn"
              disabled={pageSafe <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              title="Halaman Sebelumnya"
            >
              ‹
            </button>

            {/* Dynamic Page Buttons */}
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(
                (p) =>
                  p === 1 ||
                  p === totalPages ||
                  (p >= pageSafe - 2 && p <= pageSafe + 2)
              )
              .map((p, idx, arr) => {
                const prev = arr[idx - 1];
                return (
                  <span key={p} style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                    {prev && p - prev > 1 && <span style={{ color: "var(--text-dim)", padding: "0 4px" }}>…</span>}
                    <button
                      type="button"
                      className={`page-btn ${pageSafe === p ? "active" : ""}`}
                      onClick={() => setCurrentPage(p)}
                    >
                      {p}
                    </button>
                  </span>
                );
              })}

            <button
              type="button"
              className="page-btn"
              disabled={pageSafe >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              title="Halaman Berikutnya"
            >
              ›
            </button>
            <button
              type="button"
              className="page-btn"
              disabled={pageSafe >= totalPages}
              onClick={() => setCurrentPage(totalPages)}
              title="Halaman Terakhir"
            >
              »
            </button>
          </div>
        </div>
      </section>
    </>
  );
}
