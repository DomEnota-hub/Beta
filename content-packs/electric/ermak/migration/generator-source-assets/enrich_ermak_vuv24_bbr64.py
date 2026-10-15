#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
VUV_ID = "ER-EQ-TR-008"
VUV_ARTICLE_ID = "ER-KB-EQ-ER-EQ-TR-008"
BBR_ID = "ER-EQ-TR-010"
BBR_ARTICLE_ID = "ER-KB-EQ-ER-EQ-TR-010"
NEIGHBOR_ID = "ER-EQ-TR-009"

SCHEME_SOURCE_ID = "ER-SRC-002"
RE4_SOURCE_ID = "ER-SRC-005"
RE5_SOURCE_ID = "ER-SRC-006"
VUV_TECH_SOURCE_ID = "ER-SRC-068"
VUV_VARIANT_SOURCE_ID = "ER-SRC-069"
BBR_TECH_SOURCE_ID = "ER-SRC-070"
BBR_VARIANT_SOURCE_ID = "ER-SRC-071"
MAINT_SOURCE_ID = "ER-SRC-072"

VUV_TECH_REF = {
    "sourceId": VUV_TECH_SOURCE_ID,
    "document": "Каталог электротехнического оборудования",
    "title": "ВУВ-24 ДТЖИ.656152.014 (6ТС.360.024СП) — назначение, устройство и технические характеристики",
    "url": "https://electro.mashinform.ru/ehlektrooborudovanie-ehlektrovozov/blok-vyprjamitelnoj-ustanovki-vozbuzhdenija-vuv-24-obj3521.html",
    "locator": "карточка «Блок выпрямительной установки возбуждения ВУВ-24»",
}
VUV_VARIANT_REF = {
    "sourceId": VUV_VARIANT_SOURCE_ID,
    "document": "ФБУ «РС ФЖТ»: сертификационные испытания блоков выпрямительной установки возбуждения",
    "title": "Семейство ВУВ-24: исполнения ВУВ-24 и ВУВ-24-01",
    "url": "https://rsfgt.ru/LotPage/1723630",
    "locator": "техническое задание: ДТЖИ.656152.014 и ДТЖИ.656152.014-01",
}
BBR_TECH_REF = {
    "sourceId": BBR_TECH_SOURCE_ID,
    "document": "Учебно-техническое описание электрооборудования электровоза",
    "title": "Блок балластных резисторов ББР-64 — технические характеристики и конструкция",
    "url": "https://studopedia.net/20_24286_naznachenie-apparatov-raspolozhennih-na-blokah-i-panelyah.html",
    "locator": "раздел «Блок балластных резисторов ББР-64»",
}
BBR_VARIANT_REF = {
    "sourceId": BBR_VARIANT_SOURCE_ID,
    "document": "ФБУ «РС ФЖТ»: реестр сертификатов и деклараций",
    "title": "ББР-64 и ББР-64-01 — исполнения конструкторской документации 6ТС.277.064",
    "url": "https://rsfgt.ru/Certificates/24302",
    "locator": "объект сертификации: 6ТС.277.064, исполнения 6ТС.277.064 и 6ТС.277.064-01",
}
MAINT_REF = {
    "sourceId": MAINT_SOURCE_ID,
    "document": "ИДМБ.661142.009РЭ8, электровоз магистральный 2ЭС5К (3ЭС5К)",
    "title": "Техническое обслуживание и текущий ремонт электронного оборудования, резисторов и системы вентиляции",
    "url": "https://rcit.su/techinfoV58.html",
    "locator": "пп. 4.5.8, 6.5.6, 8.4.25, 8.5.5 и проверка производительности вентиляции",
}

VUV_PARAMETERS = [
    {"name": "Номинальный продолжительный выпрямительный ток", "value": 850, "unit": "A", "sourceId": VUV_TECH_SOURCE_ID},
    {"name": "Выпрямительный ток 20-минутного режима", "value": 1100, "unit": "A", "sourceId": VUV_TECH_SOURCE_ID},
    {"name": "Номинальное напряжение питания", "value": "2×270", "unit": "V", "sourceId": VUV_TECH_SOURCE_ID},
    {"name": "Допустимый диапазон напряжения питания", "value": "100–330", "unit": "V", "sourceId": VUV_TECH_SOURCE_ID},
    {"name": "Номинальное напряжение цепей управления", "value": 50, "unit": "V", "sourceId": VUV_TECH_SOURCE_ID},
    {"name": "Расход охлаждающего воздуха, не менее", "value": 10, "unit": "m3/min", "sourceId": VUV_TECH_SOURCE_ID},
    {"name": "Масса", "value": 147, "unit": "kg", "sourceId": VUV_TECH_SOURCE_ID},
]

BBR_PARAMETERS = [
    {"name": "Сопротивление секций 1-2; 5-6; 9-10; 13-14 при 20 °C", "value": "0.0715 ±0.0036", "unit": "Ohm", "sourceId": BBR_TECH_SOURCE_ID},
    {"name": "Сопротивление секций 1-3; 5-7; 9-11; 13-15 при 20 °C", "value": "0.1144 ±0.0057", "unit": "Ohm", "sourceId": BBR_TECH_SOURCE_ID},
    {"name": "Сопротивление секций 1-4; 5-8; 9-12; 13-16 при 20 °C", "value": "0.143 ±0.007", "unit": "Ohm", "sourceId": BBR_TECH_SOURCE_ID},
    {"name": "Номинальный ток", "value": 1000, "unit": "A", "sourceId": BBR_TECH_SOURCE_ID},
    {"name": "Номинальное напряжение изоляции", "value": 2000, "unit": "V", "sourceId": BBR_TECH_SOURCE_ID},
    {"name": "Охлаждение", "value": "воздушное принудительное", "unit": "", "sourceId": BBR_TECH_SOURCE_ID},
    {"name": "Расход охлаждающего воздуха на входе, не менее", "value": 250, "unit": "m3/min", "sourceId": BBR_TECH_SOURCE_ID},
    {"name": "Превышение температуры охлаждающего воздуха на выходе, не более", "value": 125, "unit": "°C", "sourceId": BBR_TECH_SOURCE_ID},
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
    register_source(registry, "VUV24_TECHNICAL_DATA", VUV_TECH_REF)
    register_source(registry, "VUV24_EXECUTION_FAMILY", VUV_VARIANT_REF)
    register_source(registry, "BBR64_TECHNICAL_DATA", BBR_TECH_REF)
    register_source(registry, "BBR64_EXECUTION_FAMILY", BBR_VARIANT_REF)
    register_source(registry, "TR_EQUIPMENT_MAINTENANCE", MAINT_REF)

    vuv = find_record(root, VUV_ID)
    bbr = find_record(root, BBR_ID)
    neighbor = find_record(root, NEIGHBOR_ID)

    if vuv.get("modelNames") != ["ВУВ-24"] or vuv.get("schemeDesignations") != ["U3"]:
        raise SystemExit(f"Unexpected {VUV_ID} identity: {vuv.get('modelNames')!r} / {vuv.get('schemeDesignations')!r}")
    if bbr.get("modelNames") != ["ББР-64"] or bbr.get("schemeDesignations") != ["R10"]:
        raise SystemExit(f"Unexpected {BBR_ID} identity: {bbr.get('modelNames')!r} / {bbr.get('schemeDesignations')!r}")
    if vuv.get("parameters") or bbr.get("parameters"):
        raise SystemExit("TR-008 or TR-010 already has parameters; review concurrent changes before enriching")
    if len(neighbor.get("parameters", [])) != 5 or "РОВ-21" not in neighbor.get("modelNames", []) or "ИШ-95" not in neighbor.get("modelNames", []):
        raise SystemExit("TR-009 state changed; stop before applying the two-node package")

    vuv["purpose"] = "Выпрямление и плавное регулирование тока в обмотках возбуждения тяговых двигателей при электрическом (рекуперативном) торможении."
    vuv["parameters"] = VUV_PARAMETERS
    vuv["sourceRefs"] = unique_refs(vuv.get("sourceRefs", []) + [VUV_TECH_REF, VUV_VARIANT_REF, MAINT_REF])
    vuv["parameterCoverage"] = {"status": "documented", "count": len(VUV_PARAMETERS)}
    vuv_notes = [n for n in vuv.get("notes", []) if not n.startswith("ВУВ-24:") and not n.startswith("ВУВ-24-01:")]
    vuv_notes += [
        "ВУВ-24: управляемый тиристорный выпрямитель; силовые тиристоры установлены на охладителях в воздушном тракте, а цепи управления питаются напряжением 50 В.",
        "При ТО контролируют состояние монтажа, предохранителей F1–F6 и фиксацию движков переменных резисторов R1/R2; работоспособность проверяют по току возбуждения.",
        "ВУВ-24-01: документировано отдельное исполнение семейства ВУВ-24 (ДТЖИ.656152.014-01 / 6ТС.360.024-01СП); паспортные данные базового ВУВ-24 не переносить автоматически без сверки маркировки и документации.",
    ]
    vuv["notes"] = vuv_notes

    bbr["purpose"] = "Повышение электрической устойчивости рекуперативного торможения и улучшение распределения тока между параллельно включёнными якорями тяговых двигателей."
    bbr["parameters"] = BBR_PARAMETERS
    bbr["sourceRefs"] = unique_refs(bbr.get("sourceRefs", []) + [BBR_TECH_REF, BBR_VARIANT_REF, MAINT_REF])
    bbr["parameterCoverage"] = {"status": "documented", "count": len(BBR_PARAMETERS)}
    bbr_notes = [n for n in bbr.get("notes", []) if not n.startswith("ББР-64:") and not n.startswith("ББР-64-01:")]
    bbr_notes += [
        "ББР-64: ленточные резистивные элементы собраны пакетами на изолированных шпильках в жёстком металлическом каркасе; рамки элементов формируют каналы принудительного охлаждения.",
        "В силовой схеме R10 работает в режиме рекуперативного торможения; охлаждение обеспечивается отдельным вентилятором, и блок должен эксплуатироваться только при штатном принудительном обдуве.",
        "ББР-64-01: отдельное документированное исполнение 6ТС.277.064-01; параметры базового ББР-64 не считать универсальными для исполнения -01 без сверки маркировки и документации.",
        "Масса в открытом учебном источнике приведена как 2678 кг и выглядит как ошибка/искажение исходного значения; без независимого подтверждения масса сознательно не включена в паспортные параметры.",
    ]
    bbr["notes"] = bbr_notes

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    vuv = find_article(root, VUV_ID, VUV_ARTICLE_ID)
    bbr = find_article(root, BBR_ID, BBR_ARTICLE_ID)

    vuv["summary"] = "ВУВ-24 (U3) выпрямляет и плавно регулирует ток независимого возбуждения тяговых двигателей при электрическом торможении."
    vuv["principle"] = (
        "ВУВ-24 представляет собой управляемый тиристорный выпрямитель. Изменением управляющих импульсов силовых тиристоров "
        "установка регулирует выпрямленный ток в обмотках возбуждения тяговых двигателей, тем самым участвуя в регулировании "
        "рекуперативного торможения. Параллельные силовые ветви используют элементы выравнивания тока, а потери тиристоров "
        "отводятся принудительным воздушным охлаждением."
    )
    vuv["keyParameters"] = kb_parameters(
        VUV_PARAMETERS,
        "ВУВ-24 базового исполнения 2ЭС5К/3ЭС5К; для ВУВ-24-01 фактические паспортные значения сверять по маркировке и документации исполнения.",
    )
    vuv["normalState"] = [
        "Электрический монтаж, шины, контактные соединения и изоляционные элементы визуально исправны, без следов перегрева и повреждений.",
        "Предохранители F1–F6 исправны, движки переменных резисторов R1 и R2 надёжно зафиксированы.",
        "Охладители силовых тиристоров и воздушный тракт чисты; обеспечивается требуемый принудительный расход охлаждающего воздуха не менее 10 м³/мин.",
        "При проверке электрического торможения ток возбуждения формируется и регулируется без нештатных срывов."
    ]
    vuv["deviationSigns"] = [
        "Перегоревшие предохранители F1–F6, ослабление фиксации R1/R2, повреждение монтажа, шин или контактных соединений.",
        "Загрязнение охладителей либо недостаточный воздушный поток, сопровождающийся перегревом силовых тиристоров и элементов блока.",
        "Отсутствие, нестабильность или ненормальное регулирование тока возбуждения при попытке собрать электрическое торможение.",
        "Повреждение изоляции, следы пробоя, перегрева или механического повреждения элементов тиристорного блока."
    ]
    vuv_refs = vuv.setdefault("sourceRefs", [])
    for ref in [SCHEME_SOURCE_ID, RE5_SOURCE_ID, VUV_TECH_SOURCE_ID, VUV_VARIANT_SOURCE_ID, MAINT_SOURCE_ID]:
        if ref not in vuv_refs:
            vuv_refs.append(ref)
    vuv_rules = [r for r in vuv.get("variantRules", []) if not r.startswith("ВУВ-24:")]
    vuv_rules.append(
        "ВУВ-24: базовая карточка относится к ДТЖИ.656152.014 (6ТС.360.024СП). Исполнение ВУВ-24-01 "
        "ДТЖИ.656152.014-01 (6ТС.360.024-01СП) документировано отдельно; не смешивать паспортные данные двух исполнений без сверки маркировки."
    )
    vuv["variantRules"] = vuv_rules
    vuv.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    vuv.setdefault("atlasData", {})["parameterCoverage"] = {"status": "documented", "count": len(VUV_PARAMETERS)}

    bbr["summary"] = "ББР-64 (R10) стабилизирует режим рекуперативного торможения и улучшает распределение тока между параллельными цепями якорей тяговых двигателей."
    bbr["principle"] = (
        "При рекуперативном торможении блок R10 включён в соответствующие силовые ветви тяговых двигателей. Секции сопротивления "
        "создают заданное активное сопротивление, повышая устойчивость электрического торможения и выравнивая распределение тока "
        "между параллельными якорными цепями. Электрическая энергия рассеивается в виде тепла, которое удаляется обязательным "
        "принудительным воздушным охлаждением."
    )
    bbr["keyParameters"] = kb_parameters(
        BBR_PARAMETERS,
        "ББР-64 базового исполнения 6ТС.277.064 на 2ЭС5К/3ЭС5К; для ББР-64-01 параметры сверять по маркировке и документации исполнения.",
    )
    bbr["normalState"] = [
        "Ленточные резистивные элементы, рамки, фарфоровые изоляторы и изолированные стяжные шпильки целы, без деформации, пробоя и следов перегрева.",
        "Выводы, токоведущие шины, гибкие шунты и крепёжные соединения надёжны, без ослабления и местного перегрева.",
        "Воздушный канал свободен; принудительный обдув блока обеспечивается с расходом не менее 250 м³/мин на входе.",
        "Изоляционная стенка и уплотнение выводов не имеют повреждений, способных вызвать утечку горячего воздуха в кузов."
    ]
    bbr["deviationSigns"] = [
        "Обрыв, трещины, прожог или деформация резистивных элементов, повреждение изоляторов либо выраженные следы перегрева.",
        "Ослабление выводов, шин, гибких шунтов или крепежа, а также следы местного перегрева контактных соединений.",
        "Перекрытие воздушного канала, отказ вентилятора или расход охлаждающего воздуха ниже требуемого, вызывающий перегрев блока.",
        "Нестабильность рекуперативного торможения или заметное нарушение распределения токов между параллельными якорными цепями; признак требует дальнейшей диагностики и сам по себе не доказывает неисправность ББР."
    ]
    bbr_refs = bbr.setdefault("sourceRefs", [])
    for ref in [SCHEME_SOURCE_ID, RE4_SOURCE_ID, BBR_TECH_SOURCE_ID, BBR_VARIANT_SOURCE_ID, MAINT_SOURCE_ID]:
        if ref not in bbr_refs:
            bbr_refs.append(ref)
    bbr_rules = [r for r in bbr.get("variantRules", []) if not r.startswith("ББР-64:")]
    bbr_rules.append(
        "ББР-64: базовая карточка относится к исполнению 6ТС.277.064. ББР-64-01 / 6ТС.277.064-01 является отдельным "
        "документированным исполнением; его паспортные значения не переносить на базовый ББР-64 и наоборот без проверки маркировки."
    )
    bbr["variantRules"] = bbr_rules
    bbr.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    bbr.setdefault("atlasData", {})["parameterCoverage"] = {"status": "documented", "count": len(BBR_PARAMETERS)}

    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / "ermak_equipment.json.gz")
    patch_knowledge(base / "ermak_knowledge.json.gz")

print("Ermak VUV-24 and BBR-64 traction reference package enriched in app and patch mirrors")
