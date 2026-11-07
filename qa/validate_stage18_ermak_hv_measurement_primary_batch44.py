#!/usr/bin/env python3
"""Stage18 batch44: pinned donor identity, two independent HV candidates and fail-closed negative mutations."""
import argparse
import copy
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = json.loads((ROOT / "docs/diagnostics/STAGE18_ERMAK_HV_MEASUREMENT_PRIMARY_BATCH44_2026-11-07.json").read_text(encoding="utf-8"))
PACK = json.loads((ROOT / "content-packs/electric/ermak/diagnostics/recommended/diagnostics-07.pack.json").read_text(encoding="utf-8"))
ORIG = {e["id"]: e["sourceObject"]["object"] for e in PACK["entries"]}
FIELDS = [("originalId","id"),("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")]
IDS = ["ER-DIAG-129","ER-DIAG-130"]

def req(ok, message):
    if not ok:
        raise AssertionError(message)

def check(c):
    cid = c["originalId"]
    req(cid in IDS, "unrecognized candidate")
    o = ORIG[cid]
    for field, source_field in FIELDS:
        req(c[field] == o[source_field], "donor identity " + field)
    req(c["sourceObjectStatus"] == "BASE_CONFIRMED", "source status")
    req(c["sourceObjectApplicability"]["variantSelectionRequired"] is False, "variant selection")
    req(c["profileApplicability"] == ["base_early"] and c["lateProfileRule"] == "PROFILE_SOURCE_REQUIRED", "profile applicability")
    for key in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):
        req(c[key] is False, "blocked flag " + key)
    req(c["publicationStatus"] == "CANDIDATE" and c["exactInstalledVariant"] == "UNKNOWN" and c["unknownVariantDisposition"] == "BLOCKED", "candidate")
    req(c["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "device QA")
    req(c["warningGate"] == {"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}, "warning")
    req(c["safePolicy"] == {"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True}, "safety")
    sources = c["sourceRecords"]
    expected = {"donor","re1","re4","rule996","rule2580","safety",("re5" if cid == IDS[0] else "re2")}
    req(set(sources) == expected, "source records")
    donor = sources["donor"]
    req(donor["commit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff" and donor["blobSha"] == "c3a22c62db42308eb4b7ee44ff2da02f47686625", "pinned source")
    req(donor["objectId"] == cid and donor["rawGzipIndependentlyDecoded"] is False, "raw parity")
    req(all(s["currentOperatingAuthority"] is False for s in sources.values()), "source authority")
    req(len(c["sourceConflicts"]) == 6 and all(x["resolution"] in ("NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED") for x in c["sourceConflicts"]), "conflict dispositions")
    req(len(c["mustRemainDistinctFrom"]) >= 6 and (IDS[1] if cid == IDS[0] else IDS[0]) in c["mustRemainDistinctFrom"], "separation")
    for mode, count in (("SHORT",8),("DETAILED",12)):
        graph = c["versions"][mode]
        nodes = graph["nodes"]
        mapping = {node["id"]:node for node in nodes}
        req(len(nodes) == count and len(mapping) == count and graph["startNodeId"] == "q-active", "graph count")
        req(graph["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and graph["operatingInstructionsIncluded"] is False, "graph gate")
        visited, stack = set(), [graph["startNodeId"]]
        while stack:
            key = stack.pop()
            if key in visited:
                continue
            req(key in mapping, "dangling node")
            visited.add(key)
            node = mapping[key]
            req(node["recordedOnly"] is True and node["operationRequested"] is False and node["causeConfirmed"] is False, "node safety")
            req(node["sourceRefs"] and all(x in sources for x in node["sourceRefs"]), "node provenance")
            if node["type"] == "QUESTION":
                req(set(node["responses"]) == {"YES","NO","UNKNOWN"} and node["responses"]["UNKNOWN"] == "stop-unknown", "tristate")
                stack.extend(node["responses"].values())
            else:
                req(node["type"] in ("STOP","OBSERVATION_REPORT") and node["responses"] == {}, "terminal")
        req(len(visited) == count, "unreachable nodes")
        req(mapping["q-active"]["responses"] == {"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"}, "active hazard")
        req(mapping["q-profile"]["responses"]["NO"] == "stop-profile" and mapping["q-symptom"]["responses"]["NO"] == "stop-mismatch", "profile/mismatch")
        req(mapping["report-match"]["type"] == "OBSERVATION_REPORT" and "НЕ ИНСТРУКЦИЯ" in mapping["report-match"]["text"], "research only")
        if mode == "DETAILED":
            for key in ("q-evidence","q-mode","q-provenance"):
                req(mapping[key]["responses"]["NO"] == "stop-unverified", "unverified stop")
    extensions = c["informationExtensions"]
    req(len(extensions) == 5 and [x["version"] for x in extensions] == ["SHORT","SHORT","DETAILED","DETAILED","DETAILED"], "extensions")
    req(len({x["id"] for x in extensions}) == 5, "extension identity")
    for x in extensions:
        req(x["visibility"] == c["warningGate"] and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"] == [], "extension gate")
        req(x["sourceRefs"] and all(k in sources for k in x["sourceRefs"]), "extension sources")
        req(x["applicability"] == {"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False}, "extension profile")
    req(len(c["independentCrosschecks"]) == 5 and all(x["verifiedAt"] == "2026-11-07" for x in c["independentCrosschecks"]), "crosschecks")
    req(any(x["confidence"] == "UNVERIFIED_NORMATIVE_REFERENCE" for x in c["independentCrosschecks"]), "normative uncertainty")

def negative(c):
    cases = [
      (["publicationStatus"],"PUBLISHED"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),
      (["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
      (["exactInstalledVariant"],"KNOWN"),(["unknownVariantDisposition"],"ALLOWED"),
      (["sourceObjectStatus"],"PROFILE_REQUIRED"),(["sourceObjectApplicability","variantSelectionRequired"],True),
      (["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
      (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),
      (["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
      (["safePolicy","operationsAllowed"],["test"]),(["safePolicy","onlyPreviouslyRecorded"],False),
      (["safePolicy","unknownMustStop"],False),(["safePolicy","activeFaultImmediateStop"],False),
      (["sourceRecords","re1","currentOperatingAuthority"],True),
      (["sourceRecords","rule996","currentOperatingAuthority"],True),
      (["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
      (["sourceRecords","donor","commit"],"wrong"),
      (["sourceRecords","donor","blobSha"],"wrong"),
      (["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),
      (["mustRemainDistinctFrom"],[]),
      (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),
      (["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),
      (["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
      (["versions","DETAILED","nodes",3,"responses","NO"],"report-match"),
      (["versions","DETAILED","nodes",4,"responses","NO"],"report-match"),
      (["versions","DETAILED","nodes",5,"responses","NO"],"report-match"),
      (["versions","DETAILED","nodes",5,"operationRequested"],True),
      (["versions","SHORT","nodes",0,"recordedOnly"],False),
      (["informationExtensions",0,"visibility","default"],"VISIBLE"),
      (["informationExtensions",0,"operationalSteps"],["repair"]),
      (["informationExtensions",4,"actionAuthorityGranted"],True),
      (["independentCrosschecks",0,"verifiedAt"],"2020-01-01")
    ]
    for index,(path,value) in enumerate(cases):
        mutant = copy.deepcopy(c)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            check(mutant)
        except (AssertionError,KeyError):
            continue
        raise AssertionError("negative escaped " + str(index))
    return len(cases)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative",action="store_true")
    args = parser.parse_args()
    req(DOC["ledger"]["scenarioIds"] == IDS and len(DOC["candidates"]) == 2, "membership")
    req(DOC["ledger"]["status"] == "CANDIDATE" and DOC["ledger"]["runtimeImport"] is False and DOC["ledger"]["actionAuthorityGranted"] is False, "ledger")
    for c in DOC["candidates"]:
        check(c)
    req(IDS[0] in DOC["candidates"][1]["mustRemainDistinctFrom"] and IDS[1] in DOC["candidates"][0]["mustRemainDistinctFrom"], "cross-scenario boundary")
    print("STAGE18_BATCH44_PASS scenarios=2 SHORT=16 DETAILED=24 EXTENSIONS=10")
    if args.negative:
        print("STAGE18_BATCH44_NEGATIVE_PASS",sum(negative(c) for c in DOC["candidates"]))

if __name__ == "__main__":
    main()
