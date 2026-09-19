#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
EQUIPMENT_ID = "ER-EQ-TR-007"
ARTICLE_ID = "ER-KB-EQ-ER-EQ-TR-007"
PREVIOUS_ID = "ER-EQ-TR-006"
NEXT_ID = "ER-EQ-TR-008"

SCHEME_SOURCE_ID = "ER-SRC-067"
RE4_SOURCE_ID = "ER-SRC-063"
MAINT_SOURCE_ID = "ER-SRC-064"
TECH_SOURCE_ID = "ER-SRC-065"
VARIANT_SOURCE_ID = "ER-SRC-066"

SCHEME_REF = {
    "sourceId": SCHEME_SOURCE_ID,
    "document": "ИДМБ.661142.009РЭ1, электровоз магистральный 2ЭС5К (3ЭС5К)",
    "title": "Электрические схемы — назначение тягово-тормозного переключателя QT1",
    "url": "https://www.rcit.su/techinfoV51.html",
    "locator": "раздел 4.4 «Цепи тяговых двигателей в режиме рекуперативного торможения»; описание QT1",
}
RE4_REF = {
    "sourceId": RE4_SOURCE_ID,
    "document": "ИДМБ.661142.009РЭ4, электровоз магистральный 2ЭС5К (3ЭС5К)",
    "title": "Переключатель кулачковый двухпозиционный ПКД-01",
    "url": "https://rcit.su/techinfoV54.html",
    "locator": "раздел 5 «Переключатель кулачковый двухпозиционный ПКД-01»",
}
MAINT_REF = {
    "sourceId": MAINT_SOURCE_ID,
    "document": "ИДМБ.661142.009РЭ8, электровоз магистральный 2ЭС5К (3ЭС5К)",
    "title": "ПКД-01 — техническое обслуживание и текущий ремонт",
    "url": "https://rcit.su/techinfoV58.html",
    "locator": "п. 8.4.14 «Переключатель двухпозиционный ПКД-01»",
}
TECH_REF = {
    "sourceId": TECH_SOURCE_ID,
    "document": "Учебно-техническое описание электрических аппаратов электровоза",
    "title": "ПКД-01 — технические характеристики, устройство и работа",
    "url": "https://studopedia.net/20_24286_naznachenie-apparatov-raspolozhennih-na-blokah-i-panelyah.html",
    "locator": "раздел «Переключатель кулачковый двухпозиционный ПКД-01»",
}
VARIANT_REF = {
    "sourceId": VARIANT_SOURCE_ID,
    "document": "Каталог КрИЖТ ИрГУПС: руководство по эксплуатации 2ЭС5К (3ЭС5К, 4ЭС5К), книга 4",
    "title": "Позднее исполнение переключателя ПКД-142 в документации Ермак",
    "url": "https://irbis.krsk.irgups.ru/web/index.php?C21COM=S&I21DBN=IBIS&LNG=&P21DBN=IBIS&S21ALL=%28%3C.%3EK%3D%D0%A0%D0%95%D0%97%D0%98%D0%A1%D0%A2%D0%9E%D0%A0%3C.%3E%29&S21CNR=20&S21FMT=fullwebr&S21REF=&S21SRD=&S21SRW=AVHEAD&S21STN=1&Z21ID=",
    "locator": "содержание книги 4: «Переключатель кулачковый двухпозиционный ПКД-142», с. 15",
}

PARAMETERS = [
    {"name": "Номинальное напряжение главной цепи", "value": 3000, "unit": "V", "sourceId": TECH_SOURCE_ID},
    {"name": "Номинальный ток главной цепи", "value": 1100, "unit": "A", "sourceId": TECH_SOURCE_ID},
    {"name": "Номинальное напряжение вспомогательной цепи", "value": 50, "unit": "V", "sourceId": TECH_SOURCE_ID},
    {"name": "Номинальный ток контактов вспомогательной цепи", "value": 16, "unit": "A", "sourceId": TECH_SOURCE_ID},
    {"name": "Номинальное напряжение цепи управления", "value": 50, "unit": "V", "sourceId": TECH_SOURCE_ID},
    {"name": "Номинальное давление сжатого воздуха привода", "value": 0.5, "unit": "MPa", "sourceId": TECH_SOURCE_ID},
    {"name": "Масса", "value": 72.5, "unit": "kg", "sourceId": TECH_SOURCE_ID},
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


def to_kb_parameters(items):
    applicability = (
        "ПКД-01 в функции тягово-тормозного переключателя QT1 базового исполнения 2ЭС5К/3ЭС5К. "
        "Паспортные значения относятся к типу ПКД-01; функционально не объединять с реверсором QP1. "
        "Для исполнений с ПКД-142 фактический тип и паспорт сверять по маркировке и документации секции."
    )
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
    register_source(registry, "PKD01_QT1_SCHEME", SCHEME_REF)
    register_source(registry, "PKD01_ERMAK_RE4", RE4_REF)
    register_source(registry, "PKD01_ERMAK_MAINTENANCE", MAINT_REF)
    register_source(registry, "PKD01_TECHNICAL_DATA", TECH_REF)
    register_source(registry, "PKD142_ERMAK_VARIANT", VARIANT_REF)

    matches = [r for r in root["records"] if r.get("id") == EQUIPMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one {EQUIPMENT_ID} record, found {len(matches)}")
    record = matches[0]
    if "ПКД-01" not in record.get("modelNames", []) or record.get("schemeDesignations") != ["QT1"]:
        raise SystemExit(f"Unexpected target identity: models={record.get('modelNames')!r}, scheme={record.get('schemeDesignations')!r}")
    if record.get("parameters"):
        raise SystemExit(f"{EQUIPMENT_ID} already has parameters; review before enriching")

    previous = [r for r in root["records"] if r.get("id") == PREVIOUS_ID]
    if len(previous) != 1 or "ПКД-01" not in previous[0].get("modelNames", []) or previous[0].get("schemeDesignations") != ["QP1"]:
        raise SystemExit("Previous TR-006 is not the expected PKD-01 / QP1 card")
    if len(previous[0].get("parameters", [])) != 7:
        raise SystemExit("Previous TR-006 is not yet fully enriched; stop before touching QT1")

    next_rows = [r for r in root["records"] if r.get("id") == NEXT_ID]
    if len(next_rows) != 1 or next_rows[0].get("parameters"):
        raise SystemExit("Neighbor TR-008 state changed; review before enriching TR-007")

    record["schemeDesignations"] = ["QT1"]
    record["purpose"] = (
        "Переключение силовых цепей тяговых двигателей между режимом тяги и рекуперативного торможения. "
        "В положении «Тяга» схема работает в тяговом режиме; при переходе в «Торможение» QT1 перестраивает "
        "силовые цепи и цепи управления для рекуперации."
    )
    record["parameters"] = PARAMETERS
    record["sourceRefs"] = unique_refs(record.get("sourceRefs", []) + [SCHEME_REF, RE4_REF, MAINT_REF, TECH_REF, VARIANT_REF])
    record["parameterCoverage"] = {"status": "documented", "count": len(PARAMETERS)}

    notes = [
        n for n in record.get("notes", [])
        if not n.startswith("QT1:") and not n.startswith("ПКД-01:") and not n.startswith("ПКД-142:")
    ]
    notes += [
        "QT1: отдельная функциональная позиция тягово-тормозного переключателя; не объединять с реверсором QP1, хотя в базовом исполнении обе позиции используют аппарат типа ПКД-01.",
        "При переходе из тяги к рекуперации перевод QT1 разрешается после снятия тяговой нагрузки и выдержки времени на завершение переходных процессов; в РЭ1 цепь управления предусматривает выдержку порядка 2–3 с.",
        "В положении «Торможение» QT1 перестраивает силовые цепи так, чтобы тяговые двигатели работали в генераторном режиме с независимым возбуждением и обеспечивали рекуперативное торможение.",
        "При ремонте падение напряжения непосредственно между накладками замкнутых главных контактов допускается не более 7 мВ при токе 300 А.",
        "При сборке расстояние от боковины до шестерни кулачкового вала должно быть 8–10 мм; свисание шестерни блокировки с шестерни кулачкового вала не допускается.",
        "ПКД-142: встречается в более поздних комплектах документации семейства Ермак; паспортные данные ПКД-01 на ПКД-142 автоматически не переносить."
    ]
    record["notes"] = notes

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    matches = [a for a in root["articles"] if a.get("id") == ARTICLE_ID or a.get("equipmentId") == EQUIPMENT_ID]
    by_id = {a.get("id"): a for a in matches}
    if len(by_id) != 1:
        raise SystemExit(f"Expected exactly one article for {EQUIPMENT_ID}, found {list(by_id)}")
    article = next(iter(by_id.values()))

    article["summary"] = (
        "ПКД-01 в позиции QT1 переводит тяговые цепи между режимами «Тяга» и «Торможение», "
        "подготавливая силовую схему тяговых двигателей к рекуперативному торможению и обратно."
    )
    article["principle"] = (
        "Пневматический привод двустороннего действия поворачивает кулачковый вал ПКД-01 между двумя фиксированными "
        "положениями. В режиме «Тяга» контакты QT1 формируют штатную тяговую конфигурацию. После снятия тяговой нагрузки "
        "и завершения переходных процессов аппарат переводится в положение «Торможение»: силовые и вспомогательные контакты "
        "перекоммутируют цепи тяговых двигателей для рекуперативного режима, в котором двигатели работают как генераторы "
        "с независимым возбуждением."
    )
    article["keyParameters"] = to_kb_parameters(PARAMETERS)
    article["normalState"] = [
        "ПКД-01 чётко занимает оба фиксированных положения «Тяга» и «Торможение»; вспомогательные контакты корректно подтверждают фактическое положение аппарата.",
        "Главные и вспомогательные контакты, контактные пружины, кулачковые элементы и пневматический привод исправны, без следов перегрева и ненормального износа.",
        "Падение напряжения непосредственно между накладками замкнутых главных контактов не превышает 7 мВ при токе 300 А.",
        "Расстояние от боковины до шестерни кулачкового вала находится в пределах 8–10 мм; шестерня блокировки не свисает с шестерни кулачкового вала."
    ]
    article["deviationSigns"] = [
        "QT1 не доходит до положения «Тяга» или «Торможение», переключение неполное либо сигнал вспомогательных контактов не соответствует фактическому положению аппарата.",
        "Падение напряжения между накладками замкнутых главных контактов превышает 7 мВ при токе 300 А, имеются следы перегрева, подгара или ненормального износа контактов.",
        "Расстояние от боковины до шестерни кулачкового вала выходит за пределы 8–10 мм, имеется свисание шестерни блокировки или ненормальный осевой люфт вала.",
        "Наблюдаются механическое заедание кулачкового механизма, неисправность пневмопривода/вентиля управления либо нарушение работы вспомогательных контактов."
    ]

    refs = article.setdefault("sourceRefs", [])
    for ref in [SCHEME_SOURCE_ID, RE4_SOURCE_ID, MAINT_SOURCE_ID, TECH_SOURCE_ID, VARIANT_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)

    rules = [r for r in article.get("variantRules", []) if not r.startswith("ПКД-01:")]
    rules.append(
        "ПКД-01: эта функциональная карточка относится к тягово-тормозному переключателю QT1. Реверсор QP1 является "
        "отдельной позицией с другим назначением, хотя в базовом исполнении применяется тот же тип ПКД-01; эксплуатационные "
        "описания QP1 и QT1 не объединять. В более поздних комплектах документации семейства Ермак встречается ПКД-142; "
        "его паспортные значения не смешивать с ПКД-01 без сверки маркировки и документации конкретной секции."
    )
    article["variantRules"] = rules
    article.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    article.setdefault("atlasData", {})["parameterCoverage"] = {"status": "documented", "count": len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / "ermak_equipment.json.gz")
    patch_knowledge(base / "ermak_knowledge.json.gz")

print("Ermak PKD-01 QT1 traction-brake switch reference enriched in app and patch mirrors")
