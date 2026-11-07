#!/usr/bin/env python3
"""Stage 18 / batch 19: independent TC and TM research-only scenarios.

No locomotive operations or live tests are performed. This validator checks
exact donor sourceObject parity, graph reachability and fail-closed mutations.
"""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "docs/diagnostics/STAGE18_ERMAK_BRAKE_PRESSURE_BATCH19_2026-11-06.json").read_text(encoding="utf-8"))
PACK = json.loads((ROOT / "content-packs/electric/ermak/diagnostics/recommended/diagnostics-03.pack.json").read_text(encoding="utf-8"))
IDS = ("ER-DIAG-059", "ER-DIAG-060")
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "c3a22c62db42308eb4b7ee44ff2da02f47686625"
SRC = {e["id"]: e["sourceObject"]["object"] for e in PACK["entries"] if e["id"] in IDS}
FIELDS = {"title": "title", "symptom": "symptom", "sourceObjectStatus": "status",
          "sourceObjectApplicability": "applicability", "sourceObjectSystemIds": "systemIds",
          "sourceObjectEquipmentRefs": "equipmentRefs", "sourceObjectSourceRefs": "sourceRefs"}
HAZARDS = {"ER-DIAG-059": "REGEN_DROPOUT_WITH_TC_PRESSURE_RISE",
           "ER-DIAG-060": "REGEN_DROPOUT_WITH_TM_PRESSURE_FALL"}
WARNING = {"default": "HIDDEN", "warningReadToEnd": True,
           "warningAcknowledged": True, "warningGrantsActionAuthority": False}
POLICY = {"observationOnly": True, "onlyPreviouslyRecorded": True,
          "triState": ["YES", "NO", "UNKNOWN"], "unknownMustStop": True,
          "unknownProfile": "BLOCKED", "operationsAllowed": [],
          "activeFaultImmediateStop": True}
SOURCES = {"donor", "manufacturer", "brakeRules2026", "maintenance3508",
           "memo", "practice", "safety"}
EXT_SOURCES = [["donor"], ["manufacturer"], ["memo", "practice"],
               ["brakeRules2026", "maintenance3508"], ["safety", "manufacturer"]]


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def check_graph(graph, mode):
    count = 8 if mode == "SHORT" else 12
    require(graph["startNodeId"] == "q-active", "start")
    require(graph["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED", "authoring")
    require(graph["operatingInstructionsIncluded"] is False, "operating")
    nodes = {node["id"]: node for node in graph["nodes"]}
    require(len(nodes) == len(graph["nodes"]) == count, "node count/identity")
    require(nodes["q-active"]["responses"] == {
        "YES": "stop-active", "NO": "q-profile", "UNKNOWN": "stop-unknown"}, "active gate")
    require(nodes["q-profile"]["responses"] == {
        "YES": "q-symptom", "NO": "stop-profile", "UNKNOWN": "stop-unknown"}, "profile gate")
    require(nodes["q-symptom"]["responses"] == {
        "YES": "q-evidence" if mode == "DETAILED" else "report-match",
        "NO": "stop-mismatch", "UNKNOWN": "stop-unknown"}, "symptom gate")
    if mode == "DETAILED":
        for node_id, yes_id in (("q-evidence", "q-separation"),
                                ("q-separation", "q-provenance"),
                                ("q-provenance", "report-match")):
            require(nodes[node_id]["responses"] == {
                "YES": yes_id, "NO": "stop-unverified", "UNKNOWN": "stop-unknown"},
                "evidence gate " + node_id)
    seen = set()

    def visit(node_id):
        require(node_id in nodes, "dangling edge " + node_id)
        if node_id in seen:
            return
        seen.add(node_id)
        node = nodes[node_id]
        require(node["text"].strip() and node["recordedOnly"] is True, "recorded-only")
        require(node["operationRequested"] is False and node["causeConfirmed"] is False,
                "no action or cause")
        require(node["sourceRefs"] and set(node["sourceRefs"]).issubset(SOURCES), "node provenance")
        if node["type"] == "QUESTION":
            require(set(node["responses"]) == {"YES", "NO", "UNKNOWN"}, "tri-state")
            require(node["responses"]["UNKNOWN"] == "stop-unknown", "UNKNOWN must stop")
            for next_id in node["responses"].values():
                visit(next_id)
        else:
            require(node["type"] in ("STOP", "OBSERVATION_REPORT") and
                    node["responses"] == {}, "terminal")
    visit("q-active")
    require(len(seen) == count, "unreachable graph node")
    require(nodes["stop-profile"]["type"] == "STOP" and
            nodes["stop-unknown"]["type"] == "STOP" and
            nodes["stop-active"]["type"] == "STOP", "terminal safety")


def check(candidate):
    ident = candidate["originalId"]
    require(ident in IDS and candidate["scenarioId"] == "ermak.diag." + ident, "identity")
    donor = SRC[ident]
    for field, donor_field in FIELDS.items():
        require(candidate[field] == donor[donor_field], "donor parity " + field)
    applicability = donor["applicability"]
    require(candidate["families"] == applicability["families"], "families")
    require(candidate["profileApplicability"] == applicability["profiles"], "profiles")
    require(candidate["lateProfileRule"] == applicability["lateProfiles"], "late profiles")
    require(candidate["hazardCategory"] == HAZARDS[ident], "hazard distinction")
    require(candidate["sourceObjectStatus"] == "BASE_CONFIRMED", "donor status")
    require(candidate["authoringProfileId"] == "ermak-msud-n-early-traction-research-only", "authoring profile")
    require(candidate["earlyMsud"] == "MSUD-N_PROFILE_DEPENDENT" and
            candidate["lateMsud"] == "MSUD-015_NOT_EQUIVALENT", "MSUD separation")
    require(candidate["exactInstalledVariant"] == "UNKNOWN" and
            candidate["unknownVariantDisposition"] == "BLOCKED", "unknown profile")
    require(candidate["publicationStatus"] == "CANDIDATE" and
            candidate["runtimeImport"] is False and candidate["executable"] is False,
            "publication block")
    for field in ("actionAuthorityGranted", "sourceAuthorityVerified",
                  "exactInstalledVariantConfirmed", "substantiveSafetyReviewed"):
        require(candidate[field] is False, "authority " + field)
    require(candidate["warningGate"] == WARNING and candidate["safePolicy"] == POLICY,
            "warning/safety")
    require(candidate["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "device QA")
    require(len(candidate["mustRemainDistinctFrom"]) == 3 and
            len(set(candidate["mustRemainDistinctFrom"])) == 3 and
            ident not in candidate["mustRemainDistinctFrom"], "neighbor separation")
    require(set(candidate["sourceRecords"]) == SOURCES, "source classes")
    refs = candidate["sourceRecords"]
    require(refs["donor"]["commit"] == PIN and refs["donor"]["blobSha"] == BLOB and
            refs["donor"]["objectId"] == ident and
            refs["donor"]["rawGzipIndependentlyDecoded"] is False, "pinned donor")
    require(refs["manufacturer"]["status"] == "ARCHIVAL_VARIANT_DEPENDENT", "archival status")
    require(refs["brakeRules2026"]["status"] ==
            "CURRENT_DOCUMENT_IDENTIFIED_SPECIFIC_AUTHORITY_UNVERIFIED", "2026 rules authority")
    require(refs["maintenance3508"]["status"] == "MAINTENANCE_SCOPE_NOT_CREW_AUTHORITY",
            "3508 scope")
    require(refs["memo"]["status"] == "HISTORICAL_NOT_OPERATIONAL" and
            refs["practice"]["status"] == "UNRESOLVED_NO_AUTHORITY", "historical status")
    require(all(record["currentOperatingAuthority"] is False for record in refs.values()),
            "source grants authority")
    require([x["resolution"] for x in candidate["sourceConflicts"]] ==
            ["NO_CAUSE_INFERENCE", "PROFILE_BLOCKED", "SOURCE_AUTHORITY_BLOCKED"], "conflicts")
    require(set(candidate["versions"]) == {"SHORT", "DETAILED"}, "versions")
    for mode in ("SHORT", "DETAILED"):
        check_graph(candidate["versions"][mode], mode)
    extensions = candidate["informationExtensions"]
    require(len(extensions) == 5 and len(set(e["id"] for e in extensions)) == 5,
            "five independent extensions")
    require([e["version"] for e in extensions] ==
            ["SHORT", "SHORT", "DETAILED", "DETAILED", "DETAILED"], "extension versions")
    require([e["sourceRefs"] for e in extensions] == EXT_SOURCES, "extension provenance")
    for index, extension in enumerate(extensions, 1):
        require(extension["id"] == ident + "-INFO-" + str(index) and
                extension["title"] and extension["text"] and extension["locator"],
                "extension identity/text")
        require(extension["visibility"] == WARNING and
                extension["warningRequired"] is True and
                extension["actionAuthorityGranted"] is False and
                extension["executable"] is False and
                extension["operationalSteps"] == [], "extension safety")
        require(extension["applicability"] == {
            "exactEquipmentProfileConfirmed": False, "modernSchemeConfirmed": False},
            "extension applicability")
    crosschecks = candidate["independentCrosschecks"]
    require(len(crosschecks) == 4 and
            all(x["verifiedAt"] == "2026-11-06" for x in crosschecks),
            "crosschecks")


def negative(candidate):
    mutations = [
        (["originalId"], "ER-DIAG-060" if candidate["originalId"].endswith("059") else "ER-DIAG-059"),
        (["title"], "wrong"), (["symptom"], "wrong"), (["hazardCategory"], "OTHER"),
        (["sourceObjectStatus"], "EVOLUTION_CONFIRMED"),
        (["sourceObjectApplicability"], {}), (["sourceObjectSystemIds"], []),
        (["sourceObjectEquipmentRefs"], []), (["sourceObjectSourceRefs"], []),
        (["families"], ["2ES5K"]), (["profileApplicability"], ["msud_015_extended"]),
        (["lateProfileRule"], "AS_LISTED"), (["authoringProfileId"], "all"),
        (["earlyMsud"], "MSUD-015"), (["lateMsud"], "MSUD-N"),
        (["exactInstalledVariant"], "MSUD-N"), (["unknownVariantDisposition"], "ALLOWED"),
        (["publicationStatus"], "ACTIVE"), (["runtimeImport"], True),
        (["executable"], True), (["actionAuthorityGranted"], True),
        (["sourceAuthorityVerified"], True), (["exactInstalledVariantConfirmed"], True),
        (["substantiveSafetyReviewed"], True), (["deviceQA"], "PASS"),
        (["warningGate", "default"], "VISIBLE"),
        (["warningGate", "warningReadToEnd"], False),
        (["warningGate", "warningAcknowledged"], False),
        (["warningGate", "warningGrantsActionAuthority"], True),
        (["safePolicy", "operationsAllowed"], ["reset"]),
        (["safePolicy", "onlyPreviouslyRecorded"], False),
        (["safePolicy", "activeFaultImmediateStop"], False),
        (["sourceRecords", "donor", "commit"], "BAD"),
        (["sourceRecords", "donor", "blobSha"], "BAD"),
        (["sourceRecords", "donor", "rawGzipIndependentlyDecoded"], True),
        (["sourceRecords", "manufacturer", "status"], "CURRENT"),
        (["sourceRecords", "brakeRules2026", "status"], "CURRENT_CREW_AUTHORITY"),
        (["sourceRecords", "maintenance3508", "status"], "CREW_AUTHORIZED"),
        (["sourceRecords", "memo", "status"], "CURRENT"),
        (["sourceRecords", "practice", "status"], "VERIFIED"),
        (["sourceRecords", "brakeRules2026", "currentOperatingAuthority"], True),
        (["sourceConflicts", 0, "resolution"], "CAUSE_CONFIRMED"),
        (["mustRemainDistinctFrom"], [candidate["originalId"]]),
        (["versions", "SHORT", "nodes", 0, "responses", "YES"], "report-match"),
        (["versions", "SHORT", "nodes", 1, "responses", "NO"], "q-symptom"),
        (["versions", "SHORT", "nodes", 2, "responses", "UNKNOWN"], "report-match"),
        (["versions", "DETAILED", "nodes", 3, "responses", "NO"], "q-separation"),
        (["versions", "DETAILED", "nodes", 4, "responses", "UNKNOWN"], "q-provenance"),
        (["versions", "DETAILED", "nodes", 5, "operationRequested"], True),
        (["versions", "DETAILED", "nodes", 5, "causeConfirmed"], True),
        (["versions", "SHORT", "nodes", 0, "recordedOnly"], False),
        (["informationExtensions", 0, "sourceRefs"], ["unverified"]),
        (["informationExtensions", 0, "visibility", "warningAcknowledged"], False),
        (["informationExtensions", 0, "warningRequired"], False),
        (["informationExtensions", 0, "operationalSteps"], ["test"]),
        (["informationExtensions", 4, "actionAuthorityGranted"], True),
        (["independentCrosschecks", 0, "verifiedAt"], "2024-01-01"),
    ]
    for index, (path, value) in enumerate(mutations):
        mutated = copy.deepcopy(candidate)
        obj = mutated
        for key in path[:-1]:
            obj = obj[key]
        obj[path[-1]] = value
        try:
            check(mutated)
        except (AssertionError, KeyError):
            continue
        raise AssertionError("negative mutation escaped " + candidate["originalId"] + " " + str(index))
    return len(mutations)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    ledger = DATA["ledger"]
    require(ledger["scenarioIds"] == list(IDS) and
            [c["originalId"] for c in DATA["candidates"]] == list(IDS),
            "batch membership")
    require(ledger["donorPinnedSha"] == PIN and ledger["donorGzipBlobSha"] == BLOB and
            PACK["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"] == BLOB,
            "donor pin")
    require(ledger["status"] == "CANDIDATE" and ledger["runtimeImport"] is False and
            ledger["actionAuthorityGranted"] is False and
            ledger["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "ledger safety")
    for candidate in DATA["candidates"]:
        check(candidate)
    require(len({c["hazardCategory"] for c in DATA["candidates"]}) == 2, "hazard distinction")
    require(len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in DATA["candidates"]}) == 2,
            "independent evidence")
    print("STAGE18_BATCH19_PASS 2 scenarios SHORT=8 DETAILED=12 EXTENSIONS=5")
    if args.negative:
        print("STAGE18_BATCH19_NEGATIVE_PASS", sum(negative(c) for c in DATA["candidates"]))


if __name__ == "__main__":
    main()
