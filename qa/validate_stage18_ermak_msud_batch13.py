#!/usr/bin/env python3
"""Stage18 batch13: exact pinned MSUD-Н projections, graph safety, negative mutations."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "docs/diagnostics/STAGE18_ERMAK_MSUD_BATCH13_2026-11-06.json").read_text(encoding="utf-8"))
PACKS = [json.loads((ROOT / ("content-packs/electric/ermak/diagnostics/recommended/diagnostics-%02d.pack.json" % i)).read_text(encoding="utf-8")) for i in (2, 3)]
IDS = ["ER-DIAG-040", "ER-DIAG-041", "ER-DIAG-042"]
SRC = {e["id"]: e["sourceObject"]["object"] for pack in PACKS for e in pack["entries"] if e["id"] in IDS}
BLOB = "c3a22c62db42308eb4b7ee44ff2da02f47686625"
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
W = {"default": "HIDDEN", "warningReadToEnd": True, "warningAcknowledged": True, "warningGrantsActionAuthority": False}
FIELDS = {"title":"title","symptom":"symptom","sourceObjectStatus":"status","sourceObjectApplicability":"applicability","sourceObjectSystemIds":"systemIds","sourceObjectEquipmentRefs":"equipmentRefs","sourceObjectSourceRefs":"sourceRefs"}
SOURCES = {"donor","manufacturer","memo","practice","variant","safety"}

def require(ok, label):
    if not ok:
        raise AssertionError(label)

def check(c):
    id_ = c["originalId"]
    require(id_ in IDS and c["scenarioId"] == "ermak.diag." + id_, "id")
    src = SRC[id_]
    for field, key in FIELDS.items():
        require(c[field] == src[key], "pinned " + field)
    require(c["families"] == src["applicability"]["families"], "families")
    require(c["profileApplicability"] == src["applicability"]["profiles"], "profiles")
    require(c["lateProfileRule"] == src["applicability"]["lateProfiles"], "late")
    require(c["sourceObjectStatus"] == "BASE_CONFIRMED", "donor status")
    require(c["hazardCategory"] == {"ER-DIAG-040":"TRACTION_CURRENT_TRANSIENT","ER-DIAG-041":"INTERSECTION_MSUD_COMMUNICATION_LOSS","ER-DIAG-042":"SINGLE_SECTION_SPEED_INDICATION_LOSS"}[id_], "distinct scope")
    require(c["publicationStatus"] == "CANDIDATE" and c["runtimeImport"] is False, "publication")
    for key in ("executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):
        require(c[key] is False, key)
    require(c["exactInstalledVariant"] == "UNKNOWN" and c["unknownVariantDisposition"] == "BLOCKED", "fail closed")
    require(c["earlyMsud"] == "MSUD-N_ARCHIVAL_ONLY" and c["lateMsud"] == "MSUD-015_NOT_EQUIVALENT", "MSUD separation")
    require(c["authoringProfileId"] == "ermak-msud-n-archival-research-only", "profile")
    require(c["schemaVersion"] == "ermak-stage18-msud-batch13-research/1", "schema")
    require(c["sourceRecords"]["donor"]["projectionPath"].endswith("diagnostics-02.pack.json" if id_ == "ER-DIAG-040" else "diagnostics-03.pack.json"), "projection path")
    require(id_ in c["informationExtensions"][0]["locator"], "extension donor locator")
    require(c["warningGate"] == W, "warning")
    require(c["safePolicy"] == {"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True}, "safe policy")
    require(c["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "device QA")
    require(len(c["mustRemainDistinctFrom"]) == 3 and id_ not in c["mustRemainDistinctFrom"] and len(set(c["mustRemainDistinctFrom"])) == 3, "scenario isolation")
    require([x["resolution"] for x in c["sourceConflicts"]] == ["NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED"], "conflicts")
    r = c["sourceRecords"]
    require(set(r) == SOURCES, "sources")
    require(r["donor"]["commit"] == PIN and r["donor"]["blobSha"] == BLOB and r["donor"]["objectId"] == id_, "donor pin")
    require(r["donor"]["rawGzipIndependentlyDecoded"] is False, "source limitation")
    require(all(x["currentOperatingAuthority"] is False for x in r.values()), "source authority")
    require(r["manufacturer"]["exactInstalledVariantVerified"] is False, "variant source")
    require(r["memo"]["status"] == "HISTORICAL_NOT_OPERATIONAL" and r["practice"]["status"] == "UNVERIFIED_CONTEXT_ONLY", "historical source status")
    require(r["safety"]["sourceKind"] == "ANALYTICAL_SAFETY_GATE_NOT_NORMATIVE", "no invented norm")
    for mode, size in (("SHORT", 6), ("DETAILED", 12)):
        graph = c["versions"][mode]
        nodes = graph["nodes"]
        by = {x["id"]: x for x in nodes}
        require(len(nodes) == len(by) == size, "graph size")
        require(graph["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and graph["operatingInstructionsIncluded"] is False, "graph authority")
        require(graph["startNodeId"] == "q-active", "graph start")
        require(by["q-active"]["responses"] == {"YES":"stop-active","NO":"q-symptom" if mode == "SHORT" else "q-profile","UNKNOWN":"stop-unknown"}, "live fault stop")
        require(by["q-symptom"]["responses"]["NO"] == "stop-mismatch", "symptom isolation")
        if mode == "DETAILED":
            require(by["q-profile"]["responses"]["NO"] == "stop-profile", "unknown profile")
            for q in ("q-independent","q-scope","q-record-source"):
                require(by[q]["responses"]["NO"] == "stop-unverified", "unverified branch")
        seen = set()
        todo = [graph["startNodeId"]]
        while todo:
            k = todo.pop()
            require(k in by, "dangling")
            if k in seen:
                continue
            seen.add(k)
            n = by[k]
            require(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False, "unsafe node")
            require(n["sourceRefs"] and set(n["sourceRefs"]) <= SOURCES, "node provenance")
            if n["type"] == "QUESTION":
                require(set(n["responses"]) == {"YES","NO","UNKNOWN"}, "tri-state")
                require(by[n["responses"]["UNKNOWN"]]["type"] == "STOP", "UNKNOWN bypass")
                todo.extend(n["responses"].values())
            else:
                require(n["type"] in ("STOP","OBSERVATION_REPORT") and n["responses"] == {}, "leaf")
        require(seen == set(by), "unreachable nodes")
    ext = c["informationExtensions"]
    require(len(ext) == len({x["id"] for x in ext}) == 5, "extensions")
    require([x["version"] for x in ext] == ["SHORT","SHORT","DETAILED","DETAILED","DETAILED"], "extension modes")
    require([x["sourceRefs"][0] for x in ext] == ["donor","manufacturer","memo","practice","variant"], "extension provenance")
    for x in ext:
        require(x["id"].startswith(id_ + "-INFO-") and x["text"] and x["locator"], "extension identity")
        require(len(x["sourceRefs"]) == 1 and x["sourceRefs"][0] in SOURCES, "extension source")
        require(x["visibility"] == W and x["warningRequired"] is True, "extension warning")
        require(x["actionAuthorityGranted"] is False and x["executable"] is False and x["operationalSteps"] == [], "extension operations")
        require(x["applicability"] == {"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False}, "extension profile")

def negative(c):
    def setv(path, value):
        def apply(obj):
            target = obj
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
        return apply
    changes = [
        setv(["publicationStatus"],"ACTIVE"),
        setv(["runtimeImport"],True),
        setv(["executable"],True),
        setv(["actionAuthorityGranted"],True),
        setv(["sourceAuthorityVerified"],True),
        setv(["exactInstalledVariantConfirmed"],True),
        setv(["substantiveSafetyReviewed"],True),
        setv(["exactInstalledVariant"],"MSUD-015"),
        setv(["unknownVariantDisposition"],"ALLOWED"),
        setv(["earlyMsud"],"MSUD-015"),
        setv(["lateMsud"],"MSUD-N"),
        setv(["authoringProfileId"],"ermak-general"),
        setv(["hazardCategory"],"OTHER"),
        setv(["title"],"WRONG"),
        setv(["symptom"],"WRONG"),
        setv(["sourceObjectStatus"],"CURRENT_RULE_CONFIRMED"),
        setv(["sourceObjectSystemIds"],[]),
        setv(["sourceObjectEquipmentRefs"],[]),
        setv(["sourceObjectSourceRefs"],[]),
        setv(["families"],["3ES5K"]),
        setv(["profileApplicability"],["all_confirmed_profiles"]),
        setv(["lateProfileRule"],"APPLICABLE"),
        setv(["sourceRecords","donor","commit"],"BAD"),
        setv(["sourceRecords","donor","blobSha"],"BAD"),
        setv(["sourceRecords","donor","objectId"],"BAD"),
        setv(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
        setv(["sourceRecords","manufacturer","currentOperatingAuthority"],True),
        setv(["sourceRecords","manufacturer","exactInstalledVariantVerified"],True),
        setv(["sourceRecords","memo","status"],"CURRENT"),
        setv(["sourceRecords","practice","status"],"CURRENT"),
        setv(["sourceRecords","safety","sourceKind"],"NORMATIVE"),
        setv(["safePolicy","operationsAllowed"],["bypass_SAUT"]),
        setv(["safePolicy","onlyPreviouslyRecorded"],False),
        setv(["safePolicy","activeFaultImmediateStop"],False),
        setv(["warningGate","warningReadToEnd"],False),
        setv(["warningGate","warningGrantsActionAuthority"],True),
        setv(["versions","SHORT","nodes",0,"responses","YES"],"q-symptom"),
        setv(["versions","SHORT","nodes",0,"responses","UNKNOWN"],"q-symptom"),
        setv(["versions","DETAILED","nodes",0,"responses","YES"],"q-profile"),
        setv(["versions","DETAILED","nodes",1,"responses","NO"],"q-symptom"),
        setv(["versions","DETAILED","nodes",3,"responses","NO"],"q-scope"),
        setv(["versions","DETAILED","nodes",4,"responses","UNKNOWN"],"q-record-source"),
        setv(["versions","DETAILED","nodes",5,"operationRequested"],True),
        setv(["informationExtensions",0,"actionAuthorityGranted"],True),
        setv(["informationExtensions",0,"sourceRefs"],["UNKNOWN"]),
        setv(["informationExtensions",0,"warningRequired"],False),
        setv(["informationExtensions",0,"operationalSteps"],["switch"]),
        setv(["informationExtensions",0,"visibility","warningAcknowledged"],False),
        setv(["deviceQA"],"PASS"),
        setv(["sourceConflicts",2,"resolution"],"SOURCE_AUTHORITY_GRANTED"),
        setv(["mustRemainDistinctFrom"],["ER-DIAG-037"]),
    ]
    for i, mutate in enumerate(changes):
        candidate = copy.deepcopy(c)
        mutate(candidate)
        try:
            check(candidate)
        except (AssertionError, KeyError):
            continue
        raise AssertionError("negative mutation escaped %d" % i)
    return len(changes)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    ledger = DATA["ledger"]
    require(ledger["scenarioIds"] == IDS and len(DATA["candidates"]) == 3, "batch membership")
    require(ledger["donorPinnedSha"] == PIN and ledger["donorGzipBlobSha"] == BLOB, "ledger pin")
    require(all(p["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"] == BLOB for p in PACKS), "source blob")
    require(ledger["status"] == "CANDIDATE" and ledger["runtimeImport"] is False and ledger["actionAuthorityGranted"] is False, "ledger gates")
    require([c["originalId"] for c in DATA["candidates"]] == IDS, "order")
    for c in DATA["candidates"]:
        check(c)
    require(len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in DATA["candidates"]}) == 3, "independent scenario questions")
    require(len({c["hazardCategory"] for c in DATA["candidates"]}) == 3, "independent hazards")
    print("STAGE18_BATCH13_PASS:", ", ".join(IDS), "SHORT 6 / DETAILED 12 / 5 expansions each")
    if args.negative:
        count = sum(negative(c) for c in DATA["candidates"])
        print("STAGE18_BATCH13_NEGATIVE_PASS:", count)

if __name__ == "__main__":
    main()
