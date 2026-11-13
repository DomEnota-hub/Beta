#!/usr/bin/env python3
"""Stage 9 HV/pantograph research batch 2: pinned donor parity, graph, source, safety and negative QA."""
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/diagnostics/STAGE9_PANTOGRAPH_HV_BATCH2_2026-11-05.json"
MIGRATION = ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
INVENTORY = ROOT / "docs/data-migration/diagnostic-corpus-analysis.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
DONOR_BLOB = "090d448d0e9de20d002edf07361764e524298bf8"
IDS = json.loads(r'''["gv-air-loss","pantograph-contact-arcing","pantograph-slow-rise","pantograph-wrong-selection","roof-insulation-signs"]''')
EXPECTED = json.loads(r'''{"gv-air-loss":{"category":"Высоковольтные цепи","title":"Падает давление в резервуаре ГВ","summary":"Запас воздуха привода ГВ не сохраняется или восстанавливается слишком медленно.","equipment":"ГВ, резервуар, пневмопривод","signs":"шипение, падение давления","danger":"неуправляемое состояние ГВ"},"pantograph-contact-arcing":{"category":"Высоковольтные цепи","title":"Повышенное искрение токоприёмника","summary":"На полозе наблюдается устойчивое или необычно сильное искрение.","equipment":"токоприёмник, полоз, контактная сеть","signs":"искрение, хлопки, следы нагрева","danger":"дуга, разрушение полоза, повреждение контактного провода"},"pantograph-slow-rise":{"category":"Высоковольтные цепи","title":"Токоприёмник поднимается медленно или не удерживает положение","summary":"Подъём затянут, давление теряется либо токоприёмник самопроизвольно опускается.","equipment":"клапан №245, привод токоприёмника, воздушная магистраль","signs":"шипение, замедленный подъём, падение давления","danger":"повреждение рамы, дуга, касание контактной сети"},"pantograph-wrong-selection":{"category":"Высоковольтные цепи","title":"Не соответствует выбор токоприёмника","summary":"Поднимается не выбранный аппарат либо индикация не совпадает с фактическим положением.","equipment":"токоприёмники, цепь выбора, межсекционные соединения","signs":"несоответствие команды и положения","danger":"подъём повреждённого аппарата, одновременное нештатное состояние"},"roof-insulation-signs":{"category":"Высоковольтные цепи","title":"Признаки пробоя крышевой изоляции","summary":"Наблюдаются треск, следы перекрытия или необычное свечение на крышевом оборудовании.","equipment":"крышевые шины, изоляторы, токоприёмник","signs":"треск, вспышки, следы копоти","danger":"дуга, пожар, повреждение контактной сети"}}''')
QUESTIONS = [
    "Признак относится только к одной секции, тележке или группе?",
    "Признак устойчиво повторяется при одинаковом безопасном наблюдении?",
    "Есть опасный нагрев, дым, дуга, утечка, разрушение или защитное отключение?",
]
PROHIBITED = {
    "HV_INTERVENTION", "ROOF_ACCESS", "PROTECTION_BYPASS", "JUMPER",
    "FORCED_ENERGIZATION", "TEST_RESTART", "LIVE_MEASUREMENT",
}
FORBIDDEN = re.compile(
    r"(?i)\b(?:включите|перемкните|замкните|вскройте|измерьте|запустите|"
    r"сбросьте|повторите\s+пуск|установите\s+перемычку|поднимите\s+токоприемник)\b"
)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def graph_check(graph, count):
    nodes = graph["nodes"]
    by_id = {n["id"]: n for n in nodes}
    require(len(nodes) == len(by_id) == count, "graph count/duplicate")
    seen, stack = set(), [graph["startNodeId"]]
    while stack:
        key = stack.pop()
        require(key in by_id, "missing graph target")
        if key in seen:
            continue
        seen.add(key)
        node = by_id[key]
        require(node["type"] in {"QUESTION", "STOP", "OBSERVATION_REPORT"}, "node type")
        require(node["recordedOnly"] is True, "not recorded-only")
        require(node["operationRequested"] is False and node["causeConfirmed"] is False, "operation/cause")
        require(set(node["sourceRefs"]) and set(node["sourceRefs"]) <= {"donor", "manual1990", "textbook2006"}, "node source")
        require(not FORBIDDEN.search(node["text"]), "unsafe imperative")
        if node["type"] == "QUESTION":
            require(set(node["responses"]) == {"YES", "NO", "UNKNOWN"}, "tri-state")
            require(by_id.get(node["responses"]["UNKNOWN"], {}).get("type") == "STOP", "UNKNOWN must STOP")
            stack.extend(node["responses"].values())
        else:
            require(node["responses"] == {}, "terminal with outgoing edge")
    require(seen == set(by_id), "unreachable node")
    require(by_id["s_unknown"]["type"] == "STOP" and by_id["s_danger"]["type"] == "STOP", "critical STOP")
    require(by_id["s_record"]["type"] == "OBSERVATION_REPORT", "report type")
    require(by_id["s_unresolved"]["type"] == "STOP", "unresolved STOP")

def check_one(x, migration, inventory):
    ident = x["originalId"]
    e = EXPECTED[ident]
    src = next((v for v in migration if v["id"] == ident), None)
    row = next((v for v in inventory if v["scenarioId"] == "vl80s.diag." + ident), None)
    require(src is not None and row is not None, "migration/inventory missing")
    require(x["schemaVersion"] == "diagnostic-stage9-hv-source-first/2", "schema")
    require(x["stage"] == "9/51" and x["batch"] == "HV_PANTOGRAPH_ROOF_BATCH2", "stage/batch")
    require(x["scenarioId"] == "vl80s.diag." + ident, "scenario ID")
    for field in ("title", "summary", "category"):
        require(x[field] == e[field] == src[field], "donor " + field)
    require(x["donorOriginalCategory"] == e["category"], "donor original category")
    require(x["categoryNormalizationNote"] == "ORIGINAL_AND_MIGRATION_MATCH", "category disposition")
    require(x["donorPinnedSha"] == DONOR and x["donorOriginalQuestions"] == QUESTIONS, "donor questions")
    require(x["authoringProfileId"] == "vl80s-general", "authoring profile")
    require(x["exactInstalledVariant"] == "UNKNOWN" and x["unknownVariantDisposition"] == "BLOCKED", "variant gate")
    require(len(x["mustRemainDistinctFrom"]) >= 3 and len(x["mustRemainDistinctFrom"]) == len(set(x["mustRemainDistinctFrom"])), "distinct boundary")
    require(x["scenarioId"] not in x["mustRemainDistinctFrom"], "self-overlap")
    require(bool(x["canonicalBoundary"]), "boundary")
    donor = x["sourceRecords"]["donor"]
    require(donor["kind"] == "PINNED_DONOR_GENERATED_CATALOG", "donor type")
    require(donor["repository"] == "DomEnota-hub/Test-" and donor["commit"] == DONOR, "donor identity")
    require(donor["path"] == "app/src/main/java/ru/railbrake/calculator/core/DiagnosticExtendedCatalog.kt", "donor path")
    require(donor["blobSha"] == DONOR_BLOB and donor["sourcePointer"] == 'Seed("' + ident + '"', "donor pointer")
    require(donor["questionGenerator"] == "toScenario(seed), shared three questions", "question generator")
    require(donor["originalQuestions"] == QUESTIONS, "question parity")
    require(donor["seedFields"] == {k: e[k] for k in ("equipment", "signs", "danger")}, "seed field parity")
    require(donor["currentOperatingAuthority"] is False and donor["proceduresImported"] is False, "donor procedures")
    for source_id, kind, year in (("manual1990", "HISTORICAL_FACTORY_MANUAL", 1990), ("textbook2006", "HISTORICAL_EDUCATIONAL_TEXTBOOK", 2006)):
        s = x["sourceRecords"][source_id]
        require(s["kind"] == kind and s["year"] == year, "source kind/year")
        require(s["url"].startswith("https://djvu.online/file/"), "source URL")
        require(len(s["verifiedLocators"]) == 2 and all(s["verifiedLocators"]), "source locators")
        for key in ("currentOperatingAuthority", "modernRevisionVerified", "exactInstalledEquipmentVerified", "proceduresImported"):
            require(s[key] is False, "source gate " + key)
    claims = x["historicalEvidenceClaims"]
    require(len(claims) == 4 and len({v["id"] for v in claims}) == 4, "claims count/IDs")
    for claim in claims:
        require(claim["sourceId"] in ("manual1990", "textbook2006"), "claim source")
        require(claim["locator"] in x["sourceRecords"][claim["sourceId"]]["verifiedLocators"], "claim locator")
        require(claim["confidence"] in ("HISTORICAL_DESCRIPTION_ONLY", "EDUCATIONAL_HISTORICAL_ONLY"), "claim confidence")
        require(all(claim[k] is False for k in ("provesCurrentEquipment", "provesFaultCause", "authorizesAction")), "claim authority")
    require(set(x["versions"]) == {"SHORT", "DETAILED"}, "version set")
    graph_check(x["versions"]["SHORT"], 6)
    graph_check(x["versions"]["DETAILED"], 12)
    extensions = x["informationExtensions"]
    require(len(extensions) == 5 and len({v["id"] for v in extensions}) == 5, "extension count/IDs")
    require([v["version"] for v in extensions] == ["SHORT", "SHORT", "DETAILED", "DETAILED", "DETAILED"], "extension versions")
    require(len({v["approachFocus"] for v in extensions}) == 5, "extension approach distinct")
    for ext in extensions:
        require(ext["kind"] in ("HISTORICAL_INFORMATION_ONLY", "EDUCATIONAL_INFORMATION_ONLY"), "extension kind")
        require(ext["warningRequired"] is True and ext["actionAuthorityGranted"] is False, "extension safety")
        require(len(ext["text"]) >= 70 and not FORBIDDEN.search(ext["text"]), "extension text")
        require(len(ext["sourceRefs"]) == 1 and ext["sourceRefs"][0] in ("manual1990", "textbook2006"), "extension source")
        require(ext["locator"] in x["sourceRecords"][ext["sourceRefs"][0]]["verifiedLocators"], "extension locator")
    warning = x["extendedWarning"]
    require(warning["default"] == "HIDDEN", "warning default")
    require(warning["requiresReadToEnd"] is True and warning["requiresAcknowledgement"] is True, "warning consent")
    require(warning["consentResetsOnClose"] is True and warning["warningGrantsActionAuthority"] is False, "warning reset")
    safety = x["safety"]
    require(safety["observationOnly"] is True and safety["onlyPreviouslyRecorded"] is True, "observation gate")
    require(safety["triState"] == ["YES", "NO", "UNKNOWN"] and safety["unknownMustStop"] is True, "tri-state gate")
    require(safety["operationsAllowed"] == [] and set(safety["prohibited"]) == PROHIBITED, "operations")
    require(all(safety[k] == "NOT_APPROVED" for k in ("roleGate", "sourceGate", "safetyGate")), "promotion gates")
    require(x["publicationStatus"] == "CANDIDATE", "publication")
    require(all(x[k] is False for k in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified")), "runtime gates")
    require(x["deviceQA"] == "NOT_RUN_DEFERRED", "device QA")

MUTATIONS = [
    (["scenarioId"], "vl80s.diag.wrong"),
    (["title"], "wrong"),
    (["summary"], "wrong"),
    (["category"], "wrong"),
    (["donorOriginalCategory"], "wrong"),
    (["donorOriginalQuestions", 0], "wrong"),
    (["sourceRecords", "donor", "commit"], "wrong"),
    (["sourceRecords", "donor", "blobSha"], "wrong"),
    (["sourceRecords", "donor", "seedFields", "danger"], "wrong"),
    (["sourceRecords", "manual1990", "currentOperatingAuthority"], True),
    (["sourceRecords", "textbook2006", "modernRevisionVerified"], True),
    (["historicalEvidenceClaims", 0, "authorizesAction"], True),
    (["historicalEvidenceClaims", 0, "locator"], "invented"),
    (["exactInstalledVariant"], "CONFIRMED"),
    (["unknownVariantDisposition"], "ALLOW"),
    (["publicationStatus"], "PUBLISHED"),
    (["runtimeImport"], True),
    (["executable"], True),
    (["actionAuthorityGranted"], True),
    (["sourceAuthorityVerified"], True),
    (["safety", "roleGate"], "APPROVED"),
    (["safety", "sourceGate"], "APPROVED"),
    (["safety", "safetyGate"], "APPROVED"),
    (["safety", "operationsAllowed"], ["LIVE_MEASUREMENT"]),
    (["extendedWarning", "default"], "VISIBLE"),
    (["extendedWarning", "requiresReadToEnd"], False),
    (["extendedWarning", "requiresAcknowledgement"], False),
    (["extendedWarning", "consentResetsOnClose"], False),
    (["extendedWarning", "warningGrantsActionAuthority"], True),
    (["informationExtensions", 0, "warningRequired"], False),
    (["informationExtensions", 0, "actionAuthorityGranted"], True),
    (["informationExtensions", 0, "locator"], "invented"),
    (["versions", "SHORT", "nodes", 0, "responses", "UNKNOWN"], "s_record"),
    (["versions", "DETAILED", "nodes", 0, "operationRequested"], True),
    (["versions", "DETAILED", "nodes", 1, "sourceRefs"], []),
    (["versions", "DETAILED", "nodes", 1, "text"], "Включите ГВ"),
    (["versions", "DETAILED", "nodes", 1, "id"], "q1"),
    (["versions", "DETAILED", "nodes", 8, "type"], "OBSERVATION_REPORT"),
    (["versions", "SHORT", "nodes", 0, "type"], "STOP"),
    (["deviceQA"], "PASS"),
]

def change(obj, path, value):
    target = obj
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value

def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    migration = json.loads(MIGRATION.read_text(encoding="utf-8"))["sourceObject"]["scenarios"]
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))["rows"]
    rows = d["candidates"]
    require(d["ledger"]["donorPinnedSha"] == DONOR, "ledger donor")
    require(d["ledger"]["donorBlobSha"] == DONOR_BLOB, "ledger blob")
    require(d["ledger"]["runtimeImport"] is False and d["ledger"]["actionAuthorityGranted"] is False, "ledger gate")
    require(d["ledger"]["publicationStatus"] == "CANDIDATE", "ledger publication")
    require(len(rows) == len(IDS) == 5, "batch count")
    require([x["originalId"] for x in rows] == IDS, "batch IDs/order")
    require(d["ledger"]["scenarioIds"] == [x["scenarioId"] for x in rows], "ledger IDs")
    require(d["ledger"]["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "ledger device QA")
    for row in rows:
        check_one(row, migration, inventory)
    failures = 0
    for row in rows:
        for path, value in MUTATIONS:
            broken = copy.deepcopy(row)
            change(broken, path, value)
            try:
                check_one(broken, migration, inventory)
            except (ValueError, KeyError, TypeError, IndexError):
                failures += 1
            else:
                raise AssertionError("Negative QA did not reject: " + row["originalId"] + " / " + repr(path))
    require(failures == len(rows) * len(MUTATIONS), "negative count")
    print("STAGE9_HV_PANTOGRAPH_BATCH2_PASS", len(rows), "negative_mutations", failures,
          "short_nodes", len(rows)*6, "detailed_nodes", len(rows)*12,
          "extensions", len(rows)*5)

if __name__ == "__main__":
    main()
