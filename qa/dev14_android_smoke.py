#!/usr/bin/env python3
"""Fresh-tree Android smoke for the dev14 critical user paths."""
import os
import re
import subprocess
import time
import atexit
import xml.etree.ElementTree as ET

PACKAGE = "ru.railbrake.calculator"
OUT = os.environ.get("QA_OUT", "qa-evidence")
os.makedirs(OUT, exist_ok=True)
snapshot_number = 0

def adb(*args):
    return subprocess.check_output(["adb", *args])

def tree():
    global snapshot_number
    data = adb("exec-out", "uiautomator", "dump", "/dev/tty")
    # Some adb versions append "UI hierarchy dumped" after the XML payload.
    # Parse only the document, while retaining the unmodified fresh dump as evidence.
    xml_end = data.find(b"</hierarchy>")
    if xml_end < 0:
        raise AssertionError("uiautomator did not return a hierarchy document")
    document = data[:xml_end + len(b"</hierarchy>")]
    snapshot_number += 1
    with open(os.path.join(OUT, f"ui-{snapshot_number:02d}.xml"), "wb") as output:
        output.write(document)
    return ET.fromstring(document)

def text(node):
    return node.get("text") or node.get("content-desc") or ""

def labels(root):
    return [text(node) for node in root.iter("node") if text(node)]

def wait_for(value, timeout=55):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        root = tree()
        current_labels = labels(root)
        if "System UI isn't responding" in current_labels and "Wait" in current_labels:
            # API 29 can show this transient dialog immediately after a cold boot.
            # It belongs to the emulator, not to the application under test.
            tap("Wait")
            time.sleep(3)
            continue
        if value in current_labels:
            return root
        time.sleep(.5)
    raise AssertionError(f"Missing UI text: {value}")

def tap(value):
    root = tree()
    parents = {child: parent for parent in root.iter() for child in parent}
    node = next((node for node in root.iter("node") if text(node) == value), None)
    if node is None:
        raise AssertionError(f"Missing tap target: {value}")
    while node.get("clickable") != "true" and node in parents:
        node = parents[node]
    if node.get("clickable") != "true":
        raise AssertionError(f"No clickable ancestor: {value}")
    nums = [int(n) for n in re.findall(r"\d+", node.get("bounds", ""))]
    adb("shell", "input", "tap", str((nums[0] + nums[2]) // 2), str((nums[1] + nums[3]) // 2))
    time.sleep(.6)

def open_screen(title):
    tap("☰")
    wait_for(title)
    time.sleep(.8)
    tap(title)

def screenshot(name):
    with open(os.path.join(OUT, f"{name}.png"), "wb") as output:
        subprocess.run(["adb", "exec-out", "screencap", "-p"], check=True, stdout=output)

apk = os.environ["APK"]
subprocess.run(["adb", "install", "-r", apk], check=True)
original_font_scale = adb("shell", "settings", "get", "system", "font_scale").decode().strip() or "1.0"
atexit.register(lambda: adb("shell", "settings", "put", "system", "font_scale", original_font_scale))
adb("shell", "settings", "put", "system", "font_scale", "1.3")
adb("logcat", "-c")
adb("shell", "am", "force-stop", PACKAGE)
adb("shell", "monkey", "-p", PACKAGE, "1")
wait_for("Железнодорожный помощник")

open_screen("Приёмка")
wait_for("Полный осмотр")
tap("Полный осмотр")
wait_for("Начать снаружи")
tap("Начать снаружи")
wait_for("Шаг 1 из")
wait_for("Статус: Не проверено")
tap("Проверено")
wait_for("Статус: Проверено")
screenshot("acceptance-checked")

open_screen("Диагностика")
wait_for("Диагностика ВЛ80С")
tap("Ермак")
wait_for("Техническая база Ермак")
tap("ВЛ80С")
wait_for("Диагностика ВЛ80С")
screenshot("diagnostics-family-roundtrip")

open_screen("Первая помощь")
wait_for("Оказание первой помощи")
wait_for("Общий порядок действий")
tap("Найти по симптому или действию")
adb("shell", "input", "text", "cpr")
wait_for("Найдено: 1")
wait_for("Не дышит / СЛР")
wait_for("Что делать")
screenshot("first-aid-search-cpr")

open_screen("Локомотивы / атлас")
wait_for("Техническая база ВЛ80С")
tap("Главный выключатель")
wait_for("ВЛ80С / Оборудование")
tap("ВЛ80С / Оборудование")
wait_for("Недавние материалы")
screenshot("atlas-breadcrumbs-recents-large-font")

log = adb("logcat", "-d").decode("utf-8", "replace")
with open(os.path.join(OUT, "logcat.txt"), "w", encoding="utf-8") as output:
    output.write(log)
if "FATAL EXCEPTION" in log:
    raise AssertionError("Android crash in logcat")
print("PASS dev14 acceptance, first-aid search, Atlas breadcrumbs/recents and 1.3x font scale")
