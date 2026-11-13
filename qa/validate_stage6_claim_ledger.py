#!/usr/bin/env python3
"""Stage 6 four separately located archival claims; cannot become current authority."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"docs/diagnostics/STAGE6_HISTORICAL_CLAIM_LEDGER_2026-11-04.json"
PATHS={
"vl80s.diag.gv-no-open":ROOT/"content-packs/electric/vl80s/diagnostics/authoring/stage6-gv-no-open.research.json",
"vl80s.diag.ekg-slow-transition":ROOT/"content-packs/electric/vl80s/diagnostics/authoring/stage6-ekg-slow-transition.research.json",
}
EXPECTED={
"S6-GV-1990-01":("vl80s.diag.gv-no-open","manual1990"),
"S6-GV-1990-02":("vl80s.diag.gv-no-open","manual1990"),
"S6-EKG-1990-01":("vl80s.diag.ekg-slow-transition","manual1990"),
"S6-EKG-2005-01":("vl80s.diag.ekg-slow-transition","scheme2005"),
}
def require(value,message):
 if not value: raise ValueError(message)
def validate(d,records):
 require(d["schemaVersion"]=="diagnostic-stage6-historical-claim-ledger/1" and
         d["stage"]=="6/51" and
         d["status"]=="SOURCE_TEXT_REVIEWED_CURRENT_APPLICABILITY_AND_ACTION_AUTHORITY_UNVERIFIED",
         "source/edition verification overclaimed")
 require(d["stageTechnicalAcceptance"]=="BLOCKED" and
         d["runtimeImport"] is False and d["actionAuthorityGranted"] is False,
         "unreviewed sources promoted")
 require(len(d["claims"])==len(EXPECTED) and
         {x["claimId"] for x in d["claims"]}==set(EXPECTED),
         "missing or duplicate independent claims")
 for src in d["corroboratingSources"].values():
  require(src["sourceTextLocated"] is True and src["publishedYear"] in {1990,2005}
          and src["url"].startswith("https://") and bool(src["verifiedLocator"]),
          "historical bibliography unlocatable")
  require(src["completeModernEditionValidated"] is False and
          src["exactInstalledEquipmentVerified"] is False and
          src["currentActionAuthorityVerified"] is False and
          src["operationalProcedureImported"] is False,
          "bibliography improperly grants action")
 observed=set()
 for c in d["claims"]:
  scenario,source=EXPECTED[c["claimId"]]
  require(c["scenarioId"]==scenario and c["sourceId"]==source,
          "claim/source or canonical scenario changed")
  require(bool(c["exactSourceLocator"]) and bool(c["technicalHypothesisSummary"])
          and bool(c["sourceScopeLimitation"]),
          "historical claim lacks location or scope")
  require(c["sourceClaimReview"]=="HISTORICAL_TEXT_LOCATION_VERIFIED" and
          c["currentOperationalAuthority"]=="NOT_ESTABLISHED" and
          c["installedEquipmentApplicability"]=="NOT_ESTABLISHED" and
          c["causeAtThisLocomotive"]=="NOT_ESTABLISHED" and
          c["repairProcedure"]=="EXCLUDED_NO_ACTION_AUTHORITY",
          "technical assertion upgraded without verification")
  rec=records[scenario]
  alts={a["approachId"]:a for a in rec["versions"]["DETAILED"]["extendedRoutes"]}
  require(c["approachId"] in alts and alts[c["approachId"]]["claimId"]==c["claimId"]
          and alts[c["approachId"]]["sourceId"]==source
          and alts[c["approachId"]]["sourcePointer"]==c["exactSourceLocator"],
          "historical claim to graph provenance missing")
  require(c["claimId"] not in observed,"duplicate claim identity")
  observed.add(c["claimId"])
 require(len(d["verifiedContextCautions"])>=4,"equipment applicability warnings omitted")
 return len(observed)
if __name__=="__main__":
 claims=json.loads(LEDGER.read_text(encoding="utf-8"))
 drafts={key:json.loads(path.read_text(encoding="utf-8")) for key,path in PATHS.items()}
 print("PASS Stage6 historical source-to-graph claim mapping:",validate(claims,drafts))
