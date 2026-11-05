#!/usr/bin/env python3
"""Stage12 brake closeout: pinned donor identity, complete graphs, fail-closed and negative mutations."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "docs/diagnostics/STAGE12_BRAKES_CLOSEOUT_BATCH3_2026-11-05.json").read_text(encoding="utf-8"))
migration = json.loads((ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))
donor = {x["id"]: x for x in migration["sourceObject"]["scenarios"]}
expected = ["uncommanded-braking", "wheel-dragging"]
previous = {"brake-cylinder-imbalance", "brake-lock-state-mismatch", "brake-pipe-leak",
            "brake-pipe-no-charge", "brake-rigging-damage", "epk-leak",
            "equalizing-reservoir-mismatch", "handbrake-not-release",
            "independent-brake-no-apply", "independent-brake-no-release"}
all_brakes = {x["id"] for x in donor.values() if x["category"] == "Тормоза"}
assert all_brakes == previous | set(expected), (all_brakes - previous - set(expected))
assert len(all_brakes) == 12
assert [x["originalId"] for x in pack["candidates"]] == expected
assert set(pack["ledger"]["remainingCategoryIds"]) == set()
assert pack["ledger"]["categoryCoverageCount"] == 12
assert pack["ledger"]["scenarioIds"] == ["vl80s.diag." + x for x in expected]
assert pack["ledger"]["baseHead"] == "672dcfc79fa6bd9c2e38a553fa7ee48cee79506f"
assert pack["ledger"]["donorPinnedSha"] == migration["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
assert pack["ledger"]["donorSnapshotBlobSha"] == migration["sourceBlobSha"]
assert pack["ledger"]["runtimeImport"] is False
assert pack["ledger"]["actionAuthorityGranted"] is False
assert pack["ledger"]["originalQuestionTextVerified"] is False

def check(c):
    sid = c["originalId"]
    assert sid in expected
    src = donor[sid]
    assert c["scenarioId"] == "vl80s.diag." + sid
    assert c["category"] == src["category"] == "Тормоза"
    assert c["title"] == src["title"] and c["summary"] == src["summary"]
    assert c["donorOriginLayer"] == src["originLayer"] == "DiagnosticExpansion.kt"
    assert c["donorPinnedSha"] == migration["donorCommit"]
    assert c["donorOriginalQuestions"] is None
    assert c["donorQuestionCount"] == src["questionCount"] == 3
    assert c["authoringProfileId"] == "vl80s-general"
    assert c["exactInstalledVariant"] == "UNKNOWN"
    assert c["unknownVariantDisposition"] == "BLOCKED"
    assert c["variantEvidence"]["disposition"] == "BLOCKED"
    assert len(c["sourceDiscrepancy"]) > 100
    assert len(c["canonicalBoundary"]) > 25
    assert c["publicationStatus"] == "CANDIDATE"
    assert c["deviceQA"] == "NOT_RUN_DEFERRED"
    assert all(c[k] is False for k in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified"))
    sources = c["sourceRecords"]
    assert set(sources) == {"donor", "manual1990", "rules2026"}
    assert sources["donor"]["commit"] == migration["donorCommit"]
    assert sources["donor"]["blobSha"] == migration["sourceBlobSha"]
    assert sources["donor"]["sourceMetadataSha"] == pack["ledger"]["migrationBlobSha"]
    assert sources["donor"]["sourceOriginLayer"] == src["originLayer"]
    assert sources["donor"]["sourceProfileIds"] == src["applicableVariantIds"] == ["vl80s-general"]
    assert sources["donor"]["originalQuestionCount"] == 3
    assert sources["donor"]["originalQuestionTextVerified"] is False
    assert sources["donor"]["sourcePointer"] == "sourceObject.scenarios[id=" + sid + "]"
    assert sources["donor"]["proceduresImported"] is False
    assert sources["manual1990"]["year"] == 1990
    assert len(sources["manual1990"]["verifiedLocators"]) == 2
    assert sources["manual1990"]["currentOperatingAuthority"] is False
    assert sources["manual1990"]["proceduresImported"] is False
    assert sources["rules2026"]["effectiveDate"] == "2026-07-01"
    assert len(sources["rules2026"]["verifiedLocators"]) == 2
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
    assert {"JUMPER", "PROTECTION_BYPASS", "HV_INTERVENTION", "TEST_RESTART",
            "LIVE_MEASUREMENT", "BRAKE_VALVE_SWITCHING", "PRESSURE_TEST", "REPAIR"} <= set(safety["prohibited"])
    assert all(safety[k] == "NOT_APPROVED" for k in ("roleGate", "sourceGate", "safetyGate"))
    for mode, count, questions in (("SHORT", 6, 2), ("DETAILED", 12, 8)):
        graph = c["versions"][mode]
        nodes = {n["id"]: n for n in graph["nodes"]}
        assert len(nodes) == len(graph["nodes"]) == count
        assert graph["startNodeId"] == "q1"
        assert sum(n["type"] == "QUESTION" for n in nodes.values()) == questions
        visited, stack = set(), ["q1"]
        while stack:
            key = stack.pop()
            assert key in nodes
            if key in visited:
                continue
            visited.add(key)
            node = nodes[key]
            assert node["recordedOnly"] is True
            assert node["operationRequested"] is False
            assert node["causeConfirmed"] is False
            assert set(node["sourceRefs"]) == set(sources)
            if node["type"] == "QUESTION":
                assert node["text"].startswith("По ранее записанным сведениям:")
                assert set(node["responses"]) == {"YES", "NO", "UNKNOWN"}
                assert node["responses"]["UNKNOWN"] == "stop_unknown"
                stack.extend(node["responses"].values())
            else:
                assert node["type"] in ("STOP", "OBSERVATION_REPORT")
                assert node["responses"] == {}
        assert len(visited) == count, (sid, mode, visited)
        assert nodes["q1"]["responses"]["YES"] == "stop_danger"
        assert all(nodes[k]["type"] == "STOP" for k in ("stop_danger", "stop_unknown", "stop_unresolved"))
        assert nodes["report"]["type"] == "OBSERVATION_REPORT"
        assert "НЕ" in nodes["report"]["text"]
    exts = c["informationExtensions"]
    assert len(exts) == len({e["id"] for e in exts}) == len({e["text"] for e in exts}) == 5
    assert [e["version"] for e in exts] == ["SHORT", "SHORT", "DETAILED", "DETAILED", "DETAILED"]
    assert len(c["historicalEvidenceClaims"]) == 5
    for e in exts:
        assert e["warningRequired"] is True and e["actionAuthorityGranted"] is False
        assert len(e["sourceRefs"]) == 1
        assert e["locator"] in sources[e["sourceRefs"][0]]["verifiedLocators"]
        assert e["kind"] in ("HISTORICAL_INFORMATION_ONLY", "CURRENT_RULES_SCOPE_ONLY")
    for claim in c["historicalEvidenceClaims"]:
        assert claim["authorizesAction"] is False and claim["provesFaultCause"] is False
        assert claim["locator"] in sources[claim["sourceId"]]["verifiedLocators"]
    return True

mutations = 0
def reject(candidate, label):
    global mutations
    try:
        check(candidate)
    except (AssertionError, KeyError, TypeError):
        mutations += 1
    else:
        raise AssertionError("unsafe mutation accepted: " + label)

for candidate in pack["candidates"]:
    check(candidate)
    for key, value in (("publicationStatus", "ACTIVE"), ("runtimeImport", True),
                       ("executable", True), ("actionAuthorityGranted", True),
                       ("sourceAuthorityVerified", True), ("exactInstalledVariant", "ASSUMED"),
                       ("unknownVariantDisposition", "ALLOW"), ("donorPinnedSha", "BAD"),
                       ("donorOriginLayer", "BAD"), ("donorQuestionCount", 0)):
        c = copy.deepcopy(candidate); c[key] = value; reject(c, key)
    for key, value in (("requiresReadToEnd", False), ("requiresAcknowledgement", False),
                       ("consentResetsOnClose", False), ("warningGrantsActionAuthority", True)):
        c = copy.deepcopy(candidate); c["extendedWarning"][key] = value; reject(c, key)
    for key, value in (("roleGate", "APPROVED"), ("sourceGate", "APPROVED"),
                       ("safetyGate", "APPROVED"), ("operationsAllowed", ["BRAKE_VALVE_SWITCHING"]),
                       ("unknownMustStop", False)):
        c = copy.deepcopy(candidate); c["safety"][key] = value; reject(c, key)
    for mode in ("SHORT", "DETAILED"):
        for key, value in (("operationRequested", True), ("causeConfirmed", True), ("sourceRefs", [])):
            c = copy.deepcopy(candidate); c["versions"][mode]["nodes"][0][key] = value; reject(c, mode+key)
        c = copy.deepcopy(candidate)
        c["versions"][mode]["nodes"][0]["responses"]["UNKNOWN"] = "report"
        reject(c, mode+"unknown")
    for key, value in (("warningRequired", False), ("actionAuthorityGranted", True), ("locator", "BAD")):
        c = copy.deepcopy(candidate); c["informationExtensions"][0][key] = value; reject(c, key)
    for key, value in (("originalQuestionTextVerified", True), ("sourcePointer", "BAD"),
                       ("blobSha", "BAD"), ("sourceMetadataSha", "BAD")):
        c = copy.deepcopy(candidate); c["sourceRecords"]["donor"][key] = value; reject(c, key)
    for key, value in (("scopeOnly", False), ("exactSectionProceduresVerified", True),
                       ("actionAuthorityGranted", True)):
        c = copy.deepcopy(candidate); c["sourceRecords"]["rules2026"][key] = value; reject(c, key)
assert mutations == 74, mutations
assert len({c["canonicalBoundary"] for c in pack["candidates"]}) == 2
assert len({n["text"] for c in pack["candidates"] for n in c["versions"]["DETAILED"]["nodes"] if n["type"] == "QUESTION"}) == 16
print("STAGE12_BRAKES_CLOSEOUT_PASS", len(pack["candidates"]), "NEGATIVE_MUTATIONS", mutations, "COVERAGE", len(all_brakes))
