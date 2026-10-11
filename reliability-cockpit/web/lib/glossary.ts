export interface GlossaryTerm {
  id: string; english: string; indonesian: string; meaning: string; example: string;
  pending?: boolean;
}

// Product vocabulary derived from PRD, approved DTO boundaries and PR63 requirements.
// These explanations introduce no method definitions, limits or operational authority.
export const glossary: GlossaryTerm[] = [
  {id:'unknown',english:'UNKNOWN',indonesian:'Belum diketahui',meaning:'Informasi belum tersedia atau belum terverifikasi. Bukan angka nol dan bukan kondisi normal.',example:'Satuan atau waktu pengukuran yang belum tersedia tetap UNKNOWN.'},
  {id:'not-assessed',english:'NOT ASSESSED',indonesian:'Belum dinilai',meaning:'Belum ada penilaian yang didukung bukti dan aturan engineering yang disetujui.',example:'Aset dapat memiliki Work Order tetapi kondisi aset tetap belum dinilai.'},
  {id:'approved',english:'APPROVED',indonesian:'Rekam disetujui',meaning:'Keputusan review terhadap rekam NADI tertentu dan versinya. Bukan izin pelaksanaan pekerjaan pembangkit.',example:'Rekomendasi APPROVED dapat menjadi sumber advisory QA, tanpa mengubah WO Maximo.'},
  {id:'ack',english:'Acknowledgment / ACK',indonesian:'Konfirmasi penerimaan',meaning:'Penerima berizin menyatakan telah menerima versi advisory tertentu. Bukan persetujuan isi, izin kerja, atau bukti pekerjaan selesai.',example:'ACK di kotak masuk tidak menutup Work Order.'},
  {id:'synthetic-qa',english:'SYNTHETIC QA',indonesian:'QA sintetis',meaning:'Rekam dan identitas latihan terisolasi untuk menguji aplikasi. Bukan data kondisi pembangkit nyata.',example:'Kasus asset:SYNTHETIC:A digunakan untuk pengujian workflow.'},
  {id:'factual',english:'Factual evidence',indonesian:'Bukti faktual',meaning:'Data dari jalur sumber dan kontrak terkelola, dengan identitas, waktu, dan batas penggunaan yang jelas.',example:'Jumlah Work Order pada populasi Registry bukan jumlah kegagalan.'},
  {id:'demo',english:'DEMO',indonesian:'Demonstrasi',meaning:'Contoh tampilan atau simulasi yang ditandai jelas; bukan klaim operasional.',example:'Rekam demo dalam memori browser berbeda dari rekam QA persisten.'},
  {id:'asset-register',english:'Asset Register',indonesian:'Daftar Aset',meaning:'Aset yang menjadi anggota Registry bisnis NADI. Populasinya berbeda dari seluruh equipment teknis.',example:'Penelusuran /assets memakai identitas Aset Terdaftar.'},
  {id:'asset-health',english:'Asset Health',indonesian:'Kondisi Aset',meaning:'Ruang kerja untuk melihat konteks dan bukti aset. Tampilan ini sendiri tidak menghasilkan skor kondisi.',example:'Ringkasan Kondisi menampilkan NOT ASSESSED jika penilaian belum tersedia.'},
  {id:'canonical-id',english:'Canonical identity',indonesian:'Identitas kanonik',meaning:'Identitas stabil yang mengikat rekam ke aset yang sama tanpa pencocokan nama secara perkiraan.',example:'Detail aset mempertahankan canonical_asset_id dari kontrak backend.'},
  {id:'registry',english:'Registry',indonesian:'Registry / daftar terkelola',meaning:'Daftar keanggotaan yang menetapkan batas aset produk NADI.',example:'Equipment teknis tidak otomatis menjadi Aset Terdaftar.'},
  {id:'mart',english:'Reliability Mart',indonesian:'Reliability Mart',meaning:'Tabel data keandalan kanonik dalam database Maximo Collector yang sudah ada. Jalur publik NADI hanya membaca.',example:'NADI membaca rekam pemeliharaan dari Mart tanpa menulis ke Maximo.'},
  {id:'maximo',english:'Maximo',indonesian:'Maximo',meaning:'Sistem sumber untuk referensi aset dan pemeliharaan. Akses data bisnis NADI tetap hanya-baca.',example:'WO yang sudah ada dapat menjadi referensi informasi rekomendasi.'},
  {id:'work-order',english:'Work Order / WO',indonesian:'Work Order / referensi pekerjaan',meaning:'Rekam pekerjaan pada sistem sumber. Rekomendasi NADI merupakan rekam terpisah dan tidak membuat, menyetujui, atau menutup WO.',example:'Tautan WO pada advisory hanya memberikan konteks informasi.'},
  {id:'maintenance',english:'Maintenance',indonesian:'Pemeliharaan',meaning:'Konteks aktivitas pemeliharaan yang tersedia dari rekam sumber terkelola.',example:'Aktivitas berulang dapat mencakup inspeksi atau pekerjaan terencana, bukan otomatis kegagalan berulang.'},
  {id:'repeat-activity',english:'Repeat Activity',indonesian:'Aktivitas Berulang',meaning:'Lebih dari satu Kejadian Pemeliharaan pada aset yang sama dalam periode dipilih. Bukan identitas kegagalan berulang.',example:'Filter 2+ kejadian menunjukkan aktivitas untuk investigasi.'},
  {id:'pdm',english:'Predictive Maintenance / PdM',indonesian:'PdM / pemeliharaan prediktif',meaning:'Ruang pengukuran dan investigasi kondisi. Persetujuan metode, batas, dan interpretasi operasional tetap terpisah.',example:'Pusat PdM menampilkan pengukuran asli dan konteks review; bukan prediksi otomatis.'},
  {id:'vibration',english:'Vibration',indonesian:'Vibrasi',meaning:'Kelompok metode PdM kandidat untuk konteks pengukuran vibrasi. Definisi kolom, titik, alat, dan batas penilaian belum disahkan.',example:'Rekam vibrasi portabel tidak digabung dengan PI tanpa kesebandingan yang direview.',pending:true},
  {id:'ir',english:'IR Thermography',indonesian:'Termografi inframerah',meaning:'Kelompok metode PdM kandidat. Persyaratan rekam dan interpretasi thermogram harus divalidasi engineer.',example:'Referensi gambar bukan dasar untuk mengarang temperatur atau severity.',pending:true},
  {id:'mcsa',english:'MCSA',indonesian:'MCSA',meaning:'Metode PdM kandidat pada requirement PR63. Definisi input dan interpretasi operasional belum disahkan.',example:'Menu MCSA tidak berarti kontrak pengukuran operasional sudah aktif.',pending:true},
  {id:'tribology',english:'Tribology',indonesian:'Tribologi',meaning:'Metode PdM kandidat pada requirement PR63. Parameter, sampel, dan batas penerimaan memerlukan validasi engineer.',example:'Nilai dan satuan inspeksi ditampilkan sesuai rekam asli.',pending:true},
  {id:'pd-dga',english:'PD / DGA',indonesian:'PD / DGA',meaning:'Makna PD pada kebutuhan sumber belum dikonfirmasi. PD tidak boleh dianggap sama dengan DGA.',example:'Rekam DGA yang ada dipertahankan tanpa mengubahnya menjadi PD.',pending:true},
  {id:'threshold',english:'Severity / threshold / health score',indonesian:'Severity / batas / skor kondisi',meaning:'Definisi dan aturan penilaian memerlukan persetujuan engineer serta bukti memadai. Warna UI tidak menetapkan severity.',example:'Data kosong tidak diberi skor nol atau label sehat.',pending:true},
  {id:'fmea',english:'FMEA',indonesian:'FMEA',meaning:'Domain rekam penilaian FMEA. Header faktual tersedia sesuai populasi; detail mode kegagalan dan RPN belum otomatis tersedia.',example:'Jumlah rekam FMEA tidak ditafsirkan sebagai tingkat risiko.'},
  {id:'rcfa',english:'RCFA',indonesian:'RCFA',meaning:'Domain rekam analisis akar penyebab. Hubungan aset, WO, dan kejadian kegagalan tidak boleh disimpulkan jika belum terselesaikan.',example:'Rekam RCFA global tetap terlihat tanpa pengaitan aset buatan.'},
  {id:'pi',english:'PI System',indonesian:'PI System',meaning:'Sumber konteks historian melalui jalur terkelola. Inventaris sinyal teknis berbeda dari sinyal aset yang disetujui.',example:'Flag Good tidak membuktikan kondisi equipment sehat atau data mutakhir.'},
  {id:'cems',english:'CEMS',indonesian:'CEMS',meaning:'Komponen sumber emisi dengan batas pengumpulan tersendiri. Menu integrasi tidak membuktikan proyeksi NADI lengkap.',example:'Lokalisasi tidak mengubah jadwal atau konfigurasi CEMS.'},
  {id:'case',english:'Engineering Case',indonesian:'Kasus Engineering',meaning:'Rekam investigasi milik NADI yang memisahkan masalah, observasi, hipotesis, bukti, dan review.',example:'Reviewer independen menilai revisi kasus, bukan browser yang menetapkan persetujuan.'},
  {id:'observation',english:'Observation',indonesian:'Observasi',meaning:'Pernyataan tentang hal yang diamati dan dicatat manusia; tidak otomatis menjadi fakta sumber.',example:'Observasi inspeksi ditampilkan terpisah dari interpretasi.'},
  {id:'hypothesis',english:'Hypothesis',indonesian:'Hipotesis',meaning:'Dugaan manusia untuk investigasi, belum merupakan fakta terkonfirmasi.',example:'Hipotesis tidak berubah menjadi fakta hanya karena kasus disetujui.'},
  {id:'review',english:'Independent review',indonesian:'Review independen',meaning:'Penilaian rekam oleh identitas reviewer yang memenuhi kontrol independensi server.',example:'Penulis kasus tidak dapat menyetujui kasusnya sendiri.'},
  {id:'recommendation',english:'Recommendation',indonesian:'Rekomendasi',meaning:'Usulan tindakan dan keputusan review milik NADI, terkait versi kasus serta bukti.',example:'Rekomendasi disetujui tidak sama dengan persetujuan Work Order.'},
  {id:'advisory',english:'Engineering Advisory',indonesian:'Advisory Engineering / informasi engineering',meaning:'Pernyataan terikat versi dari rekomendasi dan bukti yang direview, tersedia bagi penerima berizin.',example:'Publikasi QA hanya ke kotak masuk aplikasi; tanpa email atau penerima nyata.'},
  {id:'inbox',english:'Recipient Inbox',indonesian:'Kotak masuk penerima',meaning:'Tampilan advisory yang boleh dibaca identitas penerima menurut lingkup server.',example:'Peran admin tidak otomatis memberikan keanggotaan penerima.'},
  {id:'follow-up',english:'Follow-Up',indonesian:'Tindak lanjut',meaning:'Progres lokal rekam NADI; tidak mengubah status pekerjaan pada sistem sumber.',example:'COMPLETED lokal tidak membuktikan efektivitas atau menutup WO.'},
  {id:'revision',english:'Revision / CAS',indonesian:'Revisi / pemeriksaan versi',meaning:'Perubahan memakai revisi yang diharapkan agar tidak menimpa revisi terbaru secara diam-diam.',example:'Konflik revisi mempertahankan isian yang belum disimpan.'},
  {id:'idempotency',english:'Idempotency',indonesian:'Idempotensi permintaan',meaning:'Percobaan ulang maksud yang sama mempertahankan ID permintaan untuk menghindari pengulangan mutasi.',example:'Tombol coba lagi memakai request_id yang sama jika payload belum berubah.'},
  {id:'audit',english:'Audit history',indonesian:'Riwayat audit',meaning:'Jejak revisi, pelaku, tindakan, waktu, dan alasan yang dapat ditelusuri.',example:'Advisory ditarik tetap memiliki riwayat publikasi dan ACK.'},
  {id:'provenance',english:'Provenance',indonesian:'Asal-usul dan jejak bukti',meaning:'Konteks sumber, identitas, versi, waktu, serta batas penggunaan suatu bukti.',example:'Snapshot beku mempertahankan satuan dan timestamp asli.'},
  {id:'freshness',english:'Freshness',indonesian:'Kemutakhiran',meaning:'Umur sumber atau proyeksi sesuai kebijakan yang disetujui; berbeda dari kualitas sinyal.',example:'Tanpa kebijakan, kemutakhiran tetap UNKNOWN.'},
  {id:'quality',english:'Quality flags',indonesian:'Flag kualitas',meaning:'Informasi kualitas sinyal sumber. Bukan penilaian kondisi equipment.',example:'Good, Questionable, Substituted, dan Annotated dipertahankan sebagai flag sumber.'},
];

export function searchGlossary(query: string): GlossaryTerm[] {
  const normalized = query.trim().toLocaleLowerCase('id-ID');
  return glossary.filter(term => [term.english, term.indonesian, term.meaning, term.example]
    .some(value => value.toLocaleLowerCase('id-ID').includes(normalized)));
}
