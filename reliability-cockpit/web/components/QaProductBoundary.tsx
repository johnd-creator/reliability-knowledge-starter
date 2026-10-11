"use client";
import { idText } from "../lib/id-copy";
import Link from "next/link";
import LocalLogin from "./LocalLogin";
import {Button,EmptyState,LoadingState,SectionCard} from "./ui";
import type {QaState} from "./useQaRecords";
export default function QaProductBoundary({state,reload}:{state:QaState;reload:()=>void}) {
 return <>
  <SectionCard className="product-data-boundary"><strong>{state==="disabled"?idText("Operational integration NOT ACTIVATED"):idText("DEVELOPMENT QA · SYNTHETIC ENGINEERING RECORDS")}</strong><p>{idText("Measurements, observations, interpretations and independent review remain separate. NADI records never authorize or mutate Maximo Work Orders.")}</p><div className="page-actions"><Link className="text-link" href="/engineering/local">{idText("Existing Engineering workflow →")}</Link><Link className="text-link" href="/panduan/istilah#approved">Panduan: persetujuan rekam bukan izin pekerjaan →</Link></div></SectionCard>
  {state==="disabled"&&<EmptyState title={idText("Operational application contract UNAVAILABLE")} detail={idText("The product layout is implemented. Operational identity, record APIs and engineering acceptance require separate activation; no fixture data is substituted.")} />}
  {state==="blocked-schema"&&<EmptyState title={idText("Advisory persistence BLOCKED — QA schema prerequisite")} detail={idText("The advisory workflow is proven in disposable tests. This persistent QA store has not been migrated; draft/publication/receipt actions stay disabled until a separately authorized schema change.")}/>}
  {state==="loading"&&<LoadingState label={idText("Reading trusted session and authorized application records…")} />}
  {state==="signed-out"&&<LocalLogin expired onAuthenticated={()=>reload()} />}
  {state==="denied"&&<SectionCard><div role="alert"><h2>{idText("Record access unavailable or denied")}</h2><p>{idText("Server role and asset scopes remain authoritative. No fallback identity or public record access.")}</p></div><Button onClick={reload}>{idText("Retry authorized access")}</Button></SectionCard>}
  {state==="error"&&<SectionCard><div role="alert"><h2>{idText("Engineering records UNAVAILABLE")}</h2><p>{idText("Previously displayed records have been cleared. No automatic retry.")}</p></div><Button onClick={reload}>{idText("Try again")}</Button></SectionCard>}
 </>;
}
