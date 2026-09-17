#!/usr/bin/env bash
set -uo pipefail

APK=${APK:?APK path required}
OUT=${OUT:-$GITHUB_WORKSPACE/final-evidence-v3}
mkdir -p "$OUT"

ERMAK_SCENARIO='Нет напряжения в цепях управления'
ERMAK_SCHEME='Базовая силовая схема 2ЭС5К/3ЭС5К'
VL80_BENCHMARK='АК-11Б: включение/отключение компрессора'

adb install -r "$APK" > "$OUT/install.txt" 2>&1 || exit 21
adb logcat -c
adb shell am force-stop ru.railbrake.calculator || true
adb shell am start -n ru.railbrake.calculator/.MainActivity > "$OUT/start.txt" 2>&1 || true

dump_ui() {
  adb shell uiautomator dump /sdcard/window.xml >/dev/null 2>&1 || true
  adb pull /sdcard/window.xml "$1" >/dev/null 2>&1 || true
}

capture() {
  local name="$1"
  dump_ui "$OUT/${name}.xml"
  adb exec-out screencap -p > "$OUT/${name}.png" 2>/dev/null || true
}

has_text() {
  local target="$1"
  dump_ui /tmp/window.xml
  TARGET="$target" python3 - <<'PY'
import os, xml.etree.ElementTree as ET
q=os.environ['TARGET'].casefold()
root=ET.parse('/tmp/window.xml').getroot()
vals=[(n.attrib.get('text') or n.attrib.get('content-desc') or '').strip().casefold() for n in root.iter('node')]
raise SystemExit(0 if any(q in x for x in vals) else 1)
PY
}

tap_text() {
  local target="$1"
  dump_ui /tmp/window.xml
  local coords
  coords=$(TARGET="$target" python3 - <<'PY'
import os,re,xml.etree.ElementTree as ET
q=os.environ['TARGET'].casefold(); root=ET.parse('/tmp/window.xml').getroot(); nodes=list(root.iter('node'))
def label(n): return (n.attrib.get('text') or n.attrib.get('content-desc') or '').strip()
def bnd(n):
    m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',n.attrib.get('bounds',''))
    return tuple(map(int,m.groups())) if m else None
matches=[n for n in nodes if label(n).casefold()==q] or [n for n in nodes if q in label(n).casefold()]
if not matches: raise SystemExit(3)
b=bnd(matches[0])
if not b: raise SystemExit(4)
x=(b[0]+b[2])//2; y=(b[1]+b[3])//2
containers=[]
for n in nodes:
    if n.attrib.get('clickable')!='true': continue
    c=bnd(n)
    if c and c[0] <= x <= c[2] and c[1] <= y <= c[3]:
        containers.append(((c[2]-c[0])*(c[3]-c[1]),c))
if containers:
    c=min(containers,key=lambda z:z[0])[1]
    x=(c[0]+c[2])//2; y=(c[1]+c[3])//2
print(x,y)
PY
  ) || return 1
  read -r x y <<< "$coords"
  adb shell input tap "$x" "$y"
  sleep 1
}

scroll_to_text() {
  local target="$1"
  for _ in $(seq 1 18); do
    has_text "$target" && return 0
    adb shell input swipe 540 1650 540 650 280 >/dev/null 2>&1 || true
    sleep 0.5
  done
  return 1
}

tap_scroll() {
  local target="$1"
  for _ in $(seq 1 18); do
    tap_text "$target" && return 0
    adb shell input swipe 540 1650 540 650 280 >/dev/null 2>&1 || true
    sleep 0.5
  done
  return 1
}

open_drawer() { tap_text '☰'; }

on_exit() {
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    capture "FAIL-${rc}" || true
    adb shell dumpsys activity activities > "$OUT/fail-activity.txt" 2>&1 || true
    adb logcat -d > "$OUT/fail-logcat.txt" 2>&1 || true
    echo "FAIL exit=$rc" > "$OUT/result.txt"
  fi
}
trap on_exit EXIT

ready=0
for i in $(seq 1 24); do
  dump_ui "$OUT/startup-${i}.xml"
  if grep -q 'Железнодорожный помощник' "$OUT/startup-${i}.xml" 2>/dev/null; then ready=1; break; fi
  sleep 2
 done
[ "$ready" -eq 1 ] || exit 31
capture 01-home

# Acceptance: reach a real route, prove NOT_CHECKED cannot silently advance, then select OK.
open_drawer || exit 32
tap_text 'Приёмка' || exit 33
capture 02-acceptance-root
has_text 'Полная приёмка' || exit 34
has_text 'Список по зонам' || exit 35
tap_scroll 'Полная приёмка' || exit 36
has_text 'Пошаговая приёмка' || exit 37
scroll_to_text 'Перед переходом выберите результат проверки этого пункта' || exit 38
capture 03-acceptance-required-state
tap_scroll 'Проверено' || exit 39
has_text 'Состояние: Проверено' || { scroll_to_text 'Состояние: Проверено' || exit 40; }
capture 04-acceptance-checked

# Ermak diagnostics: real family switch + canonical scenario + graph runtime.
open_drawer || exit 41
tap_text 'Диагностика' || exit 42
tap_text 'Ермак' || exit 43
has_text 'Техническая база Ермак' || exit 44
capture 05-ermak-diagnostics
tap_scroll "$ERMAK_SCENARIO" || exit 45
scroll_to_text 'Интерактивный маршрут диагностики' || exit 46
capture 06-ermak-scenario

# Ermak electrical atlas: real canonical scheme opens scheme runtime.
open_drawer || exit 47
tap_text 'Локомотивы / атлас' || exit 48
tap_text 'Ермак' || true
tap_scroll 'Электросхемы' || exit 49
capture 07-ermak-electrical
tap_scroll "$ERMAK_SCHEME" || exit 50
scroll_to_text 'Интерактивная функциональная схема' || exit 51
capture 08-ermak-scheme

# VL80S pneumatic reference restored by recovery8 is visible and opens.
open_drawer || exit 52
tap_text 'Локомотивы / атлас' || exit 53
tap_text 'ВЛ80С' || true
tap_scroll 'Пневмосхемы' || exit 54
tap_scroll "$VL80_BENCHMARK" || exit 55
scroll_to_text 'Учебный ориентир' || exit 56
capture 09-vl80-benchmark

adb shell dumpsys meminfo ru.railbrake.calculator > "$OUT/meminfo.txt" 2>&1 || true
adb shell dumpsys activity activities > "$OUT/activity.txt" 2>&1 || true
adb logcat -d > "$OUT/logcat.txt" 2>&1 || true
if grep -E 'FATAL EXCEPTION|AndroidRuntime.*ru\.railbrake\.calculator' "$OUT/logcat.txt"; then exit 57; fi

echo 'PASS: acceptance + Ermak diagnostics + Ermak scheme + VL80 pneumatic benchmark observed' > "$OUT/result.txt"
trap - EXIT
exit 0
