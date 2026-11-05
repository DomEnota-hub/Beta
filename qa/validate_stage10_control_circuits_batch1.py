#!/usr/bin/env python3
"""Stage 10: control-circuit candidate parity, graph and mutation QA. No runtime promotion."""
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/diagnostics/STAGE10_CONTROL_CIRCUITS_BATCH1_2026-11-05.json"
MIGRATION = ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
EXPECTED = json.loads(r'''{"battery-no-charge":{"category":"Цепи управления","title":"Аккумуляторная батарея не заряжается","summary":"Напряжение не восстанавливается после запуска штатного источника.","seedFields":{"equipment":"АКБ, зарядный агрегат, ТРПШ, автоматы","signs":"низкое напряжение, нет признака зарядки","danger":"глубокий разряд, отказ управления"}},"battery-overcharge":{"category":"Цепи управления","title":"Повышенное напряжение или признаки перезаряда АКБ","summary":"Напряжение необычно высокое, есть нагрев или газовыделение.","seedFields":{"equipment":"АКБ, зарядный агрегат, регулятор","signs":"нагрев, запах, газовыделение","danger":"повреждение батареи, пожар"}},"control-fuse-trip":{"category":"Цепи управления","title":"Повторно отключается автомат цепей управления","summary":"После штатного включения защита низковольтной цепи снова срабатывает.","seedFields":{"equipment":"автоматы, цепи 50 В, потребители","signs":"повторное отключение","danger":"короткое замыкание, нагрев проводки"}},"cab-control-mismatch":{"category":"Цепи управления","title":"Органы управления и индикация кабины не согласованы","summary":"Положение рукояток, ламп и фактическая работа оборудования расходятся.","seedFields":{"equipment":"контроллер, сигнальные цепи, межсекционные соединения","signs":"ложная или отсутствующая индикация","danger":"неверная оценка состояния аппаратов"}},"intersection-command-loss":{"category":"Цепи управления","title":"Пропадает отдельная команда между секциями","summary":"Одна команда не исполняется ведомой секцией при сохранении остальных.","seedFields":{"equipment":"межсекционные соединения, реле, разъёмы","signs":"отказ одной функции секции","danger":"несогласованная работа секций"}}}''')
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
DONOR_BLOB = "090d448d0e9de20d002edf07361764e524298bf8"
QUESTIONS = json.loads(r'''["Признак относится только к одной секции, тележке или группе?","Признак устойчиво повторяется при одинаковом безопасном наблюдении?","Есть опасный нагрев, дым, дуга, утечка, разрушение или защитное отключение?"]''')
IDS = ["battery-no-charge","battery-overcharge","control-fuse-trip","cab-control-mismatch","intersection-command-loss"]
PROHIBITED = {"HV_INTERVENTION", "ROOF_ACCESS", "PROTECTION_BYPASS", "JUMPER", "FORCED_ENERGIZATION", "TEST_RESTART", "LIVE_MEASUREMENT", "CONTROL_CIRCUIT_INTERVENTION"}
FORBIDDEN = re.compile(r"(?i)\b(?:включите|перемкните|замкните|вскройте|измерьте|запустите|сбросьте|повторите\s+пуск|установите\s+перемычку|отключите\s+защиту)\b")

def require(condition, label):
    if not condition:
        raise ValueError(label)

def check_graph(g, count):
    nodes = g["nodes"]
    by = {n["id"]: n for n in nodes}
    require(len(nodes) == len(by) == count, "node count/duplicate")
    seen, todo = set(), [g["startNodeId"]]
    while todo:
        key = todo.pop()
        require(key in by, "edge target")
        if key in seen:
            continue
        seen.add(key)
        node = by[key]
        require(node["type"] in {"QUESTION", "STOP", "OBSERVATION_REPORT"}, "node type")
        require(node["recordedOnly"] is True and node["operationRequested"] is False and node["causeConfirmed"] is False, "node authority")
        require(set(node["sourceRefs"]) == {"donor", "manual1990", "textbook2006"}, "node provenance")
        require(not FORBIDDEN.search(node["text"]), "unsafe imperative")
        if node["type"] == "QUESTION":
            require(set(node["responses"]) == {"YES", "NO", "UNKNOWN"}, "tri-state")
            require(by.get(node["responses"]["UNKNOWN"], {}).get("type") == "STOP", "unknown not STOP")
            todo.extend(node["responses"].values())
        else:
            require(node["responses"] == {}, "terminal outgoing")
    require(seen == set(by), "unreachable")
    for key in ("s_unknown", "s_danger", "s_unresolved"):
        require(by[key]["type"] == "STOP", "stop boundary")
    require(by["s_record"]["type"] == "OBSERVATION_REPORT", "report boundary")

def check(x, migration):
    ident = x["originalId"]
    require(ident in EXPECTED, "id unknown")
    e = EXPECTED[ident]
    source = next((r for r in migration if r["id"] == ident), None)
    require(source is not None, "missing migration")
    require(x["schemaVersion"] == "diagnostic-stage10-control-source-first/1", "schema")
    require(x["stage"] == "10/51" and x["batch"] == "CONTROL_CIRCUITS_BATCH1", "stage")
    require(x["scenarioId"] == "vl80s.diag." + ident, "scenario id")
    for key in ("category", "title", "summary"):
        require(x[key] == e[key] == source[key], "donor parity " + key)
    require(x["donorOriginalCategory"] == e["category"] and x["categoryNormalizationNote"] == "ORIGINAL_AND_MIGRATION_MATCH", "category normalization")
    require(x["donorPinnedSha"] == DONOR and x["donorOriginalQuestions"] == QUESTIONS, "donor questions")
    require(x["authoringProfileId"] == "vl80s-general" and x["exactInstalledVariant"] == "UNKNOWN" and x["unknownVariantDisposition"] == "BLOCKED", "variant")
    require(len(x["mustRemainDistinctFrom"]) >= 3 and len(set(x["mustRemainDistinctFrom"])) == len(x["mustRemainDistinctFrom"]), "distinct")
    require(x["scenarioId"] not in x["mustRemainDistinctFrom"] and bool(x["canonicalBoundary"]), "boundary")
    src = x["sourceRecords"]
    d = src["donor"]
    require(d["kind"] == "PINNED_DONOR_GENERATED_CATALOG" and d["repository"] == "DomEnota-hub/Test-" and d["commit"] == DONOR, "donor identity")
    require(d["path"] == "app/src/main/java/ru/railbrake/calculator/core/DiagnosticExtendedCatalog.kt" and d["blobSha"] == DONOR_BLOB, "donor blob")
    require(d["sourcePointer"] == 'Seed("' + ident + '"' and d["seedFields"] == e["seedFields"], "seed")
    require(d["questionGenerator"] == "toScenario(seed), shared three questions" and d["originalQuestions"] == QUESTIONS, "question generator")
    require(d["currentOperatingAuthority"] is False and d["proceduresImported"] is False, "donor authority")
    for sid, kind in (("manual1990", "HISTORICAL_FACTORY_MANUAL"), ("textbook2006", "HISTORICAL_EDUCATIONAL_TEXTBOOK")):
        s = src[sid]
        require(s["kind"] == kind and len(s["verifiedLocators"]) == 2, "source kind/locator")
        require(s["url"].startswith("https://djvu.online/file/"), "source url")
        require(s["currentOperatingAuthority"] is False and s["modernRevisionVerified"] is False and s["exactInstalledEquipmentVerified"] is False and s["proceduresImported"] is False, "source authority")
    claims = x["historicalEvidenceClaims"]
    require(len(claims) == 4 and len({c["id"] for c in claims}) == 4, "claims")
    for c in claims:
        require(c["sourceId"] in {"manual1990", "textbook2006"}, "claim source")
        require(c["locator"] in src[c["sourceId"]]["verifiedLocators"], "claim locator")
        require(c["confidence"] in {"HISTORICAL_DESCRIPTION_ONLY", "EDUCATIONAL_HISTORICAL_ONLY"}, "claim confidence")
        require(c["provesCurrentEquipment"] is False and c["provesFaultCause"] is False and c["authorizesAction"] is False, "claim authority")
    require(set(x["versions"]) == {"SHORT", "DETAILED"}, "versions")
    check_graph(x["versions"]["SHORT"], 6)
    check_graph(x["versions"]["DETAILED"], 12)
    extensions = x["informationExtensions"]
    require(len(extensions) == 5 and len({e["id"] for e in extensions}) == 5, "extensions")
    require([e["version"] for e in extensions] == ["SHORT", "SHORT", "DETAILED", "DETAILED", "DETAILED"], "extension modes")
    for ex in extensions:
        require(len(ex["sourceRefs"]) == 1 and ex["sourceRefs"][0] in {"manual1990", "textbook2006"}, "extension source")
        require(ex["locator"] in src[ex["sourceRefs"][0]]["verifiedLocators"], "extension locator")
        require(ex["kind"] in {"HISTORICAL_INFORMATION_ONLY", "EDUCATIONAL_INFORMATION_ONLY"}, "extension kind")
        require(bool(ex["approachFocus"]) and bool(ex["text"]), "extension text")
        require(ex["warningRequired"] is True and ex["actionAuthorityGranted"] is False, "extension authority")
        require(not FORBIDDEN.search(ex["text"]), "extension unsafe imperative")
    w = x["extendedWarning"]
    require(w == {"default":"HIDDEN","requiresReadToEnd":True,"requiresAcknowledgement":True,"consentResetsOnClose":True,"warningGrantsActionAuthority":False}, "warning")
    safety = x["safety"]
    require(safety["observationOnly"] is True and safety["onlyPreviouslyRecorded"] is True, "observation only")
    require(safety["triState"] == ["YES","NO","UNKNOWN"] and safety["unknownMustStop"] is True, "tri-state safety")
    require(safety["operationsAllowed"] == [] and set(safety["prohibited"]) >= PROHIBITED, "prohibited")
    for gate in ("roleGate", "sourceGate", "safetyGate"):
        require(safety[gate] == "NOT_APPROVED", gate)
    require(x["publicationStatus"] == "CANDIDATE" and x["runtimeImport"] is False and x["executable"] is False and x["actionAuthorityGranted"] is False and x["sourceAuthorityVerified"] is False, "runtime gate")
    require(x["deviceQA"] == "NOT_RUN_DEFERRED", "device QA")

def main():
    obj = json.loads(DATA.read_text(encoding="utf-8"))
    migration = json.loads(MIGRATION.read_text(encoding="utf-8"))["sourceObject"]["scenarios"]
    rows = obj["candidates"]
    require(obj["ledger"]["scenarioIds"] == ["vl80s.diag."+i for i in IDS], "ledger ids")
    require(obj["ledger"]["baseHead"] == "b6353c26415a01d220f1166fb53387ef6b6f9a5b" and obj["ledger"]["donorPinnedSha"] == DONOR, "ledger provenance")
    require(obj["ledger"]["publicationStatus"] == "CANDIDATE" and obj["ledger"]["runtimeImport"] is False and obj["ledger"]["actionAuthorityGranted"] is False, "ledger gates")
    require(len(rows) == 5 and [x["originalId"] for x in rows] == IDS, "candidate count/ids")
    for row in rows:
        check(row, migration)
    mutators = [
        ("schema", lambda x: x.__setitem__("schemaVersion", "BAD")),
        ("stage", lambda x: x.__setitem__("stage", "9/51")),
        ("batch", lambda x: x.__setitem__("batch", "OTHER")),
        ("scenario", lambda x: x.__setitem__("scenarioId", "wrong")),
        ("category", lambda x: x.__setitem__("category", "Тяга")),
        ("title", lambda x: x.__setitem__("title", "other")),
        ("summary", lambda x: x.__setitem__("summary", "other")),
        ("donor_sha", lambda x: x.__setitem__("donorPinnedSha", "wrong")),
        ("questions", lambda x: x.__setitem__("donorOriginalQuestions", [])),
        ("variant", lambda x: x.__setitem__("exactInstalledVariant", "ASSUMED")),
        ("variant_gate", lambda x: x.__setitem__("unknownVariantDisposition", "ALLOW")),
        ("donor_blob", lambda x: x["sourceRecords"]["donor"].__setitem__("blobSha", "wrong")),
        ("seed", lambda x: x["sourceRecords"]["donor"]["seedFields"].__setitem__("danger", "other")),
        ("source_authority", lambda x: x["sourceRecords"]["manual1990"].__setitem__("currentOperatingAuthority", True)),
        ("claim_authority", lambda x: x["historicalEvidenceClaims"][0].__setitem__("authorizesAction", True)),
        ("graph_count", lambda x: x["versions"]["SHORT"]["nodes"].pop()),
        ("graph_unknown", lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].__setitem__("UNKNOWN", "s_record")),
        ("graph_yes", lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].__setitem__("YES", "missing")),
        ("node_operation", lambda x: x["versions"]["DETAILED"]["nodes"][1].__setitem__("operationRequested", True)),
        ("node_source", lambda x: x["versions"]["DETAILED"]["nodes"][1].__setitem__("sourceRefs", [])),
        ("node_unsafe", lambda x: x["versions"]["DETAILED"]["nodes"][1].__setitem__("text", "Установите перемычку")),
        ("extension_count", lambda x: x["informationExtensions"].pop()),
        ("extension_authority", lambda x: x["informationExtensions"][0].__setitem__("actionAuthorityGranted", True)),
        ("extension_locator", lambda x: x["informationExtensions"][0].__setitem__("locator", "unverified")),
        ("warning", lambda x: x["extendedWarning"].__setitem__("requiresReadToEnd", False)),
        ("warning_consent", lambda x: x["extendedWarning"].__setitem__("warningGrantsActionAuthority", True)),
        ("allowed", lambda x: x["safety"]["operationsAllowed"].append("RESTART")),
        ("prohibited", lambda x: x["safety"].__setitem__("prohibited", [])),
        ("role", lambda x: x["safety"].__setitem__("roleGate", "APPROVED")),
        ("source_gate", lambda x: x["safety"].__setitem__("sourceGate", "APPROVED")),
        ("safety_gate", lambda x: x["safety"].__setitem__("safetyGate", "APPROVED")),
        ("runtime", lambda x: x.__setitem__("runtimeImport", True)),
        ("executable", lambda x: x.__setitem__("executable", True)),
        ("publication", lambda x: x.__setitem__("publicationStatus", "PUBLISHED")),
        ("device", lambda x: x.__setitem__("deviceQA", "PASS")),
        ("distinct", lambda x: x.__setitem__("mustRemainDistinctFrom", [])),
    ]
    failures = 0
    for row in rows:
        for name, mutate in mutators:
            bad = copy.deepcopy(row)
            mutate(bad)
            try:
                check(bad, migration)
            except (ValueError, KeyError, TypeError, IndexError):
                failures += 1
            else:
                raise AssertionError("negative mutation accepted: "+row["originalId"]+" "+name)
    require(failures == len(rows)*len(mutators), "negative count")
    print("STAGE10_CONTROL_BATCH1_PASS", len(rows), "scenarios", failures, "negative_mutations", len(rows)*6, "SHORT nodes", len(rows)*12, "DETAILED nodes", len(rows)*5, "extensions")

if __name__ == "__main__":
    main()
