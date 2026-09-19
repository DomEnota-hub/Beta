#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-HV-003'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-HV-003'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
DATA_SOURCE_ID = 'ER-SRC-040'
DATA_URL = 'https://scbist.com/scb/uploaded/1_1569870485.pdf'

PARAMETERS = [
    {'name': 'Номинальное напряжение', 'value': 25, 'unit': 'kV', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Номинальный ток на стоянке', 'value': 530, 'unit': 'A', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Номинальный ток при движении', 'value': 1100, 'unit': 'A', 'sourceId': DATA_SOURCE_ID, 'condition': 'скорость электровоза не менее 20 км/ч'},
    {'name': 'Масса', 'value': 72, 'unit': 'kg', 'sourceId': DATA_SOURCE_ID},
]

DATA_REF = {
    'sourceId': DATA_SOURCE_ID,
    'document': 'Читинское подразделение Забайкальского учебного центра ОАО «РЖД»',
    'title': 'Разъединитель Р-213-1 — назначение, устройство и технические характеристики',
    'url': DATA_URL,
    'locator': 'раздел 6.6 «Разъединители и переключатели силовых и вспомогательных цепей»'
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
            'applicability': p.get('condition', 'Р-213-1; базовое исполнение 2ЭС5К/3ЭС5К'),
            'status': 'BASE_CONFIRMED',
            'sourceRefs': [p['sourceId']],
        }
        for p in items
    ]


def patch_equipment(path: Path):
    root = read_gz(path)
    root.setdefault('sourceRegistry', {})['R213_TECH_DATA'] = DATA_REF
    record = next(r for r in root['records'] if r.get('id') == EQUIPMENT_ID)
    record['purpose'] = (
        'Изоляция повреждённого токоприёмника либо неисправной секции в высоковольтной '
        'цепи. Разъединитель предназначен только для коммутации предварительно обесточенной цепи.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(record.get('sourceRefs', []) + [DATA_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    notes = [n for n in record.get('notes', []) if not n.startswith('Р-213-1:')]
    notes += [
        'Р-213-1: высоковольтный разъединитель ножевого типа с ручным приводом. Контактная система смонтирована на опорных изоляторах и включает подвижный нож и неподвижный контакт; контактное нажатие создаётся пружинами.',
        'На базовой секции 2ЭС5К/3ЭС5К предусмотрены два Р-213-1 (QS1/QS2). Базовое руководство относит аппарат к штатному высоковольтному оборудованию; конкретное назначение каждого разъединителя определяется электрической схемой секции.',
        'Аппарат не является выключателем нагрузки: штатное назначение предусматривает изменение его положения только в обесточенной высоковольтной цепи.'
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
        'Р-213-1 — ножевой высоковольтный разъединитель секции, применяемый для электрического '
        'отделения повреждённого токоприёмника или неисправной секции от остальной первичной цепи.'
    )
    article['principle'] = (
        'В базовой схеме каждой секции установлены два разъединителя Р-213-1 (QS1 и QS2). '
        'Аппарат имеет подвижный нож, неподвижный контакт, опорные изоляторы и ручной привод. '
        'Пружины обеспечивают контактное нажатие, а механическая фиксация удерживает выбранное '
        'положение. Разъединитель не предназначен для отключения тока нагрузки и применяется '
        'только в заранее обесточенной высоковольтной цепи.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Положение разъединителя однозначно соответствует выбранной конфигурации высоковольтной схемы секции.',
        'Подвижный нож и неподвижный контакт не имеют видимых повреждений, следов перегрева или выраженного обгорания.',
        'Опорные изоляторы и механическая часть без видимых трещин и деформаций; соединение основания с заземляющей цепью сохранено.'
    ]
    article['deviationSigns'] = [
        'Неоднозначное или неполное положение ножа относительно неподвижного контакта.',
        'Следы перегрева, выраженного обгорания либо повреждение контактных поверхностей.',
        'Трещины или повреждения изоляторов, деформация механизма либо нарушение штатной фиксации положения.'
    ]
    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, DATA_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('Р-213-1')]
    rules.append(
        'Р-213-1 подтверждён базовым руководством 2ЭС5К/3ЭС5К. Конкретную функцию QS1/QS2 '
        'и фактическое исполнение на модернизированной секции подтверждать по электрической схеме и маркировке.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak R-213-1 disconnector reference enriched in app and patch mirrors')
