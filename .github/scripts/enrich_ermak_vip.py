#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
SOURCE_ID = 'ER-SRC-034'
SOURCE_URL = 'https://elvpr.ru/ru/catalog/preobrazovatelnaya-tekhnika/preobrazovateli-dlya-elektropodvizhnogo-sostava/preobrazovateli-dlya-elektrovozov/tyagovye-preobrazovateli/preobrazovatel-vypryamitelno-invertornyy-vip-4000m-ukhl2-dlya-magistralnykh-elektrovozov-vl-80r-vl-8/'

PARAMETERS = [
    {'name': 'Номинальное входное однофазное напряжение', 'value': 1570, 'unit': 'V', 'sourceId': SOURCE_ID},
    {'name': 'Номинальный длительный выходной ток', 'value': 1900, 'unit': 'A', 'sourceId': SOURCE_ID},
    {'name': 'Номинальный пусковой выходной ток', 'value': 3150, 'unit': 'A', 'sourceId': SOURCE_ID},
    {'name': 'Номинальное выходное напряжение', 'value': 1400, 'unit': 'V', 'sourceId': SOURCE_ID},
    {'name': 'Номинальная выходная мощность', 'value': 4000, 'unit': 'kW', 'sourceId': SOURCE_ID},
    {'name': 'КПД, не менее', 'value': 98.5, 'unit': '%', 'sourceId': SOURCE_ID},
    {'name': 'Расход охлаждающего воздуха, не менее', 'value': 330, 'unit': 'm3/min', 'sourceId': SOURCE_ID},
    {'name': 'Срок службы', 'value': 15, 'unit': 'years', 'sourceId': SOURCE_ID},
]

KB_PARAMETERS = [
    {
        'name': p['name'], 'value': p['value'], 'unit': p['unit'],
        'applicability': 'ВИП-4000М-УХЛ2; базовое исполнение 2ЭС5К/3ЭС5К.',
        'status': 'BASE_CONFIRMED', 'sourceRefs': [SOURCE_ID]
    }
    for p in PARAMETERS
]

SOURCE_REF = {
    'sourceId': SOURCE_ID,
    'document': 'ПАО «Электровыпрямитель»',
    'title': 'ВИП-4000М-УХЛ2 — технические характеристики',
    'url': SOURCE_URL,
    'locator': 'Описание и основные характеристики'
}


def read_gz(path: Path):
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        return json.load(fh)


def write_gz(path: Path, payload):
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='', mode='wb', fileobj=out, mtime=0, compresslevel=9) as gz:
            gz.write(raw)


def unique_source_refs(items):
    result = []
    seen = set()
    for item in items:
        key = item.get('sourceId') if isinstance(item, dict) else str(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault('sourceRegistry', {})
    registry['ELVPR'] = {
        'sourceId': SOURCE_ID,
        'document': 'ПАО «Электровыпрямитель»',
        'title': 'ВИП-4000М-УХЛ2 — технические характеристики',
        'url': SOURCE_URL,
    }
    record = next(r for r in root['records'] if r.get('id') == 'ER-EQ-TR-001')
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_source_refs(record.get('sourceRefs', []) + [SOURCE_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    notes = [n for n in record.get('notes', []) if n != 'Паспортные параметры сверены по данным изготовителя ВИП-4000М-УХЛ2.']
    notes.append('Паспортные параметры сверены по данным изготовителя ВИП-4000М-УХЛ2.')
    record['notes'] = notes
    stats = root.get('statistics', {})
    if stats:
        stats['recordsWithParameters'] = sum(bool(r.get('parameters')) for r in root['records'])
        stats['recordsWithoutParameters'] = len(root['records']) - stats['recordsWithParameters']
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    article = next(a for a in root['articles'] if a.get('id') == 'ER-KB-EQ-ER-EQ-TR-001')
    article['summary'] = 'ВИП-4000М-УХЛ2 преобразует регулируемое напряжение тяговой обмотки для питания ТЭД в тяге и работает в инверторном режиме при рекуперативном торможении.'
    article['principle'] = 'На секции установлены два ВИП (U1 и U2). Они получают питание от тяговых обмоток трансформатора, по командам системы управления регулируют ток тяговых двигателей, а при рекуперации переводятся в инверторный режим. Встроенная система диагностирования контролирует работу узлов преобразователя.'
    article['keyParameters'] = KB_PARAMETERS
    refs = article.setdefault('sourceRefs', [])
    if SOURCE_ID not in refs:
        refs.append(SOURCE_ID)
    coverage = article.setdefault('knowledgeCoverage', {})
    coverage['parameters'] = 'manufacturer_documented'
    atlas = article.setdefault('atlasData', {})
    atlas['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak VIP-4000M reference enriched in app and patch mirrors')
