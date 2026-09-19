#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-HV-005'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-HV-005'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
DATA_SOURCE_ID = 'ER-SRC-042'
DATA_URL = 'https://djvu.online/file/TVgYn3LTUveDJ'

PARAMETERS = [
    {'name': 'Номинальный ток', 'value': 320, 'unit': 'A', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Индуктивность', 'value': '7.5±0.5', 'unit': 'mH', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Ёмкость', 'value': '700±50', 'unit': 'pF', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Частота настройки контура', 'value': 2.13, 'unit': 'MHz', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Резонансное сопротивление настроенного контура, не менее', 'value': 12, 'unit': 'MOhm', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Масса', 'value': 4.6, 'unit': 'kg', 'sourceId': DATA_SOURCE_ID},
]

DATA_REF = {
    'sourceId': DATA_SOURCE_ID,
    'document': 'Руководство по эксплуатации электрических аппаратов, фильтр Ф-6',
    'title': 'Фильтр Ф-6 — назначение, устройство и технические характеристики',
    'url': DATA_URL,
    'locator': 'раздел «54 Фильтр Ф-6», рисунок 111'
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
    return [
        {
            'name': p['name'],
            'value': p['value'],
            'unit': p['unit'],
            'applicability': 'Ф-6; параметры относятся к самому аппарату. Применение Ф-6 на базовых 2ЭС5К/3ЭС5К подтверждено заводским РЭ.',
            'status': 'BASE_CONFIRMED',
            'sourceRefs': [p['sourceId']],
        }
        for p in items
    ]


def patch_equipment(path: Path):
    root = read_gz(path)
    root.setdefault('sourceRegistry', {})['F6_REFERENCE_DATA'] = DATA_REF
    record = next(r for r in root['records'] if r.get('id') == EQUIPMENT_ID)
    record['purpose'] = (
        'Подавление высокочастотных радиопомех в первичной цепи тягового трансформатора. '
        'Фильтр Ф-6 образует настроенный колебательный контур и не является коммутационным аппаратом.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(record.get('sourceRefs', []) + [DATA_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    notes = [n for n in record.get('notes', []) if not n.startswith('Ф-6:')]
    notes += [
        'Ф-6: фильтр включён в первичную цепь тягового трансформатора и предназначен для подавления помех радиоприёму.',
        'Конструктивно узел включает катушку индуктивности и конденсаторы постоянной ёмкости, образующие настроенный контур.',
        'Числовые характеристики относятся к аппарату Ф-6. Его применение на базовых 2ЭС5К/3ЭС5К подтверждено заводским РЭ; для модернизированной секции фактическое исполнение следует сверять по маркировке и схеме.'
    ]
    record['notes'] = notes
    stats = root.get('statistics', {})
    if stats:
        stats['recordsWithParameters'] = sum(bool(r.get('parameters')) for r in root['records'])
        stats['recordsWithoutParameters'] = len(root['records']) - stats['recordsWithParameters']
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    article = next(a for a in root['articles'] if a.get('id') == ARTICLE_ID)
    article['summary'] = (
        'Ф-6 — настроенный фильтр первичной высоковольтной цепи, уменьшающий радиопомехи '
        'в тракте питания тягового трансформатора.'
    )
    article['principle'] = (
        'Катушка индуктивности и конденсаторы постоянной ёмкости образуют настроенный контур. '
        'На частоте настройки контур создаёт высокое сопротивление высокочастотной составляющей помех, '
        'не вмешиваясь в штатную передачу тяговой энергии по первичной цепи.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Катушка, конденсаторная часть и основание без видимых механических повреждений и следов перегрева.',
        'Изоляционные детали без трещин, сколов и следов электрического пробоя.',
        'Токоведущие соединения и крепления сохраняют штатное состояние без признаков ослабления или перегрева.'
    ]
    article['deviationSigns'] = [
        'Следы перегрева, обгорания или повреждения токоведущих соединений.',
        'Повреждение катушки, конденсаторов, основания или изоляционных деталей.',
        'Признаки пробоя изоляции, деформации узла либо нарушения механического крепления.'
    ]
    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, DATA_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('Ф-6')]
    rules.append(
        'Ф-6 подтверждён базовым руководством 2ЭС5К/3ЭС5К. Числовые параметры относятся к аппарату Ф-6; '
        'на модернизированной секции фактическое исполнение подтверждать по маркировке и документации.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak F-6 primary filter reference enriched in app and patch mirrors')
