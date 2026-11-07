#!/usr/bin/env python3
"""Stage 7 closeout: source-first authoring gates only, NEVER operational approval."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "090d448d0e9de20d002edf07361764e524298bf8"
FILE = ROOT / "docs/diagnostics/STAGE7_AUXILIARY_CLOSEOUT_2026-11-04.json"
INVENTORY = ROOT / "docs/data-migration/diagnostic-corpus-analysis.json"
MIGRATION = ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
EXPECTED = {"fan-low-airflow", "fan-vibration", "compressor-overheat"}
EXPECTED_DISTINCT = {
    "fan-low-airflow": {"fan-vibration", "motor-fan-failure", "rectifier-overheat"},
    "fan-vibration": {"fan-low-airflow", "compressor-overheat", "aux-contactor-chatter"},
    "compressor-overheat": {"compressor-long-run", "compressor-pressure", "fan-vibration"},
}
VISIBILITY = {"default": "HIDDEN", "extendedEnabled": True, "warningReadToEnd": True,
              "warningAcknowledged": True, "warningGrantsActionAuthority": False}
POLICY = {"observationOnly": True, "onlyPreviouslyRecorded": True,
          "triState": ["YES", "NO", "UNKNOWN"], "unknownMustStop": True,
          "operationsAllowed": [], "unknownProfile": "BLOCKED"}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def graph(nodes, start, sources):
    ids = {n["id"]: n for n in nodes}
    require(len(ids) == len(nodes) and start in ids, "duplicate or missing node")
    require(all(n["operationRequested"] is False and n["causeConfirmed"] is False and
                len(n["sourceRefs"]) == 1 and n["sourceRefs"][0] in sources
                for n in nodes), "unsafe graph node or unknown source")
    for n in nodes:
        if n["type"] == "QUESTION":
            edges = n["responses"]
            require(set(edges) == {"YES", "NO", "UNKNOWN"} and
                    edges["YES"] != edges["NO"], "broken tri-state")
            require(all(target in ids for target in edges.values()) and
                    ids[edges["UNKNOWN"]]["type"] == "STOP", "UNKNOWN must STOP")
        else:
            require(n["type"] in {"STOP", "OBSERVATION_REPORT"} and
                    n["responses"] == {}, "terminal node performs action")
    seen = {start}
    queue = [start]
    while queue:
        for target in ids[queue.pop()]["responses"].values():
            if target not in seen:
                seen.add(target)
                queue.append(target)
    require(seen == set(ids), "unreachable graph node")
    require(any(n["type"] == "STOP" for n in nodes), "no STOP")

def validate_scenario(d, inventory, migration):
    sid = d["originalId"]
    require(sid in EXPECTED and d["scenarioId"] == "vl80s.diag." + sid and
            d["schemaVersion"] == "diagnostic-stage7-auxiliary-source-first/1" and
            d["stage"] == "7/51", "scenario identity")
    original = next((x for x in migration["scenarios"] if x["id"] == sid), None)
    row = next((x for x in inventory["rows"] if x["scenarioId"] == d["scenarioId"]), None)
    require(original is not None and row is not None and
            original["originLayer"] == "DiagnosticExtendedCatalog.kt" and
            d["title"] == original["title"] and d["summary"] == original["summary"] and
            d["category"] == original["category"] and
            row["graph"]["nodeCount"] == 3 and row["variantIds"] == ["vl80s-general"] and
            all(row[k] == "NOT_AUTHORED" for k in
                ("shortVersion", "detailedVersion", "shortExtendedBranch", "detailedExtendedBranch")),
            "pinned source/migration mismatch")
    require(d["donorPinnedSha"] == DONOR and d["donorOriginLayer"] == "DiagnosticExtendedCatalog.kt" and
            d["donorOriginalBlobSha"] == BLOB and d["donorGraphNodeCount"] == 3 and
            d["donorOriginalQuestions"] == [] and
            d["donorQuestionProvenance"] == "SEED_HAS_NO_EXPLICIT_QUESTIONS",
            "source provenance drift")
    require(d["authoringProfileId"] == "vl80s-general" and
            set(d["mustRemainDistinctFrom"]) ==
            {"vl80s.diag." + x for x in EXPECTED_DISTINCT[sid]}, "symptoms conflated")
    require(d["publicationStatus"] == "CANDIDATE" and
            all(d[k] is False for k in ("runtimeImport", "executable", "actionAuthorityGranted",
                                       "sourceAuthorityVerified", "exactInstalledVariantConfirmed",
                                       "substantiveSafetyReviewed")) and
            d["warningGate"] == VISIBILITY and d["safePolicy"] == POLICY and
            d["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "candidate safety bypass")
    sources = d["sourceRecords"]
    require(set(sources) == {"donor", "manual1990", "supplement"}, "source classes")
    ds = sources["donor"]
    require(ds["kind"] == "PINNED_DONOR_OFFLINE_CATALOG" and
            ds["repository"] == "DomEnota-hub/Test-" and ds["commit"] == DONOR and
            ds["blobSha"] == BLOB and ds["originalId"] == sid and
            ds["sourcePointer"] == 'Seed("' + sid + '")' and
            ds["excerpt"] == {k: original[k] for k in ("category", "title", "summary")} and
            ds["currentOperatingAuthority"] is False and ds["proceduresImported"] is False,
            "donor attribution")
    manual, supplement = sources["manual1990"], sources["supplement"]
    require(manual["kind"] == "HISTORICAL_FACTORY_MANUAL" and manual["year"] == 1990 and
            manual["isbn"] == "5-277-01048-3" and
            manual["url"] == "https://ru.djvu.online/file/wXVHhRmTUUuqq" and
            len(manual["verifiedLocators"]) == 2, "manual provenance")
    require(supplement["kind"] == ("PRACTICAL_REFERENCE_UNVERIFIED" if sid == "fan-low-airflow"
                                   else "HISTORICAL_FACTORY_APPENDIX"), "supplement kind")
    for src in (manual, supplement):
        require(src["sourceTextLocated"] is True and
                all(src[k] is False for k in
                    ("modernRevisionVerified", "exactInstalledEquipmentVerified",
                     "currentOperatingAuthority", "proceduresImported")) and
                src["verifiedLocators"] and src["url"], "source authority falsely granted")
    claims = d["historicalEvidenceClaims"]
    require(len(claims) == 3 and
            [c["sourceId"] for c in claims] == ["manual1990", "manual1990", "supplement"],
            "evidence attribution")
    for claim in claims:
        require(claim["locator"] in sources[claim["sourceId"]]["verifiedLocators"] and
                all(claim[k] is False for k in
                    ("provesCurrentEquipment", "provesFaultCause", "authorizesAction")),
                "historical claim promoted")
    require(set(d["versions"]) == {"SHORT", "DETAILED"}, "missing versions")
    seen_ids, seen_focus = set(), set()
    for version, count, routes, source_order in (
        ("SHORT", 6, 2, ["donor", "manual1990"]),
        ("DETAILED", 12, 3, ["donor", "manual1990", "supplement"]),
    ):
        v = d["versions"][version]
        require(v["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and
                v["independentTechnicalReview"] == "REQUIRED" and
                v["operatingInstructionsIncluded"] is False and
                len(v["nodes"]) == count and len(v["extendedRoutes"]) == routes,
                "version approval or node count")
        graph(v["nodes"], v["startNodeId"], sources)
        require([r["sourceId"] for r in v["extendedRoutes"]] == source_order,
                "source approach order")
        for r in v["extendedRoutes"]:
            require(r["approachId"] not in seen_ids and r["approachFocus"] not in seen_focus,
                    "duplicate source approach")
            seen_ids.add(r["approachId"])
            seen_focus.add(r["approachFocus"])
            require(r["version"] == version and r["sourcePointer"] and
                    r["approachSummary"] and
                    r["questionType"] == "ALREADY_RECORDED_FACT_ONLY" and
                    r["publicationStatus"] == "CANDIDATE" and
                    r["actionDisposition"] == "INFORMATION_ONLY" and
                    r["executable"] is False and r["actionAuthorityGranted"] is False and
                    r["operationalSteps"] == [] and
                    r["technicalClaimReview"] == "REQUIRES_EXPERT" and
                    r["applicability"] == {"profileId": "vl80s-general",
                                            "exactEquipmentProfileConfirmed": False,
                                            "modernSchemeConfirmed": False} and
                    r["visibility"] == VISIBILITY, "extension unsafe or wrong profile")
            graph(r["nodes"], r["startNodeId"], sources)
    require(d["versions"]["SHORT"]["nodes"] != d["versions"]["DETAILED"]["nodes"],
            "SHORT and DETAILED duplicated")
    return sid

def validate_bundle(bundle, inventory, migration):
    ledger = bundle["ledger"]
    require(ledger["schemaVersion"] == "stage7-auxiliary-closeout/1" and
            ledger["stage"] == "7/51" and ledger["donorPinnedSha"] == DONOR and
            ledger["previousResearchCount"] == 5 and
            ledger["stage7CurrentResearchCount"] == 8 and
            ledger["stage7OriginalTarget"] == 8 and
            ledger["stage7RemainingForTarget"] == 0 and
            ledger["technicalCompletion"] in
                {"PENDING_GREEN_CI", "TECHNICALLY_COMPLETE_DEVICE_QA_DEFERRED"} and
            ledger["publicationStatus"] == "CANDIDATE" and
            ledger["runtimeImport"] is False and ledger["actionAuthorityGranted"] is False and
            ledger["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA" and
            (ROOT / ledger["finalDeviceRegistry"]).exists(), "ledger or device registry")
    require(inventory["donorCommit"] == DONOR and
            inventory["uniqueScenarioCount"] == 340 and
            inventory["preservedGraphNodes"] == 3902, "baseline corpus drift")
    require(len(bundle["candidates"]) == 3, "wrong number of candidates")
    ids = [validate_scenario(d, inventory, migration) for d in bundle["candidates"]]
    require(set(ids) == EXPECTED and len(set(ids)) == 3 and
            set(ledger["addedScenarioIds"]) == {"vl80s.diag." + x for x in EXPECTED},
            "candidate coverage")
    return ids

class Adversarial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = json.loads(FILE.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        cls.migration = json.loads(MIGRATION.read_text(encoding="utf-8"))["sourceObject"]

    def rejects(self, change, index=0):
        d = copy.deepcopy(self.bundle["candidates"][index])
        change(d)
        with self.assertRaises(ValueError):
            validate_scenario(d, self.inventory, self.migration)

    def test_all(self):
        self.assertEqual(set(validate_bundle(self.bundle, self.inventory, self.migration)), EXPECTED)
    def test_donor_blob(self):
        self.rejects(lambda d: d.update(donorOriginalBlobSha="wrong"))
    def test_original_id(self):
        self.rejects(lambda d: d.update(originalId="fan-vibration"))
    def test_unsafe_runtime(self):
        self.rejects(lambda d: d.update(runtimeImport=True))
    def test_unsafe_action(self):
        self.rejects(lambda d: d.update(actionAuthorityGranted=True))
    def test_unverified_variant(self):
        self.rejects(lambda d: d.update(exactInstalledVariantConfirmed=True))
    def test_warning_bypass(self):
        self.rejects(lambda d: d["warningGate"].update(default="VISIBLE"))
    def test_ack_action_bypass(self):
        self.rejects(lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["visibility"].update(warningGrantsActionAuthority=True))
    def test_unknown_terminal(self):
        self.rejects(lambda d: d["versions"]["SHORT"]["nodes"][1]["responses"].update(UNKNOWN="report-yes"))
    def test_unreachable_node(self):
        self.rejects(lambda d: d["versions"]["DETAILED"]["nodes"][2]["responses"].update(NO="report-absence"))
    def test_unsafe_operation(self):
        self.rejects(lambda d: d["versions"]["DETAILED"]["extendedRoutes"][0]["nodes"][0].update(operationRequested=True))
    def test_source_authority(self):
        self.rejects(lambda d: d["sourceRecords"]["manual1990"].update(currentOperatingAuthority=True))
    def test_claim_as_proof(self):
        self.rejects(lambda d: d["historicalEvidenceClaims"][0].update(provesFaultCause=True))
    def test_fake_device_qa(self):
        self.rejects(lambda d: d.update(deviceQA="PASSED"))
    def test_duplicate_approach(self):
        self.rejects(lambda d: d["versions"]["DETAILED"]["extendedRoutes"][1].update(approachFocus="DONOR_AIRFLOW_SYMPTOM"))
    def test_profile_promotion(self):
        self.rejects(lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["applicability"].update(exactEquipmentProfileConfirmed=True))
    def test_supplement_status(self):
        self.rejects(lambda d: d["sourceRecords"]["supplement"].update(kind="CURRENT_NORMATIVE"), index=0)

if __name__ == "__main__":
    if "--negative" in sys.argv:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        bundle = json.loads(FILE.read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        migration = json.loads(MIGRATION.read_text(encoding="utf-8"))["sourceObject"]
        print("PASS Stage7 auxiliary research", validate_bundle(bundle, inventory, migration))
