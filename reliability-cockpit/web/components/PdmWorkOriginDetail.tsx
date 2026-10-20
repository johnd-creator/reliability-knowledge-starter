import type {Inspection} from '../lib/product-records';
export default function PdmWorkOriginDetail({row}:{row:Inspection}){
 const origin=row.work_origin;
 return <div className="pdm-work-origin"><h3>Asal pekerjaan</h3><dl className="asset-facts"><div><dt>Sumber pekerjaan</dt><dd>{!origin?'Belum dicatat (tidak diketahui)':origin.source==='DEPARTMENT_REQUEST'?'Permintaan bidang':'Temuan PdM · PM 52 week'}</dd></div>{origin?.source==='DEPARTMENT_REQUEST'&&<div><dt>Bidang peminta</dt><dd>{origin.requesting_department}</dd></div>}<div><dt>Aset kanonis inspeksi</dt><dd>{row.canonical_asset_id}</dd></div>{origin&&<div><dt>Label aset pada permintaan / temuan (belum diverifikasi)</dt><dd>{origin.reported_asset_label??'Belum dicatat'}</dd></div>}</dl></div>;
}
