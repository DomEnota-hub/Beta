#!/usr/bin/env python3
"""Stage 8 batch: pinned donor parity, provenance, graph, authority, negative mutations."""
import copy
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MIG = json.loads((ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))["sourceObject"]
INV = json.loads((ROOT / "docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
EXPECTED = json.loads("{\"aux-relay-113-trip\":{\"title\":\"ГВ отключился со срабатыванием реле 113\",\"summary\":\"Отключился главный выключатель и указатель реле 113 сообщает токовую защиту цепи вспомогательных машин.\",\"category\":\"Вспомогательные машины\",\"questions\":[\"Срабатывание реле 113 подтверждено его указателем, а не только лампой ГВ?\",\"Событие совпало с видимым отрывом токоприёмника, дугой, воздушной стрелкой или кратковременным исчезновением напряжения?\",\"После разрешённого восстановления реле 113 срабатывает при включении одной и той же вспомогательной машины?\"],\"locators\":[\"XI «Защита вспомогательных цепей», печ. стр. 209: реле 113 действует на ГВ, индивидуальные тепловые реле действуют на контакторы\",\"Раздел Б, табл. 14, печ. стр. 278–279: отключение ГВ при срабатывании 113 и историческая таблица поиска\",\"Сведения о реле 113, назначение, указатель и удерживающая цепь ГВ; любительский справочник без даты\"],\"canonicalGroup\":\"AUXILIARY_SUPPLY_OVERLOAD_RELAY_113_NOT_ANY_GV_TRIP\",\"distinct\":[\"gv-no-open\",\"aux-common-loss\",\"aux-machine-single-trip\",\"traction-overload-relay-trip\"],\"sourceKinds\":[\"donor\",\"manual1990\",\"practicalUndated\"]},\"ventilation-duct-damage\":{\"title\":\"Повреждён воздуховод или не действует заслонка охлаждения\",\"summary\":\"Вентилятор работает, но поток распределяется неправильно, слышен подсос/хлопок либо видимо повреждён тракт охлаждения.\",\"category\":\"Вспомогательные машины\",\"questions\":[\"Работа вентилятора и направление потока подтверждены?\",\"Поток потерян только у одной группы оборудования?\",\"Есть нагрев, запах или действие защиты охлаждаемой группы?\"],\"locators\":[\"Раздел А, §10 «Система вентиляции», печ. стр. 187–188, рис. 239: воздуховоды, заслонки и охлаждаемые группы\",\"Раздел А, §10, печ. стр. 189: маршруты охлаждения ТЭД, ВУ, трансформатора и реакторов\",\"Раздел А, §10, печ. стр. 189: сезонные фильтры и распределение воздуха в режимах тяги и торможения\"],\"canonicalGroup\":\"COOLING_DUCT_OR_DAMPER_NOT_MOTOR_FAN_FAILURE\",\"distinct\":[\"fan-low-airflow\",\"fan-vibration\",\"motor-fan-failure\",\"rectifier-overheat\"],\"sourceKinds\":[\"donor\",\"manual1990\"]},\"oil-pump-failure\":{\"title\":\"Отказ масляного насоса трансформатора\",\"summary\":\"Маслонасос трансформатора не запускается, отключается после пуска либо работа системы циркуляции масла не подтверждается.\",\"category\":\"Вспомогательные машины\",\"questions\":[\"Маслонасос совсем не запускается при штатной команде?\",\"После запуска насос отключается, гудит, вибрирует или работает с необычным шумом?\",\"Есть отсутствие подтверждённой циркуляции масла, рост температуры, запах, дым или действие защиты трансформатора?\"],\"locators\":[\"Раздел А, печ. стр. 205: маслонасос МН как потребитель трёхфазных вспомогательных цепей охлаждения трансформатора\",\"Раздел А, печ. стр. 223, рис. 255: историческая связь контактора 133 с МВ3/МВ4 и цепью маслонасоса\",\"Раздел Б, табл. 14, печ. стр. 281–282: сигнал МН, тепловая защита и исторические методы восстановления, не переносимые в сценарий\"],\"canonicalGroup\":\"TRANSFORMER_OIL_CIRCULATION_NOT_AUX_COMMON_LOSS\",\"distinct\":[\"aux-common-loss\",\"aux-machine-single-trip\",\"motor-fan-failure\",\"transformer-oil-signs\"],\"sourceKinds\":[\"donor\",\"manual1990\"]}}")
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "0d94801dcbe1d96e1a551a9dac8fef2a808b9029"
WARN = {"default":"HIDDEN","extendedEnabled":True,"warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
POLICY = {"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"operationsAllowed":[],"unknownProfile":"BLOCKED"}
FORBIDDEN = re.compile(r"(?i)\\b(?:включите|перемкните|замкните|вскройте|измерьте|запустите|сбросьте|повторите\\s+пуск|установите\\s+перемычку)\\b")
def need(ok, msg):
    if not ok: raise ValueError(msg)
def graph(nodes, start, sources, count):
    by = {n["id"]: n for n in nodes}
    need(len(by) == len(nodes) == count and start in by, "graph IDs/count")
    seen, todo = set(), [start]
    while todo:
        key = todo.pop()
        need(key in by, "missing graph target")
        if key in seen: continue
        seen.add(key)
        n = by[key]
        need(n["type"] in ("QUESTION", "STOP", "OBSERVATION_REPORT"), "node type")
        need(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False, "node safety")
        need(n["sourceRefs"] and set(n["sourceRefs"]) <= sources, "node provenance")
        need(not FORBIDDEN.search(n["text"]), "unsafe imperative")
        if n["type"] == "QUESTION":
            need(set(n["responses"]) == {"YES","NO","UNKNOWN"}, "tri-state")
            need(by.get(n["responses"]["UNKNOWN"], {}).get("type") == "STOP", "UNKNOWN must STOP")
            todo.extend(n["responses"].values())
        else:
            need(n["responses"] == {}, "terminal edges")
    need(seen == set(by), "unreachable graph node")
def validate(doc, ident):
    exp = EXPECTED[ident]
    need(set(doc) == {"ledger","candidates"} and len(doc["candidates"]) == 1, "envelope")
    l, d = doc["ledger"], doc["candidates"][0]
    sid = "vl80s.diag." + ident
    donor = next((x for x in MIG["scenarios"] if x["id"] == ident), None)
    inv = next((x for x in INV["rows"] if x["scenarioId"] == sid), None)
    need(donor is not None and inv is not None, "missing donor mapping")
    need(l["stage"] == "8/51" and l["baseHead"] == "8c4d4918bcf09298a81dfe10222aa73cb0028568" and l["addedScenarioIds"] == [sid] and l["donorPinnedSha"] == DONOR and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False and l["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "ledger")
    need(d["scenarioId"] == sid and d["originalId"] == ident and d["title"] == exp["title"] == donor["title"] and d["summary"] == exp["summary"] == donor["summary"] and d["category"] == exp["category"] == donor["category"] == "Вспомогательные машины", "donor identity")
    need(d["donorOriginLayer"] == donor["originLayer"] == "DiagnosticCompletionCatalog.kt" and donor["runtimeStatus"] == "VISIBLE_CURRENT_DIAGNOSTIC_REPOSITORY" and d["donorOriginalBlobSha"] == BLOB and d["donorPinnedSha"] == DONOR and d["donorGraphNodeCount"] == inv["graph"]["nodeCount"] == 3 and d["donorOriginalQuestions"] == exp["questions"] and inv["variantIds"] == ["vl80s-general"], "donor source parity")
    need(all(inv[k] == "NOT_AUTHORED" for k in ("shortVersion","detailedVersion","shortExtendedBranch","detailedExtendedBranch")), "no donor authoring")
    need(d["canonicalGroup"] == exp["canonicalGroup"] and set(d["mustRemainDistinctFrom"]) == {"vl80s.diag."+x for x in exp["distinct"]}, "symptom separation")
    need(d["authoringProfileId"] == "vl80s-general" and d["publicationStatus"] == "CANDIDATE" and d["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "profile")
    need(all(d[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed")), "authority gates")
    need(d["warningGate"] == WARN and d["safePolicy"] == POLICY, "warning and fail closed")
    sources = d["sourceRecords"]
    need(set(sources) == set(exp["sourceKinds"]), "source set")
    origin = sources["donor"]
    need(origin["repository"] == "DomEnota-hub/Test-" and origin["commit"] == DONOR and origin["blobSha"] == BLOB and origin["originalId"] == ident and origin["originalQuestions"] == exp["questions"] and origin["sourcePointer"] == 'id = "'+ident+'"', "origin provenance")
    need(origin["currentOperatingAuthority"] is False and origin["proceduresImported"] is False, "donor authority")
    manual = sources["manual1990"]
    need(manual["kind"] == "HISTORICAL_FACTORY_MANUAL" and manual["year"] == 1990 and manual["isbn"] == "5-277-01048-3" and manual["verifiedLocators"] == [x for x in exp["locators"] if not x.startswith("Сведения о реле")], "manual provenance")
    for src in sources.values():
        need(src["currentOperatingAuthority"] is False and src["proceduresImported"] is False, "source authority")
    if "practicalUndated" in sources:
        need(sources["practicalUndated"]["dateVerified"] is False and sources["practicalUndated"]["verifiedLocators"] == [exp["locators"][2]], "practical status")
    claims = d["historicalEvidenceClaims"]
    need(len(claims) >= 3 and all(c["sourceId"] in sources and c["locator"] in sources[c["sourceId"]]["verifiedLocators"] and c["provesCurrentEquipment"] is False and c["provesFaultCause"] is False and c["authorizesAction"] is False for c in claims), "claims and source locators")
    approaches, focuses = set(), set()
    need(set(d["versions"]) == {"SHORT","DETAILED"}, "versions")
    for name, count, exts in (("SHORT",6,2),("DETAILED",12,3)):
        v = d["versions"][name]
        need(v["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and v["independentTechnicalReview"] == "REQUIRED" and v["operatingInstructionsIncluded"] is False and len(v["extendedRoutes"]) == exts, "version safety")
        graph(v["nodes"], v["startNodeId"], set(sources), count)
        for e in v["extendedRoutes"]:
            need(e["approachId"] not in approaches and e["approachFocus"] not in focuses, "duplicate extension")
            approaches.add(e["approachId"]); focuses.add(e["approachFocus"])
            need(e["version"] == name and e["sourceId"] in sources and e["sourceLocator"] in ([origin["sourcePointer"]] if e["sourceId"] == "donor" else sources[e["sourceId"]]["verifiedLocators"]), "extension provenance")
            need(e["questionType"] == "ALREADY_RECORDED_FACT_ONLY" and e["publicationStatus"] == "CANDIDATE" and e["actionDisposition"] == "INFORMATION_ONLY" and e["technicalClaimReview"] == "REQUIRES_EXPERT" and e["operationalSteps"] == [] and e["executable"] is False and e["actionAuthorityGranted"] is False, "extension safety")
            need(e["visibility"] == WARN and e["applicability"] == {"profileId":"vl80s-general","exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False}, "extension gate")
            graph(e["nodes"], e["startNodeId"], {e["sourceId"]}, 4)
    need(len(approaches) == len(focuses) == 5, "extension count")
class BatchQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {ident:json.loads((ROOT / ("docs/diagnostics/STAGE8_"+ident.upper().replace("-","_")+"_2026-11-05.json")).read_text(encoding="utf-8")) for ident in EXPECTED}
    def test_baseline(self):
        for ident, doc in self.docs.items():
            with self.subTest(ident=ident): validate(doc, ident)
    def test_negative_mutations(self):
        mutations = [
            ("donor-id", lambda d: d.update(originalId="fake")),
            ("donor-questions", lambda d: d["donorOriginalQuestions"].append("fake")),
            ("donor-blob", lambda d: d.update(donorOriginalBlobSha="fake")),
            ("donor-title", lambda d: d.update(title="fake")),
            ("donor-source", lambda d: d["sourceRecords"]["donor"].update(commit="fake")),
            ("manual-year", lambda d: d["sourceRecords"]["manual1990"].update(year=2026)),
            ("manual-locator", lambda d: d["sourceRecords"]["manual1990"].update(verifiedLocators=[])),
            ("claim-authority", lambda d: d["historicalEvidenceClaims"][0].update(authorizesAction=True)),
            ("claim-cause", lambda d: d["historicalEvidenceClaims"][0].update(provesFaultCause=True)),
            ("profile", lambda d: d.update(exactInstalledVariantConfirmed=True)),
            ("source-gate", lambda d: d.update(sourceAuthorityVerified=True)),
            ("runtime", lambda d: d.update(runtimeImport=True)),
            ("execute", lambda d: d.update(executable=True)),
            ("action", lambda d: d.update(actionAuthorityGranted=True)),
            ("safety", lambda d: d.update(substantiveSafetyReviewed=True)),
            ("warning-scroll", lambda d: d["warningGate"].update(warningReadToEnd=False)),
            ("warning-action", lambda d: d["warningGate"].update(warningGrantsActionAuthority=True)),
            ("unknown-profile", lambda d: d["safePolicy"].update(unknownProfile="ALLOW")),
            ("operations", lambda d: d["safePolicy"].update(operationsAllowed=["switch"])),
            ("node-operation", lambda d: d["versions"]["SHORT"]["nodes"][0].update(operationRequested=True)),
            ("node-recorded", lambda d: d["versions"]["DETAILED"]["nodes"][0].update(recordedOnly=False)),
            ("unsafe-imperative", lambda d: d["versions"]["SHORT"]["nodes"][1].update(text="Включите контактор")),
            ("unknown-bypass", lambda d: d["versions"]["SHORT"]["nodes"][1]["responses"].update(UNKNOWN="report-primary")),
            ("missing-edge", lambda d: d["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="missing")),
            ("unreachable", lambda d: d["versions"]["SHORT"]["nodes"][0]["responses"].update(NO="stop-unknown")),
            ("extension-duplicate", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][0].update(approachId=d["versions"]["SHORT"]["extendedRoutes"][0]["approachId"])),
            ("extension-operation", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][0].update(operationalSteps=["switch"])),
            ("extension-profile", lambda d: d["versions"]["DETAILED"]["extendedRoutes"][0]["applicability"].update(modernSchemeConfirmed=True)),
            ("extension-unknown", lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["nodes"][0]["responses"].update(UNKNOWN="report-yes")),
            ("extension-warning", lambda d: d["versions"]["SHORT"]["extendedRoutes"][0]["visibility"].update(warningAcknowledged=False)),
            ("device-pass", lambda d: d.update(deviceQA="PASS")),
            ("category", lambda d: d.update(category="Тяга")),
        ]
        for ident, doc in self.docs.items():
            for label, mutation in mutations:
                with self.subTest(ident=ident,mutation=label):
                    altered = copy.deepcopy(doc)
                    mutation(altered["candidates"][0])
                    with self.assertRaises(ValueError):
                        validate(altered, ident)
if __name__ == "__main__":
    unittest.main()
