import {notFound} from "next/navigation";
import EngineeringWorkspace from "../../../components/EngineeringWorkspace";
import {engineeringMode} from "../../../lib/engineering";
export const dynamic="force-dynamic";
export default async function EngineeringCasePage({params}:{params:Promise<{caseId:string}>}) {
  if(engineeringMode(process.env)!=="DEMO")notFound();
  const {caseId}=await params;
  return <EngineeringWorkspace initialCaseId={caseId}/>;
}
