#!/usr/bin/env python3
"""Stage 11 batch 3: pinned donor snapshot, historical provenance and fail-closed mutation QA."""
import copy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
pack = json.loads((root / "docs/diagnostics/STAGE11_TRACTION_BATCH3_2026-11-05.json").read_text(encoding="utf-8"))
migration = json.loads((root / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))
original = {x["id"]: x for x in migration["sourceObject"]["scenarios"]}
ids = ["persistent-wheel-slip", "traction-current-imbalance", "traction-no-assemble",
       "vl80s-ekg-section-desync", "ekg-drive-disconnected"]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
SNAPSHOT = "6ffdfdabf2f467dcdc4958768905f2b675ac0c26"
METADATA = "1b4b9f175274f4738e6463bd756b9783471e73a2"

def check(c):
    sid = c["originalId"]
    assert sid in ids
    src_original = original[sid]
    assert c["scenarioId"] == "vl80s.diag." + sid
    assert c["title"] == src_original["title"]
    assert c["summary"] == src_original["summary"]
    assert c["category"] == src_original["category"] == "Тяга"
    assert c["donorOriginLayer"] == src_original["originLayer"]
    assert c["donorQuestionCount"] == src_original["questionCount"]
    assert c["donorOriginalQuestions"] is None
    assert c["donorPinnedSha"] == DONOR
    assert c["authoringProfileId"] == "vl80s-general"
    assert c["exactInstalledVariant"] == "UNKNOWN"
    assert c["unknownVariantDisposition"] == "BLOCKED"
    assert c["variantEvidence"]["disposition"] == "BLOCKED"
    assert "UNKNOWN" in c["variantEvidence"]["unverifiedInstalledVariant"]
    assert c["publicationStatus"] == "CANDIDATE"
    assert c["deviceQA"] == "NOT_RUN_DEFERRED"
    assert all(c[k] is False for k in ("runtimeImport", "executable",
               "actionAuthorityGranted", "sourceAuthorityVerified"))
    src = c["sourceRecords"]
    assert set(src) == {"donor", "manual1990", "textbook2006"}
    donor = src["donor"]
    assert donor["kind"] == "PINNED_DONOR_COMPRESSED_SNAPSHOT"
    assert donor["repository"] == "DomEnota-hub/Test-"
    assert donor["commit"] == DONOR
    assert donor["blobSha"] == SNAPSHOT
    assert donor["path"] == migration["sourcePath"]
    assert donor["sourcePointer"] == "sourceObject.scenarios[id=" + sid + "]"
    assert donor["sourceOriginLayer"] == src_original["originLayer"]
    assert donor["sourceProfileIds"] == src_original["applicableVariantIds"]
    assert donor["originalQuestionCount"] == src_original["questionCount"]
    assert donor["originalQuestionTextVerified"] is False
    assert donor["sourceMetadataSha"] == METADATA
    assert donor["currentOperatingAuthority"] is False
    assert donor["proceduresImported"] is False
    assert c["sourceDiscrepancy"] and len(c["sourceDiscrepancy"]) > 40
    for key in ("manual1990", "textbook2006"):
        record = src[key]
        assert len(record["verifiedLocators"]) == 2
        assert record["currentOperatingAuthority"] is False
        assert record["modernRevisionVerified"] is False
        assert record["exactInstalledEquipmentVerified"] is False
        assert record["proceduresImported"] is False
    assert len(c["historicalEvidenceClaims"]) == 4
    for claim in c["historicalEvidenceClaims"]:
        assert claim["sourceId"] in ("manual1990", "textbook2006")
        assert claim["locator"] in src[claim["sourceId"]]["verifiedLocators"]
        assert claim["authorizesAction"] is False
        assert claim["provesFaultCause"] is False
    assert c["extendedWarning"] == {
        "default": "HIDDEN", "requiresReadToEnd": True,
        "requiresAcknowledgement": True, "consentResetsOnClose": True,
        "warningGrantsActionAuthority": False}
    safe = c["safety"]
    assert safe["observationOnly"] is True and safe["onlyPreviouslyRecorded"] is True
    assert safe["triState"] == ["YES", "NO", "UNKNOWN"]
    assert safe["unknownMustStop"] is True and safe["operationsAllowed"] == []
    assert all(safe[k] == "NOT_APPROVED" for k in ("roleGate", "sourceGate", "safetyGate"))
    assert {"JUMPER", "PROTECTION_BYPASS", "HV_INTERVENTION",
            "TEST_RESTART", "LIVE_MEASUREMENT", "TRACTION_SWITCHING"} <= set(safe["prohibited"])
    for mode, expected, questions in (("SHORT", 6, 2), ("DETAILED", 12, 8)):
        graph = c["versions"][mode]
        nodes = graph["nodes"]
        assert len(nodes) == expected and graph["startNodeId"] == "q1"
        by_id = {n["id"]: n for n in nodes}
        assert len(by_id) == expected
        seen = set()
        pending = ["q1"]
        while pending:
            key = pending.pop()
            assert key in by_id
            if key in seen:
                continue
            seen.add(key)
            node = by_id[key]
            assert node["recordedOnly"] is True
            assert node["operationRequested"] is False and node["causeConfirmed"] is False
            assert set(node["sourceRefs"]) == set(src)
            if node["type"] == "QUESTION":
                assert node["text"].startswith("По ранее записанным сведениям:")
                assert set(node["responses"]) == {"YES", "NO", "UNKNOWN"}
                assert node["responses"]["UNKNOWN"] == "stop_unknown"
                pending.extend(node["responses"].values())
            else:
                assert node["type"] in ("STOP", "OBSERVATION_REPORT")
                assert node["responses"] == {}
        assert len(seen) == expected
        assert sum(n["type"] == "QUESTION" for n in nodes) == questions
        assert by_id["q1"]["responses"]["YES"] == "stop_danger"
        assert by_id["stop_unknown"]["type"] == "STOP"
        assert by_id["stop_danger"]["type"] == "STOP"
        assert by_id["stop_unresolved"]["type"] == "STOP"
        assert by_id["report"]["type"] == "OBSERVATION_REPORT"
        assert "НЕ" in by_id["report"]["text"]
        assert len({n["text"] for n in nodes if n["type"] == "QUESTION"}) == questions
    ext = c["informationExtensions"]
    assert len(ext) == 5 and len({x["id"] for x in ext}) == 5
    assert len({x["text"] for x in ext}) == 5
    assert [x["version"] for x in ext] == ["SHORT", "SHORT", "DETAILED", "DETAILED", "DETAILED"]
    for x in ext:
        assert x["kind"] == "HISTORICAL_INFORMATION_ONLY"
        assert x["warningRequired"] is True and x["actionAuthorityGranted"] is False
        assert len(x["sourceRefs"]) == 1
        assert x["locator"] in src[x["sourceRefs"][0]]["verifiedLocators"]
    forbidden_commands = ("включите", "нажмите", "перемычкой соедините",
                          "проверните", "измерьте", "снимите ограждение")
    for mode in ("SHORT", "DETAILED"):
        for node in c["versions"][mode]["nodes"]:
            assert not any(cmd in node["text"].lower() for cmd in forbidden_commands)

assert migration["donorCommit"] == DONOR and migration["sourceBlobSha"] == SNAPSHOT
assert [x["originalId"] for x in pack["candidates"]] == ids
assert len({x["canonicalBoundary"] for x in pack["candidates"]}) == len(ids)
assert len({x["versions"]["DETAILED"]["nodes"][1]["text"] for x in pack["candidates"]}) == len(ids)
ledger = pack["ledger"]
assert ledger["donorPinnedSha"] == DONOR and ledger["donorSnapshotBlobSha"] == SNAPSHOT
assert ledger["migrationBlobSha"] == METADATA
assert ledger["runtimeImport"] is False and ledger["actionAuthorityGranted"] is False
assert ledger["scenarioIds"] == [x["scenarioId"] for x in pack["candidates"]]
assert ledger["originalQuestionTextVerified"] is False
assert ledger["remainingOriginalIds"] == ["traction-overload-relay-trip", "traction-ground-relay-trip"]

mutations = 0
def must_reject(x, label):
    global mutations
    try:
        check(x)
    except (AssertionError, KeyError):
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
        ("donorOriginLayer", "BAD"), ("donorQuestionCount", -1)):
        x = copy.deepcopy(candidate)
        x[key] = val
        must_reject(x, key)
    for key, val in (
        ("requiresReadToEnd", False), ("requiresAcknowledgement", False),
        ("consentResetsOnClose", False), ("warningGrantsActionAuthority", True)):
        x = copy.deepcopy(candidate)
        x["extendedWarning"][key] = val
        must_reject(x, key)
    for key, val in (
        ("roleGate", "APPROVED"), ("sourceGate", "APPROVED"),
        ("safetyGate", "APPROVED"), ("operationsAllowed", ["TEST_RESTART"]),
        ("unknownMustStop", False)):
        x = copy.deepcopy(candidate)
        x["safety"][key] = val
        must_reject(x, key)
    for mode in ("SHORT", "DETAILED"):
        for kind in ("unknown", "operation", "source", "cause"):
            x = copy.deepcopy(candidate)
            node = x["versions"][mode]["nodes"][0]
            if kind == "unknown":
                node["responses"]["UNKNOWN"] = "report"
            elif kind == "operation":
                node["operationRequested"] = True
            elif kind == "source":
                node["sourceRefs"] = []
            else:
                node["causeConfirmed"] = True
            must_reject(x, mode + ":" + kind)
    for key, val in (
        ("warningRequired", False), ("actionAuthorityGranted", True),
        ("locator", "BAD")):
        x = copy.deepcopy(candidate)
        x["informationExtensions"][0][key] = val
        must_reject(x, key)
    for key in ("blobSha", "sourcePointer", "sourceOriginLayer",
                "sourceMetadataSha", "originalQuestionTextVerified"):
        x = copy.deepcopy(candidate)
        x["sourceRecords"]["donor"][key] = (
            True if key == "originalQuestionTextVerified" else "BAD")
        must_reject(x, "donor:" + key)
assert mutations == 175, mutations
print("STAGE11_TRACTION_BATCH3_PASS", len(pack["candidates"]),
      "NEGATIVE_MUTATIONS", mutations)
