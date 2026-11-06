#!/usr/bin/env python3
"""Stage18 batch15: pinned MSUD-015 source projection, graph and mutation gates."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "docs/diagnostics/STAGE18_ERMAK_MSUD015_BATCH15_2026-11-06.json").read_text(encoding="utf-8"))
PACK = json.loads((ROOT / "content-packs/electric/ermak/diagnostics/recommended/diagnostics-03.pack.json").read_text(encoding="utf-8"))
IDS = ["ER-DIAG-045", "ER-DIAG-046", "ER-DIAG-047", "ER-DIAG-048"]
SRC = {e["id"]: e["sourceObject"]["object"] for e in PACK["entries"] if e["id"] in IDS}
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "c3a22c62db42308eb4b7ee44ff2da02f47686625"
W = {"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
FIELDS = {"title":"title","symptom":"symptom","sourceObjectStatus":"status","sourceObjectApplicability":"applicability","sourceObjectSystemIds":"systemIds","sourceObjectEquipmentRefs":"equipmentRefs","sourceObjectSourceRefs":"sourceRefs"}
HAZARDS = {"ER-DIAG-045":"LATE_MSUD015_AXLE_CONTROL_CHANNEL_UNAVAILABLE","ER-DIAG-046":"LATE_SINGLE_AXLE_TRACTION_DEFICIT","ER-DIAG-047":"LATE_AXLE_CURRENT_TORQUE_ASYMMETRY","ER-DIAG-048":"LATE_REPEATED_SINGLE_AXLE_WHEELSLIP"}
def require(v,msg):
    if not v: raise AssertionError(msg)

def check(c):
    id_ = c["originalId"]
    require(id_ in IDS and c["scenarioId"] == "ermak.diag."+id_, "id")
    src = SRC[id_]
    for field, key in FIELDS.items(): require(c[field] == src[key], "donor "+field)
    require(c["families"] == src["applicability"]["families"], "families")
    require(c["profileApplicability"] == src["applicability"]["profiles"], "profile")
    require(c["lateProfileRule"] == src["applicability"]["lateProfiles"], "late rule")
    require(c["sourceObjectStatus"] == "EVOLUTION_CONFIRMED", "donor status")
    require(c["hazardCategory"] == HAZARDS[id_], "hazard separation")
    require(c["authoringProfileId"] == "ermak-msud-015-axle-control-research-only", "authoring")
    require(c["earlyMsud"] == "MSUD-N_NOT_EQUIVALENT" and c["lateMsud"] == "MSUD-015_PROFILE_SPECIFIC", "early/late")
    require(c["exactInstalledVariant"] == "UNKNOWN" and c["unknownVariantDisposition"] == "BLOCKED", "profile blocked")
    require(c["publicationStatus"] == "CANDIDATE" and c["runtimeImport"] is False, "publication")
    for k in ("executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):
        require(c[k] is False, k)
    require(c["warningGate"] == W, "warning")
    require(c["safePolicy"] == {"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True}, "safe policy")
    require(c["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "device")
    require(len(c["mustRemainDistinctFrom"]) == len(set(c["mustRemainDistinctFrom"])) == 3 and id_ not in c["mustRemainDistinctFrom"], "isolation")
    require([x["resolution"] for x in c["sourceConflicts"]] == ["NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED"], "conflicts")
    r=c["sourceRecords"]
    require(set(r) == ({"donor","manufacturer","tmh","technical","operations","safety"} | ({"unresolved"} if id_ != "ER-DIAG-048" else set())), "source set")
    require(r["donor"]["commit"] == PIN and r["donor"]["blobSha"] == BLOB and r["donor"]["objectId"] == id_, "pin")
    require(r["donor"]["rawGzipIndependentlyDecoded"] is False, "binary limitation")
    require(r["manufacturer"]["exactInstalledVariantVerified"] is False, "manufacturer variant")
    require(all(x["currentOperatingAuthority"] is False for x in r.values()), "source authority")
    require(r["technical"]["sourceKind"] == "TECHNICAL_SECONDARY_2022" and r["operations"]["sourceKind"] == "TECHNICAL_ANALYSIS_2026", "source kind")
    require(r["safety"]["sourceKind"] == "ANALYTICAL_SAFETY_GATE_NOT_NORMATIVE", "safety source")
    require(c["independentCrosschecks"]["donorDirectGzip"] == "UNAVAILABLE_FOR_BINARY_DECODING", "raw donor status")
    for mode, count in (("SHORT",6),("DETAILED",12)):
        graph = c["versions"][mode]
        require(graph["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and graph["operatingInstructionsIncluded"] is False, "graph gate")
        by = {n["id"]:n for n in graph["nodes"]}
        require(len(by) == len(graph["nodes"]) == count and graph["startNodeId"] == "q-active", "nodes")
        seen=set()
        def visit(nid):
            require(nid in by, "edge missing")
            if nid in seen: return
            seen.add(nid)
            n=by[nid]
            require(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False, "action")
            require(set(n["sourceRefs"]).issubset(set(r)), "source reference")
            if n["type"] == "QUESTION":
                require(set(n["responses"]) == {"YES","NO","UNKNOWN"} and n["responses"]["UNKNOWN"] == "stop-unknown", "tri-state")
                for nxt in n["responses"].values(): visit(nxt)
            else:
                require(n["type"] in ("STOP","OBSERVATION_REPORT") and n["responses"] == {}, "leaf")
        visit(graph["startNodeId"])
        require(len(seen) == count, "unreachable")
        require(by["q-active"]["responses"]["YES"] == "stop-active", "active event")
        if mode == "DETAILED":
            require(by["q-profile"]["responses"]["NO"] == "stop-profile", "profile")
            for q in ("q-evidence","q-separation","q-provenance"):
                require(by[q]["responses"]["NO"] == "stop-unverified", "no evidence")
    ext=c["informationExtensions"]
    require(len(ext) == len(set(x["id"] for x in ext)) == 5, "extension IDs")
    require([x["version"] for x in ext] == ["SHORT","SHORT","DETAILED","DETAILED","DETAILED"], "extension versions")
    require([x["sourceRefs"] for x in ext] == [["donor"],["manufacturer"],["tmh"],["technical"],["operations"]], "extension sources")
    for x in ext:
        require(x["id"].startswith(id_+"-INFO-") and x["locator"] and x["text"], "extension")
        require(x["visibility"] == W and x["warningRequired"] is True, "extension warning")
        require(x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"] == [], "extension action")
        require(x["applicability"] == {"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False}, "extension profile")

def negative(c):
    paths=[
        (["publicationStatus"],"ACTIVE"),(["runtimeImport"],True),(["executable"],True),
        (["actionAuthorityGranted"],True),(["sourceAuthorityVerified"],True),
        (["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
        (["exactInstalledVariant"],"MSUD-015"),(["unknownVariantDisposition"],"ALLOWED"),
        (["earlyMsud"],"MSUD-N"),(["lateMsud"],"MSUD-N"),(["authoringProfileId"],"ermak-general"),
        (["hazardCategory"],"OTHER"),(["title"],"WRONG"),(["symptom"],"WRONG"),
        (["sourceObjectStatus"],"BASE_CONFIRMED"),(["sourceObjectApplicability"],{}),(["sourceObjectSystemIds"],[]),
        (["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
        (["families"],["3ES5K"]),(["profileApplicability"],["base_early"]),
        (["lateProfileRule"],"APPLICABLE"),(["sourceRecords","donor","commit"],"WRONG"),
        (["sourceRecords","donor","blobSha"],"WRONG"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
        (["sourceRecords","manufacturer","currentOperatingAuthority"],True),
        (["sourceRecords","manufacturer","exactInstalledVariantVerified"],True),
        (["sourceRecords","technical","sourceKind"],"NORMATIVE"),
        (["sourceRecords","operations","currentOperatingAuthority"],True),
        (["sourceRecords","safety","sourceKind"],"NORMATIVE"),
        (["warningGate","warningReadToEnd"],False),(["warningGate","warningGrantsActionAuthority"],True),
        (["safePolicy","operationsAllowed"],["switch"]),(["safePolicy","onlyPreviouslyRecorded"],False),
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
        (["deviceQA"],"PASS"),(["sourceConflicts",2,"resolution"],"SOURCE_AUTHORITY_GRANTED"),
        (["mustRemainDistinctFrom"],["ER-DIAG-045"]),
    ]
    for i,(path,value) in enumerate(paths):
        obj=copy.deepcopy(c); t=obj
        for key in path[:-1]: t=t[key]
        t[path[-1]]=value
        try: check(obj)
        except (AssertionError,KeyError): continue
        raise AssertionError("negative escaped: "+c["originalId"]+" #"+str(i))
    return len(paths)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--negative",action="store_true");args=ap.parse_args()
    l=DATA["ledger"]
    require(l["scenarioIds"] == IDS and [c["originalId"] for c in DATA["candidates"]] == IDS, "membership")
    require(l["donorPinnedSha"] == PIN and l["donorGzipBlobSha"] == BLOB, "ledger")
    require(PACK["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"] == BLOB, "pack identity")
    require(l["status"] == "CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False, "ledger gate")
    for c in DATA["candidates"]: check(c)
    require(len({c["hazardCategory"] for c in DATA["candidates"]}) == 4, "distinct hazards")
    require(len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in DATA["candidates"]}) == 4, "distinct questions")
    print("STAGE18_BATCH15_PASS",len(IDS),"SHORT 6 DETAILED 12 extensions 5")
    if args.negative: print("STAGE18_BATCH15_NEGATIVE_PASS",sum(negative(c) for c in DATA["candidates"]))
if __name__=="__main__": main()
