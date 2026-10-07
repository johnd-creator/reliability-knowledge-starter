"use client";
import { useEffect, useState } from "react";
import { reliabilityApi, type IntegrationStatus } from "@/lib/api";
import { LoadingState, EmptyState, SectionCard } from "@/components/ui";
import IntegrationStatusView from "./IntegrationStatusView";

export default function IntegrationStatusPanel({ canonicalId }: { canonicalId?: string }) {
  const [data,setData]=useState<IntegrationStatus | null>(null);
  const [loading,setLoading]=useState(true);
  useEffect(() => {
    let cancelled=false; setData(null); setLoading(true);
    reliabilityApi.integrationStatus(canonicalId).then(next => { if (!cancelled) setData(next); })
      .catch(() => { if (!cancelled) setData(null); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled=true; };
  },[canonicalId]);
  return <SectionCard><div className="section-heading"><h2>Integration Status</h2></div>
    {loading ? <LoadingState /> : data ? <IntegrationStatusView data={data} /> : <EmptyState title="Integration status UNKNOWN." detail="Local evidence cannot be read. Equipment condition remains unknown." />}
  </SectionCard>;
}
