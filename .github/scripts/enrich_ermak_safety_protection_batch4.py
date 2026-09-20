#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
TARGETS = ['ER-EQ-SF-001','ER-EQ-SF-004','ER-EQ-PR-002','ER-EQ-PR-005']
RE1_ID='ER-SRC-002'
RE2_ID='ER-SRC-003'
RE4_ID='ER-SRC-005'
KLUB_ID='ER-SRC-107'
SAUT_ID='ER-SRC-108'
ERMAK_PROT_ID='ER-SRC-109'
PROT_TECH_ID='ER-SRC-110'

KLUB_REF={
    'sourceId':KLUB_ID,
    'document':'НТЦ ИРЗ, КЛУБ-У',
    'title':'КЛУБ-У — технические характеристики производителя',
    'url':'https://ntcirz.ru/klub-u',
    'locator':'раздел «Технические характеристики»',
}
SAUT_REF={
    'sourceId':SAUT_ID,
    'document':'ГРСИ РФ №24132-07',
    'title':'САУТ-ЦМ/485 — описание типа и технические характеристики',
    'url':'https://grmetr.ru/gosreestr/329060-24132-07-saut-tsm-485',
    'locator':'таблица 2 «Основные метрологические и технические характеристики»',
}
ERMAK_PROT_REF={
    'sourceId':ERMAK_PROT_ID,
    'document':'Учебный материал по электрическим аппаратам 2ЭС5К',
    'title':'Уставки аппаратов 2ЭС5К: ПЗКО-844 и РТ-546-1',
    'url':'https://studopedia.net/13_14030_perechen-sostavnih-chastey-bloka-silovih-apparatov-a-a.html',
    'locator':'Приложение Е, таблица Е.1',
}
PROT_TECH_REF={
    'sourceId':PROT_TECH_ID,
    'document':'Учебно-технический материал по электрическим аппаратам 2ЭС5К',
    'title':'РТ-546-1 и ПЗКО-844 — технические характеристики',
    'url':'https://studopedia.net/20_24290_rele-peregruzki-tipov-rt--rt--rt--.html',
    'locator':'таблица характеристик РТ-253/РТ-255/РТ-546-1 и раздел 7.15 ПЗКО-844',
}

KLUB_PARAMS=[
    {'name':'Потребляемая мощность, не более','value':300,'unit':'W','sourceId':KLUB_ID},
    {'name':'Рабочая температура','value':'−40…+55','unit':'°C','sourceId':KLUB_ID},
    {'name':'Срок службы','value':20,'unit':'years','sourceId':KLUB_ID},
    {'name':'Поддерживаемые напряжения сети постоянного тока','value':'50; 75; 110','unit':'V','sourceId':KLUB_ID},
]
SAUT_PARAMS=[
    {'name':'Напряжение питания постоянного тока','value':50,'unit':'V','sourceId':SAUT_ID},
    {'name':'Потребляемая мощность, не более','value':60,'unit':'W','sourceId':SAUT_ID},
    {'name':'Сопротивление изоляции входных и выходных цепей, не менее','value':20,'unit':'MOhm','sourceId':SAUT_ID},
    {'name':'Испытательное напряжение изоляции в течение 60±5 с, не менее','value':1200,'unit':'V','sourceId':SAUT_ID},
    {'name':'Рабочая температура','value':'−40…+50','unit':'°C','sourceId':SAUT_ID},
    {'name':'Относительная влажность при 40 °C, не более','value':93,'unit':'%','sourceId':SAUT_ID},
    {'name':'Средний срок службы, не менее','value':15,'unit':'years','sourceId':SAUT_ID},
    {'name':'Средняя наработка на отказ, не менее','value':35000,'unit':'h','sourceId':SAUT_ID},
]
RT_PARAMS=[
    {'name':'Род тока','value':'переменный','unit':'','sourceId':PROT_TECH_ID},
    {'name':'Номинальное напряжение изоляции катушки (шины)','value':2000,'unit':'V','sourceId':PROT_TECH_ID},
    {'name':'Номинальный ток катушки (шины)','value':1950,'unit':'A','sourceId':PROT_TECH_ID},
    {'name':'Ток уставки','value':'4000±200','unit':'A','sourceId':ERMAK_PROT_ID},
    {'name':'Номинальное напряжение контактов','value':50,'unit':'V','sourceId':PROT_TECH_ID},
    {'name':'Номинальный отключаемый ток контактов при U=50 В и τ=0,05 с','value':3,'unit':'A','sourceId':PROT_TECH_ID},
]
PZKO_PARAMS=[
    {'name':'Род тока главной цепи','value':'пульсирующий','unit':'','sourceId':PROT_TECH_ID},
    {'name':'Коэффициент пульсации','value':45,'unit':'%','sourceId':PROT_TECH_ID},
    {'name':'Номинальное напряжение изоляции','value':1500,'unit':'V','sourceId':PROT_TECH_ID},
    {'name':'Напряжение срабатывания реле','value':'450±50','unit':'V','sourceId':ERMAK_PROT_ID},
]

def read_gz(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:
        return json.load(f)

def write_gz(path,payload):
    raw=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0,compresslevel=9) as gz:
            gz.write(raw)

def record(root,eid):
    rows=[r for r in root['records'] if r.get('id')==eid]
    if len(rows)!=1:
        raise SystemExit(f'Expected one record {eid}, found {len(rows)}')
    return rows[0]

def article(root,eid):
    rows=[a for a in root['articles'] if a.get('equipmentId')==eid]
    if len(rows)!=1:
        raise SystemExit(f'Expected one article {eid}, found {len(rows)}')
    return rows[0]

def unique_strings(items):
    return list(dict.fromkeys(items))

def unique_refs(items):
    out=[]; seen=set()
    for item in items:
        key=item.get('sourceId') if isinstance(item,dict) else str(item)
        if key not in seen:
            seen.add(key); out.append(item)
    return out

def register_source(reg,key,ref):
    if key in reg and reg[key]!=ref:
        raise SystemExit(f'Source key {key} changed concurrently')
    sid=ref['sourceId']
    for old_key,old in reg.items():
        if isinstance(old,dict) and old.get('sourceId')==sid and old_key!=key:
            raise SystemExit(f'Source ID {sid} already used by {old_key}')
    reg[key]=ref

def source_by_id(reg,sid):
    rows=[v for v in reg.values() if isinstance(v,dict) and v.get('sourceId')==sid]
    if len(rows)!=1:
        raise SystemExit(f'Expected one source {sid}, found {len(rows)}')
    return rows[0]

def kb_params(params,applicability):
    return [{
        'name':p['name'],'value':p['value'],'unit':p['unit'],
        'applicability':applicability,'status':'BASE_CONFIRMED','sourceRefs':[p['sourceId']]
    } for p in params]


def patch_equipment(path):
    root=read_gz(path)
    stats=root.get('statistics',{})
    if stats.get('recordsWithParameters')!=68 or stats.get('recordsWithoutParameters')!=43:
        raise SystemExit(f"Live statistics changed: {stats.get('recordsWithParameters')}/{stats.get('recordsWithoutParameters')}")
    reg=root.setdefault('sourceRegistry',{})
    for key,ref in [
        ('KLUBU_MANUFACTURER_DATA',KLUB_REF),
        ('SAUT_CM485_GRSI_DATA',SAUT_REF),
        ('ERMAK_PROTECTION_SETTINGS_TABLE',ERMAK_PROT_REF),
        ('RT546_PZKO_TECH_DATA',PROT_TECH_REF),
    ]:
        register_source(reg,key,ref)
    re1=source_by_id(reg,RE1_ID); re2=source_by_id(reg,RE2_ID); re4=source_by_id(reg,RE4_ID)

    klub=record(root,'ER-EQ-SF-001')
    saut=record(root,'ER-EQ-SF-004')
    rt=record(root,'ER-EQ-PR-002')
    pzko=record(root,'ER-EQ-PR-005')

    if klub.get('name')!='КЛУБ-У' or klub.get('modelNames')!=[] or klub.get('schemeDesignations')!=[]:
        raise SystemExit('SF-001 identity changed')
    if saut.get('name')!='САУТ-ЦМ/485' or saut.get('modelNames')!=[] or saut.get('schemeDesignations')!=[]:
        raise SystemExit('SF-004 identity changed')
    if rt.get('name')!='Реле защиты тяговых обмоток и ВИП' or rt.get('modelNames')!=[] or rt.get('schemeDesignations')!=['KA1-KA6']:
        raise SystemExit('PR-002 identity changed')
    if pzko.get('name')!='Панель защиты ТЭД от кругового огня' or pzko.get('modelNames')!=['ПЗКО-844'] or pzko.get('schemeDesignations')!=[]:
        raise SystemExit('PR-005 identity changed')
    if any(r.get('parameters') for r in (klub,saut,rt,pzko)):
        raise SystemExit('One selected record already has parameters; review concurrent change')

    neighbor_counts={
        'ER-EQ-SF-002':3,'ER-EQ-SF-003':6,'ER-EQ-SF-006':7,'ER-EQ-SF-008':6,
        'ER-EQ-SF-005':0,'ER-EQ-SF-007':0,'ER-EQ-SF-009':0,
        'ER-EQ-PR-001':0,'ER-EQ-PR-004':0,'ER-EQ-PR-006':0,
    }
    for eid,count in neighbor_counts.items():
        got=len(record(root,eid).get('parameters',[]))
        if got!=count:
            raise SystemExit(f'Neighbor {eid} changed: {got} != {count}')

    klub['purpose']='Комплексная локомотивная система безопасности для приёма и обработки сигналов АЛС, контроля скорости и бдительности, определения координаты, регистрации параметров движения и формирования защитных воздействий.'
    klub['parameters']=KLUB_PARAMS
    klub['sourceRefs']=unique_refs(klub.get('sourceRefs',[])+[re1,re2,KLUB_REF])
    klub['parameterCoverage']={'status':'documented','count':len(KLUB_PARAMS)}
    klub['notes']=[
        'РЭ1/РЭ2 Ермака подтверждают применение КЛУБ-У; числовые характеристики добавлены по данным производителя семейства КЛУБ-У.',
        'Значения 50, 75 и 110 В являются поддерживаемыми вариантами питания семейства, а не тремя одновременными напряжениями конкретного электровоза.',
        'Паспортные данные отдельных компонентов КЛУБ-У (БИЛ, ТСКБМ, АУУ и др.) не смешиваются с паспортом комплекса и остаются в их собственных карточках.'
    ]

    saut['purpose']='Локомотивная система автоматического управления торможением: измерение скорости, пути и давления, расчёт допустимых параметров движения и формирование команд торможения.'
    saut['parameters']=SAUT_PARAMS
    saut['sourceRefs']=unique_refs(saut.get('sourceRefs',[])+[re1,re2,SAUT_REF])
    saut['parameterCoverage']={'status':'documented','count':len(SAUT_PARAMS)}
    saut['notes']=[
        'РЭ1/РЭ2 Ермака подтверждают применение САУТ-ЦМ/485; числовые значения относятся к аппаратуре САУТ-ЦМ/485 как к комплектной системе.',
        'Габариты и масса компонентов не переносятся на комплектную систему; пульт ПМ2-САУТ6 остаётся отдельной карточкой без заимствования параметров ПМ3/ПМ4/ПМ6.',
        'Параметры электропитания, изоляции и надёжности взяты из описания типа ГРСИ №24132-07.'
    ]

    rt['modelNames']=['РТ-546-1']
    rt['purpose']='Защита вторичных тяговых цепей и преобразователей от перегрузок и коротких замыканий: шесть реле KA1–KA6 формируют защитное отключение при превышении установленного тока.'
    rt['parameters']=RT_PARAMS
    rt['sourceRefs']=unique_refs(rt.get('sourceRefs',[])+[re1,ERMAK_PROT_REF,PROT_TECH_REF])
    rt['parameterCoverage']={'status':'documented','count':len(RT_PARAMS)}
    rt['notes']=[
        'Таблица уставок 2ЭС5К прямо связывает KA1–KA6 с РТ-546-1 и уставкой 4000±200 А переменного тока.',
        'Техническая таблица РТ-253/РТ-255/РТ-546-1 подтверждает изоляцию 2000 В, номинальный ток шины 1950 А, напряжение контактов 50 В и отключаемый ток 3 А.',
        'Заголовок открытого материала использует написание РТ-546-01, тогда как таблица и таблица уставок Ермака дают РТ-546-1; суффиксные варианты автоматически не объединяются.'
    ]

    pzko['purpose']='Обнаружение опасного напряжения между равнопотенциальными точками якорных цепей тяговых двигателей при круговом огне и выдача защитного воздействия в цепи управления.'
    pzko['parameters']=PZKO_PARAMS
    pzko['sourceRefs']=unique_refs(pzko.get('sourceRefs',[])+[re1,re4,ERMAK_PROT_REF,PROT_TECH_REF])
    pzko['parameterCoverage']={'status':'documented','count':len(PZKO_PARAMS)}
    pzko['notes']=[
        'Для 2ЭС5К панель A27 прямо указана как ПЗКО-844 с уставкой 450±50 В.',
        'Техническое описание ПЗКО-844 подтверждает пульсирующий род тока главной цепи, коэффициент пульсации 45% и номинальное напряжение изоляции 1500 В.',
        'Внутренний элемент контроля — РКН-37; его отдельные паспортные характеристики не выдаются за параметры всей панели.'
    ]

    stats['recordsWithParameters']=sum(bool(r.get('parameters')) for r in root['records'])
    stats['recordsWithoutParameters']=len(root['records'])-stats['recordsWithParameters']
    write_gz(path,root)


def patch_knowledge(path):
    root=read_gz(path)
    klub=article(root,'ER-EQ-SF-001')
    saut=article(root,'ER-EQ-SF-004')
    rt=article(root,'ER-EQ-PR-002')
    pzko=article(root,'ER-EQ-PR-005')

    klub['summary']='КЛУБ-У — комплексная локомотивная система безопасности Ермака, объединяющая контроль сигналов АЛС, скорости, бдительности, местоположения и регистрацию параметров с формированием защитных воздействий.'
    klub['principle']='Комплекс получает сигналы путевых и локомотивных датчиков, определяет фактические параметры движения, сопоставляет их с допустимыми условиями, отображает информацию экипажу, выполняет самодиагностику и при опасном отклонении формирует предусмотренное тормозное воздействие.'
    klub['keyParameters']=kb_params(KLUB_PARAMS,'Семейство КЛУБ-У; варианты 50/75/110 В не считать одновременными напряжениями конкретного профиля Ермака.')
    klub['normalState']=[
        'Самодиагностика комплекса проходит без активных отказов, а основные блоки находятся в связи.',
        'Сигналы АЛС, скорость, координата и ограничения отображаются согласованно с фактическим режимом движения.',
        'Защитные воздействия возникают только при предусмотренных алгоритмом условиях и корректно снимаются после устранения причины.'
    ]
    klub['deviationSigns']=[
        'Пропадают или становятся недостоверными сигналы АЛС, скорости или координаты.',
        'Комплекс выдаёт устойчивую ошибку самодиагностики либо теряет связь между блоками.',
        'Возникает необоснованное защитное торможение или, наоборот, отсутствует ожидаемая реакция при контролируемом нарушении.'
    ]
    klub['sourceRefs']=unique_strings(klub.get('sourceRefs',[])+[RE1_ID,RE2_ID,KLUB_ID])
    klub['variantRules']=unique_strings(klub.get('variantRules',[])+[
        'Напряжения 50/75/110 В хранить как поддерживаемые варианты семейства КЛУБ-У; точное питание конкретного профиля Ермака фиксировать только по схеме его комплектации.',
        'Паспортные характеристики БИЛ-УТ, ТСКБМ и АУУ-1Н не переносить на комплект КЛУБ-У и наоборот.'
    ])

    saut['summary']='САУТ-ЦМ/485 — комплектная локомотивная система автоматического управления торможением, контролирующая скорость, путь и давление и рассчитывающая безопасный режим движения.'
    saut['principle']='Аппаратура получает импульсы датчиков скорости/пути и данные давления, рассчитывает текущие параметры и безопасную траекторию торможения, обменивается данными между блоками по штатным интерфейсам и при необходимости формирует команды управления тормозами.'
    saut['keyParameters']=kb_params(SAUT_PARAMS,'Комплектная аппаратура САУТ-ЦМ/485; параметры отдельных пультов и датчиков хранить раздельно.')
    saut['normalState']=[
        'Каналы скорости, пути и давления выдают достоверные значения, а обмен между блоками устойчив.',
        'Самоконтроль не фиксирует активных отказов, питание и изоляция находятся в допустимом состоянии.',
        'Расчёт ограничений и тормозные команды соответствуют фактическому режиму движения.'
    ]
    saut['deviationSigns']=[
        'Отсутствуют или искажены данные скорости, пути либо давления.',
        'Есть потеря связи между блоками, отказ самодиагностики или нестабильное питание.',
        'Система формирует несоответствующую режиму тормозную команду либо не формирует ожидаемую защитную команду.'
    ]
    saut['sourceRefs']=unique_strings(saut.get('sourceRefs',[])+[RE1_ID,RE2_ID,SAUT_ID])
    saut['variantRules']=unique_strings(saut.get('variantRules',[])+[
        'Параметры ГРСИ относятся к аппаратуре САУТ-ЦМ/485 в целом; габариты, масса и электрические данные ПМ2-САУТ6 должны подтверждаться отдельным паспортом точного пульта.',
        'Не переносить параметры ПМ3/ПМ4/ПМ6 на ПМ2-САУТ6 только из-за принадлежности к семейству САУТ.'
    ])

    rt['summary']='KA1–KA6 — шесть реле перегрузки РТ-546-1, контролирующих вторичные тяговые цепи и преобразователи Ермака по току.'
    rt['principle']='При росте переменного тока шины выше отрегулированной уставки электромагнитное реле притягивает якорь, переключает блокировочный контакт и инициирует защитное отключение. После срабатывания механический блинкер фиксирует событие до ручного возврата.'
    rt['keyParameters']=kb_params(RT_PARAMS,'РТ-546-1 в позициях KA1–KA6 базовой схемы 2ЭС5К/3ЭС5К.')
    rt['normalState']=[
        'Реле возвращено, механический блинкер не показывает срабатывание и регулировка опломбирована.',
        'При штатном тяговом токе отсутствуют ложные срабатывания.',
        'Контактная и магнитная системы не имеют повреждений, заеданий или признаков перегрева.'
    ]
    rt['deviationSigns']=[
        'Реле срабатывает при токе вне допустимой зоны уставки либо нестабильно повторяет срабатывание.',
        'При проверке отсутствует ожидаемое переключение или защитное отключение.',
        'Есть повреждение механизма, контактов, изоляции, пломбы или указателя срабатывания.'
    ]
    rt['sourceRefs']=unique_strings(rt.get('sourceRefs',[])+[RE1_ID,ERMAK_PROT_ID,PROT_TECH_ID])
    rt['variantRules']=unique_strings(rt.get('variantRules',[])+[
        'Для KA1–KA6 использовать идентичность РТ-546-1 из таблицы уставок Ермака; написание РТ-546-01 в заголовке родственного материала не считать автоматическим подтверждением взаимозаменяемости суффиксных исполнений.'
    ])

    pzko['summary']='ПЗКО-844 — панель защиты тяговых двигателей от кругового огня, контролирующая опасную разность потенциалов в якорных цепях и выдающая защитный сигнал.'
    pzko['principle']='Высоковольтные выводы панели подключаются к равнопотенциальным точкам якорей ТЭД. Через выпрямительные столбы и ограничительные резисторы напряжение подаётся на реле РКН-37; при достижении уставки реле переключает контакт цепи управления и запускает защиту.'
    pzko['keyParameters']=kb_params(PZKO_PARAMS,'ПЗКО-844 базовой схемы Ермака, позиция A27; внутренний РКН-37 не считать отдельным паспортом панели.')
    pzko['normalState']=[
        'При отсутствии кругового огня реле панели не сработано и защитная цепь находится в штатном состоянии.',
        'Соединения высоковольтных выводов, выпрямительные столбы, резисторы и РКН-37 не имеют повреждений или перегрева.',
        'Уставка срабатывания находится в пределах 450±50 В и после регулирования реле опломбировано.'
    ]
    pzko['deviationSigns']=[
        'Панель выдаёт защитный сигнал без соответствующей разности потенциалов либо имеет нестабильное срабатывание.',
        'При проверочном напряжении в диапазоне уставки реле не срабатывает.',
        'Обнаружены повреждения РКН-37, выпрямительных столбов, резисторов, изоляционной панели или высоковольтных соединений.'
    ]
    pzko['sourceRefs']=unique_strings(pzko.get('sourceRefs',[])+[RE1_ID,RE4_ID,ERMAK_PROT_ID,PROT_TECH_ID])
    pzko['variantRules']=unique_strings(pzko.get('variantRules',[])+[
        'Параметры внутреннего реле РКН-37 и других вариантов панелей защиты не переносить на ПЗКО-844 без прямого подтверждения.'
    ])

    for a,params in ((klub,KLUB_PARAMS),(saut,SAUT_PARAMS),(rt,RT_PARAMS),(pzko,PZKO_PARAMS)):
        a['atlasData']['parameterCoverage']={'status':'documented','count':len(params)}
        a['knowledgeCoverage']['parameters']='documented'
    write_gz(path,root)

for base in ROOTS:
    patch_equipment(base/'ermak_equipment.json.gz')
    patch_knowledge(base/'ermak_knowledge.json.gz')
print('Enriched Ermak KLUB-U, SAUT-CM/485, RT-546-1 and PZKO-844')
