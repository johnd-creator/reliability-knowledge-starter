import { idText } from "../../lib/id-copy";
import Link from "next/link";
import {notFound} from "next/navigation";
import EngineeringWorkspace from "../../components/EngineeringWorkspace";
import {PageHeader, EmptyState} from "../../components/ui";
import {engineeringMode} from "../../lib/engineering";
export const dynamic="force-dynamic";
export default function EngineeringPage() {
  const mode=engineeringMode(process.env);
  if(mode==="OFF")notFound();
  if(mode==="BLOCKED")return <><PageHeader eyebrow={idText("PHASE 2 / CANDIDATE")} title={idText("Engineering Workspace")} description={idText("Operational case actions require reviewed authentication and application writer provisioning.")}/><EmptyState title={idText("Authentication integration pending.")} detail={idText("Engineering write and review actions are disabled. Factual NADI browsing remains available.")}/></>;
  return <><Link className="engineering-primary" href="/engineering/lab">{idText("PdM / Asset 360 / Recommendations / Action Board ↗")}</Link><Link className="engineering-primary" href="/engineering/workflow">{idText("Integrated reviewed inspection workflow ↗")}</Link><EngineeringWorkspace/></>;
}
