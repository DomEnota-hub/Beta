#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-TR-009'
ARTICLE_ID = f'ER-KB-EQ-{EQUIPMENT_ID}'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
ISH95_SOURCE_ID = 'ER-SRC-049'
ERMAK_RE4_SOURCE_ID = 'ER-SRC-050'
ERMAK_MAINT_SOURCE_ID = 'ER-SRC-051'
THREE_ES5K_SOURCE_ID = 'ER-SRC-052'

ISH95_URL = 'https://poezdvl.com/vl80k/vl80k_45.html'
ERMAK_RE4_URL = 'https://rcit.su/techinfoV54.html'
ERMAK_MAINT_URL = 'https://rcit.su/techinfoV58.html'
THREE_ES5K_URL = 'https://rgups.ru/site/assets/files/213502/dissertatciia_verigin_o_s__27_09_2024.pdf'

PARAMETERS = [
    {
        'name': 'ИШ-95 — номинальное напряжение относительно земли',
        'value': 2000,
        'unit': 'V',
        'sourceId': ISH95_SOURCE_ID,
        'applicability': 'ИШ-95; справочные данные аппарата. Применение ИШ-95 на 2ЭС5К/3ЭС5К подтверждено ИДМБ.661142.009РЭ4; исполнение конкретной секции сверять по маркировке.',
    },
    {
        'name': 'ИШ-95 — номинальный ток',
        'value': 520,
        'unit': 'A',
        'sourceId': ISH95_SOURCE_ID,
        'applicability': 'ИШ-95; справочные данные аппарата. Применение ИШ-95 на 2ЭС5К/3ЭС5К подтверждено ИДМБ.661142.009РЭ4; исполнение конкретной секции сверять по маркировке.',
    },
    {
        'name': 'ИШ-95 — индуктивность при токе 520 А, не менее',
        'value': 1.5,
        'unit': 'mH',
        'sourceId': ISH95_SOURCE_ID,
        'applicability': 'ИШ-95; справочные данные аппарата. Не переносить на ИШ-009.',
    },
    {
        'name': 'ИШ-95 — сопротивление при 20 °C',
        'value': 0.0051,
        'unit': 'Ohm',
        'sourceId': ISH95_SOURCE_ID,
        'applicability': 'ИШ-95; справочные данные аппарата. Не переносить на ИШ-009.',
    },
    {
        'name': 'ИШ-95 — охлаждение',
        'value': 'воздушное принудительное',
        'unit': '',
        'sourceId': ISH95_SOURCE_ID,
        'applicability': 'ИШ-95; эксплуатация аппарата без принудительного охлаждения не допускается по справочному описанию ИШ-95.',
    },
]

ISH95_REF = {
    'sourceId': ISH95_SOURCE_ID,
    'document': 'Справочное описание электрооборудования ВЛ80К',
    'title': 'Индуктивный шунт ИШ-95 — назначение, технические данные, устройство и обслуживание',
    'url': ISH95_URL,
    'locator': 'раздел «Индуктивные шунты ИШ-84 и ИШ-95»',
}

ERMAK_RE4_REF = {
    'sourceId': ERMAK_RE4_SOURCE_ID,
    'document': 'ИДМБ.661142.009РЭ4, электровоз магистральный 2ЭС5К (3ЭС5К)',
    'title': 'Электрические аппараты и оборудование — ИШ-95 и РОВ-21',
    'url': ERMAK_RE4_URL,
    'locator': 'содержание книги 4: п. 73 «Индуктивный шунт ИШ-95», п. 82 «Резисторы ослабления возбуждения РОВ-21»',
}

ERMAK_MAINT_REF = {
    'sourceId': ERMAK_MAINT_SOURCE_ID,
    'document': 'ИДМБ.661142.009РЭ8, электровоз магистральный 2ЭС5К (3ЭС5К)',
    'title': 'Трансформаторы, реакторы и дроссели — техническое обслуживание и текущий ремонт',
    'url': ERMAK_MAINT_URL,
    'locator': 'пп. 4.3.2, 6.3.2 и 8.3.2',
}

THREE_ES5K_REF = {
    'sourceId': THREE_ES5K_SOURCE_ID,
    'document': 'РГУПС, исследование тягового электропривода электровоза 3ЭС5К',
    'title': 'РОВ-21 и альтернативное исполнение с индуктивным шунтом ИШ-009',
    'url': THREE_ES5K_URL,
    'locator': 'Приложение Б, таблицы Б.6 и Б.7',
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


def find_equipment(root):
    candidates = [r for r in root['records'] if r.get('id') == EQUIPMENT_ID]
    if len(candidates) != 1:
        raise SystemExit(f'Expected exactly one {EQUIPMENT_ID} equipment record, found {len(candidates)}')
    record = candidates[0]
    models = set(record.get('modelNames', []))
    if not {'РОВ-21', 'ИШ-95'} <= models:
        raise SystemExit(f'{EQUIPMENT_ID} no longer matches expected ROV-21 + ISh-95 base models: {sorted(models)}')
    return record


def find_article(root):
    candidates = [
        a for a in root['articles']
        if a.get('id') == ARTICLE_ID or a.get('equipmentId') == EQUIPMENT_ID
    ]
    unique = {a.get('id'): a for a in candidates}
    if len(unique) != 1:
        raise SystemExit(f'Expected exactly one knowledge article for {EQUIPMENT_ID}, found {len(unique)}')
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
    registry['ISH95_REFERENCE_DATA'] = ISH95_REF
    registry['ERMAK_FIELD_WEAKENING_RE4'] = ERMAK_RE4_REF
    registry['ERMAK_FIELD_WEAKENING_MAINTENANCE'] = ERMAK_MAINT_REF
    registry['ERMAK_3ES5K_FIELD_WEAKENING_VARIANT'] = THREE_ES5K_REF

    record = find_equipment(root)
    record['purpose'] = (
        'Ослабление возбуждения тяговых двигателей резисторами РОВ-21 и улучшение коммутации '
        'ТЭД при переходных процессах за счёт индуктивного шунта. Для исполнения, отражённого '
        'в базовой карточке, шунт указан как ИШ-95.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(
        record.get('sourceRefs', []) + [ISH95_REF, ERMAK_RE4_REF, ERMAK_MAINT_REF, THREE_ES5K_REF]
    )
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}

    notes = [
        n for n in record.get('notes', [])
        if not n.startswith('Цепь ослабления возбуждения:') and not n.startswith('ИШ-95:')
    ]
    notes += [
        'Цепь ослабления возбуждения: РОВ-21 шунтирует обмотку возбуждения ТЭД; индуктивный шунт в ветви резистора уменьшает неблагоприятное перераспределение тока при переходных процессах и улучшает коммутацию двигателя.',
        'ИШ-95: для базовой карточки сохранён именно этот тип, поскольку ИДМБ.661142.009РЭ4 2ЭС5К/3ЭС5К прямо перечисляет ИШ-95 и РОВ-21. Паспортные значения ИШ-95 в параметрах не распространяются на ИШ-009.',
        'Для части исполнений 3ЭС5К документально встречается ИШ-009: у него при том же номинальном токе 520 А электрическое сопротивление 0,0066 Ом, тогда как для ИШ-95 справочное значение составляет 0,0051 Ом. Фактический тип шунта необходимо сверять по маркировке и комплекту документации секции.',
        'При обслуживании проверяют крепления и контактные соединения, изоляционные поверхности, катушку, магнитопровод, стяжные шпильки и подводящие шины; при более глубоком ремонте контролируют трещины шины, межвитковые замыкания и состояние изоляции.',
    ]
    record['notes'] = notes

    stats = root.get('statistics', {})
    if stats:
        stats['recordsWithParameters'] = sum(bool(r.get('parameters')) for r in root['records'])
        stats['recordsWithoutParameters'] = len(root['records']) - stats['recordsWithParameters']
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    article = find_article(root)
    article['summary'] = (
        'РОВ-21 формирует резистивную ветвь ослабления возбуждения тягового двигателя, а '
        'индуктивный шунт стабилизирует распределение тока в переходных режимах и улучшает коммутацию ТЭД.'
    )
    article['principle'] = (
        'При ослаблении возбуждения резистор РОВ-21 подключается параллельно обмотке возбуждения ТЭД. '
        'Без дополнительной индуктивности переменная составляющая тока при переходном процессе стремится '
        'перераспределиться в резистивную ветвь быстрее, чем в индуктивную обмотку возбуждения. '
        'Индуктивный шунт, включённый последовательно с резистором, повышает индуктивное сопротивление '
        'этой ветви, уменьшает броски тока и улучшает условия коммутации на коллекторе двигателя.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Крепление деталей и узлов, особенно электрических контактных соединений, надёжно; резьбовые соединения не ослаблены.',
        'Изоляционные поверхности, катушка и магнитопровод без видимых повреждений; изоляционное покрытие сохранено.',
        'Стяжные шпильки, подводящие крепления и шины исправны и надёжно закреплены; следов перегрева и повреждения контактных соединений нет.',
    ]
    article['deviationSigns'] = [
        'Ослабление креплений, резьбовых или электрических контактных соединений, подводящих шин.',
        'Повреждение изоляционных поверхностей или покрытия, трещины в шине катушки либо признаки межвиткового замыкания.',
        'Повреждение катушки, магнитопровода или стяжных шпилек, а также отклонение состояния изоляции от требований ремонта.',
    ]

    refs = article.setdefault('sourceRefs', [])
    for ref in [
        SCHEME_SOURCE_ID,
        MANUAL_SOURCE_ID,
        ISH95_SOURCE_ID,
        ERMAK_RE4_SOURCE_ID,
        ERMAK_MAINT_SOURCE_ID,
        THREE_ES5K_SOURCE_ID,
    ]:
        if ref not in refs:
            refs.append(ref)

    rules = [
        r for r in article.get('variantRules', [])
        if not r.startswith('Цепь ослабления возбуждения') and not r.startswith('ИШ-95')
    ]
    rules.append(
        'Цепь ослабления возбуждения имеет вариантность по типу индуктивного шунта. '
        'ИДМБ.661142.009РЭ4 2ЭС5К/3ЭС5К перечисляет ИШ-95 совместно с РОВ-21, тогда как '
        'данные по электрооборудованию одного из исполнений 3ЭС5К фиксируют ИШ-009 (520 А, 0,0066 Ом). '
        'ИШ-95 и ИШ-009 не считать взаимозаменяемыми по паспортным значениям: для ИШ-95 в этой карточке '
        'приведены 2000 В, 520 А, не менее 1,5 мГн при 520 А, 0,0051 Ом при 20 °C и принудительное '
        'воздушное охлаждение. Фактический тип сверять по маркировке и документации конкретной секции.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak field-weakening chain (ROV-21 + ISh-95, ISh-009 variant-aware) enriched in app and patch mirrors')
