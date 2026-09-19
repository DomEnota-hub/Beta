#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
FACTORY_SOURCE_ID = 'ER-SRC-049'
ERMAK_SOURCE_ID = 'ER-SRC-050'
MAINT_SOURCE_ID = 'ER-SRC-051'
RGUPS_SOURCE_ID = 'ER-SRC-052'

FACTORY_URL = 'https://djvu.online/file/TVgYn3LTUveDJ'
ERMAK_URL = 'https://parketspektr.ru/remont-tyagovogo-transformatora-elektrovoza-2es5k/'
MAINT_URL = 'https://rcit.su/techinfoV58.html'
RGUPS_URL = 'https://rgups.ru/site/assets/files/213502/dissertatciia_verigin_o_s__27_09_2024.pdf'

PARAMETERS = [
    {
        'name': 'Номинальное напряжение изоляции',
        'value': 2000,
        'unit': 'V',
        'sourceId': FACTORY_SOURCE_ID,
        'applicability': 'ИШ-009; паспорт аппарата по заводскому РЭ ИДМБ.661142.004-01 РЭ4; на конкретной секции исполнение сверять по маркировке',
    },
    {
        'name': 'Номинальный ток',
        'value': 520,
        'unit': 'A',
        'sourceId': RGUPS_SOURCE_ID,
        'applicability': 'ИШ-009 на 3ЭС5К; независимо совпадает с заводскими данными аппарата ИШ-009',
    },
    {
        'name': 'Индуктивность при токе до 100 А, не менее',
        'value': 2.2,
        'unit': 'mH',
        'sourceId': FACTORY_SOURCE_ID,
        'applicability': 'ИШ-009; паспорт аппарата по заводскому РЭ ИДМБ.661142.004-01 РЭ4; на конкретной секции исполнение сверять по маркировке',
    },
    {
        'name': 'Индуктивность при токе 520 А, не менее',
        'value': 1.7,
        'unit': 'mH',
        'sourceId': FACTORY_SOURCE_ID,
        'applicability': 'ИШ-009; паспорт аппарата по заводскому РЭ ИДМБ.661142.004-01 РЭ4; на конкретной секции исполнение сверять по маркировке',
    },
    {
        'name': 'Электрическое сопротивление',
        'value': 0.0066,
        'unit': 'Ohm',
        'sourceId': RGUPS_SOURCE_ID,
        'applicability': 'ИШ-009 на 3ЭС5К; таблица Б.7 исследования электрооборудования 3ЭС5К',
    },
]

FACTORY_REF = {
    'sourceId': FACTORY_SOURCE_ID,
    'document': 'ИДМБ.661142.004-01 РЭ4, электровоз ЭП1М (ЭП1П)',
    'title': 'Индуктивный шунт ИШ-009 — назначение и технические характеристики',
    'url': FACTORY_URL,
    'locator': 'раздел 52 «Индуктивный шунт ИШ-009»',
}

ERMAK_REF = {
    'sourceId': ERMAK_SOURCE_ID,
    'document': 'Технический материал по силовой тяговой цепи электровоза 2ЭС5К',
    'title': 'Индуктивный шунт ИШ-009 — назначение, устройство и работа в схеме',
    'url': ERMAK_URL,
    'locator': 'раздел «Индуктивный шунт ИШ-009»',
}

MAINT_REF = {
    'sourceId': MAINT_SOURCE_ID,
    'document': 'ИДМБ.661142.009РЭ8, электровоз магистральный 2ЭС5К (3ЭС5К)',
    'title': 'Трансформаторы, реакторы и дроссели — техническое обслуживание и текущий ремонт',
    'url': MAINT_URL,
    'locator': 'пп. 4.3.2, 6.3.2, 8.3.2',
}

RGUPS_REF = {
    'sourceId': RGUPS_SOURCE_ID,
    'document': 'РГУПС, исследование тягового электропривода электровоза 3ЭС5К',
    'title': 'Основные технические характеристики индуктивного шунта ИШ-009',
    'url': RGUPS_URL,
    'locator': 'Приложение Б, таблица Б.7',
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


def searchable_text(record):
    values = [record.get('name', ''), record.get('model', '')]
    for key in ('modelNames', 'aliases'):
        value = record.get(key, [])
        if isinstance(value, list):
            values.extend(x for x in value if isinstance(x, str))
    return ' '.join(str(x) for x in values if x)


def find_equipment(root):
    candidates = [r for r in root['records'] if 'ИШ-009' in searchable_text(r)]
    if len(candidates) != 1:
        raise SystemExit(f'Expected exactly one ИШ-009 equipment record, found {len(candidates)}')
    return candidates[0]


def find_article(root, equipment_id):
    expected_id = f'ER-KB-EQ-{equipment_id}'
    candidates = [
        a for a in root['articles']
        if a.get('equipmentId') == equipment_id or a.get('id') == expected_id
    ]
    unique = {a.get('id'): a for a in candidates}
    if len(unique) != 1:
        raise SystemExit(f'Expected exactly one ИШ-009 knowledge article for {equipment_id}, found {len(unique)}')
    return next(iter(unique.values()))


def to_kb_parameters(items):
    return [
        {
            'name': p['name'],
            'value': p['value'],
            'unit': p['unit'],
            'applicability': p['applicability'],
            'status': 'BASE_CONFIRMED',
            'sourceRefs': [p['sourceId']],
        }
        for p in items
    ]


def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault('sourceRegistry', {})
    registry['ISH009_FACTORY_DATA'] = FACTORY_REF
    registry['ISH009_ERMAK_OPERATION'] = ERMAK_REF
    registry['ISH009_MAINTENANCE'] = MAINT_REF
    registry['ISH009_RGUPS_3ES5K'] = RGUPS_REF

    record = find_equipment(root)
    record['purpose'] = (
        'Уменьшение бросков тока и улучшение коммутации тягового двигателя при переходных '
        'процессах в режиме ослабления возбуждения. Шунт работает в ветви резистора ослабления '
        'возбуждения соответствующего тягового двигателя.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(
        record.get('sourceRefs', []) + [FACTORY_REF, ERMAK_REF, MAINT_REF, RGUPS_REF]
    )
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}

    notes = [n for n in record.get('notes', []) if not n.startswith('ИШ-009:')]
    notes += [
        'ИШ-009: на 2ЭС5К в тяговой схеме шунты обозначаются L11–L14; каждый включается последовательно с резистором ослабления возбуждения соответствующего ТЭД при первой ступени ослабления возбуждения.',
        'Шунт состоит из катушки, магнитопровода, двух гетинаксовых боковин, трёх стягивающих шпилек и установочных уголков. Катушка выполнена из медной шины 3×35 мм², намотанной на ребро с межвитковыми зазорами; межвитковая изоляция — электронит.',
        'Магнитопровод набран из пластин электротехнической стали марки 2212 толщиной 0,5 мм и изолирован от катушки стеклопластом; катушка с магнитопроводом вакуумно-нагнетательно пропитывается электроизоляционным лаком с последующей выпечкой.',
        'ИШ-009 не является коммутационным аппаратом: его индуктивность выравнивает переходный процесс в ветви ослабления возбуждения и улучшает условия коммутации ТЭД.',
    ]
    record['notes'] = notes

    stats = root.get('statistics', {})
    if stats:
        stats['recordsWithParameters'] = sum(bool(r.get('parameters')) for r in root['records'])
        stats['recordsWithoutParameters'] = len(root['records']) - stats['recordsWithParameters']
    equipment_id = record['id']
    write_gz(path, root)
    return equipment_id


def patch_knowledge(path: Path, equipment_id):
    root = read_gz(path)
    article = find_article(root, equipment_id)
    article['summary'] = (
        'ИШ-009 работает в цепи ослабления возбуждения тягового двигателя и уменьшает броски '
        'тока при переходных процессах, улучшая условия коммутации на коллекторе.'
    )
    article['principle'] = (
        'При ослаблении возбуждения резистор подключается параллельно обмотке возбуждения ТЭД. '
        'Из-за малого индуктивного сопротивления этой ветви переходная переменная составляющая тока '
        'без дополнительной индуктивности распределялась бы неблагоприятно для коммутации. ИШ-009 '
        'включён последовательно с резистором ослабления возбуждения соответствующего ТЭД и повышает '
        'индуктивное сопротивление шунтирующей ветви. Это уменьшает броски тока и риск тяжёлого искрения '
        'или кругового огня при восстановлении контакта токоприёмника, переключении контакторов '
        'ослабления возбуждения и бросках напряжения.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Крепление деталей и узлов, особенно контактных соединений, надёжно; резьбовые соединения не имеют признаков ослабления.',
        'Изоляционные поверхности, катушка и магнитопровод без видимых повреждений; изоляционное покрытие сохранено.',
        'Подводящие крепления и шины закреплены; стягивающие шпильки магнитопровода исправны и не ослаблены.',
    ]
    article['deviationSigns'] = [
        'Ослабление креплений, резьбовых или электрических контактных соединений, подводящих шин.',
        'Повреждение изоляционных поверхностей или покрытия, трещины в шине катушки либо признаки межвиткового замыкания.',
        'Повреждение катушки, магнитопровода или стягивающих шпилек, выявленное при осмотре и ремонте.',
    ]

    refs = article.setdefault('sourceRefs', [])
    for ref in [
        SCHEME_SOURCE_ID,
        MANUAL_SOURCE_ID,
        FACTORY_SOURCE_ID,
        ERMAK_SOURCE_ID,
        MAINT_SOURCE_ID,
        RGUPS_SOURCE_ID,
    ]:
        if ref not in refs:
            refs.append(ref)

    rules = [r for r in article.get('variantRules', []) if not r.startswith('ИШ-009')]
    rules.append(
        'ИШ-009 подтверждён для тяговой цепи 2ЭС5К и для электрооборудования 3ЭС5К. '
        'В отдельных более ранних ремонтных перечнях 2ЭС5К встречается ИШ-95, поэтому параметры '
        'ИШ-009 нельзя автоматически переносить на ИШ-95: фактический тип сверять по маркировке '
        'и комплекту документации конкретной секции. Значения 2000 В и 2,2/1,7 мГн уточнены по '
        'заводскому РЭ того же аппарата ИШ-009; 520 А и 0,0066 Ом независимо подтверждены для 3ЭС5К.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


ids = []
for base in ROOTS:
    equipment_id = patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz', equipment_id)
    ids.append(equipment_id)

if len(set(ids)) != 1:
    raise SystemExit(f'App/patch ИШ-009 equipment IDs differ: {ids}')

print(f'Ermak ИШ-009 inductive shunt reference enriched in app and patch mirrors ({ids[0]})')
