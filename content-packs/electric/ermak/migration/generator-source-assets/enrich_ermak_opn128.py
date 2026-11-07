#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-TR-002'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-TR-002'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
FACTORY_SOURCE_ID = 'ER-SRC-053'
TU_SOURCE_ID = 'ER-SRC-054'

FACTORY_URL = 'https://djvu.online/file/TVgYn3LTUveDJ'
TU_URL = 'https://electrosfera.ru/wp-content/uploads/2016/03/2.4.5.pdf'

PARAMETERS = [
    {
        'name': 'Номинальное напряжение',
        'value': 1.28,
        'unit': 'kV',
        'sourceId': FACTORY_SOURCE_ID,
    },
    {
        'name': 'Наибольшее рабочее напряжение (действующее значение)',
        'value': 1.56,
        'unit': 'kV',
        'sourceId': FACTORY_SOURCE_ID,
    },
    {
        'name': 'Остающееся напряжение при импульсном токе 125/250 мкс, 1000 А, не более',
        'value': 3.6,
        'unit': 'kV',
        'sourceId': FACTORY_SOURCE_ID,
    },
    {
        'name': 'Высота',
        'value': 145,
        'unit': 'mm',
        'sourceId': TU_SOURCE_ID,
    },
    {
        'name': 'Масса',
        'value': '3.5±0.3',
        'unit': 'kg',
        'sourceId': FACTORY_SOURCE_ID,
    },
]

FACTORY_REF = {
    'sourceId': FACTORY_SOURCE_ID,
    'document': 'ИДМБ.661142.004-01 РЭ4, электровоз ЭП1М (ЭП1П)',
    'title': 'Ограничитель перенапряжений ОПН-1,28 УХЛ2 — назначение, технические характеристики, устройство и работа',
    'url': FACTORY_URL,
    'locator': 'раздел 57 «Ограничитель перенапряжений ОПН-1,28 УХЛ2»',
}

TU_REF = {
    'sourceId': TU_SOURCE_ID,
    'document': 'ТУ 16-674.064-86, каталог ограничителей перенапряжений',
    'title': 'ОПН-1,28 УХЛ2 — технические данные и устройство',
    'url': TU_URL,
    'locator': 'раздел 2.4.5, таблица технических данных',
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
    result = []
    seen = set()
    for item in items:
        key = item.get('sourceId') if isinstance(item, dict) else str(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def to_kb_parameters(items):
    result = []
    for p in items:
        result.append({
            'name': p['name'],
            'value': p['value'],
            'unit': p['unit'],
            'applicability': (
                'ОПН-1,28 УХЛ2; аппарат подтверждён для базового раннего исполнения 2ЭС5К/3ЭС5К; '
                'паспортное значение подтверждено документацией того же типа аппарата; '
                'на модернизированных секциях фактическое исполнение сверять по маркировке'
            ),
            'status': 'BASE_CONFIRMED',
            'sourceRefs': [p['sourceId']],
        })
    return result


def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault('sourceRegistry', {})
    registry['OPN128_FACTORY_DATA'] = FACTORY_REF
    registry['OPN128_TU_DATA'] = TU_REF

    matches = [r for r in root['records'] if r.get('id') == EQUIPMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f'Expected exactly one {EQUIPMENT_ID} record, found {len(matches)}')
    record = matches[0]
    models = record.get('modelNames', [])
    if 'ОПН-1,28 УХЛ2' not in models:
        raise SystemExit(f'Unexpected modelNames for {EQUIPMENT_ID}: {models!r}')
    designations = record.get('schemeDesignations', [])
    if not {'F2', 'F3'} <= set(designations):
        raise SystemExit(f'Factory RE1 requires F2/F3, found {designations!r}')

    record['purpose'] = (
        'Защита вторичных тяговых обмоток тягового трансформатора и подключённого к ним '
        'электрооборудования от атмосферных и коммутационных перенапряжений.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(record.get('sourceRefs', []) + [FACTORY_REF, TU_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}

    notes = [n for n in record.get('notes', []) if not n.startswith('ОПН-1,28 УХЛ2:')]
    notes += [
        'ОПН-1,28 УХЛ2: в заводской схеме 2ЭС5К/3ЭС5К ограничители F2 и F3 установлены в цепях вторичных тяговых обмоток.',
        'Защитный аппарат содержит высоконелинейные резисторы в герметизированном изоляционном корпусе; при опасном перенапряжении через них проходит импульсный ток, ограничивая напряжение до безопасного уровня.',
        'Современные исполнения семейства ОПН-1,28 могут отличаться конструкцией, массой и другими параметрами; значения от вариантов ОПН-1,28В/Ф/П не переносятся на эту базовую карточку без сверки маркировки.',
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
        'ОПН-1,28 УХЛ2 защищает вторичные тяговые обмотки трансформатора и подключённое к ним '
        'оборудование от атмосферных и коммутационных перенапряжений; в базовой схеме секции это F2 и F3.'
    )
    article['principle'] = (
        'Ограничитель содержит высоконелинейные резисторы в герметизированном изоляционном корпусе. '
        'При появлении опасного перенапряжения через резисторы проходит значительный импульсный ток, '
        'за счёт чего напряжение на защищаемом оборудовании снижается до безопасного уровня.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Корпус ограничителя и наружная изоляция визуально целы: без трещин, сколов, следов перекрытия и разрушения.',
        'Выводы, контактные соединения и крепление ограничителя без видимых повреждений, ослабления и следов местного перегрева.',
        'На корпусе и в зоне выводов отсутствуют видимые признаки нарушения герметичности или электрического пробоя.',
    ]
    article['deviationSigns'] = [
        'Трещины, сколы, разрушение корпуса или наружной изоляции, следы перекрытия либо электрической дуги.',
        'Повреждение, ослабление или выраженный перегрев контактных соединений и выводов.',
        'Следы пробоя, разрушения защитного аппарата или иного нарушения целостности герметизированного корпуса.',
    ]

    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, FACTORY_SOURCE_ID, TU_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)

    rules = [r for r in article.get('variantRules', []) if not r.startswith('ОПН-1,28 УХЛ2')]
    rules.append(
        'ОПН-1,28 УХЛ2 и обозначения F2/F3 подтверждены заводскими РЭ 2ЭС5К/3ЭС5К для базового раннего профиля. '
        'Паспортные значения уточнены по документации того же типа аппарата и ТУ 16-674.064-86. '
        'Современные исполнения ОПН-1,28В/Ф/П могут иметь иные конструктивные параметры; их данные не считать '
        'универсальными для этой карточки без сверки фактической маркировки.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak OPN-1.28 UHL2 surge arrester reference enriched in app and patch mirrors')
