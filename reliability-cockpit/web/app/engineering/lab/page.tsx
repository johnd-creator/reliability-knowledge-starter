import {notFound} from "next/navigation";
import Phase2Workspace from "../../../components/Phase2Workspace";
import {PageHeader,EmptyState} from "../../../components/ui";
import {engineeringMode} from "../../../lib/engineering";
export const dynamic="force-dynamic";
export default function Phase2Lab(){
  const mode=engineeringMode(process.env);
  if(mode==="OFF")notFound();
  if(mode!=="DEMO")return <><PageHeader eyebrow="PHASE 2 / CANDIDATE" title="Engineering Data Platform" description="Operational identity, engineer field approval and provisioning remain pending."/><EmptyState title="Development workspace unavailable." detail="No operational inspection or recommendation actions are enabled."/></>;
  return <Phase2Workspace/>;
}
