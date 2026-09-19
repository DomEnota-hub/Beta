#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-TR-004'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-TR-004'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
RE4_SOURCE_ID = 'ER-SRC-058'
MAINT_SOURCE_ID = 'ER-SRC-059'
TECH_SOURCE_ID = 'ER-SRC-060'
CROSSCHECK_SOURCE_ID = 'ER-SRC-061'

RE4_URL = 'https://rcit.su/techinfoV54.html'
MAINT_URL = 'https://rcit.su/techinfoV58.html'
TECH_URL = 'https://studfile.net/preview/14121981/page%3A3/'
CROSSCHECK_URL = 'https://lektsii.org/17-31975.html'

PARAMETERS = [
    {'name': 'Номинальное напряжение главной цепи', 'value': 1250, 'unit': 'V', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Номинальный ток главной цепи', 'value': 1000, 'unit': 'A', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Номинальный ток уставки', 'value': '2000 (+200/-100)', 'unit': 'A', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Пределы регулирования тока уставки', 'value': '1500–2500', 'unit': 'A', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Собственное время отключения при скорости нарастания тока 150 А/мс, не более', 'value': 3, 'unit': 'ms', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Номинальное напряжение цепи управления постоянного тока', 'value': 50, 'unit': 'V', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Номинальный ток удерживающей катушки', 'value': 0.5, 'unit': 'A', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Номинальное давление сжатого воздуха привода', 'value': 0.5, 'unit': 'MPa', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Масса', 'value': 79.5, 'unit': 'kg', 'sourceId': TECH_SOURCE_ID},
]

RE4_REF = {
    'sourceId': RE4_SOURCE_ID,
    'document': 'ИДМБ.661142.009РЭ4, электровоз магистральный 2ЭС5К (3ЭС5К)',
    'title': 'Выключатель быстродействующий ВБ-8 — штатный электрический аппарат 2ЭС5К/3ЭС5К',
    'url': RE4_URL,
    'locator': 'раздел 3 «Выключатель быстродействующий ВБ-8»',
}
MAINT_REF = {
    'sourceId': MAINT_SOURCE_ID,
    'document': 'ИДМБ.661142.009РЭ8, электровоз магистральный 2ЭС5К (3ЭС5К)',
    'title': 'Выключатель быстродействующий ВБ-8 — техническое обслуживание и текущий ремонт',
    'url': MAINT_URL,
    'locator': 'пп. 4.4.3, 6.4.6, 7.4.4 и 8.4.9',
}
TECH_REF = {
    'sourceId': TECH_SOURCE_ID,
    'document': 'Учебные технические материалы по электрооборудованию 2ЭС5К/3ЭС5К',
    'title': 'Выключатель быстродействующий ВБ-8 — назначение, технические характеристики, устройство и принцип работы',
    'url': TECH_URL,
    'locator': 'раздел «Выключатель быстродействующий ВБ-8»',
}
CROSSCHECK_REF = {
    'sourceId': CROSSCHECK_SOURCE_ID,
    'document': 'Учебно-техническое описание быстродействующего выключателя ВБ-8',
    'title': 'ВБ-8 — технические параметры и принцип действия',
    'url': CROSSCHECK_URL,
    'locator': 'таблица «Технические параметры ВБ-8» и раздел «Принцип работы ВБ-8»',
}


def read_gz(path: Path):
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        return json.load(fh)


def write_gz(path: Path, payload):
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='', mode='wb', fileobj=out, mtime=0, compresslevel=9) as gz:
            gz.write(raw)


def unique_refs(items):
    result, seen = [], set()
    for item in items:
        key = item.get('sourceId') if isinstance(item, dict) else str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def to_kb_parameters(items):
    return [
        {
            'name': p['name'],
            'value': p['value'],
            'unit': p['unit'],
            'applicability': (
                'ВБ-8; аппарат подтверждён заводскими РЭ 2ЭС5К/3ЭС5К. '
                'Числовое значение подтверждено открытыми техническими материалами по ВБ-8; '
                'при замене/модернизации фактическое исполнение сверять по маркировке и документации аппарата.'
            ),
            'status': 'BASE_CONFIRMED',
            'sourceRefs': [p['sourceId']],
        }
        for p in items
    ]


def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault('sourceRegistry', {})
    registry['VB8_ERMAK_RE4'] = RE4_REF
    registry['VB8_ERMAK_MAINTENANCE'] = MAINT_REF
    registry['VB8_TECHNICAL_DATA'] = TECH_REF
    registry['VB8_TECHNICAL_CROSSCHECK'] = CROSSCHECK_REF

    matches = [r for r in root['records'] if r.get('id') == EQUIPMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f'Expected exactly one {EQUIPMENT_ID} record, found {len(matches)}')
    record = matches[0]
    if 'ВБ-8' not in record.get('modelNames', []):
        raise SystemExit(f'Unexpected modelNames for {EQUIPMENT_ID}: {record.get("modelNames")!r}')
    designations = set(record.get('schemeDesignations', []))
    if not {'QF11', 'QF12'} <= designations:
        raise SystemExit(f'Expected QF11/QF12 for {EQUIPMENT_ID}, found {sorted(designations)}')

    record['purpose'] = (
        'Оперативное включение и отключение силовых цепей тяговых двигателей, а также их быстродействующая '
        'защита от аварийных сверхтоков и токов короткого замыкания в режимах тяги и рекуперативного торможения.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(record.get('sourceRefs', []) + [RE4_REF, MAINT_REF, TECH_REF, CROSSCHECK_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}

    notes = [n for n in record.get('notes', []) if not n.startswith('ВБ-8:')]
    notes += [
        'ВБ-8: на базовой секции 2ЭС5К/3ЭС5К быстродействующие выключатели тяговых двигателей обозначены QF11 и QF12.',
        'Выключатель поляризованного действия: ток главной цепи проходит через размагничивающий виток; при достижении тока уставки встречный магнитный поток уменьшает удержание якоря, после чего отключающие пружины размыкают главные контакты.',
        'Электрическая дуга при отключении гасится в лабиринтно-щелевой дугогасительной камере с магнитным дутьём; включение выполняется пневматическим приводом с электромагнитным вентилем.',
        'Сопротивление удерживающей катушки намеренно не занесено в параметры: открытые технические источники дают расходящиеся значения 85,2 и 90 Ом; до первичного паспорта это значение не считать подтверждённым.',
    ]
    record['notes'] = notes

    stats = root.get('statistics', {})
    if stats:
        stats['recordsWithParameters'] = sum(bool(r.get('parameters')) for r in root['records'])
        stats['recordsWithoutParameters'] = len(root['records']) - stats['recordsWithParameters']
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    matches = [a for a in root['articles'] if a.get('id') == ARTICLE_ID or a.get('equipmentId') == EQUIPMENT_ID]
    by_id = {a.get('id'): a for a in matches}
    if len(by_id) != 1:
        raise SystemExit(f'Expected exactly one article for {EQUIPMENT_ID}, found {list(by_id)}')
    article = next(iter(by_id.values()))

    article['summary'] = (
        'ВБ-8 (QF11/QF12) коммутирует силовые цепи тяговых двигателей и быстро отключает их при аварийном '
        'сверхтоке в тяге и рекуперативном торможении.'
    )
    article['principle'] = (
        'ВБ-8 является поляризованным быстродействующим выключателем. Удерживающая катушка создаёт магнитный поток, '
        'удерживающий якорь во включённом состоянии, а ток главной цепи через размагничивающий виток создаёт встречный поток. '
        'Когда ток достигает уставки, результирующий поток уменьшается, якорь освобождается и отключающие пружины размыкают '
        'главные контакты. Возникшая дуга вытягивается магнитным полем и гасится в дугогасительной камере. '
        'Оперативное отключение выполняется снятием напряжения с удерживающей катушки, включение — пневматическим приводом.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Главные контакты чистые и гладкие, без выраженных наплывов металла и кратера; профиль контактов не нарушен.',
        'Зазор δ между упорами контактного рычага и якоря при контроле износа главных контактов составляет не менее 2 мм.',
        'Изоляционные поверхности чистые и без видимых повреждений; разъёмные контактные соединения и фиксаторы наконечников надёжны.',
        'Пневматический привод не имеет слышимых утечек воздуха, подвижные части работают свободно, переключения чёткие.',
        'Дугогасительная камера и её элементы без недопустимых оплавлений, нагара и разрушения; выключатель соответствует контрольным нормам ремонта.',
    ]
    article['deviationSigns'] = [
        'Подгар, наплывы металла, кратер или выраженный износ главных контактов; зазор δ менее 2 мм.',
        'Повреждение или загрязнение изоляционных поверхностей, ослабление контактных соединений либо фиксации наконечников.',
        'Утечка сжатого воздуха, повреждение цилиндра, поршня или манжеты пневмопривода, нечёткое либо затруднённое переключение.',
        'Оплавление, сильный нагар, повреждение резисторных или других элементов дугогасительной камеры.',
        'Самопроизвольное отключение под нагрузкой или отклонение тока уставки от установленного диапазона требуют проверки регулировки и механизма выключателя.',
    ]

    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, RE4_SOURCE_ID, MAINT_SOURCE_ID, TECH_SOURCE_ID, CROSSCHECK_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)

    rules = [r for r in article.get('variantRules', []) if not r.startswith('ВБ-8:')]
    rules.append(
        'ВБ-8: применение аппарата и обозначения QF11/QF12 подтверждены для базового 2ЭС5К/3ЭС5К. '
        'Паспортные числовые значения в карточке собраны из согласующихся открытых технических материалов по ВБ-8, '
        'а эксплуатационные критерии — из ИДМБ.661142.009РЭ8. Сопротивление удерживающей катушки не приводить как '
        'подтверждённое паспортное значение до сверки первичной документации, поскольку открытые источники расходятся.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak VB-8 high-speed breaker reference enriched in app and patch mirrors')
