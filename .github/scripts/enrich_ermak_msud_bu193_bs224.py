#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
BU_ID = "ER-EQ-CT-002"
BU_ARTICLE_ID = "ER-KB-EQ-ER-EQ-CT-002"
BS_ID = "ER-EQ-CT-004"
BS_ARTICLE_ID = "ER-KB-EQ-ER-EQ-CT-004"
ERMAK_SCHEME_ID = "ER-SRC-002"
ERMAK_RE5_ID = "ER-SRC-006"
MSUD_MANUAL_ID = "ER-SRC-083"
BU_VARIANT_ID = "ER-SRC-084"

MSUD_MANUAL_REF = {
    "sourceId": MSUD_MANUAL_ID,
    "document": "ИДМБ.421455.001 РЭ (3ТС.676.004 РЭ), МСУД-Н",
    "title": "МСУД-Н — БУ-193, БС-224, структура двухсекционного электровоза",
    "url": "https://studfile.net/preview/13491985/",
    "locator": "разделы 1.1.2.2, 1.2.1 и 1.2.3",
}
BU_VARIANT_REF = {
    "sourceId": BU_VARIANT_ID,
    "document": "АО «Локомотивные электронные системы»: история разработки аппаратуры МСУД-Н",
    "title": "БУ-193-02 как более поздняя замена блока БУ-193",
    "url": "https://zaoles.ru/about/",
    "locator": "2009 год — разработка БУ-193-02 для замены БУ-193",
}

BU_PARAMETERS = [
    {"name": "Последовательный интерфейс бортовой сети", "value": "RS-485", "unit": "", "sourceId": MSUD_MANUAL_ID},
    {"name": "Резервирование контроллеров БУТП", "value": "МПК1 основной + МПК2 резервный", "unit": "", "sourceId": MSUD_MANUAL_ID},
    {"name": "Роль блока в составе секций", "value": "ведущий (master) / ведомый (slave)", "unit": "", "sourceId": MSUD_MANUAL_ID},
    {"name": "Структура регулирования в тяге", "value": "двухконтурная", "unit": "", "sourceId": ERMAK_SCHEME_ID},
    {"name": "Структура регулирования при рекуперации", "value": "трёхконтурная", "unit": "", "sourceId": ERMAK_SCHEME_ID},
]

BS_PARAMETERS = [
    {"name": "Схемные позиции на секции", "value": "A81, A82", "unit": "", "sourceId": ERMAK_SCHEME_ID},
    {"name": "Интерфейс бортовой сети", "value": "RS-485", "unit": "", "sourceId": MSUD_MANUAL_ID},
    {"name": "Разъёмы СМЕ блока A81", "value": "X19, X20", "unit": "", "sourceId": ERMAK_SCHEME_ID},
    {"name": "Межсекционные разъёмы блока A82", "value": "X18, X29", "unit": "", "sourceId": ERMAK_SCHEME_ID},
    {"name": "Интерфейс тормозного оборудования", "value": "CAN к УКТОЛ через A13", "unit": "", "sourceId": MSUD_MANUAL_ID},
    {"name": "Резервная передача команд при отказе БУ-193", "value": "SM1/S2 через X5 блока A82", "unit": "", "sourceId": ERMAK_SCHEME_ID},
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


def unique_strings(items):
    return list(dict.fromkeys(items))


def register_source(registry, key, ref):
    sid = ref["sourceId"]
    for old_key, old in registry.items():
        if isinstance(old, dict) and old.get("sourceId") == sid and old_key != key:
            raise SystemExit(f"Source ID {sid} already used by {old_key}")
    registry[key] = ref


def source_by_id(registry, sid):
    matches = [v for v in registry.values() if isinstance(v, dict) and v.get("sourceId") == sid]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one source {sid}, found {len(matches)}")
    return matches[0]


def find_record(root, eid):
    matches = [r for r in root["records"] if r.get("id") == eid]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one {eid}, found {len(matches)}")
    return matches[0]


def find_article(root, eid, aid):
    matches = [a for a in root["articles"] if a.get("id") == aid or a.get("equipmentId") == eid]
    by_id = {a.get("id"): a for a in matches}
    if len(by_id) != 1:
        raise SystemExit(f"Expected exactly one article for {eid}, found {list(by_id)}")
    return next(iter(by_id.values()))


def kb_params(items, applicability):
    return [{
        "name": p["name"], "value": p["value"], "unit": p["unit"],
        "applicability": applicability, "status": "BASE_CONFIRMED", "sourceRefs": [p["sourceId"]]
    } for p in items]


def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault("sourceRegistry", {})
    register_source(registry, "MSUD_N_ORIGINAL_MANUAL", MSUD_MANUAL_REF)
    register_source(registry, "BU19302_REPLACEMENT_BOUNDARY", BU_VARIANT_REF)
    scheme_ref = source_by_id(registry, ERMAK_SCHEME_ID)
    re5_ref = source_by_id(registry, ERMAK_RE5_ID)

    bu = find_record(root, BU_ID)
    bs = find_record(root, BS_ID)
    ct1 = find_record(root, "ER-EQ-CT-001")
    ct3 = find_record(root, "ER-EQ-CT-003")
    ct5 = find_record(root, "ER-EQ-CT-005")

    if bu.get("modelNames") != ["БУ-193"] or bu.get("schemeDesignations") != ["A55"]:
        raise SystemExit(f"Unexpected {BU_ID} identity")
    if bs.get("modelNames") != ["БС-224"] or bs.get("schemeDesignations"):
        raise SystemExit(f"Unexpected {BS_ID} identity/state")
    if bu.get("parameters") or bs.get("parameters"):
        raise SystemExit("CT-002 or CT-004 already enriched; review concurrent change")
    if ct1.get("parameters") or ct3.get("parameters") or len(ct5.get("parameters", [])) != 9:
        raise SystemExit("Neighbor CT records changed; stop before applying package")

    bu["purpose"] = (
        "Основной вычислительный блок МСУД-Н секции: принимает сигналы датчиков и органов управления, "
        "формирует управляющие воздействия для тяги и рекуперации, выполняет диагностику и обменивается командами по бортовой сети."
    )
    bu["parameters"] = BU_PARAMETERS
    bu["sourceRefs"] = unique_refs(bu.get("sourceRefs", []) + [MSUD_MANUAL_REF, BU_VARIANT_REF])
    bu["parameterCoverage"] = {"status": "documented", "count": len(BU_PARAMETERS)}
    bu["notes"] = [
        "A55: на каждой секции 2ЭС5К/3ЭС5К установлен свой БУ-193; ведущий блок выбирается при запуске, остальные работают ведомыми.",
        "БУТП содержит два идентичных микропроцессорных контроллера: МПК1 основной, МПК2 резервный.",
        "БУ-193-02 — более поздний блок, разработанный в 2009 году как замена БУ-193; его паспортные характеристики не перенесены в карточку базового БУ-193.",
        "Числа по памяти, количеству каналов и скорости RS-485 из вторичных материалов не включены из-за расхождений между ревизиями аппаратуры."
    ]

    bs["quantity"] = "2 per section"
    bs["schemeDesignations"] = ["A81", "A82"]
    bs["purpose"] = (
        "Сопряжение БУ-193 с внутрисекционной и межсекционной сетью МСУД-Н, СМЕ и внешним тормозным оборудованием; "
        "на секции используются два блока БС-224 в позициях A81 и A82 с различающимися подключениями."
    )
    bs["parameters"] = BS_PARAMETERS
    bs["sourceRefs"] = unique_refs(bs.get("sourceRefs", []) + [scheme_ref, MSUD_MANUAL_REF])
    bs["parameterCoverage"] = {"status": "documented", "count": len(BS_PARAMETERS)}
    bs["notes"] = [
        "A81: связан с розетками X19/X20 системы многих единиц, блоком индикации и системой пневматического торможения.",
        "A82: связан с межсекционными разъёмами X18/X29 и принимает на X5 сигналы SM1/S2 для передачи на другую секцию при отказе БУ-193 своей секции.",
        "В тексте РЭ1 позиции A81/A82 местами обозначены как «БУ-224»; наименование аппарата БС-224 подтверждено РЭ5 и отдельным руководством МСУД-Н, поэтому карточка сохраняет модель БС-224."
    ]

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    bu = find_article(root, BU_ID, BU_ARTICLE_ID)
    bs = find_article(root, BS_ID, BS_ARTICLE_ID)

    bu["summary"] = "БУ-193 (A55) — секционный вычислительный блок МСУД-Н, управляющий тягой, рекуперацией и диагностикой оборудования."
    bu["principle"] = (
        "Каждая секция имеет собственный A55. БУ-193 получает сигналы токов, напряжений, скоростей и ДУК, обрабатывает команды машиниста "
        "и формирует воздействия на преобразователи и релейно-контакторную аппаратуру. Ведущий БУ задаёт режим ведомым секциям по RS-485; "
        "в тяге применяется двухконтурное, а при рекуперации трёхконтурное регулирование."
    )
    bu["keyParameters"] = kb_params(BU_PARAMETERS, "Базовое исполнение МСУД-Н с БУ-193 на 2ЭС5К/3ЭС5К; не смешивать с БУ-193-02.")
    bu["normalState"] = [
        "БУ-193 участвует в обмене МСУД-Н по RS-485 и корректно определяется как ведущий либо ведомый блок секции.",
        "Сигналы датчиков тока, напряжения, скорости и угла коммутации поступают в A55 без выпадения связанных каналов.",
        "Управляющие команды тяговым преобразователям и релейно-контакторной аппаратуре формируются в соответствии с заданным режимом.",
        "Основной и резервный микропроцессорные контроллеры БУТП не дают признаков нарушения резервирования."
    ]
    bu["deviationSigns"] = [
        "Отсутствует обмен с другими секциями или блоками МСУД-Н при исправной линии связи.",
        "Не формируются управляющие воздействия при наличии корректных входных сигналов и разрешающих условий.",
        "Одновременно пропадает группа контролируемых аналоговых/импульсных параметров, заведённых на A55.",
        "Система фиксирует отказ ведущего/ведомого блока либо нарушение работы основного и резервного каналов БУТП."
    ]
    bu["sourceRefs"] = unique_strings(bu.get("sourceRefs", []) + [ERMAK_SCHEME_ID, ERMAK_RE5_ID, MSUD_MANUAL_ID, BU_VARIANT_ID])
    bu["variantRules"] = unique_strings(bu.get("variantRules", []) + [
        "БУ-193-02 является отдельным более поздним исполнением-заменой; его паспортные данные не считать характеристиками базового БУ-193.",
        "Карточка относится к профилю base_early с секционным БУ-193 (A55)."
    ])
    bu["atlasData"]["parameterCoverage"] = {"status": "documented", "count": len(BU_PARAMETERS)}
    bu["knowledgeCoverage"]["parameters"] = "documented"

    bs["summary"] = "БС-224 — блоки сопряжения A81/A82, формирующие коммуникационные связи МСУД-Н внутри секции, между секциями и по СМЕ."
    bs["principle"] = (
        "На секции применены два БС-224. A81 связывает A55 с кабиной, СМЕ и тормозным оборудованием; A82 обеспечивает межсекционный обмен. "
        "Через X5 A82 предусмотрен проводной проход сигналов SM1/S2 на другую секцию при отказе БУ-193 данной секции."
    )
    bs["keyParameters"] = kb_params(BS_PARAMETERS, "БС-224 в позициях A81/A82 базового 2ЭС5К/3ЭС5К.")
    bs["normalState"] = [
        "Оба блока A81 и A82 присутствуют в предусмотренных секцией позициях и участвуют в обмене бортовой сети.",
        "Внутрисекционный и межсекционный каналы RS-485 обеспечивают обмен между A55, блоком индикации и соседней секцией.",
        "Связь по СМЕ через X19/X20 и связь с тормозным оборудованием работают без потери соответствующих каналов.",
        "Резервная передача команд SM1/S2 через A82 доступна для предусмотренного схемой обхода отказавшего БУ-193."
    ]
    bs["deviationSigns"] = [
        "Нарушается внутрисекционная либо межсекционная связь при исправном БУ-193.",
        "Пропадает связь по СМЕ через X19/X20 или обмен с тормозным оборудованием при сохранной остальной сети.",
        "Отказ A81 либо A82 вызывает выпадение только соответствующей группы внешних/межсекционных соединений.",
        "При отказе БУ-193 не обеспечивается предусмотренная схемой передача сигналов SM1/S2 через A82."
    ]
    bs["sourceRefs"] = unique_strings(bs.get("sourceRefs", []) + [ERMAK_RE5_ID, ERMAK_SCHEME_ID, MSUD_MANUAL_ID])
    bs["variantRules"] = unique_strings(bs.get("variantRules", []) + [
        "Для базового 2ЭС5К/3ЭС5К карточка фиксирует два БС-224 на секцию: A81 и A82.",
        "Обозначение БС-224 подтверждено РЭ5 и руководством МСУД-Н; схемные позиции A81/A82 взяты из РЭ1."
    ])
    bs["atlasData"]["quantity"] = "2 per section"
    bs["atlasData"]["schemeDesignations"] = ["A81", "A82"]
    bs["atlasData"]["parameterCoverage"] = {"status": "documented", "count": len(BS_PARAMETERS)}
    bs["knowledgeCoverage"]["parameters"] = "documented"

    write_gz(path, root)


for root in ROOTS:
    patch_equipment(root / "ermak_equipment.json.gz")
    patch_knowledge(root / "ermak_knowledge.json.gz")

print("Enriched Ermak CT-002 BU-193 and CT-004 BS-224")
