#!/usr/bin/env python3
import gzip, json
from pathlib import Path

ROOTS=[Path('app/src/main/assets/technical'),Path('patch/app/src/main/assets/technical')]
EQ='ER-EQ-HV-002'; KB='ER-KB-EQ-ER-EQ-HV-002'; SRC='ER-SRC-041'
URL='https://rgups.ru/site/assets/files/213502/dissertatciia_verigin_o_s__27_09_2024.pdf'
PARAMS=[
 {'name':'Номинальное напряжение изоляции','value':25,'unit':'kV','sourceId':SRC},
 {'name':'Номинальный ток продолжительного режима','value':650,'unit':'A','sourceId':SRC},
 {'name':'Пусковой ток','value':300,'unit':'A','sourceId':SRC},
 {'name':'Индуктивность','value':250,'unit':'uH','sourceId':SRC},
 {'name':'Сопротивление катушки постоянному току','value':0.0061,'unit':'Ohm','sourceId':SRC},
 {'name':'Масса','value':38,'unit':'kg','sourceId':SRC},
]
REF={'sourceId':SRC,'document':'РГУПС, диссертационная работа по электромеханическим процессам 3ЭС5К','title':'Основные технические характеристики дросселя помехоподавления ДП-011','url':URL,'locator':'Приложение Б, таблица Б.1'}

def load(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
def save(p,x):
    raw=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
    with p.open('wb') as o:
        with gzip.GzipFile(filename='',mode='wb',fileobj=o,mtime=0,compresslevel=9) as g:g.write(raw)
def refs(items,extra):
    out=[]; seen=set()
    for x in items+[extra]:
        k=x.get('sourceId') if isinstance(x,dict) else str(x)
        if k not in seen: seen.add(k); out.append(x)
    return out

def patch_eq(p):
    r=load(p); r.setdefault('sourceRegistry',{})['DP011_RGUPS']=REF
    q=next(x for x in r['records'] if x.get('id')==EQ)
    q['purpose']='Подавление радиопомех, возникающих в первичной высоковольтной цепи при нарушениях токосъёма между полозом токоприёмника и контактным проводом.'
    q['parameters']=PARAMS
    q['sourceRefs']=refs(q.get('sourceRefs',[]),REF)
    q['parameterCoverage']={'status':'documented','count':len(PARAMS)}
    q['notes']=[n for n in q.get('notes',[]) if not n.startswith('ДП-011:')]+[
      'ДП-011 установлен последовательно в высоковольтном тракте секции после токоприёмника; далее питание проходит к разъединителям и главному выключателю.',
      'Дроссель уменьшает высокочастотную составляющую помех при кратковременных нарушениях контакта токоприёмника с контактным проводом; это фильтрующий элемент, а не коммутационный аппарат.'
    ]
    if r.get('statistics') is not None:
        r['statistics']['recordsWithParameters']=sum(bool(x.get('parameters')) for x in r['records'])
        r['statistics']['recordsWithoutParameters']=len(r['records'])-r['statistics']['recordsWithParameters']
    save(p,r)

def patch_kb(p):
    r=load(p); a=next(x for x in r['articles'] if x.get('id')==KB)
    a['summary']='ДП-011 — последовательный дроссель первичной высоковольтной цепи, уменьшающий радиопомехи при нарушениях токосъёма.'
    a['principle']='Ток контактной сети после токоприёмника проходит через катушку ДП-011. Индуктивность дросселя препятствует быстрому изменению высокочастотной составляющей тока и снижает уровень радиопомех, после чего высоковольтный тракт продолжается через разъединители к главному выключателю.'
    a['keyParameters']=[{'name':x['name'],'value':x['value'],'unit':x['unit'],'applicability':'ДП-011; базовое исполнение 2ЭС5К/3ЭС5К','status':'BASE_CONFIRMED','sourceRefs':[SRC]} for x in PARAMS]
    a['normalState']=['Корпус, изолятор и токоведущие соединения без видимых механических повреждений и следов перегрева.','Высоковольтный тракт секции сохраняет электрическую целостность, а узел не имеет признаков пробоя изоляции или ослабления крепления.']
    a['deviationSigns']=['Следы перегрева или обгорания токоведущих соединений.','Трещины либо повреждения изолятора, деформация катушки или креплений.','Признаки пробоя изоляции или нарушения электрической целостности высоковольтного тракта.']
    if SRC not in a.setdefault('sourceRefs',[]): a['sourceRefs'].append(SRC)
    rules=[x for x in a.get('variantRules',[]) if not x.startswith('ДП-011')]
    rules.append('ДП-011 подтверждён базовым руководством 2ЭС5К/3ЭС5К; при модернизации конкретной секции фактический тип аппарата сверять по маркировке и документации.')
    a['variantRules']=rules
    a.setdefault('knowledgeCoverage',{})['parameters']='documented'
    a.setdefault('atlasData',{})['parameterCoverage']={'status':'documented','count':len(PARAMS)}
    save(p,r)

for b in ROOTS:
    patch_eq(b/'ermak_equipment.json.gz'); patch_kb(b/'ermak_knowledge.json.gz')
print('Ermak DP-011 reference enriched in app and patch mirrors')
