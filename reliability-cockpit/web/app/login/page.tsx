import {notFound} from "next/navigation";
import LoginPage from "../../components/LoginPage";
export const dynamic="force-dynamic";
export default async function Page({searchParams}:{searchParams:Promise<{expired?:string}>}) {
 if(process.env.NODE_ENV!=="development"||process.env.NADI_ENGINEERING_QA_ENABLED!=="true")notFound();
 const query=await searchParams;
 return <LoginPage expired={query.expired==="1"}/>;
}
