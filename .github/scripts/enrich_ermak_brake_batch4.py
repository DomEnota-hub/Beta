#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
TARGETS = {
    "ER-EQ-BR-004": "ER-KB-EQ-ER-EQ-BR-004",
    "ER-EQ-BR-009": "ER-KB-EQ-ER-EQ-BR-009",
    "ER-EQ-BR-012": "ER-KB-EQ-ER-EQ-BR-012",
    "ER-EQ-BR-014": "ER-KB-EQ-ER-EQ-BR-014",
}

BVR_ID = "ER-SRC-095"
OVERHAUL_ID = "ER-SRC-096"
CHANGES_ID = "ER-SRC-097"
EPK_ERMAK_ID = "ER-SRC-098"
EPK_CONSTRUCTION_ID = "ER-SRC-099"
KM395_ID = "ER-SRC-100"

BVR_REF = {
    "sourceId": BVR_ID,
    "document": "Блок тормозного оборудования 010 для локомотивов грузового типа",
    "title": "Блок воздухораспределителя БТО 010: состав, режимы и проверочные давления",
    "url": "https://rcit.su/techinfoP4.html",
    "locator": "разделы 1.2 и 1.5, таблица 2",
}
OVERHAUL_REF = {
    "sourceId": OVERHAUL_ID,
    "document": "ЦАРВ.094.00.00.000 РК, руководство по среднему и капитальному ремонту электровозов 2ЭС5К/3ЭС5К",
    "title": "Перечень тормозных аппаратов 2ЭС5К/3ЭС5К",
    "url": "https://www.centrmag.ru/catalog/product/carv_094_00_00_000_rk_rykovodstvo_po_srednemy_i_kapitalnomy_remonty_elektrovozov_2es5k_3es5k/",
    "locator": "разделы 4.5.5, 4.5.8, 4.5.9 и 4.5.11",
}
CHANGES_REF = {
    "sourceId": CHANGES_ID,
    "document": "Некоторые изменения в конструкции электровоза 2ЭС5К «Ермак»",
    "title": "Профиль тормозного оборудования 2ЭС5К: 395М-3-01 и кран управления 215-1",
    "url": "https://scbist.com/xx2/50844-01-2017-nekotorye-izmeneniya-v-konstrukcii-elektrovoza-2es5k-ermak.html",
    "locator": "изменения №057–058 и №192",
}
EPK_ERMAK_REF = {
    "sourceId": EPK_ERMAK_ID,
    "document": "VR-тренажер «Ремонт узлов и деталей электровоза переменного тока 2ЭС5К „Ермак“»",
    "title": "Прямая применимость ЭПК-150 на 2ЭС5К",
    "url": "https://npcat.ru/remont2es5k",
    "locator": "операция «Смена электропневматического клапана ЭПК-150»",
}
EPK_CONSTRUCTION_REF = {
    "sourceId": EPK_CONSTRUCTION_ID,
    "document": "Устройство и ремонт электропневматического клапана автостопа ЭПК-150",
    "title": "Конструкция ЭПК-150 и камера выдержки времени",
    "url": "https://scbist.com/zheldor/diplom/d_6.4_epk_150.html",
    "locator": "описание кронштейна и камеры выдержки времени К",
}
KM395_REF = {
    "sourceId": KM395_ID,
    "document": "Технические характеристики крана машиниста 395М-3-01",
    "title": "Кран машиниста 395М-3-01 — технические характеристики точной модели",
    "url": "https://gdzp.ru/store/tormoznoe_oborudovanie/kran-mashinista-395m-3-01/",
    "locator": "таблица «Технические характеристики»",
}

BVR_PARAMS = [
    {"name": "Давление в тормозных цилиндрах — порожний режим", "value": "0.14–0.18", "unit": "MPa", "sourceId": BVR_ID},
    {"name": "Давление в тормозных цилиндрах — средний режим", "value": "0.30–0.34", "unit": "MPa", "sourceId": BVR_ID},
    {"name": "Давление в тормозных цилиндрах — гружёный режим", "value": "0.40–0.45", "unit": "MPa", "sourceId": BVR_ID},
]
KU215_PARAMS = [
    {"name": "Объём буферного резервуара в цепи крана управления", "value": 5, "unit": "L", "sourceId": CHANGES_ID},
    {"name": "Диаметр дросселя выпускного отверстия крана управления", "value": 4.5, "unit": "mm", "sourceId": CHANGES_ID},
]
EPK_PARAMS = [
    {"name": "Объём камеры выдержки времени", "value": 1, "unit": "L", "sourceId": EPK_CONSTRUCTION_ID},
]
KM395_PARAMS = [
    {"name": "Давление сжатого воздуха в питательной магистрали", "value": "0.65–1.0", "unit": "MPa", "sourceId": KM395_ID},
    {"name": "Диапазон давления в тормозной магистрали, регулируемый редуктором", "value": "0.45–0.62", "unit": "MPa", "sourceId": KM395_ID},
    {"name": "Давление настройки редуктора для стендовых испытаний", "value": "0.54–0.55", "unit": "MPa", "sourceId": KM395_ID},
    {"name": "Габаритные размеры", "value": "380×363×269", "unit": "mm", "sourceId": KM395_ID},
    {"name": "Масса, не более", "value": 21, "unit": "kg", "sourceId": KM395_ID},
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
        ("BTO010_BVR_TECH_DATA", BVR_REF),
        ("ERMAK_OVERHAUL_BRAKE_TYPES", OVERHAUL_REF),
        ("ERMAK_BRAKE_PROFILE_CHANGES", CHANGES_REF),
        ("ERMAK_EPK150_REPAIR", EPK_ERMAK_REF),
        ("EPK150_CONSTRUCTION_DATA", EPK_CONSTRUCTION_REF),
        ("KM395M301_EXACT_DATA", KM395_REF),
    ]:
        register_source(reg, key, ref)

    bvr = record(root, "ER-EQ-BR-004")
    ku = record(root, "ER-EQ-BR-009")
    epk = record(root, "ER-EQ-BR-012")
    km = record(root, "ER-EQ-BR-014")

    if bvr.get("name") != "Воздухораспределитель грузового типа" or bvr.get("schemeDesignations") != ["ВРГ"] or bvr.get("modelNames") not in ([], None):
        raise SystemExit("BR-004 identity changed")
    if ku.get("name") != "Кран вспомогательного тормоза" or ku.get("schemeDesignations") != ["КУ"] or ku.get("modelNames") not in ([], None):
        raise SystemExit("BR-009 identity changed")
    if epk.get("name") != "Электропневматический клапан автостопа" or epk.get("schemeDesignations") != ["У25", "ЭПК"] or epk.get("modelNames") not in ([], None):
        raise SystemExit("BR-012 identity changed")
    if km.get("name") != "Кран машиниста №395" or km.get("modelNames") not in ([], None):
        raise SystemExit("BR-014 identity changed")
    if any(x.get("parameters") for x in (bvr, ku, epk, km)):
        raise SystemExit("One of BR-004/BR-009/BR-012/BR-014 already has parameters; review concurrent change")

    neighbor_counts = {
        "ER-EQ-BR-001": 0, "ER-EQ-BR-002": 0, "ER-EQ-BR-003": 0,
        "ER-EQ-BR-005": 0, "ER-EQ-BR-007": 0, "ER-EQ-BR-008": 0,
        "ER-EQ-BR-010": 0, "ER-EQ-BR-011": 0,
        "ER-EQ-PN-006": 5, "ER-EQ-PN-008": 8, "ER-EQ-PN-011": 4, "ER-EQ-CB-003": 7,
    }
    for eid, count in neighbor_counts.items():
        if len(record(root, eid).get("parameters", [])) != count:
            raise SystemExit(f"Neighbor {eid} changed")

    bvr["modelNames"] = ["010.10-3"]
    bvr["purpose"] = "Управление давлением в тормозных цилиндрах локомотива по изменению давления в тормозной магистрали с учётом выбранного грузового режима."
    bvr["parameters"] = BVR_PARAMS
    bvr["sourceRefs"] = unique_refs(bvr.get("sourceRefs", []) + [BVR_REF, OVERHAUL_REF])
    bvr["parameterCoverage"] = {"status": "documented", "count": len(BVR_PARAMS)}
    bvr["notes"] = [
        "На 2ЭС5К/3ЭС5К руководство по ремонту прямо выделяет блок воздухораспределителя 010.10-3; внутри блока применяются магистральная часть 483А.010-01 (вариант 483М.010-01), главная часть 270.023-1 и камера 180.",
        "Параметры карточки относятся к режимной работе блока ВР как установленного узла: порожний, средний и гружёный режимы.",
        "Не переносить массу, габариты или иные паспортные параметры полного воздухораспределителя 483М на блок 010.10-3: компоновка и камера блока отличаются."
    ]

    ku["modelNames"] = ["215-1"]
    ku["purpose"] = "Независимое управление вспомогательным тормозом локомотива из кабины через управляющую полость реле давления."
    ku["parameters"] = KU215_PARAMS
    ku["sourceRefs"] = unique_refs(ku.get("sourceRefs", []) + [OVERHAUL_REF, CHANGES_REF])
    ku["parameterCoverage"] = {"status": "documented", "count": len(KU215_PARAMS)}
    ku["notes"] = [
        "Для 2ЭС5К/3ЭС5К руководство по ремонту прямо указывает кран управления 215-1.",
        "На модернизированном 2ЭС5К между краном 215-1 и управляющей полостью реле давления 404 установлен буферный резервуар 5 л, а на выпускном отверстии крана — дроссель Ø4,5 мм для увеличения времени отпуска вспомогательного тормоза.",
        "Эти два числа — параметры установки 215-1 на Ермаке, а не универсальный паспорт семейства 215; массу, габариты и ступени давления старых исполнений 215 без прямого подтверждения не переносить."
    ]

    epk["modelNames"] = ["ЭПК-150"]
    epk["purpose"] = "Исполнительный прибор автостопа: при срабатывании устройств безопасности обеспечивает предупредительный сигнал и при отсутствии подтверждения бдительности — экстренную разрядку тормозной магистрали."
    epk["parameters"] = EPK_PARAMS
    epk["sourceRefs"] = unique_refs(epk.get("sourceRefs", []) + [EPK_ERMAK_REF, EPK_CONSTRUCTION_REF])
    epk["parameterCoverage"] = {"status": "documented", "count": len(EPK_PARAMS)}
    epk["notes"] = [
        "Прямая применимость ЭПК-150 к 2ЭС5К подтверждена профильным тренажёром ремонта узлов Ермака.",
        "Для базовой конструкции ЭПК-150 камера выдержки времени К имеет объём 1 л.",
        "Точный суффикс исполнения семейства 150И для этой карточки не установлен; поэтому напряжение катушки, масса, габариты и другие вариант-зависимые числа 150И/150И-1/150И-2 сюда не переносятся."
    ]

    km["modelNames"] = ["395М-3-01"]
    km["purpose"] = "Управление автоматическими пневматическими тормозами поезда и локомотива изменением и поддержанием давления в тормозной магистрали."
    km["parameters"] = KM395_PARAMS
    km["sourceRefs"] = unique_refs(km.get("sourceRefs", []) + [OVERHAUL_REF, CHANGES_REF, KM395_REF])
    km["parameterCoverage"] = {"status": "documented", "count": len(KM395_PARAMS)}
    km["notes"] = [
        "Кран 395М-3-01 относится только к профилю brake_395: на 2ЭС5К он применялся вместо крана 130.1.01.50 В на соответствующих сериях/модификациях.",
        "Паспортные параметры взяты для точной модели 395М-3-01, а не для всего семейства №395.",
        "Не переносить эти значения на 395М-4/-5 или на профили с краном №130 без отдельного подтверждения."
    ]

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path):
    root = read_gz(path)
    bvr = article(root, "ER-EQ-BR-004")
    ku = article(root, "ER-EQ-BR-009")
    epk = article(root, "ER-EQ-BR-012")
    km = article(root, "ER-EQ-BR-014")

    bvr["summary"] = "Блок воздухораспределителя 010.10-3 (ВРГ) формирует управляющее давление автоматического пневматического тормоза в зависимости от разрядки тормозной магистрали и выбранного грузового режима."
    bvr["principle"] = "Магистральная и главная части воздухораспределителя реагируют на изменение давления в тормозной магистрали; через камеру и переключатель режимов формируется давление, передаваемое к управляющим полостям реле давления, которые наполняют тормозные цилиндры."
    bvr["keyParameters"] = kb_params(BVR_PARAMS, "Блок воздухораспределителя 010.10-3 в составе тормозного оборудования грузового типа 2ЭС5К/3ЭС5К.")
    bvr["normalState"] = [
        "Давление в тормозных цилиндрах соответствует выбранному порожнему, среднему или гружёному режиму.",
        "После отпуска давление в тормозных цилиндрах снижается, устойчивого остаточного торможения нет.",
        "Соединения блока герметичны, а переключатель режимов фиксируется в требуемом положении."
    ]
    bvr["deviationSigns"] = [
        "Давление тормозных цилиндров не соответствует выбранному режиму либо заметно отличается между одинаковыми секциями.",
        "После команды отпуска сохраняется давление в тормозных цилиндрах или отпуск происходит ненормально медленно.",
        "Есть утечки, неисправность переключателя режимов или нестабильная работа магистральной/главной части."
    ]
    bvr["sourceRefs"] = unique_strings(bvr.get("sourceRefs", []) + [BVR_ID, OVERHAUL_ID])
    bvr["variantRules"] = unique_strings(bvr.get("variantRules", []) + [
        "010.10-3 считать самостоятельной блочной компоновкой; не подменять её паспортом полного воздухораспределителя 483М.",
        "483А.010-01 и 483М.010-01 указываются как варианты магистральной части внутри блока; отличия вариантов не смешивать без отдельного документа."
    ])

    ku["summary"] = "Кран управления 215-1 (КУ) — орган независимого вспомогательного тормоза; на 2ЭС5К его выпускная цепь дополнена буферным резервуаром и дросселем для формирования отпуска."
    ku["principle"] = "Кран задаёт давление в управляющей полости реле давления вспомогательного тормоза. При отпуске воздух выходит через выпуск крана; буферный резервуар 5 л и дроссель Ø4,5 мм в компоновке 2ЭС5К замедляют изменение давления и увеличивают время отпуска."
    ku["keyParameters"] = kb_params(KU215_PARAMS, "Параметры установки крана управления 215-1 на 2ЭС5К; это не универсальный паспорт семейства 215.")
    ku["normalState"] = [
        "Вспомогательный тормоз плавно набирает и снижает давление в соответствии с положением крана.",
        "После отпуска давление снижается без зависания и без постоянной утечки через соединения.",
        "Буферный резервуар и дроссель выпускной цепи не засорены и не разгерметизированы."
    ]
    ku["deviationSigns"] = [
        "Вспомогательный тормоз не набирает давление, отпускает слишком быстро/медленно или сохраняет остаточное давление.",
        "Есть устойчивая утечка через кран, резервуар, дроссель или соединения.",
        "Ход рукоятки не соответствует ожидаемому изменению тормозного давления."
    ]
    ku["sourceRefs"] = unique_strings(ku.get("sourceRefs", []) + [OVERHAUL_ID, CHANGES_ID])
    ku["variantRules"] = unique_strings(ku.get("variantRules", []) + [
        "Числа 5 л и Ø4,5 мм относятся к компоновке 215-1 на 2ЭС5К и не являются паспортными параметрами самого крана.",
        "Паспортные данные старого крана 215 не переносить на 215-1 без прямого подтверждения."
    ])

    epk["summary"] = "ЭПК-150 (У25/ЭПК) — электропневматический клапан автостопа, связывающий устройства безопасности с пневматическим экстренным торможением."
    epk["principle"] = "При штатном подтверждении бдительности ЭПК сохраняет тормозную магистраль заряженной. При срабатывании автостопа и отсутствии требуемого действия машиниста клапан через срывной орган разряжает тормозную магистраль; камера выдержки времени участвует во временной логике работы."
    epk["keyParameters"] = kb_params(EPK_PARAMS, "Базовая конструкция ЭПК-150; вариант-зависимые электрические данные семейства 150И сознательно исключены.")
    epk["normalState"] = [
        "При исправных устройствах безопасности и подтверждённой бдительности тормозная магистраль через ЭПК не разряжается.",
        "Предупредительная и тормозная фазы автостопа отрабатывают последовательно и без заеданий.",
        "Камера выдержки времени, срывной клапан, замок и пневматические соединения герметичны."
    ]
    epk["deviationSigns"] = [
        "Самопроизвольная разрядка тормозной магистрали либо отсутствие разрядки при требуемом срабатывании автостопа.",
        "Нарушена выдержка времени, свисток/срывной клапан работают нестабильно или механизм заедает.",
        "Есть утечка воздуха, повреждение замка, электромагнита или пневматических соединений."
    ]
    epk["sourceRefs"] = unique_strings(epk.get("sourceRefs", []) + [EPK_ERMAK_ID, EPK_CONSTRUCTION_ID])
    epk["variantRules"] = unique_strings(epk.get("variantRules", []) + [
        "Для карточки подтверждена модель ЭПК-150, но точный суффикс семейства 150И на данном профиле не установлен.",
        "Не фиксировать напряжение, ток, массу или габариты вариантов 150И/150И-1/150И-2 как параметры Ермака без прямой идентификации исполнения."
    ])

    km["summary"] = "395М-3-01 — профильный вариант крана машиниста №395 для части 2ЭС5К, управляющий зарядкой, служебным и экстренным торможением через тормозную магистраль."
    km["principle"] = "Положением рукоятки кран соединяет тормозную магистраль с питательной магистралью, перекрывает её либо сообщает с атмосферой; редуктор поддерживает заданное поездное давление."
    km["keyParameters"] = kb_params(KM395_PARAMS, "Точная модель 395М-3-01, профиль brake_395 на 2ЭС5К.")
    km["normalState"] = [
        "В поездном положении редуктор устойчиво поддерживает установленное давление тормозной магистрали.",
        "Ступени служебного торможения и отпуск выполняются плавно, без самопроизвольного изменения давления.",
        "Кран, редуктор, микровыключатель и пневматические соединения герметичны и механически исправны."
    ]
    km["deviationSigns"] = [
        "Давление тормозной магистрали не поддерживается, самопроизвольно растёт/снижается или не соответствует положению рукоятки.",
        "Нарушен отпуск или служебное торможение, есть заедание рукоятки либо нестабильная работа редуктора.",
        "Обнаружена утечка воздуха, неисправность контактов или повреждение корпуса/соединений."
    ]
    km["sourceRefs"] = unique_strings(km.get("sourceRefs", []) + [OVERHAUL_ID, CHANGES_ID, KM395_ID])
    km["variantRules"] = unique_strings(km.get("variantRules", []) + [
        "395М-3-01 относится к профилю brake_395 и не применяется к карточкам профилей brake_130_uktol / brake_130_2_uktol.",
        "Не переносить паспортные значения 395М-3-01 на 395М-4, 395М-5 и другие исполнения семейства №395."
    ])

    for a, params in ((bvr, BVR_PARAMS), (ku, KU215_PARAMS), (epk, EPK_PARAMS), (km, KM395_PARAMS)):
        a["atlasData"]["parameterCoverage"] = {"status": "documented", "count": len(params)}
        a["knowledgeCoverage"]["parameters"] = "documented"
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / "ermak_equipment.json.gz")
    patch_knowledge(base / "ermak_knowledge.json.gz")
print("Enriched Ermak BR-004, BR-009, BR-012 and BR-014")
