#!/usr/bin/env python3
import gzip
import json
from pathlib import Path

ROOTS=[Path('app/src/main/assets/technical'),Path('patch/app/src/main/assets/technical')]
TARGETS=['ER-EQ-PR-001','ER-EQ-PR-004','ER-EQ-PR-006','ER-EQ-CT-006']
ERMAK_SCHEME_ID='ER-SRC-002'
ERMAK_EQUIP_ID='ER-SRC-005'
RT_TECH_ID='ER-SRC-110'
SETTINGS_ID='ER-SRC-113'
BATTERY_ID='ER-SRC-114'

SETTINGS_REF={
 'sourceId':SETTINGS_ID,
 'document':'Электровоз 2ЭС5К «Ермак». Электрические схемы',
 'title':'Уставки срабатывания аппаратов защиты и контроля: K2, KA9, KV4',
 'url':'https://3uch.ru/textbook/crprot/epeivenan/bevalll',
 'locator':'таблица «Уставки срабатывания аппаратов защиты и контроля»: QF1/K2, KA9, KV4/KV5',
}
BATTERY_REF={
 'sourceId':BATTERY_ID,
 'document':'Учебный материал по аккумуляторной батарее 21KL-125P электровоза 2ЭС5К',
 'title':'Аккумуляторная батарея 21KL-125P 2ЭС5К: состав и номинальные данные',
 'url':'https://infourok.ru/urok-ustroystvo-akkumulyatornoy-batarei-klp-elektrovoza-esk-3035074.html',
 'locator':'разделы «Технические характеристики» и «Устройство и работа»',
 'note':'Идентичность KL-125P дополнительно подтверждается РЭ8 Ермака, которое предписывает обслуживание по руководству на аккумуляторы KL-125P.',
}

K2_PARAMS=[
 {'name':'Ток уставки реле максимального тока K2','value':'250+22.5','unit':'A','sourceId':SETTINGS_ID},
]
KV4_PARAMS=[
 {'name':'Ток срабатывания РКЗ-306','value':'72.6±2.5','unit':'mA','sourceId':SETTINGS_ID},
]
KA9_PARAMS=[
 {'name':'Род тока','value':'переменный','unit':'','sourceId':SETTINGS_ID},
 {'name':'Номинальное напряжение изоляции катушки (шины)','value':3000,'unit':'V','sourceId':RT_TECH_ID},
 {'name':'Номинальный ток катушки (шины)','value':1000,'unit':'A','sourceId':RT_TECH_ID},
 {'name':'Ток уставки на Ермаке','value':'3500±175','unit':'A','sourceId':SETTINGS_ID},
 {'name':'Время срабатывания по таблице уставок Ермака','value':0.01,'unit':'s','sourceId':SETTINGS_ID},
 {'name':'Номинальное напряжение контактов','value':50,'unit':'V','sourceId':RT_TECH_ID},
]
BATTERY_PARAMS=[
 {'name':'Номинальная ёмкость','value':125,'unit':'Ah','sourceId':BATTERY_ID},
 {'name':'Номинальное напряжение комплекта на секцию','value':50,'unit':'V','sourceId':BATTERY_ID},
 {'name':'Количество аккумуляторных элементов в комплекте секции','value':42,'unit':'pcs','sourceId':BATTERY_ID},
 {'name':'Номинальное напряжение одного элемента KL-125P','value':1.2,'unit':'V','sourceId':BATTERY_ID},
 {'name':'Максимальный ток подзаряда разряженного комплекта','value':31,'unit':'A','sourceId':ERMAK_SCHEME_ID},
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
    if stats.get('recordsWithParameters')!=76 or stats.get('recordsWithoutParameters')!=35:
        raise SystemExit(f"Live statistics changed: {stats.get('recordsWithParameters')}/{stats.get('recordsWithoutParameters')}")
    frozen=freeze_non_targets_records(root)
    reg=root.setdefault('sourceRegistry',{})
    register(reg,'ERMAK_PROTECTION_SETTINGS_EXTENDED',SETTINGS_REF)
    register(reg,'ERMAK_BATTERY_21KL125P',BATTERY_REF)
    re1=source_by_id(reg,ERMAK_SCHEME_ID); re4=source_by_id(reg,ERMAK_EQUIP_ID); rttech=source_by_id(reg,RT_TECH_ID)

    k2=rec(root,'ER-EQ-PR-001'); kv4=rec(root,'ER-EQ-PR-004'); ka9=rec(root,'ER-EQ-PR-006'); bat=rec(root,'ER-EQ-CT-006')
    if k2.get('schemeDesignations')!=['K2'] or k2.get('modelNames')!=[]:raise SystemExit('PR-001 identity changed')
    if kv4.get('schemeDesignations')!=['KV4'] or kv4.get('modelNames')!=[]:raise SystemExit('PR-004 identity changed')
    if ka9.get('schemeDesignations')!=['KA9'] or ka9.get('modelNames')!=[]:raise SystemExit('PR-006 identity changed')
    if bat.get('schemeDesignations')!=[] or bat.get('modelNames')!=[]:raise SystemExit('CT-006 identity changed')
    if any(x.get('parameters') for x in (k2,kv4,ka9,bat)):raise SystemExit('Selected record already has parameters')

    k2['purpose']='Максимальная токовая защита первичной цепи тягового трансформатора: встроенное в главный выключатель QF1 реле K2 размыкает цепь удерживающего электромагнита при опасном токе.'
    k2['parameters']=K2_PARAMS
    k2['sourceRefs']=unique_refs(k2.get('sourceRefs',[])+[re1,SETTINGS_REF])
    k2['parameterCoverage']={'status':'documented','count':1}
    k2['notes']=[
      'K2 — реле максимального тока в составе главного выключателя QF1 ВОВ-25А-10/400 УХЛ1; отдельную модель реле в modelNames не придумывать.',
      'Запись уставки 250+22,5 А сохранена в форме источника; не превращать её в симметричный допуск ±22,5 А без отдельного документа.',
    ]

    kv4['modelNames']=['РКЗ-306']
    kv4['purpose']='Контроль замыкания вспомогательных цепей на корпус с выдачей сигнализации «РКЗ». На базовой схеме Ермака позиция KV4 выполнена реле контроля земли РКЗ-306.'
    kv4['parameters']=KV4_PARAMS
    kv4['sourceRefs']=unique_refs(kv4.get('sourceRefs',[])+[re1,SETTINGS_REF])
    kv4['parameterCoverage']={'status':'documented','count':1}
    kv4['notes']=[
      'Таблица уставок 2ЭС5К прямо связывает KV4/KV5 с РКЗ-306 и током срабатывания 72,6±2,5 мА.',
      'Карточка KV4 описывает контроль земли вспомогательных цепей; назначение KV5 для другой контролируемой цепи не переносить автоматически.'
    ]

    ka9['modelNames']=['РТ-255']
    ka9['purpose']='Токовая защита цепей собственных нужд от коротких замыканий: при срабатывании KA9 разрывается цепь удержания главного выключателя QF1.'
    ka9['parameters']=KA9_PARAMS
    ka9['sourceRefs']=unique_refs(ka9.get('sourceRefs',[])+[re1,SETTINGS_REF,rttech])
    ka9['parameterCoverage']={'status':'documented','count':len(KA9_PARAMS)}
    ka9['notes']=[
      'Таблица уставок Ермака прямо задаёт KA9 как РТ-255, 3500±175 А, переменный ток, время срабатывания 0,01 с.',
      'Паспортные электрические характеристики РТ-255 берутся только из строки этой модели; данные РТ-253 и РТ-546-1 не смешиваются.'
    ]

    bat['modelNames']=['21KL-125P']
    bat['purpose']='Резервное питание цепей управления и освещения секции при неработающем шкафе питания, а также сглаживание переходов питания цепей управления.'
    bat['parameters']=BATTERY_PARAMS
    bat['sourceRefs']=unique_refs(bat.get('sourceRefs',[])+[re1,re4,BATTERY_REF])
    bat['parameterCoverage']={'status':'documented','count':len(BATTERY_PARAMS)}
    bat['notes']=[
      'РЭ1 Ермака обозначает два аккумуляторных блока GB1 и GB2; комплект секции в сумме содержит 42 никель-кадмиевых элемента и имеет номинальное напряжение 50 В.',
      'Обозначение 21KL-125P относится к 21-элементной батарейной единице; в карточке оно хранится как тип применённой батареи, а не как утверждение о наличии только 21 элемента во всём комплекте секции.',
      'Ток 31 А — предельный ток подзаряда разряженного комплекта в схеме Ермака, а не номинальный разрядный ток аккумулятора.'
    ]

    stats['recordsWithParameters']=sum(bool(r.get('parameters')) for r in root['records'])
    stats['recordsWithoutParameters']=len(root['records'])-stats['recordsWithParameters']
    if freeze_non_targets_records(root)!=frozen:raise SystemExit('Non-target equipment record changed')
    write_gz(path,root)


def patch_knowledge(path):
    root=read_gz(path); frozen=freeze_non_targets_articles(root)
    k2=art(root,'ER-EQ-PR-001'); kv4=art(root,'ER-EQ-PR-004'); ka9=art(root,'ER-EQ-PR-006'); bat=art(root,'ER-EQ-CT-006')

    k2['summary']='K2 — встроенное в главный выключатель реле максимального тока, защищающее первичную цепь тягового трансформатора Ермака.'
    k2['principle']='При токе первичной цепи, достигающем уставки K2, реле воздействует на цепь удержания QF1 и вызывает отключение главного выключателя.'
    k2['keyParameters']=kb_params(K2_PARAMS,'K2 в составе QF1 ВОВ-25А-10/400 УХЛ1 базовой схемы 2ЭС5К/3ЭС5К.')
    k2['normalState']=['При штатном токе K2 не вызывает отключение QF1.','Цепь удерживающего электромагнита QF1 не разомкнута защитой K2.']
    k2['deviationSigns']=['Срабатывание K2 фиксируется при перегрузке или коротком замыкании первичной цепи.','Необоснованное либо отсутствующее срабатывание требует проверки уставки и цепей главного выключателя.']
    k2['sourceRefs']=unique_strings(k2.get('sourceRefs',[])+[ERMAK_SCHEME_ID,SETTINGS_ID])
    k2['variantRules']=unique_strings(k2.get('variantRules',[])+[
      'K2 хранить как встроенное реле максимального тока QF1; не назначать отдельный тип реле без прямого документа.',
      'Уставку 250+22,5 А не переписывать как ±22,5 А.'
    ])

    kv4['summary']='KV4 — РКЗ-306, реле контроля замыкания вспомогательных цепей Ермака на корпус.'
    kv4['principle']='При появлении утечки на корпус контролируемая цепь создаёт ток через чувствительный орган РКЗ-306; при достижении уставки реле переключает контакт и формирует сигнал «РКЗ».'
    kv4['keyParameters']=kb_params(KV4_PARAMS,'РКЗ-306 в позиции KV4 базовой схемы Ермака.')
    kv4['normalState']=['При исправной изоляции KV4 не сработано, сигнал «РКЗ» отсутствует.','Контролируемая вспомогательная сеть не имеет устойчивой связи с корпусом.']
    kv4['deviationSigns']=['Появляется сигнал «РКЗ» и срабатывает KV4.','Повторное срабатывание после восстановления требует поиска утечки или повреждения изоляции.']
    kv4['sourceRefs']=unique_strings(kv4.get('sourceRefs',[])+[ERMAK_SCHEME_ID,SETTINGS_ID])
    kv4['variantRules']=unique_strings(kv4.get('variantRules',[])+['Для KV4 использовать тип РКЗ-306 и уставку из таблицы Ермака; KV5 не считать той же функциональной карточкой только из-за одинакового типа реле.'])

    ka9['summary']='KA9 — реле перегрузки РТ-255 защиты цепей собственных нужд Ермака от коротких замыканий.'
    ka9['principle']='Переменный ток вспомогательной цепи проходит через токовую шину РТ-255. При превышении уставки магнитная система переключает блокировку KA9, что приводит к отключению QF1.'
    ka9['keyParameters']=kb_params(KA9_PARAMS,'РТ-255 в позиции KA9 базовой схемы 2ЭС5К/3ЭС5К.')
    ka9['normalState']=['При штатной нагрузке KA9 не сработано и цепь удержания QF1 замкнута через его контакт.','Механизм и контакты реле не имеют следов перегрева, заедания или повреждения изоляции.']
    ka9['deviationSigns']=['При коротком замыкании вспомогательной цепи KA9 срабатывает и отключает QF1.','Ложное либо отсутствующее срабатывание указывает на необходимость проверки уставки, токовой шины и контактного механизма.']
    ka9['sourceRefs']=unique_strings(ka9.get('sourceRefs',[])+[ERMAK_SCHEME_ID,SETTINGS_ID,RT_TECH_ID])
    ka9['variantRules']=unique_strings(ka9.get('variantRules',[])+['Параметры РТ-253 и РТ-546-1 не переносить на KA9; для этой позиции базового Ермака подтверждён РТ-255.'])

    bat['summary']='Аккумуляторный комплект секции Ермака на элементах KL-125P обеспечивает резервное питание цепей управления и освещения при отсутствии питания от шкафа А25.'
    bat['principle']='Два батарейных блока GB1 и GB2 включены в цепь питания управления; суммарный комплект секции содержит 42 последовательно работающих никель-кадмиевых элемента и подзаряжается от шкафа питания.'
    bat['keyParameters']=kb_params(BATTERY_PARAMS,'Аккумуляторный комплект секции базового 2ЭС5К/3ЭС5К на батареях 21KL-125P.')
    bat['normalState']=['Напряжение комплекта соответствует состоянию заряда и температуре, соединения GB1/GB2 исправны.','При работающем шкафе питания батарея подзаряжается без превышения допустимого тока.']
    bat['deviationSigns']=['Напряжение батареи быстро проседает под штатной нагрузкой или не восстанавливается при подзаряде.','Есть перегрев, утечка электролита, повреждение соединений или выраженный разброс состояния элементов.']
    bat['sourceRefs']=unique_strings(bat.get('sourceRefs',[])+[ERMAK_SCHEME_ID,ERMAK_EQUIP_ID,BATTERY_ID])
    bat['variantRules']=unique_strings(bat.get('variantRules',[])+[
      '21KL-125P — тип одной 21-элементной батарейной единицы; комплект секции включает GB1 и GB2 и суммарно 42 элемента.',
      'Не переносить массу и габариты отдельного элемента KL-125P на весь комплект секции.'
    ])

    for a,params in [(k2,K2_PARAMS),(kv4,KV4_PARAMS),(ka9,KA9_PARAMS),(bat,BATTERY_PARAMS)]:
        a.setdefault('atlasData',{})['parameterCoverage']={'status':'documented','count':len(params)}
        a.setdefault('knowledgeCoverage',{})['parameters']='documented'
    kv4['atlasData']['modelNames']=['РКЗ-306']
    ka9['atlasData']['modelNames']=['РТ-255']
    bat['atlasData']['modelNames']=['21KL-125P']
    if freeze_non_targets_articles(root)!=frozen:raise SystemExit('Non-target knowledge article changed')
    write_gz(path,root)

for root in ROOTS:
    patch_equipment(root/'ermak_equipment.json.gz')
    patch_knowledge(root/'ermak_knowledge.json.gz')
print('Enriched K2, KV4/RKZ-306, KA9/RT-255 and 21KL-125P battery set')
