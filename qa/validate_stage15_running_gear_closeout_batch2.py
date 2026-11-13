#!/usr/bin/env python3
"""Stage15 VL80S running gear closeout: donor, source and negative fail-closed QA."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "docs/diagnostics/STAGE15_RUNNING_GEAR_CLOSEOUT_BATCH2_2026-11-05.json").read_text(encoding="utf-8"))
migration = json.loads((ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))
source = {s["id"]: s for s in migration["sourceObject"]["scenarios"]}
expected = ["traction-gear-noise","wheel-bearing-heat","wheel-flat-impact"]
ledger = pack["ledger"]
assert ledger["baseHead"] == "f63295e2582ccca8d171a6f289a2023c1a184d88"
assert ledger["donorPinnedSha"] == migration["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
assert ledger["donorSnapshotBlobSha"] == migration["sourceBlobSha"]
assert ledger["categorySourceCount"] == 8 and ledger["remainingCategoryIds"] == []
assert ledger["scenarioIds"] == ["vl80s.diag." + x for x in expected]
previous = json.loads((ROOT / "docs/diagnostics/STAGE15_RUNNING_GEAR_BATCH1_2026-11-05.json").read_text(encoding="utf-8"))
previous_ids = [c["originalId"] for c in previous["candidates"]]
assert set(previous_ids).isdisjoint(expected)
assert len(previous_ids) == 5
assert {s["id"] for s in source.values() if s["category"] == "Ходовая часть"} == set(expected) | set(previous_ids)
assert [c["originalId"] for c in pack["candidates"]] == expected
assert ledger["runtimeImport"] is False and ledger["actionAuthorityGranted"] is False
assert ledger["negativeMutationCount"] == 105

def check(c):
    s = source[c["originalId"]]
    assert c["scenarioId"] == "vl80s.diag." + s["id"]
    assert c["title"] == s["title"] and c["summary"] == s["summary"]
    assert c["category"] == s["category"] == "Ходовая часть"
    assert c["donorOriginLayer"] == s["originLayer"]
    assert c["donorQuestionCount"] == s["questionCount"]
    assert c["donorPinnedSha"] == migration["donorCommit"]
    assert c["donorOriginalQuestions"] is None and c["originalQuestionTextVerified"] is False
    assert c["authoringProfileId"] == "vl80s-general"
    assert c["exactInstalledVariant"] == "UNKNOWN" and c["unknownVariantDisposition"] == "BLOCKED"
    assert c["variantEvidence"]["disposition"] == "BLOCKED"
    assert len(c["canonicalBoundary"]) > 80 and len(c["sourceDiscrepancy"]) > 100
    assert c["publicationStatus"] == "CANDIDATE" and c["deviceQA"] == "NOT_RUN_DEFERRED"
    assert all(c[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified"))
    rec = c["sourceRecords"]
    assert set(rec) == {"donor","manual1990","textbook2006","currentRequirements"}
    assert rec["donor"]["commit"] == migration["donorCommit"]
    assert rec["donor"]["blobSha"] == migration["sourceBlobSha"]
    assert rec["donor"]["sourceMetadataSha"] == ledger["migrationBlobSha"]
    assert rec["donor"]["sourcePointer"] == "sourceObject.scenarios[id=" + s["id"] + "]"
    assert rec["donor"]["sourceProfileIds"] == s["applicableVariantIds"] == ["vl80s-general"]
    assert rec["donor"]["originalQuestionCount"] == s["questionCount"]
    assert rec["donor"]["originalQuestionTextVerified"] is False
    assert rec["donor"]["proceduresImported"] is False
    assert rec["manual1990"]["year"] == 1990 and len(rec["manual1990"]["verifiedLocators"]) >= 2
    assert rec["manual1990"]["currentOperatingAuthority"] is False
    assert rec["textbook2006"]["relevance"] == "NOT_VERIFIED_FOR_THIS_SPECIFIC_SYMPTOM"
    assert rec["textbook2006"]["verifiedLocators"] == []
    assert rec["currentRequirements"]["status"] == "UNKNOWN"
    assert rec["currentRequirements"]["exactSectionProceduresVerified"] is False
    assert rec["currentRequirements"]["actionAuthorityGranted"] is False
    assert c["extendedWarning"] == {"default":"HIDDEN","requiresReadToEnd":True,"requiresAcknowledgement":True,"consentResetsOnClose":True,"warningGrantsActionAuthority":False}
    safety = c["safety"]
    assert safety["observationOnly"] and safety["onlyPreviouslyRecorded"] and safety["unknownMustStop"]
    assert safety["triState"] == ["YES","NO","UNKNOWN"] and safety["operationsAllowed"] == []
    assert {"JUMPER","PROTECTION_BYPASS","HV_INTERVENTION","TEST_RESTART","LIVE_MEASUREMENT","REPAIR","ELECTRICAL_SWITCHING"} <= set(safety["prohibited"])
    assert all(safety[k] == "NOT_APPROVED" for k in ("roleGate","sourceGate","safetyGate"))
    for mode,count,qcount in (("SHORT",6,2),("DETAILED",12,8)):
        graph = c["versions"][mode]
        nodes = {n["id"]:n for n in graph["nodes"]}
        assert len(nodes) == len(graph["nodes"]) == count
        assert graph["startNodeId"] == "q1"
        assert sum(n["type"] == "QUESTION" for n in nodes.values()) == qcount
        seen,stack=set(),["q1"]
        while stack:
            k=stack.pop()
            assert k in nodes
            if k in seen: continue
            seen.add(k)
            n=nodes[k]
            assert n["recordedOnly"] is True
            assert n["operationRequested"] is False and n["causeConfirmed"] is False
            assert set(n["sourceRefs"]) == {"donor","manual1990"}
            if n["type"] == "QUESTION":
                assert n["text"].startswith("По ранее записанным сведениям:")
                assert set(n["responses"]) == {"YES","NO","UNKNOWN"}
                assert n["responses"]["UNKNOWN"] == "stop_unknown"
                stack.extend(n["responses"].values())
            else:
                assert n["type"] in ("STOP","OBSERVATION_REPORT")
                assert n["responses"] == {}
        assert len(seen) == count
        assert nodes["q1"]["responses"]["YES"] == "stop_danger"
        assert all(nodes[k]["type"] == "STOP" for k in ("stop_danger","stop_unknown","stop_unresolved"))
        assert nodes["report"]["type"] == "OBSERVATION_REPORT" and "НЕ" in nodes["report"]["text"]
    ex=c["informationExtensions"]
    assert len(ex)==len({x["id"] for x in ex})==len({x["text"] for x in ex})==5
    assert [x["version"] for x in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"]
    for x in ex:
        assert x["kind"]=="HISTORICAL_INFORMATION_ONLY"
        assert x["sourceRefs"]==["manual1990"]
        assert x["locator"] in rec["manual1990"]["verifiedLocators"]
        assert x["warningRequired"] is True and x["actionAuthorityGranted"] is False
    assert len(c["historicalEvidenceClaims"]) == 3
    assert all(x["proceduresImported"] is False for x in c["historicalEvidenceClaims"])

for c in pack["candidates"]: check(c)

def must_fail(mutated):
    try: check(mutated)
    except (AssertionError, KeyError, TypeError, ValueError): return
    raise AssertionError("Unsafe mutation passed: " + mutated["originalId"])

count=0
for c in pack["candidates"]:
    for mode in ("SHORT","DETAILED"):
        for i in range(len(c["versions"][mode]["nodes"])):
            x=copy.deepcopy(c);x["versions"][mode]["nodes"][i]["operationRequested"]=True
            must_fail(x);count+=1
    for i in range(5):
        x=copy.deepcopy(c);x["informationExtensions"][i]["actionAuthorityGranted"]=True
        must_fail(x);count+=1
    for i in range(5):
        x=copy.deepcopy(c);x["informationExtensions"][i]["warningRequired"]=False
        must_fail(x);count+=1
    for k in ("runtimeImport","executable","actionAuthorityGranted"):
        x=copy.deepcopy(c);x[k]=True
        must_fail(x);count+=1
    for k in ("roleGate","sourceGate","safetyGate"):
        x=copy.deepcopy(c);x["safety"][k]="APPROVED"
        must_fail(x);count+=1
    x=copy.deepcopy(c);x["safety"]["unknownMustStop"]=False
    must_fail(x);count+=1
assert count == 105, count
print("Stage15 CLOSEOUT PASS: 8/8 donor IDs, 3 new candidates, 54 nodes, 15 extensions, 105 negative mutations; CANDIDATE/UNKNOWN/BLOCKED")
