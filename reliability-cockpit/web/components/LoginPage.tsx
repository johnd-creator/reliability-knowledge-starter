import { idText } from "../lib/id-copy";
import Image from "next/image";
import LocalLogin from "./LocalLogin";
import { ThemeToggle } from "./ThemeProvider";

/** Standalone presentation for existing Engineering QA authentication. */
export default function LoginPage({ expired = false, returnTo }: { expired?: boolean; returnTo?: string }) {
  return <div className="nadi-login-page">
    <div className="login-surface">
      <aside className="login-brand-panel" aria-label={idText("NADI product identity")}>
        <div className="login-logo-surface">
          <Image src="/login/logo_nadi-white-cyan.png" width={1939} height={811} alt="NADI — Platform Analitik Keandalan Aset Pembangkit" priority />
        </div>
        <div className="login-brand-message"><p className="login-brand-eyebrow">PLATFORM DATA KEANDALAN</p><h2 className="login-brand-headline">Data Andal<br /><span>Keputusan Terarah</span></h2><span className="login-brand-rule" aria-hidden="true" /></div>
        <svg className="login-energy-line" viewBox="0 0 700 600" fill="none" aria-hidden="true"><path d="M-30 510L320 445Q360 432 390 470L540 85Q570 15 610 75L740 300" stroke="currentColor" strokeWidth="1.5"/></svg>
        <div className="login-brand-context"><strong>PLTU Banten 1 Suralaya</strong><p>Ilustrasi digital · bukan dokumentasi fasilitas</p></div>
      </aside>
      <div className="login-form-panel">
        <div className="login-utilities"><span className="scope-chip">QA terisolasi · SINTETIS</span><ThemeToggle /></div>
        <div className="login-form-content"><LocalLogin returnTo={returnTo} expired={expired} headingLevel={1} />
          <p className="login-page-note">Masuk diperlukan untuk seluruh aplikasi pengembangan lokal. Data faktual tetap hanya-baca; akses mengikuti scope yang disetujui.</p>
        </div>
        <p className="login-footer">NADI · Platform Analitik Keandalan Aset Pembangkit</p>
      </div>
    </div>
  </div>;
}
