import AdvisoryWorkspace from '../../../components/AdvisoryWorkspace';
export const dynamic='force-dynamic';
export default function Page(){return <AdvisoryWorkspace enabled={process.env.NODE_ENV==='development'&&process.env.NADI_ENGINEERING_QA_ENABLED==='true'}/>;}
