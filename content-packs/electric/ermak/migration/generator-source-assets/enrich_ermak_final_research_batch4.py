#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS=[Path('app/src/main/assets/technical'),Path('patch/app/src/main/assets/technical')]
TARGETS=['ER-EQ-MC-001','ER-EQ-SF-005','ER-EQ-MC-006','ER-EQ-PN-005']
ERMAK_SCHEME_ID='ER-SRC-002'
ERMAK_LAYOUT_ID='ER-SRC-003'
ERMAK_MECH_ID='ER-SRC-007'
ERMAK_PNEU_ID='ER-SRC-013'
BOGIE_ID='ER-SRC-115'
CHECK_VALVE_ID='ER-SRC-116'

BOGIE_REF={
 'sourceId':BOGIE_ID,
 'document':'ИДМБ.661142.009РЭ6 (3ТС.001.012РЭ6). Электровоз магистральный 2ЭС5К (3ЭС5К). Руководство по эксплуатации. Книга 6. Механическая часть',
 'title':'Двухосная тележка 2ЭС5К/3ЭС5К: техническая характеристика',
 'url':'https://3uch.ru/textbook/yahemis/fove/ille',
 'locator':'раздел 2 «Тележки», таблица/изображение «Техническая характеристика»: длина, ширина, база и масса тележки',
}
CHECK_VALVE_REF={
 'sourceId':CHECK_VALVE_ID,
 'document':'ИДМБ.661142.009РЭ6 (3ТС.001.012РЭ6). Электровоз магистральный 2ЭС5К (3ЭС5К). Руководство по эксплуатации. Книга 6. Механическая часть',
 'title':'Обратный клапан компрессора ВУ 3,5/10-1450: исполнение 1-10 и техническая характеристика',
 'url':'https://3uch.ru/textbook/yahemis/fove/ille',
 'locator':'раздел 5.1: KO7 защищает компрессор от противодавления; раздел 6.2: клапан 1-10 предназначен для ВУ 3,5/10-1450; таблица характеристик 1-10',
}

BOGIE_PARAMS=[
 {'name':'Длина тележки','value':4780,'unit':'mm','sourceId':BOGIE_ID},
 {'name':'Ширина тележки','value':2750,'unit':'mm','sourceId':BOGIE_ID},
 {'name':'База тележки','value':2900,'unit':'mm','sourceId':BOGIE_ID},
 {'name':'Масса тележки','value':21200,'unit':'kg','sourceId':BOGIE_ID},
 {'name':'Масса тележки с ручным тормозом и гребнесмазывателем АГС8','value':21300,'unit':'kg','sourceId':BOGIE_ID},
]
CHECK_VALVE_PARAMS=[
 {'name':'Рабочее давление','value':'0.6–1.0','unit':'MPa','sourceId':CHECK_VALVE_ID},
 {'name':'Присоединительная резьба','value':'G1 1/2-B','unit':'','sourceId':CHECK_VALVE_ID},
 {'name':'Габаритные размеры','value':'130×86×157','unit':'mm','sourceId':CHECK_VALVE_ID},
 {'name':'Масса','value':5.0,'unit':'kg','sourceId':CHECK_VALVE_ID},
]

def read_gz(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)

def write_gz(path,payload):
    raw=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with path.open('wb') as out:
        with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0,compresslevel=9) as gz:gz.write(raw)

def rec(root,eid):
    rows=[r for r in root['records'] if r.get('id')==eid]
    if len(rows)!=1:raise SystemExit(f'Expected one record {eid}, got {len(rows)}')
    return rows[0]

def art(root,eid):
    rows=[a for a in root['articles'] if a.get('equipmentId')==eid]
    if len(rows)!=1:raise SystemExit(f'Expected one article {eid}, got {len(rows)}')
    return rows[0]

def unique_refs(items):
    out=[];seen=set()
    for x in items:
        key=x.get('sourceId') if isinstance(x,dict) else str(x)
        if key not in seen:seen.add(key);out.append(x)
    return out

def unique_strings(items):return list(dict.fromkeys(items))

def register(reg,key,ref):
    if key in reg and reg[key]!=ref:raise SystemExit(f'Source key changed: {key}')
    sid=ref['sourceId']
    for k,v in reg.items():
        if isinstance(v,dict) and v.get('sourceId')==sid and k!=key:
            raise SystemExit(f'Source ID collision {sid}: {k}')
    reg[key]=ref

def source_by_id(reg,sid):
    rows=[v for v in reg.values() if isinstance(v,dict) and v.get('sourceId')==sid]
    if len(rows)!=1:raise SystemExit(f'Expected source {sid}, got {len(rows)}')
    return rows[0]

def kb_params(params,applicability):
    return [{'name':p['name'],'value':p['value'],'unit':p['unit'],'applicability':applicability,
             'status':'BASE_CONFIRMED','sourceRefs':[p['sourceId']]} for p in params]

def freeze_non_targets_records(root):
    return json.dumps([r for r in root['records'] if r.get('id') not in TARGETS],ensure_ascii=False,sort_keys=True)

def freeze_non_targets_articles(root):
    return json.dumps([a for a in root['articles'] if a.get('equipmentId') not in TARGETS],ensure_ascii=False,sort_keys=True)


def patch_equipment(path):
    root=read_gz(path)
    stats=root.get('statistics',{})
    if stats.get('recordsWithParameters')!=80 or stats.get('recordsWithoutParameters')!=31:
        raise SystemExit(f"Live statistics changed: {stats.get('recordsWithParameters')}/{stats.get('recordsWithoutParameters')}")
    frozen=freeze_non_targets_records(root)
    reg=root.setdefault('sourceRegistry',{})
    register(reg,'ERMAK_RE6_BOGIE_TECH_DATA',BOGIE_REF)
    register(reg,'ERMAK_RE6_CHECK_VALVE_1_10',CHECK_VALVE_REF)
    scheme=source_by_id(reg,ERMAK_SCHEME_ID)
    layout=source_by_id(reg,ERMAK_LAYOUT_ID)
    mech=source_by_id(reg,ERMAK_MECH_ID)
    pneu=source_by_id(reg,ERMAK_PNEU_ID)

    bogie=rec(root,'ER-EQ-MC-001')
    pm2=rec(root,'ER-EQ-SF-005')
    speed=rec(root,'ER-EQ-MC-006')
    ko7=rec(root,'ER-EQ-PN-005')

    if bogie.get('name')!='Двухосная тележка' or bogie.get('modelNames')!=[] or bogie.get('schemeDesignations')!=[]:
        raise SystemExit('MC-001 identity changed')
    if pm2.get('name')!='Пульт машиниста САУТ' or pm2.get('modelNames')!=['ПМ2-САУТ6']:
        raise SystemExit('SF-005 identity changed')
    if speed.get('name')!='Датчик скорости колёсной пары' or speed.get('schemeDesignations')!=['ДС'] or speed.get('modelNames')!=[]:
        raise SystemExit('MC-006 identity changed')
    if ko7.get('name')!='Обратный клапан компрессора' or ko7.get('schemeDesignations')!=['КО7'] or ko7.get('modelNames')!=[]:
        raise SystemExit('PN-005 identity changed')
    if any(x.get('parameters') for x in (bogie,pm2,speed,ko7)):
        raise SystemExit('One selected record already has parameters; review concurrent change')

    bogie['parameters']=BOGIE_PARAMS
    bogie['sourceRefs']=unique_refs(bogie.get('sourceRefs',[])+[mech,BOGIE_REF])
    bogie['parameterCoverage']={'status':'documented','count':len(BOGIE_PARAMS)}
    bogie['notes']=[
      'Числовые данные относятся к базовой двухосной тележке раннего 2ЭС5К/3ЭС5К по РЭ6 2004 года.',
      'Масса 21 300 кг относится именно к тележке с ручным тормозом и гребнесмазывателем АГС8; для обычной тележки РЭ6 даёт 21 200 кг.',
      'Не переносить эти массы и конструктивные параметры на поздние тележки с изменённым моторно-осевым подвешиванием или поосным регулированием без их собственного РЭ.'
    ]

    pm2['sourceRefs']=unique_refs(pm2.get('sourceRefs',[])+[layout])
    pm2['parameterCoverage']={
      'status':'not_required_for_atlas','count':0,
      'reason':'Точная идентичность ПМ2-САУТ6 на Ермаке подтверждена, но отдельный паспорт именно этого исполнения с числовыми характеристиками не установлен; данные ПУ2/ПУ3/ПУ4/ПУ5-САУТ-ЦМ/485 не переносятся.'
    }
    pm2['notes']=[
      'РЭ2 прямо подтверждает установку ПМ2-САУТ6 на правой вертикальной панели пульта машиниста.',
      'Отдельный надёжный паспорт ПМ2-САУТ6 с числовыми характеристиками в доступных источниках не установлен.',
      'Не подменять ПМ2-САУТ6 характеристиками современных ПУ2-САУТ-ЦМ/485, ПУ3-САУТ-ЦМ/485, ПУ4-САУТ-ЦМ/485 или ПУ5-САУТ-ЦМ/485 только по сходству обозначений.'
    ]

    speed['sourceRefs']=unique_refs(speed.get('sourceRefs',[])+[scheme,mech])
    speed['parameterCoverage']={
      'status':'not_required_for_atlas','count':0,
      'reason':'Функция измерения частоты вращения колёсных пар подтверждается схемой Ермака, однако точная модель/исполнение датчика для этой карточки не установлены; семейные характеристики ДСНТ-01 без прямой привязки не переносятся.'
    }
    speed['notes']=[
      'В электрических материалах Ермака измерительные элементы частоты вращения обозначаются BR1–BR4/датчиками угла поворота; карточка сохраняет функциональное имя «датчик скорости колёсной пары».',
      'РЭ6 подтверждает установку датчиков угла поворота на буксовых крышках и механическую передачу вращения от оси, но не указывает точную модель датчика.',
      'Не присваивать ДСНТ-01 или его суффиксное исполнение без прямого документа, связывающего конкретный датчик с 2ЭС5К/3ЭС5К данной комплектации.'
    ]

    ko7['modelNames']=['1-10']
    ko7['purpose']='Защита главного мотор-компрессора ВУ 3,5/10-1450 от противодавления со стороны главных резервуаров и пропуск сжатого воздуха только в сторону резервуаров.'
    ko7['parameters']=CHECK_VALVE_PARAMS
    ko7['sourceRefs']=unique_refs(ko7.get('sourceRefs',[])+[pneu,CHECK_VALVE_REF])
    ko7['parameterCoverage']={'status':'documented','count':len(CHECK_VALVE_PARAMS)}
    ko7['notes']=[
      'РЭ6 в описании системы приготовления воздуха называет КО7 обратным клапаном главного компрессора ВУ 3,5/10-1450.',
      'В разделе 6.2 того же РЭ клапан 1-10 прямо назначен для разгрузки компрессора ВУ 3,5/10-1450; поэтому идентичность КО7 → 1-10 замыкается внутри одного руководства.',
      'Не переносить параметры клапана 1-2: он относится к другому компрессору ВВ 0,05/7-1000.'
    ]

    stats['recordsWithParameters']=sum(bool(r.get('parameters')) for r in root['records'])
    stats['recordsWithoutParameters']=len(root['records'])-stats['recordsWithParameters']
    if freeze_non_targets_records(root)!=frozen:raise SystemExit('Non-target equipment record changed')
    write_gz(path,root)


def patch_knowledge(path):
    root=read_gz(path); frozen=freeze_non_targets_articles(root)
    bogie=art(root,'ER-EQ-MC-001'); pm2=art(root,'ER-EQ-SF-005'); speed=art(root,'ER-EQ-MC-006'); ko7=art(root,'ER-EQ-PN-005')

    bogie['summary']='Двухосная тележка базового Ермака воспринимает массу кузова, передаёт тяговые и тормозные силы и объединяет колесно-моторные блоки, рессорное и тормозное оборудование.'
    bogie['principle']='Кузов опирается на тележку через вторичное подвешивание, рама распределяет вертикальные и горизонтальные нагрузки по буксам и колесным парам, а тяговые и тормозные усилия передаются между кузовом, рамой тележки и рельсом.'
    bogie['keyParameters']=kb_params(BOGIE_PARAMS,'Базовая двухосная тележка раннего 2ЭС5К/3ЭС5К по РЭ6 2004 года; масса 21 300 кг только для тележки с ручным тормозом и АГС8.')
    bogie['normalState']=['Рама, подвешивание, буксовые связи и тормозная рычажная система не имеют повреждений и недопустимых люфтов.','Нагрузка распределена без признаков перекоса, а тележка свободно поворачивается относительно кузова в пределах конструкции.']
    bogie['deviationSigns']=['Трещины, деформации, повреждение тяг/подвесок или аномальные люфты тележки.','Неравномерный износ колёс, повышенные удары, увод или нетипичные колебания кузова/тележки.']
    bogie['sourceRefs']=unique_strings(bogie.get('sourceRefs',[])+[ERMAK_MECH_ID,BOGIE_ID])
    bogie['variantRules']=unique_strings(bogie.get('variantRules',[])+[
      'Размеры и массы из РЭ6 2004 года считать базовыми для раннего профиля; поздние тележки с конструктивными изменениями подтверждать отдельно.',
      'Массу 21 300 кг применять только к тележке с ручным тормозом и гребнесмазывателем АГС8; базовая масса тележки — 21 200 кг.'
    ])

    pm2['summary']='ПМ2-САУТ6 — установленный на пульте машиниста Ермака орган индикации и ввода команд системы САУТ.'
    pm2['principle']='Пульт обеспечивает взаимодействие машиниста с аппаратурой САУТ; точные электрические и массогабаритные характеристики данного исполнения должны браться только из паспорта ПМ2-САУТ6.'
    pm2['keyParameters']=[]
    pm2['sourceRefs']=unique_strings(pm2.get('sourceRefs',[])+[ERMAK_LAYOUT_ID])
    pm2['variantRules']=unique_strings(pm2.get('variantRules',[])+[
      'ПМ2-САУТ6 подтверждён РЭ2 Ермака по месту установки, но отдельный паспорт с числовыми характеристиками не установлен.',
      'Не переносить характеристики ПУ2/ПУ3/ПУ4/ПУ5-САУТ-ЦМ/485 на ПМ2-САУТ6 без прямого документа о взаимозаменяемости.'
    ])

    speed['summary']='Датчики вращения колёсных пар дают МСУД-Н информацию о частоте/угле вращения осей для регулирования тяги, диагностики и защитных алгоритмов.'
    speed['principle']='Вращение оси механически передаётся на установленный на буксовой крышке датчик; электрическая система использует его импульсный/угловой сигнал для определения частоты вращения. Точная модель датчика в доступном РЭ для этой карточки не установлена.'
    speed['keyParameters']=[]
    speed['sourceRefs']=unique_strings(speed.get('sourceRefs',[])+[ERMAK_SCHEME_ID,ERMAK_MECH_ID])
    speed['variantRules']=unique_strings(speed.get('variantRules',[])+[
      'Не назначать модели семейства ДСНТ-01 только по функциональному сходству; требуется прямое подтверждение конкретного исполнения на 2ЭС5К/3ЭС5К.',
      'Обозначения BR1–BR4/датчик угла поворота из схем и функциональное имя карточки «датчик скорости» считать описанием роли, а не паспортной идентичностью модели.'
    ])

    ko7['summary']='КО7 — обратный клапан 1-10 главного компрессора ВУ 3,5/10-1450, исключающий обратное давление главных резервуаров на остановленный компрессор.'
    ko7['principle']='При подаче воздуха компрессором клапан открывает поток в сторону главных резервуаров; при падении давления со стороны компрессора закрывается и не допускает обратного потока.'
    ko7['keyParameters']=kb_params(CHECK_VALVE_PARAMS,'Клапан 1-10 в позиции КО7 системы приготовления сжатого воздуха базового 2ЭС5К/3ЭС5К с компрессором ВУ 3,5/10-1450.')
    ko7['normalState']=['При работе компрессора воздух свободно поступает к главным резервуарам.','После остановки компрессора отсутствует обратный переток воздуха и противодавление на компрессор.']
    ko7['deviationSigns']=['Обратный переток воздуха после остановки компрессора или разгрузка главных резервуаров через компрессор.','Повышенное сопротивление прямому потоку, заедание или негерметичность клапана.']
    ko7['sourceRefs']=unique_strings(ko7.get('sourceRefs',[])+[ERMAK_PNEU_ID,CHECK_VALVE_ID])
    ko7['variantRules']=unique_strings(ko7.get('variantRules',[])+[
      'КО7 базового Ермака с компрессором ВУ 3,5/10-1450 идентифицировать как клапан 1-10 по РЭ6.',
      'Не переносить параметры исполнения 1-2, предназначенного для компрессора ВВ 0,05/7-1000.'
    ])

    for a,count,status in [(bogie,5,'documented'),(pm2,0,'not_required_for_atlas'),(speed,0,'not_required_for_atlas'),(ko7,4,'documented')]:
        a.setdefault('atlasData',{})['parameterCoverage']={'status':status,'count':count}
        a.setdefault('knowledgeCoverage',{})['parameters']='documented' if count else 'not_required_for_atlas'
    if freeze_non_targets_articles(root)!=frozen:raise SystemExit('Non-target knowledge article changed')
    write_gz(path,root)

for base in ROOTS:
    patch_equipment(base/'ermak_equipment.json.gz')
    patch_knowledge(base/'ermak_knowledge.json.gz')
print('Updated final four-node research pass: MC-001 and PN-005 documented; SF-005 and MC-006 explicitly bounded without guessed parameters')
