#!/usr/bin/env python3
"""Stage12 brake batch: pinned source, exact IDs, graph, role and safety gates, negative mutations."""
import copy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
pack = json.loads((root / "docs/diagnostics/STAGE12_BRAKES_BATCH2_2026-11-05.json").read_text(encoding="utf-8"))
migration = json.loads((root / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))
donor = {s["id"]: s for s in migration["sourceObject"]["scenarios"]}
expected = ["epk-leak","equalizing-reservoir-mismatch","handbrake-not-release","independent-brake-no-apply","independent-brake-no-release"]
assert migration["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
assert [c["originalId"] for c in pack["candidates"]] == expected
assert len(set(expected)) == 5
assert set(pack['ledger']['remainingCategoryIds']) == {'uncommanded-braking','wheel-dragging'}
assert not set(expected) & {'brake-cylinder-imbalance','brake-lock-state-mismatch','brake-pipe-leak','brake-pipe-no-charge','brake-rigging-damage'}
assert pack["ledger"]["scenarioIds"] == ["vl80s.diag." + x for x in expected]
assert pack["ledger"]["baseHead"] == "88d390d1eb223e44818301acaf81b5b64035deb2"
assert pack["ledger"]["donorSnapshotBlobSha"] == migration["sourceBlobSha"]
assert pack["ledger"]["runtimeImport"] is False
assert pack["ledger"]["actionAuthorityGranted"] is False
assert set(pack["ledger"]["remainingCategoryIds"]) == {x["id"] for x in donor.values() if x["category"] == "Тормоза"} - set(expected)

def check(c):
    sid = c["originalId"]
    assert sid in expected
    src = donor[sid]
    assert c["scenarioId"] == "vl80s.diag." + sid
    assert c["title"] == src["title"] and c["summary"] == src["summary"]
    assert c["category"] == src["category"] == "Тормоза"
    assert c["donorOriginLayer"] == src["originLayer"]
    assert c["donorQuestionCount"] == src["questionCount"] == 3
    assert c["donorOriginalQuestions"] is None
    assert c["donorPinnedSha"] == migration["donorCommit"]
    assert c["authoringProfileId"] == "vl80s-general"
    assert c["exactInstalledVariant"] == "UNKNOWN"
    assert c["unknownVariantDisposition"] == "BLOCKED"
    assert c["variantEvidence"]["disposition"] == "BLOCKED"
    assert c["publicationStatus"] == "CANDIDATE"
    assert c["deviceQA"] == "NOT_RUN_DEFERRED"
    assert all(c[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified"))
    assert len(c["sourceDiscrepancy"]) > 60
    s = c["sourceRecords"]
    assert set(s) == {"donor","manual1990","rules2026"}
    assert s["donor"]["commit"] == migration["donorCommit"]
    assert s["donor"]["blobSha"] == migration["sourceBlobSha"]
    assert s["donor"]["sourceMetadataSha"] == pack["ledger"]["migrationBlobSha"]
    assert s["donor"]["sourceOriginLayer"] == src["originLayer"]
    assert s["donor"]["sourceProfileIds"] == src["applicableVariantIds"]
    assert s["donor"]["originalQuestionTextVerified"] is False
    assert s["donor"]["sourcePointer"] == "sourceObject.scenarios[id=" + sid + "]"
    assert s["donor"]["proceduresImported"] is False
    assert s["manual1990"]["year"] == 1990 and len(s["manual1990"]["verifiedLocators"]) == 2
    assert s["manual1990"]["currentOperatingAuthority"] is False
    assert s["manual1990"]["proceduresImported"] is False
    assert s["rules2026"]["effectiveDate"] == "2026-07-01"
    assert s["rules2026"]["scopeOnly"] is True
    assert s["rules2026"]["exactSectionProceduresVerified"] is False
    assert s["rules2026"]["actionAuthorityGranted"] is False
    assert c["extendedWarning"] == {"default":"HIDDEN","requiresReadToEnd":True,
        "requiresAcknowledgement":True,"consentResetsOnClose":True,"warningGrantsActionAuthority":False}
    safety = c["safety"]
    assert safety["observationOnly"] and safety["onlyPreviouslyRecorded"] and safety["unknownMustStop"]
    assert safety["triState"] == ["YES","NO","UNKNOWN"]
    assert safety["operationsAllowed"] == []
    assert {"JUMPER","PROTECTION_BYPASS","HV_INTERVENTION","TEST_RESTART",
            "LIVE_MEASUREMENT","BRAKE_VALVE_SWITCHING","PRESSURE_TEST","REPAIR"} <= set(safety["prohibited"])
    assert all(safety[k] == "NOT_APPROVED" for k in ("roleGate","sourceGate","safetyGate"))
    for mode,count,qcount in (("SHORT",6,2),("DETAILED",12,8)):
        g = c["versions"][mode]
        nodes = {n["id"]:n for n in g["nodes"]}
        assert len(nodes) == len(g["nodes"]) == count
        assert g["startNodeId"] == "q1"
        assert sum(n["type"] == "QUESTION" for n in nodes.values()) == qcount
        visited = set()
        stack = ["q1"]
        while stack:
            k = stack.pop()
            assert k in nodes
            if k in visited: continue
            visited.add(k)
            n = nodes[k]
            assert n["recordedOnly"] is True
            assert n["operationRequested"] is False and n["causeConfirmed"] is False
            assert set(n["sourceRefs"]) == set(s)
            if n["type"] == "QUESTION":
                assert n["text"].startswith("По ранее записанным сведениям:")
                assert set(n["responses"]) == {"YES","NO","UNKNOWN"}
                assert n["responses"]["UNKNOWN"] == "stop_unknown"
                stack.extend(n["responses"].values())
            else:
                assert n["type"] in ("STOP","OBSERVATION_REPORT")
                assert n["responses"] == {}
        assert len(visited) == count
        assert nodes["q1"]["responses"]["YES"] == "stop_danger"
        assert all(nodes[k]["type"] == "STOP" for k in ("stop_danger","stop_unknown","stop_unresolved"))
        assert nodes["report"]["type"] == "OBSERVATION_REPORT"
        assert "НЕ" in nodes["report"]["text"]
    exts = c["informationExtensions"]
    assert len(exts) == len({e["id"] for e in exts}) == len({e["text"] for e in exts}) == 5
    assert [e["version"] for e in exts] == ["SHORT","SHORT","DETAILED","DETAILED","DETAILED"]
    assert len(c["historicalEvidenceClaims"]) == 5
    for e in exts:
        assert e["warningRequired"] is True and e["actionAuthorityGranted"] is False
        assert len(e["sourceRefs"]) == 1
        assert e["locator"] in s[e["sourceRefs"][0]]["verifiedLocators"]
        assert e["kind"] in ("HISTORICAL_INFORMATION_ONLY","CURRENT_RULES_SCOPE_ONLY")
    for claim in c["historicalEvidenceClaims"]:
        assert claim["authorizesAction"] is False and claim["provesFaultCause"] is False
        assert claim["locator"] in s[claim["sourceId"]]["verifiedLocators"]
    return True

mutations = 0
def reject(c, label):
    global mutations
    try: check(c)
    except (AssertionError, KeyError, TypeError): mutations += 1
    else: raise AssertionError("unsafe mutation accepted: " + label)

for c in pack["candidates"]:
    check(c)
    for key,value in (("publicationStatus","ACTIVE"),("runtimeImport",True),
        ("executable",True),("actionAuthorityGranted",True),("sourceAuthorityVerified",True),
        ("exactInstalledVariant","ASSUMED"),("unknownVariantDisposition","ALLOW"),
        ("donorPinnedSha","BAD"),("donorOriginLayer","BAD"),("donorQuestionCount",0)):
        x=copy.deepcopy(c);x[key]=value;reject(x,key)
    for key,value in (("requiresReadToEnd",False),("requiresAcknowledgement",False),
        ("consentResetsOnClose",False),("warningGrantsActionAuthority",True)):
        x=copy.deepcopy(c);x["extendedWarning"][key]=value;reject(x,key)
    for key,value in (("roleGate","APPROVED"),("sourceGate","APPROVED"),
        ("safetyGate","APPROVED"),("operationsAllowed",["PRESSURE_TEST"]),
        ("unknownMustStop",False)):
        x=copy.deepcopy(c);x["safety"][key]=value;reject(x,key)
    for mode in ("SHORT","DETAILED"):
        for key,value in (("operationRequested",True),("causeConfirmed",True),
            ("sourceRefs",[])):
            x=copy.deepcopy(c);x["versions"][mode]["nodes"][0][key]=value;reject(x,mode+key)
        x=copy.deepcopy(c);x["versions"][mode]["nodes"][0]["responses"]["UNKNOWN"]="report";reject(x,mode+"unknown")
    for key,value in (("warningRequired",False),("actionAuthorityGranted",True),
        ("locator","BAD")):
        x=copy.deepcopy(c);x["informationExtensions"][0][key]=value;reject(x,key)
    for key,value in (("originalQuestionTextVerified",True),("sourcePointer","BAD"),
        ("blobSha","BAD"),("sourceMetadataSha","BAD")):
        x=copy.deepcopy(c);x["sourceRecords"]["donor"][key]=value;reject(x,key)
    for key,value in (("scopeOnly",False),("exactSectionProceduresVerified",True),
        ("actionAuthorityGranted",True)):
        x=copy.deepcopy(c);x["sourceRecords"]["rules2026"][key]=value;reject(x,key)
assert mutations == 185, mutations
assert len({c['canonicalBoundary'] for c in pack['candidates']}) == 5
assert len({n['text'] for c in pack['candidates'] for n in c['versions']['DETAILED']['nodes'] if n['type']=='QUESTION'}) == 40
print("STAGE12_BRAKES_BATCH2_PASS",len(pack["candidates"]),"NEGATIVE_MUTATIONS",mutations)
