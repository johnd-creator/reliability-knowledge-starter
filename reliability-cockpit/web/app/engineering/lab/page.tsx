import { idText } from "../../../lib/id-copy";
import {notFound} from "next/navigation";
import Phase2Workspace from "../../../components/Phase2Workspace";
import {PageHeader,EmptyState} from "../../../components/ui";
import {engineeringMode} from "../../../lib/engineering";
export const dynamic="force-dynamic";
export default function Phase2Lab(){
  const mode=engineeringMode(process.env);
  if(mode==="OFF")notFound();
  if(mode!=="DEMO")return <><PageHeader eyebrow={idText("PHASE 2 / CANDIDATE")} title={idText("Engineering Data Platform")} description={idText("Operational identity, engineer field approval and provisioning remain pending.")}/><EmptyState title={idText("Development workspace unavailable.")} detail={idText("No operational inspection or recommendation actions are enabled.")}/></>;
  return <Phase2Workspace/>;
}
