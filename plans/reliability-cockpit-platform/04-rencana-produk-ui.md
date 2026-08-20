# 04 — Rencana Produk dan UI Reliability Cockpit

## Arah produk

Lima konsep menggambarkan satu alur keputusan:

```text
Executive Overview
       │ memilih risiko/aset
       ▼
Asset Health Detail ──▶ PdM Finding ──▶ Recommendation ──▶ Action/Decision
       ▲                                                        │
       └──────────────── status WO/hasil pekerjaan ─────────────┘
```

Fokus implementasi bukan menyalin screenshot secara statis, melainkan membangun
design system dan alur data yang menghasilkan komposisi serupa dari data nyata.

## Information architecture

| Navigation | Route awal | Tujuan |
|---|---|---|
| Executive Overview | `/` atau `/overview` | ringkasan reliability dan attention |
| Asset Health | `/assets`, `/assets/[id]` | portfolio dan detail asset |
| PdM Center | `/pdm` | condition monitoring, trend, findings |
| Recommendations | `/recommendations`, `/recommendations/[id]` | lifecycle action teknis |
| Action Board | `/actions` | keputusan management |
| Reports | `/reports` | dataset/print/export terkontrol |
| System Integration | `/integrations` | source health, freshness, coverage |
| Administration | `/admin` | taxonomy, thresholds, mappings, users/roles |

Work Orders tetap dapat diakses dari detail asset/recommendation dan route pendukung
`/work-orders`, tetapi bukan navigasi utama seperti starter saat ini.

## Application shell dan design system

Elemen konsisten dari seluruh konsep:

- sidebar gelap dengan logo, icon + label, active state hijau, collapse state;
- top bar berisi menu mobile, notification, user/role, dan timestamp freshness;
- background netral terang, card putih, border/shadow lembut;
- semantic colors: green healthy/closed, amber warning/open, red critical/overdue,
  blue informational/in-progress;
- typography yang padat tetapi terbaca untuk dashboard operasional;
- filter bar, stat card, chart card, table card, badge, pagination, empty/error state;
- semua warna menjadi design token dan tidak menjadi satu-satunya penanda status.

Komponen reusable yang perlu dibuat:

```text
AppShell, Sidebar, TopBar, PageHeader, FreshnessBadge
FilterBar, DateRangePicker, SearchField, SelectFilter
MetricCard, SeverityBadge, StatusBadge, RiskBadge
ChartCard, DonutChart, TrendChart, StackedBarChart, Sparkline
DataTable, SortHeader, Pagination, EmptyState, ErrorState, Skeleton
AssetLink, WorkOrderLink, PersonChip, SourceHealthCard
DecisionCard, RecommendationTimeline, DataQualityNotice
```

Library proposal: icon set tunggal, chart library React yang accessibility-friendly,
TanStack Table untuk server-side table state, dan query/cache library untuk request.
Pilihan library dikunci pada spike awal dan harus kompatibel dengan Next.js 15/React
19. Jangan menambahkan component framework besar sebelum token/layout diuji.

## 1. Executive Overview

Acuan: [konsep5.png](../../konsep5.png).

### Tujuan

Menjawab dalam satu layar: kondisi portfolio, perubahan trend, risiko terbesar, dan
hal yang perlu perhatian management.

### Isi

- filter plant/site, unit, date range, dan global search;
- cards: Healthy, Warning, Critical assets; Critical Findings Open; Overdue
  Recommendations; WO Backlog;
- Asset Health Summary donut;
- Top Asset Risk table;
- Management Attention Required list;
- Reliability Trend + WO count.

### Sumber data

- health/risk snapshots dari cockpit derived service;
- WO backlog/status/count dari Maximo projection;
- finding/recommendation/action dari workflow cockpit;
- reliability KPI trend dari versioned KPI projection;
- `as_of` memakai freshness minimum dari input yang dipakai, bukan jam browser.

### Interaksi

Klik metric/filter menavigasi ke list dengan query yang sama. Klik asset membuka
detail. Attention item membuka Action Board yang sudah difilter. Date range harus
dipakai backend, bukan hanya mengubah label.

## 2. Asset Health

Acuan detail: [konsep4.png](../../konsep4.png).

### Portfolio `/assets`

Tambahkan halaman list sebelum detail:

- health score/category, criticality, asset status, unit/location;
- open/overdue WO, open findings, overdue recommendations;
- last condition update dan data completeness;
- server-side search/filter/sort/pagination.

### Detail `/assets/[id]`

- header identity + service status;
- cards: Health Score, Criticality, Last Failure, Open WO, Overdue Recommendation;
- asset details dari Maximo;
- PdM Condition Summary per method dengan finding, last update, trend;
- WO Summary stacked chart;
- Recommendations/Actions table;
- link ke full PdM history, WO, dan recommendations;
- expandable "Why this score?" untuk breakdown/provenance.

Jika asset belum mempunyai PI link verified, panel PdM menampilkan coverage gap dan
aksi administrasi mapping—bukan angka nol/healthy.

## 3. PdM Center

Acuan: [konsep3.png](../../konsep3.png).

### Isi

- metrics: monitored assets, assets with findings, active methods, healthy/normal
  findings, overdue inspections;
- method tabs: All, Vibration, IR Thermography, MCSA, Tribology, DGA, dan method
  tambahan yang memang tersedia;
- severity distribution;
- trend normal/alert/high atau scale yang disepakati;
- latest findings table dengan asset, location, severity, update, finding, trend,
  recommendation, status;
- time range dan filters.

### Aturan data

- Tab method hanya muncul bila taxonomy/mapping ada; jangan mengubah kategori PI
  menjadi method dengan substring heuristic pada runtime.
- ISO 10816/20816 hanya ditampilkan bila equipment class, measurement type, unit,
  operating condition, dan threshold telah dimodelkan benar.
- CEMS tidak dimasukkan ke Vibration/PdM. Bila digunakan, buat tab
  Environmental/Emissions atau tampilkan pada Executive/Integration sesuai mapping.
- Setiap trend punya unit, timezone, sampling/aggregation, quality, dan data gap.
- `value_good=false`, stale, dan insufficient samples tidak boleh menjadi Normal.

## 4. Recommendations

Acuan: [konsep2.png](../../konsep2.png).

### Isi

- status tabs/count: All, Overdue, Open, In Progress, Closed;
- search + advanced filter drawer;
- table: ID, Asset, Method, Finding, Recommendation, Risk Impact, Target Completion,
  Status, WO Reference, PIC, menu action;
- recommendation detail/drawer dengan evidence, score/risk breakdown, history,
  attachments/link, dan transition controls;
- server-side pagination dan sort.

### Workflow dan izin

- Viewer hanya membaca;
- Reliability Engineer membuat/mengedit recommendation dan menghubungkan finding;
- Assignee mengubah progress sesuai rule;
- Manager menyetujui decision/risk acceptance;
- Admin mengelola taxonomy/configuration, bukan mengubah bukti source.

WO Reference adalah link ke WO yang sudah dikoleksi. Tidak ada tombol "Create WO in
Maximo" pada scope read-only ini.

## 5. Action Board

Acuan: [konsep1.png](../../konsep1.png).

### Isi

- empat attention cards: Maintenance Window, Budget Decision, Repeat Failure/RCA,
  Risk Acceptance;
- Top Asset Risk (rolling period);
- Critical Findings Open;
- decision list/detail dengan owner, due date, evidence, comment/audit timeline;
- filter site/unit/date/status/owner.

### Aturan

- Count card berasal dari query rule yang sama dengan detail list agar tidak berbeda;
- setiap card menampilkan definisi dan cutoff date;
- Repeat Failure mempunyai rule/version/window yang dapat diaudit;
- Budget/acceptance adalah data workflow cockpit, bukan inferred hanya dari cost;
- keputusan tidak mengubah source system.

## Halaman pendukung

### Reports

- daftar report versioned: executive reliability, asset health, PdM findings,
  recommendation ageing, WO backlog, source quality, environmental/CEMS;
- filter dan snapshot `as_of` yang sama dengan layar;
- CSV untuk data tabular dan PDF/print view untuk ringkasan;
- export merekam actor, filter, waktu, dan model version;
- large export dijalankan background dan mempunyai retention.

### System Integration

- satu card per Maximo/PI/CEMS/cockpit worker/API/DB;
- state healthy/degraded/down/stale;
- last success/attempt, next run, duration, watermark, rows/errors, lag;
- registry coverage: Maximo verified object, PI verified/active/gone/error, CEMS
  documented/verified/collect-enabled;
- read-only badge dan safety guard summary;
- recent runs table dan sanitized error detail;
- tombol manual run hanya untuk role tepat, internal API, lock-protected, dan tidak
  mengizinkan bypass safety.

### Administration

- verified asset-source links dan unmapped coverage;
- measurement method taxonomy;
- health/risk model version dan approval state;
- threshold/rule configuration dengan maker-checker/audit;
- recommendation types/status policy;
- user/role management bila identity provider terintegrasi;
- tidak ada editor WebId/register mentah di cockpit; perubahan source knowledge tetap
  melalui knowledge repository dan proses verifikasi.

## Frontend data architecture

- Next.js tetap menjadi browser-facing layer dan proxy ke cockpit API;
- browser tidak memanggil collector API langsung;
- URL menyimpan filter/sort/page agar deep-link dan back/forward berfungsi;
- dashboard summary diambil dari endpoint agregat, bukan N+1 call per card/asset;
- detail chart memakai server-side range/aggregation query;
- query key mencakup filter dan `as_of`;
- refetch interval mengikuti freshness source, dengan pause ketika tab tidak aktif;
- mutation memakai CSRF/session protection sesuai auth design;
- optimistic update hanya pada workflow cockpit yang reversible, bukan source data.

## State wajib untuk setiap widget

| State | Perilaku |
|---|---|
| Loading | skeleton mempertahankan layout |
| Empty valid | pesan spesifik dan filter reset |
| Not configured | jelaskan mapping/rule yang belum tersedia |
| Stale | tampilkan last successful timestamp dan warning |
| Partial | tampilkan coverage dan komponen yang hilang |
| Error | retry bounded + correlation ID, tanpa credential/raw payload |
| Forbidden | jelaskan role/access, tidak menyamar sebagai empty |

## Responsive dan accessibility

- Desktop konsep menjadi target utama, tetapi tablet/mobile tetap usable;
- sidebar collapse menjadi drawer; table berubah ke horizontal scroll atau card list
  terpilih, bukan mengecilkan teks;
- keyboard navigation, visible focus, semantic heading/table, skip link;
- WCAG AA contrast; icon/status selalu disertai label/text;
- chart memiliki summary/table alternatif dan tidak bergantung warna saja;
- tap target minimum, reduced motion, locale number/date, timezone WIB yang eksplisit;
- nilai kosong memakai `—` + tooltip sebab, bukan `0`.

## Performance budget awal

- initial route tidak menarik raw series;
- dashboard API p95 target staging ditentukan setelah data seed, baseline awal <2 s;
- interaction/filter cached <500 ms bila read model tersedia;
- table page default 25–50 row;
- chart default memakai agregat dan jumlah point bounded;
- bundle dipantau per route; chart code lazy-loaded bila tidak above-the-fold;
- virtualize hanya saat benar-benar dibutuhkan; server pagination tetap utama.

## Urutan pengerjaan UI

1. Design tokens + AppShell + common states.
2. System Integration terlebih dahulu untuk membuktikan data platform/freshness.
3. Asset portfolio/detail dengan Maximo data nyata.
4. Executive Overview dengan KPI/WO yang sudah nyata; widget belum tersedia diberi
   explicit not-configured state.
5. PdM Center setelah identity/method/rule siap.
6. Recommendations setelah domain + RBAC + audit siap.
7. Action Board setelah decision rules/workflow siap.
8. Reports dan Administration.

Urutan ini mencegah halaman terlihat lengkap secara visual tetapi sebenarnya berisi
angka dummy tanpa provenance.

## Status eksekusi — 20 Agustus 2026

| Status | Butir | Keterangan |
|---|---|---|
| DONE | Urutan dan guard produk | Rencana mengunci bahwa layar konsep hanya boleh memakai source/derived/workflow/not-configured state; tidak ada metric bisnis hardcoded yang ditambahkan. |
| PARTIAL | Landasan UI | API Cockpit saat ini masih menyediakan equipment, work order, KPI, dan sync status; konsep visual belum dapat dipetakan penuh tanpa read model/API domain yang direncanakan. |
| BLOCKED | UI-001 s.d. UI-107 | Tidak dieksekusi sebelum endpoint agregat, identity verified, formula/rule version, AuthZ, serta data freshness tersedia. Mengimplementasikan lima layar sekarang akan menghasilkan data contoh yang menyesatkan. |
