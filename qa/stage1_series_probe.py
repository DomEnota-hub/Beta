"""Focused diagnostics-series probe; screenshots and fresh UI trees per action."""
import os
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET

OUT = Path(os.environ['OUT'])
OUT.mkdir(parents=True, exist_ok=True)
counter = 0

def adb(*args):
    return subprocess.check_output(['adb', *args])

def tree():
    global counter
    counter += 1
    remote = f'/sdcard/stage1-{counter}.xml'
    adb('shell', 'uiautomator', 'dump', remote)
    data = adb('shell', 'cat', remote)
    root = ET.fromstring(data)
    (OUT / f'{counter:03d}.xml').write_bytes(data)
    return root

def label(n):
    return n.get('text') or n.get('content-desc') or ''

def capture(name):
    (OUT / f'{name}.png').write_bytes(adb('exec-out', 'screencap', '-p'))

def tap(text):
    root = tree()
    parents = {c: p for p in root.iter() for c in p}
    matches = [n for n in root.iter('node') if label(n) == text]
    if not matches:
        raise AssertionError(f'Missing target: {text}')
    n = matches[0]
    while n.get('clickable') != 'true' and n in parents:
        n = parents[n]
    assert n.get('clickable') == 'true', f'No clickable ancestor: {text}'
    b = list(map(int, re.findall(r'\d+', n.get('bounds'))))
    x, y = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
    print(f'TAP {text}: {x},{y} attributes={n.attrib}', flush=True)
    adb('shell', 'input', 'tap', str(x), str(y))

def expect(text):
    for attempt in range(8):
        root = tree()
        labels = [label(n) for n in root.iter('node') if label(n)]
        print(f'EXPECT {text} attempt={attempt}: {labels[:14]}', flush=True)
        if any(text in s for s in labels):
            return
        time.sleep(1)
    capture('failed')
    raise AssertionError(f'Expected screen absent: {text}')

try:
    # The legacy driver first reproduces the acceptance -> diagnostics path.
    expect('Диагностика ВЛ80С')
    for cycle in range(3):
        tap('Ермак')
        expect('Техническая база Ермак')
        capture(f'{cycle}-ermak')
        tap('ВЛ80С')
        expect('Диагностика ВЛ80С')
        capture(f'{cycle}-vl80s')
    print('PASS: three complete VL80S -> Ermak -> VL80S cycles', flush=True)
finally:
    (OUT / 'logcat.txt').write_bytes(adb('logcat', '-d'))
