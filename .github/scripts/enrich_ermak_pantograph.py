#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-HV-001'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-HV-001'
MANUAL_SOURCE_ID = 'ER-SRC-005'
SCHEME_SOURCE_ID = 'ER-SRC-002'
DATA_SOURCE_ID = 'ER-SRC-039'
DATA_URL = 'https://pu-shilka.profiedu.ru/file/download?id=2891'

PARAMETERS = [
    {'name': 'Номинальное напряжение контактной сети', 'value': 25, 'unit': 'kV', 'sourceId': SCHEME_SOURCE_ID},
    {'name': 'Номинальный ток при движении', 'value': 1300, 'unit': 'A', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Номинальный ток на стоянке', 'value': 130, 'unit': 'A', 'sourceId': DATA_SOURCE_ID, 'condition': 'температура воздуха выше +10 °C'},
    {'name': 'Номинальный ток на стоянке', 'value': 200, 'unit': 'A', 'sourceId': DATA_SOURCE_ID, 'condition': 'температура воздуха +10 °C и ниже'},
    {'name': 'Статическое нажатие активное, не менее', 'value': 60, 'unit': 'N', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Статическое нажатие пассивное, не более', 'value': 90, 'unit': 'N', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Опускающая сила в диапазоне рабочей высоты, не менее', 'value': 120, 'unit': 'N', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Приведённая масса подвижных частей', 'value': 32, 'unit': 'kg', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Время подъёма до максимальной рабочей высоты', 'value': '7–10', 'unit': 's', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Время опускания', 'value': '3.5–6', 'unit': 's', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Диапазон рабочей высоты', 'value': '400–1900', 'unit': 'mm', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Максимальная высота подъёма', 'value': 2100, 'unit': 'mm', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Рабочее давление в баллоне пневмопривода', 'value': 0.24, 'unit': 'MPa', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Максимальная скорость движения электровоза', 'value': 160, 'unit': 'km/h', 'sourceId': DATA_SOURCE_ID},
    {'name': 'Масса токоприёмника', 'value': 123.2, 'unit': 'kg', 'sourceId': DATA_SOURCE_ID},
]

DATA_REF = {
    'sourceId': DATA_SOURCE_ID,
    'document': 'Учебный материал по ТАсС-10-01',
    'title': 'Токоприёмник ТАсС-10-01 — назначение, устройство и технические характеристики',
    'url': DATA_URL,
    'locator': 'раздел «Магистраль питания», технические характеристики'
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
            'applicability': p.get('condition', 'ТАсС-10-01; базовое исполнение 2ЭС5К/3ЭС5К'),
            'status': 'BASE_CONFIRMED',
            'sourceRefs': [p['sourceId']],
        }
        for p in items
    ]


def patch_equipment(path: Path):
    root = read_gz(path)
    root.setdefault('sourceRegistry', {})['TASS10_TECH_DATA'] = DATA_REF
    record = next(r for r in root['records'] if r.get('id') == EQUIPMENT_ID)
    record['purpose'] = (
        'Съём тока с контактной сети 25 кВ и передача его через крышевую высоковольтную '
        'цепь к главному выключателю и далее к тяговому трансформатору секции.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(record.get('sourceRefs', []) + [DATA_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    notes = [n for n in record.get('notes', []) if not n.startswith('ТАсС-10-01:')]
    notes += [
        'ТАсС-10-01: асимметричный токоприёмник с пневматическим приводом, верхней рамой, несущим рычагом, каретками и полозом; подъем обеспечивается сжатым воздухом, опускание — после выпуска воздуха под действием массы подвижной системы.',
        'Базовое руководство 2ЭС5К/3ЭС5К прямо включает ТАсС-10-01 в состав электрических аппаратов; на каждой секции предусмотрен один токоприёмник. Конкретное исполнение на модернизированном локомотиве подтверждать по маркировке и профилю секции.'
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
        'ТАсС-10-01 обеспечивает токосъём с контактного провода и является первым аппаратом '
        'высоковольтного тракта секции перед главным выключателем и тяговым трансформатором.'
    )
    article['principle'] = (
        'Пневмопривод поднимает несущий рычаг и верхнюю раму, выводя каретки с полозом к '
        'контактному проводу. Подрессоренные каретки поддерживают требуемое контактное нажатие '
        'в диапазоне рабочей высоты. После выпуска воздуха подвижная система опускается под '
        'действием собственной массы на буферные устройства. Электрически токоприёмник связан '
        'с крышевыми шинами и главным выключателем секции.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Подъём и опускание происходят без заметных рывков и укладываются в паспортные интервалы времени.',
        'Положение полоза устойчиво, видимых повреждений кареток, рам и контактных вставок нет.',
        'В пневмоприводе отсутствует выраженная утечка воздуха, а фактическое положение соответствует индикации.'
    ]
    article['deviationSigns'] = [
        'Токоприёмник не поднимается, поднимается замедленно либо не удерживает рабочее положение.',
        'Наблюдаются выраженная утечка воздуха, рывки механизма или несоответствие фактического положения индикации.',
        'Есть видимые повреждения полоза, кареток или рам, либо признаки неустойчивого токосъёма.'
    ]
    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, DATA_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('ТАсС-10-01')]
    rules.append(
        'ТАсС-10-01 подтверждён базовым руководством 2ЭС5К/3ЭС5К; на модернизированных секциях '
        'фактический тип токоприёмника подтверждать по маркировке и документации конкретного локомотива.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak TAsS-10-01 pantograph reference enriched in app and patch mirrors')
