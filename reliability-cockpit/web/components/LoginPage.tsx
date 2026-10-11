import { idText } from "../lib/id-copy";
import Image from "next/image";
import LocalLogin from "./LocalLogin";
import { ThemeToggle } from "./ThemeProvider";

/** Standalone presentation for existing Engineering QA authentication. */
export default function LoginPage({ expired = false }: { expired?: boolean }) {
  return <div className="nadi-login-page">
    <div className="login-surface">
      <aside className="login-brand-panel" aria-label={idText("NADI product identity")}>
        <div className="login-logo-surface">
          <Image src="/logo_nadi.png" width={820} height={468} alt="NADI — Platform Analitik Keandalan Aset Pembangkit" priority />
        </div>
        <p className="login-brand-eyebrow">{idText("RELIABILITY DATA PLATFORM")}</p>
        <p className="login-brand-headline">{idText("Trusted evidence.")}<br />{idText("Clear engineering decisions.")}</p>
        <p className="login-brand-copy">{idText("Asset context, engineering evidence and accountable follow-up in one workspace.")}</p>
        <div className="login-brand-context"><span>{idText("OPERATING CONTEXT")}</span><strong>PLTU Banten 1 Suralaya</strong><p>{idText("Engineering development · isolated QA")}</p></div>
      </aside>
      <div className="login-form-panel">
        <div className="login-utilities"><span className="scope-chip">QA SINTETIS · Engineering</span><ThemeToggle /></div>
        <div className="login-form-content"><LocalLogin expired={expired} headingLevel={1} />
          <p className="login-page-note">{idText("Factual development screens remain accessible. This sign-in opens the existing isolated Engineering workspace.")}</p>
        </div>
        <p className="login-footer">NADI · Platform Analitik Keandalan Aset Pembangkit</p>
      </div>
    </div>
  </div>;
}
