// Browser-only test entry: actual candidate components, no listening server.
import React from 'react';
import {createRoot} from 'react-dom/client';
import {AppShell} from '../../components/AppNavigation';
import Executive from '../../components/ExecutiveOverview';
import Login from '../../components/LoginPage';
import Glossary from '../../components/Glossary';
import Cases from '../../components/CaseWorkspace';
import Advisory from '../../components/AdvisoryWorkspace';
import Recommendations from '../../components/RecommendationWorkspace';
import Pdm from '../../components/PdmCenter';
import EngineeringQa from '../../components/EngineeringQa';
import EngineeringWorkflow from '../../components/EngineeringWorkflow';
import Phase2 from '../../components/Phase2Workspace';
import Engineering from '../../components/EngineeringWorkspace';
import Assets from '../../app/assets/page';
import Asset from '../../app/assets/[...canonicalId]/page';
import Health from '../../app/asset-health/page';
import Maintenance from '../../app/maintenance/page';
import Investigation from '../../app/maintenance/investigation/page';
import Fmea from '../../app/fmea/page';
import Rcfa from '../../app/rcfa/page';
import Overhaul from '../../app/overhauls/page';
import Trust from '../../app/data-quality/page';
import WorkOrders from '../../app/work-orders/page';
import Equipment from '../../app/equipment/[id]/page';
const path=location.pathname;
const pages:Record<string,React.ReactNode>={
 '/':<Executive/>, '/login':<Login/>, '/panduan/istilah':<Glossary/>,
 '/engineering/cases':<Cases enabled/>, '/engineering/advisories':<Advisory enabled/>,
 '/engineering/inbox':<Advisory enabled inbox/>, '/engineering/local':<EngineeringQa localAuthentication/>,
 '/engineering':<Engineering/>, '/engineering/lab':<Phase2/>, '/engineering/workflow':<EngineeringWorkflow/>,
 '/recommendations':<Recommendations qaEnabled/>, '/action-board':<Recommendations qaEnabled board/>,
 '/pdm':<Pdm qaEnabled/>, '/assets':<Assets/>, '/asset-health':<Health/>, '/maintenance':<Maintenance/>,
 '/maintenance/investigation':<Investigation/>, '/fmea':<Fmea/>, '/rcfa':<Rcfa/>, '/overhauls':<Overhaul/>,
 '/data-quality':<Trust/>, '/work-orders':<WorkOrders/>, '/equipment/DEMO':<Equipment params={Promise.resolve({id:'DEMO'})}/>, '/engineering/qa':<EngineeringQa/>,
};
const assetParams=Promise.resolve({canonicalId:[decodeURIComponent(path.split('/').at(-1)??'')]});
const content=path.startsWith('/assets/')?<Asset params={assetParams}/>:pages[path];
createRoot(document.getElementById('root')!).render(<AppShell engineeringVisible liveDevelopment>
 <aside role="note" className="scope-banner engineering-demo"><strong>DEMO — QA SINTETIS · UJI KOMPONEN KANDIDAT</strong><span>Fixture browser terisolasi; bukan data pembangkit atau runtime yang diterapkan.</span></aside>{content}
</AppShell>);
