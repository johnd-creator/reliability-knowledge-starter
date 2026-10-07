"""Reproducible contract exports; --check is read-only, --write updates files.

The handoff reuses canonical evidence/selection schema assertions rather than
weakening them to bare Pydantic shapes. Cross-field identity/provenance rules
remain enforced by EvidenceBatch at the trusted consumer boundary.
"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.domain.condition_evidence import EvidenceBatch
from src.domain.integration_status import IntegrationStatus,CollectorObservation
ROOT=Path(__file__).resolve().parents[2]/"reliability-data-contracts/schemas"

def exports():
    result={"integration-status":IntegrationStatus.model_json_schema(),"collector-observation":CollectorObservation.model_json_schema()}
    batch=EvidenceBatch.model_json_schema()
    for model,filename in (("ConditionEvidence","condition-evidence"),("ProjectionPlan","condition-projection-plan"),("SignalSelection","condition-signal-selection")):
        canonical=json.loads((ROOT/(filename+".schema.json")).read_text())
        batch["$defs"].update(canonical.pop("$defs",{}))
        for key in ("$schema","$id"):canonical.pop(key,None)
        batch["$defs"][model]=canonical
    result["condition-evidence-batch"]=batch
    for name,schema in result.items():
        schema["$schema"]="https://json-schema.org/draft/2020-12/schema"
        schema["$id"]="https://contracts.reliability.local/"+name+".schema.json"
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group();mode.add_argument("--check",action="store_true");mode.add_argument("--write",action="store_true")
    args=parser.parse_args();failures=[]
    for name,schema in exports().items():
        path=ROOT/(name+".schema.json")
        if args.write:path.write_text(json.dumps(schema,indent=2)+"\n")
        elif not path.exists() or json.loads(path.read_text())!=schema:failures.append(name)
    if failures:raise SystemExit("contract drift: "+", ".join(failures))
    print("3 canonical exports: "+("written" if args.write else "compatible"))
if __name__=="__main__":main()
