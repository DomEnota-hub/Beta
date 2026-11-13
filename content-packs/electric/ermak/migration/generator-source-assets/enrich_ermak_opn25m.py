#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-HV-007'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-HV-007'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
FACTORY_SOURCE_ID = 'ER-SRC-045'
FACTORY_URL = 'https://opnzeu.ru/ogranichiteli-perenapryaz/podvizhnoj-sostav-25-kv.html'

PARAMETERS = [
    {'name': 'Класс напряжения сети', 'value': 25, 'unit': 'kV', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Наибольшее длительно допустимое рабочее напряжение', 'value': 29, 'unit': 'kV', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Номинальное напряжение ОПН', 'value': 22.5, 'unit': 'kV', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Номинальный разрядный ток', 'value': 10, 'unit': 'kA', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Остающееся напряжение при импульсе 8/20 мкс, 1000 А, не более', 'value': 76, 'unit': 'kV', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Остающееся напряжение при импульсе 8/20 мкс, 5000 А, не более', 'value': 85, 'unit': 'kV', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Пропускная способность, импульсы 8/20 мкс', 'value': '20 × 10', 'unit': 'kA', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Пропускная способность, прямоугольные импульсы 2 мс', 'value': '18 × 400', 'unit': 'A', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Длина пути утечки внешней изоляции, не менее', 'value': 63, 'unit': 'cm', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Ток проводимости при Uнр, не более', 'value': 0.7, 'unit': 'mA', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Сопротивление изоляции, не менее', 'value': 10000, 'unit': 'MOhm', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Масса, не более', 'value': 32, 'unit': 'kg', 'sourceId': FACTORY_SOURCE_ID},
]

FACTORY_REF = {
    'sourceId': FACTORY_SOURCE_ID,
    'document': 'АО «Завод энергозащитных устройств»',
    'title': 'Ограничители перенапряжений для подвижного состава 25 кВ — ОПН-25М УХЛ1',
    'url': FACTORY_URL,
    'locator': 'таблица «Основные характеристики ограничителей перенапряжений»'
}


def read_gz(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def write_gz(path, data):
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='', mode='wb', fileobj=out, mtime=0, compresslevel=9) as gz:
            gz.write(raw)


def unique_refs(items):
    out, seen = [], set()
    for item in items:
        key = item.get('sourceId') if isinstance(item, dict) else str(item)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def kb_params():
    return [{
        'name': p['name'],
        'value': p['value'],
        'unit': p['unit'],
        'applicability': 'ОПН-25М УХЛ1; параметры аппарата',
        'status': 'BASE_CONFIRMED',
        'sourceRefs': [p['sourceId']],
    } for p in PARAMETERS]


def patch_equipment(path):
    root = read_gz(path)
    root.setdefault('sourceRegistry', {})['OPN25M_FACTORY'] = FACTORY_REF
    rec = next(x for x in root['records'] if x.get('id') == EQUIPMENT_ID)
    rec['purpose'] = (
        'Ограничение атмосферных и коммутационных перенапряжений в первичной цепи 25 кВ '
        'и защита изоляции высоковольтного оборудования секции.'
    )
    rec['parameters'] = PARAMETERS
    rec['sourceRefs'] = unique_refs(rec.get('sourceRefs', []) + [FACTORY_REF])
    rec['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    rec['notes'] = [n for n in rec.get('notes', []) if not n.startswith('ОПН-25М:')] + [
        'ОПН-25М: нелинейный ограничитель перенапряжений на основе оксидно-цинковых резистивных элементов в герметичном изоляционном корпусе; в штатном режиме практически не влияет на первичную цепь, а при импульсе перенапряжения резко снижает сопротивление и ограничивает напряжение.',
        'Аппарат работает как защитный шунтирующий элемент и не является коммутационным устройством. На базовых 2ЭС5К/3ЭС5К установлен один ОПН-25М УХЛ1 (F1) на секцию.',
        'Для осмотра важны целостность наружной изоляции, отсутствие следов перекрытия, трещин, сколов, выраженного загрязнения и повреждений присоединений. Любые действия на крышевом высоковольтном оборудовании выполняются только по установленному порядку допуска.'
    ]
    if root.get('statistics') is not None:
        root['statistics']['recordsWithParameters'] = sum(bool(x.get('parameters')) for x in root['records'])
        root['statistics']['recordsWithoutParameters'] = len(root['records']) - root['statistics']['recordsWithParameters']
    write_gz(path, root)


def patch_knowledge(path):
    root = read_gz(path)
    article = next(x for x in root['articles'] if x.get('id') == ARTICLE_ID)
    article['summary'] = (
        'ОПН-25М УХЛ1 защищает изоляцию первичной высоковольтной цепи секции от атмосферных '
        'и коммутационных перенапряжений, ограничивая амплитуду импульса до безопасного для оборудования уровня.'
    )
    article['principle'] = (
        'В нормальном режиме нелинейные резистивные элементы ограничителя имеют высокое сопротивление. '
        'При перенапряжении их сопротивление резко уменьшается, импульсный ток отводится через защитный '
        'аппарат, а напряжение на защищаемом оборудовании ограничивается. После исчезновения импульса '
        'ОПН возвращается в высокоомное состояние.'
    )
    article['keyParameters'] = kb_params()
    article['normalState'] = [
        'Наружная изоляция без видимых трещин, сколов и следов электрического перекрытия.',
        'Присоединения и крепление без видимых повреждений, следов перегрева или ослабления.',
        'Корпус и защитная арматура без механических повреждений и выраженного загрязнения.'
    ]
    article['deviationSigns'] = [
        'Трещины, сколы либо следы перекрытия по поверхности изолятора.',
        'Следы перегрева, обгорания или повреждения высоковольтного присоединения.',
        'Механическое повреждение корпуса, крепления либо состояние изоляции, способное снизить электрическую прочность.'
    ]
    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, FACTORY_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('ОПН-25М')]
    rules.append(
        'ОПН-25М УХЛ1 подтверждён базовым руководством 2ЭС5К/3ЭС5К. Паспортные значения взяты '
        'из актуальной таблицы производителя для ОПН-25М; фактический тип на модернизированной секции сверять по маркировке.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak OPN-25M surge arrester reference enriched in app and patch mirrors')
