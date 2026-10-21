#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-HV-006'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-HV-006'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
RZD_SOURCE_ID = 'ER-SRC-043'
TECH_SOURCE_ID = 'ER-SRC-044'

RZD_REF = {
    'sourceId': RZD_SOURCE_ID,
    'document': 'ЛВ2.0003 КО, общее руководство по капитальному ремонту электропоездов, утв. распоряжением ОАО «РЖД» №2726р от 25.12.2017',
    'title': 'Высоковольтный ввод с трансформатором тока ТПОФ-25 — основные характеристики',
    'url': 'https://rags.ru/documents/prod/perechen/7/lv2.html',
    'locator': 'Приложение Е, таблица Е.2'
}
TECH_REF = {
    'sourceId': TECH_SOURCE_ID,
    'document': 'Техническое описание трансформатора тока ТПОФ-25',
    'title': 'ТПОФ-25 — назначение, устройство и технические данные',
    'url': 'https://poezdvl.com/vl80c/vl80c_32.html',
    'locator': 'раздел «Трансформатор тока ТПОФ-25»'
}

PARAMETERS = [
    {'name': 'Номинальное напряжение', 'value': 25, 'unit': 'kV', 'sourceId': RZD_SOURCE_ID},
    {'name': 'Номинальный первичный ток', 'value': 400, 'unit': 'A', 'sourceId': RZD_SOURCE_ID},
    {'name': 'Номинальный ток вторичной обмотки', 'value': 25, 'unit': 'A', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Коэффициент трансформации', 'value': '16±0.5', 'unit': '', 'sourceId': TECH_SOURCE_ID, 'condition': 'первичный ток 200–300 А'},
    {'name': 'Коэффициент трансформации', 'value': '16±0.4', 'unit': '', 'sourceId': TECH_SOURCE_ID, 'condition': 'первичный ток 300–600 А'},
    {'name': 'Ток динамической устойчивости, амплитудное значение', 'value': 25, 'unit': 'kA', 'sourceId': RZD_SOURCE_ID},
    {'name': 'Ток термической стойкости', 'value': 10, 'unit': 'kA', 'sourceId': TECH_SOURCE_ID, 'condition': '0.1 с'},
    {'name': 'Масса', 'value': 50, 'unit': 'kg', 'sourceId': RZD_SOURCE_ID},
]


def read_gz(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def write_gz(path, data):
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='', mode='wb', fileobj=out, mtime=0, compresslevel=9) as gz:
            gz.write(raw)


def add_unique_refs(items, extras):
    out, seen = [], set()
    for item in items + extras:
        key = item.get('sourceId') if isinstance(item, dict) else str(item)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def kb_params():
    return [{
        'name': p['name'], 'value': p['value'], 'unit': p['unit'],
        'applicability': p.get('condition', 'ТПОФ-25; параметры самого аппарата'),
        'status': 'BASE_CONFIRMED', 'sourceRefs': [p['sourceId']]
    } for p in PARAMETERS]


def patch_equipment(path):
    root = read_gz(path)
    root.setdefault('sourceRegistry', {})['TPOF25_RZD'] = RZD_REF
    root['sourceRegistry']['TPOF25_TECH'] = TECH_REF
    rec = next(x for x in root['records'] if x.get('id') == EQUIPMENT_ID)
    rec['purpose'] = (
        'Измерение тока первичной высоковольтной цепи и формирование вторичного сигнала для '
        'максимальной токовой защиты главного выключателя. Конструктивно ТПОФ-25 также служит '
        'высоковольтным вводом цепи 25 кВ в кузов секции.'
    )
    rec['parameters'] = PARAMETERS
    rec['sourceRefs'] = add_unique_refs(rec.get('sourceRefs', []), [RZD_REF, TECH_REF])
    rec['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    rec['notes'] = [n for n in rec.get('notes', []) if not n.startswith('ТПОФ-25:')] + [
        'ТПОФ-25: первичный ток проходит по токоведущему стержню внутри полого фарфорового изолятора; катушка с магнитопроводом формирует пропорциональный вторичный ток для защитной цепи.',
        'Сам трансформатор тока не отключает высоковольтную цепь: его сигнал используется реле максимального тока, которое инициирует отключение главного выключателя.',
        'Применение ТПОФ-25 на базовых 2ЭС5К/3ЭС5К подтверждено заводским РЭ; на модернизированной секции фактический тип аппарата сверять по маркировке и документации.'
    ]
    if root.get('statistics') is not None:
        root['statistics']['recordsWithParameters'] = sum(bool(x.get('parameters')) for x in root['records'])
        root['statistics']['recordsWithoutParameters'] = len(root['records']) - root['statistics']['recordsWithParameters']
    write_gz(path, root)


def patch_knowledge(path):
    root = read_gz(path)
    article = next(x for x in root['articles'] if x.get('id') == ARTICLE_ID)
    article['summary'] = (
        'ТПОФ-25 контролирует ток первичной цепи секции, выдаёт вторичный сигнал в канал '
        'максимальной токовой защиты ГВ и одновременно выполняет функцию высоковольтного ввода 25 кВ.'
    )
    article['principle'] = (
        'Первичная цепь проходит через токоведущий стержень ТПОФ-25. Магнитный поток в сердечнике '
        'создаёт во вторичной обмотке ток, пропорциональный первичному; этот сигнал поступает в цепь '
        'реле максимального тока. При превышении установленного порога уже защитная цепь формирует '
        'команду на отключение главного выключателя.'
    )
    article['keyParameters'] = kb_params()
    article['normalState'] = [
        'Фарфоровый изолятор без видимых трещин, сколов, следов перекрытия или пробоя.',
        'Токоведущие выводы и крепления без признаков перегрева, ослабления или механического повреждения.',
        'Канал максимальной токовой защиты получает штатный измерительный сигнал без признаков нарушения цепи.'
    ]
    article['deviationSigns'] = [
        'Трещины, сколы или следы электрического перекрытия на фарфоровом изоляторе.',
        'Следы перегрева, обгорания либо механическое повреждение выводов и креплений.',
        'Признаки нарушения измерительной цепи или несоответствия сигнала канала максимальной токовой защиты.'
    ]
    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, RZD_SOURCE_ID, TECH_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('ТПОФ-25')]
    rules.append(
        'ТПОФ-25 подтверждён базовым руководством 2ЭС5К/3ЭС5К. Числовые характеристики относятся '
        'к аппарату ТПОФ-25; фактическое исполнение модернизированной секции подтверждать по маркировке.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak TPOF-25 reference enriched in app and patch mirrors')
