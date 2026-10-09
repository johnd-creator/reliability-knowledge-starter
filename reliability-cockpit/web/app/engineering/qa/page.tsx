import {notFound} from 'next/navigation';
import EngineeringQa from '../../../components/EngineeringQa';
export const dynamic='force-dynamic';
export default function Page(){
 if(process.env.NODE_ENV!=='development'||process.env.NADI_ENGINEERING_QA_ENABLED!=='true')notFound();
 return <EngineeringQa/>;
}
