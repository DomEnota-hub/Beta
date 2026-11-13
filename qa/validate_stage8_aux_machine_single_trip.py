#!/usr/bin/env python3
"""Stage8 single auxiliary machine trip: provenance, graph and fail-closed negative QA."""
import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/diagnostics/STAGE8_AUX_MACHINE_SINGLE_TRIP_2026-11-05.json"
MIG = ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
INV = ROOT / "docs/data-migration/diagnostic-corpus-analysis.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "0d94801dcbe1d96e1a551a9dac8fef2a808b9029"
ID = "aux-machine-single-trip"
SID = "vl80s.diag." + ID
QUESTIONS = [
    "Остальные вспомогательные машины сохраняют нормальную работу?",
    "Отключение связано с прогревом, ростом нагрузки или необычным звуком?",
    "Есть запах, дым, сильная вибрация или опасный нагрев?",
]
LOC = [
    "VI §27, печ. стр. 105–106, рис. 142: тепловые реле ТРТ защищают приводы вспомогательных машин от перегрузок",
    "XI, защита вспомогательных цепей, печ. стр. 209: реле 113 общей защиты и тепловые реле отдельных приводов различаются",
    "Раздел Б, табл. 14, печ. стр. 281–282: отдельная сигнальная лампа МК/МВ1–МВ4/МН при отключении одной машины",
    "«Цепи управления вспомогательными машинами», абзацы о контакторах 127–130, 133 и тепловых реле (перепечатка 2015, заголовок [01-2004])",
    "«Цепи управления вспомогательными машинами», абзац о самовозврате тепловых реле и запрете автоматического повторного включения (перепечатка 2015)",
]
WARNING = {"default": "HIDDEN", "extendedEnabled": True, "warningReadToEnd": True,
           "warningAcknowledged": True, "warningGrantsActionAuthority": False}
POLICY = {"observationOnly": True, "onlyPreviouslyRecorded": True,
          "triState": ["YES", "NO", "UNKNOWN"], "unknownMustStop": True,
          "operationsAllowed": [], "unknownProfile": "BLOCKED"}
DISTINCT = {
    "vl80s.diag.aux-common-loss", "vl80s.diag.aux-contactor-chatter",
    "vl80s.diag.motor-fan-failure", "vl80s.diag.compressor-overheat",
    "vl80s.diag.oil-pump-failure", "vl80s.diag.phase-splitter-no-start",
}
FORBIDDEN = re.compile(
    r"(?i)\b(?:включите|перемкните|замкните|вскройте|измерьте|запустите|"
    r"сбросьте|отключите\s+защиту|установите\s+перемычку|повторите\s+пуск)\b"
)

def need(condition, label):
    if not condition:
        raise ValueError(label)

def graph(nodes, start, sources, expected_count):
    ids = {n["id"]: n for n in nodes}
    need(len(ids) == len(nodes) == expected_count and start in ids, "graph count or IDs")
    visited, queue = set(), [start]
    while queue:
        key = queue.pop()
        if key in visited:
            continue
        visited.add(key)
        n = ids[key]
        need(n["recordedOnly"] is True and n["operationRequested"] is False
             and n["causeConfirmed"] is False and n["sourceRefs"]
             and set(n["sourceRefs"]) <= sources, "unsafe node")
        need(not FORBIDDEN.search(n["text"]), "imperative operation")
        if n["type"] == "QUESTION":
            edges = n["responses"]
            need(set(edges) == {"YES", "NO", "UNKNOWN"} and
                 edges["YES"] != edges["NO"] and
                 all(target in ids for target in edges.values()) and
                 ids[edges["UNKNOWN"]]["type"] == "STOP", "unsafe tri-state")
            queue.extend(edges.values())
        else:
            need(n["type"] in {"STOP", "OBSERVATION_REPORT"} and not n["responses"],
                 "unsafe terminal")
    need(visited == set(ids), "unreachable graph node")
    # All graph nodes were visited and safety-checked, not only the happy path.

def validate(doc, migration, inventory):
    need(set(doc) == {"ledger", "candidates"} and len(doc["candidates"]) == 1, "envelope")
    l, d = doc["ledger"], doc["candidates"][0]
    orig = next((x for x in migration["scenarios"] if x["id"] == ID), None)
    row = next((x for x in inventory["rows"] if x["scenarioId"] == SID), None)
    need(orig is not None and row is not None, "missing donor mapping")
    need(l["stage"] == "8/51" and l["donorPinnedSha"] == DONOR and
         l["baseHead"] == "1754fce72b858d9b735f37741f895d9cdf181375" and
         l["addedScenarioIds"] == [SID] and
         l["stage8OverallStatus"] == "IN_PROGRESS_NOT_CLOSED" and
         l["publicationStatus"] == "CANDIDATE" and
         l["runtimeImport"] is False and l["actionAuthorityGranted"] is False and
         l["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "ledger")
    need(d["schemaVersion"] == "diagnostic-stage8-aux-machine-single-trip-source-first/1"
         and d["stage"] == "8/51" and d["scenarioId"] == SID
         and d["originalId"] == ID and d["title"] == orig["title"]
         and d["summary"] == orig["summary"] and d["category"] == orig["category"]
         and orig["originLayer"] == d["donorOriginLayer"] == "DiagnosticCompletionCatalog.kt"
         and orig["runtimeStatus"] == "VISIBLE_CURRENT_DIAGNOSTIC_REPOSITORY"
         and d["donorPinnedSha"] == DONOR and d["donorOriginalBlobSha"] == BLOB
         and d["donorGraphNodeCount"] == row["graph"]["nodeCount"] == 3
         and d["donorOriginalQuestions"] == QUESTIONS
         and d["donorQuestionProvenance"] == "PINNED_DONOR_QUESTION_TEXT_ONLY_NO_ACTIONS"
         and row["variantIds"] == ["vl80s-general"]
         and all(row[k] == "NOT_AUTHORED" for k in
                 ("shortVersion", "detailedVersion", "shortExtendedBranch",
                  "detailedExtendedBranch")), "source parity")
    need(d["canonicalGroup"] == "ONE_AUXILIARY_DRIVE_RECURRENT_TRIP_NOT_COMMON_LOSS"
         and set(d["mustRemainDistinctFrom"]) == DISTINCT, "distinct symptoms")
    need(d["authoringProfileId"] == "vl80s-general" and
         d["publicationStatus"] == "CANDIDATE" and
         d["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA" and
         all(d[k] is False for k in
             ("runtimeImport", "executable", "actionAuthorityGranted",
              "sourceAuthorityVerified", "exactInstalledVariantConfirmed",
              "substantiveSafetyReviewed")) and
         d["warningGate"] == WARNING and d["safePolicy"] == POLICY, "safety gate")
    sources = d["sourceRecords"]
    need(set(sources) == {"donor", "manual1990", "technical2004"}, "source set")
    s, m, t = sources["donor"], sources["manual1990"], sources["technical2004"]
    need(s["repository"] == "DomEnota-hub/Test-" and s["commit"] == DONOR and
         s["blobSha"] == BLOB and s["originalId"] == ID and
         s["path"] == "app/src/main/java/ru/railbrake/calculator/core/DiagnosticCompletionCatalog.kt" and
         s["sourcePointer"] == 'id = "aux-machine-single-trip"' and
         s["originalQuestions"] == QUESTIONS and
         s["kind"] == "PINNED_DONOR_OFFLINE_CATALOG" and
         s["currentOperatingAuthority"] is False and
         s["proceduresImported"] is False and
         s["containsHistoricalUnsafeProcedures"] is True, "donor source")
    need(m["kind"] == "HISTORICAL_FACTORY_MANUAL" and m["year"] == 1990
         and m["isbn"] == "5-277-01048-3"
         and m["url"] == "https://djvu.online/file/wXVHhRmTUUuqq"
         and m["verifiedLocators"] == LOC[:3], "manual identity")
    need(t["kind"] == "HISTORICAL_DEPOT_TECHNICAL_PUBLICATION_REPRINT" and
         t["originalYearClaim"] == 2004 and
         t["reprintDate"] == "2015-05-24" and
         t["originalEditionIndependentlyVerified"] is False and
         t["verifiedLocators"] == LOC[3:] and
         t["url"] == "https://scbist.com/xx2/43048-01-2004-elektrovoz-vl80s-opisanie-cepei-upravleniya-i-ustranenie-neispravnostei.html",
         "depot account identity")
    for item in (m, t):
        need(item["sourceTextLocated"] is True and
             item["containsHistoricalUnsafeProcedures"] is True and
             all(item[k] is False for k in
                 ("modernRevisionVerified", "exactInstalledEquipmentVerified",
                  "currentOperatingAuthority", "proceduresImported")), "historical authority")
    claims = d["historicalEvidenceClaims"]
    need(len(claims) == 5 and
         [x["locator"] for x in claims] == LOC and
         [x["sourceId"] for x in claims] ==
         ["manual1990"] * 3 + ["technical2004"] * 2 and
         all(x["provesCurrentEquipment"] is False and
             x["provesFaultCause"] is False and
             x["authorizesAction"] is False for x in claims), "evidence authority")
    need(set(d["versions"]) == {"SHORT", "DETAILED"}, "versions")
    approaches, focuses = set(), set()
    for version, count, ext_count in (("SHORT", 6, 2), ("DETAILED", 12, 3)):
        v = d["versions"][version]
        need(v["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and
             v["independentTechnicalReview"] == "REQUIRED" and
             v["operatingInstructionsIncluded"] is False and
             len(v["extendedRoutes"]) == ext_count, "version status")
        graph(v["nodes"], v["startNodeId"], set(sources), count)
        for e in v["extendedRoutes"]:
            need(e["approachId"] not in approaches and
                 e["approachFocus"] not in focuses, "duplicate approach")
            approaches.add(e["approachId"])
            focuses.add(e["approachFocus"])
            need(e["version"] == version and e["sourceId"] in sources and
                 e["sourceLocator"] in
                 ([s["sourcePointer"]] if e["sourceId"] == "donor" else
                  m["verifiedLocators"] if e["sourceId"] == "manual1990" else
                  t["verifiedLocators"]) and
                 e["questionType"] == "ALREADY_RECORDED_FACT_ONLY" and
                 e["publicationStatus"] == "CANDIDATE" and
                 e["actionDisposition"] == "INFORMATION_ONLY" and
                 e["technicalClaimReview"] == "REQUIRES_EXPERT" and
                 e["operationalSteps"] == [] and
                 e["executable"] is False and
                 e["actionAuthorityGranted"] is False and
                 e["applicability"] == {
                     "profileId": "vl80s-general",
                     "exactEquipmentProfileConfirmed": False,
                     "modernSchemeConfirmed": False} and
                 e["visibility"] == WARNING, "extension authority")
            graph(e["nodes"], e["startNodeId"], {e["sourceId"]}, 4)
    need(len(approaches) == len(focuses) == 5, "extension coverage")
    return True

class NegativeQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.migration = json.loads(MIG.read_text(encoding="utf-8"))["sourceObject"]
        cls.inventory = json.loads(INV.read_text(encoding="utf-8"))
    def reject(self, mutate):
        doc = copy.deepcopy(self.doc)
        mutate(doc["candidates"][0])
        with self.assertRaises(ValueError):
            validate(doc, self.migration, self.inventory)
    def test_baseline(self):
        self.assertTrue(validate(self.doc, self.migration, self.inventory))
    def test_negative_mutations(self):
        cases = [
            ("donor_blob", lambda d: d.update(donorOriginalBlobSha="fake")),
            ("donor_id", lambda d: d.update(originalId="aux-common-loss")),
            ("donor_question", lambda d: d["donorOriginalQuestions"].append("fake")),
            ("source_pointer", lambda d: d["sourceRecords"]["donor"].update(sourcePointer="fake")),
            ("source_commit", lambda d: d["sourceRecords"]["donor"].update(commit="fake")),
            ("manual_locator", lambda d: d["sourceRecords"]["manual1990"].update(verifiedLocators=[])),
            ("depot_locator", lambda d: d["sourceRecords"]["technical2004"].update(verifiedLocators=[])),
            ("depot_edition", lambda d: d["sourceRecords"]["technical2004"].update(originalEditionIndependentlyVerified=True)),
            ("modern_manual", lambda d: d["sourceRecords"]["manual1990"].update(modernRevisionVerified=True)),
            ("modern_depot", lambda d: d["sourceRecords"]["technical2004"].update(modernRevisionVerified=True)),
            ("profile", lambda d: d.update(exactInstalledVariantConfirmed=True)),
            ("authority", lambda d: d.update(sourceAuthorityVerified=True)),
            ("runtime", lambda d: d.update(runtimeImport=True)),
            ("execute", lambda d: d.update(executable=True)),
            ("action", lambda d: d.update(actionAuthorityGranted=True)),
            ("safety", lambda d: d.update(substantiveSafetyReviewed=True)),
            ("warning_scroll", lambda d: d["warningGate"].update(warningReadToEnd=False)),
            ("warning_permission", lambda d: d["warningGate"].update(warningGrantsActionAuthority=True)),
            ("profile_unknown", lambda d: d["safePolicy"].update(unknownProfile="ALLOW")),
            ("allowed_operation", lambda d: d["safePolicy"].update(operationsAllowed=["switch"])),
            ("question_operation", lambda d: d["versions"]["SHORT"]["nodes"][0].update(operationRequested=True)),
            ("imperative", lambda d: d["versions"]["SHORT"]["nodes"][1].update(text="Включите привод")),
            ("record_only", lambda d: d["versions"]["DETAILED"]["nodes"][0].update(recordedOnly=False)),
            ("unknown_to_report", lambda d: d["versions"]["SHORT"]["nodes"][1]["responses"].update(UNKNOWN="report-single")),
            ("missing_target", lambda d: d["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="missing")),
            ("unreachable", lambda d: d["versions"]["SHORT"]["nodes"][0]["responses"].update(NO="stop-unknown")),
            ("terminal_operation", lambda d: d["versions"]["DETAILED"]["nodes"][5].update(operationRequested=True)),
            ("extension_duplicate", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][0].update(approachId="vl80s.aux-machine-single-trip.short-1")),
            ("extension_operation", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][2].update(operationalSteps=["start"])),
            ("extension_profile", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][2]["applicability"].update(exactEquipmentProfileConfirmed=True)),
            ("extension_unknown", lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["nodes"][0]["responses"].update(UNKNOWN="record-yes")),
            ("extension_warning", lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["visibility"].update(warningAcknowledged=False)),
            ("claim_action", lambda d: d["historicalEvidenceClaims"][0].update(authorizesAction=True)),
            ("conflate", lambda d: d.update(canonicalGroup="COMMON_LOSS")),
            ("device_pass", lambda d: d.update(deviceQA="PASS")),
        ]
        for label, mutator in cases:
            with self.subTest(label=label):
                self.reject(mutator)

if __name__ == "__main__":
    unittest.main()
