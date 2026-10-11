"use client";

import { idText } from "../lib/id-copy";
import ConditionEvidenceView from "./ConditionEvidenceView";
import { useEffect, useState } from "react";
import { reliabilityApi, type AssetConditionEvidence } from "@/lib/api";
import { EmptyState, LoadingState, SectionCard } from "@/components/ui";

export default function ConditionEvidencePanel({ canonicalId }: { canonicalId: string }) {
  const [data, setData] = useState<AssetConditionEvidence | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let cancelled = false;
    setData(null); setLoading(true);
    reliabilityApi.conditionEvidence(canonicalId).then((result) => { if (!cancelled) setData(result); })
      .catch(() => { if (!cancelled) setData(null); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [canonicalId]);
  return <SectionCard>
    <div className="section-heading"><div><p className="eyebrow">{idText("Selected signal evidence")}</p><h2>{idText("Condition Evidence")}</h2></div></div>
    {loading ? <LoadingState /> : !data ? <EmptyState title={idText("Condition evidence unavailable.")} detail={idText("Equipment condition remains unknown.")} /> : <>
      <ConditionEvidenceView data={data} />
    </>}
  </SectionCard>;
}
