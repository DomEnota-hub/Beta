#!/usr/bin/env python3
"""Stage8 heater-fault source-first authoring and fail-closed negative QA."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/diagnostics/STAGE8_MOTOR_FAN_FAILURE_2026-11-04.json"
MIG = ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
INV = ROOT / "docs/data-migration/diagnostic-corpus-analysis.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "090d448d0e9de20d002edf07361764e524298bf8"
ID = "heater-fault"
SID = "vl80s.diag." + ID
PTR = 'Seed("heater-fault")'
LOC = [
    "§55 «Электрокалорифер. Электропечь», печ. стр. 146–147, рис. 195–196: отдельные приборы обогрева стекла и кабины",
    "IX §1, печ. стр. 179–180, рис. 231: размещение печей и ограждений в кабине",
    "XI §2, печ. стр. 205–207, рис. 245: однофазные цепи печей и калорифера; группы печей и контакторы",
]
QUESTIONS = []
WARNING = dict(default="HIDDEN", extendedEnabled=True, warningReadToEnd=True,
               warningAcknowledged=True, warningGrantsActionAuthority=False)
POLICY = dict(observationOnly=True, onlyPreviouslyRecorded=True,
              triState=["YES", "NO", "UNKNOWN"], unknownMustStop=True,
              operationsAllowed=[], unknownProfile="BLOCKED")
DISTINCT = {
    "vl80s.diag.aux-common-loss", "vl80s.diag.aux-contactor-chatter",
    "vl80s.diag.motor-fan-failure", "vl80s.diag.fan-low-airflow",
    "vl80s.diag.fire-alarm-signal",
}

def need(value, message):
    if not value:
        raise ValueError(message)

def graph(nodes, start, sources):
    ids = {n["id"]: n for n in nodes}
    need(len(ids) == len(nodes) and start in ids, "duplicate/missing graph ID")
    seen, pending = {start}, [start]
    while pending:
        n = ids[pending.pop()]
        need(n["recordedOnly"] is True and n["operationRequested"] is False
             and n["causeConfirmed"] is False and bool(n["sourceRefs"])
             and set(n["sourceRefs"]) <= sources, "unsafe graph node")
        if n["type"] == "QUESTION":
            edges = n["responses"]
            need(set(edges) == {"YES", "NO", "UNKNOWN"}
                 and edges["YES"] != edges["NO"]
                 and all(target in ids for target in edges.values())
                 and ids[edges["UNKNOWN"]]["type"] == "STOP", "unsafe tri-state")
            for target in edges.values():
                if target not in seen:
                    seen.add(target)
                    pending.append(target)
        else:
            need(n["type"] in {"STOP", "OBSERVATION_REPORT"} and not n["responses"],
                 "unsafe terminal")
    need(seen == set(ids), "unreachable nodes")
    # Explicitly cover unreachable nodes as well, including source and action flags.
    for n in nodes:
        need(n["recordedOnly"] is True and n["operationRequested"] is False
             and n["causeConfirmed"] is False and bool(n["sourceRefs"])
             and set(n["sourceRefs"]) <= sources, "unsafe unreachable node")

def validate(doc, migration, inventory):
    need(set(doc) == {"ledger", "candidates"} and len(doc["candidates"]) == 1, "envelope")
    ledger, d = doc["ledger"], doc["candidates"][0]
    orig = next((x for x in migration["scenarios"] if x["id"] == ID), None)
    row = next((x for x in inventory["rows"] if x["scenarioId"] == SID), None)
    need(orig is not None and row is not None, "missing preserved source")
    need(ledger["stage"] == "8/51" and ledger["donorPinnedSha"] == DONOR
         and ledger["addedScenarioIds"] == [SID] and ledger["baseHead"] == "e2ebe859209de9b2320263d0a5e2c42e629ab90a"
         and ledger["stage8OverallStatus"] == "IN_PROGRESS_NOT_CLOSED"
         and ledger["publicationStatus"] == "CANDIDATE"
         and ledger["runtimeImport"] is False
         and ledger["actionAuthorityGranted"] is False
         and ledger["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "ledger")
    need(d["schemaVersion"] == "diagnostic-stage8-heater-fault-source-first/1"
         and d["stage"] == "8/51" and d["scenarioId"] == SID
         and d["originalId"] == ID and d["title"] == orig["title"]
         and d["summary"] == orig["summary"] and d["category"] == orig["category"]
         and orig["originLayer"] == "DiagnosticExtendedCatalog.kt"
         and orig["runtimeStatus"] == "VISIBLE_CURRENT_DIAGNOSTIC_REPOSITORY"
         and d["donorPinnedSha"] == DONOR and d["donorOriginalBlobSha"] == BLOB
         and d["donorOriginLayer"] == "DiagnosticExtendedCatalog.kt"
         and d["donorGraphNodeCount"] == row["graph"]["nodeCount"] == 3
         and d["donorOriginalQuestions"] == QUESTIONS
         and d["donorQuestionProvenance"] == "SEED_HAS_NO_EXPLICIT_QUESTIONS"
         and row["variantIds"] == ["vl80s-general"]
         and all(row[k] == "NOT_AUTHORED" for k in
                 ("shortVersion", "detailedVersion", "shortExtendedBranch",
                  "detailedExtendedBranch")), "origin/parity")
    need(d["canonicalGroup"] == "CAB_HEATER_VS_WINDSCREEN_CALORIFIER_AND_OVERHEAT"
         and set(d["mustRemainDistinctFrom"]) == DISTINCT, "symptom boundaries")
    need(d["authoringProfileId"] == "vl80s-general"
         and d["publicationStatus"] == "CANDIDATE"
         and d["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA"
         and all(d[k] is False for k in
                 ("runtimeImport", "executable", "actionAuthorityGranted",
                  "sourceAuthorityVerified", "exactInstalledVariantConfirmed",
                  "substantiveSafetyReviewed"))
         and d["warningGate"] == WARNING and d["safePolicy"] == POLICY,
         "source/profile/safety gate")
    sources = d["sourceRecords"]
    need(set(sources) == {"donor", "manual1990"}, "source set")
    s, m = sources["donor"], sources["manual1990"]
    need(s["kind"] == "PINNED_DONOR_OFFLINE_CATALOG"
         and s["repository"] == "DomEnota-hub/Test-" and s["commit"] == DONOR
         and s["blobSha"] == BLOB
         and s["path"] == "app/src/main/java/ru/railbrake/calculator/core/DiagnosticExtendedCatalog.kt"
         and s["sourcePointer"] == PTR and s["originalId"] == ID
         and s["originalQuestions"] == QUESTIONS
         and s["currentOperatingAuthority"] is False
         and s["proceduresImported"] is False
         and s["containsHistoricalUnsafeProcedures"] is False, "donor provenance")
    need(m["kind"] == "HISTORICAL_FACTORY_MANUAL"
         and m["year"] == 1990 and m["isbn"] == "5-277-01048-3"
         and m["url"] == "https://djvu.online/file/wXVHhRmTUUuqq"
         and m["verifiedLocators"] == LOC and m["sourceTextLocated"] is True
         and m["containsHistoricalUnsafeProcedures"] is True
         and all(m[k] is False for k in
                 ("modernRevisionVerified", "exactInstalledEquipmentVerified",
                  "currentOperatingAuthority", "proceduresImported")), "manual authority")
    claims = d["historicalEvidenceClaims"]
    need(len(claims) == 3 and {x["locator"] for x in claims} == set(LOC)
         and all(x["sourceId"] == "manual1990"
                 and x["confidence"] == "HISTORICAL_DESCRIPTION_ONLY"
                 and all(x[k] is False for k in
                         ("provesCurrentEquipment", "provesFaultCause", "authorizesAction"))
                 for x in claims), "historical claims")
    need(set(d["versions"]) == {"SHORT", "DETAILED"}, "versions")
    approaches, focuses = set(), set()
    for name, count, ext_count in (("SHORT", 6, 2), ("DETAILED", 12, 3)):
        v = d["versions"][name]
        need(v["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED"
             and v["independentTechnicalReview"] == "REQUIRED"
             and v["operatingInstructionsIncluded"] is False
             and len(v["nodes"]) == count and len(v["extendedRoutes"]) == ext_count,
             "version counts")
        graph(v["nodes"], v["startNodeId"], set(sources))
        for e in v["extendedRoutes"]:
            need(e["approachId"] not in approaches and
                 e["approachFocus"] not in focuses, "duplicate extension")
            approaches.add(e["approachId"])
            focuses.add(e["approachFocus"])
            need(e["version"] == name and e["sourceId"] in sources
                 and e["sourceLocator"] in
                 (LOC if e["sourceId"] == "manual1990" else [PTR])
                 and e["questionType"] == "ALREADY_RECORDED_FACT_ONLY"
                 and e["publicationStatus"] == "CANDIDATE"
                 and e["actionDisposition"] == "INFORMATION_ONLY"
                 and e["technicalClaimReview"] == "REQUIRES_EXPERT"
                 and e["operationalSteps"] == []
                 and e["executable"] is False and e["actionAuthorityGranted"] is False
                 and e["applicability"] == {
                     "profileId": "vl80s-general",
                     "exactEquipmentProfileConfirmed": False,
                     "modernSchemeConfirmed": False}
                 and e["visibility"] == WARNING, "extension safety")
            graph(e["nodes"], e["startNodeId"], set(sources))
    need(len(approaches) == len(focuses) == 5, "extension count")
    return True

class NegativeQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.mig = json.loads(MIG.read_text(encoding="utf-8"))["sourceObject"]
        cls.inv = json.loads(INV.read_text(encoding="utf-8"))
    def reject(self, mutate):
        doc = copy.deepcopy(self.doc)
        mutate(doc["candidates"][0])
        with self.assertRaises(ValueError):
            validate(doc, self.mig, self.inv)
    def test_baseline(self):
        self.assertTrue(validate(self.doc, self.mig, self.inv))
    def test_negative_mutations(self):
        cases = [
            ("donor_blob", lambda d: d.update(donorOriginalBlobSha="invented")),
            ("original_id", lambda d: d.update(originalId="fan-low-airflow")),
            ("source_pointer", lambda d: d["sourceRecords"]["donor"].update(sourcePointer="fake")),
            ("source_commit", lambda d: d["sourceRecords"]["donor"].update(commit="wrong")),
            ("source_questions", lambda d: d.update(donorOriginalQuestions=["invented"])),
            ("manual_locator", lambda d: d["sourceRecords"]["manual1990"].update(verifiedLocators=[])),
            ("manual_authority", lambda d: d["sourceRecords"]["manual1990"].update(currentOperatingAuthority=True)),
            ("modern_scheme", lambda d: d["sourceRecords"]["manual1990"].update(modernRevisionVerified=True)),
            ("profile", lambda d: d.update(exactInstalledVariantConfirmed=True)),
            ("source_authority", lambda d: d.update(sourceAuthorityVerified=True)),
            ("runtime", lambda d: d.update(runtimeImport=True)),
            ("executable", lambda d: d.update(executable=True)),
            ("action", lambda d: d.update(actionAuthorityGranted=True)),
            ("warning_bypass", lambda d: d["warningGate"].update(warningReadToEnd=False)),
            ("warning_action", lambda d: d["warningGate"].update(warningGrantsActionAuthority=True)),
            ("unknown_profile", lambda d: d["safePolicy"].update(unknownProfile="ALLOW")),
            ("new_operation", lambda d: d["versions"]["SHORT"]["nodes"][0].update(operationRequested=True)),
            ("unrecorded_probe", lambda d: d["versions"]["DETAILED"]["nodes"][0].update(recordedOnly=False)),
            ("unknown_to_report", lambda d: d["versions"]["SHORT"]["nodes"][1]["responses"].update(UNKNOWN="report-identified")),
            ("bad_graph_target", lambda d: d["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="missing")),
            ("unreachable", lambda d: d["versions"]["SHORT"]["nodes"][0]["responses"].update(NO="stop-unknown")),
            ("unsafe_terminal", lambda d: d["versions"]["SHORT"]["nodes"][2].update(operationRequested=True)),
            ("ext_duplicate", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][0].update(approachId="vl80s.heater-fault.short-1")),
            ("ext_operation", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][2].update(operationalSteps=["start"])),
            ("ext_locator", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][2].update(sourceLocator="fake")),
            ("ext_profile", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][2]["applicability"].update(exactEquipmentProfileConfirmed=True)),
            ("ext_warning", lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["visibility"].update(warningAcknowledged=False)),
            ("claim_authority", lambda d: d["historicalEvidenceClaims"][0].update(authorizesAction=True)),
            ("conflate_heater_with_airflow", lambda d: d.update(canonicalGroup="FAN_LOW_AIRFLOW")),
            ("device_pass", lambda d: d.update(deviceQA="PASS")),
        ]
        for label, mutator in cases:
            with self.subTest(label=label):
                self.reject(mutator)

if __name__ == "__main__":
    unittest.main()
