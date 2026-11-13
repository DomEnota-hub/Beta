#!/usr/bin/env python3
"""Stage18 batch17 pinned early-MSUD traction diagnostics and fail-closed mutation QA."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "docs/diagnostics/STAGE18_ERMAK_TRACTION_BV_BATCH17_2026-11-06.json").read_text(encoding="utf-8"))
PACK = json.loads((ROOT / "content-packs/electric/ermak/diagnostics/recommended/diagnostics-03.pack.json").read_text(encoding="utf-8"))
IDS = ["ER-DIAG-054","ER-DIAG-055","ER-DIAG-056"]
SRC = {e["id"]:e["sourceObject"]["object"] for e in PACK["entries"] if e["id"] in IDS}
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "c3a22c62db42308eb4b7ee44ff2da02f47686625"
W = {"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
HAZARDS = {"ER-DIAG-054":"TRACTION_GROUP_CONTACTOR_NOT_ENGAGED","ER-DIAG-055":"SECTION_NO_LOAD_WITH_NORMAL_INDICATION","ER-DIAG-056":"BOTH_FAST_BREAKERS_NOT_ENGAGED_SECTION"}
FIELDS = {"title":"title","symptom":"symptom","sourceObjectStatus":"status","sourceObjectApplicability":"applicability","sourceObjectSystemIds":"systemIds","sourceObjectEquipmentRefs":"equipmentRefs","sourceObjectSourceRefs":"sourceRefs"}

def req(x, message):
    if not x: raise AssertionError(message)

def check(c):
    ident=c["originalId"]
    req(ident in IDS and c["scenarioId"]=="ermak.diag."+ident,"identity")
    source=SRC[ident]
    for dest, key in FIELDS.items(): req(c[dest]==source[key],"donor "+dest)
    req(c["families"]==source["applicability"]["families"] and c["profileApplicability"]==source["applicability"]["profiles"] and c["lateProfileRule"]==source["applicability"]["lateProfiles"],"profile exact")
    req(c["sourceObjectStatus"]=="BASE_CONFIRMED" and c["authoringProfileId"]=="ermak-msud-n-early-traction-research-only","authoring")
    req(c["earlyMsud"]=="MSUD-N_PROFILE_DEPENDENT" and c["lateMsud"]=="MSUD-015_NOT_EQUIVALENT","msud separation")
    req(c["hazardCategory"]==HAZARDS[ident],"hazard identity")
    req(c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","variant")
    req(c["publicationStatus"]=="CANDIDATE" and c["runtimeImport"] is False,"publication")
    for key in ("executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):
        req(c[key] is False,key)
    req(c["warningGate"]==W,"warning")
    req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True},"policy")
    req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
    req(len(c["mustRemainDistinctFrom"])==len(set(c["mustRemainDistinctFrom"]))==3 and ident not in c["mustRemainDistinctFrom"],"separation")
    req([x["resolution"] for x in c["sourceConflicts"]]==["NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED"],"conflicts")
    refs=c["sourceRecords"]
    req(set(refs)=={"donor","manufacturer","normative","memo","practice","safety"},"sources")
    req(refs["donor"]["commit"]==PIN and refs["donor"]["blobSha"]==BLOB and refs["donor"]["objectId"]==ident,"pinned")
    req(refs["donor"]["rawGzipIndependentlyDecoded"] is False,"binary status")
    req(refs["manufacturer"]["sourceKind"]=="MANUFACTURER_ARCHIVAL_PUBLIC_2007","manufacturer age")
    req(refs["normative"]["status"]=="CURRENT_COMPLETENESS_UNKNOWN","normative not cleared")
    req(refs["memo"]["sourceKind"]=="HISTORICAL_TRAINING_PUBLIC" and refs["practice"]["status"]=="UNRESOLVED_NO_AUTHORITY","historical")
    req(refs["safety"]["sourceKind"]=="ANALYTICAL_SAFETY_GATE_NOT_NORMATIVE","safety source")
    req(all(x["currentOperatingAuthority"] is False for x in refs.values()),"authority")
    for mode,count in (("SHORT",6),("DETAILED",12)):
        g=c["versions"][mode]
        req(g["startNodeId"]=="q-active" and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph gates")
        nodes={n["id"]:n for n in g["nodes"]}
        req(len(nodes)==len(g["nodes"])==count,"node count/unique")
        seen=set()
        def walk(k):
            req(k in nodes,"dangling edge")
            if k in seen:return
            seen.add(k)
            node=nodes[k]
            req(node["recordedOnly"] is True and node["operationRequested"] is False and node["causeConfirmed"] is False,"no operations")
            req(set(node["sourceRefs"]).issubset(refs),"source refs")
            if node["type"]=="QUESTION":
                req(set(node["responses"])=={"YES","NO","UNKNOWN"} and node["responses"]["UNKNOWN"]=="stop-unknown","tri-state stop")
                for dest in node["responses"].values():walk(dest)
            else:req(node["type"] in ("STOP","OBSERVATION_REPORT") and node["responses"]=={},"leaf")
        walk(g["startNodeId"])
        req(len(seen)==count,"unreachable")
        req(nodes["q-active"]["responses"]["YES"]=="stop-active","active stop")
        req(nodes["q-symptom"]["responses"]["NO"]=="stop-mismatch","symptom mismatch")
        if mode=="DETAILED":
            req(nodes["q-profile"]["responses"]["NO"]=="stop-profile","profile block")
            for key in ("q-evidence","q-separation","q-provenance"):
                req(nodes[key]["responses"]["NO"]=="stop-unverified","evidence block")
    ex=c["informationExtensions"]
    req(len(ex)==len(set(x["id"] for x in ex))==5,"extensions")
    req([x["version"] for x in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension modes")
    req([x["sourceRefs"] for x in ex]==[["donor"],["manufacturer"],["memo","practice"],["normative"],["safety","manufacturer"]],"extension source categories")
    for x in ex:
        req(x["id"].startswith(ident+"-INFO-") and x["text"] and x["locator"],"extension identity")
        req(x["visibility"]==W and x["warningRequired"] is True,"extension warning")
        req(x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension actions")
        req(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension applicability")
    req(len(c["independentCrosschecks"])==3 and all(x["verifiedAt"]=="2026-11-06" for x in c["independentCrosschecks"]),"crosschecks")

def negative(c):
    changes=[
(["publicationStatus"],"ACTIVE"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),
(["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
(["exactInstalledVariant"],"MSUD-N"),(["unknownVariantDisposition"],"ALLOWED"),
(["authoringProfileId"],"ermak-all"),(["earlyMsud"],"MSUD-015"),(["lateMsud"],"MSUD-N"),
(["hazardCategory"],"OTHER"),(["title"],"WRONG"),(["symptom"],"WRONG"),(["sourceObjectStatus"],"EVOLUTION_CONFIRMED"),
(["sourceObjectApplicability"],{}),(["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
(["families"],["2ES5K"]),(["profileApplicability"],["msud_015_extended"]),(["lateProfileRule"],"AS_LISTED"),
(["sourceRecords","donor","commit"],"BAD"),(["sourceRecords","donor","blobSha"],"BAD"),
(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
(["sourceRecords","manufacturer","currentOperatingAuthority"],True),
(["sourceRecords","manufacturer","sourceKind"],"MODERN_NORMATIVE"),
(["sourceRecords","normative","status"],"VERIFIED_CURRENT"),
(["sourceRecords","normative","currentOperatingAuthority"],True),
(["sourceRecords","memo","sourceKind"],"NORMATIVE"),
(["sourceRecords","practice","status"],"VERIFIED"),
(["sourceRecords","safety","sourceKind"],"NORMATIVE"),
(["warningGate","warningReadToEnd"],False),(["warningGate","warningGrantsActionAuthority"],True),
(["safePolicy","operationsAllowed"],["reset"]),(["safePolicy","onlyPreviouslyRecorded"],False),
(["safePolicy","activeFaultImmediateStop"],False),
(["versions","SHORT","nodes",0,"responses","YES"],"report-match"),
(["versions","SHORT","nodes",0,"responses","UNKNOWN"],"report-match"),
(["versions","DETAILED","nodes",1,"responses","NO"],"q-symptom"),
(["versions","DETAILED","nodes",3,"responses","NO"],"q-separation"),
(["versions","DETAILED","nodes",4,"responses","UNKNOWN"],"q-provenance"),
(["versions","DETAILED","nodes",5,"operationRequested"],True),
(["informationExtensions",0,"sourceRefs"],["unverified"]),
(["informationExtensions",0,"warningRequired"],False),
(["informationExtensions",0,"operationalSteps"],["test"]),
(["informationExtensions",0,"visibility","warningAcknowledged"],False),
(["informationExtensions",4,"actionAuthorityGranted"],True),
(["deviceQA"],"PASS"),
(["sourceConflicts",2,"resolution"],"SOURCE_AUTHORITY_GRANTED"),
(["mustRemainDistinctFrom"],[c["originalId"]])
    ]
    for i,(path,value) in enumerate(changes):
        t=copy.deepcopy(c);cur=t
        for k in path[:-1]:cur=cur[k]
        cur[path[-1]]=value
        try:check(t)
        except (AssertionError,KeyError):continue
        raise AssertionError("negative escaped: "+c["originalId"]+" #"+str(i))
    return len(changes)

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--negative",action="store_true");args=parser.parse_args()
    l=DATA["ledger"]
    req(l["scenarioIds"]==IDS and [c["originalId"] for c in DATA["candidates"]]==IDS,"batch membership")
    req(l["donorPinnedSha"]==PIN and l["donorGzipBlobSha"]==BLOB,"ledger pin")
    req(PACK["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]==BLOB,"pack pin")
    req(l["status"]=="CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False,"ledger gate")
    for c in DATA["candidates"]:check(c)
    req(len({c["hazardCategory"] for c in DATA["candidates"]})==3,"distinct hazards")
    req(len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in DATA["candidates"]})==3,"distinct evidence questions")
    print("STAGE18_BATCH17_PASS 3 SHORT=6 DETAILED=12 EXTENSIONS=5")
    if args.negative:print("STAGE18_BATCH17_NEGATIVE_PASS",sum(negative(c) for c in DATA["candidates"]))
if __name__=="__main__":main()
