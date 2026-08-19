# User Guide — Reliability Knowledge Stack

Panduan praktis untuk menjalankan dan menguji 3 project: **maximo-knowledge**,
**reliability-data-contracts**, dan **reliability-cockpit**.

> `pi-knowledge` belum diintegrasikan (PI adapter masih placeholder) dan tidak
> dibahas di sini.

---

## Daftar Isi

1. [Arsitektur & Alur Data](#1-arsitektur--alur-data)
2. [Prasyarat](#2-prasyarat)
3. [Cheat Sheet (ringkas)](#3-cheat-sheet-ringkas)
4. [Project 1: maximo-knowledge](#4-project-1-maximo-knowledge)
5. [Project 2: reliability-data-contracts](#5-project-2-reliability-data-contracts)
6. [Project 3: reliability-cockpit](#6-project-3-reliability-cockpit)
7. [Skenario End-to-End](#7-skenario-end-to-end)
8. [Checklist Verifikasi](#8-checklist-verifikasi)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Arsitektur & Alur Data

```
maximo-knowledge          reliability-data-contracts         reliability-cockpit
(SOURCE OF TRUTH)    →     (VENDOR-NEUTRAL LAYER)      →     (CONSUMER APP)

Menemukan & memverifikasi   Menerjemahkan field Maximo        Sync data Maximo
API Maximo (read-only).     ke kontrak snake_case yang         ke DB lokal (Postgres),
Hasilnya: catalog OSLC      vendor-neutral.                   sajikan via REST API
462 object structure, 7     Hasilnya: 12 JSON Schema          + web UI Next.js.
diverifikasi, 6 forbidden.  + mapping table.
```

**Aturan arsitektur:**
- Cockpit **tidak pernah** rediscover Maximo — selalu baca dari knowledge.
- Field vendor (Maximo) diisolasi di `sources.maximo` block, tidak bocor ke kontrak inti.
- Semua akses ke Maximo **GET/HEAD/OPTIONS only** (read-only enforced di code).

**Urutan setup yang benar:**
```
maximo-knowledge (discover)  →  data-contracts (validate)  →  cockpit (sync + serve)
```

---

## 2. Prasyarat

| Tool | Versi | Cek |
|---|---|---|
| Python | ≥ 3.11 | `python3 --version` |
| Node.js | ≥ 18 | `node --version` |
| PostgreSQL | ≥ 14 | `psql --version` |
| Git | any | `git --version` |

**Kredensial Maximo (read-only):**
- `MAXIMO_READ_ONLY_TOKEN` — bearer token read-only, **atau**
- `MAXIMO_SESSION_COOKIE` — session cookie dari login manual (out-of-band)

> Token/cookie **tidak boleh** di-commit. Letakkan di file `.env` masing-masing
> project (sudah di-gitignore).

---

## 3. Cheat Sheet (ringkas)

```bash
# ── maximo-knowledge ──────────────────────────────────────────
cd maximo-knowledge
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium          # untuk session discovery
cp .env.example .env                                      # isi token
.venv/bin/python -m unittest discover -s tests           # jalankan tests

# ── reliability-data-contracts ───────────────────────────────
cd reliability-data-contracts
# Validasi schema (butuh jsonschema — pakai venv maximo-knowledge):
../maximo-knowledge/.venv/bin/python -c "
import json, glob
from jsonschema import Draft202012Validator
for f in sorted(glob.glob('schemas/*.schema.json')):
    Draft202012Validator.check_schema(json.load(open(f)))
    print(f'OK: {f}')
"

# ── reliability-cockpit ──────────────────────────────────────
cd reliability-cockpit
python3 -m venv .venv && .venv/bin/pip install -e .       # install deps + command 'cockpit'
cp .env.example .env                                      # isi token + DATABASE_URL
cockpit init-db                                           # buat tabel Postgres
cockpit sync                                              # sync data Maximo (delta)
cockpit kpi                                               # hitung + simpan KPI
cockpit serve                                             # start API di :8000

# ── Web UI ───────────────────────────────────────────────────
cd reliability-cockpit/web
npm install
cp .env.example .env.local
npm run dev                                               # start web di :3000
```

---

## 4. Project 1: maximo-knowledge

### 4.1 Tujuan
Knowledge base yang memetakan API Maximo (site **BSR**, org **IP**). Menjawab
pertanyaan: *field apa saja yang tersedia, bagaimana cara membacanya dengan
aman, dan apa arti bisnisnya*.

### 4.2 Setup

```bash
cd maximo-knowledge

# Buat virtual environment
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Install browser untuk session discovery (opsional, sekali saja)
.venv/bin/python -m playwright install chromium

# Konfigurasi kredensial
cp .env.example .env
# Edit .env, isi:
#   MAXIMO_READ_ONLY_TOKEN=<token-anda>
```

### 4.3 Menjalankan Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

**Expected output:** `Ran 37 tests ... OK`

Test mencakup: OAS parsing, OSLC member extraction, sanitization, schema
validation (13 object records), CLI guards.

### 4.4 Discovery (membutuhkan akses jaringan ke Maximo)

**Opsi A — Parse OAS lokal (tanpa network):**

```bash
.venv/bin/python scripts/discover.py \
  --oas-file discovery/oslc/maximo_oas.json \
  --scope reliability-core
```

**Opsi B — Fetch OAS live (butuh token):**

```bash
.venv/bin/python scripts/discover.py \
  --fetch-oas --execute --scope reliability-core
```

**Opsi C — Enumerasi OSLC object structures (butuh token):**

```bash
.venv/bin/python scripts/discover.py \
  --enumerate-oslc --execute --scope reliability-core
```

**Opsi D — Browser session discovery (login manual):**

```bash
.venv/bin/python scripts/session_discover.py run \
  --scope reliability-core --verify-samples
```

Membuka Chromium → Anda login manual → CLI melakukan GET-only discovery.

### 4.5 Output yang dihasilkan

| Path | Isi |
|---|---|
| `discovery/objects/*.json` | 13 record per-object (7 verified, 6 forbidden) |
| `discovery/object-structures.json` | Ringkasan catalog |
| `discovery/oslc/catalog.json` | Catalog lengkap 462 object structures |
| `discovery/capabilities.json` | Kapabilitas OSLC (filter/sort/page/select) |
| `docs/objects.md` | Penjelasan bisnis tiap object |
| `docs/relationships.md` | Peta relationship antar entity |

---

## 5. Project 2: reliability-data-contracts

### 5.1 Tujuan
Kontrak data vendor-neutral yang menjadi anti-corruption layer antara aplikasi
dan sistem source (Maximo/PI). Field vendor dikarantina di `sources.*` block.

### 5.2 Struktur

```
schemas/        12 JSON Schema (Draft 2020-12)
                ├── 6 verified Maximo: equipment, work-order, service-request,
                │   person, item, labor
                ├── 1 template PI: condition-parameter
                └── 5 derived: failure, downtime, location,
                    maintenance-event, reliability-kpi
mappings/       maximo-to-contracts.md (tabel translasi field-by-field)
catalog/        2 example instance (equipment, work-order)
```

### 5.3 Validasi Schema

Project ini tidak punya venv sendiri. Gunakan venv maximo-knowledge yang sudah
ter-install `jsonschema`:

```bash
cd reliability-data-contracts
../maximo-knowledge/.venv/bin/python -c "
import json, glob
from jsonschema import Draft202012Validator
ok = True
for f in sorted(glob.glob('schemas/*.schema.json')):
    try:
        schema = json.load(open(f))
        Draft202012Validator.check_schema(schema)
        print(f'  OK  {f}')
    except Exception as e:
        print(f'  FAIL {f}: {e}')
        ok = False
print('All schemas valid!' if ok else 'ERRORS FOUND')
"
```

**Expected:** semua 12 schema `OK`.

### 5.4 Membaca Mapping

Buka `mappings/maximo-to-contracts.md` — tabel translasi field-by-field untuk
setiap object, dengan status legend:
- ✅ verified — field diverifikasi via live OSLC
- ⛔ forbidden — object tidak bisa dibaca (BMXAA0024E)
- ⊘ derived — diturunkan dari object lain

---

## 6. Project 3: reliability-cockpit

### 6.1 Tujuan
Aplikasi consumer yang sync data Maximo ke DB lokal, lalu menyajikannya via
REST API + web UI. **Tidak pernah rediscover** — selalu baca kontrak dari
data-contracts dan fakta dari maximo-knowledge.

### 6.2 Setup

```bash
cd reliability-cockpit

# Buat virtual environment + install (termasuk command 'cockpit')
python3 -m venv .venv
.venv/bin/pip install -e .

# Konfigurasi
cp .env.example .env
# Edit .env, isi:
#   MAXIMO_READ_ONLY_TOKEN=<token-anda>
#   DATABASE_URL=postgresql://cockpit:cockpit@localhost:5432/cockpit
```

### 6.3 Setup Database (Postgres)

```bash
# Buat database + user (sekali saja)
sudo -u postgres psql -c "CREATE USER cockpit WITH PASSWORD 'cockpit';"
sudo -u postgres psql -c "CREATE DATABASE cockpit OWNER cockpit;"

# Buat semua tabel (menggunakan ORM metadata.create_all)
.venv/bin/cockpit init-db
```

**Expected output:** `cockpit local tables created (Postgres)`

Tabel yang dibuat (8): `equipment`, `work_order`, `service_request`, `person`,
`item`, `labor`, `reliability_kpi`, `sync_cursor`.

### 6.4 Sync Data dari Maximo

```bash
# Sync semua object (asset, workorder, sr, person, item, labor)
.venv/bin/cockpit sync

# Atau sync object tertentu saja
.venv/bin/cockpit sync mxasset mxwodetail

# Sync ulang dengan resource name juga bisa
.venv/bin/cockpit sync equipment workorder
```

**Expected output:**
```
mxasset        mode=full       seen=150   upserted=150
mxwodetail     mode=full       seen=3200  upserted=3200
...
```

> Sync menggunakan delta-sync dengan watermark `changedate`.
> Run kedua akan otomatis `mode=incremental`.

### 6.5 Hitung KPI

```bash
# Hitung KPI 90 hari terakhir (default), semua equipment
.venv/bin/cockpit kpi

# Hitung untuk periode spesifik
.venv/bin/cockpit kpi --from 2026-01-01 --to 2026-06-30

# Hitung untuk satu equipment saja
.venv/bin/cockpit kpi --equipment "CS10CVA02GA000-001"
```

**Expected output:**
```
KPI period 2026-05-16 .. 2026-08-13: 200 computed & persisted
  AVAILABILITY        50
  MTBF                50
  MTTR                50
  PM_COMPLIANCE       50
```

### 6.6 Start API Server

```bash
.venv/bin/cockpit serve
# Atau dengan custom host/port:
.venv/bin/cockpit serve --host 0.0.0.0 --port 9000
```

API berjalan di `http://127.0.0.1:8000`. Endpoint:

| Endpoint | Method | Deskripsi |
|---|---|---|
| `/health` | GET | Health check → `{"status":"ok"}` |
| `/equipment` | GET | List equipment (`?equipment_class=&limit=`) |
| `/equipment/{id}` | GET | Detail satu equipment (PK lookup) |
| `/work-orders` | GET | List work orders (`?equipment_id=&limit=`) |
| `/kpis/{equipment_id}/{metric}` | GET | KPI terbaru (MTBF/MTTR/AVAILABILITY/PM_COMPLIANCE) |
| `/sync/status` | GET | Status sync cursor (`?object_structure=mxasset`) |

**Cek API:**
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/equipment?limit=5
curl "http://127.0.0.1:8000/kpis/CS10CVA02GA000-001/MTBF"
```

Dokumentasi interaktif: `http://127.0.0.1:8000/docs`

### 6.7 Start Web UI

```bash
# Di terminal terpisah
cd reliability-cockpit/web
npm install
cp .env.example .env.local
npm run dev
```

Web UI berjalan di `http://localhost:3000`.

**Halaman yang tersedia:**

| URL | Isi |
|---|---|
| `/` | Tabel equipment (klik ID → halaman detail) |
| `/equipment/{id}` | Detail equipment + **KPI cards** + work orders |
| `/work-orders` | Semua work orders dengan link ke equipment |

### 6.8 Menjalankan Tests

```bash
cd reliability-cockpit
.venv/bin/python -m unittest discover -s tests -v
```

**Expected:** `Ran 34 tests ... OK`

Test mencakup: mappers (6 OSLC→domain), KPI math (MTBF/MTTR/availability/PM),
KpiService orchestration, sync engine (watermark/incremental), OSLC client
(member extraction, pagination, size cap, write-method block).

---

## 7. Skenario End-to-End

Skenario lengkap untuk pengujian besok (urutan ini harus diikuti):

### Langkah 1 — Verifikasi knowledge base
```bash
cd maximo-knowledge
.venv/bin/python -m unittest discover -s tests
# Expected: 37 tests OK
```

### Langkah 2 — Validasi contracts
```bash
cd ../reliability-data-contracts
../maximo-knowledge/.venv/bin/python -c "
import json, glob
from jsonschema import Draft202012Validator
for f in sorted(glob.glob('schemas/*.schema.json')):
    Draft202012Validator.check_schema(json.load(open(f)))
    print(f'OK: {f}')
"
# Expected: 12 schema OK
```

### Langkah 3 — Setup cockpit DB
```bash
cd ../reliability-cockpit
.venv/bin/pip install -e .       # pastikan 'cockpit' command tersedia
.venv/bin/cockpit init-db
# Expected: cockpit local tables created (Postgres)
```

### Langkah 4 — Sync data Maximo
```bash
.venv/bin/cockpit sync
# Expected: beberapa object upserted, mode=full untuk run pertama
```

### Langkah 5 — Hitung KPI
```bash
.venv/bin/cockpit kpi
# Expected: KPI computed & persisted untuk 4 metric
```

### Langkah 6 — Start API + Web
```bash
# Terminal 1
.venv/bin/cockpit serve
# Terminal 2
cd web && npm run dev
```

### Langkah 7 — Verifikasi via browser
1. Buka `http://localhost:3000` → tabel equipment muncul
2. Klik sebuah equipment ID → halaman detail dengan **4 KPI cards**
3. Klik nav "Work Orders" → tabel work orders
4. Buka `http://localhost:8000/docs` → Swagger UI untuk eksplorasi API

---

## 8. Checklist Verifikasi

| # | Item | Cara cek | Expected |
|---|---|---|---|
| 1 | maximo-knowledge tests | `python -m unittest discover -s tests` | 37 OK |
| 2 | Schema validation (knowledge) | termasuk dalam test #1 | 4 OK |
| 3 | Contracts schema valid | python jsonschema script | 12 OK |
| 4 | Cockpit tests | `python -m unittest discover -s tests` | 34 OK |
| 5 | `cockpit` command available | `cockpit --help` | show 4 subcommands |
| 6 | DB tables created | `cockpit init-db` | "tables created" |
| 7 | Sync berhasil | `cockpit sync` | rows seen/upserted > 0 |
| 8 | KPI terhitung | `cockpit kpi` | 4 metrics x N equipment |
| 9 | API health | `curl localhost:8000/health` | `{"status":"ok"}` |
| 10 | API equipment | `curl localhost:8000/equipment?limit=1` | JSON array |
| 11 | API KPI | `curl localhost:8000/kpis/{id}/MTBF` | JSON with value |
| 12 | Web equipment table | buka `localhost:3000` | tabel muncul |
| 13 | Web KPI cards | klik equipment ID | 4 KPI cards |
| 14 | Web work orders | buka `localhost:3000/work-orders` | tabel muncul |

---

## 9. Troubleshooting

### `cockpit: command not found`
Pastikan install dengan `-e .` dan pakai venv yang benar:
```bash
cd reliability-cockpit
.venv/bin/pip install -e .
.venv/bin/cockpit --help        # atau aktifkan venv: source .venv/bin/activate
```

### `connection refused` / database error
Postgres belum running atau database belum dibuat:
```bash
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE USER cockpit WITH PASSWORD 'cockpit';"
sudo -u postgres psql -c "CREATE DATABASE cockpit OWNER cockpit;"
cockpit init-db
```

### Sync menghasilkan 0 rows
Kemungkinan token/cookie expired atau tidak ada akses:
- Cek `MAXIMO_READ_ONLY_TOKEN` atau `MAXIMO_SESSION_COOKIE` di `.env`
- Pastikan token memiliki READ access ke site BSR
- Lihat log error: `cockpit sync` mencetak `OslcError` jika auth gagal

### KPI endpoint return 404
KPI belum dihitung. Jalankan dulu:
```bash
cockpit kpi
```

### Web UI "Belum ada data"
Sync belum dijalankan. Backend API harus punya data dulu:
```bash
cockpit sync && cockpit kpi
cockpit serve                   # biarkan running di terminal ini
```

### `ModuleNotFoundError: jsonschema`
Hanya relevan untuk maximo-knowledge:
```bash
cd maximo-knowledge
.venv/bin/pip install -r requirements.txt
```

### 6 object forbidden (BMXAA0024E)
`failurecode`, `location`, `pm`, `meter`, `jobplan`, `mxapiwodetail` tidak
bisa dibaca dengan akun discovery saat ini. Ini **bukan bug** — akun butuh
READ sigoption pada object tersebut (grant oleh Maximo admin, scoped ke BSR).

### Port sudah dipakai
```bash
cockpit serve --port 9000       # ganti port API
npm run dev -- -p 3001          # ganti port web
```
Update `web/.env.local`: `COCKPIT_API_BASE=http://127.0.0.1:9000`
