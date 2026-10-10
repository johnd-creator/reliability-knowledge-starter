import RecommendationWorkspace from "../../components/RecommendationWorkspace";
export const dynamic="force-dynamic";
export default function Page(){return <RecommendationWorkspace qaEnabled={process.env.NODE_ENV==="development"&&process.env.NADI_ENGINEERING_QA_ENABLED==="true"}/>;}
