import {headers} from "next/headers";
import {redirect} from "next/navigation";
import {localGuardEnabled,verifyLocalSession} from "../../lib/local-session";
import AuthenticatedWorkspace from "../../components/AuthenticatedWorkspace";
import DevelopmentStatus from "../../components/DevelopmentStatus";
import { AppShell } from "../../components/ui";
import EngineeringDraftProviders from "../../components/EngineeringDraftProviders";
import {PdmDraftProvider} from "../../components/PdmDraftContext";

export const dynamic="force-dynamic";
export default async function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const liveDevelopment = process.env.NODE_ENV === "development" && process.env.NADI_LIVE_DEV === "true";
  const identity=localGuardEnabled()?await verifyLocalSession(await headers()):null;
  if(identity?.state==="anonymous")redirect("/login");
  if(identity?.state==="unavailable")return <main className="state-card" role="alert"><h1>Otoritas sesi tidak tersedia</h1><p>Akses ditutup sementara. Muat ulang setelah layanan pulih.</p></main>;
  const shell=<AppShell engineeringVisible={process.env.NADI_ENGINEERING_WORKSPACE_ENABLED === "true"} liveDevelopment={liveDevelopment}>
    {liveDevelopment && (!identity || identity.state==="authenticated" && identity.session.roles.includes("ADMIN")) && <DevelopmentStatus />}<EngineeringDraftProviders>{children}</EngineeringDraftProviders>
  </AppShell>;
  return <PdmDraftProvider>{identity?.state==="authenticated"?<AuthenticatedWorkspace identity={identity.session}>{shell}</AuthenticatedWorkspace>:shell}</PdmDraftProvider>;
}
