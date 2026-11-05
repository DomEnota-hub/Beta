#!/usr/bin/env python3
"""Stage9 five-source-first research candidates: donor parity, graph and negative safety QA."""
import copy
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"docs/diagnostics/STAGE9_HV_PROTECTIONS_BATCH_2026-11-05.json"
MIG=json.loads((ROOT/"content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))["sourceObject"]["scenarios"]
INV=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))["rows"]
EXPECTED=json.loads("{\"substation-protection-roof\":{\"title\":\"Сработала защита подстанции: подозрение на крышевое оборудование\",\"summary\":\"После вспышки или повреждения на крыше пропало напряжение контактной сети; возможны повреждение токоприёмника, изолятора, крышевой шины или ГВ.\",\"category\":\"Высоковольтные цепи\",\"questions\":[\"Есть повреждение контактного провода, выход токоприёмника за габарит, провисание или сохраняющаяся дуга?\",\"Удалось по уже имеющимся показаниям установить секцию и поднятый токоприёмник в момент события?\"],\"donorPath\":\"app/src/main/java/ru/railbrake/calculator/core/DiagnosticCompletionCatalog.kt\",\"donorBlob\":\"0d94801dcbe1d96e1a551a9dac8fef2a808b9029\",\"locators\":[\"Раздел А, VI §54, печ. стр. 145: ОПН-25УХЛ1 и разрядник РВМК-IV, историческое описание защиты от перенапряжений\",\"Раздел Б, табл. 14, печ. стр. 275–276: подстанционная защита и возможные крышевые повреждения; операции по разъединителям НЕ импортированы\"],\"distinct\":[\"pantograph-no-rise\",\"roof-insulation-signs\",\"protection-trip\"]},\"transformer-protection\":{\"title\":\"Признаки неисправности тягового трансформатора или действие его защиты\",\"summary\":\"ГВ отключается по связанной защите, появляется ненормальный гул, масло, запах или нагрев трансформатора.\",\"category\":\"Высоковольтные цепи\",\"questions\":[\"Есть физические признаки: масло, дым, запах или ненормальный гул?\",\"Однозначно установлена защита трансформатора?\",\"Отключение повторилось после единственного разрешённого восстановления?\"],\"donorPath\":\"patch/app/src/main/java/ru/railbrake/calculator/core/DiagnosticExpansion.kt\",\"donorBlob\":\"7a222f1eca7be9438d8a8dbad937235dec83b7ff\",\"locators\":[\"Раздел А, IV §1, печ. стр. 40–42, рис. 45: тяговый трансформатор ОДЦЭ-5000/25Б, масло и принудительное охлаждение\",\"Раздел А, XI §3, печ. стр. 208–209: защиты силовых цепей; отдельная современная схема защиты трансформатора НЕ установлена\"],\"distinct\":[\"oil-pump-failure\",\"rectifier-differential-trip\",\"protection-trip\"]},\"protection-trip\":{\"title\":\"Сработала токовая, земляная или перегрузочная защита\",\"summary\":\"ГВ или отдельная группа отключились по сигналу защиты; причина не очевидна.\",\"category\":\"Защиты\",\"questions\":[\"Защита сработала повторно после разрешённого восстановления?\",\"Отказ связан с одной секцией/группой?\",\"Есть признаки дыма, запаха или дуги?\"],\"donorPath\":\"app/src/main/java/ru/railbrake/calculator/core/DiagnosticRepository.kt\",\"donorBlob\":\"5f57ff2c98f02a04692e8553700ec8d23077d166\",\"locators\":[\"Раздел А, VI §23, печ. стр. 94–95: реле заземления, контроля земли и перегрузки различаются по назначению\",\"Раздел А, XI §3, печ. стр. 208–209: защита силовых и вспомогательных цепей, РМТ и реле заземления 88\"],\"distinct\":[\"traction-ground-relay-trip\",\"rectifier-differential-trip\",\"aux-relay-113-trip\"]},\"rectifier-differential-trip\":{\"title\":\"ГВ отключился с сигналом БРД и ВУ-1 или ВУ-2\",\"summary\":\"Сработала дифференциальная защита, ГВ отключился и появилась индикация одной выпрямительной установки.\",\"category\":\"Защиты\",\"questions\":[\"Совпали отключение ГВ, указатель БРД и сигнал ВУ-1 либо ВУ-2?\",\"Были хлопок, вспышка, запах, дым или повторное отключение?\"],\"donorPath\":\"app/src/main/java/ru/railbrake/calculator/core/DiagnosticCompletionCatalog.kt\",\"donorBlob\":\"0d94801dcbe1d96e1a551a9dac8fef2a808b9029\",\"locators\":[\"Раздел А, VI §26, печ. стр. 102–104, рис. 138–140: БРД-356 и два дифференциальных реле\",\"Раздел А, XI §3, печ. стр. 208–209: дифференциальная защита ВУ; раздел Б, печ. стр. 240: сигналы ВУ1/ВУ2\"],\"distinct\":[\"rectifier-group-fault\",\"protection-trip\",\"traction-ground-relay-trip\"]},\"rectifier-group-fault\":{\"title\":\"Подозрение на неисправность выпрямительной установки\",\"summary\":\"Отсутствует ток одной группы, выражена асимметрия, срабатывает защита либо появляется ненормальный нагрев ВУ.\",\"category\":\"Силовые цепи\",\"questions\":[\"Отказ относится к одной группе одной секции?\",\"Проявление зависит от позиции ЭКГ?\",\"Есть токовая или земляная защита?\"],\"donorPath\":\"patch/app/src/main/java/ru/railbrake/calculator/core/DiagnosticExpansion.kt\",\"donorBlob\":\"7a222f1eca7be9438d8a8dbad937235dec83b7ff\",\"locators\":[\"Раздел А, V §1, печ. стр. 51, выпрямители ВУК-4000Т-02 и В-ОППД-3,15к-1,4к-02: конструктивно разные исполнения\",\"Раздел А, XI §3, печ. стр. 208–209: дифференциальная защита ВУ; различать отказ охлаждения и электрическую защиту\"],\"distinct\":[\"rectifier-differential-trip\",\"traction-current-imbalance\",\"motor-fan-failure\"]}}")
IDS=["substation-protection-roof","transformer-protection","protection-trip","rectifier-differential-trip","rectifier-group-fault"]
DONOR="3176d6ee228f0ed4b78371f45209e10c1c724eff"
BASE="e38676cbdaebd86ec6650b615425015f7e9560b0"
FORBIDDEN=re.compile(r"(?i)\b(?:включите|перемкните|замкните|вскройте|измерьте|запустите|сбросьте|повторите\s+пуск|установите\s+перемычку)\b")

def require(condition, reason):
    if not condition: raise ValueError(reason)

def validate_graph(graph, count):
    nodes=graph["nodes"]
    by={n["id"]:n for n in nodes}
    require(len(nodes)==len(by)==count, "graph size or duplicate node")
    seen=set()
    pending=[graph["startNodeId"]]
    while pending:
        key=pending.pop()
        require(key in by, "missing target")
        if key in seen: continue
        seen.add(key)
        n=by[key]
        require(n["type"] in ("QUESTION","STOP","OBSERVATION_REPORT"),"node type")
        require(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"unsafe node")
        require(set(n["sourceRefs"]) and set(n["sourceRefs"]) <= {"donor","manual1990"},"node source")
        require(not FORBIDDEN.search(n["text"]),"unsafe imperative")
        if n["type"]=="QUESTION":
            require(set(n["responses"])=={"YES","NO","UNKNOWN"},"tri-state")
            require(by.get(n["responses"]["UNKNOWN"],{}).get("type")=="STOP","unknown must stop")
            pending.extend(n["responses"].values())
        else:
            require(n["responses"]=={},"terminal outgoing")
    require(seen==set(by),"unreachable node")

def validate(d, ident):
    e=EXPECTED[ident]
    src=next((x for x in MIG if x["id"]==ident),None)
    row=next((x for x in INV if x["scenarioId"]=="vl80s.diag."+ident),None)
    require(src is not None and row is not None,"donor/inventory missing")
    require(d["schemaVersion"]=="diagnostic-stage9-hv-source-first/1" and d["stage"]=="9/51","schema")
    require(d["scenarioId"]=="vl80s.diag."+ident and d["originalId"]==ident,"id")
    for field in ("title","summary","category"):
        require(d[field]==e[field]==src[field],"donor "+field)
    require(d["donorOriginalQuestions"]==e["questions"],"donor question parity")
    require(d["donorOriginalCategory"]=={"rectifier-differential-trip":"Тяга"}.get(ident,e["category"]),"donor original category")
    require(d["categoryNormalizationNote"]==("ORIGINAL_AND_MIGRATION_MATCH" if d["donorOriginalCategory"]==d["category"] else "MIGRATION_CATEGORY_DIFFERS_FROM_PINNED_DONOR_KEEP_BOTH"),"category discrepancy")
    require(d["donorPinnedSha"]==DONOR,"donor commit")
    require(d["authoringProfileId"]=="vl80s-general" and d["exactInstalledVariant"]=="UNKNOWN" and d["unknownVariantDisposition"]=="BLOCKED","variant fail closed")
    require(set(d["mustRemainDistinctFrom"])=={"vl80s.diag."+x for x in e["distinct"]},"distinct scenarios")
    require(d["publicationStatus"]=="CANDIDATE" and d["runtimeImport"] is False and d["executable"] is False and d["actionAuthorityGranted"] is False and d["sourceAuthorityVerified"] is False,"publication gate")
    require(d["deviceQA"]=="NOT_RUN_DEFERRED","device deferred")
    sources=d["sourceRecords"]
    require(set(sources)=={"donor","manual1990"},"source keys")
    ds=sources["donor"]
    require(ds["kind"]=="PINNED_DONOR_CATALOG" and ds["repository"]=="DomEnota-hub/Test-" and ds["commit"]==DONOR and ds["path"]==e["donorPath"] and ds["blobSha"]==e["donorBlob"] and ds["originalQuestions"]==e["questions"],"donor provenance")
    require(ds["currentOperatingAuthority"] is False and ds["proceduresImported"] is False,"donor no authority")
    manual=sources["manual1990"]
    require(manual["kind"]=="HISTORICAL_FACTORY_MANUAL" and manual["year"]==1990 and manual["isbn"]=="5-277-01048-3" and manual["verifiedLocators"]==e["locators"],"manual provenance")
    require(manual["currentOperatingAuthority"] is False and manual["modernRevisionVerified"] is False and manual["exactInstalledEquipmentVerified"] is False and manual["proceduresImported"] is False,"manual no authority")
    require(len(d["historicalEvidenceClaims"])==2,"claims")
    for claim in d["historicalEvidenceClaims"]:
        require(claim["sourceId"]=="manual1990" and claim["locator"] in e["locators"] and claim["confidence"]=="HISTORICAL_DESCRIPTION_ONLY","claim provenance")
        require(claim["provesCurrentEquipment"] is False and claim["provesFaultCause"] is False and claim["authorizesAction"] is False,"claim authority")
    require(set(d["versions"])=={"SHORT","DETAILED"},"versions")
    validate_graph(d["versions"]["SHORT"],6)
    validate_graph(d["versions"]["DETAILED"],12)
    ext=d["informationExtensions"]
    require(len(ext)==5 and len({x["id"] for x in ext})==5 and len({x["approachFocus"] for x in ext})==5,"extensions unique")
    require([x["version"] for x in ext]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extensions per version")
    for x in ext:
        require(x["kind"]=="HISTORICAL_INFORMATION_ONLY" and x["warningRequired"] is True and x["actionAuthorityGranted"] is False,"extension authority")
        require(x["locator"] in e["locators"] and set(x["sourceRefs"]) <= set(sources) and x["sourceRefs"],"extension source")
        require(not FORBIDDEN.search(x["text"]),"unsafe extension")
    w=d["extendedWarning"]
    require(w=={"default":"HIDDEN","requiresReadToEnd":True,"requiresAcknowledgement":True,"consentResetsOnClose":True,"warningGrantsActionAuthority":False},"warning")
    s=d["safety"]
    require(s["observationOnly"] is True and s["onlyPreviouslyRecorded"] is True and s["triState"]==["YES","NO","UNKNOWN"] and s["unknownMustStop"] is True and s["operationsAllowed"]==[],"safety policy")
    require(s["roleGate"]=="NOT_APPROVED" and s["sourceGate"]=="NOT_APPROVED" and s["safetyGate"]=="NOT_APPROVED","independent gates")
    require({"HV_INTERVENTION","PROTECTION_BYPASS","JUMPER","FORCED_ENERGIZATION","TEST_RESTART","LIVE_MEASUREMENT"} <= set(s["prohibited"]),"prohibited actions")

def negative_mutations(d,ident):
    mutations=[
      lambda x:x.update(runtimeImport=True),
      lambda x:x.update(executable=True),
      lambda x:x.update(actionAuthorityGranted=True),
      lambda x:x.update(publicationStatus="PUBLISHED"),
      lambda x:x.update(sourceAuthorityVerified=True),
      lambda x:x.update(exactInstalledVariant="vl80s-937-1260"),
      lambda x:x.update(unknownVariantDisposition="ALLOW"),
      lambda x:x["donorOriginalQuestions"].append("invented question"),
      lambda x:x.update(title="invented title"),
      lambda x:x["sourceRecords"]["donor"].update(blobSha="invented"),
      lambda x:x["sourceRecords"]["manual1990"].update(currentOperatingAuthority=True),
      lambda x:x["sourceRecords"]["manual1990"].update(verifiedLocators=["invented"]),
      lambda x:x["historicalEvidenceClaims"][0].update(authorizesAction=True),
      lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="q2"),
      lambda x:x["versions"]["DETAILED"]["nodes"][0].update(text="Включите ГВ"),
      lambda x:x["versions"]["SHORT"]["nodes"].pop(),
      lambda x:x["informationExtensions"].pop(),
      lambda x:x["informationExtensions"][0].update(actionAuthorityGranted=True),
      lambda x:x["informationExtensions"][0].update(locator="unverified page"),
      lambda x:x["extendedWarning"].update(requiresReadToEnd=False),
      lambda x:x["extendedWarning"].update(warningGrantsActionAuthority=True),
      lambda x:x["safety"].update(operationsAllowed=["RESTART"]),
      lambda x:x["safety"].update(roleGate="APPROVED"),
      lambda x:x["safety"].update(unknownMustStop=False),
      lambda x:x.update(deviceQA="PASS"),
    ]
    for i,mutate in enumerate(mutations):
        broken=copy.deepcopy(d)
        mutate(broken)
        try:validate(broken,ident)
        except (ValueError,KeyError,TypeError):continue
        raise AssertionError("negative mutation accepted: "+ident+" #"+str(i))
    return len(mutations)

def main():
    obj=json.loads(DATA.read_text(encoding="utf-8"))
    l=obj["ledger"]
    require(l["schemaVersion"]=="stage9-hv-protections-batch/1" and l["stage"]=="9/51" and l["baseHead"]==BASE and l["donorPinnedSha"]==DONOR,"ledger")
    require(l["publicationStatus"]=="CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False and l["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","ledger safety")
    require(l["scenarioIds"]==["vl80s.diag."+i for i in IDS],"ledger ids")
    require([x["originalId"] for x in obj["candidates"]]==IDS,"batch IDs")
    total=0
    for d in obj["candidates"]:
        ident=d["originalId"]
        validate(d,ident)
        total+=negative_mutations(d,ident)
    print("STAGE9_HV_PROTECTIONS_PASS scenarios="+str(len(IDS))+" negative_mutations="+str(total))

if __name__=="__main__": main()
