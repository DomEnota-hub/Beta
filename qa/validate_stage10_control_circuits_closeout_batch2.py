#!/usr/bin/env python3
"""Stage10 control-circuit closeout: donor provenance, graph and negative mutation QA. Never runtime."""
import copy, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"docs/diagnostics/STAGE10_CONTROL_CIRCUITS_CLOSEOUT_BATCH2_2026-11-05.json"
MIGRATION=ROOT/"content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
BATCH1=ROOT/"docs/diagnostics/STAGE10_CONTROL_CIRCUITS_BATCH1_2026-11-05.json"
EXPECTED=json.loads(r'''{"control-voltage-low":{"title":"Понижено или пропадает напряжение цепей управления","summary":"Аппараты работают неустойчиво, контакторы отпадают, освещение и сигнализация изменяются при нагрузке.","origin":"EXPANDED_PATCH","path":"patch/app/src/main/java/ru/railbrake/calculator/core/DiagnosticExpansion.kt","blob":"7a222f1eca7be9438d8a8dbad937235dec83b7ff","ptr":"expandedScenario(id = \"control-voltage-low\"","questions":["Напряжение заметно падает только при включении нагрузки?","Неисправность относится только к одной секции?","Есть признак нормальной зарядки аккумуляторной батареи?"],"boundary":"LOW_OR_UNSTABLE_CONTROL_VOLTAGE"},"section-control-loss":{"title":"Нет управления одной секцией или нарушена межсекционная связь","summary":"Команды ведущей секции не исполняются одной секцией либо её индикация противоречит фактическому состоянию.","origin":"EXPANDED_PATCH","path":"patch/app/src/main/java/ru/railbrake/calculator/core/DiagnosticExpansion.kt","blob":"7a222f1eca7be9438d8a8dbad937235dec83b7ff","ptr":"expandedScenario(id = \"section-control-loss\"","questions":["Работают ли на отказавшей секции вспомогательные машины?","Индикация положения аппаратов этой секции достоверна?","Отказ сохраняется после штатного перевода органов управления в ноль?"],"boundary":"SECTION_WIDE_COMMAND_OR_FEEDBACK_LOSS"},"battery-no-voltage":{"title":"АКБ не даёт напряжения в цепи управления","summary":"При отсутствии штатного питания батарея не поддерживает цепь управления; это отличается от отказа зарядки при сохранённом напряжении.","origin":"COMPLETION_CATALOG","path":"app/src/main/java/ru/railbrake/calculator/core/DiagnosticCompletionCatalog.kt","blob":"0d94801dcbe1d96e1a551a9dac8fef2a808b9029","ptr":"scenario(id = \"battery-no-voltage\"","questions":["При работе штатного зарядного источника напряжение управления восстанавливается?","Отсутствие напряжения наблюдается только на одной секции?","Есть нагрев, запах электролита, дым или повреждение батареи?"],"boundary":"BATTERY_NOT_SUPPLYING_CONTROL_BUS"},"relay-panel-overheat":{"title":"Запах или нагрев на релейной панели","summary":"Появились запах, потрескивание либо локальный перегрев панели.","origin":"GENERATED_SEED","path":"app/src/main/java/ru/railbrake/calculator/core/DiagnosticExtendedCatalog.kt","blob":"090d448d0e9de20d002edf07361764e524298bf8","ptr":"Seed(\"relay-panel-overheat\"","questions":["Признак относится только к одной секции, тележке или группе?","Признак устойчиво повторяется при одинаковом безопасном наблюдении?","Есть опасный нагрев, дым, дуга, утечка, разрушение или защитное отключение?"],"boundary":"RELAY_PANEL_THERMAL_OR_ODOR_SIGNS"}}''')
IDS=["control-voltage-low","section-control-loss","battery-no-voltage","relay-panel-overheat"]
DONOR="3176d6ee228f0ed4b78371f45209e10c1c724eff"
FORBIDDEN=re.compile(r"(?i)\\b(?:включите|перемкните|замкните|вскройте|измерьте|запустите|сбросьте|повторите\\s+пуск|установите\\s+перемычку|отключите\\s+защиту|прозвоните)\\b")
PROHIBITED={"HV_INTERVENTION","ROOF_ACCESS","PROTECTION_BYPASS","JUMPER","FORCED_ENERGIZATION","TEST_RESTART","LIVE_MEASUREMENT","CONTROL_CIRCUIT_INTERVENTION"}
def require(ok,why):
    if not ok: raise ValueError(why)
def graph(g,expected_count):
    ns=g["nodes"]; by={n["id"]:n for n in ns}
    require(len(ns)==len(by)==expected_count and g["startNodeId"]=="q1","graph count/ids")
    seen=set(); todo=[g["startNodeId"]]
    while todo:
        key=todo.pop(); require(key in by,"dangling edge")
        if key in seen: continue
        seen.add(key); n=by[key]
        require(n["type"] in {"QUESTION","STOP","OBSERVATION_REPORT"},"node type")
        require(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"node authority")
        require(set(n["sourceRefs"])=={"donor","manual1990","textbook2006"},"node source refs")
        require(not FORBIDDEN.search(n["text"]),"unsafe imperative")
        if n["type"]=="QUESTION":
            require(set(n["responses"])=={"YES","NO","UNKNOWN"},"tri state")
            require(by.get(n["responses"]["UNKNOWN"],{}).get("type")=="STOP","unknown stop")
            todo.extend(n["responses"].values())
        else: require(n["responses"]=={},"terminal outgoing")
    require(seen==set(by),"unreachable")
    require({n["id"] for n in ns if n["type"]=="QUESTION"}=={"q"+str(i) for i in range(1,expected_count-3)},"question ids")
    for k in ("s_unknown","s_danger","s_unresolved"): require(by[k]["type"]=="STOP","mandatory stop")
    require(by["s_record"]["type"]=="OBSERVATION_REPORT","report")
def check(x,migration):
    ident=x["originalId"]; require(ident in EXPECTED,"original id")
    e=EXPECTED[ident]; m=next((v for v in migration if v["id"]==ident),None)
    require(m is not None and m["category"]=="Цепи управления","migration category")
    require(x["schemaVersion"]=="diagnostic-stage10-control-closeout-source-first/1" and x["stage"]=="10/51" and x["batch"]=="CONTROL_CIRCUITS_CLOSEOUT_BATCH2","schema stage")
    require(x["scenarioId"]=="vl80s.diag."+ident and x["category"]==x["donorOriginalCategory"]=="Цепи управления","id/category")
    require(x["categoryNormalizationNote"]=="ORIGINAL_AND_MIGRATION_MATCH","category note")
    require(x["title"]==e["title"]==m["title"] and x["summary"]==e["summary"]==m["summary"],"donor parity")
    require(x["canonicalBoundary"]==e["boundary"] and len(x["mustRemainDistinctFrom"])>=4 and len(set(x["mustRemainDistinctFrom"]))==len(x["mustRemainDistinctFrom"]) and x["scenarioId"] not in x["mustRemainDistinctFrom"],"distinct boundary")
    require(x["donorPinnedSha"]==DONOR and x["donorOriginalQuestions"]==e["questions"] and x["donorOriginLayer"]==e["origin"],"donor questions")
    require(x["authoringProfileId"]=="vl80s-general" and x["exactInstalledVariant"]=="UNKNOWN" and x["unknownVariantDisposition"]=="BLOCKED","variant")
    src=x["sourceRecords"]; d=src["donor"]
    require(d["kind"]==e["origin"] and d["repository"]=="DomEnota-hub/Test-" and d["commit"]==DONOR,"donor identity")
    require(d["path"]==e["path"] and d["blobSha"]==e["blob"] and d["sourcePointer"]==e["ptr"] and d["originalQuestions"]==e["questions"],"donor provenance")
    require(d["originalCategory"]=="Цепи управления" and d["currentOperatingAuthority"] is False and d["proceduresImported"] is False,"donor authority")
    for sid,kind,year in (("manual1990","HISTORICAL_FACTORY_MANUAL",1990),("textbook2006","HISTORICAL_EDUCATIONAL_TEXTBOOK",2006)):
        s=src[sid]
        require(s["kind"]==kind and s["year"]==year and len(s["verifiedLocators"])==2,"source metadata")
        require(s["url"].startswith("https://djvu.online/file/"),"source url")
        require(all(s[k] is False for k in ("currentOperatingAuthority","modernRevisionVerified","exactInstalledEquipmentVerified","proceduresImported")),"source authority")
    claims=x["historicalEvidenceClaims"]; require(len(claims)==4 and len({c["id"] for c in claims})==4,"claims")
    for c in claims:
        require(c["sourceId"] in ("manual1990","textbook2006") and c["locator"] in src[c["sourceId"]]["verifiedLocators"],"claim locator")
        require(c["confidence"]==("HISTORICAL_DESCRIPTION_ONLY" if c["sourceId"]=="manual1990" else "EDUCATIONAL_HISTORICAL_ONLY"),"claim confidence")
        require(all(c[k] is False for k in ("provesCurrentEquipment","provesFaultCause","authorizesAction")),"claim authority")
    require(set(x["versions"])=={"SHORT","DETAILED"},"versions")
    graph(x["versions"]["SHORT"],6); graph(x["versions"]["DETAILED"],12)
    exs=x["informationExtensions"]
    require(len(exs)==5 and len({e["id"] for e in exs})==5,"extensions")
    require([e["version"] for e in exs]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension modes")
    for e in exs:
        require(len(e["sourceRefs"])==1 and e["sourceRefs"][0] in ("manual1990","textbook2006"),"extension refs")
        require(e["locator"] in src[e["sourceRefs"][0]]["verifiedLocators"],"extension locator")
        require(e["kind"]==("HISTORICAL_INFORMATION_ONLY" if e["sourceRefs"][0]=="manual1990" else "EDUCATIONAL_INFORMATION_ONLY"),"extension kind")
        require(bool(e["approachFocus"]) and bool(e["text"]) and not FORBIDDEN.search(e["text"]),"extension content")
        require(e["warningRequired"] is True and e["actionAuthorityGranted"] is False,"extension gate")
    require(x["extendedWarning"]=={"default":"HIDDEN","requiresReadToEnd":True,"requiresAcknowledgement":True,"consentResetsOnClose":True,"warningGrantsActionAuthority":False},"warning")
    s=x["safety"]
    require(s["observationOnly"] is True and s["onlyPreviouslyRecorded"] is True and s["triState"]==["YES","NO","UNKNOWN"] and s["unknownMustStop"] is True,"safety")
    require(s["operationsAllowed"]==[] and set(s["prohibited"])>=PROHIBITED,"prohibited")
    require(all(s[k]=="NOT_APPROVED" for k in ("roleGate","sourceGate","safetyGate")),"approval gates")
    require(x["publicationStatus"]=="CANDIDATE" and all(x[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified")),"runtime gate")
    require(x["deviceQA"]=="NOT_RUN_DEFERRED","device QA")
def main():
    obj=json.loads(DATA.read_text(encoding="utf-8"))
    migration=json.loads(MIGRATION.read_text(encoding="utf-8"))["sourceObject"]["scenarios"]
    batch1=json.loads(BATCH1.read_text(encoding="utf-8"))["candidates"]
    rows=obj["candidates"]; ledger=obj["ledger"]
    require([r["originalId"] for r in rows]==IDS and ledger["scenarioIds"]==["vl80s.diag."+i for i in IDS],"batch ids")
    require(ledger["baseHead"]=="f35dae8dd1da1a473a9728f8bcbf2d89d49fd805" and ledger["donorPinnedSha"]==DONOR,"ledger provenance")
    require(ledger["publicationStatus"]=="CANDIDATE" and ledger["runtimeImport"] is False and ledger["actionAuthorityGranted"] is False,"ledger gates")
    expected_all={m["id"] for m in migration if m["category"]=="Цепи управления"}
    actual_all={r["originalId"] for r in rows+batch1}
    require(len(rows)==4 and len(batch1)==5 and len(actual_all)==9 and actual_all==expected_all,"Stage10 control category coverage")
    for row in rows: check(row,migration)
    mutators=[
        ("schema",lambda x:x.__setitem__("schemaVersion","BAD")),
        ("stage",lambda x:x.__setitem__("stage","9/51")),
        ("batch",lambda x:x.__setitem__("batch","OTHER")),
        ("id",lambda x:x.__setitem__("scenarioId","bad")),
        ("category",lambda x:x.__setitem__("category","Тяга")),
        ("title",lambda x:x.__setitem__("title","bad")),
        ("summary",lambda x:x.__setitem__("summary","bad")),
        ("boundary",lambda x:x.__setitem__("canonicalBoundary","bad")),
        ("distinct",lambda x:x.__setitem__("mustRemainDistinctFrom",[])),
        ("donor sha",lambda x:x.__setitem__("donorPinnedSha","bad")),
        ("questions",lambda x:x.__setitem__("donorOriginalQuestions",[])),
        ("origin",lambda x:x.__setitem__("donorOriginLayer","bad")),
        ("profile",lambda x:x.__setitem__("authoringProfileId","assumed")),
        ("variant",lambda x:x.__setitem__("exactInstalledVariant","ASSUMED")),
        ("variant gate",lambda x:x.__setitem__("unknownVariantDisposition","ALLOWED")),
        ("donor path",lambda x:x["sourceRecords"]["donor"].__setitem__("path","bad")),
        ("donor blob",lambda x:x["sourceRecords"]["donor"].__setitem__("blobSha","bad")),
        ("donor source pointer",lambda x:x["sourceRecords"]["donor"].__setitem__("sourcePointer","bad")),
        ("donor authority",lambda x:x["sourceRecords"]["donor"].__setitem__("currentOperatingAuthority",True)),
        ("source kind",lambda x:x["sourceRecords"]["manual1990"].__setitem__("kind","CURRENT")),
        ("source locator",lambda x:x["sourceRecords"]["textbook2006"].__setitem__("verifiedLocators",[])),
        ("source current",lambda x:x["sourceRecords"]["manual1990"].__setitem__("modernRevisionVerified",True)),
        ("claim source",lambda x:x["historicalEvidenceClaims"][0].__setitem__("sourceId","other")),
        ("claim authority",lambda x:x["historicalEvidenceClaims"][0].__setitem__("authorizesAction",True)),
        ("graph short missing",lambda x:x["versions"]["SHORT"]["nodes"].pop()),
        ("graph detailed missing",lambda x:x["versions"]["DETAILED"]["nodes"].pop()),
        ("graph bad target",lambda x:x["versions"]["DETAILED"]["nodes"][0]["responses"].__setitem__("NO","missing")),
        ("graph unknown",lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].__setitem__("UNKNOWN","s_record")),
        ("graph action",lambda x:x["versions"]["DETAILED"]["nodes"][1].__setitem__("operationRequested",True)),
        ("graph imperative",lambda x:x["versions"]["DETAILED"]["nodes"][1].__setitem__("text","Включите автомат")),
        ("extension missing",lambda x:x["informationExtensions"].pop()),
        ("extension duplicate",lambda x:x["informationExtensions"][1].__setitem__("id",x["informationExtensions"][0]["id"])),
        ("extension locator",lambda x:x["informationExtensions"][0].__setitem__("locator","fabricated")),
        ("extension authority",lambda x:x["informationExtensions"][0].__setitem__("actionAuthorityGranted",True)),
        ("warning scroll",lambda x:x["extendedWarning"].__setitem__("requiresReadToEnd",False)),
        ("warning consent",lambda x:x["extendedWarning"].__setitem__("requiresAcknowledgement",False)),
        ("safety unknown",lambda x:x["safety"].__setitem__("unknownMustStop",False)),
        ("safety operations",lambda x:x["safety"].__setitem__("operationsAllowed",["TEST_RESTART"])),
        ("safety gate",lambda x:x["safety"].__setitem__("safetyGate","APPROVED")),
        ("runtime",lambda x:x.__setitem__("runtimeImport",True)),
        ("publication",lambda x:x.__setitem__("publicationStatus","PUBLISHED")),
        ("device QA",lambda x:x.__setitem__("deviceQA","PASS"))
    ]
    tested=0
    for row in rows:
        for name,mut in mutators:
            bad=copy.deepcopy(row); mut(bad)
            try: check(bad,migration)
            except (ValueError,KeyError,TypeError): tested+=1
            else: raise AssertionError("Mutation accepted: "+row["originalId"]+" "+name)
    print("STAGE10_CONTROL_CLOSEOUT_PASS",len(rows),"candidates",len(rows)*2,"graphs",len(rows)*5,"extensions",tested,"negative mutations",len(expected_all),"category IDs")
if __name__=="__main__": main()
