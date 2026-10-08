import {notFound} from "next/navigation";
import EngineeringWorkspace from "../../components/EngineeringWorkspace";
import {PageHeader, EmptyState} from "../../components/ui";
import {engineeringMode} from "../../lib/engineering";
export const dynamic="force-dynamic";
export default function EngineeringPage() {
  const mode=engineeringMode(process.env);
  if(mode==="OFF")notFound();
  if(mode==="BLOCKED")return <><PageHeader eyebrow="PHASE 2 / CANDIDATE" title="Engineering Workspace" description="Operational case actions require reviewed authentication and application writer provisioning."/><EmptyState title="Authentication integration pending." detail="Engineering write and review actions are disabled. Factual NADI browsing remains available."/></>;
  return <EngineeringWorkspace/>;
}
