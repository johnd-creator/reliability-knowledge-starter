import {notFound} from "next/navigation";
import LocalLogin from "../../components/LocalLogin";
import {PageHeader} from "../../components/ui";
export const dynamic="force-dynamic";
export default async function Page({searchParams}:{searchParams:Promise<{expired?:string}>}) {
 if(process.env.NODE_ENV!=="development"||process.env.NADI_ENGINEERING_QA_ENABLED!=="true")notFound();
 const query=await searchParams;
 return <div className="engineering-qa"><PageHeader eyebrow="DEVELOPMENT / DISPOSABLE QA" title="NADI login" description="Secure local sign-in for isolated Engineering workflows."/><LocalLogin expired={query.expired==="1"}/></div>;
}
