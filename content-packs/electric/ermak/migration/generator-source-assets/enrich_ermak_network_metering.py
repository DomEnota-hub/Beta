#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
HV009_ID = "ER-EQ-HV-009"
HV009_ARTICLE_ID = "ER-KB-EQ-ER-EQ-HV-009"
HV010_ID = "ER-EQ-HV-010"
HV010_ARTICLE_ID = "ER-KB-EQ-ER-EQ-HV-010"
TR013_ID = "ER-EQ-TR-013"

SCHEME_SOURCE_ID = "ER-SRC-002"
RE4_SOURCE_ID = "ER-SRC-005"
TR19_FACTORY_SOURCE_ID = "ER-SRC-076"
TR19_ERMAK_MAPPING_SOURCE_ID = "ER-SRC-077"

TR19_FACTORY_REF = {
    "sourceId": TR19_FACTORY_SOURCE_ID,
    "document": "ИДМБ.661142.004-01РЭ4, электровоз ЭП1М (ЭП1П), заводское руководство по эксплуатации",
    "title": "Трансформатор Тр-19 — назначение, устройство и технические характеристики",
    "url": "https://djvu.online/file/TVgYn3LTUveDJ",
    "locator": "раздел 68 «Трансформатор Тр-19», листы 211–213",
}
TR19_ERMAK_MAPPING_REF = {
    "sourceId": TR19_ERMAK_MAPPING_SOURCE_ID,
    "document": "Учебно-технический материал по трансформаторам электровоза Ермак",
    "title": "Трансформатор Тр-19 (T12) — назначение и характеристики на Ермак",
    "url": "https://infourok.ru/urok-transformatori-elektrovoza-ermak-3322837.html",
    "locator": "раздел «Трансформатор Тр-19(Т12)»",
}

HV009_PARAMETERS = [
    {"name": "Номинальная мощность трансформатора T12 (Тр-19)", "value": 155, "unit": "VA", "sourceId": TR19_FACTORY_SOURCE_ID},
    {"name": "Номинальное напряжение первичной обмотки A-X", "value": 220, "unit": "V", "sourceId": TR19_FACTORY_SOURCE_ID},
    {"name": "Номинальное напряжение вторичной обмотки a2-x", "value": 233, "unit": "V", "sourceId": TR19_FACTORY_SOURCE_ID},
    {"name": "Номинальное напряжение вторичной обмотки a1-x", "value": 100, "unit": "V", "sourceId": TR19_FACTORY_SOURCE_ID},
    {"name": "Номинальный ток вторичной обмотки a2-x", "value": 0.6, "unit": "A", "sourceId": TR19_FACTORY_SOURCE_ID},
    {"name": "Номинальная частота", "value": 50, "unit": "Hz", "sourceId": TR19_FACTORY_SOURCE_ID},
    {"name": "Масса трансформатора Тр-19", "value": 2.5, "unit": "kg", "sourceId": TR19_FACTORY_SOURCE_ID},
]

HV010_PARAMETERS = [
    {"name": "Учитываемые направления электроэнергии", "value": "потребление и рекуперация", "unit": "", "sourceId": SCHEME_SOURCE_ID},
    {"name": "Токовый измерительный канал", "value": "T7", "unit": "", "sourceId": SCHEME_SOURCE_ID},
    {"name": "Напряженческий измерительный канал", "value": "T12 через панель U21", "unit": "", "sourceId": SCHEME_SOURCE_ID},
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


def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault("sourceRegistry", {})
    register_source(registry, "TR19_FACTORY_DATA", TR19_FACTORY_REF)
    register_source(registry, "TR19_ERMAK_T12_MAPPING", TR19_ERMAK_MAPPING_REF)

    hv9 = find_record(root, HV009_ID)
    hv10 = find_record(root, HV010_ID)
    tr13 = find_record(root, TR013_ID)

    if hv9.get("schemeDesignations") != ["T12", "PV1"]:
        raise SystemExit(f"Unexpected {HV009_ID} scheme: {hv9.get('schemeDesignations')!r}")
    if hv10.get("schemeDesignations") != ["PJ1"]:
        raise SystemExit(f"Unexpected {HV010_ID} scheme: {hv10.get('schemeDesignations')!r}")
    if hv9.get("parameters") or hv10.get("parameters"):
        raise SystemExit("HV-009 or HV-010 already has parameters; review concurrent changes before enriching")
    if hv10.get("modelNames"):
        raise SystemExit(f"HV-010 acquired a model name concurrently: {hv10.get('modelNames')!r}")
    if tr13.get("parameters") or tr13.get("modelNames") or tr13.get("schemeDesignations"):
        raise SystemExit("TR-013 state changed; stop before applying metering package")

    hv9["modelNames"] = ["Тр-19", "вольтметр сети"]
    hv9["purpose"] = (
        "Преобразование напряжения цепи собственных нужд трансформатором T12 (Тр-19) для контроля напряжения "
        "контактной сети вольтметром PV1 и питания связанных измерительно-защитных цепей."
    )
    hv9["parameters"] = HV009_PARAMETERS
    hv9["sourceRefs"] = unique_refs(hv9.get("sourceRefs", []) + [TR19_FACTORY_REF, TR19_ERMAK_MAPPING_REF])
    hv9["parameterCoverage"] = {"status": "documented", "count": len(HV009_PARAMETERS)}
    hv9_notes = [n for n in hv9.get("notes", []) if not n.startswith("T12:") and not n.startswith("Тр-19:") and not n.startswith("PV1:")]
    hv9_notes += [
        "T12: в схеме 2ЭС5К/3ЭС5К получает питание от обмотки собственных нужд тягового трансформатора и питает цепи PV1, PJ1 и вентиля защиты через панель U21.",
        "Тр-19: точное соответствие T12↔Тр-19 подтверждается материалом по оборудованию Ермак; паспортные значения дополнительно взяты из заводского руководства другого электровоза для того же типа Тр-19 и потому должны сверяться по маркировке конкретного аппарата при расхождении исполнения.",
        "PV1: является кабиным прибором индикации; наличие T12 на секции не следует трактовать как наличие отдельного PV1 в секции без кабины управления.",
    ]
    hv9["notes"] = hv9_notes

    hv10["purpose"] = "Учёт потреблённой из контактной сети и возвращённой при рекуперации электроэнергии по измерительным каналам T7 и T12."
    hv10["parameters"] = HV010_PARAMETERS
    hv10["parameterCoverage"] = {
        "status": "documented",
        "count": len(HV010_PARAMETERS),
        "reason": "Документированы функциональные измерительные интерфейсы PJ1; точный тип/модель счётчика в доступном заводском РЭ Ермак не указан.",
    }
    hv10_notes = [n for n in hv10.get("notes", []) if not n.startswith("PJ1:")]
    hv10_notes += [
        "PJ1: токовый сигнал для учёта получает от трансформатора тока T7, а напряженческий канал связан со вторичной цепью T12 через панель U21.",
        "Точная модель и паспортные электрические характеристики самого счётчика PJ1 в использованной документации 2ЭС5К/3ЭС5К не идентифицированы; параметры счётчиков других серий электровозов сюда не переносить.",
        "Для карточки PJ1 приведены только подтверждённые интерфейсные характеристики, а не неподтверждённый паспорт прибора.",
    ]
    hv10["notes"] = hv10_notes

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    hv9 = find_article(root, HV009_ID, HV009_ARTICLE_ID)
    hv10 = find_article(root, HV010_ID, HV010_ARTICLE_ID)

    hv9["summary"] = (
        "Канал T12/PV1 использует трансформатор Тр-19 для формирования низковольтного сигнала и питания цепей, "
        "связанных с контролем напряжения контактной сети; PV1 отображает напряжение в кабине машиниста."
    )
    hv9["principle"] = (
        "Первичная обмотка T12 (Тр-19) питается от обмотки собственных нужд тягового трансформатора. "
        "Его вторичная обмотка формирует уровни, используемые панелью U21, вольтметром PV1, счётчиком PJ1 и вентилем защиты. "
        "PV1 тем самым получает гальванически отделённый измерительный сигнал вместо прямого подключения к цепи 25 кВ."
    )
    hv9["keyParameters"] = kb_parameters(
        HV009_PARAMETERS,
        "Трансформатор Тр-19 в функции T12 базового 2ЭС5К/3ЭС5К. Численные паспортные значения взяты из заводского РЭ того же типа Тр-19 на ЭП1М/ЭП1П; при ремонте сверять исполнение по маркировке аппарата.",
    )
    hv9["normalState"] = [
        "T12 и его выводы закреплены, изоляция и соединения без повреждений, следов перегрева и загрязнения, способного ухудшить изоляцию.",
        "Вторичные цепи T12 и панели U21 исправны; PV1 в кабине показывает правдоподобное напряжение контактной сети без провалов и скачков, не соответствующих режиму.",
        "Питание связанных цепей PJ1 и вентиля защиты от вторичной цепи T12 сохраняется в предусмотренных схемой режимах.",
        "Цепь PV1 не создаёт признаков обрыва или короткого замыкания во вторичной цепи T12."
    ]
    hv9["deviationSigns"] = [
        "PV1 не показывает напряжение при наличии штатного питания T12 либо показание явно не соответствует состоянию контактной сети.",
        "Одновременно нарушается работа нескольких потребителей вторичной цепи T12/U21, что указывает на необходимость проверки общего канала питания, а не только PV1.",
        "На T12 заметны нагрев, повреждение изоляции, ослабление крепления или дефекты выводов и проводников.",
        "Показание PV1 нестабильно при устойчивом режиме; требуется проверка T12, U21, проводки и самого прибора без преждевременного назначения виновного элемента."
    ]
    refs = hv9.setdefault("sourceRefs", [])
    for source_id in [SCHEME_SOURCE_ID, RE4_SOURCE_ID, TR19_FACTORY_SOURCE_ID, TR19_ERMAK_MAPPING_SOURCE_ID]:
        if source_id not in refs:
            refs.append(source_id)
    rules = [r for r in hv9.get("variantRules", []) if not r.startswith("T12/Тр-19:")]
    rules.append(
        "T12/Тр-19: численные характеристики относятся к типу Тр-19 и подтверждены заводским РЭ того же аппарата на ЭП1М/ЭП1П; "
        "для конкретной секции Ермак при расхождении исполнения приоритет имеет маркировка и её документация. PV1 является кабиным прибором, "
        "поэтому его фактическое наличие зависит от типа секции/кабины."
    )
    hv9["variantRules"] = rules
    hv9.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    hv9.setdefault("atlasData", {})["modelNames"] = ["Тр-19", "вольтметр сети"]
    hv9["atlasData"]["parameterCoverage"] = {"status": "documented", "count": len(HV009_PARAMETERS)}

    hv10["summary"] = (
        "PJ1 учитывает электроэнергию в обоих направлениях: потреблённую электровозом и возвращённую в сеть при рекуперации. "
        "Токовый измерительный сигнал поступает от T7, напряженческий — из цепи T12/U21."
    )
    hv10["principle"] = (
        "Трансформатор тока T7 формирует токовый измерительный канал счётчика, а вторичная цепь T12 через панель U21 — его напряженческий канал. "
        "По этим двум входам PJ1 ведёт учёт потреблённой и рекуперированной электроэнергии. Точный тип счётчика в доступном заводском РЭ "
        "2ЭС5К/3ЭС5К не указан, поэтому паспортные значения конкретной модели в атлас не подставляются."
    )
    hv10["keyParameters"] = kb_parameters(
        HV010_PARAMETERS,
        "Функциональные интерфейсы PJ1 базового 2ЭС5К/3ЭС5К; это подтверждённые связи схемы, а не паспорт неизвестной модели счётчика.",
    )
    hv10["normalState"] = [
        "PJ1 ведёт учёт как потреблённой, так и рекуперированной электроэнергии в соответствующих режимах электровоза.",
        "Токовый канал от T7 и напряженческий канал от T12/U21 электрически исправны и согласованно участвуют в измерении.",
        "Питание и соединения счётчика надёжны; нет следов перегрева, повреждения разъёмов или проводки.",
        "Изменение показаний/накопленной энергии соответствует фактическому режиму тяги или рекуперации без очевидно невозможных скачков."
    ]
    hv10["deviationSigns"] = [
        "Учёт не изменяется при длительном подтверждённом потреблении или рекуперации, либо изменяется явно несогласованно с режимом.",
        "Отсутствует один из измерительных входов — токовый от T7 или напряженческий от T12/U21; это требует проверки всей соответствующей цепи.",
        "Есть повреждение питания, проводки или соединений PJ1, следы перегрева или нестабильный контакт.",
        "Неверный учёт не следует автоматически приписывать самому счётчику: до замены прибора проверяют T7, T12/U21 и соединительные цепи."
    ]
    refs = hv10.setdefault("sourceRefs", [])
    if SCHEME_SOURCE_ID not in refs:
        refs.append(SCHEME_SOURCE_ID)
    rules = [r for r in hv10.get("variantRules", []) if not r.startswith("PJ1:")]
    rules.append(
        "PJ1: точный тип/модель счётчика в использованном заводском РЭ 2ЭС5К/3ЭС5К не установлен. Не переносить паспортные параметры "
        "счётчиков с других серий электровозов без документального подтверждения конкретного исполнения Ермак."
    )
    hv10["variantRules"] = rules
    hv10.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    hv10.setdefault("atlasData", {})["parameterCoverage"] = {
        "status": "documented",
        "count": len(HV010_PARAMETERS),
        "reason": "Подтверждены интерфейсные характеристики PJ1; модель счётчика не идентифицирована.",
    }

    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / "ermak_equipment.json.gz")
    patch_knowledge(base / "ermak_knowledge.json.gz")

print("Ermak HV-009 network voltage channel and HV-010 energy metering reference enriched in app and patch mirrors")
