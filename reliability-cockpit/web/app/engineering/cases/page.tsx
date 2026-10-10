import CaseWorkspace from '../../../components/CaseWorkspace';
export const dynamic='force-dynamic';
export default function Page(){return <CaseWorkspace enabled={process.env.NODE_ENV==='development'&&process.env.NADI_ENGINEERING_QA_ENABLED==='true'}/>;}
