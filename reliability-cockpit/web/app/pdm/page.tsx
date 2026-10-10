import PdmCenter from "../../components/PdmCenter";
export const dynamic="force-dynamic";
export default function Page(){return <PdmCenter qaEnabled={process.env.NODE_ENV==="development"&&process.env.NADI_ENGINEERING_QA_ENABLED==="true"}/>;}
