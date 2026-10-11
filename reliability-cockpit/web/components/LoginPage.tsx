import Image from "next/image";
import Link from "next/link";
import LocalLogin from "./LocalLogin";

/** Presentation for the existing development login; no application access policy. */
export default function LoginPage({ expired = false }: { expired?: boolean }) {
  return <div className="nadi-login-page">
    <div className="login-page-heading">
      <div><p className="eyebrow">ENGINEERING DEVELOPMENT ACCESS</p><h1>NADI login</h1></div>
      <Link className="button" href="/">← Executive Overview</Link>
    </div>
    <div className="login-surface">
      <aside className="login-brand-panel" aria-label="NADI product identity">
        <div className="login-logo-surface">
          <Image src="/logo_nadi.png" width={820} height={468} alt="NADI — Platform Analitik Keandalan Aset Pembangkit" priority />
        </div>
        <p className="login-brand-eyebrow">RELIABILITY DATA PLATFORM</p>
        <h2>Trusted evidence.<br />Clear engineering decisions.</h2>
        <p className="login-brand-copy">Asset context, engineering evidence and accountable follow-up in one workspace.</p>
        <div className="login-brand-context"><span>OPERATING CONTEXT</span><strong>PLTU Banten 1 Suralaya</strong><p>Engineering development · isolated QA</p></div>
      </aside>
      <div className="login-form-panel"><LocalLogin expired={expired} /></div>
    </div>
    <p className="login-page-note">Factual development screens remain accessible. This sign-in opens the existing isolated Engineering workspace.</p>
  </div>;
}
