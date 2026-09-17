"""Stage 4: acceptance semantics, persistence, exceptional states and safety gates."""
import gzip, json, os, re, subprocess, time, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

APK=Path(os.environ['APK']); OUT=Path(os.environ['OUT']); OUT.mkdir(parents=True,exist_ok=True)
seq=0

def adb(*args,check=True):
    return subprocess.run(['adb',*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=check).stdout

def load_acceptance():
    with zipfile.ZipFile(APK) as z:
        for name in ('assets/technical/vl80s_acceptance.json','assets/technical/vl80s_acceptance.json.gz'):
            try: raw=z.read(name)
            except KeyError: continue
            if name.endswith('.gz'): raw=gzip.decompress(raw)
            return json.loads(raw.decode('utf-8'))
    raise AssertionError('vl80s_acceptance asset missing')

CAN=load_acceptance()
items={x['id']:x for x in CAN['items']}
cabin=next(r for r in CAN['routes'] if r.get('title')=='Начать из кабины')
cabin_ids=cabin['itemIds']
first_gate_index=next(i for i,item_id in enumerate(cabin_ids) if items[item_id].get('preconditions'))
first_gate_ids=items[cabin_ids[first_gate_index]].get('preconditions',[])
(OUT/'canonical-targets.txt').write_text(f'cabin_items={len(cabin_ids)}\nfirst_gate_index={first_gate_index}\nfirst_gate_ids={first_gate_ids}\nnotes={cabin.get("notes","")}\n',encoding='utf-8')

def shot(name): (OUT/f'{name}.png').write_bytes(adb('exec-out','screencap','-p',check=False))

def fresh(tag='tree'):
    """Use only a newly-created UI tree; retry slow/no-KVM dumps."""
    global seq; seq+=1
    remote=f'/sdcard/stage4-{seq}.xml'; last=b''
    for attempt in range(6):
        adb('shell','rm','-f',remote,check=False)
        dump=adb('shell','uiautomator','dump',remote,check=False)
        data=adb('shell','cat',remote,check=False)
        last=b'dump='+dump+b'\ncat='+data
        if data.lstrip().startswith(b'<?xml') or data.lstrip().startswith(b'<hierarchy'):
            (OUT/f'{seq:03d}-{tag}.xml').write_bytes(data)
            return ET.fromstring(data)
        (OUT/f'{seq:03d}-{tag}-retry{attempt}.txt').write_bytes(last)
        time.sleep(1.5)
    shot(f'ui-dump-failed-{seq}')
    raise AssertionError(f'fresh UI dump unavailable: {last[-500:]!r}')

def label(n): return (n.get('text') or n.get('content-desc') or '').strip()
def pmap(root): return {c:p for p in root.iter() for c in p}
def bnd(n):
    v=list(map(int,re.findall(r'\d+',n.get('bounds','')))); assert len(v)==4,n.attrib; return v

def find(root,text,contains=False):
    nodes=[n for n in root.iter('node') if label(n)]
    return [n for n in nodes if (text.casefold() in label(n).casefold() if contains else label(n)==text)]

def tappable(root,node,allow_focus=False):
    ps=pmap(root); n=node
    while n in ps and n.get('clickable')!='true' and not (allow_focus and n.get('focusable')=='true'): n=ps[n]
    if n.get('clickable')!='true' and not (allow_focus and n.get('focusable')=='true'): return node
    return n

def tap_node(root,node,allow_focus=False):
    n=tappable(root,node,allow_focus); b=bnd(n); x=(b[0]+b[2])//2; y=(b[1]+b[3])//2
    adb('shell','input','tap',str(x),str(y)); time.sleep(.8)

def tap_visible(text,contains=False,allow_focus=False):
    root=fresh('tap'); ms=find(root,text,contains)
    if not ms: return False
    tap_node(root,ms[0],allow_focus); return True

def dismiss_emulator_system_anr(root):
    if find(root,"System UI isn't responding",True):
        waits=find(root,'Wait')
        if waits:
            tap_node(root,waits[0]);
            (OUT/'system-ui-anr-handled.txt').write_text('Observed emulator System UI ANR dialog; chose Wait and continued.\n',encoding='utf-8')
            time.sleep(3)
            return True
    return False

def wait_for_app(timeout=210):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        root=fresh('startup')
        if find(root,'Железнодорожный помощник'): return
        if dismiss_emulator_system_anr(root):
            adb('shell','am','start','-n','ru.railbrake.calculator/.MainActivity',check=False)
            continue
        time.sleep(1)
    shot('startup-timeout')
    (OUT/'startup-activity.txt').write_bytes(adb('shell','dumpsys','activity','activities',check=False))
    raise AssertionError('app home did not become visible after handling emulator dialogs')

def swipe_up(): adb('shell','input','swipe','540','1650','540','650','260'); time.sleep(.45)
def swipe_down(): adb('shell','input','swipe','540','650','540','1650','260'); time.sleep(.45)

def scroll_top():
    for _ in range(8): swipe_down()

def tap_scroll(text,max_swipes=24,contains=True,allow_focus=False):
    for _ in range(max_swipes+1):
        if tap_visible(text,False,allow_focus) or (contains and tap_visible(text,True,allow_focus)): return
        swipe_up()
    shot('missing-'+re.sub(r'\W+','-',text)[:35]); raise AssertionError(f'missing target {text}')

def expect_visible(text,timeout=60,contains=False):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        root=fresh('expect')
        if dismiss_emulator_system_anr(root): continue
        if find(root,text,contains): return
        time.sleep(.8)
    shot('expect-'+re.sub(r'\W+','-',text)[:35]); raise AssertionError(f'expected {text}')

def expect_scroll(text,max_swipes=24,contains=True):
    for _ in range(max_swipes+1):
        root=fresh('expect-scroll')
        if find(root,text,False) or (contains and find(root,text,True)): return
        swipe_up()
    shot('expect-scroll-'+re.sub(r'\W+','-',text)[:35]); raise AssertionError(f'expected after scroll {text}')

def clickable(text):
    root=fresh('clickable'); ms=find(root,text,False) or find(root,text,True)
    if not ms: return False
    ps=pmap(root); n=ms[0]
    while n in ps:
        if n.get('clickable')=='true': return n.get('enabled','true')=='true'
        n=ps[n]
    return n.get('clickable')=='true' and n.get('enabled','true')=='true'

def type_field(label_text,value):
    tap_scroll(label_text,allow_focus=True)
    adb('shell','input','text',value)
    adb('shell','input','keyevent','4',check=False)
    time.sleep(.8)

def drawer():
    scroll_top()
    if not tap_visible('☰'): raise AssertionError('drawer unavailable')

def open_acceptance():
    drawer();
    if not tap_visible('Приёмка'): raise AssertionError('acceptance menu unavailable')
    expect_visible('Полная приёмка',timeout=60)

def select_state(name): tap_scroll(name,max_swipes=28)

def expect_step(n,total=66):
    scroll_top(); expect_visible(f'Шаг {n} из {total}',timeout=45,contains=True)

try:
    (OUT/'install.txt').write_bytes(adb('install','-r',str(APK)))
    adb('logcat','-c'); adb('shell','am','force-stop','ru.railbrake.calculator',check=False)
    (OUT/'start.txt').write_bytes(adb('shell','am','start','-n','ru.railbrake.calculator/.MainActivity',check=False))
    wait_for_app(); shot('00-home')

    # Full acceptance: explicit state, advance, then leave/re-enter and resume the same route position.
    open_acceptance(); tap_scroll('Полная приёмка'); expect_step(1); expect_scroll('Перед переходом выберите результат проверки этого пункта')
    select_state('Проверено'); tap_scroll('Далее'); expect_step(2); shot('01-full-step2')
    open_acceptance(); tap_scroll('Полная приёмка'); expect_step(2); shot('02-resumed-step2')

    # BLOCKING requires both comment and an explicit resolution before progression.
    select_state('Блокирующее замечание'); expect_scroll('Блокирующее замечание нельзя закрыть без комментария и оформленного решения.')
    if clickable('Далее'): raise AssertionError('Next is enabled before BLOCKING justification')
    type_field('Комментарий и локализация','stage4note')
    type_field('Оформленное решение / дальнейшее действие','stage4resolution')
    tap_scroll('Далее'); expect_step(3); shot('03-blocking-resolved')

    # NOT_APPLICABLE requires a reason and then allows progression.
    select_state('Не применяется'); expect_scroll('Для этого состояния требуется комментарий.')
    if clickable('Далее'): raise AssertionError('Next is enabled before NOT_APPLICABLE reason')
    type_field('Причина применимости / варианта','notapplicable')
    tap_scroll('Далее'); expect_step(4); shot('04-not-applicable-resolved')

    # Alternate canonical start: locate first gated item from the APK data itself.
    open_acceptance(); tap_scroll('Начать из кабины'); expect_visible('Пошаговая приёмка',timeout=45)
    for i in range(first_gate_index):
        select_state('Проверено'); tap_scroll('Далее'); expect_step(i+2,total=len(cabin_ids))
    expect_step(first_gate_index+1,total=len(cabin_ids))
    expect_scroll('Условия безопасности перед этим пунктом')
    select_state('Проверено')
    expect_scroll('Переход дальше заблокирован: не подтверждены обязательные условия безопасности.')
    if clickable('Далее'): raise AssertionError('Next is enabled while safety gate is unconfirmed')
    for _ in first_gate_ids: tap_scroll('Подтвердить условие')
    tap_scroll('Далее')
    expect_step(first_gate_index+2,total=len(cabin_ids)); shot('05-cabin-safety-gate-cleared')

    (OUT/'result.txt').write_text('PASS: full acceptance + resume + BLOCKING + NOT_APPLICABLE + cabin safety gate\n',encoding='utf-8')
finally:
    (OUT/'logcat.txt').write_bytes(adb('logcat','-d',check=False))
