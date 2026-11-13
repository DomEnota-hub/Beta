#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
MANUAL_SOURCE_ID = 'ER-SRC-004'
CERT_SOURCE_ID = 'ER-SRC-035'
TMH_SOURCE_ID = 'ER-SRC-036'
CERT_URL = 'https://www.rsfgt.ru/Certificates/27488'
TMH_URL = 'https://tmholding.ru/journal_files/Transmashholding_04_2022_12.pdf'

PARAMETERS = [
    {'name': 'Номинальная мощность, часовой режим', 'value': 820, 'unit': 'kW', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'Номинальная мощность, продолжительный режим', 'value': 765, 'unit': 'kW', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'Номинальное напряжение', 'value': 1000, 'unit': 'V', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'Номинальный ток якоря, часовой режим', 'value': 870, 'unit': 'A', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'Номинальный ток якоря, продолжительный режим', 'value': 810, 'unit': 'A', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'Номинальная частота вращения, часовой режим', 'value': 920, 'unit': 'rpm', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'Номинальная частота вращения, продолжительный режим', 'value': 940, 'unit': 'rpm', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'КПД, продолжительный режим', 'value': 94.7, 'unit': '%', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'Расход вентилирующего воздуха при полном напоре 620 Па, не менее', 'value': 70, 'unit': 'm3/min', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б / НБ-514Е'},
    {'name': 'Масса без зубчатой передачи', 'value': 4300, 'unit': 'kg', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Б'},
    {'name': 'Масса без зубчатой передачи', 'value': 4350, 'unit': 'kg', 'sourceId': MANUAL_SOURCE_ID, 'condition': 'НБ-514Е'},
]

KB_PARAMETERS = [
    {
        'name': p['name'], 'value': p['value'], 'unit': p['unit'],
        'applicability': p['condition'], 'status': 'BASE_CONFIRMED',
        'sourceRefs': [p['sourceId']]
    }
    for p in PARAMETERS
]

CERT_REF = {
    'sourceId': CERT_SOURCE_ID,
    'document': 'Реестр ФБУ «РС ФЖТ»',
    'title': 'Сертификат на тяговые двигатели НБ-514Е и НБ-514Б',
    'url': CERT_URL,
    'locator': 'ЕАЭС RU С-RU.ЖТ02.В.02208/24; действует до 08.12.2029'
}

TMH_REF = {
    'sourceId': TMH_SOURCE_ID,
    'document': 'Вектор ТМХ №4, 2022',
    'title': 'НБ-514Е для электровозов семейства «Ермак»',
    'url': TMH_URL,
    'locator': 'стр. 20–21'
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
    registry['RSFZT_NB514_CERT_2024'] = CERT_REF
    registry['TMH_NB514E_2022'] = TMH_REF

    record = next(r for r in root['records'] if r.get('id') == 'ER-EQ-TR-005')
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_source_refs(record.get('sourceRefs', []) + [CERT_REF, TMH_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    notes = [n for n in record.get('notes', []) if not n.startswith('НБ-514')]
    notes += [
        'НБ-514Б и НБ-514Е — шестиполюсные компенсированные тяговые двигатели пульсирующего тока с независимой вентиляцией; в тяге работают с последовательным возбуждением, при рекуперации — как генераторы с независимым регулируемым возбуждением.',
        'НБ-514Е подтверждён ТМХ как вариант для семейства «Ермак» с опорно-осевым подвешиванием на моторно-осевых подшипниках качения. Применимость конкретного исполнения двигателя должна определяться по профилю/номеру локомотива, а не только по обозначению серии.'
    ]
    record['notes'] = notes
    stats = root.get('statistics', {})
    if stats:
        stats['recordsWithParameters'] = sum(bool(r.get('parameters')) for r in root['records'])
        stats['recordsWithoutParameters'] = len(root['records']) - stats['recordsWithParameters']
    write_gz(path, root)


def patch_knowledge(path: Path):
    root = read_gz(path)
    article = next(a for a in root['articles'] if a.get('id') == 'ER-KB-EQ-ER-EQ-TR-005')
    article['summary'] = 'Тяговые двигатели НБ-514Б/НБ-514Е преобразуют электрическую энергию тяговой цепи в момент на колёсной паре, а при рекуперативном торможении работают в генераторном режиме.'
    article['principle'] = 'На каждой секции установлено четыре ТЭД. Двигатель выполнен шестиполюсным и компенсированным, с независимой вентиляцией. В тяговом режиме используется последовательное возбуждение; при рекуперативном торможении машина работает как генератор с независимым регулируемым возбуждением. Вариант НБ-514Е применяется в колесно-моторных блоках с моторно-осевыми подшипниками качения; конкретное исполнение следует определять по профилю локомотива.'
    article['keyParameters'] = KB_PARAMETERS
    refs = article.setdefault('sourceRefs', [])
    for ref in [MANUAL_SOURCE_ID, CERT_SOURCE_ID, TMH_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('НБ-514')]
    rules += [
        'НБ-514Б и НБ-514Е не объединять в один безусловный вариант: конструктивное исполнение колесно-моторного блока и моторно-осевых подшипников зависит от профиля локомотива.',
        'Для НБ-514Е подтверждено применение моторно-осевых подшипников качения; серийную границу конкретного локомотива хранить как отдельный профиль применимости.'
    ]
    article['variantRules'] = rules
    coverage = article.setdefault('knowledgeCoverage', {})
    coverage['parameters'] = 'manual_documented'
    atlas = article.setdefault('atlasData', {})
    atlas['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak NB-514B/NB-514E reference enriched in app and patch mirrors')
