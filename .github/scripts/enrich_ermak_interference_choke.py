#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-HV-002'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-HV-002'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
RGUPS_SOURCE_ID = 'ER-SRC-041'
TRAINING_SOURCE_ID = 'ER-SRC-042'
RGUPS_URL = 'https://rgups.ru/site/assets/files/213502/dissertatciia_verigin_o_s__27_09_2024.pdf'
TRAINING_URL = 'https://scbist.com/scb/uploaded/1_1569870485.pdf'

PARAMETERS = [
    {'name': 'Номинальное напряжение изоляции', 'value': 25, 'unit': 'kV', 'sourceId': RGUPS_SOURCE_ID},
    {'name': 'Номинальный ток продолжительного режима', 'value': 650, 'unit': 'A', 'sourceId': RGUPS_SOURCE_ID, 'condition': 'при скорости охлаждающего воздуха не менее 25 км/ч'},
    {'name': 'Пусковой ток', 'value': 300, 'unit': 'A', 'sourceId': RGUPS_SOURCE_ID, 'condition': 'при скорости набегающего потока охлаждающего воздуха не более 10 км/ч'},
    {'name': 'Индуктивность', 'value': '250±25', 'unit': 'uH', 'sourceId': TRAINING_SOURCE_ID},
    {'name': 'Сопротивление катушки постоянному току при 20 °C', 'value': 0.0061, 'unit': 'Ohm', 'sourceId': RGUPS_SOURCE_ID},
    {'name': 'Охлаждение', 'value': 'воздушное', 'unit': '', 'sourceId': TRAINING_SOURCE_ID},
    {'name': 'Масса', 'value': 38, 'unit': 'kg', 'sourceId': RGUPS_SOURCE_ID},
]

RGUPS_REF = {
    'sourceId': RGUPS_SOURCE_ID,
    'document': 'РГУПС, исследование электрооборудования 3ЭС5К',
    'title': 'Основные технические характеристики дросселя помехоподавления ДП-011',
    'url': RGUPS_URL,
    'locator': 'Приложение Б, таблица Б.1'
}

TRAINING_REF = {
    'sourceId': TRAINING_SOURCE_ID,
    'document': 'Читинское подразделение Забайкальского учебного центра ОАО «РЖД»',
    'title': 'Дроссель ДП-011 — назначение и устройство',
    'url': TRAINING_URL,
    'locator': 'раздел 7.17 «Дроссель ДП-011»'
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
            'applicability': p.get('condition', 'ДП-011; базовое исполнение 2ЭС5К/3ЭС5К'),
            'status': 'BASE_CONFIRMED',
            'sourceRefs': [p['sourceId']],
        }
        for p in items
    ]


def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault('sourceRegistry', {})
    registry['DP011_RGUPS_DATA'] = RGUPS_REF
    registry['DP011_TRAINING_DATA'] = TRAINING_REF
    record = next(r for r in root['records'] if r.get('id') == EQUIPMENT_ID)
    record['purpose'] = (
        'Снижение уровня радиопомех, возникающих при кратковременном нарушении контакта '
        'между токоприёмником и контактным проводом, в первичной высоковольтной цепи секции.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(record.get('sourceRefs', []) + [RGUPS_REF, TRAINING_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    notes = [n for n in record.get('notes', []) if not n.startswith('ДП-011:')]
    notes += [
        'ДП-011: высоковольтный дроссель радиопомех, установленный в первичном тракте после токоприёмника; на базовой секции 2ЭС5К/3ЭС5К обозначается L1.',
        'Катушка выполнена из алюминиевой шины с зазорами между витками и закреплена на фарфоровом изоляторе через изоляционное основание; конструкция рассчитана на воздушное охлаждение набегающим потоком.',
        'ДП-011 не является коммутационным аппаратом: его функция — увеличение сопротивления высокочастотным составляющим помех при сохранении прохождения рабочего тягового тока.'
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
        'ДП-011 включён в первичную высоковольтную цепь секции и уменьшает радиопомехи, '
        'возникающие при нестабильном контакте токоприёмника с контактным проводом.'
    )
    article['principle'] = (
        'Дроссель L1 расположен в высоковольтном тракте после токоприёмника. Его индуктивность '
        'создаёт повышенное сопротивление высокочастотным составляющим помех, тогда как рабочий '
        'ток контактной сети проходит через катушку. ДП-011 выполнен в виде катушки из алюминиевой '
        'шины, закреплённой на фарфоровом изоляторе, и охлаждается воздушным потоком.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Катушка и её крепление не имеют видимых деформаций, повреждений или следов выраженного перегрева.',
        'Фарфоровый изолятор без видимых трещин, сколов и следов перекрытия; межвитковые зазоры сохранены.',
        'Высоковольтные соединения и крепёж визуально целы, без признаков ослабления или локального перегрева.'
    ]
    article['deviationSigns'] = [
        'Деформация витков, нарушение межвитковых зазоров либо повреждение изоляционных прокладок.',
        'Следы перегрева, оплавления, электрического перекрытия или повреждения высоковольтных соединений.',
        'Трещины, сколы или загрязнение изолятора, способные ухудшить его электрическую прочность.'
    ]
    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, RGUPS_SOURCE_ID, TRAINING_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('ДП-011')]
    rules.append(
        'ДП-011 подтверждён базовым руководством 2ЭС5К/3ЭС5К; технические параметры дополнительно '
        'подтверждены для 3ЭС5К. На модернизированных секциях фактический тип аппарата сверять по маркировке.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak DP-011 interference choke reference enriched in app and patch mirrors')

# Reapply canonical DP-011 enrichment after concurrent catalog edits.
