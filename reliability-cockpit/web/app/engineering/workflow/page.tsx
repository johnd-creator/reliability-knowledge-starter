import {notFound} from "next/navigation";
import EngineeringWorkflow from "../../../components/EngineeringWorkflow";
import {PageHeader,EmptyState} from "../../../components/ui";
import {engineeringMode} from "../../../lib/engineering";
export const dynamic="force-dynamic";
export default function WorkflowCandidate(){
  const mode=engineeringMode(process.env);
  if(mode==="OFF")notFound();
  if(mode!=="DEMO")return <><PageHeader eyebrow="PHASE 2 / CANDIDATE" title="Engineering workflow unavailable" description="Production identity, reviewed provisioning and engineer field approval remain pending."/><EmptyState title="Operational Engineering is BLOCKED." detail="No operational inspection, recommendation or review actions enabled."/></>;
  return <EngineeringWorkflow/>;
}
