#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
EQUIPMENT_ID = "ER-EQ-TR-006"
ARTICLE_ID = "ER-KB-EQ-ER-EQ-TR-006"
NEIGHBOR_ID = "ER-EQ-TR-007"

SCHEME_SOURCE_ID = "ER-SRC-062"
RE4_SOURCE_ID = "ER-SRC-063"
MAINT_SOURCE_ID = "ER-SRC-064"
TECH_SOURCE_ID = "ER-SRC-065"
VARIANT_SOURCE_ID = "ER-SRC-066"

SCHEME_REF = {
    "sourceId": SCHEME_SOURCE_ID,
    "document": "ИДМБ.661142.009РЭ1, электровоз магистральный 2ЭС5К (3ЭС5К)",
    "title": "Электрические схемы — назначение реверсора QP1",
    "url": "https://www.rcit.su/techinfoV51.html",
    "locator": "раздел 4 «Схема силовых цепей»; описание QP1",
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
        "ПКД-01 в функции реверсора QP1 базового исполнения 2ЭС5К/3ЭС5К. "
        "Не переносить автоматически на тягово-тормозной переключатель QT1 или на более поздний ПКД-142; "
        "фактический тип сверять по маркировке и документации секции."
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
    register_source(registry, "PKD01_QP1_SCHEME", SCHEME_REF)
    register_source(registry, "PKD01_ERMAK_RE4", RE4_REF)
    register_source(registry, "PKD01_ERMAK_MAINTENANCE", MAINT_REF)
    register_source(registry, "PKD01_TECHNICAL_DATA", TECH_REF)
    register_source(registry, "PKD142_ERMAK_VARIANT", VARIANT_REF)

    matches = [r for r in root["records"] if r.get("id") == EQUIPMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one {EQUIPMENT_ID} record, found {len(matches)}")
    record = matches[0]
    if "ПКД-01" not in record.get("modelNames", []):
        raise SystemExit(f"Unexpected modelNames for {EQUIPMENT_ID}: {record.get('modelNames')!r}")

    neighbors = [r for r in root["records"] if r.get("id") == NEIGHBOR_ID]
    if len(neighbors) != 1 or "ПКД-01" not in neighbors[0].get("modelNames", []) or "QT1" not in neighbors[0].get("schemeDesignations", []):
        raise SystemExit("Neighbor TR-007 is not the expected separate PKD-01 / QT1 card")
    if neighbors[0].get("parameters"):
        raise SystemExit("Neighbor TR-007 already has parameters; review before enriching TR-006")

    record["schemeDesignations"] = ["QP1"]
    record["purpose"] = (
        "Изменение направления тока в обмотках возбуждения тяговых двигателей для изменения направления "
        "вращения ТЭД и направления движения электровоза. Переключение выполняется при разгруженной тяговой цепи."
    )
    record["parameters"] = PARAMETERS
    record["sourceRefs"] = unique_refs(record.get("sourceRefs", []) + [SCHEME_REF, RE4_REF, MAINT_REF, TECH_REF, VARIANT_REF])
    record["parameterCoverage"] = {"status": "documented", "count": len(PARAMETERS)}

    notes = [
        n for n in record.get("notes", [])
        if not n.startswith("ПКД-01:") and not n.startswith("QP1:") and not n.startswith("ПКД-142:")
    ]
    notes += [
        "QP1: реверсор меняет направление тока в обмотках возбуждения ТЭД; функционально не объединять с тягово-тормозным переключателем QT1, хотя в базовом исполнении применяется тот же тип ПКД-01.",
        "ПКД-01: групповой двухпозиционный кулачковый аппарат с кулачковым валом, элементами КЭ-01, пневматическим приводом двустороннего действия и узлом вспомогательных контактов; кулачковые элементы выполнены без дугогашения.",
        "При ремонте падение напряжения непосредственно между накладками замкнутых главных контактов допускается не более 7 мВ при токе 300 А.",
        "При сборке расстояние от боковины до шестерни кулачкового вала должно быть 8–10 мм; свисание шестерни блокировки с шестерни кулачкового вала не допускается.",
        "ПКД-142: встречается в более поздних комплектах документации семейства Ермак; паспортные данные ПКД-01 на ПКД-142 автоматически не переносить.",
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
        "ПКД-01 в позиции QP1 выполняет реверсирование тяговых двигателей: изменяет направление тока "
        "в их обмотках возбуждения и тем самым направление движения электровоза."
    )
    article["principle"] = (
        "Пневматический привод двустороннего действия поворачивает кулачковый вал между двумя фиксированными положениями. "
        "Профиль кулачковых шайб управляет главными и вспомогательными контактами КЭ-01, перекоммутируя выводы обмоток "
        "возбуждения ТЭД. Рабочее реверсирование выполняют при разгруженной тяговой цепи, поэтому кулачковые элементы "
        "ПКД-01 выполнены без дугогасительных камер."
    )
    article["keyParameters"] = to_kb_parameters(PARAMETERS)
    article["normalState"] = [
        "Главные и вспомогательные контакты, контактные пружины, кулачковые элементы и пневматический привод исправны; аппарат чётко занимает оба фиксированных положения.",
        "Падение напряжения непосредственно между накладками замкнутых главных контактов не превышает 7 мВ при токе 300 А.",
        "Расстояние от боковины до шестерни кулачкового вала находится в пределах 8–10 мм; шестерня блокировки не свисает с шестерни кулачкового вала.",
        "Метки «Б», «В», «Г» и «Д» на шестернях совмещены при сборке; диаграмма коммутационных положений соответствует документации.",
    ]
    article["deviationSigns"] = [
        "Падение напряжения между накладками главных контактов превышает 7 мВ при токе 300 А, имеются следы перегрева, подгара или ненормального износа контактов.",
        "Расстояние от боковины до шестерни кулачкового вала выходит за пределы 8–10 мм, имеется свисание шестерни блокировки или ненормальный осевой люфт вала.",
        "Метки шестерён не совмещены либо фактическая диаграмма коммутационных положений не соответствует требуемой.",
        "Кулачковый механизм, вспомогательные контакты или пневмопривод не обеспечивают полного и чёткого перевода аппарата между положениями.",
    ]

    refs = article.setdefault("sourceRefs", [])
    for ref in [SCHEME_SOURCE_ID, RE4_SOURCE_ID, MAINT_SOURCE_ID, TECH_SOURCE_ID, VARIANT_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)

    rules = [r for r in article.get("variantRules", []) if not r.startswith("ПКД-01:")]
    rules.append(
        "ПКД-01: эта функциональная карточка относится к реверсору QP1. Тот же тип аппарата используется отдельно как "
        "тягово-тормозной переключатель QT1; назначение и эксплуатационные записи этих функций не объединять. "
        "В более поздних комплектах документации семейства Ермак встречается ПКД-142; его паспортные данные не смешивать "
        "с ПКД-01 без сверки маркировки и документации конкретной секции."
    )
    article["variantRules"] = rules
    article.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    article.setdefault("atlasData", {})["parameterCoverage"] = {"status": "documented", "count": len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / "ermak_equipment.json.gz")
    patch_knowledge(base / "ermak_knowledge.json.gz")

print("Ermak PKD-01 QP1 reverser reference enriched in app and patch mirrors")
