#!/usr/bin/env bash
set -euo pipefail

APK="$GITHUB_WORKSPACE/source/buildsrc/RailBrakeCalculator/app/build/outputs/apk/debug/app-debug.apk"
OUT="$GITHUB_WORKSPACE/qa-output"
mkdir -p "$OUT"

adb install -r "$APK"
adb logcat -c
adb shell am start -W -n ru.railbrake.calculator/.MainActivity
sleep 2

# Android runner already targets the active emulator, so plain adb is intentional.
dump_ui() {
  local target="$1"
  adb shell uiautomator dump /sdcard/window.xml >/dev/null
  adb pull /sdcard/window.xml "$target" >/dev/null
}

capture() {
  local name="$1"
  adb exec-out screencap -p > "$OUT/${name}.png"
  dump_ui "$OUT/${name}.xml"
  adb shell dumpsys activity activities > "$OUT/${name}-activity.txt"
}

find_coords() {
  local target="$1"
  dump_ui /tmp/window.xml
  TARGET="$target" python3 - <<'PY'
import os,re,xml.etree.ElementTree as ET

target=os.environ['TARGET']
root=ET.parse('/tmp/window.xml').getroot()
nodes=list(root.iter('node'))

def label(n):
    return (n.attrib.get('text') or n.attrib.get('content-desc') or '').strip()

matches=[n for n in nodes if label(n)==target]
if not matches:
    matches=[n for n in nodes if target in label(n)]
if not matches:
    raise SystemExit(2)

b=matches[0].attrib.get('bounds','')
m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',b)
if not m:
    raise SystemExit(3)
x1,y1,x2,y2=map(int,m.groups())
print((x1+x2)//2,(y1+y2)//2)
PY
}

tap_text() {
  local target="$1"
  local coords
  if ! coords=$(find_coords "$target"); then
    # One controlled scroll attempt before deciding the target is absent.
    adb shell input swipe 540 1850 540 700 450
    sleep 1
    coords=$(find_coords "$target") || {
      echo "UI target not found after scroll: $target" >&2
      dump_ui "$OUT/missing-target.xml" || true
      adb exec-out screencap -p > "$OUT/missing-target.png" || true
      return 1
    }
  fi
  local x y
  read -r x y <<< "$coords"
  adb shell input tap "$x" "$y"
  sleep 1
}

open_drawer() {
  tap_text '☰'
}

capture home
open_drawer
capture drawer_home

tap_text 'Приёмка'
capture acceptance_routes

tap_text 'Все пункты'
capture acceptance_all

tap_text 'Маршруты'
capture acceptance_routes_again

tap_text 'Полная приёмка'
capture acceptance_full_step1

# Confirm that the full route exposes the canonical state model.
dump_ui /tmp/acceptance-step.xml
for label in 'Не проверено' 'Проверено' 'Замечание' 'Блокирующее' 'Не применяется'; do
  if ! grep -Fq "$label" /tmp/acceptance-step.xml; then
    echo "Canonical acceptance state missing from UI: $label" >&2
    exit 4
  fi
done

adb logcat -d > "$OUT/logcat.txt"

echo "Black-box acceptance flow completed"
