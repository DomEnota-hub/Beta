#!/usr/bin/env python3
"""Stage 5 start: validate two source-divergence dossiers, not operational methods."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH="docs/diagnostics/DIAGNOSTIC_AUTHORING_STAGE5_SOURCE_VARIATION.json"

def require(value,message):
    if not value: raise ValueError(message)

def check(doc, inventory):
    require(doc["stage"]=="5/51" and
            doc["workStatus"]=="FIRST_PAIR_DISCOVERY_ONLY_NOT_STAGE_COMPLETE",
            "premature Stage 5 completion")
    require(doc["donorCommit"]==inventory["donorCommit"],"wrong donor version")
    require(doc["publicationStatus"]=="CANDIDATE" and doc["runtimeImport"] is False
            and doc["actionAuthorityGranted"] is False, "published source dossier")
    require(doc["selectionPriority"]=="DIAGNOSTIC_DISTINCTNESS_BEFORE_SOURCE_COUNT",
            "source count is not diagnostic diversity")
    by={r["scenarioId"]:r for r in inventory["rows"]}
    ids=[x["scenarioId"] for x in doc["scenarios"]]
    require(len(ids)==len(set(ids))==2 and
            set(ids)=={"vl80s.diag.gv-no-close","vl80s.diag.ekg-stuck"},
            "Stage 5 pilot identities drifted")
    for case in doc["scenarios"]:
        row=by[case["scenarioId"]]
        require(case["sourceScenarioId"]==row["sourceScenarioId"] and
                case["canonicalRuntimePath"]==row["donorPath"] and
                case["canonicalGraphNodeCount"]==row["graph"]["nodeCount"] and
                case["variantIds"]==row["variantIds"], "canonical scenario drifted")
        require(case["canonicalSourceRefCount"]==row["sourceRefCount"]==
                len(case["canonicalSourceRefs"]) and case["canonicalSourceRefs"]==row["sourceRefIds"],
                "must distinguish new research from canonical source links")
        require(all(v=="NOT_AUTHORED" for v in case["versions"].values()),
                "discovery cannot auto-publish authored versions")
        require(case["publicationStatus"]=="CANDIDATE" and
                case["runtimeImport"] is False and case["actionAuthorityGranted"] is False,
                "case activated")
        sources=case["alternativeSourceCandidates"]
        require(len(sources)>=2 and len({s["id"] for s in sources})==len(sources), "too few independent source records")
        require(len({s["approachFocus"] for s in sources})>=2 and
                case["distinctDiagnosticFocusCount"]==len({s["approachFocus"] for s in sources}),
                "multiple URLs are not multiple diagnostic methods")
        require(case["candidateSourceCount"]==len(sources) and
                len({s["url"] for s in sources})>=2,"provenance URL missing")
        for s in sources:
            require(s["url"].startswith("https://") and bool(s["title"]) and
                    bool(s["recordedDifference"]), "source description missing")
            require(s["evidenceBasis"]=="PUBLIC_PAGE_AND_SUBJECT_SNIPPET_LOCATED_FULL_CLAIM_NOT_REVIEWED"
                    and s["currentOperationalAuthorityVerified"] is False and
                    s["applicabilityToInstalledVariantVerified"] is False,
                    "unverified external source promoted")
            require(s["actionDisposition"]=="INFORMATION_ONLY" and
                    s["executable"] is False and s["permittedProcedureSteps"]==[]
                    and s["unsafeOperationalTechniquesExcluded"] is True
                    and s["needsIndependentTechnicalReview"] is True,
                    "historical solution converted into operating command")
        require(case["differingInterpretationsAreVerifiedContradictions"] is False,
                "difference of methods not yet proven contradiction")
    return {"scenarios":len(ids),"sourceRecords":sum(len(c["alternativeSourceCandidates"]) for c in doc["scenarios"])}

if __name__=="__main__":
    doc=json.loads((ROOT/PATH).read_text(encoding="utf-8"))
    inv=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
    print("PASS Stage5 discovery, no approved methods:",check(doc,inv))
