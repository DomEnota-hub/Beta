#!/usr/bin/env python3
"""Stage13 pneumatic research candidates: pinned identity, graphs, gates, negative mutations."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "docs/diagnostics/STAGE13_PNEUMATICS_BATCH1_2026-11-05.json").read_text(encoding="utf-8"))
migration = json.loads((ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))
donor = {x["id"]: x for x in migration["sourceObject"]["scenarios"]}
expected = ["feed-line-leak", "main-reservoir-safety-valve", "pressure-gauge-mismatch"]
ledger = pack["ledger"]
assert ledger["baseHead"] == "bcd3eb25ff364b25f38e45e5aa8f28b6c6e0aa10"
assert ledger["donorPinnedSha"] == migration["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
assert ledger["donorSnapshotBlobSha"] == migration["sourceBlobSha"]
assert ledger["categorySourceCount"] == 9
assert ledger["scenarioIds"] == ["vl80s.diag." + s for s in expected]
assert ledger["remainingCategoryIds"] == [s["id"] for s in migration["sourceObject"]["scenarios"] if s["category"] == "Пневматика" and s["id"] not in expected]
assert ledger["publicationStatus"] == "CANDIDATE"
assert ledger["runtimeImport"] is False and ledger["actionAuthorityGranted"] is False
assert ledger["originalQuestionTextVerified"] is False
assert [c["originalId"] for c in pack["candidates"]] == expected

def check(c):
    sid = c["originalId"]
    assert sid in expected
    src = donor[sid]
    assert c["scenarioId"] == "vl80s.diag." + sid
    assert c["title"] == src["title"] and c["summary"] == src["summary"]
    assert c["category"] == src["category"] == "Пневматика"
    assert c["donorOriginLayer"] == src["originLayer"]
    assert c["donorQuestionCount"] == src["questionCount"]
    assert c["donorPinnedSha"] == migration["donorCommit"]
    assert c["donorOriginalQuestions"] is None
    assert c["authoringProfileId"] == "vl80s-general"
    assert c["exactInstalledVariant"] == "UNKNOWN"
    assert c["unknownVariantDisposition"] == "BLOCKED"
    assert c["variantEvidence"]["disposition"] == "BLOCKED"
    assert len(c["canonicalBoundary"]) > 30 and len(c["sourceDiscrepancy"]) > 100
    assert c["publicationStatus"] == "CANDIDATE" and c["deviceQA"] == "NOT_RUN_DEFERRED"
    assert all(c[k] is False for k in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified"))
    sources = c["sourceRecords"]
    assert set(sources) == {"donor", "manual1990", "textbook2006", "rules2026"}
    ds = sources["donor"]
    assert ds["commit"] == migration["donorCommit"]
    assert ds["blobSha"] == migration["sourceBlobSha"]
    assert ds["sourceMetadataSha"] == ledger["migrationBlobSha"]
    assert ds["sourcePointer"] == "sourceObject.scenarios[id=" + sid + "]"
    assert ds["sourceOriginLayer"] == src["originLayer"]
    assert ds["sourceProfileIds"] == src["applicableVariantIds"] == ["vl80s-general"]
    assert ds["originalQuestionCount"] == src["questionCount"]
    assert ds["originalQuestionTextVerified"] is False and ds["proceduresImported"] is False
    for key, year in (("manual1990", 1990), ("textbook2006", 2006)):
        assert sources[key]["year"] == year
        assert len(sources[key]["verifiedLocators"]) == 2
        assert sources[key]["currentOperatingAuthority"] is False
        assert sources[key]["proceduresImported"] is False
    assert sources["rules2026"]["effectiveDate"] == "2026-07-01"
    assert sources["rules2026"]["scopeOnly"] is True
    assert sources["rules2026"]["exactSectionProceduresVerified"] is False
    assert sources["rules2026"]["actionAuthorityGranted"] is False
    assert c["extendedWarning"] == {
        "default": "HIDDEN", "requiresReadToEnd": True, "requiresAcknowledgement": True,
        "consentResetsOnClose": True, "warningGrantsActionAuthority": False
    }
    safety = c["safety"]
    assert safety["observationOnly"] and safety["onlyPreviouslyRecorded"] and safety["unknownMustStop"]
    assert safety["triState"] == ["YES", "NO", "UNKNOWN"]
    assert safety["operationsAllowed"] == []
    assert {"JUMPER", "PROTECTION_BYPASS", "HV_INTERVENTION", "TEST_RESTART", "LIVE_MEASUREMENT", "BRAKE_VALVE_SWITCHING", "PRESSURE_TEST", "REPAIR", "FORCED_VALVE_ACTUATION"} <= set(safety["prohibited"])
    assert all(safety[k] == "NOT_APPROVED" for k in ("roleGate", "sourceGate", "safetyGate"))
    for mode, count, qcount in (("SHORT", 6, 2), ("DETAILED", 12, 8)):
        g = c["versions"][mode]
        nodes = {n["id"]: n for n in g["nodes"]}
        assert len(nodes) == len(g["nodes"]) == count
        assert g["startNodeId"] == "q1"
        assert sum(n["type"] == "QUESTION" for n in nodes.values()) == qcount
        visited, stack = set(), ["q1"]
        while stack:
            key = stack.pop()
            assert key in nodes
            if key in visited:
                continue
            visited.add(key)
            n = nodes[key]
            assert n["recordedOnly"] is True
            assert n["operationRequested"] is False and n["causeConfirmed"] is False
            assert set(n["sourceRefs"]) == {"donor", "manual1990", "textbook2006"}
            if n["type"] == "QUESTION":
                assert n["text"].startswith("По ранее записанным сведениям:")
                assert set(n["responses"]) == {"YES", "NO", "UNKNOWN"}
                assert n["responses"]["UNKNOWN"] == "stop_unknown"
                stack.extend(n["responses"].values())
            else:
                assert n["type"] in ("STOP", "OBSERVATION_REPORT")
                assert n["responses"] == {}
        assert len(visited) == count
        assert nodes["q1"]["responses"]["YES"] == "stop_danger"
        assert all(nodes[k]["type"] == "STOP" for k in ("stop_danger", "stop_unknown", "stop_unresolved"))
        assert nodes["report"]["type"] == "OBSERVATION_REPORT" and "НЕ" in nodes["report"]["text"]
    exts = c["informationExtensions"]
    assert len(exts) == len({e["id"] for e in exts}) == len({e["text"] for e in exts}) == 5
    assert [e["version"] for e in exts] == ["SHORT", "SHORT", "DETAILED", "DETAILED", "DETAILED"]
    assert len(c["historicalEvidenceClaims"]) == 5
    for e in exts:
        assert e["warningRequired"] is True and e["actionAuthorityGranted"] is False
        assert len(e["sourceRefs"]) == 1
        assert e["locator"] in sources[e["sourceRefs"][0]]["verifiedLocators"]
        assert e["kind"] in ("HISTORICAL_INFORMATION_ONLY", "CURRENT_RULES_SCOPE_ONLY")
    for cl in c["historicalEvidenceClaims"]:
        assert cl["authorizesAction"] is False and cl["provesFaultCause"] is False
        assert cl["locator"] in sources[cl["sourceId"]]["verifiedLocators"]

mutations = 0
def reject(c, label):
    global mutations
    try:
        check(c)
    except (AssertionError, KeyError, TypeError):
        mutations += 1
    else:
        raise AssertionError("unsafe mutation accepted: " + label)

for candidate in pack["candidates"]:
    check(candidate)
    for key, val in (
        ("publicationStatus", "ACTIVE"), ("runtimeImport", True),
        ("executable", True), ("actionAuthorityGranted", True),
        ("sourceAuthorityVerified", True), ("exactInstalledVariant", "ASSUMED"),
        ("unknownVariantDisposition", "ALLOW"), ("donorPinnedSha", "BAD"),
        ("donorOriginLayer", "BAD"), ("donorQuestionCount", 0), ("deviceQA", "PASSED")
    ):
        c = copy.deepcopy(candidate); c[key] = val; reject(c, key)
    for key, val in (
        ("requiresReadToEnd", False), ("requiresAcknowledgement", False),
        ("consentResetsOnClose", False), ("warningGrantsActionAuthority", True)
    ):
        c = copy.deepcopy(candidate); c["extendedWarning"][key] = val; reject(c, key)
    for key, val in (
        ("roleGate", "APPROVED"), ("sourceGate", "APPROVED"),
        ("safetyGate", "APPROVED"), ("operationsAllowed", ["PRESSURE_TEST"]),
        ("unknownMustStop", False)
    ):
        c = copy.deepcopy(candidate); c["safety"][key] = val; reject(c, key)
    for mode in ("SHORT", "DETAILED"):
        for key, val in (("operationRequested", True), ("causeConfirmed", True), ("sourceRefs", [])):
            c = copy.deepcopy(candidate); c["versions"][mode]["nodes"][0][key] = val; reject(c, mode+key)
        c = copy.deepcopy(candidate); c["versions"][mode]["nodes"][0]["responses"]["UNKNOWN"] = "report"; reject(c, mode+"unknown")
    for key, val in (
        ("originalQuestionTextVerified", True), ("sourcePointer", "BAD"),
        ("blobSha", "BAD"), ("sourceMetadataSha", "BAD")
    ):
        c = copy.deepcopy(candidate); c["sourceRecords"]["donor"][key] = val; reject(c, key)
    for key, val in (("warningRequired", False), ("actionAuthorityGranted", True), ("locator", "BAD")):
        c = copy.deepcopy(candidate); c["informationExtensions"][0][key] = val; reject(c, key)

assert mutations == 105, mutations
assert len({c["canonicalBoundary"] for c in pack["candidates"]}) == 3
assert len({n["text"] for c in pack["candidates"] for n in c["versions"]["DETAILED"]["nodes"] if n["type"] == "QUESTION"}) == 24
print("STAGE13_PNEUMATICS_BATCH1_PASS", len(pack["candidates"]), "NEGATIVE_MUTATIONS", mutations)
