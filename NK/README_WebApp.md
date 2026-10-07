# 🔥 Aplikasi Web Prediksi Nilai Kalor (NK) Batubara

Aplikasi web interaktif untuk memprediksi Nilai Kalor batubara menggunakan model Machine Learning yang telah dioptimasi dengan Genetic Algorithm dan Particle Swarm Optimization.

## 🚀 Fitur Utama

### 1. **Prediksi Real-time**
- Input parameter operasional pembangkit secara interaktif
- Prediksi NK dengan confidence interval
- Gauge chart untuk visualisasi hasil

### 2. **Interface User-Friendly**
- Sidebar dengan parameter input yang terorganisir
- Slider untuk setiap parameter dengan range yang sesuai
- Kategorisasi parameter (Beban & Daya, Batubara, Steam, dll.)

### 3. **Visualisasi Komprehensif**
- Gauge chart untuk hasil prediksi
- Radar chart untuk distribusi parameter
- Bar chart untuk nilai parameter
- Histogram data historis

### 4. **Analisis Lanjutan**
- Perbandingan dengan data historis
- Statistik prediksi (mean, std, min, max)
- Download data input dalam format CSV

## 📋 Parameter Input

Aplikasi menerima 13 parameter operasional:

### ⚡ Parameter Beban & Daya
- **Gross Load** (MW): 100-800
- **PS**: 0-100

### 🔥 Parameter Batubara
- **Coal Flow** (t/h): 10-200
- **SFC** (Specific Fuel Consumption): 0.1-1.0

### 💨 Parameter Steam
- **Main Steam Press** (bar): 50-200
- **Main Steam Temp** (°C): 400-600
- **Main Steam Flow** (t/h): 100-1000

### 🌡️ Parameter Temperatur
- **Economizer Inlet Temp** (°C): 200-400
- **APH Flue Gas Temp** (°C): 100-300

### 🌬️ Parameter Udara & Gas
- **APH A In O2** (%): 2-10
- **Condensor Vacuum** (mmHg): -800 to -600
- **Feedwater Flow** (t/h): 100-1000
- **Total Air Flow** (t/h): 500-2000

## 🛠️ Instalasi dan Penggunaan

### 1. **Persiapan Environment**
```bash
# Install dependencies
pip3 install -r requirements.txt
```

### 2. **Menjalankan Aplikasi**
```bash
# Jalankan aplikasi Streamlit
streamlit run nk_web_app.py

# Atau dengan konfigurasi headless
STREAMLIT_SERVER_EMAIL='' python3 -m streamlit run nk_web_app.py --server.headless=true
```

### 3. **Akses Aplikasi**
- **Local URL**: http://localhost:8501
- **Network URL**: http://[IP_ADDRESS]:8501

## 📊 Model Information

### Model Terbaik: Random Forest dengan Genetic Algorithm
- **Akurasi**: 94.56% (MAE: 216.74 kJ/kg)
- **Test R²**: 0.268
- **Cross-validation**: MAE 199.38 ± 9.70
- **Data Training**: 900+ sampel data operasional

### File Model
- `optimasi/best_model_optimasi.pkl` - Model Random Forest teoptimasi
- `optimasi/scaler_optimasi.pkl` - Scaler untuk preprocessing
- `prediksi_NK.pkcls` - Model fallback (jika diperlukan)

## 🎯 Cara Menggunakan

### 1. **Input Parameter**
- Buka sidebar di sebelah kiri
- Atur nilai parameter menggunakan slider
- Parameter dikelompokkan berdasarkan kategori

### 2. **Prediksi**
- Klik tombol "🚀 Prediksi NK"
- Tunggu hasil prediksi muncul
- Lihat nilai NK dengan confidence interval

### 3. **Analisis Hasil**
- Periksa kategori kualitas batubara
- Lihat gauge chart untuk visualisasi
- Analisis distribusi parameter dengan radar chart

### 4. **Export Data**
- Download parameter input sebagai CSV
- Bandingkan dengan data historis

## 📈 Interpretasi Hasil

### Kategori Kualitas Batubara
- 🟢 **Sangat Baik**: NK > 6000 kJ/kg
- 🟡 **Baik**: NK 5000-6000 kJ/kg
- 🟠 **Sedang**: NK 4000-5000 kJ/kg
- 🔴 **Rendah**: NK < 4000 kJ/kg

### Confidence Interval
- Menunjukkan tingkat kepercayaan prediksi (95% CI)
- Semakin kecil interval, semakin akurat prediksi
- Berdasarkan variabilitas prediksi dari ensemble trees

## 🔧 Troubleshooting

### Error: Model tidak ditemukan
```
❌ Model tidak dapat dimuat! Pastikan file model tersedia.
```
**Solusi**: Pastikan file `optimasi/best_model_optimasi.pkl` dan `optimasi/scaler_optimasi.pkl` ada di direktori yang benar.

### Error: Import module
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solusi**: Install dependencies dengan `pip3 install -r requirements.txt`

### Performance Warning
```
For better performance, install the Watchdog module
```
**Solusi**: Install watchdog dengan `pip install watchdog`

## 📁 Struktur File

```
NK/
├── nk_web_app.py              # Aplikasi Streamlit utama
├── requirements.txt           # Dependencies Python
├── README_WebApp.md          # Dokumentasi aplikasi
├── optimasi/
│   ├── best_model_optimasi.pkl    # Model Random Forest terbaik
│   ├── scaler_optimasi.pkl        # Scaler preprocessing
│   ├── prediksi_optimasi.csv      # Data prediksi historis
│   └── laporan_makalah_optimasi.md # Laporan lengkap
└── prediksi_NK.pkcls         # Model fallback
```

## 🎓 Background Teknis

Aplikasi ini dikembangkan berdasarkan:
- **Modul 8d - Optimasi Tingkat Lanjut**
- **Genetic Algorithm** untuk hyperparameter tuning Random Forest
- **Particle Swarm Optimization** untuk optimasi Gradient Boosting
- **Cross-validation** untuk validasi model
- **Feature engineering** dari data operasional pembangkit

## 📞 Support

Untuk pertanyaan atau masalah teknis:
1. Periksa file log di terminal
2. Pastikan semua dependencies terinstall
3. Verifikasi keberadaan file model
4. Cek koneksi network untuk akses web

---

**Developed with ❤️ using Streamlit and Scikit-learn**

*Aplikasi ini dirancang untuk membantu operator pembangkit dalam memprediksi kualitas batubara secara real-time berdasarkan parameter operasional.*
## Input Manual dan PI Collector

Pilih **Sumber input → Manual** atau **PI Collector**. Manual tetap dapat
menggunakan slider atau CSV dengan 13 kolom bernama persis seperti fitur model.
Prediksi saat input berubah tidak menjalankan loop refresh yang memblokir halaman.

Mode PI membaca **data tersimpan** melalui `GET /attributes` dan
`GET /snapshots?limit=5000` dari API collector. NK tidak menghubungi PI produksi,
tidak memicu koleksi, tidak memiliki kredensial database, dan tidak membuat DB baru.

Konfigurasi opsional: salin `.env.example` ke `.env` di direktori NK.
`PI_COLLECTOR_API_BASE` default `http://127.0.0.1:8001`; batas umur sumber 900 detik,
selisih waktu antarfitur 300 detik, refresh otomatis 60 detik. Environment proses
mengalahkan file `.env`. Jangan memasukkan password dalam URL API.

Di panel **Pemetaan 13 fitur ke atribut PI**, pilih atribut yang tersedia,
isi satuan sumber dan satuan training, serta referensi bukti; konfirmasi
kesesuaiannya dan klik **Simpan pemetaan**. Konfigurasi disimpan dalam
`pi_feature_mapping.json`, berlaku bersama bagi sesi NK di workspace ini.
Daftar kandidat dan keterbatasan awal terdapat di `PI_MAPPING.md`.
Kandidat hanya petunjuk pencarian: seluruh pemetaan awal berstatus `unknown`.
Jangan mengonfirmasi satuan atau hubungan fitur hanya berdasarkan nama tag.

Mode otomatis baru memprediksi setelah semua 13 pemetaan dikonfirmasi dan
snapshot lolos pemeriksaan identitas registry verified/ok, angka finite,
`value_good=true`, questionable/substituted=false, satuan dan timestamp.
Data hilang, kualitas tidak diketahui, terlalu lama, timestamp tanpa timezone,
atau waktu antarfitur terlalu jauh akan memblokir prediksi. Tidak ada penggantian
otomatis dengan nilai manual atau nol. Mengganti mode tidak menampilkan hasil
mode sebelumnya. Refresh otomatis menggunakan fragment Streamlit agar hasil
tetap tampil; pembacaan ulang selalu memvalidasi data terkini.

Konversi yang tersedia: satuan identik atau tekanan kPa/MPa/bar/mmHg.
Perubahan absolute/gauge pressure atau rumus PS/SFC tidak disimpulkan otomatis.
File model dan scaler menggunakan urutan fitur yang sama dengan scaler training.
Hasil ini masih perlu validasi terhadap data dan label NK unit operasional;
keberhasilan integrasi teknis tidak membuktikan akurasi model di produksi.
Riwayat prediksi PI hanya disimpan di sesi (maksimal 50 batch berbeda), dapat
unduh JSON; tidak tersimpan permanen setelah sesi ditutup.

```bash
cd NK
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run nk_web_app.py --server.address 127.0.0.1 --server.port 8501
MPLCONFIGDIR=/tmp/nk-matplotlib .venv/bin/python -m unittest discover -s tests
```
