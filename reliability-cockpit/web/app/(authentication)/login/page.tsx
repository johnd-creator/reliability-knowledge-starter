import {notFound} from "next/navigation";
import LoginPage from "../../../components/LoginPage";
import {safeReturnDestination} from "../../../lib/login-navigation";
export const dynamic="force-dynamic";
export default async function Page({searchParams}:{searchParams:Promise<{expired?:string;returnTo?:string|string[]}>}) {
 if(process.env.NODE_ENV!=="development"||process.env.NADI_ENGINEERING_QA_ENABLED!=="true")notFound();
 const query=await searchParams;
 return <LoginPage returnTo={safeReturnDestination(query.returnTo)} expired={query.expired==="1"}/>;
}
