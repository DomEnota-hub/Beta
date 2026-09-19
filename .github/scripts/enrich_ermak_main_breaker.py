#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-HV-004'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-HV-004'
MANUAL_SOURCE_ID = 'ER-SRC-005'
MAKER_SOURCE_ID = 'ER-SRC-032'
TO2_SOURCE_ID = 'ER-SRC-038'
TO2_URL = 'https://zinref.ru/000_uchebniki/04600_raznie_3/080_eletrovoz_2s5k_TO2/004.htm'

EXTRA_PARAMETERS = [
    {
        'name': 'Наибольшее рабочее напряжение',
        'value': 29,
        'unit': 'kV',
        'sourceId': TO2_SOURCE_ID,
        'condition': 'ВОВ-25А-10/400 УХЛ1'
    },
    {
        'name': 'Номинальный ток оперативной коммутации',
        'value': 10,
        'unit': 'A',
        'sourceId': TO2_SOURCE_ID,
        'condition': 'ВОВ-25А-10/400 УХЛ1'
    },
]

TO2_REF = {
    'sourceId': TO2_SOURCE_ID,
    'document': 'Материалы ТО-2 электровоза 2ЭС5К',
    'title': 'Выключатель ВОВ-25А-10/400 УХЛ1: состав и контроль',
    'url': TO2_URL,
    'locator': 'технологическая карта КЭ 58'
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


def merge_parameters(existing):
    names = {p.get('name') for p in existing}
    return existing + [p for p in EXTRA_PARAMETERS if p['name'] not in names]


def kb_parameters(parameters):
    result = []
    for p in parameters:
        result.append({
            'name': p.get('name'),
            'value': p.get('value'),
            'unit': p.get('unit', ''),
            'applicability': p.get('condition', 'ВОВ-25А-10/400 УХЛ1; 2ЭС5К/3ЭС5К по базовому РЭ'),
            'status': 'BASE_CONFIRMED',
            'sourceRefs': [p.get('sourceId', MAKER_SOURCE_ID)]
        })
    return result


def patch_equipment(path: Path):
    root = read_gz(path)
    root.setdefault('sourceRegistry', {})['ES5K_VOV_TO2'] = TO2_REF
    record = next(r for r in root['records'] if r.get('id') == EQUIPMENT_ID)
    record['parameters'] = merge_parameters(record.get('parameters', []))
    record['sourceRefs'] = unique_refs(record.get('sourceRefs', []) + [TO2_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(record['parameters'])}
    record['purpose'] = (
        'Оперативное включение и отключение секции от контактной сети и аварийное отключение '
        'тягового трансформатора; после отключения первичная высоковольтная цепь переводится '
        'в безопасное заземлённое состояние штатным механизмом выключателя.'
    )
    notes = [n for n in record.get('notes', []) if not n.startswith('ВОВ-25А-10/400:')]
    notes += [
        'ВОВ-25А-10/400: однополюсный высоковольтный воздушный выключатель для сети 25 кВ, 50 Гц. Сжатый воздух используется как рабочая среда выключателя; номинальное избыточное давление в баке — 0,8 МПа.',
        'В состав узла входят дугогасительная камера, воздухопроводный изолятор, разъединитель, блок управления и воздушный резервуар; комплектно с выключателем применяется трансформатор тока ТПОФ-25.',
        'Базовое руководство 2ЭС5К/3ЭС5К прямо включает ВОВ-25А-10/400 УХЛ1. При сверке конкретного локомотива учитывать фактическую маркировку аппарата и исполнение секции.'
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
        'Главный выключатель ВОВ-25А-10/400 связывает контактную сеть 25 кВ с первичной цепью '
        'тягового трансформатора секции и обеспечивает как штатную коммутацию, так и быстрое '
        'отключение при аварийных режимах.'
    )
    article['principle'] = (
        'На каждой секции установлен один ВОВ-25А-10/400 УХЛ1. Аппарат выполнен воздушным: '
        'для его работы требуется запас сжатого воздуха. При включении он подаёт питание на '
        'первичную цепь тягового трансформатора; при команде защиты или штатном отключении '
        'разрывает высоковольтную цепь. Конструктивно узел включает дугогасительную камеру, '
        'воздухопроводный изолятор, разъединитель, блок управления и воздушный резервуар. '
        'С выключателем связан трансформатор тока ТПОФ-25, а отключение по аварийному току '
        'формируется цепями защиты главного выключателя.'
    )
    article['keyParameters'] = kb_parameters(
        next(r for r in read_gz(path.parent / 'ermak_equipment.json.gz')['records'] if r.get('id') == EQUIPMENT_ID)
        .get('parameters', [])
    ) if (path.parent / 'ermak_equipment.json.gz').exists() else article.get('keyParameters', [])
    article['normalState'] = [
        'Выключатель включается только при выполненных штатных блокировках и достаточном давлении сжатого воздуха.',
        'После включения первичная цепь тягового трансформатора получает питание без срабатывания максимальной или земляной защиты.',
        'Положение аппарата и индикация соответствуют поданной команде; выраженной утечки воздуха из привода нет.'
    ]
    article['deviationSigns'] = [
        'Главный выключатель не включается при наличии команды и выполненных внешних условий.',
        'Главный выключатель отключается после включения или срабатывает при наборе тяги.',
        'Наблюдается утечка сжатого воздуха, неполное срабатывание механизма либо несоответствие фактического положения индикации.',
        'Повторное отключение защитой рассматривается как симптом неисправности цепи или оборудования, а не как основание для многократного повторного включения.'
    ]
    refs = article.setdefault('sourceRefs', [])
    for ref in [MANUAL_SOURCE_ID, MAKER_SOURCE_ID, TO2_SOURCE_ID]:
        if ref not in refs:
            refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('ВОВ-25А-10/400')]
    rules.append('ВОВ-25А-10/400 УХЛ1 указан в базовом руководстве 2ЭС5К/3ЭС5К; фактическое исполнение аппарата на конкретной секции подтверждать по маркировке и документации локомотива.')
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    write_gz(path, root)


for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak VOV-25A-10/400 reference enriched in app and patch mirrors')
