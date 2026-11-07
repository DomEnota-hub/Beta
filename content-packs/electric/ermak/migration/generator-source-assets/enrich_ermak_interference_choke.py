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
FACTORY_SOURCE_ID = 'ER-SRC-047'
MAINT_SOURCE_ID = 'ER-SRC-048'
RGUPS_URL = 'https://rgups.ru/site/assets/files/213502/dissertatciia_verigin_o_s__27_09_2024.pdf'
TRAINING_URL = 'https://scbist.com/scb/uploaded/1_1569870485.pdf'
FACTORY_URL = 'https://djvu.online/file/TVgYn3LTUveDJ'
MAINT_URL = 'https://rcit.su/techinfoV58.html'

PARAMETERS = [
    {'name': 'Номинальное напряжение изоляции', 'value': 25, 'unit': 'kV', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Номинальный ток продолжительного режима', 'value': 650, 'unit': 'A', 'sourceId': FACTORY_SOURCE_ID, 'condition': 'при скорости охлаждающего воздуха не менее 25 км/ч'},
    {'name': 'Пусковой ток', 'value': 300, 'unit': 'A', 'sourceId': FACTORY_SOURCE_ID, 'condition': 'при скорости набегающего потока охлаждающего воздуха не более 10 км/ч'},
    {'name': 'Индуктивность', 'value': '250±25', 'unit': 'uH', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Сопротивление катушки постоянному току при 20 °C', 'value': 0.0061, 'unit': 'Ohm', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Охлаждение', 'value': 'воздушное', 'unit': '', 'sourceId': FACTORY_SOURCE_ID},
    {'name': 'Масса', 'value': 38, 'unit': 'kg', 'sourceId': FACTORY_SOURCE_ID},
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

FACTORY_REF = {
    'sourceId': FACTORY_SOURCE_ID,
    'document': 'ИДМБ.661142.004-01 РЭ4, электровоз ЭП1М (ЭП1П)',
    'title': 'Дроссель помехоподавления ДП-011 — назначение, технические характеристики, устройство и работа',
    'url': FACTORY_URL,
    'locator': 'раздел 50 «Дроссель помехоподавления ДП-011»'
}

MAINT_REF = {
    'sourceId': MAINT_SOURCE_ID,
    'document': 'ИДМБ.661142.009РЭ8, электровоз магистральный 2ЭС5К (3ЭС5К)',
    'title': 'Трансформаторы, реакторы и дроссели — обслуживание ДП-011',
    'url': MAINT_URL,
    'locator': 'п. 6.3.2 «Трансформаторы, реакторы и дроссели»'
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
            'applicability': p.get(
                'condition',
                'ДП-011; базовое исполнение 2ЭС5К/3ЭС5К; для модернизаций фактический тип сверять по маркировке'
            ),
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
    registry['DP011_FACTORY_DATA'] = FACTORY_REF
    registry['DP011_MAINTENANCE'] = MAINT_REF
    record = next(r for r in root['records'] if r.get('id') == EQUIPMENT_ID)
    record['purpose'] = (
        'Снижение уровня радиопомех, возникающих при нарушении контакта между токоприёмником '
        'и контактным проводом. Дроссель включён в первичную высоковольтную цепь секции.'
    )
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(
        record.get('sourceRefs', []) + [RGUPS_REF, TRAINING_REF, FACTORY_REF, MAINT_REF]
    )
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    notes = [n for n in record.get('notes', []) if not n.startswith('ДП-011:')]
    notes += [
        'ДП-011: на базовой секции 2ЭС5К/3ЭС5К обозначается L1 и установлен в первичном высоковольтном тракте после токоприёмника.',
        'Катушка намотана на ребро из алюминиевой шины сечением 4×40 мм с межвитковыми зазорами, выполненными электронитовыми прокладками; катушка закреплена на гетинаксовом основании и фарфоровом изоляторе.',
        'ДП-011 не является коммутационным аппаратом: рабочий ток проходит через катушку, а её индуктивность противодействует быстрым изменениям тока, связанным с радиопомехами.',
        'При обслуживании проверяют крепление деталей и контактных соединений, состояние катушки и изоляционных поверхностей, а отдельно — опорный изолятор ДП-011.'
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
        'ДП-011 включён в первичную высоковольтную цепь секции и снижает радиопомехи, '
        'возникающие при нарушении контакта токоприёмника с контактным проводом.'
    )
    article['principle'] = (
        'Рабочий ток первичной цепи проходит через катушку L1. При быстрых изменениях тока, '
        'возникающих при нестабильном контакте токоприёмника с контактным проводом, индуктивность '
        'дросселя препятствует высокочастотной составляющей помехи. Катушка выполнена из алюминиевой '
        'шины 4×40 мм, закреплена на изоляционном основании и фарфоровом опорном изоляторе; охлаждение воздушное.'
    )
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = [
        'Крепление деталей, шин и контактных соединений надёжно; резьбовые соединения не имеют признаков ослабления.',
        'Катушка и изоляционные поверхности без видимых повреждений; покрытие и межвитковые зазоры сохранены.',
        'Опорный фарфоровый изолятор чистый и без недопустимых повреждений; в зимнее время на дросселе отсутствуют снег и лёд.'
    ]
    article['deviationSigns'] = [
        'Повреждение поверхности или сколы опорного изолятора свыше 10% длины пути возможного перекрытия напряжением — такой изолятор к эксплуатации не допускается.',
        'Ослабление креплений, шин или контактных соединений, повреждение изоляционных поверхностей либо защитного покрытия катушки.',
        'Трещины в шине катушки, признаки межвиткового замыкания по результатам проверки, а также снег или лёд на ДП-011 в зимнее время.'
    ]
    refs = article.setdefault('sourceRefs', [])
    for ref in [
        SCHEME_SOURCE_ID,
        MANUAL_SOURCE_ID,
        RGUPS_SOURCE_ID,
        TRAINING_SOURCE_ID,
        FACTORY_SOURCE_ID,
        MAINT_SOURCE_ID,
    ]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('ДП-011')]
    rules.append(
        'ДП-011 подтверждён базовым заводским РЭ 2ЭС5К/3ЭС5К. Паспортные значения и устройство '
        'уточнены по заводскому РЭ того же аппарата ДП-011 на ЭП1М/ЭП1П; основные значения '
        '25 кВ, 650 А, 300 А, 250 мкГн, 0,0061 Ом и 38 кг независимо подтверждены для 3ЭС5К. '
        'На модернизированных секциях фактический тип аппарата сверять по маркировке и документации.'
    )
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak DP-011 interference choke reference enriched in app and patch mirrors')
