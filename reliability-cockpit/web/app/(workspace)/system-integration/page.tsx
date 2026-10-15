import SystemIntegrationCenter from "../../../components/SystemIntegrationCenter";
import { PageHeader, SectionCard } from "../../../components/ui";
export const dynamic = "force-dynamic";
export default function Page() {
  // Existing factual endpoints have no route-level auth dependency. Deployment authorization is a separate prerequisite.
  if (process.env.NODE_ENV !== "development") return <><PageHeader eyebrow="NADI / Integrasi" title="Pusat Integrasi Sistem" description="Kandidat workspace ini tersedia hanya pada development." /><SectionCard><h2>Akses deployment belum diaktifkan</h2><p>Otorisasi endpoint dan lingkup deployment memerlukan review terpisah. Tidak ada bukti integrasi yang diminta oleh halaman ini.</p></SectionCard></>;
  return <SystemIntegrationCenter />;
}
