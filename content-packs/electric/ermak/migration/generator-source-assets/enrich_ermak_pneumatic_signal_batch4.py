#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path("app/src/main/assets/technical"), Path("patch/app/src/main/assets/technical")]
TARGETS = {
    "ER-EQ-PN-006": "ER-KB-EQ-ER-EQ-PN-006",
    "ER-EQ-PN-008": "ER-KB-EQ-ER-EQ-PN-008",
    "ER-EQ-PN-011": "ER-KB-EQ-ER-EQ-PN-011",
    "ER-EQ-CB-003": "ER-KB-EQ-ER-EQ-CB-003",
}
RE4_ID = "ER-SRC-005"
RE8_ID = "ER-SRC-086"
KR1_ID = "ER-SRC-091"
KP29_ID = "ER-SRC-092"
KT_S17_ID = "ER-SRC-093"
TS22_ID = "ER-SRC-094"

KR1_REF = {
    "sourceId": KR1_ID,
    "document": "Электровоз ВЛ85. Руководство по эксплуатации",
    "title": "Разгрузочный клапан КР-1 — назначение и технические данные того же типа аппарата",
    "url": "https://poezdvl.com/vl85/vl85_65.html",
    "locator": "раздел «Разгрузочный клапан КР-1»",
}
KP29_REF = {
    "sourceId": KP29_ID,
    "document": "Учебно-технический материал по аппаратам электровоза 2ЭС5К",
    "title": "КП-29-01 — назначение и технические характеристики",
    "url": "https://studopedia.net/20_24291_v-atmosferu-a-sledovatelno-i-ne-razblokiruet.html",
    "locator": "раздел «Клапан продувки КП-29-01»",
}
KT_S17_REF = {
    "sourceId": KT_S17_ID,
    "document": "ИДМБ.661142.004-01 РЭ4, электровоз ЭП1М (ЭП1П)",
    "title": "КТ-20-02 и С-17 — технические характеристики аппаратов того же типа",
    "url": "https://djvu.online/file/TVgYn3LTUveDJ",
    "locator": "разделы 76 и 84",
}
TS22_REF = {
    "sourceId": TS22_ID,
    "document": "ЗАО «Электромагнит», технические данные изделия ТС-22",
    "title": "Ревун ТС-22 — основные технические характеристики",
    "url": "https://vv32.ru/product/ts-22-2/",
    "locator": "таблица основных технических характеристик",
}

KR_PARAMS = [
    {"name": "Номинальное напряжение электромагнитного вентиля", "value": 50, "unit": "V", "sourceId": KR1_ID},
    {"name": "Максимальное давление сжатого воздуха", "value": 0.9, "unit": "MPa", "sourceId": KR1_ID},
    {"name": "Сопротивление катушки вентиля при 20 °C", "value": "173 (+12/-8)", "unit": "Ohm", "sourceId": KR1_ID},
    {"name": "Время разгрузки магистрали объёмом не более 8 л", "value": 7, "unit": "s max", "sourceId": KR1_ID},
    {"name": "Масса", "value": 4.3, "unit": "kg", "sourceId": KR1_ID},
]
KP_PARAMS = [
    {"name": "Номинальное напряжение вентиля", "value": 50, "unit": "V", "sourceId": KP29_ID},
    {"name": "Номинальный ток", "value": 0.21, "unit": "A", "sourceId": KP29_ID},
    {"name": "Минимальный ток срабатывания вентиля", "value": 0.15, "unit": "A", "sourceId": KP29_ID},
    {"name": "Сопротивление катушки вентиля при 20 °C", "value": "173 (+12/-8)", "unit": "Ohm", "sourceId": KP29_ID},
    {"name": "Сопротивление нагревателя при 20 °C", "value": "29.2±2", "unit": "Ohm", "sourceId": KP29_ID},
    {"name": "Рабочее давление сжатого воздуха", "value": "0.75–0.9", "unit": "MPa", "sourceId": KP29_ID},
    {"name": "Ход клапана, не менее", "value": 3, "unit": "mm", "sourceId": KP29_ID},
    {"name": "Масса", "value": 6.0, "unit": "kg", "sourceId": KP29_ID},
]
KT_PARAMS = [
    {"name": "Номинальное напряжение вентиля", "value": 50, "unit": "V", "sourceId": KT_S17_ID},
    {"name": "Номинальный ток вентиля", "value": 0.13, "unit": "A", "sourceId": KT_S17_ID},
    {"name": "Сопротивление катушки при 20 °C", "value": 286, "unit": "Ohm", "sourceId": KT_S17_ID},
    {"name": "Время опускания токоприёмника", "value": "3.5–6", "unit": "s", "sourceId": KT_S17_ID},
]
SOUND_PARAMS = [
    {"name": "С-17 — номинальное напряжение вентиля", "value": 50, "unit": "V", "sourceId": KT_S17_ID},
    {"name": "С-17 — рабочее давление сжатого воздуха", "value": "0.75–0.9", "unit": "MPa", "sourceId": KT_S17_ID},
    {"name": "ТС-22 — частота основного тона тифона", "value": "370±10", "unit": "Hz", "sourceId": TS22_ID},
    {"name": "ТС-22 — частота основного тона свистка", "value": "650±50", "unit": "Hz", "sourceId": TS22_ID},
    {"name": "ТС-22 — рабочее давление сжатого воздуха", "value": "0.75–0.9", "unit": "MPa", "sourceId": TS22_ID},
    {"name": "ТС-22 — габаритные размеры", "value": "103×217×134", "unit": "mm", "sourceId": TS22_ID},
    {"name": "ТС-22 — масса (допуск ±5%)", "value": 5.0, "unit": "kg", "sourceId": TS22_ID},
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
        ("KR1_SAME_TYPE_MANUAL", KR1_REF),
        ("KP2901_2ES5K_TECH_DATA", KP29_REF),
        ("KT2002_S17_SAME_TYPE_FACTORY_RE", KT_S17_REF),
        ("TS22_MANUFACTURER_DATA", TS22_REF),
    ]:
        register_source(reg, key, ref)
    re4 = source_by_id(reg, RE4_ID)
    re8 = source_by_id(reg, RE8_ID)

    kr = record(root, "ER-EQ-PN-006")
    kp = record(root, "ER-EQ-PN-008")
    kt = record(root, "ER-EQ-PN-011")
    snd = record(root, "ER-EQ-CB-003")

    if kr.get("modelNames") != ["КР-1"] or kr.get("schemeDesignations") != ["У5"]:
        raise SystemExit("PN-006 identity changed")
    if kp.get("modelNames") != ["КП-29-01"] or kp.get("schemeDesignations") != ["У21", "У22", "У23", "У24"]:
        raise SystemExit("PN-008 identity changed")
    if kt.get("modelNames") != ["КТ-20-02"] or kt.get("schemeDesignations") != ["У10"]:
        raise SystemExit("PN-011 identity changed")
    if snd.get("modelNames") != ["С-17", "ТС-22"] or snd.get("schemeDesignations"):
        raise SystemExit("CB-003 identity changed")
    if any(x.get("parameters") for x in (kr, kp, kt, snd)):
        raise SystemExit("One of PN-006/PN-008/PN-011/CB-003 already has parameters; review concurrent change")

    neighbor_counts = {
        "ER-EQ-PN-003": 2, "ER-EQ-PN-004": 1, "ER-EQ-PN-005": 0,
        "ER-EQ-PN-007": 0, "ER-EQ-PN-009": 0, "ER-EQ-PN-010": 3,
        "ER-EQ-PN-012": 1, "ER-EQ-CB-001": 0, "ER-EQ-CB-002": 0, "ER-EQ-CB-004": 0,
    }
    for eid, count in neighbor_counts.items():
        if len(record(root, eid).get("parameters", [])) != count:
            raise SystemExit(f"Neighbor {eid} changed")

    kr["purpose"] = "Разгрузка участка нагнетательной магистрали между компрессором и обратным клапаном после остановки, чтобы следующий пуск компрессора происходил без избыточной противодавлением нагрузки."
    kr["parameters"] = KR_PARAMS
    kr["sourceRefs"] = unique_refs(kr.get("sourceRefs", []) + [KR1_REF, re8])
    kr["parameterCoverage"] = {"status": "documented", "count": len(KR_PARAMS)}
    kr["notes"] = [
        "На 2ЭС5К/3ЭС5К РЭ4 прямо указан клапан КР-1, а РЭ8 обслуживает КР-1 совместно с другими электропневматическими клапанами.",
        "Паспортные числа добавлены по аппарату КР-1 того же типа; отдельное исполнение КР-1-02 не считается тем же вариантом и его параметры автоматически не переносятся.",
        "Нормальное состояние предполагает закрытие после разгрузки: постоянный сброс воздуха после завершения цикла не является штатным режимом."
    ]

    kp["purpose"] = "Дистанционная продувка конденсата из главных резервуаров и связанных точек сбора конденсата пневмосистемы."
    kp["parameters"] = KP_PARAMS
    kp["sourceRefs"] = unique_refs(kp.get("sourceRefs", []) + [KP29_REF, re8])
    kp["parameterCoverage"] = {"status": "documented", "count": len(KP_PARAMS)}
    kp["notes"] = [
        "На каждой секции базового профиля применяются четыре КП-29-01 в схемных позициях У21–У24; количество сохраняется как atlasData, а не как паспорт одного клапана.",
        "Напряжение питания нагревателя в открытой копии источника имеет неоднозначное OCR-представление и сознательно не включено в параметры.",
        "РЭ8 требует контроля герметичности запорного клапана; устойчивый сброс после снятия команды является признаком отклонения."
    ]

    kt["purpose"] = "Электропневматическое управление токоприёмником и регулирование времени его опускания; время подъёма задаётся отдельным калибровочным клапаном 5ТН.456.129."
    kt["parameters"] = KT_PARAMS
    kt["sourceRefs"] = unique_refs(kt.get("sourceRefs", []) + [KT_S17_REF, re8])
    kt["parameterCoverage"] = {"status": "documented", "count": len(KT_PARAMS)}
    kt["notes"] = [
        "КТ-20-02 прямо указан в РЭ4 2ЭС5К/3ЭС5К и отдельно обслуживается в РЭ8.",
        "Масса и рабочее давление не внесены: для КТ-20-02 в открытых источниках разных применений встречаются расходящиеся значения, а точный паспорт исполнения Ермака не подтверждён.",
        "Время подъёма токоприёмника не приписано КТ-20-02: в руководстве того же аппарата его регулирует отдельный калибровочный клапан 5ТН.456.129."
    ]

    snd["purpose"] = "Подача звуковых сигналов из кабины: С-17 формирует отдельный электропневматический свисток, ТС-22 — основные и маневровые сигналы тифоном/свистком."
    snd["parameters"] = SOUND_PARAMS
    snd["sourceRefs"] = unique_refs(snd.get("sourceRefs", []) + [KT_S17_REF, TS22_REF, re8])
    snd["parameterCoverage"] = {"status": "documented", "count": len(SOUND_PARAMS)}
    snd["notes"] = [
        "С-17 и ТС-22 — разные аппараты в одной карточке; каждый параметр подписан моделью и не считается общим для комплекта.",
        "Для С-17 не добавлены ток, масса и частотная характеристика: открытые руководства того же типа дают различающиеся значения, поэтому без паспорта исполнения Ермака их перенос был бы недоказанным.",
        "Для ТС-22 использованы данные производителя точной модели; РЭ8 Ермака отдельно предусматривает обслуживание С-17 и ТС-22."
    ]

    stats = root.get("statistics", {})
    if stats:
        stats["recordsWithParameters"] = sum(bool(r.get("parameters")) for r in root["records"])
        stats["recordsWithoutParameters"] = len(root["records"]) - stats["recordsWithParameters"]
    write_gz(path, root)


def patch_knowledge(path):
    root = read_gz(path)
    kr = article(root, "ER-EQ-PN-006")
    kp = article(root, "ER-EQ-PN-008")
    kt = article(root, "ER-EQ-PN-011")
    snd = article(root, "ER-EQ-CB-003")

    kr["summary"] = "КР-1 (У5) — разгрузочный клапан компрессора, снимающий давление с нагнетательного участка после остановки для облегчения следующего пуска."
    kr["principle"] = "После остановки компрессора электропневматический привод кратковременно открывает сообщение разгружаемого участка с атмосферой. По мере падения давления клапан возвращается в закрытое положение, поэтому следующий пуск выполняется на разгруженный участок."
    kr["keyParameters"] = kb_params(KR_PARAMS, "КР-1 базового профиля 2ЭС5К/3ЭС5К; значения КР-1-02 не смешивать с базовым КР-1.")
    kr["normalState"] = [
        "После остановки компрессора нагнетательный участок разгружается и клапан затем закрывается.",
        "При работающем компрессоре отсутствует постоянный сброс воздуха через КР-1.",
        "Корпус, электромагнитный привод и пневматические соединения не имеют повреждений и недопустимой утечки."
    ]
    kr["deviationSigns"] = [
        "После остановки компрессора участок не разгружается, и следующий пуск происходит под заметной пневматической нагрузкой.",
        "Клапан остаётся открытым либо через него продолжается устойчивый сброс воздуха после завершения разгрузки.",
        "Есть заедание механизма, повреждение привода или негерметичность соединений."
    ]
    kr["sourceRefs"] = unique_strings(kr.get("sourceRefs", []) + [RE4_ID, RE8_ID, KR1_ID])
    kr["variantRules"] = unique_strings(kr.get("variantRules", []) + ["КР-1-02 считать отдельным исполнением; его напряжение и другие паспортные значения не переносить на КР-1 без прямого подтверждения."])

    kp["summary"] = "КП-29-01 (У21–У24) — электропневматические клапаны дистанционной продувки конденсата из резервуаров и связанных точек пневмосистемы."
    kp["principle"] = "При подаче команды электромагнитный привод открывает клапан и выпускает накопленный конденсат вместе с частью сжатого воздуха; после снятия команды запорный орган должен герметично закрыться. В конструкции предусмотрен нагреватель."
    kp["keyParameters"] = kb_params(KP_PARAMS, "КП-29-01 базового профиля 2ЭС5К/3ЭС5К, схемные позиции У21–У24.")
    kp["normalState"] = [
        "Каждый клапан уверенно срабатывает по команде и после неё закрывается без устойчивой утечки.",
        "Конденсат удаляется из закреплённой за клапаном точки, а в резервуарах не наблюдается его ненормальное накопление.",
        "Катушка, нагреватель, корпус и пневматические соединения не имеют признаков перегрева, повреждения или разгерметизации."
    ]
    kp["deviationSigns"] = [
        "При команде продувки отсутствует выход воздуха/конденсата либо клапан срабатывает нестабильно.",
        "После снятия команды сохраняется утечка через запорный орган.",
        "Наблюдается ненормальное накопление конденсата, повреждение нагревателя/катушки или разгерметизация соединений."
    ]
    kp["sourceRefs"] = unique_strings(kp.get("sourceRefs", []) + [RE4_ID, RE8_ID, KP29_ID])
    kp["variantRules"] = unique_strings(kp.get("variantRules", []) + ["Не использовать неоднозначно распознанное значение напряжения нагревателя из открытой копии без сверки с оригиналом документа."])

    kt["summary"] = "КТ-20-02 (У10) — электропневматический клапан управления токоприёмником, отвечающий за его опускание; подъём регулируется отдельным калибровочным клапаном."
    kt["principle"] = "Электромагнитный клапан переключает подачу/выпуск сжатого воздуха в пневмопривод токоприёмника и формирует требуемый режим опускания. Отдельный калибровочный клапан 5ТН.456.129 ограничивает скорость наполнения при подъёме."
    kt["keyParameters"] = kb_params(KT_PARAMS, "КТ-20-02 базового профиля 2ЭС5К/3ЭС5К; числовые данные подтверждены для того же типа аппарата, спорные масса и рабочее давление исключены.")
    kt["normalState"] = [
        "Клапан герметичен в невозбуждённом состоянии и устойчиво переключает пневмопривод по команде.",
        "Токоприёмник опускается плавно, без зависания и ненормального замедления.",
        "Уплотнения, подвижные детали и пневматические соединения не имеют повреждений или устойчивой утечки."
    ]
    kt["deviationSigns"] = [
        "Токоприёмник не опускается по команде, опускается заметно медленнее штатного или движение становится неустойчивым.",
        "Есть постоянная утечка воздуха через клапан или соединения.",
        "Электромагнитный привод не переключает клапан либо запорный орган не обеспечивает герметичность."
    ]
    kt["sourceRefs"] = unique_strings(kt.get("sourceRefs", []) + [RE4_ID, RE8_ID, KT_S17_ID])
    kt["variantRules"] = unique_strings(kt.get("variantRules", []) + [
        "Массу и рабочее давление КТ-20-02 не фиксировать как паспорт Ермака без отдельного подтверждения: открытые данные разных применений расходятся.",
        "Время подъёма относится к системе с калибровочным клапаном 5ТН.456.129 и не считается самостоятельным параметром КТ-20-02."
    ])

    snd["summary"] = "С-17 и ТС-22 — комплект электропневматических звуковых аппаратов головной секции для подачи предупредительных, основных и маневровых сигналов."
    snd["principle"] = "Электромагнитные органы управления подают сжатый воздух к звуковым элементам. С-17 работает как отдельный свисток, а ТС-22 содержит каналы тифона и свистка с различной основной частотой звучания."
    snd["keyParameters"] = kb_params(SOUND_PARAMS, "Параметры строго разделены по С-17 и ТС-22; не переносить значения между аппаратами или иными исполнениями.")
    snd["normalState"] = [
        "С-17 и оба звуковых канала ТС-22 срабатывают по соответствующей команде и дают устойчивый различимый сигнал.",
        "После снятия команды подача воздуха прекращается, постоянной утечки через аппарат нет.",
        "Корпуса, мембрана ТС-22, крепёж, электромагнитные органы и пневматические соединения не имеют повреждений."
    ]
    snd["deviationSigns"] = [
        "Один из сигналов отсутствует, звучит заметно слабее/нестабильнее либо не соответствует ожидаемому каналу.",
        "После снятия команды продолжается подача воздуха или слышна устойчивая утечка.",
        "Есть повреждение мембраны, корпуса, электромагнитного привода, крепежа или пневматических соединений."
    ]
    snd["sourceRefs"] = unique_strings(snd.get("sourceRefs", []) + [RE4_ID, RE8_ID, KT_S17_ID, TS22_ID])
    snd["variantRules"] = unique_strings(snd.get("variantRules", []) + [
        "Параметры С-17 и ТС-22 хранить раздельно внутри сводной карточки.",
        "Для С-17 ток, масса и частотные данные не фиксировать как параметры Ермака без паспорта конкретного исполнения из-за расхождений между открытыми руководствами."
    ])

    for a, params in ((kr, KR_PARAMS), (kp, KP_PARAMS), (kt, KT_PARAMS), (snd, SOUND_PARAMS)):
        a["atlasData"]["parameterCoverage"] = {"status": "documented", "count": len(params)}
        a["knowledgeCoverage"]["parameters"] = "documented"
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / "ermak_equipment.json.gz")
    patch_knowledge(base / "ermak_knowledge.json.gz")
print("Enriched Ermak PN-006, PN-008, PN-011 and CB-003")
