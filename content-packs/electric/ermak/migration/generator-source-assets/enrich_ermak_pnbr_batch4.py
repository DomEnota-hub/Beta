#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS = [Path('app/src/main/assets/technical'), Path('patch/app/src/main/assets/technical')]
TARGETS = ['ER-EQ-BR-005','ER-EQ-BR-007','ER-EQ-BR-010','ER-EQ-BR-011']
SCHEME_ID = 'ER-SRC-013'
RE2_ID = 'ER-SRC-003'
MTZ_ID = 'ER-SRC-111'
RZD_ID = 'ER-SRC-112'

MTZ_REF = {
    'sourceId': MTZ_ID,
    'document': 'ОАО «МТЗ ТРАНСМАШ», акт квалификационных испытаний изделий 010-3 и 130-2, 2012',
    'title': 'Состав БКТО 010-3 и крана машиниста 130-2',
    'url': 'https://www.mtz-transmash.ru/files/presscentr/mvk/2012/akt-2.pdf',
    'locator': 'стр. 2–3: БТО 010.20-3; состав 130-2',
}
RZD_REF = {
    'sourceId': RZD_ID,
    'document': 'Распоряжение ОАО «РЖД» от 28.12.2022 №3508/р, ред. 14.01.2025',
    'title': 'Инструкция по ТО, ремонту и испытанию тормозного оборудования: 010.20-3, 130.20-1, 130.30',
    'url': 'https://meganorm.ru/mega_doc/norm_update_01012026/instrukciya/0/instruktsiya_po_tekhnicheskomu_obsluzhivaniyu_remontu_i.html',
    'locator': 'пп. 9.11, 9.12, 9.20; рис. 9.32; таблицы 9.2, 9.3, 9.5, 9.6',
}

RD_PARAMS = [
    {'name':'Время наполнения резервуара 20 л от 0 до 0,35 МПа, не более','value':4,'unit':'s','sourceId':RZD_ID},
    {'name':'Чувствительность поддержания давления при утечке через отверстие 1±0,1 мм','value':'±0.015','unit':'MPa','sourceId':RZD_ID},
    {'name':'Время снижения давления в резервуаре 20 л с 0,35 до 0,04 МПа, не более','value':10,'unit':'s','sourceId':RZD_ID},
    {'name':'Удержание мыльного пузыря при проверке атмосферного клапана','value':5,'unit':'s','sourceId':RZD_ID},
]
KEB_PARAMS = [
    {'name':'Номинальное напряжение исполнения БТО 010.20-3','value':50,'unit':'V','sourceId':RZD_ID},
    {'name':'Диапазон рабочего напряжения ЭПВН','value':'0.7–1.1','unit':'×Uном','sourceId':RZD_ID},
    {'name':'Время наполнения ТЦ от 0 до 0,35 МПа при снятом напряжении, не более','value':4,'unit':'s','sourceId':RZD_ID},
    {'name':'Время снижения давления в ТЦ с 0,35 до 0,04 МПа, не более','value':4,'unit':'s','sourceId':RZD_ID},
]
KRU_PARAMS = [
    {'name':'Рабочие положения рукоятки','value':'отпуск; перекрыша; тормоз','unit':'','sourceId':RZD_ID},
    {'name':'Время наполнения УР 20 л до 0,44 МПа в положении «Отпуск»','value':'30–40','unit':'s','sourceId':RZD_ID},
    {'name':'Изменение давления в УР после ступени торможения 0,05 МПа, не более','value':0.01,'unit':'MPa','sourceId':RZD_ID},
    {'name':'Максимальное подводимое давление сжатого воздуха','value':0.64,'unit':'MPa','sourceId':RZD_ID},
]
KAET_PARAMS = [
    {'name':'Давление в питательной магистрали при стендовом испытании','value':0.69,'unit':'MPa','sourceId':RZD_ID},
    {'name':'Время снижения давления в резервуаре 55 л с 0,49 до 0,25 МПа, не более','value':3,'unit':'s','sourceId':RZD_ID},
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
    if stats.get('recordsWithParameters')!=72 or stats.get('recordsWithoutParameters')!=39:
        raise SystemExit(f"Live statistics changed: {stats.get('recordsWithParameters')}/{stats.get('recordsWithoutParameters')}")
    reg=root.setdefault('sourceRegistry',{})
    register_source(reg,'BTO0103_AND_KM130_COMPOSITION',MTZ_REF)
    register_source(reg,'RZD_BRAKE_REPAIR_3508R_2025',RZD_REF)
    scheme=source_by_id(reg,SCHEME_ID)
    re2=source_by_id(reg,RE2_ID)

    rd=record(root,'ER-EQ-BR-005')
    keb=record(root,'ER-EQ-BR-007')
    kru=record(root,'ER-EQ-BR-010')
    kaet=record(root,'ER-EQ-BR-011')

    if rd.get('name')!='Реле давления тормозных цилиндров' or rd.get('schemeDesignations')!=['РД1','РД2'] or rd.get('modelNames')!=[]:
        raise SystemExit('BR-005 identity changed')
    if keb.get('name')!='Электроблокировочные клапаны тормоза' or keb.get('schemeDesignations')!=['КЭБ1','КЭБ2'] or keb.get('modelNames')!=[]:
        raise SystemExit('BR-007 identity changed')
    if kru.get('name')!='Кран резервного управления тормозами' or kru.get('schemeDesignations')!=['КРУ'] or kru.get('modelNames')!=[]:
        raise SystemExit('BR-010 identity changed')
    if kaet.get('name')!='Клапаны аварийно-экстренного торможения' or kaet.get('schemeDesignations')!=['SQ3','SQ4'] or kaet.get('modelNames')!=[]:
        raise SystemExit('BR-011 identity changed')
    if any(r.get('parameters') for r in (rd,keb,kru,kaet)):
        raise SystemExit('One selected record already has parameters; review concurrent change')

    neighbor_counts={
        'ER-EQ-BR-004':3,'ER-EQ-BR-009':2,'ER-EQ-BR-012':1,'ER-EQ-BR-014':5,
        'ER-EQ-BR-001':0,'ER-EQ-BR-002':0,'ER-EQ-BR-003':0,'ER-EQ-BR-008':0,
        'ER-EQ-PN-005':0,'ER-EQ-PN-007':0,
    }
    for eid,count in neighbor_counts.items():
        got=len(record(root,eid).get('parameters',[]))
        if got!=count:
            raise SystemExit(f'Neighbor {eid} changed: {got} != {count}')

    rd['modelNames']=['042.010']
    rd['purpose']='Пневматическое реле, повторяющее управляющее давление в тормозных цилиндрах тележек с требуемым расходом воздуха и обеспечивающее их наполнение и отпуск.'
    rd['parameters']=RD_PARAMS
    rd['sourceRefs']=unique_refs(rd.get('sourceRefs',[])+[scheme,MTZ_REF,RZD_REF])
    rd['parameterCoverage']={'status':'documented','count':len(RD_PARAMS)}
    rd['notes']=[
        'В квалификационном составе БТО 010.20-3 для блока 010-3 прямо указано реле давления 042; действующая инструкция уточняет исполнение 042.010.',
        'Параметры таблицы 9.5 относятся к испытанию реле давления 042.010: резервуар 20 л, чувствительность и темпы наполнения/отпуска.',
        'Не переносить на РД1/РД2 характеристики реле давления 404: 404 встречается в другой тормозной компоновке и не является реле БТО 010.20-3.'
    ]

    keb['modelNames']=['208-1','208-1-02']
    keb['purpose']='Электропневматическая блокировка тормозных цепей в БТО 010.20-3: коммутация управляющих полостей и выпуск воздуха в предусмотренных режимах отпуска и блокировки.'
    keb['parameters']=KEB_PARAMS
    keb['sourceRefs']=unique_refs(keb.get('sourceRefs',[])+[scheme,MTZ_REF,RZD_REF])
    keb['parameterCoverage']={'status':'documented','count':len(KEB_PARAMS)}
    keb['notes']=[
        'Для БТО 010.20-3 (50 В) действующая инструкция перечисляет два электроблокировочных клапана: 208-1 и 208-1-02; исполнения 208-1-01 и 208-1-03 относятся к варианту 110 В.',
        'Таблица 9.6 задаёт динамические проверки 208-1 и диапазон рабочего напряжения 0,7–1,1 Uном.',
        'Квалификационный акт 010-3 использует более раннюю запись 208-1 (208-2); её нельзя трактовать как разрешение смешивать паспорт 208-2 с текущими 208-1/208-1-02.'
    ]

    kru['modelNames']=['130.20-1']
    kru['purpose']='Резервное непосредственное пневматическое управление тормозами при отказе дистанционного электрического управления краном машиниста семейства 130.'
    kru['parameters']=KRU_PARAMS
    kru['sourceRefs']=unique_refs(kru.get('sourceRefs',[])+[scheme,re2,MTZ_REF,RZD_REF])
    kru['parameterCoverage']={'status':'documented','count':len(KRU_PARAMS)}
    kru['notes']=[
        'Квалификационный состав крана машиниста 130-2 прямо включает КРУ 130.20-1; действующая инструкция содержит отдельную таблицу его испытаний.',
        'Идентичность 130.20-1 применяется только к профилю дистанционного тормозного управления 130; для профиля с краном 395 эту модель не считать установленной автоматически.',
        'Не переносить параметры кранов резервного управления 025А/025Л на 130.20-1: это другие исполнения.'
    ]

    kaet['modelNames']=['130.30']
    kaet['purpose']='Аварийная непосредственная разрядка тормозной магистрали по нажатию кнопки КАЭТ с одновременным переключением контрольного контакта.'
    kaet['parameters']=KAET_PARAMS
    kaet['sourceRefs']=unique_refs(kaet.get('sourceRefs',[])+[scheme,re2,MTZ_REF,RZD_REF])
    kaet['parameterCoverage']={'status':'documented','count':len(KAET_PARAMS)}
    kaet['notes']=[
        'Кран машиниста 130-2 по квалификационному акту включает клапан аварийного экстренного торможения 130.30; действующая инструкция отдельно нормирует его испытание.',
        'При стендовой проверке 130.30 давление питания составляет 0,69 МПа, а резервуар 55 л должен разрядиться с 0,49 до 0,25 МПа не более чем за 3 с.',
        'Модель 130.30 привязана к профилю КМД130; для иных тормозных профилей наличие и модель аварийного клапана подтверждать отдельно.'
    ]

    stats['recordsWithParameters']=sum(bool(r.get('parameters')) for r in root['records'])
    stats['recordsWithoutParameters']=len(root['records'])-stats['recordsWithParameters']
    write_gz(path,root)


def patch_knowledge(path):
    root=read_gz(path)
    rd=article(root,'ER-EQ-BR-005')
    keb=article(root,'ER-EQ-BR-007')
    kru=article(root,'ER-EQ-BR-010')
    kaet=article(root,'ER-EQ-BR-011')

    rd['summary']='РД1/РД2 — реле давления 042.010 в БТО 010.20-3, наполняющие и разряжающие тормозные цилиндры тележек по управляющему давлению.'
    rd['principle']='Управляющее давление воздействует на диафрагменный узел реле, который открывает либо закрывает питательный и атмосферный каналы. За счёт этого большой объём тормозных цилиндров следует за управляющим давлением без пропуска полного расхода через управляющий аппарат.'
    rd['keyParameters']=kb_params(RD_PARAMS,'Реле давления 042.010 в БТО 010.20-3 для РД1/РД2; не смешивать с 404.')
    rd['normalState']=[
        'Тормозные цилиндры обеих тележек набирают и отпускают давление без заметной асимметрии и зависания.',
        'Реле поддерживает заданное давление при малой контролируемой утечке в пределах чувствительности ±0,015 МПа.',
        'Места соединений и атмосферный клапан сохраняют требуемую герметичность.'
    ]
    rd['deviationSigns']=[
        'Одна тележка заметно медленнее набирает или отпускает давление при исправной подводящей цепи.',
        'Давление не удерживается при малой утечке либо возникает самопроизвольный набор/отпуск.',
        'Есть постоянная утечка через атмосферный клапан или соединения.'
    ]
    rd['sourceRefs']=unique_strings(rd.get('sourceRefs',[])+[SCHEME_ID,MTZ_ID,RZD_ID])
    rd['variantRules']=unique_strings(rd.get('variantRules',[])+[
        'Для РД1/РД2 БТО 010.20-3 использовать 042.010; паспорт реле 404 не переносить на эту карточку.'
    ])

    keb['summary']='КЭБ1/КЭБ2 — пара электроблокировочных клапанов 208-1 и 208-1-02 в 50-вольтовом БТО 010.20-3, управляющая блокировкой и выпуском воздуха тормозных цепей.'
    keb['principle']='Электропневматический вентиль переводит поршень клапана между пневматическими состояниями, соединяя требуемые полости либо с питанием, либо с атмосферой. В составе БТО пара клапанов выполняет разные ветви блокировки и отпуска.'
    keb['keyParameters']=kb_params(KEB_PARAMS,'208-1 и 208-1-02 в БТО 010.20-3 (50 В); 110-вольтовые суффиксы хранить отдельно.')
    keb['normalState']=[
        'Оба клапана чётко переключают пневматические каналы при штатном управляющем напряжении.',
        'Наполнение и выпуск ТЦ укладываются в нормативные времена испытания.',
        'В отключённом и включённом состояниях отсутствуют недопустимые утечки через соединения и клапанные пары.'
    ]
    keb['deviationSigns']=[
        'Клапан не переключается либо переключается нестабильно при исправной электрической цепи.',
        'Наполнение или отпуск ТЦ выходит за нормативное время.',
        'Появляется постоянная утечка, неполный отпуск или нежелательная блокировка тормоза.'
    ]
    keb['sourceRefs']=unique_strings(keb.get('sourceRefs',[])+[SCHEME_ID,MTZ_ID,RZD_ID])
    keb['variantRules']=unique_strings(keb.get('variantRules',[])+[
        'В БТО 010.20-3 (50 В) хранить 208-1 и 208-1-02; 208-1-01/208-1-03 относятся к 110-вольтовому исполнению.',
        'Не подменять эти клапаны данными 208-2 только на основании ранней групповой записи 208-1 (208-2).'
    ])

    kru['summary']='КРУ 130.20-1 — резервный пневматический орган управления тормозами профиля КМД130, позволяющий управлять торможением без штатного дистанционного электрического канала.'
    kru['principle']='Перевод рукоятки между положениями «Отпуск», «Перекрыша» и «Тормоз» напрямую изменяет давление уравнительного резервуара и связанной тормозной магистрали. Это сохраняет базовую возможность управления при отказе электрической части дистанционного крана.'
    kru['keyParameters']=kb_params(KRU_PARAMS,'КРУ 130.20-1 только для профиля brake_130_uktol / base_remote_brake_control.')
    kru['normalState']=[
        'Рукоятка чётко занимает три предусмотренных положения, без заеданий и самопроизвольного смещения.',
        'В «Отпуске» уравнительный резервуар набирает 0,44 МПа за 30–40 с.',
        'В «Перекрыше» после ступени 0,05 МПа изменение давления не превышает 0,01 МПа.'
    ]
    kru['deviationSigns']=[
        'Не обеспечивается зарядка УР/ТМ или темп заметно выходит за норматив.',
        'В перекрыше давление уходит больше допустимого при исправной внешней пневматике.',
        'Рукоятка или клапанный механизм заедают, либо имеется постоянная утечка.'
    ]
    kru['sourceRefs']=unique_strings(kru.get('sourceRefs',[])+[SCHEME_ID,RE2_ID,MTZ_ID,RZD_ID])
    kru['variantRules']=unique_strings(kru.get('variantRules',[])+[
        '130.20-1 относится к профилю дистанционного управления КМД130; для brake_395_if_not_equipped не считать его установленным.',
        'Краны 025А/025Л являются отдельными изделиями и их параметры не переносить на 130.20-1.'
    ])
    kru['atlasData']['applicability']={'models':['2ES5K','3ES5K'],'profiles':['brake_130_uktol','base_remote_brake_control'],'exclusions':['brake_395_if_not_equipped']}

    kaet['summary']='SQ3/SQ4 профиля КМД130 — клапаны аварийного экстренного торможения 130.30, обеспечивающие быструю непосредственную разрядку тормозной магистрали из кабины.'
    kaet['principle']='Нажатие кнопки механически открывает выпускной путь тормозной магистрали и одновременно переключает встроенный контрольный выключатель. При отпускании кнопки клапан закрывается, после чего штатная система восстанавливает зарядное давление.'
    kaet['keyParameters']=kb_params(KAET_PARAMS,'КАЭТ 130.30 для профиля brake_130_uktol / base_remote_brake_control.')
    kaet['normalState']=[
        'При нажатии кнопки происходит быстрая разрядка тормозной магистрали и корректное переключение контрольного контакта.',
        'При отпускании кнопки выпуск закрывается и зарядное давление восстанавливается штатно.',
        'Корпус, соединения и клапанная пара герметичны.'
    ]
    kaet['deviationSigns']=[
        'Разрядка тормозной магистрали идёт медленнее нормы либо не возникает.',
        'После отпускания кнопки сохраняется утечка и зарядное давление не восстанавливается.',
        'Контрольный контакт не переключается синхронно с пневматическим действием.'
    ]
    kaet['sourceRefs']=unique_strings(kaet.get('sourceRefs',[])+[SCHEME_ID,RE2_ID,MTZ_ID,RZD_ID])
    kaet['variantRules']=unique_strings(kaet.get('variantRules',[])+[
        'Идентичность 130.30 относится к профилю КМД130; для других тормозных профилей модель аварийного клапана подтверждать отдельно.'
    ])
    kaet['atlasData']['applicability']={'models':['2ES5K','3ES5K'],'profiles':['brake_130_uktol','base_remote_brake_control'],'exclusions':['brake_395_if_not_equipped','booster_only']}

    for a,params in [(rd,RD_PARAMS),(keb,KEB_PARAMS),(kru,KRU_PARAMS),(kaet,KAET_PARAMS)]:
        a.setdefault('atlasData',{})['parameterCoverage']={'status':'documented','count':len(params)}
        a.setdefault('knowledgeCoverage',{})['parameters']='documented'

    write_gz(path,root)


def main():
    for base in ROOTS:
        patch_equipment(base/'ermak_equipment.json.gz')
        patch_knowledge(base/'ermak_knowledge.json.gz')

if __name__=='__main__':
    main()
