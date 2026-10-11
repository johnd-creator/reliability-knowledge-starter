"use client";
import Link from "next/link";
import LocalLogin from "./LocalLogin";
import {Button,EmptyState,LoadingState,SectionCard} from "./ui";
import type {QaState} from "./useQaRecords";
export default function QaProductBoundary({state,reload}:{state:QaState;reload:()=>void}) {
 return <>
  <SectionCard className="product-data-boundary"><strong>{state==="disabled"?"Operational integration NOT ACTIVATED":"DEVELOPMENT QA · SYNTHETIC ENGINEERING RECORDS"}</strong><p>Measurements, observations, interpretations and independent review remain separate. NADI records never authorize or mutate Maximo Work Orders.</p><Link className="text-link" href="/engineering/local">Existing Engineering workflow →</Link></SectionCard>
  {state==="disabled"&&<EmptyState title="Operational application contract UNAVAILABLE" detail="The product layout is implemented. Operational identity, record APIs and engineering acceptance require separate activation; no fixture data is substituted." />}
  {state==="blocked-schema"&&<EmptyState title="Advisory persistence BLOCKED — QA schema prerequisite" detail="The advisory workflow is proven in disposable tests. This persistent QA store has not been migrated; draft/publication/receipt actions stay disabled until a separately authorized schema change."/>}
  {state==="loading"&&<LoadingState label="Reading trusted session and authorized application records…" />}
  {state==="signed-out"&&<LocalLogin expired onAuthenticated={()=>reload()} />}
  {state==="denied"&&<SectionCard><div role="alert"><h2>Record access unavailable or denied</h2><p>Server role and asset scopes remain authoritative. No fallback identity or public record access.</p></div><Button onClick={reload}>Retry authorized access</Button></SectionCard>}
  {state==="error"&&<SectionCard><div role="alert"><h2>Engineering records UNAVAILABLE</h2><p>Previously displayed records have been cleared. No automatic retry.</p></div><Button onClick={reload}>Try again</Button></SectionCard>}
 </>;
}
