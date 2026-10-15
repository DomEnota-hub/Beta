#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
PUMP_ID = "ER-EQ-AU-004"
PUMP_ARTICLE_ID = "ER-KB-EQ-ER-EQ-AU-004"
FAN_ID = "ER-EQ-AU-005"
FAN_ARTICLE_ID = "ER-KB-EQ-ER-EQ-AU-005"

SCHEME_SOURCE_ID = "ER-SRC-002"
RE4_SOURCE_ID = "ER-SRC-005"
BBR_MAINT_SOURCE_ID = "ER-SRC-072"
PUMP_DATA_SOURCE_ID = "ER-SRC-078"
ERMAK_OPERATION_SOURCE_ID = "ER-SRC-079"
ERMAK_NVA55_SOURCE_ID = "ER-SRC-080"
NVA55_TECH_SOURCE_ID = "ER-SRC-081"
NVA55S_VARIANT_SOURCE_ID = "ER-SRC-082"

PUMP_DATA_REF = {
    "sourceId": PUMP_DATA_SOURCE_ID,
    "document": "Каталог трансформаторных электронасосов по ТУ 26-06-1617-92",
    "title": "ТТ 63/10-02 — обозначение и технические характеристики",
    "url": "https://www.pintam.ru/component/virtuemart/catalog/nasosi-transform-detail?Itemid=0",
    "locator": "раздел «Характеристики модельного ряда», строка ТТ 63/10 и расшифровка ТТ63-10-02",
}
ERMAK_OPERATION_REF = {
    "sourceId": ERMAK_OPERATION_SOURCE_ID,
    "document": "ИДМБ.661142.009РЭ7, электровоз магистральный 2ЭС5К (3ЭС5К)",
    "title": "Использование по назначению — вспомогательные машины, маслонасос M15 и вентилятор M13",
    "url": "https://rcit.su/techinfoV57.html",
    "locator": "проверка вспомогательных машин, зимняя эксплуатация и проверка электрического торможения",
}
ERMAK_NVA55_REF = {
    "sourceId": ERMAK_NVA55_SOURCE_ID,
    "document": "ИДМБ.661142.009РЭ3, электровоз магистральный 2ЭС5К (3ЭС5К)",
    "title": "Асинхронный электродвигатель НВА-55 — назначение, техническая характеристика и устройство",
    "url": "https://rcit.su/techinfoV53.html",
    "locator": "раздел 2 «Описание и работа асинхронного электродвигателя НВА-55»",
}
NVA55_TECH_REF = {
    "sourceId": NVA55_TECH_SOURCE_ID,
    "document": "ИДМБ.661141.004РЭ3, электровоз 2ЭС4К, заводское руководство по эксплуатации",
    "title": "Электродвигатель НВА-55 — техническая характеристика того же типа аппарата",
    "url": "https://sinref.ru/000_uchebniki/05301_transport_jd_elektrovozi/154_00_elektrovoz-2ES4K_ruk_s-saita-inov_04600_raznie_13/001.htm",
    "locator": "раздел 2.2, таблица 2",
}
NVA55S_VARIANT_REF = {
    "sourceId": NVA55S_VARIANT_SOURCE_ID,
    "document": "Техническая публикация об изменениях конструкции электровоза 2ЭС5К «Ермак»",
    "title": "НВА-55 и НВА-55С — изменение исполнения вспомогательных электродвигателей",
    "url": "https://scbist.com/xx2/50844-01-2017-nekotorye-izmeneniya-v-konstrukcii-elektrovoza-2es5k-ermak.html",
    "locator": "пункт о замене НВА-55 с алюминиевым ротором на НВА-55С с медным ротором",
}

PUMP_PARAMETERS = [
    {"name": "Номинальная подача", "value": 63, "unit": "m3/h", "sourceId": PUMP_DATA_SOURCE_ID},
    {"name": "Напор при номинальной подаче", "value": 10, "unit": "m", "sourceId": PUMP_DATA_SOURCE_ID},
    {"name": "Рабочий интервал подач", "value": "40–80", "unit": "m3/h", "sourceId": PUMP_DATA_SOURCE_ID},
    {"name": "Допускаемый кавитационный запас при номинальной подаче", "value": 3.5, "unit": "m", "sourceId": PUMP_DATA_SOURCE_ID},
    {"name": "Номинальная мощность встроенного электродвигателя", "value": 2.2, "unit": "kW", "sourceId": PUMP_DATA_SOURCE_ID},
    {"name": "Габаритные размеры", "value": "425×330×445", "unit": "mm", "sourceId": PUMP_DATA_SOURCE_ID},
    {"name": "Масса", "value": 105, "unit": "kg", "sourceId": PUMP_DATA_SOURCE_ID},
]

FAN_PARAMETERS = [
    {"name": "Род тока электродвигателя", "value": "трёхфазный", "unit": "", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Номинальное линейное напряжение электродвигателя", "value": 380, "unit": "V", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Мощность на валу электродвигателя", "value": 55, "unit": "kW", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Номинальный линейный ток электродвигателя", "value": 113, "unit": "A", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Номинальная частота", "value": 50, "unit": "Hz", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Синхронная частота вращения", "value": 1500, "unit": "rpm", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "КПД электродвигателя", "value": 90.2, "unit": "%", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Коэффициент мощности", "value": 0.82, "unit": "", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Режим работы электродвигателя", "value": "продолжительный или повторно-кратковременный", "unit": "", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Класс нагревостойкости изоляции", "value": "F", "unit": "", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Масса электродвигателя НВА-55", "value": 375, "unit": "kg", "sourceId": NVA55_TECH_SOURCE_ID},
    {"name": "Минимальный расход воздуха через ББР", "value": 250, "unit": "m3/min", "sourceId": BBR_MAINT_SOURCE_ID},
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
    source_id = ref["sourceId"]
    for existing_key, existing in registry.items():
        if isinstance(existing, dict) and existing.get("sourceId") == source_id:
            if existing_key != key and existing != ref:
                raise SystemExit(f"Source ID {source_id} already used by {existing_key}")
    registry[key] = ref


def source_by_id(registry, source_id):
    matches = [v for v in registry.values() if isinstance(v, dict) and v.get("sourceId") == source_id]
    if len(matches) != 1:
        raise SystemExit(f"Expected one registry source {source_id}, found {len(matches)}")
    return matches[0]


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
    register_source(registry, "TT6310_PRODUCT_DATA", PUMP_DATA_REF)
    register_source(registry, "ERMAK_AUX_OPERATION", ERMAK_OPERATION_REF)
    register_source(registry, "ERMAK_NVA55_BASE", ERMAK_NVA55_REF)
    register_source(registry, "NVA55_SAME_TYPE_FACTORY_DATA", NVA55_TECH_REF)
    register_source(registry, "NVA55S_LATE_VARIANT_CHANGE", NVA55S_VARIANT_REF)
    bbr_maint_ref = source_by_id(registry, BBR_MAINT_SOURCE_ID)

    pump = find_record(root, PUMP_ID)
    fan = find_record(root, FAN_ID)
    tr010 = find_record(root, "ER-EQ-TR-010")
    tr013 = find_record(root, "ER-EQ-TR-013")

    if pump.get("modelNames") != ["ТТ 63/10-02"] or pump.get("schemeDesignations") != ["M15"]:
        raise SystemExit(f"Unexpected {PUMP_ID} identity: {pump.get('modelNames')!r} / {pump.get('schemeDesignations')!r}")
    if fan.get("schemeDesignations") != ["M13"]:
        raise SystemExit(f"Unexpected {FAN_ID} scheme: {fan.get('schemeDesignations')!r}")
    if fan.get("modelNames"):
        raise SystemExit(f"{FAN_ID} acquired a model concurrently: {fan.get('modelNames')!r}")
    if pump.get("parameters") or fan.get("parameters"):
        raise SystemExit("AU-004 or AU-005 already has parameters; review concurrent changes before enriching")
    if len(tr010.get("parameters", [])) != 8:
        raise SystemExit("TR-010 state changed; stop before applying auxiliary package")
    if tr013.get("parameters") or tr013.get("modelNames") or tr013.get("schemeDesignations"):
        raise SystemExit("TR-013 state changed; stop before applying auxiliary package")

    pump["purpose"] = (
        "Принудительная циркуляция трансформаторного масла в системе охлаждения тягового трансформатора; "
        "на 2ЭС5К/3ЭС5К электронасос M15 работает совместно с системой вспомогательных машин."
    )
    pump["parameters"] = PUMP_PARAMETERS
    pump["sourceRefs"] = unique_refs(pump.get("sourceRefs", []) + [PUMP_DATA_REF, ERMAK_OPERATION_REF])
    pump["parameterCoverage"] = {"status": "documented", "count": len(PUMP_PARAMETERS)}
    pump_notes = [n for n in pump.get("notes", []) if not n.startswith("M15:") and not n.startswith("ТТ 63/10-02:")]
    pump_notes += [
        "M15: при штатной проверке вспомогательных машин должен запускаться вместе с вентиляторами M11–M12; повышенный шум маслонасоса в РЭ указан как основание для его замены.",
        "При температуре масла ниже −15 °C датчик-реле SK11 через KV47 отключает M15; после нагрева масла выше −10 °C насос возвращается в штатную схему.",
        "ТТ 63/10-02: число 63 в обозначении соответствует номинальной подаче 63 м³/ч, число 10 — напору 10 м; «02» относится к климатическому исполнению и категории размещения. Температурный предел масла в доступных каталогах расходится, поэтому в паспортные параметры карточки он не включён.",
    ]
    pump["notes"] = pump_notes

    fan["modelNames"] = ["НВА-55"]
    fan["purpose"] = (
        "Привод центробежного вентилятора M13, обеспечивающего принудительное охлаждение блока балластных резисторов R10 "
        "при электрическом торможении/рекуперации."
    )
    fan["parameters"] = FAN_PARAMETERS
    fan["sourceRefs"] = unique_refs(
        fan.get("sourceRefs", []) + [bbr_maint_ref, ERMAK_OPERATION_REF, ERMAK_NVA55_REF, NVA55_TECH_REF, NVA55S_VARIANT_REF]
    )
    fan["parameterCoverage"] = {"status": "documented", "count": len(FAN_PARAMETERS)}
    fan_notes = [n for n in fan.get("notes", []) if not n.startswith("M13:") and not n.startswith("НВА-55:") and not n.startswith("НВА-55С:")]
    fan_notes += [
        "M13: в базовом профиле атласа привод вентилятора описывается асинхронным трёхфазным НВА-55; РЭ 2ЭС5К/3ЭС5К прямо содержит отдельный раздел по НВА-55 как вспомогательной электрической машине.",
        "В режиме рекуперации M13 включается контактором KM13 после формирования соответствующих условий; отсутствие его работы означает потерю охлаждения ББР и может приводить к ограничению электрического торможения.",
        "НВА-55С: на более поздних изменениях конструкции НВА-55 с алюминиевым ротором заменялся машиной НВА-55С с медным ротором. Паспортные данные НВА-55С не смешиваются с базовой карточкой НВА-55; конкретное исполнение сверять по маркировке секции и двигателя.",
    ]
    fan["notes"] = fan_notes

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    pump = find_article(root, PUMP_ID, PUMP_ARTICLE_ID)
    fan = find_article(root, FAN_ID, FAN_ARTICLE_ID)

    pump["summary"] = (
        "Электронасос M15 ТТ 63/10-02 обеспечивает циркуляцию масла тягового трансформатора и тем самым работу его принудительной системы охлаждения."
    )
    pump["principle"] = (
        "Центробежный герметичный электронасос создаёт циркуляцию трансформаторного масла через охлаждающий контур. "
        "Номинальная подача типа ТТ 63/10 составляет 63 м³/ч при напоре 10 м. На электровозе управление M15 связано со схемой вспомогательных машин; "
        "при слишком холодном масле SK11/KV47 временно запрещают работу насоса до прогрева."
    )
    pump["keyParameters"] = kb_parameters(
        PUMP_PARAMETERS,
        "ТТ 63/10-02 (M15) базового 2ЭС5К/3ЭС5К; гидравлические и габаритные значения относятся к точному типу ТТ 63/10 по ТУ 26-06-1617-92.",
    )
    pump["normalState"] = [
        "M15 запускается в предусмотренных схемой режимах и обеспечивает устойчивую циркуляцию масла без повышенного шума и заметной вибрации.",
        "Корпус насоса, фланцевые соединения и трубопроводы герметичны; подтекания масла отсутствуют.",
        "При температуре масла ниже −15 °C блокировка SK11/KV47 не допускает работу насоса; после прогрева выше −10 °C M15 возвращается в штатный режим.",
        "Работа насоса сопровождается ожидаемым охлаждением тягового трансформатора без защитных ограничений по температуре."
    ]
    pump["deviationSigns"] = [
        "Повышенный шум маслонасоса — прямой признак отклонения; руководство предписывает замену такого насоса.",
        "M15 не запускается при допустимой температуре масла и штатно работающей цепи вспомогательных машин.",
        "Есть течь масла, заметная вибрация либо нарушение крепления и фланцевых соединений.",
        "Температура трансформатора растёт при ожидаемой работе M15; требуется проверка фактической циркуляции, контура охлаждения и электрической цепи привода."
    ]
    pump["sourceRefs"] = unique_strings(pump.get("sourceRefs", []) + [SCHEME_SOURCE_ID, RE4_SOURCE_ID, PUMP_DATA_SOURCE_ID, ERMAK_OPERATION_SOURCE_ID])
    base_rules = [r for r in pump.get("variantRules", []) if not r.startswith("ТТ 63/10-02:")]
    pump["variantRules"] = unique_strings(base_rules + [
        "ТТ 63/10-02: гидравлические характеристики приведены по точному типу ТТ 63/10; климатическое исполнение «02» не должно подменяться данными других модификаций насосов.",
        "Применимость по профилям атласа: base_early."
    ])
    pump.setdefault("atlasData", {})["parameterCoverage"] = {"status": "documented", "count": len(PUMP_PARAMETERS)}
    pump["atlasData"]["modelNames"] = ["ТТ 63/10-02"]
    pump.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    pump["knowledgeCoverage"]["normalState"] = "SOURCE_BACKED_NON_PROCEDURAL"
    pump["knowledgeCoverage"]["deviationSigns"] = "SOURCE_BACKED_NON_DIAGNOSTIC"

    fan["summary"] = (
        "M13 — привод центробежного вентилятора ББР. В базовом исполнении карточка относится к асинхронному двигателю НВА-55; вентилятор работает при рекуперации и отводит тепло от R10."
    )
    fan["principle"] = (
        "Трёхфазный асинхронный двигатель НВА-55 вращает центробежное рабочее колесо вентилятора. В схеме электрического торможения контактор KM13 включает M13, "
        "после чего поток воздуха проходит через блок балластных резисторов R10. Для ББР контролируется достаточный расход охлаждающего воздуха; подтверждённое требование — не менее 250 м³/мин."
    )
    fan["keyParameters"] = kb_parameters(
        FAN_PARAMETERS,
        "Базовый профиль 2ЭС5К/3ЭС5К: M13 с НВА-55. Паспортные числа двигателя взяты из заводского РЭ того же типа НВА-55 на другой серии; поздний НВА-55С является отдельным вариантом и требует собственных значений.",
    )
    fan["normalState"] = [
        "В режиме рекуперации M13 запускается после формирования схемных условий и создаёт устойчивый поток воздуха через ББР.",
        "Рабочее колесо вращается без затирания, выраженной вибрации и постороннего шума; крепление блока вентилятора и воздуховодов надёжно.",
        "Двигатель не имеет признаков перегрева, повреждения изоляции или ослабления выводов; токи и режим соответствуют исправной вспомогательной машине.",
        "Расход воздуха через ББР соответствует требуемому уровню; нагрев резисторного блока не выходит за допустимый режим."
    ]
    fan["deviationSigns"] = [
        "M13 не запускается при собранной схеме рекуперации либо отключается после пуска.",
        "Слышны затирание рабочего колеса, повышенный шум или вибрация; требуется проверка зазоров, крепления и состояния двигателя/вентилятора.",
        "Недостаточный поток воздуха сопровождается ускоренным нагревом ББР и может приводить к ограничению электрического торможения или его замещению пневматическим.",
        "Есть признаки перегрева двигателя, повреждения выводов или снижения сопротивления изоляции."
    ]
    fan["sourceRefs"] = unique_strings(
        fan.get("sourceRefs", []) + [SCHEME_SOURCE_ID, BBR_MAINT_SOURCE_ID, ERMAK_OPERATION_SOURCE_ID, ERMAK_NVA55_SOURCE_ID, NVA55_TECH_SOURCE_ID, NVA55S_VARIANT_SOURCE_ID]
    )
    base_rules = [r for r in fan.get("variantRules", []) if not r.startswith("M13/NVA") and not r.startswith("НВА-55С:")]
    fan["variantRules"] = unique_strings(base_rules + [
        "M13/NVA-55: базовый профиль атласа описывает двигатель НВА-55, прямо представленный в РЭ 2ЭС5К/3ЭС5К как тип вспомогательной асинхронной машины.",
        "НВА-55С: на последующих исполнениях применялась модернизированная машина с медным ротором; её ток, cosφ, масса и другие паспортные числа не смешивать с НВА-55.",
        "Применимость по профилям атласа: base_early."
    ])
    fan.setdefault("atlasData", {})["parameterCoverage"] = {"status": "documented", "count": len(FAN_PARAMETERS)}
    fan["atlasData"]["modelNames"] = ["НВА-55"]
    fan.setdefault("knowledgeCoverage", {})["parameters"] = "documented"
    fan["knowledgeCoverage"]["normalState"] = "SOURCE_BACKED_NON_PROCEDURAL"
    fan["knowledgeCoverage"]["deviationSigns"] = "SOURCE_BACKED_NON_DIAGNOSTIC"

    write_gz(path, root)


def main():
    for root in ROOTS:
        patch_equipment(root / "ermak_equipment.json.gz")
        patch_knowledge(root / "ermak_knowledge.json.gz")


if __name__ == "__main__":
    main()
