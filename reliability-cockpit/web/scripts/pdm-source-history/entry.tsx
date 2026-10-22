// Actual component; all data and requests are synthetic/intercepted by the runner.
import React,{useCallback,useState} from 'react';
import {createRoot} from 'react-dom/client';
import PdmSourceHistory from '../../components/PdmSourceHistory';
function Fixture(){const [selected,setSelected]=useState(''),[expired,setExpired]=useState(false);const onExpired=useCallback(()=>setExpired(true),[]);return <main className="nadi-shell"><p>DEMO — UJI RIWAYAT SUMBER SINTETIS</p><PdmSourceHistory onExpired={onExpired} onSelect={setSelected}/><output>{expired?'SESI BERAKHIR':selected}</output></main>;}
createRoot(document.getElementById('root')!).render(<Fixture/>);
