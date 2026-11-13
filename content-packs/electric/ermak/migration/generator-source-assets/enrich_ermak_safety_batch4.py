#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
TARGETS = ['ER-EQ-SF-002','ER-EQ-SF-003','ER-EQ-SF-006','ER-EQ-SF-008']
RE2_ID = 'ER-SRC-003'
BIL_MANUAL_ID = 'ER-SRC-101'
BILPOM_MANUAL_ID = 'ER-SRC-102'
BIL_METROLOGY_ID = 'ER-SRC-103'
TSKBM_MFG_ID = 'ER-SRC-104'
AUU_EXACT_ID = 'ER-SRC-105'
AUU_BOUNDARY_ID = 'ER-SRC-106'

BIL_MANUAL_REF = {
    'sourceId': BIL_MANUAL_ID,
    'document': 'АО «ИРЗ», 36991-300-00 РЭ',
    'title': 'Комплекты БИЛ — БИЛ-УТ: руководство по эксплуатации',
    'url': 'https://i.irz.ru/uploads/files/70_2.pdf',
    'locator': 'п. 3.4.2.1; исполнение БИЛ-УТ 36991-308-00',
}
BILPOM_MANUAL_REF = {
    'sourceId': BILPOM_MANUAL_ID,
    'document': 'АО «ИРЗ», 36991-310-00-02 РЭ',
    'title': 'Блок БИЛ-ПОМ / БИЛ-В-ПОМ — руководство по эксплуатации',
    'url': 'https://i.irz.ru/uploads/files/70_3.pdf',
    'locator': 'пп. 1.1.5–1.1.11, 3.4.1–3.4.3',
}
BIL_METROLOGY_REF = {
    'sourceId': BIL_METROLOGY_ID,
    'document': 'ФГИС Аршин, описание типа 67274-17',
    'title': 'Каналы измерительные скорости и давления из состава КЛУБ-У — данные БИЛ-УТ',
    'url': 'https://all-pribors.ru/docs/2017-67274-17.pdf',
    'locator': 'таблица основных технических характеристик; строка БИЛ-УТ',
    'note': 'В описании типа встречается обозначение 36691-318-00; значения используются только для явно названного БИЛ-УТ и не переносятся на иные блоки БИЛ.',
}
TSKBM_MFG_REF = {
    'sourceId': TSKBM_MFG_ID,
    'document': 'АО «Нейроком»',
    'title': 'ТСКБМ — магистральное исполнение, характеристики ТСКБМ-К и ТСКБМ-П',
    'url': 'https://www.neurocom.ru/products/ukb/tskbm-basic/',
    'locator': 'раздел «Характеристики»',
}
AUU_EXACT_REF = {
    'sourceId': AUU_EXACT_ID,
    'document': 'Спецремонт-М, каталог оборудования КЛУБ-У',
    'title': 'Антенно-усилительное устройство АУУ-1Н ЦВИЯ.468731.001-01 — технические данные',
    'url': 'https://sklad.spetsremont.ru/catalog/oborudovanie_dlya_elektropoezdov/antenno_usilitelnoe_ustroystvo_auu_1n/',
    'locator': 'таблица технических характеристик',
}
AUU_BOUNDARY_REF = {
    'sourceId': AUU_BOUNDARY_ID,
    'document': 'АО «ИРЗ», КЛУБ-УП 36993-00-00 РЭ',
    'title': 'Состав и габаритно-массовые данные КЛУБ-УП — АУУ-1Н ЦВИЯ.468731.001-01',
    'url': 'https://i.irz.ru/uploads/files/71.pdf',
    'locator': 'таблица габаритных размеров и массы; АУУ-1Н ЦВИЯ.468731.001-01',
    'note': 'Открытые данные по габаритам и массе расходятся с каталогом точной модели; эти величины в паспорт карточки не включаются.',
}

BIL_PARAMS = [
    {'name':'Максимальный ток потребления при проверке','value':1.0,'unit':'A max','sourceId':BIL_MANUAL_ID},
    {'name':'Габаритные размеры, не более','value':'236×253×110','unit':'mm','sourceId':BIL_METROLOGY_ID},
    {'name':'Масса, не более','value':3.5,'unit':'kg','sourceId':BIL_METROLOGY_ID},
]
BILPOM_PARAMS = [
    {'name':'Диапазон напряжения питания','value':'41–55','unit':'V','sourceId':BILPOM_MANUAL_ID},
    {'name':'Ток потребления при проверке, не более','value':0.14,'unit':'A','sourceId':BILPOM_MANUAL_ID},
    {'name':'Рабочая температура окружающей среды','value':'−30…+55','unit':'°C','sourceId':BILPOM_MANUAL_ID},
    {'name':'Степень защиты оболочки','value':'IP32','unit':'','sourceId':BILPOM_MANUAL_ID},
    {'name':'Габаритные размеры БИЛ-В-ПОМ, не более','value':'50×160×84','unit':'mm','sourceId':BILPOM_MANUAL_ID},
    {'name':'Масса БИЛ-В-ПОМ, не более','value':0.7,'unit':'kg','sourceId':BILPOM_MANUAL_ID},
]
TSKBM_PARAMS = [
    {'name':'Система ТСКБМ — входное напряжение','value':'50±30%','unit':'V','sourceId':TSKBM_MFG_ID},
    {'name':'Система ТСКБМ — входной ток, не более','value':0.5,'unit':'A','sourceId':TSKBM_MFG_ID},
    {'name':'ТСКБМ-К — габаритные размеры','value':'100×300×300','unit':'mm','sourceId':TSKBM_MFG_ID},
    {'name':'ТСКБМ-К — масса','value':5.0,'unit':'kg','sourceId':TSKBM_MFG_ID},
    {'name':'ТСКБМ-К — рабочая температура','value':'−50…+50','unit':'°C','sourceId':TSKBM_MFG_ID},
    {'name':'ТСКБМ-П — габаритные размеры','value':'250×180×100','unit':'mm','sourceId':TSKBM_MFG_ID},
    {'name':'ТСКБМ-П — рабочая температура','value':'−40…+40','unit':'°C','sourceId':TSKBM_MFG_ID},
]
AUU_PARAMS = [
    {'name':'Диапазон рабочих частот GPS/ГЛОНАСС','value':'1574–1610','unit':'MHz','sourceId':AUU_EXACT_ID},
    {'name':'Коэффициент усиления МШУ','value':'27–32','unit':'dB','sourceId':AUU_EXACT_ID},
    {'name':'Коэффициент шума входного фильтра + МШУ','value':'<2','unit':'dB','sourceId':AUU_EXACT_ID},
    {'name':'Напряжение питания','value':'5–12','unit':'V','sourceId':AUU_EXACT_ID},
    {'name':'Ток потребления, не более','value':50,'unit':'mA','sourceId':AUU_EXACT_ID},
    {'name':'Рабочая температура','value':'−40…+50','unit':'°C','sourceId':AUU_EXACT_ID},
]


def read_gz(path):
    with gzip.open(path,'rt',encoding='utf-8') as f: return json.load(f)

def write_gz(path,payload):
    raw=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0,compresslevel=9) as gz:
            gz.write(raw)

def record(root,eid):
    rows=[r for r in root['records'] if r.get('id')==eid]
    if len(rows)!=1: raise SystemExit(f'Expected one record {eid}, found {len(rows)}')
    return rows[0]

def article(root,eid):
    rows=[a for a in root['articles'] if a.get('equipmentId')==eid]
    if len(rows)!=1: raise SystemExit(f'Expected one article {eid}, found {len(rows)}')
    return rows[0]

def unique_strings(items): return list(dict.fromkeys(items))
def unique_refs(items):
    out=[]; seen=set()
    for item in items:
        key=item.get('sourceId') if isinstance(item,dict) else str(item)
        if key not in seen: seen.add(key); out.append(item)
    return out

def register_source(reg,key,ref):
    if key in reg and reg[key]!=ref: raise SystemExit(f'Source key {key} changed concurrently')
    sid=ref['sourceId']
    for old_key,old in reg.items():
        if isinstance(old,dict) and old.get('sourceId')==sid and old_key!=key:
            raise SystemExit(f'Source ID {sid} already used by {old_key}')
    reg[key]=ref

def source_by_id(reg,sid):
    rows=[v for v in reg.values() if isinstance(v,dict) and v.get('sourceId')==sid]
    if len(rows)!=1: raise SystemExit(f'Expected one source {sid}, found {len(rows)}')
    return rows[0]

def kb_params(params,applicability):
    return [{'name':p['name'],'value':p['value'],'unit':p['unit'],'applicability':applicability,
             'status':'BASE_CONFIRMED','sourceRefs':[p['sourceId']]} for p in params]


def patch_equipment(path):
    root=read_gz(path)
    if root.get('statistics',{}).get('recordsWithParameters')!=64 or root.get('statistics',{}).get('recordsWithoutParameters')!=47:
        raise SystemExit('Live statistics changed; review concurrent enrichment')
    reg=root.setdefault('sourceRegistry',{})
    for key,ref in [
        ('BIL_UT_MANUFACTURER_RE',BIL_MANUAL_REF),
        ('BIL_V_POM_MANUFACTURER_RE',BILPOM_MANUAL_REF),
        ('BIL_UT_METROLOGY',BIL_METROLOGY_REF),
        ('TSKBM_MANUFACTURER_DATA',TSKBM_MFG_REF),
        ('AUU1N_EXACT_TECH_DATA',AUU_EXACT_REF),
        ('AUU1N_IRZ_BOUNDARY',AUU_BOUNDARY_REF),
    ]: register_source(reg,key,ref)
    re2=source_by_id(reg,RE2_ID)

    bil=record(root,'ER-EQ-SF-002'); pom=record(root,'ER-EQ-SF-003'); tsk=record(root,'ER-EQ-SF-006'); auu=record(root,'ER-EQ-SF-008')
    if bil.get('modelNames')!=['БИЛ-УТ'] or bil.get('schemeDesignations')!=[]: raise SystemExit('SF-002 identity changed')
    if pom.get('modelNames')!=['БИЛ-В-ПОМ'] or pom.get('schemeDesignations')!=[]: raise SystemExit('SF-003 identity changed')
    if tsk.get('modelNames')!=['ТСКБМ-П','ТСКБМ-К'] or tsk.get('schemeDesignations')!=[]: raise SystemExit('SF-006 identity changed')
    if auu.get('modelNames')!=['АУУ-1Н'] or auu.get('schemeDesignations')!=[]: raise SystemExit('SF-008 identity changed')
    if any(x.get('parameters') for x in (bil,pom,tsk,auu)): raise SystemExit('One selected SF record already has parameters')
    for eid in ['ER-EQ-SF-001','ER-EQ-SF-004','ER-EQ-SF-005','ER-EQ-SF-007','ER-EQ-SF-009']:
        if record(root,eid).get('parameters'): raise SystemExit(f'Expected empty neighbor {eid} changed')
    if not record(root,'ER-EQ-SF-010').get('parameters'): raise SystemExit('Expected populated neighbor SF-010 changed')

    bil['purpose']='Основной встраиваемый блок индикации КЛУБ-У на рабочем месте машиниста: отображение фактической, допустимой и целевой скорости, сигналов АЛС, координаты, времени, давления и диагностической информации, а также ввод предусмотренных параметров с клавиатуры.'
    bil['parameters']=BIL_PARAMS
    bil['sourceRefs']=unique_refs(bil.get('sourceRefs',[])+[BIL_MANUAL_REF,BIL_METROLOGY_REF,re2])
    bil['parameterCoverage']={'status':'documented','count':len(BIL_PARAMS)}
    bil['notes']=[
        'РЭ2 Ермака прямо размещает БИЛ-УТ на центральной вертикальной панели пульта машиниста.',
        'Максимальный ток взят из заводской методики проверки комплекта БИЛ-УТ 36991-308-00.',
        'Масса и габариты взяты из метрологического описания типа для явно названного БИЛ-УТ; обозначение исполнения в реестре отличается от заводского обозначения комплекта, поэтому эти данные не переносятся на другие варианты БИЛ.'
    ]

    pom['purpose']='Дублирование критичной информации КЛУБ-У на рабочем месте помощника машиниста: сигнал локомотивного светофора и предусмотренная световая индикация состояния комплекса.'
    pom['parameters']=BILPOM_PARAMS
    pom['sourceRefs']=unique_refs(pom.get('sourceRefs',[])+[BILPOM_MANUAL_REF,re2])
    pom['parameterCoverage']={'status':'documented','count':len(BILPOM_PARAMS)}
    pom['notes']=[
        'РЭ2 Ермака прямо указывает БИЛ-В-ПОМ на пульте помощника машиниста.',
        'Напряжение, ток, температура, степень защиты, габариты и масса относятся именно к исполнению БИЛ-В-ПОМ в руководстве изготовителя.',
        'Не смешивать БИЛ-В-ПОМ с полноразмерным БИЛ-ПОМ: в одном РЭ для них приведены разные габариты и масса.'
    ]

    tsk['purpose']='Телемеханический контроль бодрствования машиниста: ТСКБМ-П принимает/обрабатывает информацию комплекса, ТСКБМ-К обеспечивает блоковую часть системы и взаимодействие с локомотивной аппаратурой безопасности.'
    tsk['parameters']=TSKBM_PARAMS
    tsk['sourceRefs']=unique_refs(tsk.get('sourceRefs',[])+[TSKBM_MFG_REF,re2])
    tsk['parameterCoverage']={'status':'documented','count':len(TSKBM_PARAMS)}
    tsk['notes']=[
        'ТСКБМ-П и ТСКБМ-К хранятся в одной карточке, но их габариты, масса и температурные диапазоны не смешиваются.',
        'Масса ТСКБМ-П сознательно не фиксируется как универсальная: метрологические материалы выделяют исполнения ТСКБМ-П с отличающейся массой.',
        'Параметры питания 50 В ±30% и ток не более 0,5 А относятся к входу системы ТСКБМ в магистральном исполнении.'
    ]

    auu['purpose']='Приём сигналов спутниковых навигационных систем GPS/ГЛОНАСС и их усиление для навигационного канала КЛУБ-У.'
    auu['parameters']=AUU_PARAMS
    auu['sourceRefs']=unique_refs(auu.get('sourceRefs',[])+[AUU_EXACT_REF,AUU_BOUNDARY_REF,re2])
    auu['parameterCoverage']={'status':'documented','count':len(AUU_PARAMS)}
    auu['notes']=[
        'РЭ2 Ермака закрепляет применение спутникового навигационного оборудования КЛУБ-У; карточка относится к точной модели АУУ-1Н.',
        'Радиочастотные и электрические значения взяты для АУУ-1Н ЦВИЯ.468731.001-01.',
        'Габариты и масса намеренно исключены: открытый каталог точной модели и руководство ИРЗ КЛУБ-УП для того же обозначения приводят несовпадающие габаритно-массовые данные; значения не усредняются.'
    ]

    stats=root.get('statistics',{})
    if stats:
        stats['recordsWithParameters']=sum(bool(r.get('parameters')) for r in root['records'])
        stats['recordsWithoutParameters']=len(root['records'])-stats['recordsWithParameters']
    write_gz(path,root)


def patch_knowledge(path):
    root=read_gz(path)
    bil=article(root,'ER-EQ-SF-002'); pom=article(root,'ER-EQ-SF-003'); tsk=article(root,'ER-EQ-SF-006'); auu=article(root,'ER-EQ-SF-008')

    bil['summary']='БИЛ-УТ — основной встраиваемый блок индикации КЛУБ-У в кабине Ермака, отображающий параметры движения, сигналы безопасности, давление и диагностические сообщения.'
    bil['principle']='Блок получает данные КЛУБ-У по интерфейсу, преобразует их в цифровую и световую индикацию и через встроенную клавиатуру позволяет выполнять предусмотренный ввод параметров и команд. Отказ или искажение индикации рассматриваются как неисправность комплекса безопасности.'
    bil['keyParameters']=kb_params(BIL_PARAMS,'БИЛ-УТ на рабочем месте машиниста 2ЭС5К/3ЭС5К; не переносить на БИЛ-У, БИЛ-В или БИЛ-М.')
    bil['normalState']=['После включения КЛУБ-У БИЛ-УТ проходит самоконтроль и устойчиво отображает предусмотренные параметры без выпадения сегментов.','Фактическая/допустимая скорость, сигнал светофора, давление и диагностическая строка изменяются согласованно с состоянием комплекса.','Клавиатура и регулировка яркости работают без залипания и самопроизвольных команд.']
    bil['deviationSigns']=['Нет индикации при наличии питания КЛУБ-У либо часть индикаторов не проходит тест.','Показания зависают, самопроизвольно изменяются или расходятся с другими каналами комплекса.','Клавиатура не принимает команды, имеются признаки перегрева, повреждения соединителей или нестабильного питания.']
    bil['sourceRefs']=unique_strings(bil.get('sourceRefs',[])+[RE2_ID,BIL_MANUAL_ID,BIL_METROLOGY_ID])
    bil['variantRules']=unique_strings(bil.get('variantRules',[])+['БИЛ-УТ не объединять по паспортным данным с БИЛ-У, БИЛ-В, БИЛ-М и другими исполнениями семейства БИЛ.','Габаритно-массовые данные метрологического описания использовать только для явно названного БИЛ-УТ; отличающееся обозначение исполнения не считать основанием для переноса данных на иной блок.'])

    pom['summary']='БИЛ-В-ПОМ — компактный блок индикации КЛУБ-У на рабочем месте помощника машиниста, дублирующий критичные сигналы безопасности.'
    pom['principle']='По данным КЛУБ-У блок отображает локомотивный сигнал и предусмотренную световую информацию. Яркость связана с общей настройкой индикации КЛУБ-У; питание и обмен должны оставаться устойчивыми в рабочем диапазоне.'
    pom['keyParameters']=kb_params(BILPOM_PARAMS,'БИЛ-В-ПОМ установленного типа; параметры не распространять на полноразмерный БИЛ-ПОМ.')
    pom['normalState']=['После включения комплекса индикация соответствует сигналу на основном БИЛ и изменяется синхронно с ним.','Все световые элементы читаемы, яркость регулируется штатно, корпус и соединители без повреждений.','Нет самопроизвольного погасания, мерцания или несогласованности сигналов между рабочими местами.']
    pom['deviationSigns']=['Сигнал на БИЛ-В-ПОМ отсутствует или не соответствует основному БИЛ.','Индикаторы мерцают, частично не работают или самопроизвольно меняют яркость.','Нарушены питание/CAN-соединение, повреждены корпус, разъёмы или крепление.']
    pom['sourceRefs']=unique_strings(pom.get('sourceRefs',[])+[RE2_ID,BILPOM_MANUAL_ID])
    pom['variantRules']=unique_strings(pom.get('variantRules',[])+['БИЛ-В-ПОМ и БИЛ-ПОМ являются различными исполнениями: не переносить между ними габариты, массу и иные паспортные значения.'])

    tsk['summary']='ТСКБМ-П/ТСКБМ-К — комплект телемеханического контроля бодрствования машиниста, взаимодействующий с КЛУБ-У и выдающий информацию о функциональном состоянии машиниста.'
    tsk['principle']='Носимая/приёмная часть формирует данные о состоянии машиниста, а локомотивные блоки ТСКБМ принимают и обрабатывают их, передавая результат в систему безопасности. При потере достоверного контроля КЛУБ-У действует по предусмотренному алгоритму контроля бдительности.'
    tsk['keyParameters']=kb_params(TSKBM_PARAMS,'Параметры внутри карточки разделены по ТСКБМ-К и ТСКБМ-П; общие значения питания помечены как системные.')
    tsk['normalState']=['После включения ТСКБМ проходит контроль и устойчиво обменивается данными с КЛУБ-У.','ТСКБМ-П и ТСКБМ-К не имеют признаков перегрева, повреждения или потери связи.','Индикация состояния и запросы бдительности соответствуют фактическому режиму работы комплекса.']
    tsk['deviationSigns']=['КЛУБ-У фиксирует отсутствие/неисправность ТСКБМ или пропадает устойчивый обмен.','Появляются ложные/непрерывные запросы контроля при исправных внешних условиях.','Есть повреждение корпуса/кабелей, нестабильное питание или выход температуры эксплуатации за допустимые границы.']
    tsk['sourceRefs']=unique_strings(tsk.get('sourceRefs',[])+[RE2_ID,TSKBM_MFG_ID])
    tsk['variantRules']=unique_strings(tsk.get('variantRules',[])+['Параметры ТСКБМ-П и ТСКБМ-К хранить раздельно; системные параметры питания не трактовать как паспорт отдельного блока.','Массу ТСКБМ-П не фиксировать без номера исполнения: для отдельных модификаций встречаются разные значения.'])

    auu['summary']='АУУ-1Н — антенно-усилительное устройство спутникового навигационного канала КЛУБ-У, принимающее GPS/ГЛОНАСС и усиливающее сигнал перед подачей в локомотивную аппаратуру.'
    auu['principle']='Антенная часть принимает сигналы спутниковых систем, входной фильтр и малошумящий усилитель формируют усиленный радиочастотный сигнал для навигационного канала. Потеря приёма приводит к отсутствию корректной спутниковой привязки времени/координаты.'
    auu['keyParameters']=kb_params(AUU_PARAMS,'АУУ-1Н ЦВИЯ.468731.001-01; габариты и масса исключены из-за конфликта открытых данных.')
    auu['normalState']=['При нахождении в зоне уверенного спутникового приёма КЛУБ-У получает навигационные данные и корректирует время/координату.','Корпус, кабель и соединители АУУ-1Н не имеют деформаций, обрывов и повреждения изоляции.','Питание и радиочастотный тракт устойчивы, отсутствуют периодические пропадания приёма при неизменных внешних условиях.']
    auu['deviationSigns']=['После нескольких минут работы КЛУБ-У отсутствует спутниковая коррекция при уверенной зоне приёма.','Есть повреждение корпуса, кабеля, соединителей или нарушение изоляции.','Приём нестабилен, появляются повторяющиеся выпадения координаты/времени при исправном остальном тракте КЛУБ-У.']
    auu['sourceRefs']=unique_strings(auu.get('sourceRefs',[])+[RE2_ID,AUU_EXACT_ID,AUU_BOUNDARY_ID])
    auu['variantRules']=unique_strings(auu.get('variantRules',[])+['Для АУУ-1Н ЦВИЯ.468731.001-01 не фиксировать габариты и массу, пока не установлена причина расхождения открытых данных ИРЗ и каталога точной модели; значения не усреднять.'])

    for a,params in [(bil,BIL_PARAMS),(pom,BILPOM_PARAMS),(tsk,TSKBM_PARAMS),(auu,AUU_PARAMS)]:
        a['atlasData']['parameterCoverage']={'status':'documented','count':len(params)}
        a['knowledgeCoverage']['parameters']='documented'
    write_gz(path,root)

for base in ROOTS:
    patch_equipment(base/'ermak_equipment.json.gz')
    patch_knowledge(base/'ermak_knowledge.json.gz')
print('Enriched Ermak SF-002, SF-003, SF-006 and SF-008')
