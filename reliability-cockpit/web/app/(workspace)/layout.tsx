import DevelopmentStatus from "../../components/DevelopmentStatus";
import { AppShell } from "../../components/ui";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const liveDevelopment = process.env.NODE_ENV === "development" && process.env.NADI_LIVE_DEV === "true";
  return <AppShell engineeringVisible={process.env.NADI_ENGINEERING_WORKSPACE_ENABLED === "true"} liveDevelopment={liveDevelopment}>
    {liveDevelopment && <DevelopmentStatus />}{children}
  </AppShell>;
}
