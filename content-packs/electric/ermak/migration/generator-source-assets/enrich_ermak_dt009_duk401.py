#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
DT_ID = "ER-EQ-TR-011"
DT_ARTICLE_ID = "ER-KB-EQ-ER-EQ-TR-011"
DUK_ID = "ER-EQ-TR-012"
DUK_ARTICLE_ID = "ER-KB-EQ-ER-EQ-TR-012"

SCHEME_SOURCE_ID = "ER-SRC-002"
RE4_SOURCE_ID = "ER-SRC-005"
DT_TECH_SOURCE_ID = "ER-SRC-073"
DUK_TECH_SOURCE_ID = "ER-SRC-074"
REPAIR_SOURCE_ID = "ER-SRC-075"

DT_TECH_REF = {
    "sourceId": DT_TECH_SOURCE_ID,
    "document": "ИДМБ.661142.004-01РЭ4, электровоз ЭП1М (ЭП1П), заводское руководство по эксплуатации",
    "title": "Датчик тока ДТ-009 — назначение, устройство и технические характеристики",
    "url": "https://djvu.online/file/TVgYn3LTUveDJ",
    "locator": "раздел 59 «Датчик тока ДТ-009», листы 195–196",
}
DUK_TECH_REF = {
    "sourceId": DUK_TECH_SOURCE_ID,
    "document": "ИДМБ.661142.004-01РЭ4, электровоз ЭП1М (ЭП1П), заводское руководство по эксплуатации",
    "title": "Датчик угла коммутации ДУК-4-01 — назначение, устройство и технические характеристики",
    "url": "https://djvu.online/file/TVgYn3LTUveDJ",
    "locator": "раздел 61 «Датчик угла коммутации ДУК-4-01», лист 199",
}
REPAIR_REF = {
    "sourceId": REPAIR_SOURCE_ID,
    "document": "ПКБ ЦТ.06.0046, руководство по ТО, ТР и ДР электровозов 2(3)ЭС5К, Э5К",
    "title": "ДТ-009, LV100/SP51 и ДУК-4-01 — контроль при ремонте",
    "url": "https://rcit.su/techinfoR8.html",
    "locator": "раздел 13.6.11",
}

DT_PARAMETERS = [
    {"name": "Номинальное напряжение изоляции шины первичного тока", "value": 3000, "unit": "V", "sourceId": DT_TECH_SOURCE_ID},
    {"name": "Номинальный первичный ток", "value": 1000, "unit": "A", "sourceId": DT_TECH_SOURCE_ID},
    {"name": "Диапазон измеряемого тока", "value": "0–1500", "unit": "A", "sourceId": DT_TECH_SOURCE_ID},
    {"name": "Коэффициент трансформации", "value": "1:5000", "unit": "", "sourceId": DT_TECH_SOURCE_ID},
    {"name": "Напряжение питания датчика", "value": "±24", "unit": "V", "sourceId": DT_TECH_SOURCE_ID},
    {"name": "Выходное внутреннее сопротивление", "value": 40, "unit": "Ohm", "sourceId": DT_TECH_SOURCE_ID},
    {"name": "Режим работы", "value": "продолжительный", "unit": "", "sourceId": DT_TECH_SOURCE_ID},
    {"name": "Охлаждение", "value": "воздушное естественное", "unit": "", "sourceId": DT_TECH_SOURCE_ID},
    {"name": "Масса", "value": 3.5, "unit": "kg", "sourceId": DT_TECH_SOURCE_ID},
]

DUK_PARAMETERS = [
    {"name": "Номинальный ток первичной обмотки", "value": 2550, "unit": "A", "sourceId": DUK_TECH_SOURCE_ID},
    {"name": "Часовой ток первичной обмотки", "value": 2750, "unit": "A", "sourceId": DUK_TECH_SOURCE_ID},
    {"name": "Напряжение вторичной обмотки при номинальном первичном токе", "value": 21, "unit": "V", "sourceId": DUK_TECH_SOURCE_ID},
    {"name": "Номинальный ток вторичной обмотки", "value": 0.03, "unit": "A", "sourceId": DUK_TECH_SOURCE_ID},
    {"name": "Масса", "value": 8.5, "unit": "kg", "sourceId": DUK_TECH_SOURCE_ID},
]


def read_gz(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def write_gz(path: Path, payload):
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with path.open("wb") as out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0, compresslevel=9) as gz:
            gz.write(raw)


def unique_refs(items):
    result, seen = [], set()
    for item in items:
        key = item.get("sourceId") if isinstance(item, dict) else str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def register_source(registry, key, ref):
    source_id = ref["sourceId"]
    for existing_key, existing in registry.items():
        if isinstance(existing, dict) and existing.get("sourceId") == source_id:
            if existing_key != key and existing != ref:
                raise SystemExit(f"Source ID {source_id} already used by {existing_key}")
    registry[key] = ref


def kb_parameters(items, applicability):
    return [
        {
            "name": p["name"],
            "value": p["value"],
            "unit": p["unit"],
            "applicability": applicability,
            "status": "BASE_CONFIRMED",
            "sourceRefs": [p["sourceId"]],
        }
        for p in items
    ]


def find_record(root, equipment_id):
    matches = [r for r in root["records"] if r.get("id") == equipment_id]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one {equipment_id}, found {len(matches)}")
    return matches[0]


def find_article(root, equipment_id, article_id):
    matches = [a for a in root["articles"] if a.get("id") == article_id or a.get("equipmentId") == equipment_id]
    by_id = {a.get("id"): a for a in matches}
    if len(by_id) != 1:
        raise SystemExit(f"Expected exactly one article for {equipment_id}, found {list(by_id)}")
    return next(iter(by_id.values()))


def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault("sourceRegistry", {})
    register_source(registry, "DT009_FACTORY_DATA", DT_TECH_REF)
    register_source(registry, "DUK401_FACTORY_DATA", DUK_TECH_REF)
    register_source(registry, "TR_SENSOR_REPAIR_GUIDE", REPAIR_REF)

    dt = find_record(root, DT_ID)
    duk = find_record(root, DUK_ID)
    tr008 = find_record(root, "ER-EQ-TR-008")
    tr009 = find_record(root, "ER-EQ-TR-009")
    tr010 = find_record(root, "ER-EQ-TR-010")

    if dt.get("modelNames") != ["ДТ-009"] or dt.get("schemeDesignations") != ["ДТ", "ДТЯ", "ДТВ"]:
        raise SystemExit(f"Unexpected {DT_ID} identity: {dt.get('modelNames')!r} / {dt.get('schemeDesignations')!r}")
    if duk.get("modelNames") != ["ДУК-4-01"] or duk.get("schemeDesignations") != ["T21", "T22", "T23", "T24"]:
        raise SystemExit(f"Unexpected {DUK_ID} identity: {duk.get('modelNames')!r} / {duk.get('schemeDesignations')!r}")
    if dt.get("parameters") or duk.get("parameters"):
        raise SystemExit("TR-011 or TR-012 already has parameters; review concurrent changes before enriching")
    if len(tr008.get("parameters", [])) != 7 or len(tr009.get("parameters", [])) != 5 or len(tr010.get("parameters", [])) != 8:
        raise SystemExit("TR-008/TR-009/TR-010 state changed; stop before applying sensor package")

    dt["purpose"] = (
        "Измерение постоянного, пульсирующего и переменного тока в тяговых цепях с формированием "
        "гальванически развязанного сигнала для регулирования, диагностики и защит МСУД-Н."
    )
    dt["parameters"] = DT_PARAMETERS
    dt["sourceRefs"] = unique_refs(dt.get("sourceRefs", []) + [DT_TECH_REF, REPAIR_REF])
    dt["parameterCoverage"] = {"status": "documented", "count": len(DT_PARAMETERS)}
    dt_notes = [n for n in dt.get("notes", []) if not n.startswith("ДТ-009:") and not n.startswith("LT-1000")]
    dt_notes += [
        "ДТ-009: датчик работает по компенсационному принципу; ток измерительного контура повторяет ток первичной цепи в масштабе 1:5000, а выходной сигнал снимается через измерительный резистор с вывода M.",
        "Заводское описание того же аппарата указывает внутренний датчик-трансформатор LEM LT-1000SI/SP58. В РЭ самого 2ЭС5К/3ЭС5К для соответствующих входов МСУД указан тип LT1000 без фиксации подисполнения, поэтому SP58 не считать обязательным для каждой секции без сверки маркировки.",
        "При контроле состояния важны исправность питания ±24 В, крепление силовой шины и датчика, целостность изоляции и разъёмов, а также правдоподобность сигнала относительно фактического тока цепи.",
    ]
    dt["notes"] = dt_notes

    duk["purpose"] = (
        "Формирование сигнала, пропорционального процессу коммутации ВИП, и передача его в МСУД-Н "
        "для авторегулирования инверторного режима."
    )
    duk["parameters"] = DUK_PARAMETERS
    duk["sourceRefs"] = unique_refs(duk.get("sourceRefs", []) + [DUK_TECH_REF, REPAIR_REF])
    duk["parameterCoverage"] = {"status": "documented", "count": len(DUK_PARAMETERS)}
    duk_notes = [n for n in duk.get("notes", []) if not n.startswith("ДУК-4-01:")]
    duk_notes += [
        "ДУК-4-01: первичной обмоткой служит медная шина; вторичная обмотка состоит из четырёх последовательно соединённых катушек, расположенных попарно по обе стороны шины.",
        "Каждая вторичная катушка содержит 250 витков провода ПЭТ-200 диаметром 0,63 мм на шести ферритовых кольцевых сердечниках; между обмотками расположен экран.",
        "На 2ЭС5К/3ЭС5К применяются четыре датчика T21–T24 на секцию; отказ или рассогласование одного канала нарушает достоверность информации об угле коммутации для МСУД-Н.",
    ]
    duk["notes"] = duk_notes

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    dt = find_article(root, DT_ID, DT_ARTICLE_ID)
    duk = find_article(root, DUK_ID, DUK_ARTICLE_ID)

    dt["summary"] = (
        "ДТ-009 измеряет ток тяговых цепей и передаёт в МСУД-Н гальванически развязанный масштабированный сигнал, "
        "используемый в регулировании, диагностике и защитах."
    )
    dt["principle"] = (
        "Первичная силовая шина проходит через магнитную систему датчика LEM. Электроника датчика по принципу компенсации "
        "магнитного поля формирует вторичный ток, пропорциональный первичному с коэффициентом 1:5000. Питание датчика — ±24 В; "
        "сигнал с измерительного вывода через резистор поступает в измерительные цепи МСУД-Н."
    )
    dt["keyParameters"] = kb_parameters(
        DT_PARAMETERS,
        "ДТ-009 базового исполнения в тяговых цепях 2ЭС5К/3ЭС5К; внутреннее подисполнение LEM сверять по маркировке конкретного датчика.",
    )
    dt["normalState"] = [
        "Корпус, изоляторы, силовая шина, крепёж и электрические соединения датчика целы, чисты и надёжно закреплены; следов перегрева и повреждения изоляции нет.",
        "Питание датчика ±24 В присутствует, цепи выводов «+», «-» и «M» исправны.",
        "Выходной сигнал изменяется согласованно с током контролируемой цепи и не имеет необъяснимых скачков, зависания или устойчивого смещения.",
        "Показания каналов тока в МСУД-Н согласуются с режимом работы тягового оборудования и не создают ложных ограничений или защитных воздействий.",
    ]
    dt["deviationSigns"] = [
        "Отсутствует или искажено питание ±24 В, повреждены разъёмы, проводка, изоляция, крепление датчика или силовой шины.",
        "Сигнал отсутствует, зависает, скачкообразно изменяется либо не соответствует фактическому изменению тока тяговой цепи.",
        "МСУД-Н фиксирует неправдоподобный ток, устойчивое рассогласование токовых каналов или связанные с каналом тока ограничения/защиты.",
        "Имеются следы перегрева, механического повреждения или загрязнения, способного ухудшить изоляцию и точность измерения.",
    ]
    dt_refs = dt.setdefault("sourceRefs", [])
    for ref in [SCHEME_SOURCE_ID, RE4_SOURCE_ID, DT_TECH_SOURCE_ID, REPAIR_SOURCE_ID]:
        if ref not in dt_refs:
            dt_refs.append(ref)
    dt_rules = [r for r in dt.get("variantRules", []) if not r.startswith("ДТ-009:")]
    dt_rules.append(
        "ДТ-009: паспортные значения относятся к типу ДТ-009. Заводское описание того же аппарата указывает LEM LT-1000SI/SP58, "
        "но РЭ 2ЭС5К/3ЭС5К фиксирует для соответствующих каналов лишь тип LT1000; конкретное подисполнение внутреннего преобразователя сверять по маркировке секции."
    )
    dt["variantRules"] = dt_rules
    dt.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    dt.setdefault("atlasData", {})["parameterCoverage"] = {"status": "documented", "count": len(DT_PARAMETERS)}

    duk["summary"] = (
        "ДУК-4-01 формирует сигнал, связанный с коммутацией ВИП; четыре датчика T21–T24 каждой секции передают эту информацию "
        "в МСУД-Н для авторегулирования инверторного режима."
    )
    duk["principle"] = (
        "Силовая медная шина образует первичную обмотку. Четыре вторичные катушки на ферритовых сердечниках соединены "
        "последовательно и формируют сигнал, пропорциональный процессу коммутации. Сигналы T21–T24 используются системой "
        "управления для контроля и регулирования угла коммутации ВИП."
    )
    duk["keyParameters"] = kb_parameters(
        DUK_PARAMETERS,
        "ДУК-4-01 в позициях T21–T24 базового исполнения 2ЭС5К/3ЭС5К.",
    )
    duk["normalState"] = [
        "Все четыре датчика T21–T24 установлены и подключены; шины, катушки, изоляция, крепёж и выводы не имеют механических повреждений и следов перегрева.",
        "Цепи вторичных обмоток исправны, соединения надёжны; отсутствуют обрывы и межвитковые повреждения, влияющие на выходной сигнал.",
        "Сигналы четырёх каналов изменяются согласованно с работой ВИП и обеспечивают устойчивое авторегулирование инверторного режима.",
        "При номинальном первичном токе 2550 А паспортное напряжение вторичной обмотки составляет 21 В при номинальном вторичном токе 0,03 А.",
    ]
    duk["deviationSigns"] = [
        "Один из каналов T21–T24 отсутствует, заметно отличается от остальных либо выдаёт нестабильный/неправдоподобный сигнал.",
        "Повреждены вторичная обмотка, изоляция, крепление, выводы или силовая шина датчика; имеются следы перегрева или механического воздействия.",
        "Нарушается устойчивость инверторного режима или МСУД-Н получает недостоверные данные об угле коммутации при исправных остальных элементах цепи.",
        "Выходной сигнал не соответствует изменению тока/режима ВИП, что требует проверки самого датчика, его цепей и подключённого измерительного канала.",
    ]
    duk_refs = duk.setdefault("sourceRefs", [])
    for ref in [SCHEME_SOURCE_ID, RE4_SOURCE_ID, DUK_TECH_SOURCE_ID, REPAIR_SOURCE_ID]:
        if ref not in duk_refs:
            duk_refs.append(ref)
    duk_rules = [r for r in duk.get("variantRules", []) if not r.startswith("ДУК-4-01:")]
    duk_rules.append(
        "ДУК-4-01: карточка относится к четырём датчикам T21–T24 базового 2ЭС5К/3ЭС5К. Паспортные данные взяты из заводского "
        "описания того же типа аппарата; при наличии иной маркировки на конкретной секции параметры необходимо сверять по её документации."
    )
    duk["variantRules"] = duk_rules
    duk.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    duk.setdefault("atlasData", {})["parameterCoverage"] = {"status": "documented", "count": len(DUK_PARAMETERS)}

    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / "ermak_equipment.json.gz")
    patch_knowledge(base / "ermak_knowledge.json.gz")

print("Ermak DT-009 and DUK-4-01 traction sensor references enriched in app and patch mirrors")
