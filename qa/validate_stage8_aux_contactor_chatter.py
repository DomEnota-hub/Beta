#!/usr/bin/env python3
"""Stage8 first source-scoped auxiliary symptom: non-runtime research QA."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "docs/diagnostics/STAGE8_AUX_CONTACTOR_CHATTER_2026-11-04.json"
INV = ROOT / "docs/data-migration/diagnostic-corpus-analysis.json"
MIG = ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "090d448d0e9de20d002edf07361764e524298bf8"
LOC = [
    "XI §5, печ. стр. 222–223, рис. 255: цепи катушек контакторов 124, 127–130, 133",
    "XI §5, печ. стр. 223: самоподхват контакторов 127–130 и отключение через реле 259/260",
    "XI §5, печ. стр. 223: тепловые реле 141–148 и запрет автоматического повторного включения"
]
VISIBILITY = {"default":"HIDDEN","extendedEnabled":True,"warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
POLICY = {"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"operationsAllowed":[],"unknownProfile":"BLOCKED"}

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def graph(nodes, start, sources):
    by_id = {n["id"]: n for n in nodes}
    need(len(by_id) == len(nodes) and start in by_id, "graph identity")
    for n in nodes:
        need(n["sourceRefs"] and set(n["sourceRefs"]).issubset(sources) and
             n["recordedOnly"] is True and n["operationRequested"] is False and
             n["causeConfirmed"] is False, "unsafe node or source")
        if n["type"] == "QUESTION":
            e = n["responses"]
            need(set(e) == {"YES", "NO", "UNKNOWN"} and
                 e["YES"] != e["NO"] and all(x in by_id for x in e.values()) and
                 by_id[e["UNKNOWN"]]["type"] == "STOP", "tri-state fail-closed")
        else:
            need(n["type"] in {"STOP", "OBSERVATION_REPORT"} and n["responses"] == {},
                 "terminal action")
    seen, pending = {start}, [start]
    while pending:
        for target in by_id[pending.pop()]["responses"].values():
            if target not in seen:
                seen.add(target)
                pending.append(target)
    need(seen == set(by_id), "unreachable node")

def validate(d, inventory, migration):
    orig = next((s for s in migration["scenarios"] if s["id"] == "aux-contactor-chatter"), None)
    row = next((s for s in inventory["rows"] if s["scenarioId"] == "vl80s.diag.aux-contactor-chatter"), None)
    need(orig is not None and row is not None and
         d["schemaVersion"] == "diagnostic-stage8-aux-contactor-chatter-source-first/1" and
         d["stage"] == "8/51" and d["scenarioId"] == "vl80s.diag.aux-contactor-chatter" and
         d["originalId"] == "aux-contactor-chatter" and
         d["donorPinnedSha"] == DONOR and d["donorOriginalBlobSha"] == BLOB and
         d["donorOriginLayer"] == "DiagnosticExtendedCatalog.kt" and
         d["donorGraphNodeCount"] == 3 and d["donorOriginalQuestions"] == [] and
         d["donorQuestionProvenance"] == "SEED_HAS_NO_EXPLICIT_QUESTIONS" and
         d["title"] == orig["title"] and d["summary"] == orig["summary"] and
         d["category"] == orig["category"] and orig["originLayer"] == "DiagnosticExtendedCatalog.kt" and
         row["graph"]["nodeCount"] == 3 and row["variantIds"] == ["vl80s-general"] and
         all(row[k] == "NOT_AUTHORED" for k in
             ("shortVersion", "detailedVersion", "shortExtendedBranch", "detailedExtendedBranch")),
         "pinned donor or inventory mismatch")
    need(d["authoringProfileId"] == "vl80s-general" and
         set(d["mustRemainDistinctFrom"]) == set(["vl80s.diag.aux-common-loss","vl80s.diag.motor-fan-failure","vl80s.diag.phase-splitter-no-start","vl80s.diag.aux-machine-single-trip"]) and
         d["canonicalGroup"] == "REPEATED_SINGLE_AUX_CONTACTOR_STATE_VS_GROUP_LOSS_OR_UNVERIFIED_SOUND",
         "profile or symptom boundary")
    need(d["publicationStatus"] == "CANDIDATE" and d["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA" and
         all(d[k] is False for k in ("runtimeImport", "executable", "actionAuthorityGranted",
                                    "sourceAuthorityVerified", "exactInstalledVariantConfirmed",
                                    "substantiveSafetyReviewed")) and
         d["warningGate"] == VISIBILITY and d["safePolicy"] == POLICY,
         "publication or safety bypass")
    sources = d["sourceRecords"]
    need(set(sources) == {"donor", "manual1990"}, "source identity")
    src = sources["donor"]
    need(src["kind"] == "PINNED_DONOR_OFFLINE_CATALOG" and src["commit"] == DONOR and
         src["repository"] == "DomEnota-hub/Test-" and src["blobSha"] == BLOB and
         src["sourcePointer"] == 'Seed("aux-contactor-chatter")' and
         src["excerpt"] == {k: orig[k] for k in ("category", "title", "summary")} and
         src["currentOperatingAuthority"] is False and src["proceduresImported"] is False,
         "donor provenance")
    manual = sources["manual1990"]
    need(manual["kind"] == "HISTORICAL_FACTORY_MANUAL" and manual["year"] == 1990 and
         manual["isbn"] == "5-277-01048-3" and
         manual["url"] == "https://djvu.online/file/wXVHhRmTUUuqq" and
         manual["verifiedLocators"] == LOC and manual["sameDocumentAcrossApproaches"] is True and
         manual["containsHistoricalUnsafeProcedures"] is True and
         manual["sourceTextLocated"] is True and
         all(manual[k] is False for k in ("modernRevisionVerified", "exactInstalledEquipmentVerified",
                                         "currentOperatingAuthority", "proceduresImported")),
         "historical source promoted")
    claims = d["historicalEvidenceClaims"]
    need(len(claims) == 3 and {c["locator"] for c in claims} == set(LOC) and
         all(c["sourceId"] == "manual1990" and c["confidence"].startswith("HISTORICAL_") and
             all(c[k] is False for k in ("provesCurrentEquipment", "provesFaultCause",
                                         "authorizesAction")) for c in claims),
         "historical claim as current authority")
    need(set(d["versions"]) == {"SHORT", "DETAILED"}, "missing route version")
    ids, focuses = set(), set()
    for version, count, extensions in (("SHORT", 6, 2), ("DETAILED", 12, 3)):
        v = d["versions"][version]
        need(v["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and
             v["independentTechnicalReview"] == "REQUIRED" and
             v["operatingInstructionsIncluded"] is False and
             len(v["nodes"]) == count and len(v["extendedRoutes"]) == extensions,
             "version size or review status")
        graph(v["nodes"], v["startNodeId"], sources)
        for r in v["extendedRoutes"]:
            need(r["approachId"] not in ids and r["approachFocus"] not in focuses,
                 "duplicate approach")
            ids.add(r["approachId"])
            focuses.add(r["approachFocus"])
            need(r["version"] == version and r["sourceId"] in sources and
                 r["sourceLocator"] in (LOC if r["sourceId"] == "manual1990" else
                                        ['Seed("aux-contactor-chatter")']) and
                 r["questionType"] == "ALREADY_RECORDED_FACT_ONLY" and
                 r["publicationStatus"] == "CANDIDATE" and
                 r["actionDisposition"] == "INFORMATION_ONLY" and
                 r["technicalClaimReview"] == "REQUIRES_EXPERT" and
                 r["operationalSteps"] == [] and r["executable"] is False and
                 r["actionAuthorityGranted"] is False and
                 r["applicability"] == {"profileId": "vl80s-general",
                                         "exactEquipmentProfileConfirmed": False,
                                         "modernSchemeConfirmed": False} and
                 r["visibility"] == VISIBILITY, "extension authority or provenance")
            graph(r["nodes"], r["startNodeId"], sources)
    need(len(ids) == 5 and len(focuses) == 5 and
         [r["sourceId"] for r in d["versions"]["SHORT"]["extendedRoutes"]] == ["donor", "manual1990"] and
         [r["sourceId"] for r in d["versions"]["DETAILED"]["extendedRoutes"]] ==
             ["donor", "manual1990", "manual1990"] and
         d["versions"]["SHORT"]["nodes"] != d["versions"]["DETAILED"]["nodes"],
         "version approach separation")
    return True

class NegativeQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(FILE.read_text(encoding="utf-8"))["candidates"][0]
        cls.inventory = json.loads(INV.read_text(encoding="utf-8"))
        cls.migration = json.loads(MIG.read_text(encoding="utf-8"))["sourceObject"]

    def reject(self, mutation):
        d = copy.deepcopy(self.d)
        mutation(d)
        with self.assertRaises(ValueError):
            validate(d, self.inventory, self.migration)

    def test_baseline(self):
        self.assertTrue(validate(self.d, self.inventory, self.migration))
    def test_pinned_blob(self):
        self.reject(lambda d: d.update(donorOriginalBlobSha="wrong"))
    def test_source_pointer(self):
        self.reject(lambda d: d["sourceRecords"]["donor"].update(sourcePointer="Seed(OTHER)"))
    def test_runtime_promotion(self):
        self.reject(lambda d: d.update(runtimeImport=True))
    def test_action_promotion(self):
        self.reject(lambda d: d.update(actionAuthorityGranted=True))
    def test_variant_promotion(self):
        self.reject(lambda d: d.update(exactInstalledVariantConfirmed=True))
    def test_warning_skip(self):
        self.reject(lambda d: d["warningGate"].update(warningReadToEnd=False))
    def test_warning_action(self):
        self.reject(lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["visibility"].update(warningGrantsActionAuthority=True))
    def test_unknown_to_report(self):
        self.reject(lambda d: d["versions"]["SHORT"]["nodes"][1]["responses"].update(UNKNOWN="report-recorded"))
    def test_unreachable_node(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["nodes"][0]["responses"].update(NO="stop-unknown"))
    def test_unsafe_node(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["nodes"][0].update(operationRequested=True))
    def test_unrecorded_probe(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["nodes"][0].update(recordedOnly=False))
    def test_extended_operation(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["extendedRoutes"][1].update(operationalSteps=["switch"]))
    def test_source_authority(self):
        self.reject(lambda d: d["sourceRecords"]["manual1990"].update(currentOperatingAuthority=True))
    def test_source_locator(self):
        self.reject(lambda d: d["versions"]["SHORT"]["extendedRoutes"][1].update(sourceLocator="invented page"))
    def test_claim_promotion(self):
        self.reject(lambda d: d["historicalEvidenceClaims"][0].update(provesFaultCause=True))
    def test_fake_device_pass(self):
        self.reject(lambda d: d.update(deviceQA="PASS"))
    def test_duplicate_approach(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["extendedRoutes"][0].update(approachFocus="DONOR_SINGLE_CONTACTOR_SYMPTOM"))
    def test_profile_bypass(self):
        self.reject(lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["applicability"].update(modernSchemeConfirmed=True))
    def test_graph_node_missing(self):
        self.reject(lambda d: d["versions"]["SHORT"]["nodes"].pop())
    def test_false_chatter_diagnosis(self):
        self.reject(lambda d: d["historicalEvidenceClaims"][1].update(provesFaultCause=True))
    def test_warning_not_runtime(self):
        self.reject(lambda d: d["versions"]["DETAILED"]["extendedRoutes"][0].update(executable=True))
    def test_invented_manual_equivalence(self):
        self.reject(lambda d: d["sourceRecords"]["manual1990"].update(sameDocumentAcrossApproaches=False))

if __name__ == "__main__":
    bundle = json.loads(FILE.read_text(encoding="utf-8"))
    inventory = json.loads(INV.read_text(encoding="utf-8"))
    migration = json.loads(MIG.read_text(encoding="utf-8"))["sourceObject"]
    ledger = bundle["ledger"]
    need(ledger["stage"] == "8/51" and ledger["stage8OverallStatus"] == "IN_PROGRESS_NOT_CLOSED" and
         ledger["addedScenarioIds"] == ["vl80s.diag.aux-contactor-chatter"] and
         ledger["publicationStatus"] == "CANDIDATE" and ledger["runtimeImport"] is False and
         ledger["actionAuthorityGranted"] is False and
         ledger["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA" and
         len(bundle["candidates"]) == 1 and ledger["baseHead"] == "ec3e2366f6b64f6124e1fea312559e9e050af7cd", "stage8 ledger")
    if "--negative" in sys.argv:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        print("PASS Stage8 auxiliary contactor chatter source-first", validate(bundle["candidates"][0], inventory, migration))
