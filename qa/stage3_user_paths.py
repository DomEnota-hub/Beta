"""Stage 3: real Android paths through Ermak diagnostics/schemes and VL80 pneumatic reference."""
import os, re, subprocess, time
from pathlib import Path
import xml.etree.ElementTree as ET

APK=Path(os.environ['APK']); OUT=Path(os.environ['OUT']); OUT.mkdir(parents=True,exist_ok=True)
SCENARIO='Нет напряжения в цепях управления'
SCHEME='Базовая силовая схема 2ЭС5К/3ЭС5К'
BENCH='АК-11Б: включение/отключение компрессора'
seq=0

def run(*args, check=True):
    p=subprocess.run(list(args),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=check)
    return p.stdout

def adb(*args,check=True): return run('adb',*args,check=check)

def fresh_tree(tag='tree'):
    """Never reuse stale XML. Retry the dump itself and archive each failure."""
    global seq; seq+=1
    remote=f'/sdcard/stage3-{seq}.xml'
    last=b''
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
    screenshot(f'ui-dump-failed-{seq}')
    raise AssertionError(f'Fresh UI dump unavailable after retries: {last[-500:]!r}')

def label(n): return (n.get('text') or n.get('content-desc') or '').strip()
def parents(root): return {c:p for p in root.iter() for c in p}

def screenshot(name): (OUT/f'{name}.png').write_bytes(adb('exec-out','screencap','-p',check=False))

def clickable_for(root,node):
    ps=parents(root); n=node
    while n.get('clickable')!='true' and n in ps: n=ps[n]
    if n.get('clickable')!='true': raise AssertionError(f'No clickable ancestor for {label(node)!r}')
    return n

def bounds(n):
    nums=list(map(int,re.findall(r'\d+',n.get('bounds',''))))
    if len(nums)!=4: raise AssertionError(f'Bad bounds {n.get("bounds")}')
    return nums

def tap_visible(text,contains=False):
    root=fresh_tree('tap')
    nodes=[n for n in root.iter('node') if label(n)]
    matches=[n for n in nodes if (text.casefold() in label(n).casefold() if contains else label(n)==text)]
    if not matches: return False
    n=clickable_for(root,matches[0]); b=bounds(n); x=(b[0]+b[2])//2; y=(b[1]+b[3])//2
    print('TAP',text,'->',label(matches[0]),x,y,flush=True)
    adb('shell','input','tap',str(x),str(y)); time.sleep(1)
    return True

def swipe_up(): adb('shell','input','swipe','540','1650','540','650','280'); time.sleep(.6)

def tap_scroll(text,max_swipes=20):
    for _ in range(max_swipes+1):
        if tap_visible(text) or tap_visible(text,contains=True): return
        swipe_up()
    screenshot('missing-'+re.sub(r'[^A-Za-zА-Яа-я0-9]+','-',text)[:40])
    raise AssertionError(f'Missing scroll target: {text}')

def expect(text,timeout=120,contains=False):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        root=fresh_tree('expect')
        vals=[label(n) for n in root.iter('node') if label(n)]
        ok=any((text.casefold() in v.casefold() if contains else v==text) for v in vals)
        if ok:
            print('EXPECT PASS',text,flush=True); return
        time.sleep(1)
    screenshot('expect-fail-'+re.sub(r'[^A-Za-zА-Яа-я0-9]+','-',text)[:40])
    raise AssertionError(f'Expected text absent: {text}')

def open_drawer():
    if not tap_visible('☰'): raise AssertionError('Drawer button missing')

try:
    (OUT/'install.txt').write_bytes(adb('install','-r',str(APK)))
    adb('logcat','-c'); adb('shell','am','force-stop','ru.railbrake.calculator',check=False)
    (OUT/'start.txt').write_bytes(adb('shell','am','start','-n','ru.railbrake.calculator/.MainActivity',check=False))
    expect('Железнодорожный помощник',timeout=90); screenshot('01-home')

    open_drawer(); tap_visible('Диагностика') or (_ for _ in ()).throw(AssertionError('Диагностика menu missing'))
    expect('Диагностика ВЛ80С',timeout=45)
    tap_visible('Ермак') or (_ for _ in ()).throw(AssertionError('Ермак selector missing'))
    expect('Техническая база Ермак',timeout=120); screenshot('02-ermak-diagnostics')
    tap_scroll(SCENARIO)
    expect('Интерактивный маршрут диагностики',timeout=120,contains=True); screenshot('03-ermak-scenario')

    open_drawer(); tap_visible('Локомотивы / атлас') or (_ for _ in ()).throw(AssertionError('Atlas menu missing'))
    time.sleep(1); tap_visible('Ермак')
    tap_scroll('Электросхемы')
    tap_scroll(SCHEME)
    expect('Интерактивная функциональная схема',timeout=120,contains=True); screenshot('04-ermak-electrical-scheme')

    open_drawer(); tap_visible('Локомотивы / атлас') or (_ for _ in ()).throw(AssertionError('Atlas menu missing on return'))
    time.sleep(1); tap_visible('ВЛ80С')
    tap_scroll('Пневмосхемы')
    tap_scroll(BENCH)
    expect('Учебный ориентир',timeout=90,contains=True); screenshot('05-vl80-benchmark')

    (OUT/'result.txt').write_text('PASS: Ermak diagnostic scenario -> Ermak electrical scheme -> VL80 pneumatic benchmark\n',encoding='utf-8')
finally:
    (OUT/'logcat.txt').write_bytes(adb('logcat','-d',check=False))
