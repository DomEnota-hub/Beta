#!/usr/bin/env python3
"""Stage8 phase-splitter research candidate: provenance, graph and negative safety gates."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/diagnostics/STAGE8_PHASE_SPLITTER_NO_START_2026-11-04.json"
MIG = ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
INV = ROOT / "docs/data-migration/diagnostic-corpus-analysis.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "7a222f1eca7be9438d8a8dbad937235dec83b7ff"
ID = "phase-splitter-no-start"
SID = "vl80s.diag." + ID
LOC = {
 "manual1990": [
  "XI §5, печ. стр. 221, рис. 254: контакторы 119/125 и реле 249 при пуске ФР",
  "XI §5, печ. стр. 221–222, рис. 254–255: реле 259/260 и связь с вспомогательными машинами"],
 "article2005": [
  "Публикация [09-2005], репост 03.08.2015: ПУСК ФР ПРИ НАЛИЧИИ ПАНЕЛИ ПУСКА",
  "Публикация [09-2005], репост 03.08.2015: КОНДЕНСАТОРНЫЙ ЗАПУСК ФР"]
}
PTR = 'expandedScenario(id = "phase-splitter-no-start")'
WARNING = {"default":"HIDDEN","extendedEnabled":True,"warningReadToEnd":True,
           "warningAcknowledged":True,"warningGrantsActionAuthority":False}
POLICY = {"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],
          "unknownMustStop":True,"operationsAllowed":[],"unknownProfile":"BLOCKED"}

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def graph(nodes, start, sources):
    by_id = {n["id"]:n for n in nodes}
    need(len(by_id) == len(nodes) and start in by_id, "graph IDs")
    seen, pending = {start}, [start]
    while pending:
        node = by_id[pending.pop()]
        need(node["recordedOnly"] is True and node["operationRequested"] is False
             and node["causeConfirmed"] is False and
             set(node["sourceRefs"]) <= sources and node["sourceRefs"], "unsafe node")
        if node["type"] == "QUESTION":
            edges = node["responses"]
            need(set(edges) == {"YES","NO","UNKNOWN"} and edges["YES"] != edges["NO"]
                 and all(t in by_id for t in edges.values()) and
                 by_id[edges["UNKNOWN"]]["type"] == "STOP", "tri-state fail-closed")
            for target in edges.values():
                if target not in seen:
                    seen.add(target)
                    pending.append(target)
        else:
            need(node["type"] in {"STOP","OBSERVATION_REPORT"} and not node["responses"], "terminal")
    need(seen == set(by_id), "unreachable node")
    # Check every node, including an unreachable node, for safety.
    for node in nodes:
        need(node["recordedOnly"] is True and node["operationRequested"] is False and
             node["causeConfirmed"] is False, "unsafe unreachable node")

def validate(doc, migration, inventory):
    need(set(doc) == {"ledger","candidates"} and len(doc["candidates"]) == 1, "envelope")
    ledger, d = doc["ledger"], doc["candidates"][0]
    orig = next((x for x in migration["scenarios"] if x["id"] == ID), None)
    row = next((x for x in inventory["rows"] if x["scenarioId"] == SID), None)
    need(orig is not None and row is not None and
         ledger["stage"] == "8/51" and ledger["donorPinnedSha"] == DONOR and
         ledger["addedScenarioIds"] == [SID] and
         ledger["stage8OverallStatus"] == "IN_PROGRESS_NOT_CLOSED" and
         ledger["publicationStatus"] == "CANDIDATE" and
         ledger["runtimeImport"] is False and ledger["actionAuthorityGranted"] is False and
         ledger["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "ledger")
    need(d["schemaVersion"] == "diagnostic-stage8-phase-splitter-no-start-source-first/1"
         and d["stage"] == "8/51" and d["scenarioId"] == SID and d["originalId"] == ID
         and d["title"] == orig["title"] and d["summary"] == orig["summary"]
         and d["category"] == orig["category"] and orig["originLayer"] == "DiagnosticExpansion.kt"
         and d["donorPinnedSha"] == DONOR and d["donorOriginalBlobSha"] == BLOB
         and d["donorOriginLayer"] == "DiagnosticExpansion.kt" and d["donorGraphNodeCount"] == 3
         and d["donorOriginalQuestions"] == ["Есть попытка вращения?",
           "Фазорасщепитель разгоняется, но затем отключается?",
           "Одновременно отказали все трёхфазные вспомогательные машины?"]
         and d["donorQuestionProvenance"] == "PINNED_EXPANSION_THREE_QUESTIONS_REWRITTEN_AS_RECORDED_ONLY"
         and row["graph"]["nodeCount"] == 3 and row["variantIds"] == ["vl80s-general"]
         and all(row[k] == "NOT_AUTHORED" for k in ("shortVersion","detailedVersion",
                  "shortExtendedBranch","detailedExtendedBranch")), "pinned origin mismatch")
    need(d["canonicalGroup"] == "PHASE_SPLITTER_START_AND_STABILITY_VS_GROUP_OR_SINGLE_AUX_LOSS"
         and set(d["mustRemainDistinctFrom"]) == {
          "vl80s.diag.aux-machines","vl80s.diag.aux-common-loss",
          "vl80s.diag.motor-fan-failure","vl80s.diag.compressor-no-start",
          "vl80s.diag.aux-contactor-chatter"}, "symptom separation")
    need(d["authoringProfileId"] == "vl80s-general" and
         d["publicationStatus"] == "CANDIDATE" and
         d["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA" and
         all(d[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted",
              "sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"))
         and d["warningGate"] == WARNING and d["safePolicy"] == POLICY, "publication/safety")
    sources = d["sourceRecords"]
    need(set(sources) == {"donor","manual1990","article2005"}, "source list")
    donor = sources["donor"]
    need(donor["kind"] == "PINNED_DONOR_OFFLINE_CATALOG" and donor["commit"] == DONOR
         and donor["blobSha"] == BLOB and donor["repository"] == "DomEnota-hub/Test-"
         and donor["path"] == "patch/app/src/main/java/ru/railbrake/calculator/core/DiagnosticExpansion.kt"
         and donor["sourcePointer"] == PTR and donor["originalId"] == ID
         and donor["excerpt"] == {k:orig[k] for k in ("category","title","summary")}
         and donor["proceduresImported"] is False and
         donor["currentOperatingAuthority"] is False, "donor source")
    manual, article = sources["manual1990"], sources["article2005"]
    need(manual["kind"] == "HISTORICAL_FACTORY_MANUAL" and manual["year"] == 1990
         and manual["isbn"] == "5-277-01048-3"
         and manual["url"] == "https://djvu.online/file/wXVHhRmTUUuqq"
         and article["kind"] == "HISTORICAL_TRAINING_TECHNICAL_ARTICLE_REPOST"
         and article["sourceIssue"] == "09-2005 (указано в перепечатке)"
         and article["repostDate"] == "2015-08-03"
         and article["originalPrintIndependentlyVerified"] is False
         and article["url"] == "https://scbist.com/xx2/44052-09-2005-cepi-puska-fazorasschepitelei-na-elektrovozah-vl80s.html"
         and all(s["verifiedLocators"] == LOC[key] and s["sourceTextLocated"] is True
              and s["containsHistoricalUnsafeProcedures"] is True
              and all(s[k] is False for k in ("modernRevisionVerified","exactInstalledEquipmentVerified",
                                             "currentOperatingAuthority","proceduresImported"))
              for key,s in (("manual1990",manual),("article2005",article))), "historical authority")
    claims = d["historicalEvidenceClaims"]
    need(len(claims) == 4 and {(x["sourceId"],x["locator"]) for x in claims} ==
         {(source,loc) for source,locs in LOC.items() for loc in locs}
         and all(x["confidence"].startswith("HISTORICAL_") and
                 all(x[k] is False for k in ("provesCurrentEquipment","provesFaultCause","authorizesAction"))
                 for x in claims), "claim authority")
    need(set(d["versions"]) == {"SHORT","DETAILED"}, "version presence")
    approaches, focuses = set(), set()
    for name,count,expected in (("SHORT",6,2),("DETAILED",12,3)):
        v = d["versions"][name]
        need(v["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and
             v["independentTechnicalReview"] == "REQUIRED" and
             v["operatingInstructionsIncluded"] is False and
             len(v["nodes"]) == count and len(v["extendedRoutes"]) == expected, "version")
        graph(v["nodes"],v["startNodeId"],set(sources))
        for ext in v["extendedRoutes"]:
            need(ext["approachId"] not in approaches and ext["approachFocus"] not in focuses,
                 "duplicate approach")
            approaches.add(ext["approachId"])
            focuses.add(ext["approachFocus"])
            need(ext["version"] == name and ext["sourceId"] in sources and
                 ext["sourceLocator"] in (LOC.get(ext["sourceId"],[PTR])) and
                 ext["questionType"] == "ALREADY_RECORDED_FACT_ONLY" and
                 ext["publicationStatus"] == "CANDIDATE" and
                 ext["actionDisposition"] == "INFORMATION_ONLY" and
                 ext["technicalClaimReview"] == "REQUIRES_EXPERT" and
                 ext["operationalSteps"] == [] and ext["executable"] is False and
                 ext["actionAuthorityGranted"] is False and
                 ext["applicability"] == {"profileId":"vl80s-general",
                   "exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False}
                 and ext["visibility"] == WARNING, "extension authority")
            graph(ext["nodes"],ext["startNodeId"],set(sources))
    need(len(approaches) == len(focuses) == 5 and
         [x["sourceId"] for x in d["versions"]["SHORT"]["extendedRoutes"]] ==
         ["donor","manual1990"] and
         [x["sourceId"] for x in d["versions"]["DETAILED"]["extendedRoutes"]] ==
         ["donor","manual1990","article2005"], "extension sources")
    return True

class NegativeQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.mig = json.loads(MIG.read_text(encoding="utf-8"))["sourceObject"]
        cls.inv = json.loads(INV.read_text(encoding="utf-8"))
    def reject(self, mutator):
        doc = copy.deepcopy(self.doc)
        mutator(doc["candidates"][0])
        with self.assertRaises(ValueError):
            validate(doc,self.mig,self.inv)
    def test_baseline(self):
        self.assertTrue(validate(self.doc,self.mig,self.inv))
    def test_pinned_blob(self):
        self.reject(lambda d: d.update(donorOriginalBlobSha="wrong"))
    def test_donor_pointer(self):
        self.reject(lambda d: d["sourceRecords"]["donor"].update(sourcePointer="invented"))
    def test_variant_promotion(self):
        self.reject(lambda d: d.update(exactInstalledVariantConfirmed=True))
    def test_runtime_promotion(self):
        self.reject(lambda d: d.update(runtimeImport=True))
    def test_action_promotion(self):
        self.reject(lambda d: d.update(actionAuthorityGranted=True))
    def test_warning_bypass(self):
        self.reject(lambda d: d["warningGate"].update(warningReadToEnd=False))
    def test_warning_action(self):
        self.reject(lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["visibility"].update(warningGrantsActionAuthority=True))
    def test_unknown_to_report(self):
        self.reject(lambda d: d["versions"]["SHORT"]["nodes"][1]["responses"].update(UNKNOWN="report-recorded"))
    def test_unreachable(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["nodes"][0]["responses"].update(NO="stop-unknown"))
    def test_new_operation(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["nodes"][0].update(operationRequested=True))
    def test_unrecorded_probe(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["nodes"][0].update(recordedOnly=False))
    def test_extension_operation(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["extendedRoutes"][2].update(operationalSteps=["switch"]))
    def test_historical_promotion(self):
        self.reject(lambda d: d["sourceRecords"]["article2005"].update(currentOperatingAuthority=True))
    def test_unverified_print_promotion(self):
        self.reject(lambda d: d["sourceRecords"]["article2005"].update(originalPrintIndependentlyVerified=True))
    def test_source_locator(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["extendedRoutes"][2].update(sourceLocator="invented"))
    def test_claim_promotion(self):
        self.reject(lambda d: d["historicalEvidenceClaims"][3].update(authorizesAction=True))
    def test_conflate_aux(self):
        self.reject(lambda d: d.update(canonicalGroup="GROUP_LOSS"))
    def test_device_pass(self):
        self.reject(lambda d: d.update(deviceQA="PASS"))
    def test_unknown_profile(self):
        self.reject(lambda d: d["safePolicy"].update(unknownProfile="ALLOW"))
    def test_unsafe_variant(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["extendedRoutes"][2]["applicability"].update(exactEquipmentProfileConfirmed=True))

if __name__ == "__main__":
    unittest.main()
