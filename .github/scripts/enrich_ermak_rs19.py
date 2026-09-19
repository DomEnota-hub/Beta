#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
EQUIPMENT_ID = 'ER-EQ-TR-003'
ARTICLE_ID = 'ER-KB-EQ-ER-EQ-TR-003'
SCHEME_SOURCE_ID = 'ER-SRC-002'
MANUAL_SOURCE_ID = 'ER-SRC-005'
MAINT_SOURCE_ID = 'ER-SRC-051'
TECH_SOURCE_ID = 'ER-SRC-055'
CATALOG_SOURCE_ID = 'ER-SRC-056'
VARIANT_SOURCE_ID = 'ER-SRC-057'

TECH_URL = 'https://infourok.ru/urok-transformatori-elektrovoza-ermak-3322837.html'
CATALOG_URL = 'https://www.b2b-center.ru/market/realizatsiia-nevostrebovannykh-tmts-lot-182-5/tender-3103794/?action=positions'
VARIANT_URL = 'https://scbist.com/xx2/52257-10-2019-osobennosti-elektrovozov-serii-ermak-s-poosnym-regulirovaniem-sily-tyagi.html'
MAINT_URL = 'https://rcit.su/techinfoV58.html'

PARAMETERS = [
    {'name': 'Номинальное напряжение изоляции', 'value': 1400, 'unit': 'V', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Ток продолжительного режима', 'value': 810, 'unit': 'A', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Ток часового режима', 'value': 870, 'unit': 'A', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Начальная индуктивность, не менее', 'value': 11.7, 'unit': 'mH', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Индуктивность при токе 810 А, не менее', 'value': 8.2, 'unit': 'mH', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Охлаждение', 'value': 'воздушное принудительное', 'unit': '', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Расход охлаждающего воздуха', 'value': 20, 'unit': 'm3/min', 'sourceId': TECH_SOURCE_ID},
    {'name': 'Масса', 'value': 443, 'unit': 'kg', 'sourceId': CATALOG_SOURCE_ID},
    {'name': 'Габаритные размеры', 'value': '765×475×600', 'unit': 'mm', 'sourceId': CATALOG_SOURCE_ID},
]

TECH_REF = {'sourceId': TECH_SOURCE_ID, 'document': 'Учебные технические материалы по электрооборудованию электровоза «Ермак»', 'title': 'Реактор сглаживающий РС-19 — назначение, технические характеристики и конструкция', 'url': TECH_URL, 'locator': 'раздел «Реактор сглаживающий РС-19»'}
CATALOG_REF = {'sourceId': CATALOG_SOURCE_ID, 'document': 'Отраслевая номенклатура локомотивного оборудования', 'title': 'Реактор сглаживающий РС-19 6ТС.210.019 — тип, габариты и основные данные', 'url': CATALOG_URL, 'locator': 'позиция «Реактор сглаживающий РС-19 6ТС.210.019»'}
VARIANT_REF = {'sourceId': VARIANT_SOURCE_ID, 'document': 'Особенности электровозов серии «Ермак» с поосным регулированием силы тяги', 'title': 'РС-19-01 в исполнениях Ермак с поосным регулированием', 'url': VARIANT_URL, 'locator': 'перечень отличий электровозов с поосным регулированием'}
MAINT_REF = {'sourceId': MAINT_SOURCE_ID, 'document': 'ИДМБ.661142.009РЭ8, электровоз магистральный 2ЭС5К (3ЭС5К)', 'title': 'Трансформаторы, реакторы и дроссели — техническое обслуживание и текущий ремонт', 'url': MAINT_URL, 'locator': 'пп. 4.3.2, 6.3.2 и 8.3.2'}

def read_gz(path: Path):
    with gzip.open(path, 'rt', encoding='utf-8') as fh: return json.load(fh)

def write_gz(path: Path, payload):
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='', mode='wb', fileobj=out, mtime=0, compresslevel=9) as gz: gz.write(raw)

def unique_refs(items):
    result, seen = [], set()
    for item in items:
        key = item.get('sourceId') if isinstance(item, dict) else str(item)
        if key not in seen: seen.add(key); result.append(item)
    return result

def to_kb_parameters(items):
    return [{'name': p['name'], 'value': p['value'], 'unit': p['unit'], 'applicability': 'РС-19; базовое исполнение 2ЭС5К/3ЭС5К. Значение относится к РС-19 и не переносится автоматически на РС-19-01 для электровозов с поосным регулированием; фактический тип сверять по маркировке и комплекту документации секции.', 'status': 'BASE_CONFIRMED', 'sourceRefs': [p['sourceId']]} for p in items]

def patch_equipment(path: Path):
    root = read_gz(path)
    registry = root.setdefault('sourceRegistry', {})
    registry['RS19_TECHNICAL_DATA'] = TECH_REF
    registry['RS19_INDUSTRY_CATALOG'] = CATALOG_REF
    registry['RS1901_POR_VARIANT'] = VARIANT_REF
    matches = [r for r in root['records'] if r.get('id') == EQUIPMENT_ID]
    if len(matches) != 1: raise SystemExit(f'Expected exactly one {EQUIPMENT_ID} record, found {len(matches)}')
    record = matches[0]
    if 'РС-19' not in record.get('modelNames', []): raise SystemExit(f'Unexpected modelNames for {EQUIPMENT_ID}: {record.get("modelNames")!r}')
    record['schemeDesignations'] = ['L2', 'L3', 'L4', 'L5']
    record['purpose'] = 'Сглаживание пульсаций выпрямленного тока в цепи каждого тягового двигателя, уменьшение бросков тока и улучшение условий коммутации ТЭД.'
    record['parameters'] = PARAMETERS
    record['sourceRefs'] = unique_refs(record.get('sourceRefs', []) + [TECH_REF, CATALOG_REF, VARIANT_REF, MAINT_REF])
    record['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    notes = [n for n in record.get('notes', []) if not n.startswith('РС-19:') and not n.startswith('РС-19-01:')]
    notes += ['РС-19: базовый реактор 6ТС.210.019; в силовой схеме секции реакторы L2–L5 включены в цепи тяговых двигателей.', 'Катушка выполнена из медной шины, намотанной на ребро с межвитковыми зазорами; магнитопровод набран из листов электротехнической стали и изолирован от катушки стеклотекстолитом. Узел стянут шпильками и пропитан электроизоляционным лаком.', 'Принудительное воздушное охлаждение является частью штатных условий работы; нарушение охлаждающего потока повышает риск перегрева реактора.', 'РС-19-01: отдельное исполнение, применяемое на электровозах серии «Ермак» с поосным регулированием силы тяги; паспортные данные базового РС-19 не считать универсальными для РС-19-01.']
    record['notes'] = notes
    stats = root.get('statistics', {})
    if stats:
        stats['recordsWithParameters'] = sum(bool(r.get('parameters')) for r in root['records'])
        stats['recordsWithoutParameters'] = len(root['records']) - stats['recordsWithParameters']
    write_gz(path, root)

def patch_knowledge(path: Path):
    root = read_gz(path)
    matches = [a for a in root['articles'] if a.get('id') == ARTICLE_ID or a.get('equipmentId') == EQUIPMENT_ID]
    by_id = {a.get('id'): a for a in matches}
    if len(by_id) != 1: raise SystemExit(f'Expected exactly one article for {EQUIPMENT_ID}, found {list(by_id)}')
    article = next(iter(by_id.values()))
    article['summary'] = 'РС-19 сглаживает пульсации выпрямленного тока в цепях тяговых двигателей; в базовой схеме секции реакторы L2–L5 работают по одному в цепи каждого ТЭД.'
    article['principle'] = 'Индуктивность сглаживающего реактора препятствует быстрым изменениям тока и уменьшает его пульсации после выпрямительно-инверторного преобразователя. Более плавный ток снижает неблагоприятные броски в тяговой цепи и улучшает условия коммутации тягового двигателя. Для отвода тепла РС-19 использует принудительное воздушное охлаждение.'
    article['keyParameters'] = to_kb_parameters(PARAMETERS)
    article['normalState'] = ['Катушка, магнитопровод, изоляционные детали и защитные элементы визуально целы, без следов перегрева, обугливания и механической деформации.', 'Крепления, стяжные шпильки, выводы и электрические контактные соединения надёжны; следов ослабления и местного перегрева нет.', 'Воздушный тракт не имеет видимых препятствий, а принудительное охлаждение реактора обеспечивается в предусмотренном режиме.', 'Межвитковые зазоры и изоляция катушки визуально сохранены, видимых признаков межвиткового повреждения нет.']
    article['deviationSigns'] = ['Следы перегрева, потемнения или обугливания изоляции, деформация катушки либо повреждение изоляционных деталей.', 'Ослабление креплений, стяжных шпилек, выводов или контактных соединений, а также следы местного перегрева на них.', 'Загрязнение или перекрытие воздушного тракта, отсутствие требуемого принудительного охлаждения или выраженный перегрев реактора.', 'Повреждение магнитопровода, нарушение межвитковых зазоров либо видимые признаки повреждения витковой изоляции.']
    refs = article.setdefault('sourceRefs', [])
    for ref in [SCHEME_SOURCE_ID, MANUAL_SOURCE_ID, MAINT_SOURCE_ID, TECH_SOURCE_ID, CATALOG_SOURCE_ID, VARIANT_SOURCE_ID]:
        if ref not in refs: refs.append(ref)
    rules = [r for r in article.get('variantRules', []) if not r.startswith('РС-19:')]
    rules.append('РС-19: базовая карточка относится к реактору РС-19 (6ТС.210.019), применяемому на 2ЭС5К/3ЭС5К. На электровозах серии «Ермак» с поосным регулированием силы тяги документировано отдельное исполнение РС-19-01 с классом изоляции «Н»; параметры РС-19 и РС-19-01 не смешивать без сверки маркировки и документации конкретной секции.')
    article['variantRules'] = rules
    article.setdefault('knowledgeCoverage', {})['parameters'] = 'documented'
    article.setdefault('atlasData', {})['parameterCoverage'] = {'status': 'documented', 'count': len(PARAMETERS)}
    write_gz(path, root)

for base in ROOTS:
    patch_equipment(base / 'ermak_equipment.json.gz')
    patch_knowledge(base / 'ermak_knowledge.json.gz')

print('Ermak RS-19 smoothing reactor reference enriched in app and patch mirrors')
