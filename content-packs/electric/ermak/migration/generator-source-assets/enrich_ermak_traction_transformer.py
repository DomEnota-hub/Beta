#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-HV-008'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-HV-008'
MANUFACTURER_SOURCE_ID = 'ER-SRC-033'
RGUPS_SOURCE_ID = 'ER-SRC-037'
RGUPS_URL = 'https://rgups.ru/site/assets/files/213502/dissertatciia_verigin_o_s__27_09_2024.pdf'

EXTRA_PARAMETERS = [
    {'name': 'Номинальная мощность трансформатора', 'value': 4350, 'unit': 'kVA', 'sourceId': RGUPS_SOURCE_ID, 'condition': '3ЭС5К; ОНДЦЭ-4350/25'},
    {'name': 'Номинальный ток сетевой обмотки', 'value': 173.8, 'unit': 'A', 'sourceId': RGUPS_SOURCE_ID, 'condition': '3ЭС5К; ОНДЦЭ-4350/25'},
    {'name': 'Номинальный ток тяговых обмоток', 'value': 1600, 'unit': 'A', 'sourceId': RGUPS_SOURCE_ID, 'condition': '3ЭС5К; ОНДЦЭ-4350/25'},
    {'name': 'Потери короткого замыкания', 'value': 56.8, 'unit': 'kW', 'sourceId': RGUPS_SOURCE_ID, 'condition': '3ЭС5К; ОНДЦЭ-4350/25'},
    {'name': 'Ток холостого хода', 'value': 0.8, 'unit': '%', 'sourceId': RGUPS_SOURCE_ID, 'condition': '3ЭС5К; ОНДЦЭ-4350/25'},
]

RGUPS_REF = {
    'sourceId': RGUPS_SOURCE_ID,
    'document': 'РГУПС, диссертация О.С. Веригина, 2024',
    'title': 'Основные технические характеристики электрооборудования электровоза 3ЭС5К',
    'url': RGUPS_URL,
    'locator': 'Приложение Б, таблица Б.2, стр. 128–129 PDF'
}


def read_gz(path: Path):
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        return json.load(fh)


def write_gz(path: Path, payload):
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='', mode='wb', fileobj=out, mtime=0, compresslevel=9) as gz:
            gz.write(raw)


def parameter_key(item):
    return (item.get('name'), str(item.get('value')), item.get('unit'), item.get('condition'))


def merge_parameters(existing, extra):
    out = list(existing)
    seen = {parameter_key(x) for x in out if isinstance(x, dict)}
    for item in extra:
        if parameter_key(item) not in seen:
            out.append(item)
            seen.add(parameter_key(item))
    return out


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
    root.setdefault('sourceRegistry', {})['RGUPS_3ES5K_TRANSFORMER_2024'] = RGUPS_REF
    record = next(r for r in root['records'] if r.get('id') == EQUIPMENT_ID)
    record['parameters'] = merge_parameters(record.get('parameters', []), EXTRA_PARAMETERS)
    record['sourceRefs'] = unique_source_refs(record.get('sourceRefs', []) + [RGUPS_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(record['parameters'])}
    record['purpose'] = (
        'Преобразование напряжения контактной сети 25 кВ для питания двух тяговых ветвей, '
        'цепей возбуждения и собственных нужд секции; при рекуперации участвует в передаче энергии обратно в контактную сеть.'
    )
    notes = [n for n in record.get('notes', []) if not n.startswith('По открытым источникам значения')]
    notes.append(
        'По открытым источникам значения отдельных параметров обмотки собственных нужд и полной массы могут различаться между исполнениями/изготовителями. '
        'Для карточки базовыми по этим полям приняты данные каталога изготовителя ОНДЦЭ-4350/25П-У2; точный суффикс и паспортные данные конкретного трансформатора следует определять по маркировке и эксплуатационной документации.'
    )
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
        'Тяговый трансформатор ОНДЦЭ-4350/25 принимает 25 кВ от контактной сети и формирует напряжения '
        'для двух тяговых обмоток, цепи возбуждения и собственных нужд секции.'
    )
    article['principle'] = (
        'Однофазный масляный тяговый трансформатор имеет сетевую обмотку и две тяговые обмотки, питающие два '
        'выпрямительно-инверторных преобразователя. Отдельные обмотки питают цепь возбуждения тяговых двигателей '
        'и собственные нужды. Исполнение ОНДЦЭ использует принудительную циркуляцию масла и воздуха с направленным '
        'потоком масла. При рекуперативном торможении трансформатор работает в обратном энергетическом потоке вместе '
        'с ВИП, обеспечивая передачу энергии тяговых двигателей в контактную сеть.'
    )
    kb_extra = [
        {
            'name': p['name'], 'value': p['value'], 'unit': p['unit'],
            'applicability': p['condition'], 'status': 'BASE_CONFIRMED', 'sourceRefs': [p['sourceId']]
        }
        for p in EXTRA_PARAMETERS
    ]
    article['keyParameters'] = merge_parameters(article.get('keyParameters', []), [
        {
            'name': p['name'], 'value': p['value'], 'unit': p['unit'],
            'condition': p.get('applicability'), 'sourceId': p['sourceRefs'][0]
        }
        for p in kb_extra
    ])
    # Normalize added KB items to the article schema while preserving pre-existing entries untouched.
    normalized = []
    for item in article['keyParameters']:
        if item.get('sourceId') == RGUPS_SOURCE_ID:
            normalized.append({
                'name': item['name'], 'value': item['value'], 'unit': item['unit'],
                'applicability': item.get('condition', '3ЭС5К; ОНДЦЭ-4350/25'),
                'status': 'BASE_CONFIRMED', 'sourceRefs': [RGUPS_SOURCE_ID]
            })
        else:
            normalized.append(item)
    article['keyParameters'] = normalized
    refs = article.setdefault('sourceRefs', [])
    if RGUPS_SOURCE_ID not in refs:
        refs.append(RGUPS_SOURCE_ID)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('Точный суффикс трансформатора')]
    rules.append(
        'Точный суффикс трансформатора и отдельные паспортные значения проверять по маркировке конкретной секции: '
        'открытые источники для ОНДЦЭ-4350/25 содержат расхождения по массе и параметрам обмотки собственных нужд.'
    )
    article['variantRules'] = rules
    coverage = article.setdefault('knowledgeCoverage', {})
    coverage['parameters'] = 'manufacturer_and_3es5k_documented'
    atlas = article.setdefault('atlasData', {})
    atlas['parameterCoverage'] = {'status': 'documented', 'count': len(article['keyParameters'])}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak traction transformer reference enriched in app and patch mirrors')
