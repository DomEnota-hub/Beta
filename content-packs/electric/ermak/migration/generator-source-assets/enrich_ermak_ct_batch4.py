#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
TARGETS = {
    "ER-EQ-CT-007": "ER-KB-EQ-ER-EQ-CT-007",
    "ER-EQ-CT-011": "ER-KB-EQ-ER-EQ-CT-011",
    "ER-EQ-CT-012": "ER-KB-EQ-ER-EQ-CT-012",
    "ER-EQ-CT-013": "ER-KB-EQ-ER-EQ-CT-013",
}
SCHEME_ID = "ER-SRC-002"
RE4_ID = "ER-SRC-005"
RE5_ID = "ER-SRC-006"
KM_AE_ID = "ER-SRC-085"
RE8_ID = "ER-SRC-086"
PB3_ID = "ER-SRC-087"
BU_INTERLOCK_ID = "ER-SRC-088"
BP_SWITCH_ID = "ER-SRC-089"
BS173_ID = "ER-SRC-090"

KM_AE_REF = {
    "sourceId": KM_AE_ID,
    "document": "Учебно-технический материал по аппаратам электровоза 2ЭС5К",
    "title": "КМ-34 и АЕ2541М/АЕ2544М — назначение, устройство и технические характеристики",
    "url": "https://studopedia.net/20_24290_rele-peregruzki-tipov-rt--rt--rt--.html",
    "locator": "разделы 7.18 и 8.1",
}
RE8_REF = {
    "sourceId": RE8_ID,
    "document": "ИДМБ.661142.009РЭ8 (3ТС.001.012РЭ8), электровоз 2ЭС5К (3ЭС5К)",
    "title": "Инструкция по техническому обслуживанию — КМ-34, БВ-108, АЕ2541М, БП-207-02, ПБ-179 и БС-173",
    "url": "https://rcit.su/techinfoV58.html",
    "locator": "разделы 6.4.7, 6.5.5, 7.4.6, 8.4.8 и 8.4.11",
}
PB3_REF = {
    "sourceId": PB3_ID,
    "document": "ЗАО «Электромагнит», технические данные изделия ПБ-3",
    "title": "Пневматическая блокировка ПБ-3 — назначение и основные характеристики",
    "url": "https://vv32.ru/product/pb-3/",
    "locator": "таблица основных технических характеристик",
}
BU_INTERLOCK_REF = {
    "sourceId": BU_INTERLOCK_ID,
    "document": "ИДМБ.661141.004РЭ4, заводское руководство электровоза 2ЭС4К",
    "title": "Блокировочное устройство БУ-01/БУ-02 — технические характеристики того же типа аппарата",
    "url": "https://zinref.ru/000_uchebniki/04600_raznie_3/078_eletrovoz_2es4k_rukovod/017.htm",
    "locator": "раздел 1.41",
}
BP_SWITCH_REF = {
    "sourceId": BP_SWITCH_ID,
    "document": "Техническое описание блокировочных переключателей ПБ-179, БП-207",
    "title": "ПБ-179 и БП-207 — общие технические характеристики аппаратов того же семейства",
    "url": "https://poezdvl.com/vl85/vl85_49.html",
    "locator": "раздел «Блокировочные переключатели ПБ-179, БП-207»",
}
BS173_REF = {
    "sourceId": BS173_ID,
    "document": "ОАО «Электромашина», каталог электросиловой аппаратуры для электровозов",
    "title": "Блок сигнализации БС-173 — технические характеристики",
    "url": "https://promspectech.com/images/electrovoz.pdf",
    "locator": "таблица технических характеристик БС-173",
}

KM_PARAMS = [
    {"name": "Номинальное напряжение постоянного тока", "value": 50, "unit": "V", "sourceId": KM_AE_ID},
    {"name": "Номинальный ток", "value": 16, "unit": "A", "sourceId": KM_AE_ID},
    {"name": "Количество контактов реверсивного вала", "value": 4, "unit": "", "sourceId": KM_AE_ID},
    {"name": "Количество контактов главного вала", "value": 5, "unit": "", "sourceId": KM_AE_ID},
    {"name": "Масса", "value": 10.6, "unit": "kg", "sourceId": KM_AE_ID},
]
BREAKER_PARAMS = [
    {"name": "Номинальное напряжение постоянного тока для DC-исполнений АЕ2541М/АЕ2544М", "value": 110, "unit": "V", "sourceId": KM_AE_ID},
    {"name": "Номинальные токи расцепителей АЕ по базовой таблице", "value": "5; 10; 16; 25", "unit": "A", "sourceId": KM_AE_ID},
    {"name": "Уставки мгновенного срабатывания АЕ", "value": "1,3; 2; 3; 5; 10", "unit": "×In", "sourceId": KM_AE_ID},
    {"name": "Масса одного автомата АЕ", "value": 0.4, "unit": "kg", "sourceId": KM_AE_ID},
    {"name": "Поворот ключа механической блокировки БВ-108 для разблокирования", "value": 90, "unit": "deg", "sourceId": RE8_ID},
]
INTERLOCK_PARAMS = [
    {"name": "ПБ-3 — номинальное давление", "value": 0.5, "unit": "MPa", "sourceId": PB3_ID},
    {"name": "ПБ-3 — диапазон рабочих давлений", "value": "0,35–0,675", "unit": "MPa", "sourceId": PB3_ID},
    {"name": "ПБ-3 — ход штока", "value": 24, "unit": "mm", "sourceId": PB3_ID},
    {"name": "ПБ-3 — габаритные размеры", "value": "194×114×82", "unit": "mm", "sourceId": PB3_ID},
    {"name": "БУ-01/БУ-02 — номинальное напряжение контактора", "value": 50, "unit": "V", "sourceId": BU_INTERLOCK_ID},
    {"name": "БУ-01/БУ-02 — номинальный ток контактора", "value": 16, "unit": "A", "sourceId": BU_INTERLOCK_ID},
    {"name": "БУ-01/БУ-02 — отключаемый ток при индуктивной нагрузке τ=0,05 с", "value": 8, "unit": "A", "sourceId": BU_INTERLOCK_ID},
    {"name": "БУ-01/БУ-02 — масса", "value": 2.9, "unit": "kg", "sourceId": BU_INTERLOCK_ID},
    {"name": "БП-207/ПБ-179 — номинальное напряжение", "value": 50, "unit": "V", "sourceId": BP_SWITCH_ID},
    {"name": "БП-207/ПБ-179 — номинальный ток", "value": 16, "unit": "A", "sourceId": BP_SWITCH_ID},
    {"name": "БП-207/ПБ-179 — номинальное давление сжатого воздуха", "value": 0.5, "unit": "MPa", "sourceId": BP_SWITCH_ID},
    {"name": "БП-207/ПБ-179 — коммутируемый ток при индуктивной нагрузке τ=0,05 с", "value": 8, "unit": "A", "sourceId": BP_SWITCH_ID},
]
BS_PARAMS = [
    {"name": "Максимальная потребляемая мощность", "value": 8, "unit": "W", "sourceId": BS173_ID},
    {"name": "Номинальное напряжение цепей индикации (среднее)", "value": 50, "unit": "V", "sourceId": BS173_ID},
    {"name": "Допустимое переходное перенапряжение в течение 0,010 с", "value": 500, "unit": "V", "sourceId": BS173_ID},
    {"name": "Максимальное допустимое напряжение питания", "value": 65, "unit": "V", "sourceId": BS173_ID},
    {"name": "Минимальная сила света красного индикатора АЛ307КМ4", "value": 4.0, "unit": "mcd", "sourceId": BS173_ID},
    {"name": "Минимальная сила света зелёного индикатора АЛ307ГМ", "value": 1.5, "unit": "mcd", "sourceId": BS173_ID},
    {"name": "Максимальная масса блока", "value": 2.8, "unit": "kg", "sourceId": BS173_ID},
]


def read_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def write_gz(path, payload):
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with path.open("wb") as out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0, compresslevel=9) as gz:
            gz.write(raw)


def unique_strings(items):
    return list(dict.fromkeys(items))


def unique_refs(items):
    out, seen = [], set()
    for item in items:
        key = item.get("sourceId") if isinstance(item, dict) else str(item)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def register_source(registry, key, ref):
    if key in registry and registry[key] != ref:
        raise SystemExit(f"Source key {key} changed concurrently")
    sid = ref["sourceId"]
    for old_key, old in registry.items():
        if isinstance(old, dict) and old.get("sourceId") == sid and old_key != key:
            raise SystemExit(f"Source ID {sid} already used by {old_key}")
    registry[key] = ref


def source_by_id(registry, sid):
    found = [v for v in registry.values() if isinstance(v, dict) and v.get("sourceId") == sid]
    if len(found) != 1:
        raise SystemExit(f"Expected one source {sid}, found {len(found)}")
    return found[0]


def record(root, eid):
    rows = [x for x in root["records"] if x.get("id") == eid]
    if len(rows) != 1:
        raise SystemExit(f"Expected one record {eid}, found {len(rows)}")
    return rows[0]


def article(root, eid):
    rows = [x for x in root["articles"] if x.get("equipmentId") == eid]
    if len(rows) != 1:
        raise SystemExit(f"Expected one article {eid}, found {len(rows)}")
    return rows[0]


def kb_params(params, applicability):
    return [{
        "name": p["name"], "value": p["value"], "unit": p["unit"],
        "applicability": applicability, "status": "BASE_CONFIRMED", "sourceRefs": [p["sourceId"]]
    } for p in params]


def patch_equipment(path):
    root = read_gz(path)
    reg = root.setdefault("sourceRegistry", {})
    for key, ref in [
        ("KM34_AE25_TECH_DATA", KM_AE_REF),
        ("ERMAK_RE8_CONTROL_MAINT", RE8_REF),
        ("PB3_MANUFACTURER_DATA", PB3_REF),
        ("BU01_BU02_SAME_TYPE_DATA", BU_INTERLOCK_REF),
        ("BP207_PB179_SAME_FAMILY_DATA", BP_SWITCH_REF),
        ("BS173_MANUFACTURER_CATALOG", BS173_REF),
    ]:
        register_source(reg, key, ref)
    scheme = source_by_id(reg, SCHEME_ID)
    re4 = source_by_id(reg, RE4_ID)
    re5 = source_by_id(reg, RE5_ID)

    km = record(root, "ER-EQ-CT-007")
    br = record(root, "ER-EQ-CT-011")
    il = record(root, "ER-EQ-CT-012")
    bs = record(root, "ER-EQ-CT-013")
    if km.get("modelNames") != ["КМ-34"] or km.get("schemeDesignations") != ["SM1"]:
        raise SystemExit("CT-007 identity changed")
    if br.get("modelNames") != ["БВ-108", "АЕ2541М", "АЕ2544М"] or br.get("schemeDesignations"):
        raise SystemExit("CT-011 identity changed")
    if il.get("modelNames") != ["ПБ-3", "БУ-01/02/03", "БП-207-02", "ПБ-179"] or il.get("schemeDesignations"):
        raise SystemExit("CT-012 identity changed")
    if bs.get("modelNames") != ["БС-173"] or bs.get("schemeDesignations") != ["A23"]:
        raise SystemExit("CT-013 identity changed")
    if any(x.get("parameters") for x in (km, br, il, bs)):
        raise SystemExit("One of CT-007/011/012/013 already has parameters; review concurrent change")
    if len(record(root, "ER-EQ-CT-002").get("parameters", [])) != 5:
        raise SystemExit("CT-002 neighbor changed")
    if len(record(root, "ER-EQ-CT-004").get("parameters", [])) != 6:
        raise SystemExit("CT-004 neighbor changed")
    if len(record(root, "ER-EQ-CT-005").get("parameters", [])) != 9:
        raise SystemExit("CT-005 neighbor changed")

    km["purpose"] = "Задание направления движения, тяги, скорости и рекуперативного торможения с передачей команд в МСУД-Н."
    km["parameters"] = KM_PARAMS
    km["sourceRefs"] = unique_refs(km.get("sourceRefs", []) + [KM_AE_REF, RE8_REF])
    km["parameterCoverage"] = {"status": "documented", "count": len(KM_PARAMS)}
    km["notes"] = [
        "КМ-34 содержит реверсивный и главный кулачковые переключатели и датчик задания скорости; реверсивные положения: В/0/Н.",
        "Главный переключатель имеет зоны тяги и рекуперации с подготовительным и нулевым положениями; реверсивная рукоятка снимается в положении «0».",
        "При ремонте контролируют профиль кулачковых шайб, фиксацию валов, механическую блокировку и диаграмму коммутации контактов."
    ]

    br["purpose"] = "Распределение, оперативное включение и защита низковольтных цепей управления; карточка объединяет блок выключателей БВ-108 и применяемые автоматы семейства АЕ."
    br["parameters"] = BREAKER_PARAMS
    br["sourceRefs"] = unique_refs(br.get("sourceRefs", []) + [KM_AE_REF, RE8_REF])
    br["parameterCoverage"] = {"status": "documented", "count": len(BREAKER_PARAMS)}
    br["notes"] = [
        "Параметры напряжения, расцепителей и массы относятся к автоматам АЕ2541М/АЕ2544М, а не к блоку БВ-108.",
        "Конкретные номиналы установленного автомата определяются его исполнением, маркировкой и схемной позицией; базовая таблица серии не заменяет проверку конкретного SF.",
        "У БВ-108 механическая блокировка устроена так, что при снятом ключе заблокированные выключатели нельзя включить; разблокирование выполняется поворотом ключа на 90°, после чего ключ нельзя вынуть во включённом состоянии.",
        "АЕ2541М в эксплуатации не ремонтируется: при нарушении работы РЭ8 предписывает замену."
    ]

    il["purpose"] = "Сводная карточка блокировочных аппаратов цепей безопасности и коммутации: ПБ-3 и БУ-01/02/03 обеспечивают блокировки доступа ВВК, а БП-207-02/ПБ-179 выполняют связанные схемой кулачковые переключения; функции аппаратов не считаются взаимозаменяемыми."
    il["parameters"] = INTERLOCK_PARAMS
    il["sourceRefs"] = unique_refs(il.get("sourceRefs", []) + [PB3_REF, BU_INTERLOCK_REF, BP_SWITCH_REF, RE8_REF])
    il["parameterCoverage"] = {"status": "documented", "count": len(INTERLOCK_PARAMS)}
    il["notes"] = [
        "ПБ-3 автоматически блокирует двери ВВК и люки крыши при поднятом токоприёмнике. Масса ПБ-3 намеренно не включена: в открытых источниках для исполнений встречаются 3,0 и 3,5 кг.",
        "БУ-01/БУ-02 предназначены для взаимного блокирования штор ВВК. Числа из карточки относятся к БУ-01/БУ-02; на БУ-03 они автоматически не переносятся без отдельного паспорта.",
        "БП-207-02 и ПБ-179 — пневматические кулачковые блокировочные переключатели; их функция шире механической блокировки дверей ВВК, поэтому они не считаются аналогами ПБ-3 или БУ-01/02.",
        "На 2ЭС5К БП-207-02 и ПБ-179 обслуживаются совместно с КМ-34: проверяются кулачковые шайбы, контакторы, фиксация и диаграмма коммутации."
    ]

    bs["purpose"] = "Световая индикация состояния оборудования, цепей управления и защит в кабине машиниста."
    bs["parameters"] = BS_PARAMS
    bs["sourceRefs"] = unique_refs(bs.get("sourceRefs", []) + [re5, BS173_REF, RE8_REF])
    bs["parameterCoverage"] = {"status": "documented", "count": len(BS_PARAMS)}
    bs["notes"] = [
        "БС-173 выполнен на базе передней панели и четырёх печатных плат со светодиодными индикаторами.",
        "При ТО блок проверяют в обесточенном состоянии; РЭ8 предусматривает продувку сухим сжатым воздухом 0,2 МПа и проверку целостности монтажа.",
        "При восстановлении пайки РЭ8 ограничивает мощность паяльника 60 Вт и время пайки 3 с; новые соединения покрываются лаком НЦ-62."
    ]

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path):
    root = read_gz(path)
    km = article(root, "ER-EQ-CT-007")
    br = article(root, "ER-EQ-CT-011")
    il = article(root, "ER-EQ-CT-012")
    bs = article(root, "ER-EQ-CT-013")

    km["summary"] = "КМ-34 (SM1) — электромеханический контроллер машиниста для задания направления, тяги, скорости и рекуперативного торможения."
    km["principle"] = "Два кулачковых переключателя — реверсивный и главный — формируют дискретные команды, а датчик скорости задаёт требуемую скорость. Команды поступают в МСУД-Н; механическая блокировка исключает недопустимое сочетание положений валов."
    km["keyParameters"] = kb_params(KM_PARAMS, "КМ-34 базового профиля 2ЭС5К/3ЭС5К, головная секция.")
    km["normalState"] = [
        "Реверсивный и главный валы чётко фиксируются на предусмотренных позициях; рукоятки перемещаются без заеданий.",
        "Кулачковые шайбы, ролики, изоляторы, рычаги, гибкие шунты и контактные напайки не имеют повреждений, влияющих на диаграмму коммутации.",
        "Механическая блокировка между валами работает, а фактическое состояние контактов соответствует диаграмме выбранной позиции.",
        "Задание направления, тяги/торможения и скорости устойчиво воспринимается МСУД-Н."
    ]
    km["deviationSigns"] = [
        "Вал не фиксируется, рукоятка заедает либо механическая блокировка допускает несогласованное положение.",
        "Профиль кулачка повреждён, ролик не отрабатывает профиль или контактная группа имеет трещины, надломы шунтов/изоляторов либо чрезмерный износ.",
        "Состояние контактов не соответствует диаграмме коммутации выбранной позиции.",
        "МСУД-Н получает нестабильное или нелогичное задание при механически исправном положении органов управления."
    ]
    km["sourceRefs"] = unique_strings(km.get("sourceRefs", []) + [KM_AE_ID, RE8_ID])

    br["summary"] = "БВ-108 и автоматы АЕ2541М/АЕ2544М образуют кабиночный узел оперативного включения, распределения и защиты низковольтных цепей управления."
    br["principle"] = "БВ-108 объединяет органы ручного включения и механическую ключевую блокировку, а автоматические выключатели АЕ отключают защищаемые цепи при перегрузке/коротком замыкании согласно своему исполнению расцепителя."
    br["keyParameters"] = kb_params(BREAKER_PARAMS, "БВ-108 и семейство АЕ в базовом профиле; номинал конкретного автомата проверять по маркировке и схемной позиции.")
    br["normalState"] = [
        "Рукоятки БВ-108 чётко переключаются, механическая ключевая блокировка исключает включение заблокированных цепей.",
        "Автоматы АЕ удерживаются во включённом состоянии при исправной защищаемой цепи и не имеют механических повреждений/перегрева.",
        "Номинал и уставка каждого установленного автомата соответствуют его маркировке и назначению конкретной цепи.",
        "Питание защищаемых цепей управления присутствует без самопроизвольных отключений."
    ]
    br["deviationSigns"] = [
        "Нарушена механическая блокировка БВ-108: ключ извлекается или выключатель включается в недопустимом состоянии.",
        "Автомат не включается, не удерживается либо повторно срабатывает при отсутствии подтверждённой перегрузки в цепи.",
        "Есть следы нагрева, повреждения корпуса/клемм или несоответствие установленного номинала схеме.",
        "После проверки защищаемой цепи неисправный АЕ2541М подлежит замене, а не ремонту на электровозе."
    ]
    br["sourceRefs"] = unique_strings(br.get("sourceRefs", []) + [KM_AE_ID, RE8_ID])
    br["variantRules"] = unique_strings(br.get("variantRules", []) + ["Для автоматов АЕ значения зависят от конкретного исполнения; карточка не подменяет маркировку конкретной позиции SF."])

    il["summary"] = "Сводный узел блокировочных аппаратов ВВК и связанных кулачковых переключателей: ПБ-3, БУ-01/02/03, БП-207-02 и ПБ-179."
    il["principle"] = "ПБ-3 использует давление пневмосистемы для физической блокировки доступа к ВВК при поднятом токоприёмнике; БУ-01/02 взаимно блокируют шторы ключами и кулачковыми контактами. БП-207-02/ПБ-179 являются отдельными пневматическими кулачковыми переключателями и выполняют собственные схемные коммутации."
    il["keyParameters"] = kb_params(INTERLOCK_PARAMS, "Параметры подписаны по конкретному аппарату; не переносить между ПБ-3, БУ и БП/ПБ переключателями.")
    il["normalState"] = [
        "ПБ-3 механически блокирует двери/люки при наличии давления и не препятствует штатному доступу после безопасного снятия условий блокировки.",
        "Ключевая логика БУ-01/02 исключает открытие штор при опасном состоянии; контакты и кулачковый вал переключаются чётко.",
        "БП-207-02 и ПБ-179 имеют исправные кулачковые шайбы, контакторы, пневмопривод и соответствуют своей диаграмме коммутации.",
        "Разрешение на подъём токоприёмника/включение ГВ появляется только при выполненной цепи безопасных блокировок."
    ]
    il["deviationSigns"] = [
        "ПБ-3 не блокирует доступ при требуемом давлении, шток заедает либо есть утечка/механическое повреждение.",
        "Ключи или вал БУ-01/02 допускают недопустимую последовательность либо контакты не соответствуют положению механизма.",
        "БП-207-02/ПБ-179 переключаются нечётко, имеют повреждение кулачков/контакторов или несоответствие диаграмме коммутации.",
        "Цепь блокировок запрещает штатный подъём токоприёмника/включение ГВ либо, наоборот, выдаёт разрешение при нарушенном ограждении."
    ]
    il["sourceRefs"] = unique_strings(il.get("sourceRefs", []) + [RE4_ID, RE8_ID, PB3_ID, BU_INTERLOCK_ID, BP_SWITCH_ID])
    il["variantRules"] = unique_strings(il.get("variantRules", []) + [
        "Масса ПБ-3 исключена из параметров из-за расхождения 3,0/3,5 кг между источниками исполнения.",
        "Параметры БУ-01/02 не распространяются автоматически на БУ-03 без паспорта конкретного исполнения.",
        "БП-207-02 и ПБ-179 не считать функциональными аналогами ПБ-3 или БУ-01/02: это отдельные кулачковые переключатели."
    ])

    bs["summary"] = "БС-173 (A23) — кабиночный блок световой сигнализации состояния оборудования, управления и защит."
    bs["principle"] = "Сигналы состояния поступают на электронные платы блока и отображаются красными/зелёными светодиодными индикаторами передней панели; питание цепей индикации рассчитано на бортовую низковольтную сеть."
    bs["keyParameters"] = kb_params(BS_PARAMS, "БС-173 базового профиля 2ЭС5К/3ЭС5К, позиция A23.")
    bs["normalState"] = [
        "Индикация читаема, соответствует фактическим состояниям оборудования и не имеет самопроизвольного мерцания/ложных комбинаций.",
        "Корпус, передняя панель, платы, разъёмы, проводка и крепёж целы; следов перегрева и загрязнения, мешающего работе, нет.",
        "При ТО монтаж очищен сухим воздухом и проверен без подачи питания; ослабленный крепёж подтянут.",
        "После ремонта электрические соединения и целостность проводов проверены до включения."
    ]
    bs["deviationSigns"] = [
        "Индикатор не светится при подтверждённом активном сигнале либо светится без соответствующего состояния цепи.",
        "Наблюдаются нестабильная яркость, мерцание, множественная ложная индикация или признаки нарушения питания блока.",
        "Обнаружены повреждённые провода, пайка, платы, разъёмы, крепёж или следы перегрева.",
        "После исключения внешней цепи сигнала индикация остаётся некорректной, что требует проверки самого БС-173."
    ]
    bs["sourceRefs"] = unique_strings(bs.get("sourceRefs", []) + [RE5_ID, RE8_ID, BS173_ID])

    for a, params in ((km, KM_PARAMS), (br, BREAKER_PARAMS), (il, INTERLOCK_PARAMS), (bs, BS_PARAMS)):
        a["atlasData"]["parameterCoverage"] = {"status": "documented", "count": len(params)}
        a["knowledgeCoverage"]["parameters"] = "documented"
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / "ermak_equipment.json.gz")
    patch_knowledge(base / "ermak_knowledge.json.gz")
print("Enriched Ermak CT-007, CT-011, CT-012 and CT-013")
