import ReportsCenter from "../../../components/ReportsCenter";
import { PageHeader, SectionCard } from "../../../components/ui";
export const dynamic = "force-dynamic";
export default function Page() {
  if (process.env.NODE_ENV !== "development") return <><PageHeader eyebrow="NADI / Laporan" title="Pusat Laporan" description="Preview kandidat hanya tersedia pada development." /><SectionCard><h2>Akses deployment belum diaktifkan</h2><p>Otorisasi endpoint factual dan lingkup deployment memerlukan review terpisah. Tidak ada reader laporan yang dipasang. Guard halaman tidak melindungi API underlying.</p></SectionCard></>;
  return <ReportsCenter />;
}
